"""Offline checks for the experiment's budget, integrity, and replay guarantees."""

import importlib.util
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location("chemistry_round_runner", Path(__file__).with_name("run_round.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def source(index, language="en", family=None):
    return {"id": f"document_{index}_{language}", "publication_number": family or f"publication_{index}",
            "language": language, "abstract": "Explicit chemical source text.", "source_index": index}


def test_sampling_is_reproducible_balanced_disjoint_and_capped():
    corpus = [source(i * 5 + j, language) for i in range(30)
              for j, language in enumerate(runner.LANGUAGES)]
    options = {"excluded_ids": {corpus[0]["id"]},
               "excluded_families": {corpus[1]["publication_number"]}, "count": 50, "seed": 7}
    first = runner.sample_sources(corpus, **options)
    assert first == runner.sample_sources(list(reversed(corpus)), **options)
    assert len(first) == len({s["id"] for s in first}) == 50
    assert all(sum(s["language"] == lang for s in first) == 10 for lang in runner.LANGUAGES)
    assert not {s["id"] for s in first} & options["excluded_ids"]
    second = runner.sample_sources(corpus, excluded_ids={s["id"] for s in first},
                                   excluded_families={s["publication_number"] for s in first},
                                   count=50, seed=8)
    assert not {s["publication_number"] for s in first} & {s["publication_number"] for s in second}
    with pytest.raises(ValueError, match="between 1 and 50"):
        runner.sample_sources(corpus, **dict(options, count=51))


def test_completed_stage_does_not_repeat_after_later_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.time, "sleep", lambda _: None)
    document = source(1)
    calls = []

    def generate(_):
        calls.append("generate")
        return [{"question": "Which compound?", "answer": "A"}]

    def fail(_):
        calls.append("grade")
        raise ValueError("malformed grade")

    options = {"client": None, "retry_errors": False, "retry_uncertain": False}
    generated = runner.execute_stage(tmp_path, document, "generation", generate, **options)
    assert runner.execute_stage(tmp_path, document, "faithfulness", fail, **options) is None
    assert runner.execute_stage(tmp_path, document, "generation", generate, **options) == generated
    assert calls.count("generate") == 1
    assert calls.count("grade") == 3
    assert runner.execute_stage(tmp_path, document, "faithfulness", fail, **options) is None
    assert calls.count("grade") == 3
    assert runner.execute_stage(tmp_path, document, "faithfulness", lambda _: [4],
                                **dict(options, retry_errors=True)) == [4]
    assert len(list(tmp_path.glob("documents/001/faithfulness/attempt_*/validation.json"))) == 4


def test_interrupted_stage_replays_received_response_without_provider_call(tmp_path):
    document = source(1)
    path = runner.stage_directory(tmp_path, document, "generation")
    runner.write_json(path / "state.json", {"status": "running", "attempt": 1})
    request = {"model": "fixture", "messages": [{"role": "user", "content": "source"}]}
    recorder = runner.CallRecorder(path / "attempt_01", None)
    assert recorder.call(request, lambda: {"answer": "saved"}) == {"answer": "saved"}

    def resume(recorder):
        def must_not_call():
            pytest.fail("Completed paid call was repeated")
        return recorder.call(request, must_not_call)

    assert runner.execute_stage(tmp_path, document, "generation", resume, None,
                                retry_errors=False, retry_uncertain=False) == {"answer": "saved"}


def test_unknown_provider_outcome_requires_explicit_retry(tmp_path):
    document = source(1)
    path = runner.stage_directory(tmp_path, document, "generation")
    runner.write_json(path / "state.json", {"status": "running", "attempt": 1})
    request = {"model": "fixture"}
    runner.write_json(path / "attempt_01/call_00.json", {
        "status": "started", "started_at": runner.now(), "request": request,
        "request_sha256": runner.digest(runner.json.dumps(request, sort_keys=True, ensure_ascii=False).encode()),
    })

    def resume(recorder):
        return recorder.call(request, lambda: pytest.fail("Unknown paid outcome retried automatically"))

    assert runner.execute_stage(tmp_path, document, "generation", resume, None,
                                retry_errors=True, retry_uncertain=False) is None
    assert runner.read_json(path / "state.json")["status"] == "running"


def test_provider_specific_service_tier_keeps_content_and_raw_envelope_verbatim(tmp_path):
    content = '  [{"answer": "μm ≥ 2"}]\n'
    raw = {"service_tier": "provisioned", "choices": [{"message": {"content": content}}],
           "provider_specific": {"untouched": True}}
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **_: SimpleNamespace(model_dump=lambda: raw))))
    recorder = runner.CallRecorder(tmp_path, client)
    response = recorder.create(model="fixture", messages=[])
    assert response.choices[0].message.content == content
    assert response.model_dump() == raw
    saved = runner.read_json(tmp_path / "call_00.json")
    assert saved["response"] == raw
    assert runner.OfflineRecorder(tmp_path, None).create(model="fixture", messages=[]).model_dump() == raw


