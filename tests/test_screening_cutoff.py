import hashlib
import json

import pytest

from clir_bench.domains.legal.qac.decider import MODES
from clir_bench.domains.legal.qac.screening_analysis import write_csv
from clir_bench.domains.legal.qac.screening_cutoff import evaluate
from clir_bench.domains.legal.qac.screening_eligibility_analysis import read_csv


@pytest.fixture
def cutoff_input(tmp_path):
    cases = {
        "un": {
            "lookup": (0.6, [(31, "clear", 4), (32, "blocking", 4)]),
            "practitioner": (0.8, [(31, "clear", 4)]),
            "conceptual": (0.3, [(34, "clear", 4)]),
            "comparison": (0.7, [(30, "clear", 4)]),
            "claim_verification": (0.9, [(35, "clear", 2)]),
            "source_finding": (0.4, []),
        },
        "eurlex": {
            "fact_pattern": (0.7, [(32, "clear", 4)]),
            "lookup": (0.5, [(32, "minor_issues", 4)]),
            "conceptual": (0.4, [(31, "clear", 4)]),
            "comparison": (0.2, [(30, "clear", 4)]),
            "claim_verification": (0.6, [(35, "blocking", 4)]),
            "source_finding": (0.8, []),
        },
    }
    decisions, grades, documents = [], [], []
    for corpus, modes in MODES.items():
        common = {"corpus": corpus, "document_id": corpus + "-doc",
                  "target_id": corpus + "-target", "symbol": corpus + "-symbol"}
        source = f"{corpus}: target source, with Unicode résolution."
        documents.append({"corpus": corpus, "document_id": common["document_id"],
                          "partition": "development" if corpus == "un" else "validation"})
        for mode in modes:
            probability, candidates = cases[corpus][mode]
            decisions.append(dict(common, mode=mode, probability_yes=probability,
                                  selected=probability >= 0.5, threshold=0.5,
                                  source_payload_sha256=hashlib.sha256(source.encode()).hexdigest()))
            for slot, candidate in enumerate(candidates or [None]):
                row = dict(common, mode=mode, source_payload=source, document_text=source,
                           candidate_id=f"{corpus}-{mode}-{slot}" if candidate else "",
                           question=f"Question, {mode}?\nPart two" if candidate else "",
                           answer="Answer" if candidate else "",
                           mode_status="completed" if candidate else "no_candidates")
                score, audit, grounding = candidate if candidate else (None, "", None)
                for field, value in {
                    "grading_status": "completed" if candidate else "",
                    "total_40": score, "grounding_5": grounding, "audit_status": audit,
                    "quality_reason": "Reason, first clause\nsecond clause" if candidate else "",
                    "faithfulness_reason": "Source grounded." if candidate else "",
                    "audit_reason": "Audit explanation." if candidate else "",
                }.items():
                    row["verifier 4__" + field] = value
                grades.append(row)
    paths = {"decisions": tmp_path / "decisions.csv", "grades": tmp_path / "grades.csv",
             "split": tmp_path / "split.json", "output": tmp_path / "evaluated"}
    write_csv(paths["decisions"], decisions)
    write_csv(paths["grades"], grades)
    paths["split"].write_text(json.dumps({"schema_version": 1, "seed": 20261007,
                                          "documents": documents}))
    return paths, decisions, grades, documents


def run(paths, **kwargs):
    return evaluate(paths["decisions"], paths["grades"], paths["output"], paths["split"], **kwargs)


def test_strict_numeric_cutoff_uses_maximum_independently_of_audit(cutoff_input):
    paths, _, grades, _ = cutoff_input
    summary = run(paths)
    assert summary["evaluated_documents"] == summary["source_grade_documents"] == 2
    assert summary["document_modes"] == 12
    assert summary["candidate_questions"] == 11
    assert summary["generation_skips"] == 2
    assert summary["scored_modes"] == 10
    assert summary["best_score_above_cutoff"] == 6
    assert summary["best_score_at_or_below_cutoff"] == 4
    assert summary["mean_best_total_40"] == 32.2
    overall = next(row for row in summary["metrics"]
                   if row["partition"] == row["corpus"] == row["mode"] == "all")
    assert [overall[key] for key in ("tp", "fp", "fn", "tn")] == [5, 3, 1, 3]
    assert overall["precision"] == 5 / 8
    assert overall["retention_rate_high"] == 5 / 6
    assert overall["rejection_rate_low"] == overall["specificity"] == 0.5
    assert overall["balanced_accuracy"] == pytest.approx(2 / 3)
    assert overall["fbeta_0_5"] == pytest.approx(6.25 / 9.5)
    modes = {(row["corpus"], row["mode"]): row
             for row in read_csv(paths["output"] / "cutoff_comparison.csv")}
    lookup = modes["un", "lookup"]
    assert lookup["best_total_40"] == "32.0"
    assert lookup["above_cutoff"] == "True"
    assert lookup["has_audit_passing_candidate_above_cutoff"] == "False"
    assert json.loads(lookup["best_candidate_ids_json"]) == ["un-lookup-1"]
    assert modes["un", "practitioner"]["above_cutoff"] == "False"
    assert modes["un", "source_finding"]["best_total_40"] == ""
    assert modes["un", "source_finding"]["above_cutoff"] == "False"
    assert modes["eurlex", "lookup"]["has_audit_passing_candidate_above_cutoff"] == "True"
    assert modes["un", "claim_verification"]["has_audit_passing_candidate_above_cutoff"] == "False"
    exported = read_csv(paths["output"] / "questions_with_cutoff_decisions.csv")
    original = read_csv(paths["grades"])
    assert len(exported) == len(grades)
    assert [{key: row[key] for key in original[0]} for row in exported] == original
    assert len(read_csv(paths["output"] / "cutoff_errors.csv")) == 4
    assert all(row["cutoff_confusion"] in ("FP", "FN")
               for row in read_csv(paths["output"] / "cutoff_error_questions.csv"))


