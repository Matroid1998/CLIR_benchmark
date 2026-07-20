"""
Publish the alias-graph benchmark.

Seven configs, because this benchmark asks a question the plain corpus/queries/
qrels triple cannot express -- can a retriever find the documents about a concept
*without being fooled by documents about chemically similar look-alikes*:

* ``queries``       carry the concept identity, its multilingual ``name_set``,
                    and the ``source_publication`` the query was written from.
* ``qrels``         mark gold documents (score 1) AND the designated look-alikes
                    (score 0). The zero-scored rows are the point: they name the
                    confusable documents a retriever is being tested against.
* ``source_qrels``  pin each query to the exact publication it was generated
                    from and that publication's translations, as distinct from
                    ``qrels``, which marks every document about the concept.
* ``hard_negatives`` name each look-alike's neighbour concept and relation, so
                    one can measure how often a wrong-but-similar compound
                    outranks the gold.
* ``concepts``      the full per-concept alias-graph record.

Everything is scoped to the concepts that actually have a generated query, so the
published dataset is self-consistent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.publish import DatasetBundle, build_card, publish_bundle
from clir_bench.domains.chem_patents.aliasgraph import chebi as chebi_mod
from clir_bench.domains.chem_patents.aliasgraph.builder import (
    DEFAULT_SOURCE,
    alias_dir,
    alias_json_path,
    load_concepts,
    qac_csv_path,
)

CONFIGS = (
    "corpus", "queries", "qrels", "source_qrels", "hard_negatives", "qac", "concepts",
)

CARD_TITLE = "Multi-lingual chemical QAC — Alias-Graph Retrieval benchmark"

CARD_DESCRIPTION = (
    "Given a chemistry concept (named in several languages), can a retriever find the "
    "documents that genuinely talk about it, across languages, **without being fooled by "
    "documents about chemically similar look-alike concepts**?\n\n"
    "Configs: `corpus` (gold + hard-negative documents), `queries` (technical questions "
    "about each concept, plus the concept's multilingual `name_set` and the "
    "`source_publication` each query was generated from), `qrels` (every document about "
    "the concept: gold docs = score 1, designated look-alike docs = score 0), "
    "`source_qrels` (the exact publication each query was generated from and its "
    "translations — the gold document in every language), `hard_negatives` (each "
    "look-alike's neighbor concept and `relation`), `qac` (full triplets), and `concepts` "
    "(the per-concept alias-graph record). Each config has a `train` split."
)


def publish_alias_graph(context: AppContext, args: argparse.Namespace) -> int:
    """Handler for ``clir alias-graph publish``."""
    repo_id = context.hf_repo("alias_graph_repo", getattr(args, "repo", None))
    if not repo_id:
        raise ValueError("no target repo: pass --repo or set alias_graph_repo in clir.toml")

    only_configs = list(getattr(args, "only_configs", None) or ()) or None
    if only_configs:
        unknown = sorted(set(only_configs) - set(CONFIGS))
        if unknown:
            raise ValueError(f"unknown config(s) for --only-configs: {unknown}")

    bundle = build_bundle(context)
    for name, rows in bundle.configs.items():
        print(f"  {name}: {len(rows)} rows")

    card = build_card(
        title=CARD_TITLE,
        description=CARD_DESCRIPTION,
        # The corpus documents are Google Patents text, so that is the licence
        # this dataset is published under regardless of which concepts it covers.
        attribution=context.domain.attribution_for(DEFAULT_SOURCE),
        bundle=bundle,
    )
    publish_bundle(
        bundle,
        repo_id,
        card=card,
        private=bool(getattr(args, "private", False)),
        dry_run=bool(getattr(args, "dry_run", False)),
        dry_run_dir=alias_dir(context) / "hf_export",
        only_configs=only_configs,
    )
    return 0


def build_bundle(context: AppContext) -> DatasetBundle:
    """Assemble the seven configs from alias_graph.json + the concept QAC CSV."""
    schema = context.schema
    concepts = load_concepts(alias_json_path(context))
    concept_by_cid = {c["chebi_id"]: c for c in concepts}

    qac_rows = corpus_io.read_rows(qac_csv_path(context))
    queried_cids = {r["chebi_id"] for r in qac_rows if r.get("chebi_id")}

    corpus_csv = context.workspace.corpus_csv(DEFAULT_SOURCE)
    docs_by_family: Dict[str, List[dict]] = {}
    for row in corpus_io.read_rows(corpus_csv):
        docs_by_family.setdefault(schema.family_of(row), []).append(row)

    # Only the documents the queried concepts actually reference are published;
    # the rest of the corpus lives in the shared haystack repo.
    needed: set[str] = set()
    for cid in queried_cids:
        concept = concept_by_cid.get(cid)
        if not concept:
            continue
        needed.update(concept.get("gold", []))
        needed.update(hn["pub"] for hn in concept.get("hard_negatives", []))

    corpus_data = [
        {
            "_id": schema.id_of(row),
            "title": row.get("title", ""),
            "text": schema.text_of(row),
            "corpus_language": schema.language_of(row),
            schema.family_field: family,
        }
        for family in sorted(needed)
        for row in docs_by_family.get(family, [])
    ]

    neighbor_names = _neighbor_name_map(context)
    queries_data: List[dict] = []
    qrels_data: List[dict] = []
    source_qrels_data: List[dict] = []
    hard_neg_data: List[dict] = []
    qac_data: List[dict] = []
    seen_qids: set[str] = set()

    for index, row in enumerate(qac_rows):
        cid = row.get("chebi_id", "")
        concept: Dict[str, Any] = concept_by_cid.get(cid, {})
        language = row.get("question_language", "")
        # The single publication this query was generated from (the gold document).
        source_family = str(row.get(schema.family_field) or "").strip()
        qid = f"{cid.replace(':', '_')}__{language}"
        if qid in seen_qids:
            qid = f"{qid}__{index}"
        seen_qids.add(qid)
        name_set_json = json.dumps(concept.get("name_set", {}), ensure_ascii=False)

        queries_data.append({
            "_id": qid, "text": row.get("question", ""), "query_language": language,
            "chebi_id": cid, "concept_name": row.get("concept_name", ""),
            "answer": row.get("answer", ""), "answer_language": row.get("answer_language", ""),
            "question_type": row.get("question_type", ""),
            "source_publication": source_family,
            "total_score": int(row.get("total_score") or 0),
            "faith_overall": int(row.get("faith_overall") or 0),
            "qual_overall": int(row.get("qual_overall") or 0),
            "name_set_json": name_set_json,
            "codes_json": json.dumps(concept.get("codes", []), ensure_ascii=False),
        })

        # Exact (query -> source publication) mapping: the gold document the query
        # was written from, plus its translations (one row per language variant).
        for doc in docs_by_family.get(source_family, []):
            source_qrels_data.append({
                "query-id": qid, "corpus-id": schema.id_of(doc),
                schema.family_field: source_family,
                "corpus_language": schema.language_of(doc),
            })

        gold = concept.get("gold", [])
        for family in gold:
            for doc in docs_by_family.get(family, []):
                qrels_data.append({"query-id": qid, "corpus-id": schema.id_of(doc), "score": 1.0})
        for hn in concept.get("hard_negatives", []):
            family, neighbor, relation = hn["pub"], hn.get("neighbor", ""), hn.get("relation", "")
            neighbor_name = (
                neighbor_names.get(neighbor) or concept_by_cid.get(neighbor, {}).get("name", "")
            )
            for doc in docs_by_family.get(family, []):
                qrels_data.append({"query-id": qid, "corpus-id": schema.id_of(doc), "score": 0.0})
                hard_neg_data.append({
                    "query-id": qid, "corpus-id": schema.id_of(doc),
                    schema.family_field: family,
                    "neighbor_chebi_id": neighbor, "neighbor_name": neighbor_name,
                    "relation": relation,
                })

        qac_data.append({
            "query_id": qid, "chebi_id": cid, "concept_name": row.get("concept_name", ""),
            "question": row.get("question", ""), "answer": row.get("answer", ""),
            "question_type": row.get("question_type", ""), "query_language": language,
            "source_publication": source_family,
            "total_score": int(row.get("total_score") or 0),
            "gold_pubs_json": json.dumps(gold, ensure_ascii=False),
            "n_gold": concept.get("n_gold", len(gold)),
            "n_hard_neg": concept.get("n_hard_neg", len(concept.get("hard_negatives", []))),
            "name_set_json": name_set_json,
        })

    concepts_data = [
        {
            "chebi_id": c["chebi_id"], "name": c["name"],
            "name_set_json": json.dumps(c.get("name_set", {}), ensure_ascii=False),
            "codes_json": json.dumps(c.get("codes", []), ensure_ascii=False),
            "gold_json": json.dumps(c.get("gold", []), ensure_ascii=False),
            "hard_negatives_json": json.dumps(c.get("hard_negatives", []), ensure_ascii=False),
            "gold_langs": "|".join(c.get("gold_langs", [])),
            "n_gold": c.get("n_gold", 0), "n_hard_neg": c.get("n_hard_neg", 0),
        }
        for c in concepts if c["chebi_id"] in queried_cids
    ]

    bundle = DatasetBundle()
    bundle.add("corpus", corpus_data)
    bundle.add("queries", queries_data)
    bundle.add("qrels", qrels_data)
    bundle.add("source_qrels", source_qrels_data)
    bundle.add("hard_negatives", hard_neg_data)
    bundle.add("qac", qac_data)
    bundle.add("concepts", concepts_data)
    return bundle


def _neighbor_name_map(context: AppContext) -> Dict[str, str]:
    """Best-effort chebi_id -> name map (for naming hard-negative look-alikes).

    Never fatal: a missing ChEBI cache leaves the look-alike names empty rather
    than blocking a publish of an otherwise complete dataset.
    """
    directory: Optional[Path] = chebi_mod.cache_dir(context)
    try:
        graph = chebi_mod.load_chebi_graph(directory, chebi_mod.variant_for(context))
    except Exception as exc:  # noqa: BLE001 - cache missing / load error
        print(f"  (neighbor names unavailable: {exc})")
        return {}
    return {nid: data.get("name", "") for nid, data in graph.nodes(data=True)}


__all__ = ["CONFIGS", "build_bundle", "publish_alias_graph"]
