"""Compare independent Jev eligibility decisions with existing blinded grades."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from clir_bench.domains.legal.qac.decider import MODES
from clir_bench.domains.legal.qac.screening_analysis import table, write_csv

VERIFIERS = tuple(f"verifier {i}" for i in range(1, 6))
PASS_AUDITS = {"clear", "minor_issues"}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _number(value: str, *, name: str, lower: float = 0, upper: float = 40) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {name}: {value!r}") from exc
    if not math.isfinite(number) or not lower <= number <= upper:
        raise ValueError(f"Invalid {name}: {value!r}")
    return number


def _boolean(value: str) -> bool:
    if value not in ("True", "False"):
        raise ValueError(f"Invalid selected boolean: {value!r}")
    return value == "True"


def _key(row: dict) -> tuple[str, str, str]:
    return row["corpus"], row["target_id"], row["mode"]


def _validate(decisions: list[dict], grades: list[dict]) -> tuple[dict, dict]:
    if not decisions or not grades:
        raise ValueError("Both decisions and grades must contain observations")
    index, document_rows = {}, defaultdict(list)
    for row in decisions:
        key = _key(row)
        if key in index:
            raise ValueError(f"Duplicate eligibility decision: {key}")
        if row["corpus"] not in MODES or row["mode"] not in MODES[row["corpus"]]:
            raise ValueError(f"Unknown corpus or mode: {key}")
        probability = _number(row["probability_yes"], name="probability_yes", upper=1)
        threshold = _number(row["threshold"], name="threshold", upper=1)
        selected = _boolean(row["selected"])
        if selected != (probability >= threshold):
            raise ValueError(f"Decision disagrees with threshold: {key}")
        if row["previous_pick"] not in (*MODES[row["corpus"]], "skip"):
            raise ValueError(f"Invalid previous pick: {key}")
        if row.get("previous_confidence"):
            _number(row["previous_confidence"], name="previous_confidence", upper=1)
        index[key] = dict(row, probability_yes=probability, threshold=threshold,
                          selected=selected, previous_selected=row["previous_pick"] == row["mode"])
        document_rows[key[:2]].append(row)
    for key, rows in document_rows.items():
        if {r["mode"] for r in rows} != set(MODES[key[0]]):
            raise ValueError(f"Expected all six modes for document: {key}")
        for field in ("document_id", "symbol", "previous_pick", "previous_confidence",
                      "source_payload_sha256"):
            if len({r[field] for r in rows}) != 1:
                raise ValueError(f"Inconsistent {field} within document: {key}")

    grouped, candidate_ids = defaultdict(list), set()
    for row in grades:
        key = _key(row)
        if key not in index:
            raise ValueError(f"Grades have no matching eligibility decision: {key}")
        decision = index[key]
        for field in ("document_id", "symbol"):
            if row[field] != decision[field]:
                raise ValueError(f"Different {field} between grades and decision: {key}")
        if row["decider_pick"] != decision["previous_pick"]:
            raise ValueError(f"Different previous pick between grades and decision: {key}")
        digest = hashlib.sha256(row["source_payload"].encode("utf-8")).hexdigest()
        if digest != decision["source_payload_sha256"]:
            raise ValueError(f"Source payload mismatch between grades and decision: {key}")
        if row.get("candidate_id"):
            if row["candidate_id"] in candidate_ids:
                raise ValueError(f"Duplicate candidate ID: {row['candidate_id']}")
            candidate_ids.add(row["candidate_id"])
            for verifier in VERIFIERS:
                for field in ("grading_status", "total_40", "grounding_5", "audit_status"):
                    if f"{verifier}__{field}" not in row:
                        raise ValueError(f"Missing grade column: {verifier}__{field}")
        elif row.get("question") or row.get("mode_status") != "no_candidates":
            raise ValueError(f"Missing candidate ID outside a generation skip: {key}")
        grouped[key].append(row)
    if grouped.keys() != index.keys():
        raise ValueError(f"Eligibility decisions lack matching grades: {sorted(index.keys() - grouped.keys())}")
    for key, rows in grouped.items():
        if any(not r.get("candidate_id") for r in rows) and len(rows) != 1:
            raise ValueError(f"Generation skip mixed with other rows: {key}")
    return index, grouped


def _grade_summary(rows: list[dict], verifier: str, corpus: str) -> dict:
    prefix = verifier + "__"
    candidates = [row for row in rows if row.get("candidate_id")]
    graded = [row for row in candidates if row[prefix + "grading_status"] == "completed"
              and row[prefix + "total_40"] != ""]
    scores = [_number(row[prefix + "total_40"], name=prefix + "total_40") for row in graded]
    passing = [row for row in graded if row[prefix + "audit_status"] in PASS_AUDITS
               and (corpus != "un" or
                    _number(row[prefix + "grounding_5"], name=prefix + "grounding_5", upper=5) >= 3)]
    return {
        prefix + "graded_candidate_count": len(graded),
        prefix + "ungraded_candidate_count": len(candidates) - len(graded),
        prefix + "best_total_40": max(scores) if scores else None,
        prefix + "mean_total_40": mean(scores) if scores else None,
        prefix + "passing_candidate_count": len(passing),
        prefix + "has_passing_candidate": bool(passing),
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _classification(rows: list[dict], verifier: str, decision_field: str) -> dict:
    label = verifier + "__has_passing_candidate"
    tp = sum(row[decision_field] and row[label] for row in rows)
    fp = sum(row[decision_field] and not row[label] for row in rows)
    fn = sum(not row[decision_field] and row[label] for row in rows)
    tn = sum(not row[decision_field] and not row[label] for row in rows)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": _ratio(tp, tp + fp), "recall": _ratio(tp, tp + fn)}


def _statistics(rows: list[dict], verifier: str, corpus: str, mode: str) -> dict:
    selected = [row for row in rows if (corpus == "all" or row["corpus"] == corpus)
                and (mode == "all" or row["mode"] == mode)]
    result = {"verifier": verifier, "corpus": corpus, "mode": mode,
              "document_mode_count": len(selected),
              "document_count": len({(r["corpus"], r["target_id"]) for r in selected}),
              "yes_count": sum(row["selected"] for row in selected),
              "observed_viable_mode_count": sum(row[verifier + "__has_passing_candidate"] for row in selected),
              "candidate_count": sum(row["candidate_count"] for row in selected),
              "passing_candidate_count": sum(row[verifier + "__passing_candidate_count"] for row in selected),
              "ungraded_candidate_count": sum(row[verifier + "__ungraded_candidate_count"] for row in selected),
              **_classification(selected, verifier, "selected")}
    result["no_count"] = len(selected) - result["yes_count"]
    for decision_field, label in (("selected", ""), ("previous_selected", "baseline_")):
        for take, group in ((True, "selected"), (False, "rejected")):
            values = [row[verifier + "__best_total_40"] for row in selected
                      if row[decision_field] == take and row[verifier + "__best_total_40"] is not None]
            result[label + group + "_scored_mode_count"] = len(values)
            result[label + "mean_best_total_40_" + group] = mean(values) if values else None
    result["baseline_selected_count"] = sum(row["previous_selected"] for row in selected)
    result.update({"baseline_" + key: value for key, value in
                   _classification(selected, verifier, "previous_selected").items()})
    return result


def analyze(output: Path, grades_csv: Path) -> dict:
    """Export exact joins, batch-level comparisons and measured routing statistics."""
    output, grades_csv = Path(output), Path(grades_csv)
    decisions = read_csv(output / "decisions.csv")
    grades = read_csv(grades_csv)
    index, grouped = _validate(decisions, grades)
    mode_rows, question_rows = [], []
    for key, decision in index.items():
        rows = grouped[key]
        candidates = [row for row in rows if row.get("candidate_id")]
        public_decision = {key: value for key, value in decision.items() if key != "response_model"}
        result = dict(public_decision, candidate_count=len(candidates),
                      questions_json=json.dumps([row["question"] for row in candidates], ensure_ascii=False))
        for verifier in VERIFIERS:
            result.update(_grade_summary(rows, verifier, decision["corpus"]))
        mode_rows.append(result)
    # Preserve the original candidate/skip row order and every existing text/grade column.
    for row in grades:
        decision = index[_key(row)]
        question_rows.append(dict(row, jev_eligibility_yes=decision["selected"],
                                  jev_probability_yes=decision["probability_yes"],
                                  jev_threshold=decision["threshold"],
                                  jev_previous_pick=decision["previous_pick"],
                                  jev_previous_confidence=decision["previous_confidence"],
                                  jev_source_payload_sha256=decision["source_payload_sha256"]))
    corpora = sorted({row["corpus"] for row in mode_rows})
    scopes = [("all", "all")]
    for corpus in corpora:
        scopes.append((corpus, "all"))
        scopes.extend((corpus, mode) for mode in MODES[corpus])
    statistics = [_statistics(mode_rows, verifier, corpus, mode)
                  for verifier in VERIFIERS for corpus, mode in scopes]
    documents = defaultdict(list)
    for row in mode_rows:
        documents[(row["corpus"], row["target_id"])].append(row)
    eligible_counts = Counter(sum(row["selected"] for row in rows) for rows in documents.values())
    overview = []
    for corpus in corpora:
        for mode in MODES[corpus]:
            rows = [row for row in mode_rows if row["corpus"] == corpus and row["mode"] == mode]
            overview.append({"corpus": corpus, "mode": mode, "documents": len(rows),
                             "yes_count": sum(row["selected"] for row in rows),
                             "mean_probability_yes": mean(row["probability_yes"] for row in rows),
                             "previous_pick_count": sum(row["previous_selected"] for row in rows)})
    summary = {"documents": len(documents), "document_modes": len(mode_rows),
               "candidate_questions": sum(row["candidate_count"] for row in mode_rows),
               "generation_skips": sum(row["candidate_count"] == 0 for row in mode_rows),
               "question_csv_rows": len(question_rows), "verifiers": list(VERIFIERS),
               "yes_count": sum(row["selected"] for row in mode_rows),
               "no_count": sum(not row["selected"] for row in mode_rows),
               "documents_with_no_yes": eligible_counts[0],
               "eligible_modes_per_document": dict(sorted(eligible_counts.items())),
               "thresholds": sorted({row["threshold"] for row in mode_rows}),
               "mode_decisions": overview,
               "overall_statistics": [row for row in statistics if row["corpus"] == row["mode"] == "all"]}
    write_csv(output / "questions_with_jev_and_grades.csv", question_rows)
    write_csv(output / "mode_comparison.csv", mode_rows)
    write_csv(output / "comparison_statistics.csv", statistics)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _report(output, summary, statistics)
    return summary


def _report(output: Path, summary: dict, statistics: list[dict]) -> None:
    overall = summary["overall_statistics"]
    preferred = [row for row in statistics if row["verifier"] == "verifier 4" and row["mode"] == "all"]
    preferred_overall = next(row for row in preferred if row["corpus"] == "all")
    selection_rate = summary["yes_count"] / summary["document_modes"]
    comparison_misses = sum(row["fn"] for row in statistics
                            if row["verifier"] == "verifier 4" and row["mode"] == "comparison")
    thresholds = ", ".join(str(value) for value in summary["thresholds"])
    report = [
        "# Independent Jev eligibility compared with existing verifier grades",
        (f"{summary['documents']} unchanged documents, {summary['document_modes']} document-mode decisions, "
        f"and {summary['candidate_questions']} previously generated questions. "
        f"Jev selected {summary['yes_count']} modes and rejected {summary['no_count']}. "
        f"{summary['documents_with_no_yes']} documents have no selected mode. "
        f"The exports preserve all {summary['generation_skips']} generation skips. "
        "This comparison performs no generation or regrading."),
        "## Decision and reference definitions",
        (f"Each mode is selected independently when its yes probability is at least the recorded threshold "
        f"({thresholds}). The 0.5 threshold is exploratory; these probabilities have not been calibrated. "
        "Several or no modes may be selected for a document. The original baseline selects exactly its "
        "previous winning mode, or none for a skip."),
        ("A document-mode is **observed viable** for a verifier if at least one generated candidate has a "
        "completed numeric grade, audit status `clear` or `minor_issues`, and, for UN, grounding at least 3/5. "
        "A high numeric score alone does not override a failed audit. Generation skips have no observed "
        "passing candidate. This is the same grounded audit-pass rule used by the original screening analysis."),
        ("Verifier judgments are weak reference labels, not human ground truth. No observed passing question "
        "does not prove that a mode is impossible: generation attempted only a limited set of questions. "
        "An ungraded candidate also cannot establish a pass. A Jev yes prediction on an observed negative "
        "is counted as an FP below only for this comparison, not as a proven routing mistake."),
        ("TP = yes with an observed passing candidate; FP = yes without one; FN = no with one; "
        "TN = no without one. Precision is TP / all yes decisions. Recall is TP / all observed viable modes. "
        "Baseline metrics use the same document-mode population and the original single winner. "
        "The new policy can select more modes and therefore use a larger generation budget; its recall gain "
        "is not a comparison at equal generation cost. Undefined ratios are blank in CSV and shown as — here."),
        ("Score averages are document-mode macro averages of the best completed total /40 in each group, "
        "including candidates that fail audit or grounding. Groups without a numeric score are excluded "
        "from score averages; scored denominators are included in the statistics CSV. Within-mode mean "
        "candidate scores and passing counts are in `mode_comparison.csv`."),
        "## Yes decisions by corpus and mode",
        table(summary["mode_decisions"], ["corpus", "mode", "documents", "yes_count",
                                          "mean_probability_yes", "previous_pick_count"]),
        "## Overall comparison with each blinded verifier",
        table(overall, ["verifier", "yes_count", "observed_viable_mode_count", "tp", "fp", "fn", "tn",
                        "precision", "recall", "baseline_selected_count", "baseline_precision", "baseline_recall"]),
        "## Verifier 4 comparison by corpus",
        table(preferred, ["corpus", "document_mode_count", "yes_count", "observed_viable_mode_count", "tp", "fp", "fn", "tn",
                          "precision", "recall", "baseline_precision", "baseline_recall",
                          "mean_best_total_40_selected", "mean_best_total_40_rejected"]),
        (f"Selecting all {summary['document_modes']} modes without Jev would have "
        f"{preferred_overall['observed_viable_mode_count'] / summary['document_modes']:.1%} precision "
        "against verifier 4 and retain every observed viable mode. "
        f"The independent policy keeps {selection_rate:.1%} of all modes "
        f"({summary['yes_count'] / summary['documents']:.2f} per document on average). "
        f"Compared with generating all modes, it would avoid {summary['no_count']} generation batches, "
        f"while missing {preferred_overall['fn']} batches with an existing verifier-4 passing question. "
        f"Of these missed batches, {comparison_misses} are comparison mode. "
        "Review those disagreements before choosing a production threshold; the current run measures "
        "eligibility coverage rather than a balanced persona allocation."),
        "## Selected versus rejected scores",
        table(overall, ["verifier", "selected_scored_mode_count", "mean_best_total_40_selected",
                        "rejected_scored_mode_count", "mean_best_total_40_rejected", "ungraded_candidate_count"]),
        "## Files",
        ("- [Every original question, grade and explanation with its new Jev decision](questions_with_jev_and_grades.csv)\n"
        "- [One row per document and mode](mode_comparison.csv)\n"
        "- [All five verifier comparisons, overall and by corpus/mode](comparison_statistics.csv)\n"
        "- [Raw independent decisions](decisions.csv)"),
    ]
    (output / "analysis.md").write_text("\n\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Directory containing decisions.csv")
    parser.add_argument("--grades-csv", type=Path, required=True, help="Existing five-verifier blinded candidate CSV")
    args = parser.parse_args()
    print(json.dumps(analyze(args.output, args.grades_csv), indent=2))


if __name__ == "__main__":
    main()
