"""
Build a EUR-Lex question set: select target articles, generate, grade, rank, write.

One target article yields three candidates; the best-scoring one is kept. So a
100-query set is 100 target articles, and the run costs 100 generation calls plus
200 grading calls.

Selection is stratified by **reference count** -- same-act articles, other
acts' articles and annexes together, since all of them travel with the target
-- and records the
stratum on every row so the resulting set can be re-weighted or split later.
Measured on the reference-complete eligible pool (16.9k articles): 36% cite no
other article and 64% cite at least one (one 21%, two-three 23%, four-plus 19%).
The default mix therefore *under*-samples citing articles (``CROSS_REFERENCE_SHARE``
below): the no-reference control must dominate, and multi-article gold is meant
to be a measured minority rather than the norm.

Filters applied before sampling, each for a reason found the hard way:

* acts in ``quarantine.jsonl`` are excluded -- their article numbering disagrees
  across languages, so an article id there is not reliably the same article in
  all four;
* amending articles are excluded by default -- they quote the text of *another*
  act, so a question drawn from one is about a document that is not in the corpus;
* very short and very long articles are excluded -- the first cannot support
  three distinct questions, the second buries the operative fact;
* articles whose citation graph is not **reference-complete** are excluded by
  default (``reference_status.jsonl`` from ``structure.resolve_external``): if
  any article the target cites could not be resolved -- another act outside the
  corpus, the Treaty, "of that Regulation" -- the generator would be writing
  about text it only half saw. ``--allow-incomplete`` lifts this.

Usage:
    python -m clir_bench.domains.legal.qac.eurlex_batch --n 100 --dry-run
    python -m clir_bench.domains.legal.qac.eurlex_batch --n 100 --workers 8
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from clir_bench.domains.legal.structure import ACT_LANGUAGES
from clir_bench.domains.legal.structure import paths as struct_paths
from clir_bench.domains.legal.qac import eurlex_context as ctx
from clir_bench.domains.legal.qac import eurlex_generate as gen
from clir_bench.domains.legal.qac.env import load_env

OUT_DIR = struct_paths.EURLEX_DIR / "qac"

# (name, min refs, max refs, share of the set). Only this share of the set is
# drawn from articles that cite another article (same act or another act in the
# corpus); the rest have no references at all and act as the control that must
# never produce a multi-article answer. Cross-referenced questions are the
# interesting minority, not the norm: 64% of the eligible pool cites something,
# so 0.20 is a deliberate under-sampling that keeps multi-article gold a measured
# minority. Raise it with --cross-ref-share when the reference graph is the point.
CROSS_REFERENCE_SHARE = 0.20

DEFAULT_STRATA: tuple[tuple[str, int, int, float], ...] = (
    ("no_refs", 0, 0, 1 - CROSS_REFERENCE_SHARE),
    ("one_ref", 1, 1, CROSS_REFERENCE_SHARE * 0.40),
    ("few_refs", 2, 3, CROSS_REFERENCE_SHARE * 0.35),
    ("many_refs", 4, 99, CROSS_REFERENCE_SHARE * 0.25),
)

MIN_CHARS, MAX_CHARS = 600, 9000


@dataclass
class Target:
    eli_id: str
    celex_id: str
    article_number: str
    n_refs: int            # same-act references
    stratum: str
    mode: str
    language: str
    n_external: int = 0    # resolved references to articles of other acts
    n_annex: int = 0       # resolved annex references (this act or another)
    complete: bool = True  # every citation resolved (reference_status)
    cites_annex: bool = False


def _quarantined() -> set[str]:
    path = struct_paths.QUARANTINE_JSONL
    if not path.exists():
        return set()
    return {json.loads(line)["celex_id"] for line in path.open(encoding="utf-8")}


def select(index: ctx.ArticleIndex, *, n: int, seed: int, languages: Sequence[str],
           modes: Sequence[str], strata=DEFAULT_STRATA,
           include_amending: bool = False,
           max_per_act: int = 2,
           require_complete: bool = True) -> list[Target]:
    """Stratified, deterministic target selection.

    ``require_complete`` restricts the pool to articles whose citations are all
    resolved (see module docstring); it needs ``reference_status.jsonl`` and
    refuses to silently sample everything when that file is missing.
    """
    bad_acts = _quarantined()
    status = getattr(index, "status", {}) or {}
    if require_complete and not status:
        raise SystemExit(
            "reference_status.jsonl not loaded: run "
            "`python -m clir_bench.domains.legal.structure.resolve_external` "
            "or pass --allow-incomplete")
    external_refs = getattr(index, "external_references", {}) or {}
    annex_refs = getattr(index, "annex_references", {}) or {}
    amending: set[str] = set()
    if not include_amending:
        with struct_paths.ARTICLES_JSONL.open(encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if (row["unit_type"] == "article" and row["language"] == "en"
                        and row.get("is_amending") and row.get("eli_id")):
                    amending.add(row["eli_id"])

    # A question language the corpus has no version of (zh) is legitimate --
    # the chemistry pipeline asks in languages the document does not exist in
    # by design, and the payload then carries English alone. What a target must
    # actually have is every REQUESTED language the corpus can supply, so any
    # article can serve any assigned language.
    needed = [lg for lg in languages if lg in ctx.ACT_LANGUAGES]

    pools: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for eli, unit in index.by_eli.items():
        # The index also holds cited ANNEX bodies; a question target is always
        # an article.
        if unit.unit_type != "article":
            continue
        if unit.celex_id in bad_acts or eli in amending:
            continue
        text = unit.texts.get("en", "")
        if not (MIN_CHARS <= len(text) <= MAX_CHARS):
            continue
        if any(not unit.texts.get(lg) for lg in needed):
            continue
        verdict = status.get(eli, {})
        if require_complete and not verdict.get("complete"):
            continue
        internal = len([t for t in index.references.get(eli, []) if t != eli])
        external = len(external_refs.get(eli, []))
        annexes = len(annex_refs.get(eli, []))
        refs = internal + external + annexes
        for name, low, high, _ in strata:
            if low <= refs <= high:
                # Without a status file nothing is verified complete, so the
                # flag is False rather than assumed -- the row says what we know.
                pools[name].append((eli, internal, external, annexes,
                                    bool(verdict.get("complete")),
                                    bool(verdict.get("cites_annex"))))
                break

    def rank(eli: str) -> str:
        return hashlib.sha256(f"{seed}:{eli}".encode()).hexdigest()

    chosen: list[Target] = []
    per_act: Counter = Counter()
    for name, _, _, share in strata:
        want = round(n * share)
        pool = sorted(pools.get(name, []), key=lambda x: rank(x[0]))
        taken = 0
        for eli, internal, external, annexes, complete, cites_annex in pool:
            if taken >= want:
                break
            unit = index.by_eli[eli]
            if per_act[unit.celex_id] >= max_per_act:
                continue
            per_act[unit.celex_id] += 1
            taken += 1
            position = len(chosen)
            chosen.append(Target(
                eli_id=eli, celex_id=unit.celex_id,
                article_number=unit.article_number, n_refs=internal, stratum=name,
                # Alternate deterministically so the set is balanced across
                # modes and question languages rather than randomly lumpy.
                mode=modes[position % len(modes)],
                language=languages[position % len(languages)],
                n_external=external, n_annex=annexes,
                complete=complete, cites_annex=cites_annex,
            ))
    return chosen


def run_one(target: Target, index: ctx.ArticleIndex, *, gen_model: str,
            grade_model: str, max_references: int, keep: int) -> list[dict[str, Any]]:
    from clir_bench.core.llm import call_with_retries, client_for
    from clir_bench.core.grading import (GraderConfig, grade_faithfulness,
                                         grade_quality, rank_candidates)

    payload = index.build(target.eli_id, max_references=max_references,
                          languages=ctx.payload_languages(target.language))
    if payload is None:
        return []
    grader = GraderConfig(model=grade_model, reasoning_effort="low")
    gen_client, grade_client = client_for(gen_model), client_for(grade_model)

    candidates = call_with_retries(
        lambda: gen.generate(payload, mode=target.mode, language=target.language,
                             model=gen_model, client=gen_client),
        retries=3, label=f"gen {target.celex_id}/{target.article_number}")
    if not candidates:
        return []

    # The graders see the declaration too: the faithfulness rubric caps the
    # grade when ``articles_involved`` is wrong, which it can only judge if shown.
    qa = [{"question": c.question, "answer": c.answer,
           "articles_involved": list(c.articles_involved)} for c in candidates]
    faith = call_with_retries(lambda: grade_faithfulness(
        grade_client, grader, gen.PROMPTS.faithfulness("batch"), payload.text, qa),
        retries=3, label="faith")
    quality = call_with_retries(lambda: grade_quality(
        grade_client, grader, gen.PROMPTS.quality(target.mode, "batch"),
        payload.text, qa, target.mode), retries=3, label="quality")

    # Ranked best-first. Row order carries the ranking, so no rank column is
    # needed: the caller writes the whole list to the all-candidates file and the
    # first row of each target to the best-only file.
    ranked = rank_candidates(qa, faith, quality, target.mode)
    order = {c["question"]: i for i, c in enumerate(qa)}
    rows: list[dict[str, Any]] = []
    for graded in ranked[:keep]:
        candidate = candidates[order[graded.qa["question"]]]
        rows.append({
            "celex_id": target.celex_id,
            "target_article_id": payload.target.eli_id,
            "target_article_number": target.article_number,
            "stratum": target.stratum,
            "n_references_available": target.n_refs,
            "reference_articles_supplied": ",".join(r.article_number for r in payload.references),
            "reference_articles_dropped": ",".join(payload.dropped_references),
            "n_external_available": target.n_external,
            "external_references_supplied": ",".join(
                ctx.external_key(u) for u in payload.external_references),
            "external_references_dropped": ",".join(payload.dropped_external_references),
            "n_annex_available": target.n_annex,
            "annex_references_supplied": ",".join(
                ctx.external_key(u) for u in payload.annexes),
            "annex_references_dropped": ",".join(payload.dropped_annex_references),
            "reference_complete": target.complete,
            "cites_annex": target.cites_annex,
            "question_language": target.language,
            "mode": target.mode,
            "question": candidate.question,
            "answer": candidate.answer,
            "question_type": candidate.classification if target.mode != "semantic" else "",
            "framing": candidate.classification if target.mode == "semantic" else "",
            "articles_involved": ",".join(candidate.articles_involved),
            "articles_involved_eli": ",".join(candidate.involved_elis),
            "multi_article": candidate.multi_article,
            "cross_act": candidate.cross_act,
            "rejected_involved": ",".join(candidate.rejected_involved),
            "faith_grounding": graded.faith.get("grounding"),
            "faith_precision": graded.faith.get("precision"),
            "faith_numerical_fidelity": graded.faith.get("numerical_fidelity"),
            "qual_overall": graded.quality.get("overall"),
            "total_score": graded.total,
        })
    return rows


# ``n_references_available`` counts same-act references only (as it always
# did); ``stratum`` is binned on same-act + other-act references together.
FIELDS = ("celex_id", "target_article_id", "target_article_number", "stratum",
          "n_references_available", "reference_articles_supplied",
          "reference_articles_dropped", "n_external_available",
          "external_references_supplied", "external_references_dropped",
          "n_annex_available", "annex_references_supplied",
          "annex_references_dropped",
          "reference_complete", "cites_annex", "question_language", "mode",
          "question", "answer", "question_type", "framing",
          "articles_involved", "articles_involved_eli", "multi_article",
          "cross_act", "rejected_involved", "faith_grounding", "faith_precision",
          "faith_numerical_fidelity", "qual_overall", "total_score")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=100, help="target articles (= queries when keep=1)")
    parser.add_argument("--keep", type=int, default=3,
                        help="candidates written to the all-candidates file")
    # The production configuration: all four corpus languages (zh is skipped
    # on purpose -- no EUR-Lex zh versions exist, so we do not ask in it), all
    # three prompt modes, gpt-5.4-mini generating and Sonnet grading.
    parser.add_argument("--languages", default="en,fr,de,es")
    parser.add_argument("--modes", default="technical,semantic,descriptive")
    parser.add_argument("--gen-model", default="gpt-5.4-mini")
    parser.add_argument("--grade-model", default="anthropic/claude-sonnet-5")
    parser.add_argument("--max-references", type=int, default=ctx.DEFAULT_MAX_REFERENCES)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--cross-ref-share", type=float, default=CROSS_REFERENCE_SHARE,
                        help="share of targets drawn from articles that cite another article")
    parser.add_argument("--seed", type=int, default=20260804)
    parser.add_argument("--include-amending", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="also sample articles whose citations are not all resolved")
    parser.add_argument("--out", default=str(OUT_DIR / "qac_eurlex.csv"))
    parser.add_argument("--dry-run", action="store_true",
                        help="show the selected targets and the call budget, make no calls")
    args = parser.parse_args()
    load_env()

    languages = [x.strip() for x in args.languages.split(",") if x.strip()]
    # Acts are parsed in ACT_LANGUAGES only; any other question language would
    # get an English-only payload and be written from a language the generator
    # never sees the source in. Refuse instead of degrading.
    unsupported = [l for l in languages if l not in ACT_LANGUAGES]
    if unsupported:
        raise SystemExit(
            f"unsupported question language(s) for EUR-Lex: {', '.join(unsupported)}. "
            f"Acts are available in {', '.join(ACT_LANGUAGES)}.")
    modes = [x.strip() for x in args.modes.split(",") if x.strip()]

    share = args.cross_ref_share
    strata = (("no_refs", 0, 0, 1 - share), ("one_ref", 1, 1, share * 0.40),
              ("few_refs", 2, 3, share * 0.35), ("many_refs", 4, 99, share * 0.25))

    index = ctx.ArticleIndex()
    targets = select(index, n=args.n, seed=args.seed, languages=languages,
                     modes=modes, strata=strata,
                     include_amending=args.include_amending,
                     require_complete=not args.allow_incomplete)

    print(f"selected {len(targets)} target articles "
          f"across {len({t.celex_id for t in targets})} acts", file=sys.stderr)
    print(f"  by stratum : {dict(Counter(t.stratum for t in targets))}", file=sys.stderr)
    print(f"  by language: {dict(Counter(t.language for t in targets))}", file=sys.stderr)
    print(f"  by mode    : {dict(Counter(t.mode for t in targets))}", file=sys.stderr)
    print(f"  with other-act refs: {sum(1 for t in targets if t.n_external)}; "
          f"with annex refs: {sum(1 for t in targets if t.n_annex)}; "
          f"reference-complete: {sum(1 for t in targets if t.complete)}", file=sys.stderr)

    if args.dry_run:
        print(f"\ncall budget: {len(targets)} generation + {2 * len(targets)} grading "
              f"= {3 * len(targets)} calls", file=sys.stderr)
        for t in targets[:12]:
            print(f"   {t.celex_id} art {t.article_number:<5} refs={t.n_refs:<3} "
                  f"ext={t.n_external:<3} anx={t.n_annex:<3} {t.stratum:<10} "
                  f"{t.mode:<9} {t.language}", file=sys.stderr)
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
                                max_references=args.max_references, keep=args.keep)),
            workers=args.workers, description="generating"):
        _, produced = result
        if produced is None:
            failed += 1
        else:
            rows.extend(produced)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # `rows` arrives grouped per target, best-first within each group, because
    # run_one returns its ranked list intact. Only the grouping is normalised
    # here; the within-target order is the ranking and must not be re-sorted.
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["celex_id"], row["target_article_number"]), []).append(row)

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

    multi = sum(1 for r in best if r["multi_article"])
    print(f"\nwrote {len(ordered)} candidates -> {out}", file=sys.stderr)
    print(f"      {len(best)} best-per-target -> {best_path}", file=sys.stderr)
    print(f"  targets that failed  : {failed}", file=sys.stderr)
    print(f"  multi-article (best set): {multi} ({multi / max(len(best), 1):.0%})", file=sys.stderr)
    print(f"  by stratum (best set): {dict(Counter(r['stratum'] for r in best))}", file=sys.stderr)


def _safe(fn, *a, **kw):
    """A failing article must not abort a 100-article build."""
    try:
        return fn(*a, **kw)
    except Exception as error:  # noqa: BLE001
        print(f"    target failed: {type(error).__name__}: {str(error)[:120]}", file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
