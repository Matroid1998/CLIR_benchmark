import hashlib
import json

import pytest

from clir_bench.domains.legal.qac.decider import MODES
from clir_bench.domains.legal.qac.screening_analysis import write_csv
from clir_bench.domains.legal.qac.screening_eligibility_analysis import VERIFIERS, analyze, read_csv


@pytest.fixture
def comparison_input(tmp_path):
    # Include grounded/non-grounded passes, audit failures, a grading failure,
    # generation skips, and a multi-candidate batch whose best score fails audit.
    cases = {
        "un": {
            "lookup": (0.5, [(39, "clear", 2)]),
            "practitioner": (0.7, [(40, "clear", 5)]),
            "conceptual": (0.2, [(30, "minor_issues", 3)]),
            "comparison": (0.1, [(39, "blocking", 5)]),
            "claim_verification": (0.8, [(38, "blocking", 5), (25, "minor_issues", 3)]),
            "source_finding": (0.9, []),
        },
        "eurlex": {
            "fact_pattern": (0.4, [(20, "clear", 0)]),
            "lookup": (0.8, [(40, "minor_issues", 0)]),
            "conceptual": (0.1, [(25, "blocking", 5)]),
            "comparison": (0.8, [(None, "", None)]),
            "claim_verification": (0.1, [(30, "clear", 5)]),
            "source_finding": (0.1, []),
        },
    }
    decisions, grades = [], []
    for corpus, modes in MODES.items():
        source = f"{corpus} source, with Unicode: résolution\nsecond line"
        common = {"corpus": corpus, "document_id": corpus + "-doc", "target_id": corpus + "-target",
                  "symbol": "A/TEST" if corpus == "un" else "32000R0001"}
        for mode in modes:
            probability, candidates = cases[corpus][mode]
            decisions.append(dict(common, mode=mode, probability_yes=probability, selected=probability >= 0.5,
                                  threshold=0.5, previous_pick="lookup", previous_confidence=0.8,
                                  response_model="typesafe/test-model",
                                  source_payload_sha256=hashlib.sha256(source.encode()).hexdigest()))
            for slot, candidate in enumerate(candidates or [None]):
                row = dict(common, mode=mode, source_payload=source, document_text=source,
                           decider_pick="lookup", decider_confidence=0.8,
                           mode_status="completed" if candidates else "no_candidates",
                           generation_skip_reason="" if candidates else "No suitable question",
                           candidate_id=f"{corpus}-{mode}-{slot}" if candidate else "",
                           question=f"Question, {mode}?\nPart two" if candidate else "",
                           answer="Answer" if candidate else "")
                for verifier in VERIFIERS:
                    score, audit, grounding = candidate if candidate else (None, "", None)
                    if verifier == "verifier 5" and corpus == "un" and mode == "lookup":
                        grounding = 5
                    for field, value in {
                        "grading_status": ("completed" if score is not None else "failed") if candidate else "",
                        "total_40": score, "audit_status": audit, "grounding_5": grounding,
                        "quality_reason": "Reason, first clause\nsecond clause" if candidate else "",
                    }.items():
                        row[verifier + "__" + field] = value
                grades.append(row)
    output = tmp_path / "output"
    output.mkdir()
    grades_csv = tmp_path / "grades.csv"
    write_csv(output / "decisions.csv", decisions)
    write_csv(grades_csv, grades)
    return output, grades_csv, decisions, grades


