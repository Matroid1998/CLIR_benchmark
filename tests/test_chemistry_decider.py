"""Offline chemistry eligibility transport, routing and CLI integration."""

from __future__ import annotations

import json
from collections import Counter
from types import SimpleNamespace

import pytest

from clir_bench import domains
from clir_bench.cli import build_parser
from clir_bench.cli import qac as cli
from clir_bench.core import corpus, grading, llm, qagen
from clir_bench.core.config import LLMSettings, Settings
from clir_bench.core.context import AppContext
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.chemistry.domain import SPEC
from clir_bench.domains.chemistry.qac import decider
from clir_bench.domains.chemistry.qac.plans import PLANS
from clir_bench.domains.chemistry.vocabulary import MODES


def response(eligible=MODES):
    return {"model": "jev-test", "answers": {
        mode: {"type": "noul", "noul": float(mode in eligible)} for mode in MODES
    }}


@pytest.fixture
def context(tmp_path):
    return AppContext.build(Settings(
        project_root=tmp_path, data_dir=tmp_path / "data", reports_dir=tmp_path / "reports",
        cluster_dir=tmp_path / "cluster", llm=LLMSettings(retries=1),
    ), SPEC)


def source_rows(family="EP-1234567-A1"):
    return [{"publication_number": family, "language": language, "doc_id": f"{family}_{language}",
             "context": text, "question": "OLD QUESTION MUST NOT REACH JEV", "total_score": "40"}
            for language, text in (("en", "Title: Catalyst\n\nAbstract: The catalyst is a zeolite."),
                                   ("de", "Title: Katalysator\n\nAbstract: Der Katalysator ist ein Zeolith."))]


def test_packaged_native_request_keeps_all_seven_independent_questions():
    template = json.loads(decider.eligibility_prompt_text())
    text = "[DE] Original passage with publication_number: EP-1234567-A1"
    request = decider.build_eligibility_request(text)
    assert request == dict(template, model=decider.JEV_MODEL, state=text)
    assert set(request["questions"]) == set(MODES)
    assert all(question["type"] == "noul" for question in request["questions"].values())
    assert decider.eligibility_policy() == {"probability_threshold": 0.5}
    result = decider.parse_eligibility(response())
    assert result["selected_modes"] == list(MODES)
    assert sum(result["probabilities_yes"].values()) == 7  # Not a choice distribution.
    assert decider.parse_eligibility(response([]))["selected_modes"] == []


def test_local_cutoff_is_not_sent_to_jev(monkeypatch):
    template = json.loads(decider.eligibility_prompt_text())
    template["routing_policy"] = {"probability_threshold": 0.6, "best_score_cutoff": 31}
    monkeypatch.setattr(decider, "eligibility_prompt_text", lambda: json.dumps(template))

    def call(request):
        assert set(request) == {"model", "state", "questions"}
        assert request["state"] == "Exact source"
        result = response([])
        result["answers"]["lookup"]["noul"] = 0.59
        result["answers"]["conceptual"]["noul"] = 0.6
        return result

    monkeypatch.setattr(llm, "decisions", call)
    assert decider.decide_eligibility("Exact source")["selected_modes"] == ["conceptual"]
    assert decider.decide_eligibility("Exact source", threshold=0.5)["selected_modes"] == [
        "lookup", "conceptual",
    ]


@pytest.mark.parametrize("value", [True, "0.5", None, -0.1, 1.1, float("nan"), float("inf")])
def test_invalid_probabilities_are_not_coerced(value):
    data = response()
    data["answers"]["lookup"]["noul"] = value
    with pytest.raises(ValueError, match="probability"):
        decider.parse_eligibility(data)


@pytest.mark.parametrize("mutation", [
    lambda data: data["answers"].pop("lookup"),
    lambda data: data["answers"].update(unexpected={"type": "noul", "noul": 1}),
    lambda data: data["answers"]["lookup"].update(type="choice"),
])
def test_missing_extra_or_wrong_type_answers_are_rejected(mutation):
    data = response()
    mutation(data)
    with pytest.raises(ValueError):
        decider.parse_eligibility(data)


