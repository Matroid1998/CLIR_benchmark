import csv
import hashlib
import json

import pytest

from clir_bench.domains.legal.qac.experiment_evaluation import (
    SCORES,
    prepare,
    validate,
    validate_generation_completion,
)


def mode_outcomes():
    return [{"corpus": "un", "target_id": "doc#1", "mode": mode, "eligible": True,
             "status": "completed" if mode == "practitioner" else "no_candidates",
             "candidate_count": 1 if mode == "practitioner" else 0}
            for mode in ("lookup", "practitioner", "semantic")]


@pytest.mark.parametrize("malformation", ["changed_text", "duplicate_target"])
def test_prepare_refuses_malformed_selection_before_reading_runs(tmp_path, malformation):
    row = {"corpus": "un", "target_id": "doc#1", "source_payload": "source",
           "source_payload_sha256": hashlib.sha256(b"source").hexdigest()}
    selection = [row]
    if malformation == "changed_text":
        row["source_payload"] = "different source"
        message = "source payload hash mismatch"
    else:
        selection.append(row.copy())
        message = "Duplicate selection target"
    with pytest.raises(ValueError, match=message):
        prepare({"test": tmp_path / "does_not_exist"}, selection)


def test_judge_inputs_hide_version_and_mode_and_deduplicate_pairs(tmp_path):
    selection = [{"corpus": "un", "target_id": "doc#1", "symbol": "S/1", "is_meeting": False,
                  "source_payload": "source", "source_payload_sha256": hashlib.sha256(b"source").hexdigest()}]
    runs = {}
    for version in ("baseline", "debiased", "simple"):
        path = tmp_path / version
        path.mkdir()
        runs[version] = path
        (path / "selection.json").write_text(json.dumps(selection))
        (path / "config.json").write_text(json.dumps({"generator": "g", "verifier": "v",
            "language": "en", "keep": 3, "meeting_modes": "all"}))
        row = {"corpus": "un", "target_id": "doc#1", "candidate_id": version,
               "screening_mode": "practitioner", "question": "Which measure?", "answer": "measure",
               "source_payload_sha256": selection[0]["source_payload_sha256"], "total_score": "40"}
        with (path / "all_mode_candidates.csv").open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        outcomes = mode_outcomes()
        with (path / "mode_runs.csv").open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(outcomes[0]))
            writer.writeheader()
            writer.writerows(outcomes)
    jobs, memberships = prepare(runs, selection)
    assert len(jobs) == 1
    envelope = jobs[0][1]
    assert len(envelope["candidates"]) == 1
    assert set(envelope["candidates"][0]) == {"candidate_id", "question", "answer"}
    assert len(memberships) == 3
    assert len({row["blind_id"] for row in memberships}) == 1
    assert all(word not in json.dumps(envelope) for word in ("baseline", "debiased", "simple", "practitioner", "total_score"))
    assert prepare(dict(reversed(list(runs.items()))), selection) == (jobs, memberships)
    (runs["simple"] / "mode_runs.csv").write_text("corpus,target_id,mode,eligible,status,candidate_count\n")
    with pytest.raises(ValueError, match="missing generation outcomes"):
        prepare(runs, selection)


@pytest.fixture
def generation_data():
    return ([{"corpus": "un", "target_id": "doc#1"}], {"meeting_modes": "all"},
            mode_outcomes(), [{"corpus": "un", "target_id": "doc#1", "screening_mode": "practitioner",
                               "question": "Which measure?", "answer": "measure",
                               "grading_status": "completed"}])


def test_completed_generation_with_failed_native_grading_can_be_evaluated(generation_data):
    selection, config, outcomes, candidates = generation_data
    outcomes[1]["status"] = "failed"
    candidates[0]["grading_status"] = "failed"
    validate_generation_completion("test", selection, config, outcomes, candidates)


@pytest.mark.parametrize("change", ["missing", "pending", "failed_empty", "wrong_count",
                                   "duplicate", "unexpected", "blank_answer", "ineligible",
                                   "empty_completed", "nonempty_no_candidates", "unfinalized_grading"])
def test_generation_preflight_rejects_missing_or_inconsistent_attempts(generation_data, change):
    selection, config, outcomes, candidates = generation_data
    if change == "missing":
        outcomes.pop()
    elif change == "pending":
        outcomes[0]["status"] = "pending"
    elif change == "failed_empty":
        outcomes[0]["status"] = "failed"
    elif change == "wrong_count":
        outcomes[1]["candidate_count"] = 2
    elif change == "duplicate":
        outcomes.append(outcomes[0].copy())
    elif change == "unexpected":
        outcomes[0]["mode"] = "fact_pattern"
    elif change == "blank_answer":
        candidates[0]["answer"] = " "
    elif change == "ineligible":
        outcomes[0]["eligible"] = False
    elif change == "empty_completed":
        outcomes[0]["status"] = "completed"
    elif change == "nonempty_no_candidates":
        outcomes[1]["status"] = "no_candidates"
    else:
        outcomes[1]["status"] = "failed"
        candidates[0]["grading_status"] = "pending"
    with pytest.raises(ValueError):
        validate_generation_completion("test", selection, config, outcomes, candidates)


def test_generation_preflight_rejects_unsupported_meeting_filter(generation_data):
    selection, config, outcomes, candidates = generation_data
    config["meeting_modes"] = "semantic_only"
    with pytest.raises(ValueError, match="unsupported meeting_modes"):
        validate_generation_completion("test", selection, config, outcomes, candidates)


def test_expected_attempts_are_derived_from_selected_corpora():
    selection = [{"corpus": "eurlex", "target_id": "article1"}]
    outcomes = [{"corpus": "eurlex", "target_id": "article1", "mode": mode, "eligible": "True",
                 "status": "no_candidates", "candidate_count": "0"}
                for mode in ("fact_pattern", "lookup")]
    validate_generation_completion("test", selection, {"meeting_modes": "all"}, outcomes, [])


def response():
    return {"candidates": [{"index": 0, "candidate_id": "q1", "scores": dict.fromkeys(SCORES, 5),
                             "reasons": dict.fromkeys(SCORES, "Specific supporting evidence")} ]}


def test_usability_gate_rejects_high_total_with_unsupported_answer():
    data = response()
    data["candidates"][0]["scores"]["grounding"] = 2
    result = validate(data, [{"candidate_id": "q1"}])[0]
    assert result["total"] == 22
    assert result["usable"] is False


def test_usability_gate_rejects_useless_or_unreadable_candidates():
    for criterion in ("information_value", "clarity"):
        data = response()
        data["candidates"][0]["scores"][criterion] = 1
        assert validate(data, [{"candidate_id": "q1"}])[0]["usable"] is False


@pytest.mark.parametrize("change", ["identity", "order", "score", "missing"])
def test_evaluation_never_accepts_misattributed_or_fabricated_scores(change):
    data = response()
    row = data["candidates"][0]
    if change == "identity":
        row["candidate_id"] = "another"
    elif change == "order":
        row["index"] = 1
    elif change == "score":
        row["scores"]["grounding"] = True
    else:
        del row["scores"]["clarity"]
    with pytest.raises(ValueError):
        validate(data, [{"candidate_id": "q1"}])
