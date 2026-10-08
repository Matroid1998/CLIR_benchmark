"""Offline decider routing, native Jev transport, and persisted run behavior."""

import json
import sqlite3
from dataclasses import asdict, replace
from types import SimpleNamespace

import pytest

from clir_bench.core import grading, llm
from clir_bench.domains.legal import qac
from clir_bench.domains.legal.qac import decider
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces, read_run_metadata
from test_domain_contract import _context
from test_legal_batch_replay_integration import Client, case, response


def jev_response(source, mode):
    return {"model": "typesafe/jev-snapshot", "id": "decision-id", "answers": {"mode": {
        "type": "choice", "choice": mode, "confidence": 0.95,
        "probabilities": {key: float(key == mode) for key in (*decider.MODES[source], "skip")},
    }}, "usage": {"input_tokens": 100, "output_tokens": 10, "cost": 0.001}}


@pytest.mark.parametrize("source", ["eurlex", "un"])
def test_jev_request_preserves_structured_guidance_and_complete_state(source):
    text = "### TARGET\nTexte français 中文\n### REFERENCES\nFull references"
    template = json.loads(decider.prompt_text(source, "jev"))
    request = decider.build_request(source, "jev", text, "gpt-test")
    assert request == dict(template, model="~typesafe/jev-latest", state=text)
    assert isinstance(request["questions"]["mode"]["instructions"], dict)
    assert set(request["questions"]["mode"]["criteria"]) == {*decider.MODES[source], "skip"}


@pytest.mark.parametrize("data", [[], {}, {"mode": "technical", "reason": "Wrong mode"},
                                  {"mode": "lookup", "reason": ""},
                                  {"mode": ["lookup"], "reason": "Bad type"}])
def test_invalid_chat_decisions_never_fall_back(data):
    with pytest.raises(ValueError):
        decider.parse_decision(data, "un", "generator")


@pytest.mark.parametrize("field,value", [
    ("type", "score"), ("choice", "technical"), ("confidence", float("nan")),
    ("confidence", 2), ("confidence", True), ("probabilities", {"lookup": 1}),
    ("probabilities", {"lookup": 1, "fact_pattern": 1, "skip": 1}),
])
def test_invalid_jev_decisions_are_rejected(field, value):
    data = jev_response("eurlex", "lookup")
    data["answers"]["mode"][field] = value
    with pytest.raises(ValueError):
        decider.parse_decision(data, "eurlex", "jev")


@pytest.mark.parametrize("symbol", ["S/PV.1234", "A/C.3/50/SR.3", "s/pv.1234"])
@pytest.mark.parametrize("backend", ["generator", "jev"])
@pytest.mark.parametrize("mode", ["lookup", "practitioner", "conceptual", "skip"])
def test_un_meeting_records_can_route_to_every_mode(symbol, backend, mode):
    data = (jev_response("un", mode) if backend == "jev" else
            {"mode": mode, "reason": "Supported by the target"})
    assert decider.parse_decision(data, "un", backend, symbol=symbol)["mode"] == mode


def test_jev_http_transport_uses_decisions_endpoint(monkeypatch):
    import requests
    calls = []
    expected = jev_response("un", "conceptual")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def raise_for_status(self):
            pass

        def json(self):
            return expected

    monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
    monkeypatch.setattr(requests, "post", lambda *a, **kw: (calls.append((a, kw)), Response())[1])
    request = decider.build_request("un", "jev", "all sections", "gpt-test")
    assert llm.decisions(request) == expected
    args, kwargs = calls[0]
    assert args == ("https://openrouter.ai/api/alpha/decisions",)
    assert kwargs["headers"] == {"Authorization": "Bearer local-test-key"}
    assert kwargs["json"] == request and kwargs["timeout"] == 180