def test_bad_provider_output_retries_without_falling_back_to_lookup(monkeypatch):
    replies = iter([{}, response(["comparison"])])
    monkeypatch.setattr(llm, "decisions", lambda request: next(replies))
    monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
    assert decider.decide_eligibility("source", retries=2)["selected_modes"] == ["comparison"]
    monkeypatch.setattr(llm, "decisions", lambda request: {})
    with pytest.raises(RuntimeError, match="eligibility failed"):
        decider.decide_eligibility("source", retries=1)


def test_assignment_balances_only_eligible_personas_and_counts_assignments():
    counts = Counter()
    weights = decider.resolve_weights()
    for index in range(70):
        choice = decider.choose(decider.parse_eligibility(response()), counts, weights,
                                seed=42, identity=str(index))
        counts[choice["mode"]] += 1
    assert counts == dict.fromkeys(MODES, 10)
    counts["lookup"] = 1000
    choice = decider.choose(decider.parse_eligibility(response(["lookup"])), counts, weights,
                            seed=42, identity="constrained")
    assert choice["mode"] == "lookup"  # Never reject the sole Yes to enforce a quota.
    assert decider.choose(decider.parse_eligibility(response([])), counts, weights,
                          seed=42, identity="empty")["mode"] == "skip"


@pytest.mark.parametrize("configured", [[], {"unknown": 1}, {"lookup": 0}, {"lookup": True},
                                        {"lookup": float("inf")}, {"lookup": "5"}])
def test_invalid_weights_fail(configured):
    with pytest.raises(ValueError):
        decider.resolve_weights(configured)


@pytest.mark.parametrize("name", PLANS)
def test_automatic_plans_count_targets_without_seven_mode_expansion(context, name):
    grouped = {f"EP-{index}-A1": source_rows(f"EP-{index}-A1") for index in range(20)}
    args = SimpleNamespace(seed=42, questions=10, pool=None, modes=None, langs=["en", "de"],
                           decider_model="jev")
    plan = PLANS[name](context=context, source=SPEC.source("gp"), grouped=grouped, args=args)
    assert len(plan) <= 10
    assert len({(item.family, item.language) for item in plan}) == len(plan)
    args.modes = ["lookup"]
    with pytest.raises(ValueError, match="cannot be combined"):
        PLANS[name](context=context, source=SPEC.source("gp"), grouped=grouped, args=args)


def test_route_screens_patents_once_and_is_independent_of_completion_order(context, tmp_path, monkeypatch):
    grouped = {family: source_rows(family) for family in ("EP-1-A1", "EP-2-A1")}
    plan = [qagen.PlanItem(family, language) for family in grouped for language in ("en", "de")]
    plan.append(plan[0])
    args = SimpleNamespace(decider_model="jev", modes=None, workers=2, seed=42, append=False)
    seen = []

    def call(request):
        seen.append(request["state"])
        assert "[EN]" in request["state"] and "[DE]" in request["state"]
        assert "publication_number:" in request["state"]
        assert "OLD QUESTION" not in request["state"] and "total_score" not in request["state"]
        return response()

    monkeypatch.setattr(llm, "decisions", call)
    kwargs = {"context": context, "source": SPEC.source("gp"), "args": args, "grouped": grouped,
              "plan": plan, "output": tmp_path / "qac.csv"}
    routed = decider.route_plan(**kwargs)
    assert len(seen) == 2 and len(routed) == 4
    monkeypatch.setattr(decider, "run_tasks", lambda items, fn, **kwargs: map(fn, reversed(items)))
    assert decider.route_plan(**kwargs) == routed
    audit = json.loads((tmp_path / "qac_eligibility.json").read_text())
    assert len(audit["runs"][0]["assignments"]) == 4
    assert len(audit["runs"][0]["eligibility"]) == 2
    args.append = True
    decider.route_plan(**kwargs)
    assert len(json.loads((tmp_path / "qac_eligibility.json").read_text())["runs"]) == 2


