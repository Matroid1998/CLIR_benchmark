"""The calibrated policy affects routing without leaking into native Jev input."""
import json

import pytest

from clir_bench.core import llm
from clir_bench.domains.legal.qac import decider


def template(policy):
    result = {"model": "jev-latest", "state": "placeholder", "questions": {
        mode: {"type": "noul", "instructions": "Assess source quality",
               "criteria": {"true": "Strong", "false": "Weak"}}
        for mode in decider.MODES["un"]}}
    if policy is not None:
        result["routing_policy"] = policy
    return json.dumps(result)


def test_policy_sets_default_but_is_omitted_from_native_request(monkeypatch):
    policy = {"probability_threshold": 0.63, "best_score_cutoff": 31}
    monkeypatch.setattr(decider, "eligibility_prompt_text", lambda source: template(policy))
    calls = []

    def call(request):
        calls.append(request)
        assert set(request) == {"model", "state", "questions"}
        assert request["state"] == "Exact source"
        return {"answers": {mode: {"type": "noul", "noul": probability}
                            for mode, probability in zip(decider.MODES["un"],
                                                         [0.62, 0.63, 0.64, 0.1, 0.7, 0.2])}}

    monkeypatch.setattr(llm, "decisions", call)
    result = decider.decide_eligibility("un", "Exact source")
    assert result["threshold"] == 0.63
    assert result["selected_modes"] == ["practitioner", "conceptual", "claim_verification"]
    assert len(calls) == 1
    overridden = decider.decide_eligibility("un", "Exact source", threshold=0.5)
    assert overridden["threshold"] == 0.5
    assert "lookup" in overridden["selected_modes"]


def test_historical_prompt_retains_half_default(monkeypatch):
    monkeypatch.setattr(decider, "eligibility_prompt_text", lambda source: template(None))
    assert decider.eligibility_policy("un") == {"probability_threshold": 0.5}


@pytest.mark.parametrize("policy", [[], {}, {"probability_threshold": True},
                                    {"probability_threshold": -0.1},
                                    {"probability_threshold": 0.5, "best_score_cutoff": True},
                                    {"probability_threshold": 0.5, "best_score_cutoff": 41},
                                    {"probability_threshold": 0.5, "best_score_cutoff": float("nan")}])
def test_invalid_policy_stops_before_provider_call(monkeypatch, policy):
    monkeypatch.setattr(decider, "eligibility_prompt_text", lambda source: template(policy))
    monkeypatch.setattr(llm, "decisions", lambda request: pytest.fail("Invalid policy made a call"))
    with pytest.raises(ValueError):
        decider.decide_eligibility("un", "source")
