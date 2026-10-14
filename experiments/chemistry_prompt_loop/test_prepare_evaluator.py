"""Offline checks for neutral packets, full review coverage, and immutable inputs."""

import csv
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location("prepare_chemistry_evaluator", Path(__file__).with_name("prepare_evaluator.py"))
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


def write_csv(path, rows, fields=None):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def round_fixture(tmp_path, monkeypatch):
    base = tmp_path / "rounds"
    directory = base / "round_01"
    directory.mkdir(parents=True)
    monkeypatch.setattr(evaluator, "BASE", base)
    make_temp = evaluator.tempfile.mkdtemp
    monkeypatch.setattr(evaluator, "tempfile", SimpleNamespace(
        mkdtemp=lambda prefix: make_temp(prefix=prefix, dir=tmp_path)))
    sources = [
        {"source_index": index, "source_document_id": f"source{index}", "publication_number": f"pub{index}",
         "source_document_language": "en", "source_document_text": f"Chemical abstract {index}."}
        for index in (1, 2)
    ]
    candidates = [
        {"candidate_id": f"s001c{index}", "source_document_id": "source1", "mode": "lookup",
         "question": f"Which material {index}?", "answer": "Chemical abstract 1.",
         "evidence": "Chemical abstract 1.", "source_document_text": "Chemical abstract 1."}
        for index in (1, 2)
    ]
    write_csv(directory / "sources_only.csv", sources)
    write_csv(directory / "blinded_candidates.csv", candidates)
    write_csv(directory / "review_with_source.csv", [dict(row, total_score=32) for row in candidates])
    evaluator.write_json(directory / "sources_and_decisions.json", [
        dict(source, decider_selected_mode="lookup" if source["source_index"] == 1 else "skip")
        for source in sources
    ])
    evaluator.write_json(directory / "manifest.json", {"round": 1, "document_count": 2,
                                                       "optimization_history": "DO_NOT_COPY_HISTORY"})
    evaluator.write_json(directory / "run_state.json", {"status": "complete"})
    evaluator.write_json(directory / "summary.json", {
        "round": 1, "prepared_sources": 2, "canonical_candidate_count": 2, "decider_skips": 1,
        "optimization_targets": "DO_NOT_COPY_TARGETS", "previous_ratings": "DO_NOT_COPY_RATINGS",
    })
    evaluator.write_json(directory / "errors.json", [])
    (directory / "evaluation_contract.md").write_text("Fixed independent chemistry contract.")
    refusal = directory / "documents/002/generation/attempt_01/call_00.json"
    refusal.parent.mkdir(parents=True)
    evaluator.write_json(refusal, {"request": {"prompt": "DO_NOT_COPY_PROMPT"},
                                   "response": {"choices": [{"finish_reason": "content_filter"}]}})
    return directory


def complete_outputs(packet):
    evaluator.write_json(packet / "independent_eligibility.json", [
        {"source_document_id": f"source{index}", "eligible_modes": ["lookup"] if index == 1 else [],
         "uncertain_modes": [], "notes": "Source-based independent reasoning."}
        for index in (1, 2)
    ])
    rows = [{"candidate_id": f"s001c{index}", "source_document_id": "source1", "mode": "lookup",
             "readiness": "ready" if index == 1 else "minor_edit", "generator_rating_10": "8.5",
             "source_support": "pass", "mode_fit": "pass", "metadata_ok": "pass",
             "issue_details": "", "suggested_repair": ""} for index in (1, 2)]
    write_csv(packet / "independent_candidates.csv", rows)
    evaluation = {"ratings": {"generator": 8.5, "verifier": 7.5, "decider": 8},
                  "coverage": {"sources_reviewed": 2, "candidates_reviewed": 2, "skips_reviewed": 1},
                  "generator": {"readiness_counts": {"ready": 1, "minor_edit": 1, "major_issue": 0}}}
    evaluator.write_json(packet / "evaluation.json", evaluation)
    return evaluation


def test_packet_is_neutral_complete_and_uses_exact_isolated_model(round_fixture):
    packet, task = evaluator.prepare(1)
    invocation = evaluator.load_json(round_fixture / "evaluator_invocation.json")
    assert invocation["model"] == "gpt-6-astra"
    assert invocation["reasoning_effort"] == "xhigh"
    assert invocation["fork_turns"] == "none"
    assert {p.name for p in packet.iterdir()} == set(evaluator.INPUT_MAPPING.values()) | {
        "run_summary.json", "evaluation_task.txt"}
    content = "\n".join(path.read_text() for path in packet.iterdir())
    assert "DO_NOT_COPY" not in content
    assert str(round_fixture) not in content
    assert "{packet_dir}" not in task
    summary = evaluator.load_json(packet / "run_summary.json")
    assert "round" not in summary
    assert summary["provider_refusal_attempts"] == [
        {"source_index": 2, "stage": "generation", "finish_reason": "content_filter", "native_finish_reason": None}]
    assert evaluator.prepare(1) == (packet, task)


def test_collection_preserves_input_hashes_and_copies_all_outputs(round_fixture):
    packet, _ = evaluator.prepare(1)
    invocation = evaluator.load_json(round_fixture / "evaluator_invocation.json")
    before = {name: (packet / name).read_bytes() for name in invocation["input_sha256"]}
    evaluation = complete_outputs(packet)
    assert evaluator.collect(1) == evaluation
    saved = evaluator.load_json(round_fixture / "evaluator_invocation.json")
    assert saved["input_sha256"] == invocation["input_sha256"]
    assert saved["task_sha256"] == invocation["task_sha256"]
    assert saved["status"] == "completed"
    assert {name: (packet / name).read_bytes() for name in before} == before
    for name in evaluator.OUTPUT_FILES:
        assert (round_fixture / "evaluation" / name).read_bytes() == (packet / name).read_bytes()