@pytest.mark.parametrize("source", ["gp", "epo"])
@pytest.mark.parametrize("outcome", ["lookup", "skip", "dry_run", "invalid"])
def test_cli_decider_controls_generation_and_preserves_audit(
    context, tmp_path, monkeypatch, source, outcome,
):
    rows = source_rows()
    corpus.write_rows(context.workspace.corpus_csv(source), rows, tuple(rows[0]))
    parser = build_parser(context, domains.load_module("chemistry"))
    output = tmp_path / f"{source}.csv"
    if outcome == "skip":
        output.write_text("stale\nprevious run\n")
    options = ["qac", "generate", "--source", source, "--decider-model", "jev",
               "--questions", "1", "--langs", "en", "--output", str(output)]
    if outcome == "dry_run":
        options.append("--dry-run")
    args = parser.parse_args(options)
    calls = []

    def decide(request):
        calls.append("eligibility")
        assert outcome != "dry_run"
        if outcome == "invalid":
            return {}
        return response(["lookup"] if outcome == "lookup" else [])

    monkeypatch.setattr(llm, "decisions", decide)

    def client(model):
        assert outcome == "lookup", "No generation clients needed for skipped or invalid inputs"

    monkeypatch.setattr(cli, "client_for", client)
    candidate = {
        "question": "Which catalyst is used?", "answer": "a zeolite", "anchor": "catalyst",
        "evidence": "a zeolite", "evidence_language": "en", "answer_is_translation": False,
        "question_type": "material_or_composition",
    }

    def generate(client, model, messages, **kwargs):
        assert messages[0]["content"] == PromptPack(SPEC.prompts_package).generation("lookup", "en")
        calls.append("generate")
        return json.dumps([candidate])

    def grade(client, config, prompt, text):
        payload = json.loads(text)
        assert payload["candidates"] == [
            dict(candidate, mode="lookup", question_language="en"),
        ]
        assert f"publication_number: {rows[0]['publication_number']}" in payload["passages"]
        assert "decider_model" not in text and "probabilities_yes" not in text
        if prompt == PromptPack(SPEC.prompts_package).faithfulness():
            return json.dumps([
                dict.fromkeys(grading.FAITHFULNESS_KEYS, 4) | {"index": 0, "reason": "Supported"},
            ])
        keys = grading.rubric_keys(prompt)
        return json.dumps({
            "candidates": [{
                "index": 0, "candidate_id": None, "scores": dict.fromkeys(keys, 4),
                "score_notes": {key: f"Supported {key}" for key in keys},
                "checks": dict.fromkeys(("mode", "support", "metadata"), "pass"),
                "problems": [],
            }],
            "batch_diversity": "not_applicable",
        })

    monkeypatch.setattr(qagen, "chat", generate)
    monkeypatch.setattr(grading, "_invoke", grade)
    if outcome == "invalid":
        with pytest.raises(RuntimeError, match="eligibility failed"):
            args.handler(args, context)
        assert calls == ["eligibility"]
        return
    assert args.handler(args, context) == 0
    audit_path = output.with_name(f"{source}_eligibility.json")
    if outcome == "dry_run":
        assert calls == [] and not audit_path.exists() and not output.exists()
        return
    audit = json.loads(audit_path.read_text())["runs"][0]
    assert audit["assignments"][0]["mode"] == outcome
    if outcome == "skip":
        assert calls == ["eligibility"]
        assert corpus.read_rows(output) == []
        assert corpus.read_rows(output.with_name(f"{source}_best.csv")) == []
        return
    assert calls == ["eligibility", "generate"]
    saved = corpus.read_rows(output)[0]
    assert saved["mode"] == saved["decider_mode"] == "lookup"
    assert saved["decider_model"] == decider.JEV_MODEL
    assert saved["decider_prompt_sha256"] == audit["prompt_sha256"]
    assert json.loads(saved["decider_eligible_modes_json"]) == ["lookup"]
    assert saved["total_score"] == "32"
    assert saved["quality_rubric_version"] == "chemistry-clir-exceptional-r1"
    assert saved["quality_audit_status"] == "clear"
    regraded = tmp_path / "regraded.csv"
    args = parser.parse_args(["qac", "regrade", "--source", source, "--input", str(output),
                              "--output", str(regraded)])
    assert args.handler(args, context) == 0
    assert all(corpus.read_rows(regraded)[0][key] == saved[key] for key in qagen.DECIDER_FIELDS)
