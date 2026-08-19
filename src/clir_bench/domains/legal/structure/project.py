"""
Stage 6 -- verify the cross-language join and annotate edges with it.

The benchmark's claim is that article numbering is identical across language
versions by drafting rule, which makes cross-language alignment a structural
join on article number rather than anything semantic. This checks that claim per
act and quarantines any act where it fails.

A note on what "projecting to the other languages" means here. Edge endpoints are
ELI subdivision URIs, and those are *already* language-independent -- the French
version of Article 6 of the GDPR has the same ELI as the English one. So the edge
set does not get copied per language; duplicating 2,306 edges four times would
store the same fact four times and invite them to drift apart.

What is genuinely language-specific is the surface form and its character span,
and those stay marked as English, because that is the only language references
were extracted from. Each edge instead records which language versions of both
endpoints actually exist, which is the fact downstream stages need.

Usage:
    python -m clir_bench.domains.legal.structure.project
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from clir_bench.domains.legal.structure import ACT_LANGUAGES, paths


def load_inventories() -> dict[str, dict[str, set[str]]]:
    """celex -> language -> set of article numbers."""
    inventories: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    with paths.ARTICLES_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row["unit_type"] != "article":
                continue
            inventories[row["celex_id"]][row["language"]].add(row["article_number"])
    return inventories


def load_unit_ids() -> dict[str, dict[str, set[str]]]:
    """celex -> language -> set of unit ELI ids.

    Edges are no longer article-to-article only: annexes and recitals are both
    sources and targets. Membership is therefore checked against the ELI id of
    the unit itself, which works uniformly for all three unit types, rather than
    against article numbers, which only exist for one of them.
    """
    ids: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    with paths.ARTICLES_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("eli_id"):
                ids[row["celex_id"]][row["language"]].add(row["eli_id"])
    return ids


def verify(inventories: dict[str, dict[str, set[str]]]) -> tuple[set[str], list[dict]]:
    """(acts whose languages agree, quarantine records for those that do not)."""
    good: set[str] = set()
    quarantine: list[dict] = []
    for celex, per_language in sorted(inventories.items()):
        present = [lg for lg in ACT_LANGUAGES if per_language.get(lg)]
        missing = [lg for lg in ACT_LANGUAGES if lg not in present]
        reference = per_language.get("en") or per_language[present[0]]
        disagreeing = {lg: sorted(per_language[lg] ^ reference)
                       for lg in present if per_language[lg] != reference}
        if missing or disagreeing:
            quarantine.append({
                "celex_id": celex,
                "reason": "missing-language" if missing else "article-set-mismatch",
                "missing_languages": missing,
                "languages_present": present,
                "n_articles": {lg: len(per_language[lg]) for lg in present},
                "symmetric_difference": {lg: diff[:40] for lg, diff in disagreeing.items()},
            })
            continue
        good.add(celex)
    return good, quarantine


def annotate(good: set[str], inventories, unit_ids) -> tuple[int, int]:
    """Add the join result to each edge; drop edges whose act is quarantined."""
    counts = [0, 0]
    for index, path in enumerate((paths.INTERNAL_EDGES_JSONL, paths.EXTERNAL_REFS_JSONL)):
        if not path.exists():
            continue
        # Rewritten through a temporary file rather than read into memory: at
        # corpus scale these run to millions of rows.
        temporary = path.with_suffix(".jsonl.tmp")
        kept = 0
        with path.open(encoding="utf-8") as source_fh, \
                temporary.open("w", encoding="utf-8") as out_fh:
            for line in source_fh:
                row = json.loads(line)
                celex = row["source_celex"]
                if celex not in good:
                    continue
                # Membership is tested on the ELI ids of the endpoints, so the
                # same check covers article, annex and recital units alike. The
                # target is looked up in its own act: same as the source for
                # intra-act edges, but a row that names a ``target_celex`` (a
                # cross-act edge) must not be checked against the source act.
                per_language = unit_ids[celex]
                target_language = unit_ids[row.get("target_celex") or celex]
                source_id = row["source_article_id"]
                target_id = row.get("target_article_id")
                row["available_languages"] = [
                    lg for lg in ACT_LANGUAGES
                    if source_id in per_language.get(lg, set())
                    and (target_id is None or target_id in target_language.get(lg, set()))]
                row["surface_language"] = "en"
                out_fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                kept += 1
        temporary.replace(path)
        counts[index] = kept
    return counts[0], counts[1]


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    paths.ensure_dirs()

    inventories = load_inventories()
    unit_ids = load_unit_ids()
    good, quarantine = verify(inventories)

    with paths.QUARANTINE_JSONL.open("w", encoding="utf-8") as fh:
        for row in quarantine:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    internal, external = annotate(good, inventories, unit_ids)

    print(f"acts with a clean four-language join : {len(good)}")
    print(f"acts quarantined                     : {len(quarantine)}")
    for row in quarantine:
        print(f"  {row['celex_id']}  {row['reason']}  present={row['languages_present']}")
    print(f"\ninternal edges kept  {internal:,}")
    print(f"external refs kept   {external:,}")
    print(f"quarantine -> {paths.QUARANTINE_JSONL}")


if __name__ == "__main__":
    main()
