"""Choose a legal generation mode before generating or grading candidates."""

from __future__ import annotations

import json
import math

from clir_bench.core import llm
from clir_bench.core.prompts import load_prompt

JEV_MODEL = "~typesafe/jev-latest"
MODES = {
    "eurlex": ("fact_pattern", "lookup", "conceptual",
               "comparison", "claim_verification", "source_finding"),
    "un": ("lookup", "practitioner", "conceptual",
           "comparison", "claim_verification", "source_finding"),
}


def prompt_text(source: str, backend: str) -> str:
    if source not in MODES or backend not in ("generator", "jev"):
        raise ValueError(f"unsupported decider: {source}/{backend}")
    name = "jev.json" if backend == "jev" else "generator.txt"
    return load_prompt(f"clir_bench.domains.legal.qac.prompts_{source}", "decider", name)


def prompt_modes(source: str) -> tuple[str, ...]:
    """Use the pinned bundle's mode vocabulary when replaying older prompts."""
    criteria = json.loads(prompt_text(source, "jev"))["questions"]["mode"]["criteria"]
    return tuple(mode for mode in criteria if mode != "skip")


def generation_mode(mode: str) -> str:
    return "practitioners" if mode == "practitioner" else mode


def eligibility_prompt_text(source: str) -> str:
    """Independent quality prediction, separate from the historical single winner."""
    if source not in MODES:
        raise ValueError(f"unsupported eligibility source: {source}")
    return load_prompt(f"clir_bench.domains.legal.qac.prompts_{source}",
                       "decider", "jev_eligibility.json")


def build_eligibility_request(source: str, text: str) -> dict:
    request = json.loads(eligibility_prompt_text(source))
    # Local routing policy is pinned with the prompt, but is not Decisions API input.
    request.pop("routing_policy", None)
    questions = request.get("questions")
    if (not isinstance(questions, dict) or set(questions) != set(MODES[source])
            or any(not isinstance(q, dict) or q.get("type") != "noul"
                   for q in questions.values())):
        raise ValueError("Eligibility prompt must ask one noul question per mode")
    return dict(request, model=JEV_MODEL, state=text)


def eligibility_policy(source: str) -> dict:
    """Read a calibrated local cutoff; historical prompts retain their 0.5 default."""
    prompt = json.loads(eligibility_prompt_text(source))
    policy = prompt.get("routing_policy", {"probability_threshold": 0.5})
    if not isinstance(policy, dict) or "probability_threshold" not in policy:
        raise ValueError("Eligibility routing policy must declare probability_threshold")
    _probability(policy["probability_threshold"])
    cutoff = policy.get("best_score_cutoff")
    if cutoff is not None and (isinstance(cutoff, bool) or not isinstance(cutoff, (int, float))
                               or not math.isfinite(cutoff) or not 0 <= cutoff <= 40):
        raise ValueError("Eligibility score cutoff must be finite and in [0,40]")
    return policy


def parse_eligibility(data, source: str, *, threshold: float = 0.5) -> dict:
    """Validate independent probabilities; they are not normalized across modes."""
    _probability(threshold)
    answers = data.get("answers") if isinstance(data, dict) else None
    if not isinstance(answers, dict) or set(answers) != set(MODES[source]):
        raise ValueError("Jev eligibility answers must cover exactly the six modes")
    probabilities = {}
    for mode in MODES[source]:
        answer = answers[mode]
        if not isinstance(answer, dict) or answer.get("type") != "noul":
            raise ValueError(f"Jev eligibility answer for {mode} must have type noul")
        probabilities[mode] = _probability(answer.get("noul"))
    return {"probabilities_yes": probabilities, "threshold": threshold,
            "selected_modes": [mode for mode, p in probabilities.items() if p >= threshold],
            "model": JEV_MODEL, "response_model": data.get("model"),
            "backend": "jev_eligibility"}


def decide_eligibility(source: str, text: str, *, threshold: float | None = None,
                       checkpoint=None, retries: int = 3) -> dict:
    if threshold is None:
        threshold = eligibility_policy(source)["probability_threshold"]
    _probability(threshold)
    request = build_eligibility_request(source, text)

    def call():
        data = checkpoint.decisions(request) if checkpoint else llm.decisions(request)
        return parse_eligibility(data, source, threshold=threshold)

    return (checkpoint.run("eligibility", call) if checkpoint else
            llm.call_with_retries(call, retries=retries, label="eligibility"))