def test_offline_adapter_does_not_turn_content_filter_refusal_into_content(tmp_path):
    raw = {"service_tier": "provisioned", "choices": [
        {"message": {"content": None, "refusal": "provider refusal"}, "finish_reason": "content_filter"}]}
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **_: SimpleNamespace(model_dump=lambda: raw))))
    response = runner.CallRecorder(tmp_path, client).create(model="fixture", messages=[])
    assert response.choices[0].message.content is None
    assert response.model_dump()["choices"][0]["finish_reason"] == "content_filter"
    with pytest.raises(runner.OfflineReplayError, match="No recorded call"):
        runner.OfflineRecorder(tmp_path / "missing", None).create(model="fixture", messages=[])


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.csv"
    rows = [source(i * 5 + j, language) for i in range(4)
            for j, language in enumerate(runner.LANGUAGES)]
    runner.write_csv(corpus, rows, list(rows[0]))
    qac = tmp_path / "prior"
    qac.mkdir()
    monkeypatch.setattr(runner, "QAC", qac)
    contract = tmp_path / "contract.md"
    contract.write_text("Fixed independent evaluator contract.")
    args = Namespace(round=1, output=tmp_path / "output", contract=contract, corpus=corpus,
                     documents=10, seed=7)
    directory = runner.prepare(args)
    return args, directory


def test_prepare_no_calls_blinded_exports_and_frozen_snapshot(prepared):
    args, directory = prepared
    assert runner.read_json(directory / "call_ledger.json") == []
    sources = runner.read_csv(directory / "sources_only.csv")
    assert len(sources) == 10
    assert not any("decider" in field or "score" in field for field in sources[0])
    assert len(runner.read_csv(directory / "sources_and_decisions.csv")) == 10
    assert runner.prepare(args) == directory
    prompt = directory / "prompts/generation/lookup/en.txt"
    prompt.write_text(prompt.read_text() + "\nChanged after freezing")
    with pytest.raises(ValueError, match="Frozen prompt changed"):
        runner.verify_snapshot(directory)


def test_five_round_limit_and_next_round_requires_actual_execution(prepared):
    args, _ = prepared
    with pytest.raises(ValueError, match="at most five rounds"):
        runner.prepare(Namespace(**(vars(args) | {"round": 6})))
    with pytest.raises(ValueError, match="Execute the preceding round"):
        runner.prepare(Namespace(**(vars(args) | {"round": 2})))


def test_partial_verifier_failure_preserves_candidates_without_inventing_scores(prepared):
    _, directory = prepared
    document = runner.read_json(directory / "sources.json")[0]
    eligibility = {"model": runner.decider.JEV_MODEL, "probabilities_yes": dict.fromkeys(runner.MODES, .8),
                   "selected_modes": list(runner.MODES), "threshold": .5}
    decision = runner.decider.choose(eligibility, runner.Counter(), runner.decider.resolve_weights(),
                                      seed=7, identity="fixture")
    for stage, result in [("decider", eligibility), ("routing", decision),
                          ("generation", [{"question": "Which compound?", "answer": "A"},
                                          {"question": "What material?", "answer": "B"}])]:
        runner.write_json(runner.stage_directory(directory, document, stage) / "state.json",
                          {"status": "complete", "result": result})
    runner.export(directory)
    rows = runner.read_csv(directory / "review_with_source.csv")
    assert len(rows) == 2
    assert all(row["total_score"] == "" for row in rows)
    assert runner.read_csv(directory / "best_per_document_with_source.csv") == []
    assert len(runner.read_csv(directory / "blinded_candidates.csv")) == 2
    assert len(runner.read_csv(directory / "sources_only.csv")) == 10


