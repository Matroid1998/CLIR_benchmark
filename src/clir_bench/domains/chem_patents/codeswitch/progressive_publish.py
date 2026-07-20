"""
Publish the progressive ladder in MTEB retrieval shape.

Three configs, and the shape differs from the standard retrieval bundle in one
way that matters: qrels carry the ladder ``depth`` of each gold document. Every
rung of a base is relevant to that base's query, so a plain qrels file would
score depth 0 and depth 5 identically; the depth column is what lets the eval
read a dose off each judgement.

The retrieval haystack at eval time is the shared corpus PLUS these variant
documents, so this dataset carries only the variants, the queries and the qrels.
``text`` is composed the same way the shared corpus composes it, so a document
encodes identically whichever side it is loaded from.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.publish import DatasetBundle, build_card, publish_bundle
from clir_bench.domains.chem_patents.codeswitch import progressive

CARD_DESCRIPTION = (
    "Progressive code-switching retrieval-decay benchmark. Each base patent yields a "
    "cumulative ladder of documents (`base__r0` clean through `base__rN`), where each step "
    "swaps one more chemistry term into another language, spelling or ontology form. One "
    "fixed question per base (about the step-1 term) is reused at every depth, and the "
    "`qrels` carry that depth, so you can measure how retrieval decays as more terms are "
    "code-switched.\n\n"
    "The retrieval haystack is this `corpus` plus a shared patent corpus supplied at "
    "evaluation time."
)


def _corpus_config(rows: list[dict[str, str]], context: AppContext) -> list[dict[str, Any]]:
    schema = context.schema
    out: list[dict[str, Any]] = []
    for row in rows:
        depth = int(row["n_replacements"])
        steps = json.loads(row.get("replacements_json") or "[]")
        out.append(
            {
                "_id": schema.id_of(row),
                "title": row.get("title", ""),
                "text": row.get("context") or row.get("abstract") or "",
                # The ladder's documents are all in the anchor language; the
                # source corpus ``language`` column is carried through unchanged
                # from the base row, so the anchor is the authoritative one.
                "corpus_language": str(row.get("anchor_language", "")).strip(),
                "base_id": row["base_id"],
                "depth": depth,
                # The mode added at THIS rung, i.e. the last applied step.
                "mode_added": steps[-1]["mode"] if depth >= 1 and steps else "",
                "source_publication_number": str(
                    row.get("source_publication_number", "")
                ).strip(),
            }
        )
    return out


def _query_configs(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """One query row per (base, language); one qrels row per (query, rung)."""
    queries: list[dict[str, Any]] = []
    seen: set[str] = set()
    qrels: list[dict[str, Any]] = []
    for row in rows:
        query_id = row.get("query_id") or row["base_id"]
        if query_id not in seen:
            seen.add(query_id)
            queries.append(
                {
                    "_id": query_id,
                    "text": row.get("question", ""),
                    "query_language": str(row.get("query_language", "")).strip(),
                    "base_id": row["base_id"],
                    "strategy": str(row.get("strategy", "")).strip(),
                    "concept_chebi_id": str(row.get("concept_chebi_id", "")).strip(),
                    "term_used": row.get("term_used", ""),
                }
            )
        qrels.append(
            {
                "query-id": query_id,
                "corpus-id": row["gold_id"],
                "score": 1.0,
                "depth": int(row["n_replacements"]),
            }
        )
    return queries, qrels


def publish_progressive(context: AppContext, args: argparse.Namespace) -> int:
    """Push corpus/queries/qrels to the Hub (or write parquet on ``--dry-run``)."""
    workdir = context.workspace.data("progressive")
    corpus_rows = corpus_io.read_rows(workdir / progressive.CORPUS_FILENAME)
    qac_rows = corpus_io.read_rows(workdir / progressive.QAC_FILENAME)

    queries, qrels = _query_configs(qac_rows)
    bundle = DatasetBundle()
    bundle.add("corpus", _corpus_config(corpus_rows, context))
    bundle.add("queries", queries)
    bundle.add("qrels", qrels)

    source = getattr(args, "source", "gp")
    card = build_card(
        title="Progressive code-switching",
        description=CARD_DESCRIPTION,
        attribution=context.domain.attribution_for(source),
        bundle=bundle,
    )

    repo = context.hf_repo("progressive_repo", args.repo)
    if not repo:
        raise ValueError("no target repo: pass --repo or set progressive_repo in clir.toml")

    publish_bundle(
        bundle,
        repo,
        card=card,
        private=args.private,
        dry_run=args.dry_run,
        dry_run_dir=workdir / "hf_export",
    )
    return 0


__all__ = ["CARD_DESCRIPTION", "publish_progressive"]