def test_threshold_proposal_never_uses_validation_and_has_minimum_recall(cutoff_input):
    paths, decisions, grades, _ = cutoff_input
    summary = run(paths)
    proposal = summary["threshold_proposal_development_metrics"]
    assert proposal["partition"] == "development"
    assert proposal["accepted"] >= 1
    assert proposal["retention_rate_high"] >= 0.5
    assert summary["proposed_probability_threshold"] == pytest.approx(0.3)
    assert all(row["partition"] == "development" for row in
               read_csv(paths["output"] / "development_threshold_sweep.csv"))
    # Invert every validation label/probability. Development selection must be unchanged.
    for row in decisions:
        if row["corpus"] == "eurlex":
            row.update(probability_yes=1 - row["probability_yes"])
            row["selected"] = row["probability_yes"] >= 0.5
    for row in grades:
        if row["corpus"] == "eurlex" and row["candidate_id"]:
            row["verifier 4__total_40"] = 20 if row["verifier 4__total_40"] > 31 else 40
    write_csv(paths["decisions"], decisions)
    write_csv(paths["grades"], grades)
    changed = run(paths)
    assert changed["proposed_probability_threshold"] == summary["proposed_probability_threshold"]
    assert changed["threshold_proposal_development_metrics"] == proposal
    assert changed["proposed_threshold_metrics"] != summary["proposed_threshold_metrics"]


def test_probability_rethreshold_does_not_change_reference_or_recorded_choices(cutoff_input):
    paths, _, _, _ = cutoff_input
    original = run(paths)
    changed = run(paths, probability_threshold=0.9)
    assert changed["best_score_above_cutoff"] == original["best_score_above_cutoff"]
    rows = read_csv(paths["output"] / "cutoff_comparison.csv")
    assert sum(row["accepted"] == "True" for row in rows) == 1
    assert sum(row["recorded_selected"] == "True" for row in rows) == 8
    at_cutoff = next(row for row in rows if row["probability_yes"] == "0.9")
    assert at_cutoff["accepted"] == "True"


def test_low_rejection_objective_trades_high_retention_for_rejection(cutoff_input):
    paths, _, _, _ = cutoff_input
    default = run(paths)
    reject_low = run(paths, selection_objective="low_rejection")
    assert default["selection_objective"] == "fbeta_0_5"
    assert reject_low["selection_objective"] == "low_rejection"
    assert reject_low["minimum_high_retention"] == 0.5
    assert default["proposed_probability_threshold"] == pytest.approx(0.3)
    assert reject_low["proposed_probability_threshold"] == pytest.approx(0.6)
    fbeta_metrics = default["threshold_proposal_development_metrics"]
    rejection_metrics = reject_low["threshold_proposal_development_metrics"]
    assert rejection_metrics["rejection_rate_low"] > fbeta_metrics["rejection_rate_low"]
    assert rejection_metrics["retention_rate_high"] < fbeta_metrics["retention_rate_high"]
    assert rejection_metrics["retention_rate_high"] >= 0.5
    assert rejection_metrics["accepted"] >= 1
    strict = run(paths, selection_objective="low_rejection", minimum_high_retention=1)
    assert strict["proposed_probability_threshold"] == pytest.approx(0.3)
    assert strict["threshold_proposal_development_metrics"]["retention_rate_high"] == 1
    unconstrained = run(paths, selection_objective="low_rejection", minimum_high_retention=0)
    assert unconstrained["proposed_probability_threshold"] == pytest.approx(0.9)
    assert unconstrained["threshold_proposal_development_metrics"]["accepted"] == 1