def test_offline_transport_recovery_uses_first_valid_response_and_keeps_history(prepared, monkeypatch):
    _, directory = prepared
    document = runner.read_json(directory / "sources.json")[0]
    eligibility = {"model": runner.decider.JEV_MODEL, "probabilities_yes": dict.fromkeys(runner.MODES, .8),
                   "selected_modes": list(runner.MODES), "threshold": .5}
    decision = runner.decider.choose(eligibility, runner.Counter(), runner.decider.resolve_weights(),
                                      seed=7, identity="fixture")
    mode, language = decision["mode"], document["language"]
    candidates = [{"question": "Which compound?", "answer": "A", "anchor": "compound",
                   "evidence": "A", "evidence_language": language, "answer_is_translation": False}]
    for stage, result in [("decider", eligibility), ("routing", decision), ("generation", candidates)]:
        runner.write_json(runner.stage_directory(directory, document, stage) / "state.json",
                          {"status": "complete", "result": result})
    runner.write_json(directory / "run_state.json", {"status": "complete"})
    prompt = (directory / "prompts/verifiers/faithfulness_batch.txt").read_text().strip()
    config = runner.GraderConfig(model=runner.MODEL_CONFIG["verifier_model"],
                                  reasoning_effort=runner.MODEL_CONFIG["verifier_reasoning_effort"],
                                  use_thinking=False)
    verifier_candidates = [dict(candidates[0], mode=mode, question_language=language, candidate_id="s001c1")]
    path = runner.stage_directory(directory, document, "faithfulness")
    parsed = []
    for attempt, score in [(1, 3), (2, 4)]:
        content = runner.json.dumps([{"index": 0, "grounding": score, "precision": score,
                                     "numerical_fidelity": score, "reason": "Fixture evidence."}])
        raw = {"service_tier": "provisioned", "choices": [{"message": {"content": content}}]}
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=lambda saved=raw, **_: SimpleNamespace(model_dump=lambda: saved))))
        recorder = runner.CallRecorder(path / f"attempt_{attempt:02d}", client)
        parsed.append(runner.grade_faithfulness(recorder, config, prompt, runner.source_packet(document),
                                                verifier_candidates, strict=True))
    original_failure = {"status": "error", "attempt": 1, "error_type": "ValidationError",
                        "error": "1 validation error for ChatCompletion\nservice_tier\ninput_value='provisioned'"}
    runner.write_json(path / "attempt_01/validation.json", original_failure)
    later_success = {"status": "complete", "attempt": 2, "result": parsed[1]}
    runner.write_json(path / "attempt_02/validation.json", later_success)
    runner.write_json(path / "state.json", later_success)
    calls_before = {p: p.read_bytes() for p in path.glob("attempt_*/call_*.json")}
    monkeypatch.setattr(runner.llm, "decisions", lambda *_: pytest.fail("Recovery called a provider"))
    report = runner.recover_transport(directory)
    assert report["paid_calls"] == 0
    assert report["records"][0]["chosen_attempt"] == 1
    assert runner.stage_result(directory, document, "faithfulness") == parsed[0]
    assert runner.read_json(path / "recovery/content_view_v1/prior_state.json") == later_success
    assert runner.read_json(path / "attempt_01/validation.json") == original_failure
    assert {p: p.read_bytes() for p in path.glob("attempt_*/call_*.json")} == calls_before
    assert runner.recover_transport(directory) == report