def build_request(source: str, backend: str, text: str, model: str) -> dict:
    prompt = prompt_text(source, backend)
    if backend == "jev":
        request = json.loads(prompt)
        request.update(model=JEV_MODEL, state=text)
        return request
    return {"model": model, "messages": [
        {"role": "system", "content": prompt}, {"role": "user", "content": text}]}


def _probability(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not 0 <= value <= 1):
        raise ValueError("decider probability/confidence must be finite and in [0, 1]")
    return value


def parse_decision(data, source: str, backend: str, *, symbol: str = "") -> dict:
    allowed = {*MODES[source], "skip"}
    previous_allowed = allowed - {"comparison", "claim_verification", "source_finding"}
    legacy_allowed = (previous_allowed - {"conceptual"} | {"semantic"} if source == "un"
                      else previous_allowed - {"conceptual"})
    if not isinstance(data, dict):
        raise ValueError("decider must return an object")  # noqa: TRY004 - invalid model output
    if backend == "jev":
        answers = data.get("answers")
        answer = answers.get("mode") if isinstance(answers, dict) else None
        if not isinstance(answer, dict) or answer.get("type") != "choice":
            raise ValueError("Jev response is missing answers.mode of type choice")
        mode, reason = answer.get("choice"), ""
        confidence = answer.get("confidence")
        probabilities = answer.get("probabilities")
        if confidence is not None:
            _probability(confidence)
        if probabilities is not None:
            if (not isinstance(probabilities, dict) or
                    set(probabilities) not in (allowed, previous_allowed, legacy_allowed)):
                raise ValueError("Jev probabilities must cover exactly the allowed modes")
            if not isinstance(mode, str) or mode not in probabilities:
                raise ValueError("Jev selected mode is absent from its probabilities")
            values = [_probability(value) for value in probabilities.values()]
            if not math.isclose(sum(values), 1.0, abs_tol=0.02):
                raise ValueError("Jev probabilities must sum to one")
    else:
        mode, reason = data.get("mode"), data.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("decider must provide a nonempty reason")
        reason = reason.strip()
        confidence = probabilities = None
    if not isinstance(mode, str) or mode not in (allowed | ({"semantic"} if source == "un" else set())):
        raise ValueError(f"unsupported {source} decider mode: {mode!r}")
    return {"mode": mode, "generation_mode": generation_mode(mode), "reason": reason,
            "confidence": confidence, "probabilities": probabilities}


def decide(source: str, payload, *, backend: str, model: str, checkpoint=None,
           retries: int = 3) -> dict:
    """Resume a validated decision; malformed output never selects a default mode."""
    request = build_request(source, backend, payload.text, model)

    def call():
        if backend == "jev":
            data = (checkpoint.decisions(request) if checkpoint else llm.decisions(request))
        else:
            client = llm.client_for(model)
            if checkpoint:
                client = checkpoint.client("decider", model, client)
            data = llm.parse_json_response(llm.chat(
                client, **request, reasoning_effort="medium"))
        result = parse_decision(data, source, backend,
                                symbol=getattr(payload.target, "symbol", ""))
        result.update(model=request["model"], backend=backend)
        return result

    return (checkpoint.run("decider", call) if checkpoint else
            llm.call_with_retries(call, retries=retries, label="decider"))


def row_metadata(decision: dict) -> dict:
    result = {"decider_model": decision["model"], "decider_mode": decision["mode"],
            "decider_reason": decision["reason"],
            "decider_confidence": decision["confidence"],
            "decider_probabilities_json": (json.dumps(decision["probabilities"], sort_keys=True)
                                           if decision["probabilities"] is not None else "")}
    if decision.get("selection_policy"):
        result.update(decider_selection_policy=decision["selection_policy"],
                      decider_routing_task=decision["routing_task"],
                      decider_threshold=decision["threshold"])
        for key in ("probabilities_yes", "eligible_modes", "persona_weights", "counts_before"):
            result[f"decider_{key}_json"] = json.dumps(decision[key], sort_keys=True)
    return result
