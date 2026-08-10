"""
Build a EUR-Lex question set: select target articles, generate, grade, rank, write.

One target article yields three candidates; the best-scoring one is kept. So a
100-query set is 100 target articles, and the run costs 100 generation calls plus
200 grading calls.

Selection is stratified by **reference count**, which is the axis that matters
here: the corpus median citing article references exactly one other article, so a
uniform sample would be almost entirely single-article and the reference graph
would buy nothing. The default mix deliberately over-samples articles with
references relative to their corpus frequency, and records the stratum on every
row so the resulting set can be re-weighted or split later.

Filters applied before sampling, each for a reason found the hard way:

* acts in ``quarantine.jsonl`` are excluded -- their article numbering disagrees
  across languages, so an article id there is not reliably the same article in
  all four;
* amending articles are excluded by default -- they quote the text of *another*
  act, so a question drawn from one is about a document that is not in the corpus;
* very short and very long articles are excluded -- the first cannot support
  three distinct questions, the second buries the operative fact.

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

from clir_bench.domains.legal.structure import paths as struct_paths
from clir_bench.domains.legal.qac import eurlex_context as ctx
from clir_bench.domains.legal.qac import eurlex_generate as gen

OUT_DIR = struct_paths.EURLEX_DIR / "qac"

# (name, min refs, max refs, share of the set). Weighted towards articles that
# can actually produce a multi-article question, which uniform sampling cannot.
# Only this share of the set is drawn from articles that cite another article;
# the rest have no references at all and act as the control that must never
# produce a multi-article answer. Cross-referenced questions are the interesting
# minority, not the norm -- overweighting them would misrepresent how EU acts
# actually read and would make the benchmark easier than the corpus.
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
    n_refs: int
    stratum: str
    mode: str
    language: str


def _quarantined() -> set[str]:
    path = struct_paths.QUARANTINE_JSONL
    if not path.exists():
        return set()
    return {json.loads(line)["celex_id"] for line in path.open(encoding="utf-8")}


def select(index: ctx.ArticleIndex, *, n: int, seed: int, languages: Sequence[str],
           modes: Sequence[str], strata=DEFAULT_STRATA,
           include_amending: bool = False,
           max_per_act: int = 2) -> list[Target]:
    """Stratified, deterministic target selection."""
    bad_acts = _quarantined()
    amending: set[str] = set()
    if not include_amending:
        with struct_paths.ARTICLES_JSONL.open(encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if (row["unit_type"] == "article" and row["language"] == "en"
                        and row.get("is_amending") and row.get("eli_id")):
                    amending.add(row["eli_id"])

    pools: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for eli, unit in index.by_eli.items():
        if unit.celex_id in bad_acts or eli in amending:
            continue
        text = unit.texts.get("en", "")
        if not (MIN_CHARS <= len(text) <= MAX_CHARS):
            continue
        if len(unit.languages()) < len(languages):
            continue
        refs = len([t for t in index.references.get(eli, []) if t != eli])
        for name, low, high, _ in strata:
            if low <= refs <= high:
                pools[name].append((eli, refs))
                break

    def rank(eli: str) -> str:
        return hashlib.sha256(f"{seed}:{eli}".encode()).hexdigest()

    chosen: list[Target] = []
    per_act: Counter = Counter()
    for name, _, _, share in strata:
        want = round(n * share)
        pool = sorted(pools.get(name, []), key=lambda x: rank(x[0]))
        taken = 0
        for eli, refs in pool:
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
                article_number=unit.article_number, n_refs=refs, stratum=name,
                # Alternate deterministically so the set is balanced across
                # modes and question languages rather than randomly lumpy.
                mode=modes[position % len(modes)],
                language=languages[position % len(languages)],
            ))
    return chosen


def run_one(target: Target, index: ctx.ArticleIndex, *, gen_model: str,
            grade_model: str, max_references: int, keep: int) -> list[dict[str, Any]]:
    from clir_bench.core.llm import call_with_retries, client_for
    from clir_bench.core.grading import (GraderConfig, grade_faithfulness,
                                         grade_quality, rank_candidates)

    payload = index.build(target.eli_id, max_references=max_references)
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

    qa = [{"question": c.question, "answer": c.answer} for c in candidates]
    faith = call_with_retries(lambda: grade_faithfulness(
        grade_client, grader, gen.PROMPTS.faithfulness("batch"), payload.text, qa),
        retries=3, label="faith")
    quality = call_with_retries(lambda: grade_quality(
        grade_client, grader, gen.PROMPTS.quality(target.mode, "batch"),
        payload.text, qa, target.mode), retries=3, label="quality")

    ranked = rank_candidates(qa, faith, quality, target.mode)
    order = {c["question"]: i for i, c in enumerate(qa)}
    rows: list[dict[str, Any]] = []
    for rank_index, graded in enumerate(ranked[:keep], start=1):
        candidate = candidates[order[graded.qa["question"]]]
        rows.append({
            "celex_id": target.celex_id,
            "target_article_id": payload.target.eli_id,
            "target_article_number": target.article_number,
            "stratum": target.stratum,
            "n_references_available": target.n_refs,
            "reference_articles_supplied": ",".join(r.article_number for r in payload.references),
            "reference_articles_dropped": ",".join(payload.dropped_references),
            "question_language": target.language,
            "mode": target.mode,
            "candidate_rank": rank_index,
            "question": candidate.question,
            "answer": candidate.answer,
            "question_type": candidate.classification if target.mode == "technical" else "",
            "framing": candidate.classification if target.mode == "semantic" else "",
            "articles_involved": ",".join(candidate.articles_involved),
            "articles_involved_eli": ",".join(candidate.involved_elis),
            "multi_article": candidate.multi_article,
            "rejected_involved": ",".join(candidate.rejected_involved),
            "faith_grounding": graded.faith.get("grounding"),
            "faith_precision": graded.faith.get("precision"),
            "faith_numerical_fidelity": graded.faith.get("numerical_fidelity"),
            "qual_overall": graded.quality.get("overall"),
            "total_score": graded.total,
        })
    return rows


FIELDS = ("celex_id", "target_article_id", "target_article_number", "stratum",
          "n_references_available", "reference_articles_supplied",
          "reference_articles_dropped", "question_language", "mode",
          "candidate_rank", "question", "answer", "question_type", "framing",
          "articles_involved", "articles_involved_eli", "multi_article",
          "rejected_involved", "faith_grounding", "faith_precision",
          "faith_numerical_fidelity", "qual_overall", "total_score")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=100, help="target articles (= queries when keep=1)")
    parser.add_argument("--keep", type=int, default=1, help="candidates kept per target")
    parser.add_argument("--languages", default="en,fr,de,es")
    parser.add_argument("--modes", default="technical,semantic")
    parser.add_argument("--gen-model", default="gpt-5.5")
    parser.add_argument("--grade-model", default="anthropic/claude-sonnet-5")
    parser.add_argument("--max-references", type=int, default=ctx.DEFAULT_MAX_REFERENCES)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--cross-ref-share", type=float, default=CROSS_REFERENCE_SHARE,
                        help="share of targets drawn from articles that cite another article")
    parser.add_argument("--seed", type=int, default=20260804)
    parser.add_argument("--include-amending", action="store_true")
    parser.add_argument("--out", default=str(OUT_DIR / "qac_eurlex.csv"))
    parser.add_argument("--dry-run", action="store_true",
                        help="show the selected targets and the call budget, make no calls")
    args = parser.parse_args()

    languages = [x.strip() for x in args.languages.split(",") if x.strip()]
    modes = [x.strip() for x in args.modes.split(",") if x.strip()]

    share = args.cross_ref_share
    strata = (("no_refs", 0, 0, 1 - share), ("one_ref", 1, 1, share * 0.40),
              ("few_refs", 2, 3, share * 0.35), ("many_refs", 4, 99, share * 0.25))

    index = ctx.ArticleIndex()
    targets = select(index, n=args.n, seed=args.seed, languages=languages,
                     modes=modes, strata=strata,
                     include_amending=args.include_amending)

    print(f"selected {len(targets)} target articles "
          f"across {len({t.celex_id for t in targets})} acts", file=sys.stderr)
    print(f"  by stratum : {dict(Counter(t.stratum for t in targets))}", file=sys.stderr)
    print(f"  by language: {dict(Counter(t.language for t in targets))}", file=sys.stderr)
    print(f"  by mode    : {dict(Counter(t.mode for t in targets))}", file=sys.stderr)

    if args.dry_run:
        print(f"\ncall budget: {len(targets)} generation + {2 * len(targets)} grading "
              f"= {3 * len(targets)} calls", file=sys.stderr)
        for t in targets[:12]:
            print(f"   {t.celex_id} art {t.article_number:<5} refs={t.n_refs:<3} "
                  f"{t.stratum:<10} {t.mode:<9} {t.language}", file=sys.stderr)
        print("   ...", file=sys.stderr)
        return

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

    rows.sort(key=lambda r: (r["celex_id"], r["target_article_number"], r["candidate_rank"]))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    multi = sum(1 for r in rows if r["multi_article"])
    print(f"\nwrote {len(rows)} queries -> {out}", file=sys.stderr)
    print(f"  targets that failed  : {failed}", file=sys.stderr)
    print(f"  multi-article queries: {multi} ({multi / max(len(rows), 1):.0%})", file=sys.stderr)
    print(f"  by stratum           : {dict(Counter(r['stratum'] for r in rows))}", file=sys.stderr)


def _safe(fn, *a, **kw):
    """A failing article must not abort a 100-article build."""
    try:
        return fn(*a, **kw)
    except Exception as error:  # noqa: BLE001
        print(f"    target failed: {type(error).__name__}: {str(error)[:120]}", file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