@pytest.mark.parametrize("source", ["eurlex", "un"])
@pytest.mark.parametrize("backend", ["generator", "jev", "jev_legacy"])
@pytest.mark.parametrize("skip", [False, True])
def test_decider_routes_real_batch_and_survives_resume(tmp_path, monkeypatch, source, backend, skip):
    from clir_bench import domains
    from clir_bench.cli import build_parser

    batch, generator, target, payload, candidates = case(source)
    chosen = "skip" if skip else ("fact_pattern" if source == "eurlex" else "practitioner")
    routed = decider.generation_mode(chosen)
    model = "gpt-test"
    judge = "gpt-judge"
    weighted = backend == "jev"
    backend_name = "jev" if backend == "jev_legacy" else backend
    calls = []
    native_calls = []
    generation_calls = []
    original_generate = generator.generate

    def observe_generation(*args, **kwargs):
        generation_calls.append(kwargs)
        return original_generate(*args, **kwargs)

    monkeypatch.setattr(generator, "generate", observe_generation)
    monkeypatch.setattr(batch, "prepare_payload", lambda *a, **kw: payload)
    index = (SimpleNamespace(status={target.eli_id: {"complete": True}}) if source == "eurlex"
             else SimpleNamespace(incomplete={}))
    monkeypatch.setattr(qac, "_indexes", lambda *a, **kw: {source: index})

    def create(**kwargs):
        calls.append(kwargs)
        prompt = kwargs["messages"][0]["content"]
        if prompt == decider.prompt_text(source, "generator"):
            assert kwargs["model"] == model
            assert kwargs["messages"][1]["content"] == payload.text
            return response(json.dumps({"mode": chosen, "reason": "The target supports it."}))
        if prompt == generator.PROMPTS.generation(routed, target.language):
            assert kwargs["model"] == model
            return response(json.dumps(candidates))
        assert kwargs["model"] == judge
        if prompt == generator.PROMPTS.faithfulness("batch"):
            output = [dict(index=i, **dict.fromkeys(grading.FAITHFULNESS_KEYS, 5)) for i in range(2)]
        else:
            assert prompt == generator.PROMPTS.quality(routed, "batch")
            inputs = json.loads(kwargs["messages"][1]["content"])["candidates"]
            keys = grading.rubric_keys(prompt)
            output = {"candidates": [{"index": i, "candidate_id": c["candidate_id"],
                "scores": dict.fromkeys(keys, 4), "score_notes": dict.fromkeys(keys, "Supported"),
                "checks": dict.fromkeys(("mode", "support", "metadata"), "pass"), "problems": []}
                for i, c in enumerate(inputs)], "batch_diversity": "pass"}
        return response(json.dumps(output), model=kwargs["model"])

    monkeypatch.setattr(llm, "client_for", lambda _: Client(create))

    def native(request):
        native_calls.append(request)
        assert request["state"] == payload.text
        if weighted:
            assert set(request["questions"]) == set(decider.MODES[source])
            return {"answers": {mode: {"type": "noul", "noul": float(mode == chosen)}
                                for mode in decider.MODES[source]}}
        return jev_response(source, chosen)

    monkeypatch.setattr(llm, "decisions", native)
    context = _context(tmp_path, "legal")
    parser = build_parser(context, domains.load_module("legal"))
    argv = ["qac", "generate", "--source", source, "--decider-model", backend_name,
            "--generation-model", model, "--verifier-model", judge, "--langs", "en",
            "--run-dir", str(tmp_path / "run"), "--trace", "--retries", "1"]
    args = parser.parse_args(argv)
    # Two explicit-mode copies of the target must turn into one decision case.
    entries = [{"corpus": source, "target": asdict(t)} for t in
               (target, replace(target, mode="fact_pattern" if source == "eurlex" else "lookup"))]
    original_options = qac._options
    if backend == "jev_legacy":
        def historical_options(*a, **kw):
            options = original_options(*a, **kw)
            options.pop("persona_selection_policy", None)
            options.pop("persona_weights", None)
            return options
        monkeypatch.setattr(qac, "_options", historical_options)
    assert qac.generate(args, context, selections=entries) == 0
    monkeypatch.setattr(qac, "_options", original_options)
    rows, _ = qac._read_csv(tmp_path / "run" / "results.csv")
    assert len(rows) == (0 if skip else 2)
    assert len(native_calls) == (backend_name == "jev")
    assert len(calls) == (backend == "generator") + (0 if skip else 3)
    if not skip:
        assert len(generation_calls) == 1 and generation_calls[0]["mode"] == routed
        assert all(row["mode"] == routed and row["decider_mode"] == chosen for row in rows)
        assert all(row["quality_verifier_prompt"] == generator.PROMPTS.quality(routed, "batch")
                   for row in rows)
        assert sum(row["is_best"] == "True" for row in rows) == 1
    metadata = read_run_metadata(tmp_path / "run")
    assert len(metadata["targets"]) == 1
    assert metadata["targets"][0]["target"]["mode"] == "auto"
    trace = json.loads((tmp_path / "run" / "llm_calls.json").read_text())
    stages = {stage["stage"]: stage for stage in trace["stages"]}
    selection_stage = "persona_selection" if weighted else "decider"
    assert stages[selection_stage]["parsed_output"]["mode"] == chosen
    routing_stages = {"eligibility", "persona_selection"} if weighted else {"decider"}
    assert set(stages) == (routing_stages if skip else routing_stages | {"generation", "faithfulness", "quality"})
    if weighted:
        balance = metadata["summary"]["persona_balance"]
        assert balance["assigned"] == (0 if skip else 1)
        assert balance["no_eligible_persona"] == int(skip)
        if not skip:
            assert json.loads(rows[0]["decider_eligible_modes_json"]) == [chosen]
    previous = (len(calls), len(native_calls))
    assert qac.generate(parser.parse_args(argv + ["--resume"]), context) == 0
    assert (len(calls), len(native_calls)) == previous
    if not skip:
        regrade_args = parser.parse_args([
            "qac", "regrade", "--input", str(tmp_path / "run" / "results.csv"),
            "--run-dir", str(tmp_path / "regrade"), "--verifier-model", judge])
        assert qac.regrade(regrade_args, context) == 0
        regraded, _ = qac._read_csv(tmp_path / "regrade" / "results.csv")
        assert [row["decider_mode"] for row in regraded] == [chosen, chosen]
        assert len(generation_calls) == 1 and len(native_calls) == previous[1]