def test_comparison_preserves_questions_and_reports_observed_passes(comparison_input):
    output, grades_csv, _, _ = comparison_input
    original = read_csv(grades_csv)
    summary = analyze(output, grades_csv)
    assert summary["documents"] == 2
    assert summary["document_modes"] == 12
    assert summary["candidate_questions"] == 11
    assert summary["generation_skips"] == 2
    assert summary["yes_count"] == summary["no_count"] == 6
    assert summary["eligible_modes_per_document"] == {2: 1, 4: 1}
    exported = read_csv(output / "questions_with_jev_and_grades.csv")
    assert len(exported) == len(original) == 13
    for before, after in zip(original, exported):
        assert {key: after[key] for key in before} == before
        assert after["jev_previous_pick"] == "lookup"
    equality_case = next(row for row in exported if row["corpus"] == "un" and row["mode"] == "lookup")
    assert equality_case["jev_eligibility_yes"] == "True"
    assert equality_case["jev_probability_yes"] == equality_case["jev_threshold"] == "0.5"

    modes = { (row["corpus"], row["mode"]): row for row in read_csv(output / "mode_comparison.csv") }
    assert modes["un", "lookup"]["verifier 4__has_passing_candidate"] == "False"
    assert modes["un", "lookup"]["verifier 5__has_passing_candidate"] == "True"
    assert modes["eurlex", "fact_pattern"]["verifier 4__has_passing_candidate"] == "True"
    claim = modes["un", "claim_verification"]
    assert claim["candidate_count"] == "2"
    assert claim["verifier 4__passing_candidate_count"] == "1"
    assert float(claim["verifier 4__best_total_40"]) == 38
    assert float(claim["verifier 4__mean_total_40"]) == 31.5
    assert len(json.loads(claim["questions_json"])) == 2

    metrics = next(row for row in summary["overall_statistics"] if row["verifier"] == "verifier 4")
    assert [metrics[key] for key in ("tp", "fp", "fn", "tn")] == [3, 3, 3, 3]
    assert metrics["precision"] == metrics["recall"] == 0.5
    assert metrics["observed_viable_mode_count"] == 6
    assert metrics["baseline_selected_count"] == 2
    assert metrics["baseline_precision"] == 0.5
    assert metrics["baseline_recall"] == pytest.approx(1 / 6)
    assert metrics["mean_best_total_40_selected"] == 39.25
    assert metrics["mean_best_total_40_rejected"] == 28.8
    assert metrics["selected_scored_mode_count"] == 4
    assert metrics["rejected_scored_mode_count"] == 5
    assert metrics["ungraded_candidate_count"] == 1
    other = next(row for row in summary["overall_statistics"] if row["verifier"] == "verifier 5")
    assert other["precision"] == pytest.approx(2 / 3)
    assert other["recall"] == pytest.approx(4 / 7)
    report = (output / "analysis.md").read_text()
    assert "probabilities have not been calibrated" in report
    assert "does not prove that a mode is impossible" in report
    assert len(read_csv(output / "comparison_statistics.csv")) == 75
    for name in ("questions_with_jev_and_grades.csv", "mode_comparison.csv", "comparison_statistics.csv"):
        assert "typesafe/test-model" not in (output / name).read_text(encoding="utf-8-sig")


def test_no_decisions_selected_has_undefined_precision_and_preserves_skips(comparison_input):
    output, grades_csv, decisions, _ = comparison_input
    for row in decisions:
        row.update(probability_yes=0.1, selected=False)
    write_csv(output / "decisions.csv", decisions)
    summary = analyze(output, grades_csv)
    assert summary["documents_with_no_yes"] == 2
    assert summary["yes_count"] == 0
    assert all(row["precision"] is None and row["recall"] == 0 for row in summary["overall_statistics"])
    assert all(row["mean_best_total_40_selected"] is None for row in summary["overall_statistics"])
    statistics = read_csv(output / "comparison_statistics.csv")
    assert all(row["precision"] == "" for row in statistics)


@pytest.mark.parametrize("failure,match", [
    ("duplicate_decision", "Duplicate eligibility"),
    ("missing_mode", "all six modes"),
    ("wrong_document", "Different document_id"),
    ("wrong_source", "Source payload mismatch"),
    ("missing_grade_group", "lack matching grades"),
    ("duplicate_candidate", "Duplicate candidate ID"),
    ("wrong_prior_pick", "Different previous pick"),
    ("nonfinite_probability", "Invalid probability_yes"),
    ("invalid_boolean", "Invalid selected boolean"),
    ("inconsistent_decision", "disagrees with threshold"),
])
def test_comparison_rejects_mismatched_or_invalid_inputs(comparison_input, failure, match):
    output, grades_csv, decisions, grades = comparison_input
    if failure == "duplicate_decision":
        decisions.append(dict(decisions[0]))
    elif failure == "missing_mode":
        decisions.pop()
    elif failure == "wrong_document":
        grades[0]["document_id"] = "different-document"
    elif failure == "wrong_source":
        grades[0]["source_payload"] += " changed"
    elif failure == "missing_grade_group":
        grades.pop()
    elif failure == "duplicate_candidate":
        grades[1]["candidate_id"] = grades[0]["candidate_id"]
    elif failure == "wrong_prior_pick":
        grades[0]["decider_pick"] = "conceptual"
    elif failure == "nonfinite_probability":
        decisions[0]["probability_yes"] = "nan"
    elif failure == "invalid_boolean":
        decisions[0]["selected"] = "yes"
    elif failure == "inconsistent_decision":
        decisions[0]["selected"] = not decisions[0]["selected"]
    write_csv(output / "decisions.csv", decisions)
    write_csv(grades_csv, grades)
    with pytest.raises(ValueError, match=match):
        analyze(output, grades_csv)
    assert not (output / "questions_with_jev_and_grades.csv").exists()
