"""Choose a legal generation mode before generating or grading candidates."""

from __future__ import annotations

import json
import math
import re
from importlib.resources import files

from clir_bench.core import llm

JEV_MODEL = "~typesafe/jev-latest"
MODES = {
    "eurlex": ("fact_pattern", "lookup"),
    "un": ("lookup", "practitioner", "semantic"),
}


def prompt_text(source: str, backend: str) -> str:
    if source not in MODES or backend not in ("generator", "jev"):
        raise ValueError(f"unsupported decider: {source}/{backend}")
    name = "jev.json" if backend == "jev" else "generator.txt"
    return files(f"clir_bench.domains.legal.qac.prompts_{source}").joinpath(
        "decider", name).read_text(encoding="utf-8")


def generation_mode(mode: str) -> str:
    return "practitioners" if mode == "practitioner" else mode


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
            if not isinstance(probabilities, dict) or set(probabilities) != allowed:
                raise ValueError("Jev probabilities must cover exactly the allowed modes")
            values = [_probability(value) for value in probabilities.values()]
            if not math.isclose(sum(values), 1.0, abs_tol=0.02):
                raise ValueError("Jev probabilities must sum to one")
    else:
        mode, reason = data.get("mode"), data.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("decider must provide a nonempty reason")
        reason = reason.strip()
        confidence = probabilities = None
    if not isinstance(mode, str) or mode not in allowed:
        raise ValueError(f"unsupported {source} decider mode: {mode!r}")
    if (source == "un" and mode not in ("semantic", "skip")
            and re.search(r"(?:^|/)\s*(?:PV|SR)(?:[./(\d]|$)", symbol.upper())):
        raise ValueError("UN meeting records permit only semantic or skip")
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
    return {"decider_model": decision["model"], "decider_mode": decision["mode"],
            "decider_reason": decision["reason"],
            "decider_confidence": decision["confidence"],
            "decider_probabilities_json": (json.dumps(decision["probabilities"], sort_keys=True)
                                           if decision["probabilities"] is not None else "")}
