"""
Fetching and validating the multilingual concept names.

Two operations sit behind ``clir alias-graph names``:

``--cache-all``  pre-fill the ChEBI -> Wikipedia title cache for the whole
                 ontology rather than lazily for corpus hits only.

``--check``      quality-check those titles against real translated patents.
                 We attach a Wikipedia title per language to each concept via
                 the ChEBI->Wikidata P683->sitelink bridge. Are those titles the
                 words actually used in translated patents? For a concept
                 mentioned in an English document, take the *same patent's*
                 translation in language L and check whether the concept's
                 L-language Wikipedia title appears there.

                 Example: caffeine's German Wikipedia title is "Coffein". If the
                 German translation of an English caffeine patent contains
                 "Coffein", the name is good; if the German text instead says
                 "Koffein", we record a miss with the alternative surface, which
                 pinpoints the name-quality issue.

Each (concept, parallel-doc, language) check records:
  * wiki_present    -- the L Wikipedia title occurs in the L document
  * concept_present -- the concept occurs in the L document by *any* name
  * matched_instead -- the surface that matched when the Wikipedia title did not
The conditional rate wiki_present / concept_present isolates name quality from
patents whose translation simply does not mention the concept.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Set

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.domains.chem_patents.aliasgraph import chebi as chebi_mod
from clir_bench.domains.chem_patents.aliasgraph import wikidata
from clir_bench.domains.chem_patents.aliasgraph.builder import (
    DEFAULT_SOURCE,
    MATCH_FIELD,
    scan_with_names,
)
from clir_bench.domains.chem_patents.aliasgraph.matching import contains_name

# The check is anchored on English documents: it is the language every concept
# has a ChEBI primary name in, so a miss is attributable to the target language.
PIVOT_LANG = "en"

# Report columns. The trailing column is the corpus family key, which is what
# pins a check to one patent and its translations.
def _check_fields(family_field: str) -> tuple[str, ...]:
    return (
        "chebi_id", "concept_name", "lang", "wiki_title",
        "wiki_present", "concept_present", "matched_instead", family_field,
    )


def run_names_command(context: AppContext, args: argparse.Namespace) -> int:
    """Handler for ``clir alias-graph names``."""
    langs = list(getattr(args, "langs", None) or wikidata.DEFAULT_LANGS)
    cache_all = bool(getattr(args, "cache_all", False))
    check = bool(getattr(args, "check", False))

    if not (cache_all or check):
        print(
            "error: nothing to do; pass --cache-all to populate the name cache "
            "or --check to validate names against parallel translations",
            file=sys.stderr,
        )
        return 2

    if cache_all:
        wikidata.cache_all_names(context, langs=langs)
    if check:
        check_name_quality(context, langs=langs)
    return 0


def check_name_quality(
    context: AppContext,
    *,
    langs: Sequence[str] = wikidata.DEFAULT_LANGS,
    source: str = DEFAULT_SOURCE,
) -> dict:
    """Measure how often Wikipedia names appear in parallel translated docs."""
    schema = context.schema
    corpus_csv = context.workspace.corpus_csv(source)
    output_dir = context.workspace.report("wiki_name_quality")
    variant = chebi_mod.variant_for(context)
    target_langs = [lang for lang in langs if lang != PIVOT_LANG]

    print(f"Reading corpus: {corpus_csv}")
    rows = corpus_io.read_rows(corpus_csv)
    groups: Dict[str, Dict[str, dict]] = defaultdict(dict)
    for row in rows:
        groups[schema.family_of(row)][schema.language_of(row)] = row
    print(f"  {len(rows)} documents, {len(groups)} publications")

    scan = scan_with_names(context, rows, variant=variant, langs=langs)
    graph, wiki_names, match_info = scan.graph, scan.wiki_names, scan.match_info

    # Concepts detected in an English document, with their pivot publication.
    detected: Set[str] = set()
    en_concept_pubs: Dict[str, Set[str]] = defaultdict(set)
    for row in rows:
        if schema.language_of(row) != PIVOT_LANG:
            continue
        for cid in match_info.get(schema.id_of(row), {}):
            detected.add(cid)
            en_concept_pubs[cid].add(schema.family_of(row))
    print(f"  concepts detected in English docs: {len(detected)}")

    # One check per (concept, pivot publication, target language).
    checks: List[dict] = []
    for cid, pubs in en_concept_pubs.items():
        cname = graph.nodes[cid].get("name", cid)
        for lang in target_langs:
            title = wiki_names.get(cid, {}).get(lang)
            if not title:
                continue
            for pub in pubs:
                parallel = groups[pub].get(lang)
                if parallel is None:
                    continue
                wiki_present = contains_name(parallel.get(MATCH_FIELD) or "", title)
                pinfo = match_info.get(schema.id_of(parallel), {})
                concept_present = cid in pinfo
                matched_instead = (
                    pinfo[cid][0] if (concept_present and not wiki_present) else ""
                )
                checks.append({
                    "chebi_id": cid,
                    "concept_name": cname,
                    "lang": lang,
                    "wiki_title": title,
                    "wiki_present": int(wiki_present),
                    "concept_present": int(concept_present),
                    "matched_instead": matched_instead,
                    schema.family_field: pub,
                })

    summary = _summarize(checks, detected, wiki_names, target_langs)
    _write_outputs(
        context, output_dir, checks, summary, target_langs,
        fields=_check_fields(schema.family_field),
    )
    _print_summary(summary, target_langs)
    return summary


def _summarize(
    checks: List[dict],
    detected: Set[str],
    wiki_names: Dict[str, Dict[str, str]],
    target_langs: Sequence[str],
) -> dict:
    per_lang: Dict[str, dict] = {}
    for lang in target_langs:
        lc = [c for c in checks if c["lang"] == lang]
        n = len(lc)
        wiki_present = sum(c["wiki_present"] for c in lc)
        concept_present = sum(c["concept_present"] for c in lc)
        with_name = sum(1 for cid in detected if wiki_names.get(cid, {}).get(lang))
        per_lang[lang] = {
            "concepts_detected": len(detected),
            "concepts_with_wiki_name": with_name,
            "name_coverage": (with_name / len(detected)) if detected else 0.0,
            "checks": n,
            "wiki_present": wiki_present,
            "concept_present": concept_present,
            "wiki_hit_rate": (wiki_present / n) if n else 0.0,
            "concept_present_rate": (concept_present / n) if n else 0.0,
            "conditional_hit_rate": (wiki_present / concept_present) if concept_present else 0.0,
        }
    return {"per_lang": per_lang}


def _write_outputs(
    context: AppContext,
    output_dir: Path,
    checks: List[dict],
    summary: dict,
    target_langs: Sequence[str],
    *,
    fields: Sequence[str],
) -> None:
    context.workspace.ensure_dir(output_dir)
    corpus_io.write_rows(output_dir / "per_pair.csv", checks, fields)

    # Misses: concept present in the translation, but via a name other than the
    # Wikipedia title -> the Wikipedia name is a poor surface form here.
    misses = [c for c in checks if c["concept_present"] and not c["wiki_present"]]
    corpus_io.write_rows(
        output_dir / "misses.csv",
        sorted(misses, key=lambda c: (c["lang"], c["concept_name"])),
        fields,
    )

    lines = ["# Wikipedia-name quality check", ""]
    lines.append(
        "For a concept mentioned in an English patent, does its Wikipedia title in "
        "language L appear in the same patent's L translation?\n"
    )
    lines.append("| lang | name coverage | checks | wiki hit rate | concept present | conditional (wiki\\|present) |")
    lines.append("|------|---------------|--------|---------------|-----------------|------------------------------|")
    for lang in target_langs:
        s = summary["per_lang"][lang]
        lines.append(
            f"| {lang} | {s['concepts_with_wiki_name']}/{s['concepts_detected']} "
            f"({s['name_coverage']:.0%}) | {s['checks']} | "
            f"{s['wiki_present']}/{s['checks']} ({s['wiki_hit_rate']:.1%}) | "
            f"{s['concept_present_rate']:.1%} | {s['conditional_hit_rate']:.1%} |"
        )
    lines.append("")
    lines.append("- **wiki hit rate**: Wikipedia title found in the L translation.")
    lines.append("- **concept present**: the concept appears in the L translation by *any* name.")
    lines.append("- **conditional**: hit rate among docs where the concept is actually present "
                 "(isolates name quality from untranslated mentions).")
    lines.append("")
    lines.append("## Most common name mismatches (concept present, Wikipedia title absent)")
    lines.append("")
    top = Counter(
        (c["lang"], c["concept_name"], c["wiki_title"], c["matched_instead"])
        for c in misses if c["matched_instead"]
    )
    if top:
        lines.append("| lang | concept | Wikipedia title | matched instead | count |")
        lines.append("|------|---------|-----------------|-----------------|-------|")
        for (lang, cname, title, instead), cnt in top.most_common(40):
            lines.append(f"| {lang} | {cname} | {title} | {instead} | {cnt} |")
    else:
        lines.append("_None._")
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_summary(summary: dict, target_langs: Sequence[str]) -> None:
    print("\nWikipedia-name quality (Wikipedia title found in parallel L translation):")
    print(f"  {'lang':>4}  {'coverage':>9}  {'checks':>7}  {'wiki hit':>9}  {'present':>8}  {'conditional':>11}")
    for lang in target_langs:
        s = summary["per_lang"][lang]
        print(
            f"  {lang:>4}  {s['name_coverage']:>8.0%}  {s['checks']:>7}  "
            f"{s['wiki_hit_rate']:>8.1%}  {s['concept_present_rate']:>7.1%}  "
            f"{s['conditional_hit_rate']:>10.1%}"
        )


__all__ = ["check_name_quality", "run_names_command"]
