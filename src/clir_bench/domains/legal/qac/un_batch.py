"""
Build a UN question set: select target blocks, generate, grade, rank, write.

One target block yields three candidates; the best-scoring one is kept. So a
100-query set is 100 target blocks: 100 generation calls plus 200 grading calls.

Selection is stratified by **document class** (the ``.ids`` body prefix). The
corpus is 45% General Assembly, 23% Security Council, 12% ECOSOC, 20% treaty
bodies and conference documents; the default mix keeps roughly that balance so
the set reads like the corpus rather than like whichever class happens to hash
first. One block per document by default -- with 86k documents there is no
reason to double up.

Filters applied before sampling:

* only blocks inside the token window (``in_range``) become targets -- the
  out-of-window remainder exists so documents stay reconstructable, not to be
  queried;
* documents whose only content is one undersized block (agendas, cover notes)
  drop out with the same filter.

Usage:
    python -m clir_bench.domains.legal.qac.un_batch --n 100 --dry-run
    python -m clir_bench.domains.legal.qac.un_batch --n 100 --workers 8
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from clir_bench.domains.legal.un import paths as un_paths
from clir_bench.domains.legal.qac import un_context as ctx
from clir_bench.domains.legal.qac import un_generate as gen
from clir_bench.domains.legal.qac.env import load_env

OUT_DIR = un_paths.QAC_DIR

# (name, body prefixes, share of the set). Prefix None catches everything else.
DEFAULT_STRATA: tuple[tuple[str, tuple[str, ...] | None, float], ...] = (
    ("ga", ("a",), 0.40),
    ("sc", ("s",), 0.25),
    ("ecosoc", ("e",), 0.10),
    ("other", None, 0.25),
)


@dataclass
class Target:
    doc_id: str
    block_id: str
    block_index: int
    n_blocks: int
    stratum: str
    mode: str
    language: str


def _stratum_for(body: str, strata=DEFAULT_STRATA) -> str:
    for name, prefixes, _ in strata:
        if prefixes is not None and body in prefixes:
            return name
    return next(name for name, prefixes, _ in strata if prefixes is None)


def select(index: ctx.BlockIndex, *, n: int, seed: int, languages: Sequence[str],
           modes: Sequence[str], strata=DEFAULT_STRATA,
           max_per_doc: int = 1) -> list[Target]:
    """Stratified, deterministic target selection.

    Documents are ranked per stratum by a seeded hash; blocks are loaded only
    for documents actually reached, so selection cost scales with ``n``, not
    with the corpus.
    """
    def rank(key: str) -> str:
        return hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()

    pools: dict[str, list[str]] = {name: [] for name, _, _ in strata}
    for doc_id, doc in index.docs.items():
        if doc.get("n_in_range", 0) < 1:
            continue
        pools[_stratum_for(doc.get("body", ""), strata)].append(doc_id)

    chosen: list[Target] = []
    for name, _, share in strata:
        want = round(n * share)
        taken = 0
        for doc_id in sorted(pools[name], key=rank):
            if taken >= want:
                break
            eligible = [b for b in index.blocks_for(doc_id) if b.in_range]
            eligible.sort(key=lambda b: rank(b.block_id))
            for block in eligible[:max_per_doc]:
                if taken >= want:
                    break
                position = len(chosen)
                chosen.append(Target(
                    doc_id=doc_id, block_id=block.block_id,
                    block_index=block.block_index, n_blocks=block.n_blocks,
                    stratum=name,
                    # Alternate deterministically so the set is balanced across
                    # modes and question languages rather than randomly lumpy.
                    mode=modes[position % len(modes)],
                    language=languages[position % len(languages)],
                ))
                taken += 1
    return chosen


def run_one(target: Target, index: ctx.BlockIndex, *, gen_model: str,
            grade_model: str, context_chars: int, keep: int) -> list[dict[str, Any]]:
    from clir_bench.core.llm import call_with_retries, client_for
    from clir_bench.core.grading import (GraderConfig, grade_columns,
                                         grade_faithfulness, grade_quality,
                                         rank_candidates)

    payload = index.build(target.doc_id, target.block_index,
                          context_chars=context_chars,
                          languages=ctx.payload_languages(target.language))
    if payload is None:
        return []
    grader = GraderConfig(model=grade_model, reasoning_effort="low")
    gen_client, grade_client = client_for(gen_model), client_for(grade_model)

    candidates = call_with_retries(
        lambda: gen.generate(payload, mode=target.mode, language=target.language,
                             model=gen_model, client=gen_client),
        retries=3, label=f"gen {target.block_id}")
    if not candidates:
        return []

    qa = [{"question": c.question, "answer": c.answer} for c in candidates]
    faith = call_with_retries(lambda: grade_faithfulness(
        grade_client, grader, gen.PROMPTS.faithfulness("batch"), payload.text, qa),
        retries=3, label="faith")
    quality = call_with_retries(lambda: grade_quality(
        grade_client, grader, gen.PROMPTS.quality(target.mode, "batch"),
        payload.text, qa, target.mode), retries=3, label="quality")

    # Ranked best-first; row order carries the ranking, exactly as in
    # eurlex_batch: the whole list goes to the all-candidates file and the
    # first row of each target to the best-only file.
    ranked = rank_candidates(qa, faith, quality, target.mode)
    order = {c["question"]: i for i, c in enumerate(qa)}
    rows: list[dict[str, Any]] = []
    for graded in ranked[:keep]:
        candidate = candidates[order[graded.qa["question"]]]
        row = {
            "doc_id": target.doc_id,
            "symbol": payload.target.symbol,
            "block_id": target.block_id,
            "block_index": target.block_index,
            "n_blocks": target.n_blocks,
            "line_start": payload.target.line_start,
            "line_end": payload.target.line_end,
            "stratum": target.stratum,
            "context_blocks_supplied": len(payload.context_blocks),
            "context_blocks_dropped": payload.n_context_dropped,
            "question_language": target.language,
            "mode": target.mode,
            "question": candidate.question,
            "answer": candidate.answer,
            "question_type": candidate.classification if target.mode == "technical" else "",
            "framing": candidate.classification if target.mode == "semantic" else "",
        }
        # Every score the verifiers returned, not just the aggregates: the
        # three faithfulness sub-criteria, the five mode-specific quality
        # sub-criteria, both overalls, the failure type, and both reasons.
        row.update(grade_columns(graded.faith, graded.quality, target.mode))
        rows.append(row)
    return rows


# Grade columns are the union of both modes' rubrics (grade_columns emits only
# the scoring mode's keys; DictWriter leaves the other mode's cells empty).
FIELDS = ("doc_id", "symbol", "block_id", "block_index", "n_blocks",
          "line_start", "line_end", "stratum",
          "context_blocks_supplied", "context_blocks_dropped",
          "question_language", "mode", "question", "answer",
          "question_type", "framing",
          "faith_grounding", "faith_precision", "faith_numerical_fidelity",
          "faith_overall",
          "qual_search_bar_realism", "qual_specificity", "qual_phrasing_economy",
          "qual_focus",
          "qual_search_realism", "qual_lexical_distance",
          "qual_conceptual_framing", "qual_retrievability",
          "qual_linguistic_quality", "qual_overall",
          "faith_reason", "qual_failure_type", "qual_reason", "total_score")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=100,
                        help="target blocks (= queries when keep=1)")
    parser.add_argument("--keep", type=int, default=3,
                        help="candidates written to the all-candidates file")
    parser.add_argument("--languages", default="en")
    parser.add_argument("--modes", default="technical,semantic")
    parser.add_argument("--gen-model", default="gpt-5.5")
    parser.add_argument("--grade-model", default="anthropic/claude-sonnet-5")
    parser.add_argument("--context-chars", type=int, default=ctx.DEFAULT_CONTEXT_CHARS)
    parser.add_argument("--max-per-doc", type=int, default=1)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--blocks", default=None, help="override blocks_en.jsonl path")
    parser.add_argument("--docs", default=None, help="override docs_en.jsonl path")
    parser.add_argument("--out", default=str(OUT_DIR / "qac_un.csv"))
    parser.add_argument("--dry-run", action="store_true",
                        help="show the selected targets and the call budget, make no calls")
    args = parser.parse_args()
    load_env()

    languages = [x.strip() for x in args.languages.split(",") if x.strip()]
    modes = [x.strip() for x in args.modes.split(",") if x.strip()]

    index = ctx.BlockIndex(blocks_path=args.blocks, docs_path=args.docs)
    targets = select(index, n=args.n, seed=args.seed, languages=languages,
                     modes=modes, max_per_doc=args.max_per_doc)

    print(f"selected {len(targets)} target blocks "
          f"across {len({t.doc_id for t in targets})} documents", file=sys.stderr)
    print(f"  by stratum : {dict(Counter(t.stratum for t in targets))}", file=sys.stderr)
    print(f"  by language: {dict(Counter(t.language for t in targets))}", file=sys.stderr)
    print(f"  by mode    : {dict(Counter(t.mode for t in targets))}", file=sys.stderr)

    if args.dry_run:
        print(f"\ncall budget: {len(targets)} generation + {2 * len(targets)} grading "
              f"= {3 * len(targets)} calls", file=sys.stderr)
        for t in targets[:12]:
            print(f"   {t.block_id:<40} {t.stratum:<8} {t.mode:<9} {t.language}",
                  file=sys.stderr)
        print("   ...", file=sys.stderr)
        return

    # Build the clients before spending an hour discovering the key is missing.
    from clir_bench.core.llm import client_for
    for model in (args.gen_model, args.grade_model):
        try:
            client_for(model)
        except Exception as error:  # noqa: BLE001
            raise SystemExit(f"cannot reach {model}: {error}") from error

    from clir_bench.core.parallel import run_tasks
    rows: list[dict[str, Any]] = []
    failed = 0
    for result in run_tasks(
            targets,
            lambda t: (t, _safe(run_one, t, index, gen_model=args.gen_model,
                                grade_model=args.grade_model,
                                context_chars=args.context_chars, keep=args.keep)),
            workers=args.workers, description="generating"):
        _, produced = result
        if produced is None:
            failed += 1
        else:
            rows.extend(produced)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Rows arrive grouped per target, best-first within each group; only the
    # grouping is normalised here. Within-target order is the ranking.
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["block_id"], []).append(row)

    ordered = [r for key in sorted(grouped) for r in grouped[key]]
    best = [grouped[key][0] for key in sorted(grouped)]

    def write(path: Path, data: list[dict[str, Any]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(data)

    best_path = out.with_name(out.stem + "_best" + out.suffix)
    write(out, ordered)
    write(best_path, best)

    if not rows:
        raise SystemExit(
            f"no queries produced: all {len(targets)} targets failed. "
            "The output file contains only a header. See the errors above.")

    if failed:
        print(f"  WARNING: {failed} of {len(targets)} targets failed", file=sys.stderr)

    print(f"\nwrote {len(ordered)} candidates -> {out}", file=sys.stderr)
    print(f"      {len(best)} best-per-target -> {best_path}", file=sys.stderr)
    print(f"  targets that failed  : {failed}", file=sys.stderr)
    print(f"  by stratum (best set): {dict(Counter(r['stratum'] for r in best))}",
          file=sys.stderr)


def _safe(fn, *a, **kw):
    """A failing block must not abort a 100-block build."""
    try:
        return fn(*a, **kw)
    except Exception as error:  # noqa: BLE001
        print(f"    target failed: {type(error).__name__}: {str(error)[:120]}",
              file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