@pytest.mark.parametrize("target", ["sources.csv", "blinded_candidates.csv", "evaluation_task.txt"])
def test_cached_prepare_and_collect_reject_tampered_inputs(round_fixture, target):
    packet, _ = evaluator.prepare(1)
    complete_outputs(packet)
    path = packet / target
    path.write_bytes(path.read_bytes() + b"\nchanged")
    for action in (evaluator.prepare, evaluator.collect):
        with pytest.raises(ValueError, match="changed"):
            action(1)


def test_collect_rejects_changed_original_round_input(round_fixture):
    packet, _ = evaluator.prepare(1)
    complete_outputs(packet)
    path = round_fixture / "summary.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Round input changed"):
        evaluator.collect(1)


@pytest.mark.parametrize("change", ["duplicate", "missing", "wrong_source", "wrong_mode", "bad_rating"])
def test_candidate_review_coverage_identity_and_ratings(round_fixture, change):
    packet, _ = evaluator.prepare(1)
    complete_outputs(packet)
    fields, rows = evaluator.read_csv(packet / "independent_candidates.csv")
    if change == "duplicate":
        rows[1] = rows[0]
    elif change == "missing":
        rows.pop()
    elif change == "wrong_source":
        rows[0]["source_document_id"] = "source2"
    elif change == "wrong_mode":
        rows[0]["mode"] = "comparison"
    else:
        rows[0]["generator_rating_10"] = "NaN"
    write_csv(packet / "independent_candidates.csv", rows, fields)
    with pytest.raises(ValueError):
        evaluator.collect(1)
    assert not (round_fixture / "evaluation").exists()


@pytest.mark.parametrize("change", ["duplicate", "missing", "unknown_mode", "overlapping_modes"])
def test_eligibility_review_covers_every_source_with_valid_mode_sets(round_fixture, change):
    packet, _ = evaluator.prepare(1)
    complete_outputs(packet)
    rows = evaluator.load_json(packet / "independent_eligibility.json")
    if change == "duplicate":
        rows[1] = rows[0]
    elif change == "missing":
        rows.pop()
    elif change == "unknown_mode":
        rows[0]["eligible_modes"] = ["made_up_mode"]
    else:
        rows[0]["uncertain_modes"] = ["lookup"]
    evaluator.write_json(packet / "independent_eligibility.json", rows)
    with pytest.raises(ValueError):
        evaluator.collect(1)


@pytest.mark.parametrize("change", ["skips", "boolean_count", "readiness", "nan_rating"])
def test_reported_counts_and_ratings_must_match_review(round_fixture, change):
    packet, _ = evaluator.prepare(1)
    evaluation = complete_outputs(packet)
    if change == "skips":
        evaluation["coverage"]["skips_reviewed"] = 0
    elif change == "boolean_count":
        evaluation["coverage"]["skips_reviewed"] = True
    elif change == "readiness":
        evaluation["generator"]["readiness_counts"]["ready"] = 2
    else:
        evaluation["ratings"]["verifier"] = float("nan")
    evaluator.write_json(packet / "evaluation.json", evaluation)
    with pytest.raises(ValueError):
        evaluator.collect(1)


@pytest.mark.parametrize("change", ["model_grade_in_blind", "duplicate_source", "missing_routing", "scored_content_changed"])
def test_prepare_rejects_broken_blinding_and_inconsistent_inputs(round_fixture, change):
    if change == "model_grade_in_blind":
        _, rows = evaluator.read_csv(round_fixture / "blinded_candidates.csv")
        write_csv(round_fixture / "blinded_candidates.csv", [dict(row, total_score=40) for row in rows])
    elif change == "duplicate_source":
        fields, rows = evaluator.read_csv(round_fixture / "sources_only.csv")
        write_csv(round_fixture / "sources_only.csv", [rows[0], rows[0]], fields)
    elif change == "missing_routing":
        rows = evaluator.load_json(round_fixture / "sources_and_decisions.json")
        evaluator.write_json(round_fixture / "sources_and_decisions.json", rows[:1])
    else:
        fields, rows = evaluator.read_csv(round_fixture / "review_with_source.csv")
        rows[0]["question"] = "Changed question"
        write_csv(round_fixture / "review_with_source.csv", rows, fields)
    with pytest.raises(ValueError):
        evaluator.prepare(1)
    assert not (round_fixture / "evaluator_invocation.json").exists()


def test_old_packets_remain_collectable_without_new_round_hashes(round_fixture):
    packet, _ = evaluator.prepare(1)
    complete_outputs(packet)
    invocation = evaluator.load_json(round_fixture / "evaluator_invocation.json")
    invocation.pop("round_input_sha256")
    evaluator.write_json(round_fixture / "evaluator_invocation.json", invocation)
    assert evaluator.collect(1)["coverage"]["sources_reviewed"] == 2


def test_prepare_requires_terminal_run_and_cap(round_fixture):
    evaluator.write_json(round_fixture / "run_state.json", {"status": "running"})
    with pytest.raises(ValueError, match="finish"):
        evaluator.prepare(1)
    with pytest.raises(ValueError, match="limits"):
        evaluator.prepare(6)
    evaluator.write_json(round_fixture / "run_state.json", {"status": "complete"})
    evaluator.write_json(round_fixture / "manifest.json", {"round": 1, "document_count": 51})
    with pytest.raises(ValueError, match="limits"):
        evaluator.prepare(1)
