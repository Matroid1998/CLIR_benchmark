"""
Alias-graph benchmark builder.

For each ChEBI concept that genuinely appears in the corpus (gold documents), we
surround it with hard negatives -- documents that mention a *taxonomic neighbor*
of the concept (chemically similar, but a different concept) and do not mention
the concept itself. A concept is kept only if it has at least ``min_gold`` gold
documents and at least ``min_negatives`` hard-negative documents. The result is
one JSON record per concept holding its multilingual name set (the retrieval
query) plus the gold and look-alike publication ids.

Pipeline: read corpus -> load ChEBI graph -> (KG-only scan to find concepts that
appear) -> fetch Wikipedia names for those concepts -> rebuild index + rescan ->
assemble gold/hard-negatives -> write alias_graph.json + manifest.csv.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.domain import CorpusSchema
from clir_bench.domains.chem_patents.aliasgraph import chebi as chebi_mod
from clir_bench.domains.chem_patents.aliasgraph import wikidata
from clir_bench.domains.chem_patents.aliasgraph.matching import (
    NameIndex,
    build_name_index,
    is_code_like_name,
    prune_names,
    scan_corpus,
)

if TYPE_CHECKING:  # networkx is heavy; only imported inside the functions below
    import networkx as nx

# Root of the ChEBI structural (actual-molecule) subtree. Restricting main
# concepts to its descendants keeps real chemical entities and drops role /
# group / atom / application classes whose names are ordinary words.
MOLECULAR_ENTITY = "CHEBI:23367"

# The corpus the alias graph is built against when a command takes no --source.
# Google Patents is the only source with the five-language coverage the concept
# name sets are written for.
DEFAULT_SOURCE = "gp"

ALIAS_GRAPH_JSON = "alias_graph.json"
MANIFEST_CSV = "manifest.csv"

# Columns appended to a corpus row when a concept's documents are exported.
EXTRA_FIELDS: Tuple[str, ...] = (
    "role", "concept_chebi_id", "concept_name", "matched_chebi_id", "relation",
)

MANIFEST_FIELDS: Tuple[str, ...] = (
    "chebi_id", "name", "n_gold", "n_hard_neg", "gold_langs", "n_neighbors_in_corpus",
)

# The concept-mention scan reads this column only; see ``scan_corpus``.
MATCH_FIELD = "context"


def alias_dir(context: AppContext) -> Path:
    return context.workspace.data("alias_graph")


def alias_json_path(context: AppContext) -> Path:
    return alias_dir(context) / ALIAS_GRAPH_JSON


def qac_csv_path(context: AppContext) -> Path:
    return alias_dir(context) / "qac" / "concept_qa.csv"


def load_concepts(path: Path) -> List[dict]:
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)["concepts"]


def _slug(name: str, maxlen: int = 60) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_name).strip("-").lower()
    return s[:maxlen] or "concept"


def _dedupe_keep_first(names: List[str]) -> List[str]:
    """Case-insensitive dedupe, preserving the first (canonical) casing."""
    out: List[str] = []
    seen: Set[str] = set()
    for n in names:
        key = n.casefold()
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out


# --------------------------------------------------------------------------- #
# The two-pass name scan, shared with the name-quality check
# --------------------------------------------------------------------------- #

@dataclass
class NameScan:
    """Everything the second (final) corpus scan produced."""

    graph: "nx.DiGraph"
    wiki_names: Dict[str, Dict[str, str]]
    index: NameIndex
    concept_to_docs: Dict[str, Set[str]]
    match_info: Dict[str, Dict[str, Tuple[str, str]]]


def scan_with_names(
    context: AppContext,
    rows: Sequence[dict],
    *,
    variant: str,
    langs: Sequence[str],
    use_wikipedia: bool = True,
    min_name_len: int = 4,
    max_concepts_per_name: int = 3,
    max_df_ratio: float = 0.02,
) -> NameScan:
    """Scan the corpus twice: once on ontology names, once with Wikipedia folded in.

    The first pass exists to discover which concepts occur at all, so only those
    ids are ever asked of Wikidata (~3k rather than ~205k), and to measure the
    per-name document frequency that drives stopword pruning.
    """
    schema = context.schema
    graph = chebi_mod.load_chebi_graph(chebi_mod.cache_dir(context), variant)

    print("Scanning corpus for ChEBI names (KG only) ...")
    kg_index = build_name_index(
        graph, {}, min_len=min_name_len, max_concepts_per_name=max_concepts_per_name
    )
    print(f"  name index: {kg_index.n_names()} names")
    concept_to_docs, _, name_doc_freq = scan_corpus(
        rows, kg_index, schema=schema, field=MATCH_FIELD
    )
    print(f"  concepts found in corpus: {len(concept_to_docs)}")

    # Names that behave like corpus stopwords (common words masquerading as
    # aliases, e.g. "para", "groupe") are pruned so only specific names match.
    df_ceiling = max_df_ratio * len(rows)
    stop_grams = {g for g, n in name_doc_freq.items() if n > df_ceiling}
    if stop_grams:
        examples = sorted(stop_grams, key=lambda g: -name_doc_freq[g])[:8]
        print(f"  pruning {len(stop_grams)} stopword names (df > {df_ceiling:.0f}); e.g. {examples}")

    wiki_names: Dict[str, Dict[str, str]] = {}
    if use_wikipedia and concept_to_docs:
        wiki_names = wikidata.fetch_wikipedia_names(
            list(concept_to_docs.keys()), langs=langs, path=wikidata.cache_path(context)
        )

    index = (
        build_name_index(
            graph, wiki_names, min_len=min_name_len, max_concepts_per_name=max_concepts_per_name
        )
        if wiki_names
        else kg_index
    )
    prune_names(index, stop_grams)
    print("Re-scanning corpus (Wikipedia names folded in, stopwords pruned) ...")
    concept_to_docs, match_info, _ = scan_corpus(
        rows, index, schema=schema, field=MATCH_FIELD
    )
    print(f"  concepts found in corpus: {len(concept_to_docs)}")

    return NameScan(
        graph=graph,
        wiki_names=wiki_names,
        index=index,
        concept_to_docs=concept_to_docs,
        match_info=match_info,
    )


# --------------------------------------------------------------------------- #
# Concept records
# --------------------------------------------------------------------------- #

def _concept_name_set(
    graph: "nx.DiGraph",
    cid: str,
    wiki_names: Dict[str, Dict[str, str]],
) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    """
    Return (name_set, codes, brand_names) for a concept. The multilingual name_set
    (the query/answer side) holds only real names; registry/regulatory codes
    (E-numbers, refrigerant numbers, company/CAS codes) are split into ``codes``.
    ChEBI ``BRAND:NAME`` synonyms are already excluded from the graph's ``synonyms``
    (kept out of matching) and surfaced here as ``brand_names`` for provenance.
    The ChEBI primary name always stays in name_set; only synonyms are classified.
    """
    data = graph.nodes[cid]
    name_set: Dict[str, List[str]] = {}
    chebi_names: List[str] = []
    codes: List[str] = []
    if data.get("name"):
        chebi_names.append(data["name"])
    for syn in data.get("synonyms", ()):
        (codes if is_code_like_name(syn) else chebi_names).append(syn)
    if chebi_names:
        name_set["chebi"] = _dedupe_keep_first(chebi_names)
    for lang, title in wiki_names.get(cid, {}).items():
        name_set.setdefault(lang, []).append(title)
    return name_set, _dedupe_keep_first(codes), _dedupe_keep_first(list(data.get("brand_names", [])))


def _neighbor_relations(graph: "nx.DiGraph", cid: str) -> Dict[str, str]:
    """Map each taxonomic neighbor id -> relation, parent/child before sibling."""
    nb = chebi_mod.taxonomic_neighbors(graph, cid)
    rel: Dict[str, str] = {}
    for nid in nb["sibling"]:
        rel[nid] = "sibling"
    for nid in nb["child"]:
        rel[nid] = "child"
    for nid in nb["parent"]:
        rel[nid] = "parent"
    return rel


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def build_alias_graph(context: AppContext, args: argparse.Namespace) -> int:
    """Select concepts, assemble gold and hard-negative sets, write the benchmark."""
    import networkx as nx

    schema: CorpusSchema = context.schema
    source = getattr(args, "source", None) or DEFAULT_SOURCE
    corpus_csv = context.workspace.corpus_csv(source)
    output_dir = alias_dir(context)
    variant = chebi_mod.variant_for(context, getattr(args, "chebi_variant", None))
    langs = list(getattr(args, "langs", None) or wikidata.DEFAULT_LANGS)
    use_wikipedia = not getattr(args, "no_wikipedia", False)
    leaf_only = not getattr(args, "include_classes", False)
    molecular_only = not getattr(args, "include_non_molecular", False)
    min_gold = args.min_gold
    min_neg = args.min_negatives
    max_concepts = getattr(args, "max_concepts", None)

    print(f"Reading corpus: {corpus_csv}")
    rows = corpus_io.read_rows(corpus_csv)
    doc_by_id = {schema.id_of(r): r for r in rows}
    print(f"  {len(rows)} documents")

    scan = scan_with_names(
        context,
        rows,
        variant=variant,
        langs=langs,
        use_wikipedia=use_wikipedia,
        max_df_ratio=args.max_df,
    )
    graph = scan.graph
    concept_to_docs = scan.concept_to_docs

    mol_entity_set: Optional[Set[str]] = None
    if molecular_only:
        if MOLECULAR_ENTITY in graph:
            mol_entity_set = nx.ancestors(graph, MOLECULAR_ENTITY) | {MOLECULAR_ENTITY}
            print(f"  restricting to {len(mol_entity_set)} molecular-entity concepts")
        else:
            print(f"  warning: {MOLECULAR_ENTITY} absent from {variant} graph; no molecular filter")

    # Documents are keyed by family (i.e. the doc id with the `_<lang>` suffix
    # stripped): the per-language versions of one patent are the same gold or
    # negative item, and their text lives once in the corpus CSV. This avoids the
    # 16x text duplication of materializing a CSV per concept.
    concept_to_pubs: Dict[str, Set[str]] = {}
    for cid, docs in concept_to_docs.items():
        concept_to_pubs[cid] = {schema.family_of(doc_by_id[d]) for d in docs}

    # Candidate main concepts: specific molecular entities (leaves of the is_a
    # graph -- not broad classes) with enough gold publications, most-attested first.
    def _is_candidate(cid: str) -> bool:
        if len(concept_to_pubs[cid]) < min_gold:
            return False
        if mol_entity_set is not None and cid not in mol_entity_set:
            return False
        if leaf_only and graph.in_degree(cid) > 0:
            return False
        return True

    candidates = sorted(
        (cid for cid in concept_to_pubs if _is_candidate(cid)),
        key=lambda c: len(concept_to_pubs[c]),
        reverse=True,
    )
    kind = "leaf molecular" if leaf_only else "molecular"
    print(f"Candidate concepts ({kind}, >= {min_gold} gold pubs): {len(candidates)}")

    concepts: List[dict] = []
    for cid in candidates:
        if max_concepts is not None and len(concepts) >= max_concepts:
            break
        gold_pubs = concept_to_pubs[cid]
        relations = _neighbor_relations(graph, cid)

        # Hard negatives: publications that mention a neighbor but NOT the concept.
        hard_neg: Dict[str, Tuple[str, str]] = {}  # pub -> (neighbor_id, relation)
        neighbors_in_corpus: Set[str] = set()
        for nid, rel in relations.items():
            nid_pubs = concept_to_pubs.get(nid)
            if not nid_pubs:
                continue
            neighbors_in_corpus.add(nid)
            for pub in nid_pubs - gold_pubs:
                hard_neg.setdefault(pub, (nid, rel))

        if len(hard_neg) < min_neg:
            continue

        concept_name = graph.nodes[cid].get("name", cid)
        name_set, codes, brand_names = _concept_name_set(graph, cid, scan.wiki_names)
        gold_langs = sorted({schema.language_of(doc_by_id[d]) for d in concept_to_docs[cid]})

        concepts.append({
            "chebi_id": cid,
            "name": concept_name,
            "name_set": name_set,
            "codes": codes,
            "brand_names": brand_names,
            "query_names": sorted({n for names in name_set.values() for n in names}),
            "gold": sorted(gold_pubs),
            "hard_negatives": [
                {"pub": pub, "neighbor": nid, "relation": rel}
                for pub, (nid, rel) in sorted(hard_neg.items())
            ],
            "n_gold": len(gold_pubs),
            "n_hard_neg": len(hard_neg),
            "gold_langs": gold_langs,
            "n_neighbors_in_corpus": len(neighbors_in_corpus),
        })

    _write_outputs(context, corpus_csv, concepts)
    print(
        f"Wrote {len(concepts)} concepts -> {output_dir / ALIAS_GRAPH_JSON}\n"
        f"  summary: {output_dir / MANIFEST_CSV}"
    )
    return 0


def _write_outputs(context: AppContext, corpus_csv: Path, concepts: List[dict]) -> None:
    """One JSON of id-only benchmark data + a tiny CSV summary (no document text)."""
    output_dir = context.workspace.ensure_dir(alias_dir(context))
    json_path = output_dir / ALIAS_GRAPH_JSON
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "corpus": str(corpus_csv),
                "id_field": context.schema.family_field,
                "n_concepts": len(concepts),
                "concepts": concepts,
            },
            fh, ensure_ascii=False, indent=2,
        )

    corpus_io.write_rows(
        output_dir / MANIFEST_CSV,
        (
            {**{k: entry[k] for k in MANIFEST_FIELDS if k != "gold_langs"},
             "gold_langs": "|".join(entry["gold_langs"])}
            for entry in concepts
        ),
        MANIFEST_FIELDS,
    )


def export_concept(context: AppContext, args: argparse.Namespace) -> int:
    """
    Materialize one concept's gold + hard-negative documents (all language
    versions, joined from the corpus) into a CSV for inspection -- the on-demand
    replacement for storing a CSV per concept.
    """
    schema = context.schema
    json_path = alias_json_path(context)
    corpus_csv = context.workspace.corpus_csv(getattr(args, "source", None) or DEFAULT_SOURCE)

    raw = str(args.concept)
    cid = raw if raw.upper().startswith("CHEBI:") else f"CHEBI:{raw}"
    if not json_path.exists():
        print(f"Cannot export {cid}: {json_path} not found; run `clir alias-graph build` first.")
        return 1

    entry = next(
        (c for c in load_concepts(json_path) if c["chebi_id"].upper() == cid.upper()), None
    )
    if entry is None:
        print(
            f"Cannot export {cid}: not found in {json_path}\n"
            f"(It may have been filtered out -- see {alias_dir(context) / MANIFEST_CSV} "
            "for available concepts.)"
        )
        return 1

    by_pub: Dict[str, List[dict]] = defaultdict(list)
    for row in corpus_io.read_rows(corpus_csv):
        by_pub[schema.family_of(row)].append(row)

    cname = entry["name"]
    out_rows: List[dict] = []
    for pub in entry["gold"]:
        for row in by_pub.get(pub, []):
            out_rows.append({
                **{k: row.get(k, "") for k in schema.fields},
                "role": "gold", "concept_chebi_id": cid, "concept_name": cname,
                "matched_chebi_id": cid, "relation": "self",
            })
    for neg in entry["hard_negatives"]:
        for row in by_pub.get(neg["pub"], []):
            out_rows.append({
                **{k: row.get(k, "") for k in schema.fields},
                "role": "hard_negative", "concept_chebi_id": cid, "concept_name": cname,
                "matched_chebi_id": neg["neighbor"], "relation": neg["relation"],
            })

    output_csv = json_path.parent / f"{cid.replace(':', '_')}__{_slug(cname)}.csv"
    corpus_io.write_rows(output_csv, out_rows, tuple(schema.fields) + EXTRA_FIELDS)
    n_gold = sum(1 for x in out_rows if x["role"] == "gold")
    print(
        f"Exported {cid} ({cname}): {n_gold} gold + {len(out_rows) - n_gold} "
        f"hard-neg doc rows -> {output_csv}"
    )
    return 0


__all__: List[str] = [
    "ALIAS_GRAPH_JSON",
    "DEFAULT_SOURCE",
    "EXTRA_FIELDS",
    "MANIFEST_CSV",
    "MATCH_FIELD",
    "MOLECULAR_ENTITY",
    "NameScan",
    "alias_dir",
    "alias_json_path",
    "build_alias_graph",
    "export_concept",
    "load_concepts",
    "qac_csv_path",
    "scan_with_names",
]