def test_jev_retry_resume_and_trace(tmp_path, monkeypatch):
    payload = SimpleNamespace(text="entire source", target=SimpleNamespace(symbol="S/RES/1"))
    calls = []

    def native(request):
        calls.append(request)
        return {"answers": {}} if len(calls) == 1 else jev_response("un", "conceptual")

    monkeypatch.setattr(llm, "decisions", native)
    with RunState(tmp_path / "run.sqlite") as state:
        decision = decider.decide("un", payload, backend="jev", model="gpt-test",
                                  checkpoint=state.checkpoint("task", retries=2))
    with RunState(tmp_path / "run.sqlite") as state:
        assert decider.decide("un", payload, backend="jev", model="gpt-test",
                              checkpoint=state.checkpoint("task", retries=2)) == decision
    assert len(calls) == 2
    export_traces(tmp_path)
    trace = json.loads((tmp_path / "llm_calls.json").read_text())
    assert len(trace["calls"]) == 2
    assert trace["calls"][-1]["record"]["request"]["state"] == payload.text
    assert trace["calls"][-1]["record"]["usage"]["provider_cost"] == 0.001
    assert trace["stages"][0]["attempts"] == 2
    assert "Decisions request" in (tmp_path / "trace.md").read_text()


def test_failed_decider_attempt_budget_survives_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "decisions", lambda _: {"answers": {}})
    payload = SimpleNamespace(text="source", target=SimpleNamespace(symbol=""))
    for _ in range(2):
        with (RunState(tmp_path / "run.sqlite") as state,
              pytest.raises(RuntimeError, match="failed after 1 attempts")):
            decider.decide("eurlex", payload, backend="jev", model="gpt-test",
                           checkpoint=state.checkpoint("task", retries=1))
    with sqlite3.connect(tmp_path / "run.sqlite") as db:
        assert db.execute("SELECT COUNT(*) FROM requests").fetchone()[0] == 1
        assert db.execute("SELECT status FROM stages").fetchone()[0] == "failed"


@pytest.mark.parametrize("extra", [{"modes": ["lookup"]}, {"questions_per_mode": 3}])
def test_decider_rejects_conflicting_mode_controls(tmp_path, extra):
    with pytest.raises(ValueError, match="cannot be combined"):
        qac._options(SimpleNamespace(decider_model="jev", **extra), _context(tmp_path, "legal"))


@pytest.mark.parametrize("backend", ["generator", "jev"])
def test_historical_semantic_decisions_keep_their_recorded_label(backend):
    data = {"mode": "semantic", "reason": "Historical decision"}
    if backend == "jev":
        data = {"answers": {"mode": {"type": "choice", "choice": "semantic",
                "probabilities": {"lookup": 0, "practitioner": 0, "semantic": 1, "skip": 0}}}}
    result = decider.parse_decision(data, "un", backend)
    assert result["mode"] == result["generation_mode"] == "semantic"


def test_historical_eurlex_probability_vocabulary_remains_supported():
    data = {"answers": {"mode": {"type": "choice", "choice": "lookup",
            "probabilities": {"fact_pattern": 0.1, "lookup": 0.8, "skip": 0.1}}}}
    assert decider.parse_decision(data, "eurlex", "jev")["mode"] == "lookup"
    data["answers"]["mode"]["choice"] = "conceptual"
    with pytest.raises(ValueError, match="absent from its probabilities"):
        decider.parse_decision(data, "eurlex", "jev")
