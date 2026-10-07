"""Evaluate source-only Jev routing against each mode's best recorded numeric grade.

This comparison deliberately keeps numeric score labels separate from audit labels.
Threshold proposals use document-grouped development data only; validation observations
never participate in selecting a threshold.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

from clir_bench.domains.legal.qac.decider import MODES
from clir_bench.domains.legal.qac.screening_analysis import write_csv
from clir_bench.domains.legal.qac.screening_eligibility_analysis import read_csv

GRADE_PREFIX = "verifier 4__"
PASS_AUDITS = {"clear", "minor_issues"}


def _number(value, name: str, upper: float = 40) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {name}: {value!r}") from exc
    if isinstance(value, bool) or not math.isfinite(result) or not 0 <= result <= upper:
        raise ValueError(f"Invalid {name}: {value!r}")
    return result


def _key(row: dict) -> tuple[str, str, str]:
    return row["corpus"], row["target_id"], row["mode"]


def _document(row: dict) -> tuple[str, str]:
    return row["corpus"], row["document_id"]


def _validate(decisions: list[dict], all_grades: list[dict]) -> tuple[dict, dict, list[dict]]:
    if not decisions or not all_grades:
        raise ValueError("Both decisions and grades must contain observations")
    index, target_rows = {}, defaultdict(list)
    for row in decisions:
        key = _key(row)
        if not row["document_id"] or not row["target_id"]:
            raise ValueError(f"Missing document or target identity: {key}")
        if key[0] not in MODES or key[2] not in MODES[key[0]]:
            raise ValueError(f"Unknown corpus or mode: {key}")
        if key in index:
            raise ValueError(f"Duplicate cutoff decision: {key}")
        probability = _number(row["probability_yes"], "probability_yes", 1)
        threshold = _number(row["threshold"], "threshold", 1)
        if row["selected"] not in ("True", "False"):
            raise ValueError(f"Invalid selected boolean: {row['selected']!r}")
        if (row["selected"] == "True") != (probability >= threshold):
            raise ValueError(f"Recorded decision disagrees with threshold: {key}")
        index[key] = dict(row, probability_yes=probability, threshold=threshold,
                          selected=row["selected"] == "True")
        target_rows[key[:2]].append(row)
    for target, rows in target_rows.items():
        if {row["mode"] for row in rows} != set(MODES[target[0]]):
            raise ValueError(f"Expected all six modes for target: {target}")
        for field in ("document_id", "symbol", "source_payload_sha256"):
            present = [row[field] for row in rows if field in row]
            if present and (len(present) != len(rows) or len(set(present)) != 1):
                raise ValueError(f"Inconsistent {field} within target: {target}")

    selected_docs = {_document(row) for row in decisions}
    source_docs = {_document(row) for row in all_grades}
    if not selected_docs <= source_docs:
        raise ValueError(f"Decision documents absent from grades: {selected_docs - source_docs}")
    grades = [row for row in all_grades if _document(row) in selected_docs]
    grouped, candidate_ids = defaultdict(list), set()
    for row in grades:
        key = _key(row)
        if key not in index:
            raise ValueError(f"Unexpected grade target/mode for selected document: {key}")
        decision = index[key]
        if row["document_id"] != decision["document_id"]:
            raise ValueError(f"Different document_id between grades and decision: {key}")
        if "symbol" in decision and row.get("symbol") != decision["symbol"]:
            raise ValueError(f"Different symbol between grades and decision: {key}")
        if decision.get("source_payload_sha256"):
            digest = hashlib.sha256(row.get("source_payload", "").encode()).hexdigest()
            if digest != decision["source_payload_sha256"]:
                raise ValueError(f"Source payload mismatch between grades and decision: {key}")
        candidate_id = row.get("candidate_id", "")
        if candidate_id:
            if candidate_id in candidate_ids:
                raise ValueError(f"Duplicate candidate ID: {candidate_id}")
            candidate_ids.add(candidate_id)
            if row.get(GRADE_PREFIX + "grading_status") != "completed":
                raise ValueError(f"Candidate has incomplete grading: {candidate_id}")
            _number(row.get(GRADE_PREFIX + "total_40"), "total_40")
        elif row.get("question") or row.get("mode_status") != "no_candidates":
            raise ValueError(f"Missing candidate ID outside generation skip: {key}")
        grouped[key].append(row)
    if grouped.keys() != index.keys():
        raise ValueError(f"Decisions lack matching grade groups: {index.keys() - grouped.keys()}")
    for key, rows in grouped.items():
        if any(not row.get("candidate_id") for row in rows) and len(rows) != 1:
            raise ValueError(f"Generation skip mixed with candidates or duplicated: {key}")
        for field in ("source_payload", "document_text"):
            if len({row.get(field) for row in rows}) != 1:
                raise ValueError(f"Inconsistent {field} within grade group: {key}")
    return index, grouped, grades


def _partitions(split_path: Path | None, decisions: dict, source_documents: set) -> dict:
    documents = {_document(row) for row in decisions.values()}
    if split_path is None:
        return {document: "unassigned" for document in documents}
    split = json.loads(Path(split_path).read_text(encoding="utf-8"))
    if split.get("schema_version") != 1 or not isinstance(split.get("documents"), list):
        raise ValueError("Split must have schema_version 1 and a documents list")
    mapping = {}
    for row in split["documents"]:
        document = _document(row)
        if document in mapping:
            raise ValueError(f"Duplicate document in split (possible partition leakage): {document}")
        if row["partition"] not in ("development", "validation"):
            raise ValueError(f"Unknown split partition: {row['partition']!r}")
        mapping[document] = row["partition"]
    if not documents <= mapping.keys():
        raise ValueError(f"Split lacks decision documents: {documents - mapping.keys()}")
    if not mapping.keys() <= source_documents:
        raise ValueError(f"Split has documents absent from source grades: {mapping.keys() - source_documents}")
    return {document: mapping[document] for document in documents}


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _metrics(rows: list[dict], threshold: float, **scope) -> dict:
    tp = sum(row["probability_yes"] >= threshold and row["above_cutoff"] for row in rows)
    fp = sum(row["probability_yes"] >= threshold and not row["above_cutoff"] for row in rows)
    fn = sum(row["probability_yes"] < threshold and row["above_cutoff"] for row in rows)
    tn = sum(row["probability_yes"] < threshold and not row["above_cutoff"] for row in rows)
    recall, specificity = _ratio(tp, tp + fn), _ratio(tn, tn + fp)
    result = dict(scope, probability_threshold=threshold, document_modes=len(rows),
                  documents=len({_document(row) for row in rows}), tp=tp, fp=fp, fn=fn, tn=tn,
                  accepted=tp + fp, rejected=tn + fn, high_score_count=tp + fn,
                  low_score_or_skip_count=tn + fp,
                  rejection_rate_low=specificity, retention_rate_high=recall,
                  precision=_ratio(tp, tp + fp), specificity=specificity,
                  balanced_accuracy=(recall + specificity) / 2
                  if recall is not None and specificity is not None else None,
                  fbeta_0_5=_ratio(1.25 * tp, 1.25 * tp + 0.25 * fn + fp),
                  generation_skips=sum(row["generation_skip"] for row in rows))
    for label, selected in (("all", rows),
                            ("accepted", [r for r in rows if r["probability_yes"] >= threshold]),
                            ("rejected", [r for r in rows if r["probability_yes"] < threshold])):
        scores = [row["best_total_40"] for row in selected if row["best_total_40"] is not None]
        result[f"scored_modes_{label}"] = len(scores)
        result[f"mean_best_total_40_{label}"] = mean(scores) if scores else None
        result[f"min_best_total_40_{label}"] = min(scores) if scores else None
        result[f"max_best_total_40_{label}"] = max(scores) if scores else None
    return result


def _scoped_metrics(rows: list[dict], threshold: float) -> list[dict]:
    result = []
    for partition in ("all", *sorted({row["partition"] for row in rows})):
        subset = [row for row in rows if partition == "all" or row["partition"] == partition]
        scopes = [("all", "all")]
        for corpus in sorted({row["corpus"] for row in subset}):
            scopes.append((corpus, "all"))
            scopes.extend((corpus, mode) for mode in MODES[corpus])
        for corpus, mode in scopes:
            observations = [row for row in subset if
                            (corpus == "all" or row["corpus"] == corpus)
                            and (mode == "all" or row["mode"] == mode)]
            result.append(_metrics(observations, threshold, partition=partition,
                                   corpus=corpus, mode=mode))
    return result


def evaluate(decisions_path: Path, grades_path: Path, output: Path,
             split_path: Path | None = None, probability_threshold: float = 0.5,
             score_cutoff: float = 31, selection_objective: str = "fbeta_0_5",
             minimum_high_retention: float = 0.5) -> dict:
    """Export a validated comparison and development-only probability calibration.

    Decision files may contain a complete subset of source documents. Every selected
    target must have all six modes, and every mode must join exactly to the grades.
    A mode is numerically positive iff its maximum recorded score is strictly above
    ``score_cutoff``. A generation skip is negative, not a fictitious zero score.
    """
    threshold = _number(probability_threshold, "probability_threshold", 1)
    cutoff = _number(score_cutoff, "score_cutoff")
    minimum_retention = _number(minimum_high_retention, "minimum_high_retention", 1)
    if selection_objective not in ("fbeta_0_5", "low_rejection"):
        raise ValueError(f"Unknown selection_objective: {selection_objective!r}")
    all_grades = read_csv(Path(grades_path))
    index, grouped, grades = _validate(read_csv(Path(decisions_path)), all_grades)
    source_documents = {_document(row) for row in all_grades}
    partitions = _partitions(split_path, index, source_documents)
    comparison = []
    for key, decision in index.items():
        candidates = [row for row in grouped[key] if row.get("candidate_id")]
        scores = [_number(row[GRADE_PREFIX + "total_40"], "total_40") for row in candidates]
        best = max(scores) if scores else None
        winners = [row for row, score in zip(candidates, scores) if score == best]
        high = best is not None and best > cutoff
        accepted = decision["probability_yes"] >= threshold
        audit_high = [row for row, score in zip(candidates, scores)
                      if score > cutoff and row.get(GRADE_PREFIX + "audit_status") in PASS_AUDITS
                      and (key[0] != "un" or _number(row.get(GRADE_PREFIX + "grounding_5"),
                                                    "grounding_5", 5) >= 3)]
        comparison.append({
            "corpus": key[0], "document_id": decision["document_id"], "target_id": key[1],
            "mode": key[2], "partition": partitions[_document(decision)],
            "probability_yes": decision["probability_yes"], "accepted": accepted,
            "probability_threshold": threshold, "recorded_selected": decision["selected"],
            "recorded_probability_threshold": decision["threshold"], "score_cutoff": cutoff,
            "best_total_40": best, "above_cutoff": high,
            "confusion": "TP" if accepted and high else "FP" if accepted else "FN" if high else "TN",
            "candidate_count": len(candidates), "generation_skip": not candidates,
            "has_audit_passing_candidate_above_cutoff": bool(audit_high),
            "best_candidate_ids_json": json.dumps([row["candidate_id"] for row in winners]),
            "best_questions_json": json.dumps([row["question"] for row in winners], ensure_ascii=False),
            "best_answers_json": json.dumps([row.get("answer", "") for row in winners], ensure_ascii=False),
            "best_audit_statuses_json": json.dumps([row.get(GRADE_PREFIX + "audit_status", "")
                                                    for row in winners]),
            "best_verifier_reasons_json": json.dumps([
                {field: row.get(GRADE_PREFIX + field, "") for field in
                 ("faithfulness_reason", "quality_reason", "audit_reason")}
                for row in winners], ensure_ascii=False),
        })
    metrics = _scoped_metrics(comparison, threshold)
    development = [row for row in comparison if row["partition"] == "development"]
    sweep = []
    if development:
        points = {i / 100 for i in range(101)} | {row["probability_yes"] for row in development}
        # Crossing a probability, rather than only landing on it, covers every distinct
        # decision set under the inclusive >= probability rule.
        points |= {math.nextafter(row["probability_yes"], 1)
                   for row in development if row["probability_yes"] < 1}
        sweep = [_metrics(development, point, partition="development", corpus="all", mode="all")
                 for point in sorted(points)]
        for row in sweep:
            row["proposal_eligible"] = (row["accepted"] >= 1
                                         and row["retention_rate_high"] is not None
                                         and row["retention_rate_high"] >= minimum_retention)
    eligible = [row for row in sweep if row["proposal_eligible"]]
    if selection_objective == "low_rejection":
        selection_key = lambda row: (
            row["rejection_rate_low"] if row["rejection_rate_low"] is not None else -1,
            row["precision"], row["tp"], row["probability_threshold"])
        priority_description = "maximize low-score rejection, then precision, retained high modes, higher threshold"
    else:
        selection_key = lambda row: (
            row["fbeta_0_5"],
            row["balanced_accuracy"] if row["balanced_accuracy"] is not None else -1,
            row["tp"], row["probability_threshold"])
        priority_description = "maximize F0.5, then balanced accuracy, retained high modes, higher threshold"
    proposal = max(eligible, key=selection_key) if eligible else None
    proposed_metrics = (_scoped_metrics(comparison, proposal["probability_threshold"])
                        if proposal else [])
    scored = [row for row in comparison if row["best_total_40"] is not None]
    summary = {
        "schema_version": 1, "reference_verifier": "verifier 4", "score_cutoff": cutoff,
        "selection_objective": selection_objective, "minimum_high_retention": minimum_retention,
        "numeric_positive_rule": f"best_total_40 > {cutoff:g}",
        "probability_threshold": threshold, "source_grade_documents": len(source_documents),
        "evaluated_documents": len(partitions), "omitted_grade_documents": len(source_documents) - len(partitions),
        "document_modes": len(comparison), "candidate_questions": sum(r["candidate_count"] for r in comparison),
        "generation_skips": len(comparison) - len(scored), "scored_modes": len(scored),
        "best_score_above_cutoff": sum(r["above_cutoff"] for r in comparison),
        "best_score_at_or_below_cutoff": sum(not r["above_cutoff"] for r in scored),
        "mean_best_total_40": mean(r["best_total_40"] for r in scored) if scored else None,
        "metrics": metrics, "proposed_probability_threshold": proposal["probability_threshold"] if proposal else None,
        "threshold_proposal_development_metrics": proposal, "proposed_threshold_metrics": proposed_metrics,
        "proposal_selection": (f"Development only; {priority_description}. Require at least one "
                               f"selected mode and high-score recall >={minimum_retention:g}."),
        "reference_limits": "Observed numeric grades of the saved candidates, not proof of source feasibility or audit validity. Skips are negative reference observations. No generation, grading, or Jev calls are performed.",
    }
    by_key = {_key(row): row for row in comparison}
    question_rows = [dict(row, **{f"cutoff_{field}": by_key[_key(row)][field] for field in
                                 ("partition", "accepted", "above_cutoff", "best_total_40",
                                  "confusion", "probability_yes", "probability_threshold", "score_cutoff")})
                     for row in grades]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "cutoff_comparison.csv", comparison)
    write_csv(output / "cutoff_metrics.csv", metrics)
    write_csv(output / "cutoff_errors.csv", [row for row in comparison if row["confusion"] in ("FP", "FN")])
    write_csv(output / "questions_with_cutoff_decisions.csv", question_rows)
    write_csv(output / "cutoff_error_questions.csv", [row for row in question_rows
                                                     if row["cutoff_confusion"] in ("FP", "FN")])
    write_csv(output / "development_threshold_sweep.csv", sweep)
    write_csv(output / "proposed_threshold_metrics.csv", proposed_metrics)
    (output / "cutoff_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--grades", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", type=Path)
    parser.add_argument("--probability-threshold", type=float, default=0.5)
    parser.add_argument("--score-cutoff", type=float, default=31)
    parser.add_argument("--selection-objective", choices=("fbeta_0_5", "low_rejection"),
                        default="fbeta_0_5")
    parser.add_argument("--minimum-high-retention", type=float, default=0.5)
    args = parser.parse_args()
    summary = evaluate(args.decisions, args.grades, args.output, args.split,
                       args.probability_threshold, args.score_cutoff,
                       args.selection_objective, args.minimum_high_retention)
    print(json.dumps({key: summary[key] for key in ("evaluated_documents", "document_modes",
                     "best_score_above_cutoff", "best_score_at_or_below_cutoff",
                     "generation_skips", "proposed_probability_threshold")}, indent=2))


if __name__ == "__main__":
    main()