@pytest.mark.parametrize("minimum", [-0.1, 1.1, float("nan"), float("inf"), True])
def test_invalid_minimum_high_retention_fails_before_export(cutoff_input, minimum):
    paths, _, _, _ = cutoff_input
    with pytest.raises(ValueError, match="Invalid minimum_high_retention"):
        run(paths, minimum_high_retention=minimum)
    assert not paths["output"].exists()


def test_unknown_selection_objective_fails_before_export(cutoff_input):
    paths, _, _, _ = cutoff_input
    with pytest.raises(ValueError, match="Unknown selection_objective"):
        run(paths, selection_objective="validation_precision")
    assert not paths["output"].exists()


def test_complete_development_subset_joins_against_full_grades(cutoff_input):
    paths, decisions, _, _ = cutoff_input
    write_csv(paths["decisions"], [row for row in decisions if row["corpus"] == "un"])
    summary = run(paths)
    assert summary["evaluated_documents"] == 1
    assert summary["source_grade_documents"] == 2
    assert summary["omitted_grade_documents"] == 1
    assert summary["document_modes"] == 6
    assert "validation" not in {row["partition"] for row in summary["metrics"]}
    assert {row["corpus"] for row in read_csv(paths["output"] / "questions_with_cutoff_decisions.csv")} == {"un"}


def test_no_split_never_implicitly_calibrates_on_all_data(cutoff_input):
    paths, _, _, _ = cutoff_input
    summary = evaluate(paths["decisions"], paths["grades"], paths["output"])
    assert summary["proposed_probability_threshold"] is None
    assert summary["threshold_proposal_development_metrics"] is None
    assert {row["partition"] for row in summary["metrics"]} == {"all", "unassigned"}


@pytest.mark.parametrize("failure,match", [
    ("duplicate_decision", "Duplicate cutoff decision"),
    ("missing_mode", "all six modes"),
    ("wrong_document", "documents absent from grades"),
    ("shifted_target", "Unexpected grade target/mode"),
    ("wrong_source", "Source payload mismatch"),
    ("missing_grade_group", "lack matching grade groups"),
    ("duplicate_candidate", "Duplicate candidate ID"),
    ("incomplete_grade", "incomplete grading"),
    ("missing_numeric_grade", "Invalid total_40"),
    ("nonfinite_probability", "Invalid probability_yes"),
    ("invalid_boolean", "Invalid selected boolean"),
    ("inconsistent_decision", "disagrees with threshold"),
    ("duplicate_split", "Duplicate document in split"),
    ("missing_split", "Split lacks decision documents"),
])
def test_invalid_or_leaking_inputs_fail_before_export(cutoff_input, failure, match):
    paths, decisions, grades, documents = cutoff_input
    if failure == "duplicate_decision":
        decisions.append(dict(decisions[0]))
    elif failure == "missing_mode":
        decisions.pop()
    elif failure == "wrong_document":
        for row in decisions:
            if row["corpus"] == "un":
                row["document_id"] = "wrong-document"
    elif failure == "shifted_target":
        grades[0]["target_id"] = "unexpected-target"
    elif failure == "wrong_source":
        grades[0]["source_payload"] += " changed"
    elif failure == "missing_grade_group":
        grades.pop()
    elif failure == "duplicate_candidate":
        grades[1]["candidate_id"] = grades[0]["candidate_id"]
    elif failure == "incomplete_grade":
        grades[0]["verifier 4__grading_status"] = "failed"
    elif failure == "missing_numeric_grade":
        grades[0]["verifier 4__total_40"] = ""
    elif failure == "nonfinite_probability":
        decisions[0]["probability_yes"] = "nan"
    elif failure == "invalid_boolean":
        decisions[0]["selected"] = "yes"
    elif failure == "inconsistent_decision":
        decisions[0]["selected"] = not decisions[0]["selected"]
    elif failure == "duplicate_split":
        documents.append(dict(documents[0], partition="validation"))
    elif failure == "missing_split":
        documents.pop()
    write_csv(paths["decisions"], decisions)
    write_csv(paths["grades"], grades)
    paths["split"].write_text(json.dumps({"schema_version": 1, "documents": documents}))
    with pytest.raises(ValueError, match=match):
        run(paths)
    assert not paths["output"].exists()


def test_no_high_reference_scores_has_no_threshold_proposal(cutoff_input):
    paths, _, grades, _ = cutoff_input
    for row in grades:
        if row["candidate_id"]:
            row["verifier 4__total_40"] = 31
    write_csv(paths["grades"], grades)
    summary = run(paths)
    assert summary["best_score_above_cutoff"] == 0
    assert summary["proposed_probability_threshold"] is None
    assert all(row["retention_rate_high"] is None for row in summary["metrics"])
