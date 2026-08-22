"""
Build a UN question set: select target blocks, generate, grade, rank, write.

One target block yields three candidates; the best-scoring one is kept. So a
100-query set is 100 target blocks: 100 generation calls plus 200 grading calls.

Selection is stratified by **genre** with user-fixed shares: resolutions &
decisions 50%, meeting records 40%, letters 10% (``GENRE_STRATA``; override
with ``--shares``, or ``--all-genres`` for the unfiltered pool). Within a
stratum the sampling unit is the **block**, ranked by a seeded hash of its
block id -- documents contribute targets in proportion to their content, the
same way the EUR-Lex batch samples articles (``--max-per-doc`` remains a
safety knob, default uncapped).

Filters applied before sampling:

* **genre filter** -- only resolutions/decisions, meeting records, and
  letters become question sources (``genre_for``); everything else, plus the
  logistics classes (agenda stubs, the daily Journal, corrigenda), is
  excluded;
* **whole-fit filter** -- a target qualifies only when its whole document
  PLUS the whole text of every referenced document stays inside the 30k-char
  context budget (``_fits_whole``, checked lazily along the ranked walk), so
  nothing the model sees is ever windowed or truncated; references are then
  rendered as full documents (``--no-fit`` reverts to windowed context and
  capped excerpts);
* only blocks inside the token window (``in_range``) AND free of Layer-2
  shape flags (``usable``) become targets -- the builder records the
  surviving indices per document (``target_idxs``), so pool enumeration
  never scans the 2.6 GB blocks file.

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
from clir_bench.domains.legal.qac import un_references as refs
from clir_bench.domains.legal.qac.env import load_env

OUT_DIR = un_paths.QAC_DIR

# Question-source genres and their shares of the set (user-fixed 50/40/10).
# Measured pool under both filters: resolutions 30,043 targets / meeting
# records 31,072 / letters 2,416 -- the letters quota of a 10k set uses ~41%
# of what exists, the other two are barely dented.
GENRE_STRATA: tuple[tuple[str, float], ...] = (
    ("resolution", 0.50),
    ("meeting", 0.40),
    ("letter", 0.10),
)

# The reject floor: a candidate whose faithfulness grader gave GROUNDING <= 2
# was judged NOT fully answerable from the target block (substance drawn from a
# referenced document, the context, or outside knowledge). Such a candidate is
# never kept as a target's best question; if none of the three clears the
# floor, the target yields no question at all. All candidates and grades are
# still written to the all-candidates file, so rejects stay auditable.
MIN_GROUNDING_FOR_BEST = 3

# The fit filter: a target qualifies only when its whole document PLUS the
# whole text of every referenced document stays inside the context budget --
# then nothing the model sees is ever truncated or windowed.
FIT_BUDGET = ctx.DEFAULT_CONTEXT_CHARS


def genre_for(doc_id: str, title: str) -> str | None:
    """Question-source genre, or None when the document class is ineligible.

    Letters are recognised by their title line and undercounted when that line
    is corrupted -- a safe direction: never misclassifies, only misses.
    """
    if "/res/" in doc_id or "/dec/" in doc_id:
        return "resolution"
    if "sr_" in doc_id or "pv_" in doc_id:
        return "meeting"
    if title.lower().startswith(("letter dated", "note verbale", "identical letters")):
        return "letter"
    return None


def _fits_whole(doc: dict, block_text: str, index: ctx.BlockIndex) -> bool:
    """Whole document + whole referenced documents within the context budget."""
    if doc["char_count"] > FIT_BUDGET:
        return False
    citations = refs.resolve_citations(
        refs.extract_citations(block_text),
        getattr(index, "symbols", None) or index.symbol_map,
        citing_doc_id=doc["doc_id"])
    kept, _ = refs.referenced_docs(citations)
    total = doc["char_count"] + sum(
        index.docs[c.doc_id]["char_count"] for c in kept)
    return total <= FIT_BUDGET


@dataclass
class Target:
    doc_id: str
    block_id: str
    block_index: int
    n_blocks: int
    stratum: str
    mode: str
    language: str
    reference_complete: bool = True
    n_unresolved: int = 0
    unresolved_reasons: str = ""    # "reason:count;..." for gated-in blocks


def _excluded_doc(doc_id: str) -> bool:
    """Layer 0: document classes that cannot anchor questions.

    Agenda stubs and the Journal are meeting logistics; corrigenda are edit
    instructions ("Replace paragraph X with...") about a *different* document
    -- both sampled corrigendum targets in the verification audit were bad.
    """
    pieces = doc_id.split("/")
    body = pieces[1] if len(pieces) > 1 else ""
    return ("/agenda/" in doc_id or body.startswith("journal")
            or any(p.startswith("corr") for p in pieces[2:]))


def select(index: ctx.BlockIndex, *, n: int, seed: int, languages: Sequence[str],
           modes: Sequence[str], strata=GENRE_STRATA,
           max_per_doc: int = 0, genre_filter: bool = True,
           fit_filter: bool = True, require_complete: bool = True) -> list[Target]:
    """Stratified, deterministic, block-level target selection.

    The pool is enumerated from the docs index alone (``target_idxs``) and
    ranked by a seeded hash of the block id; documents contribute in
    proportion to their eligible-block count. The fit check is applied lazily
    while walking the ranked pool -- only candidates actually reached get
    their block text read and citations resolved, so cost scales with ``n``.
    ``max_per_doc`` is a safety cap only; 0 means uncapped.

    ``require_complete`` restricts the pool to reference-complete blocks: a
    block citing anything that could not be resolved -- another document
    outside the corpus, a treaty article, an annex that cannot be pinned down
    -- is not a question target. Needs ``reference_status_en.jsonl``.
    """
    def rank(key: str) -> str:
        return hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()

    incomplete = index.incomplete
    if require_complete and incomplete is None:
        raise SystemExit(
            "reference_status_en.jsonl not found: run "
            "`python -m clir_bench.domains.legal.un.references_status` "
            "or pass --allow-incomplete")
    if not require_complete and incomplete is None:
        incomplete = {}

    if not genre_filter:
        strata = (("all", 1.0),)
    pools: dict[str, list[tuple[str, int]]] = {name: [] for name, _ in strata}
    missing_idxs = 0
    for doc_id, doc in index.docs.items():
        if _excluded_doc(doc_id):
            continue
        idxs = doc.get("target_idxs")
        if idxs is None:
            missing_idxs += 1
            continue
        if fit_filter and doc["char_count"] > FIT_BUDGET:
            continue
        if genre_filter:
            stratum = genre_for(doc_id, doc.get("title", ""))
            if stratum is None:
                continue
        else:
            stratum = "all"
        if require_complete:
            idxs = [idx for idx in idxs
                    if f"{doc_id}#{idx}" not in incomplete]
        pools[stratum].extend((doc_id, idx) for idx in idxs)
    if missing_idxs and not any(pools.values()):
        raise SystemExit(
            "docs index has no target_idxs -- rebuild the blocks "
            "(python -m clir_bench.domains.legal.un.blocks)")

    chosen: list[Target] = []
    per_doc: Counter = Counter()
    for name, share in strata:
        want = round(n * share)
        taken = 0
        for doc_id, idx in sorted(pools[name], key=lambda p: rank(f"{p[0]}#{p[1]}")):
            if taken >= want:
                break
            if max_per_doc and per_doc[doc_id] >= max_per_doc:
                continue
            doc = index.docs[doc_id]
            if fit_filter and not _fits_whole(
                    doc, index.blocks_for(doc_id)[idx].texts["en"], index):
                continue
            per_doc[doc_id] += 1
            position = len(chosen)
            status = incomplete.get(f"{doc_id}#{idx}")
            chosen.append(Target(
                doc_id=doc_id, block_id=f"{doc_id}#{idx}",
                block_index=idx, n_blocks=doc["n_blocks"],
                stratum=name,
                # Alternate deterministically so the set is balanced across
                # modes and question languages rather than randomly lumpy.
                mode=modes[position % len(modes)],
                language=languages[position % len(languages)],
                reference_complete=status is None,
                n_unresolved=(sum(status.get("reasons", {}).values())
                              if status else 0),
                unresolved_reasons=";".join(
                    f"{k}:{v}" for k, v in
                    (status.get("reasons", {}) if status else {}).items()),
            ))
            taken += 1
    return chosen


def run_one(target: Target, index: ctx.BlockIndex, *, gen_model: str,
            grade_model: str, context_chars: int, keep: int,
            reference_chars: int | None = None) -> list[dict[str, Any]]:
    from clir_bench.core.llm import call_with_retries, client_for
    from clir_bench.core.grading import (GraderConfig, grade_columns,
                                         grade_faithfulness, grade_quality,
                                         rank_candidates)

    # reference_chars=None renders each referenced document WHOLE -- safe
    # because the fit filter guaranteed doc + references fit the budget.
    payload = index.build(target.doc_id, target.block_index,
                          context_chars=context_chars,
                          reference_chars=reference_chars,
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
            "references_supplied": ",".join(r.symbol for r in payload.references),
            "references_dropped": ",".join(payload.dropped_references),
            "reference_complete": target.reference_complete,
            "n_unresolved": target.n_unresolved,
            "unresolved_reasons": target.unresolved_reasons,
        }
        # Every score the verifiers returned, not just the aggregates: the
        # three faithfulness sub-criteria, the five mode-specific quality
        # sub-criteria, both overalls, the failure type, and both reasons.
        row.update(grade_columns(graded.faith, graded.quality, target.mode))
        rows.append(row)
    return rows


def pick_best(grouped: dict[str, list[dict[str, Any]]]
              ) -> tuple[list[dict[str, Any]], int]:
    """(best rows, rejected-target count).

    Each group is one target's candidates, ranked best-first. The best is the
    first candidate whose GROUNDING clears ``MIN_GROUNDING_FOR_BEST``; a target
    with no such candidate contributes nothing to the best file.
    """
    best: list[dict[str, Any]] = []
    rejected = 0
    for key in sorted(grouped):
        for row in grouped[key]:
            try:
                grounding = int(row.get("faith_grounding") or 0)
            except (TypeError, ValueError):
                grounding = 0
            if grounding >= MIN_GROUNDING_FOR_BEST:
                best.append(row)
                break
        else:
            rejected += 1
    return best, rejected


# Grade columns are the union of both modes' rubrics (grade_columns emits only
# the scoring mode's keys; DictWriter leaves the other mode's cells empty).
FIELDS = ("doc_id", "symbol", "block_id", "block_index", "n_blocks",
          "line_start", "line_end", "stratum",
          "context_blocks_supplied", "context_blocks_dropped",
          "question_language", "mode", "question", "answer",
          "question_type", "framing",
          "references_supplied", "references_dropped",
          "reference_complete", "n_unresolved", "unresolved_reasons",
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
    parser.add_argument("--shares", default=None,
                        help="genre shares as resolution,meeting,letter "
                             "(e.g. 0.5,0.4,0.1)")
    parser.add_argument("--all-genres", action="store_true",
                        help="disable the genre filter (uniform pool)")
    parser.add_argument("--no-fit", action="store_true",
                        help="disable the whole-document fit filter; references "
                             "fall back to capped excerpts")
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="also sample blocks whose citations are not all resolved")
    parser.add_argument("--max-per-doc", type=int, default=0,
                        help="safety cap on targets per document (0 = uncapped; "
                             "documents contribute proportionally to size)")
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

    strata = GENRE_STRATA
    if args.shares:
        values = [float(x) for x in args.shares.split(",")]
        if len(values) != len(GENRE_STRATA):
            raise SystemExit(f"--shares needs {len(GENRE_STRATA)} values "
                             f"({', '.join(n for n, _ in GENRE_STRATA)})")
        strata = tuple(zip((name for name, _ in GENRE_STRATA), values))

    index = ctx.BlockIndex(blocks_path=args.blocks, docs_path=args.docs)
    if index.incomplete is not None:
        status_mtime = ctx.paths.REFERENCE_STATUS_JSONL.stat().st_mtime
        blocks_file = Path(args.blocks or ctx.paths.BLOCKS_JSONL)
        if blocks_file.exists() and blocks_file.stat().st_mtime > status_mtime:
            print("WARNING: blocks_en.jsonl is newer than reference_status_en.jsonl "
                  "-- re-run clir_bench.domains.legal.un.references_status",
                  file=sys.stderr)
    targets = select(index, n=args.n, seed=args.seed, languages=languages,
                     modes=modes, strata=strata, max_per_doc=args.max_per_doc,
                     genre_filter=not args.all_genres,
                     fit_filter=not args.no_fit,
                     require_complete=not args.allow_incomplete)

    print(f"selected {len(targets)} target blocks "
          f"across {len({t.doc_id for t in targets})} documents", file=sys.stderr)
    print(f"  by stratum : {dict(Counter(t.stratum for t in targets))}", file=sys.stderr)
    print(f"  by language: {dict(Counter(t.language for t in targets))}", file=sys.stderr)
    print(f"  by mode    : {dict(Counter(t.mode for t in targets))}", file=sys.stderr)
    if index.incomplete is not None:
        print(f"  reference-complete: {sum(1 for t in targets if t.reference_complete)}"
              f"/{len(targets)}; incomplete blocks known to the gate: "
              f"{len(index.incomplete):,}", file=sys.stderr)

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
                                context_chars=args.context_chars, keep=args.keep,
                                reference_chars=(refs.DEFAULT_REFERENCE_CHARS
                                                 if args.no_fit else None))),
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
    best, rejected = pick_best(grouped)

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
    print(f"  targets rejected (no candidate with grounding >= "
          f"{MIN_GROUNDING_FOR_BEST}): {rejected}", file=sys.stderr)
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
