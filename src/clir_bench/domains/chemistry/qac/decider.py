"""Independent Jev eligibility checks and deterministic chemistry persona routing."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from dataclasses import replace
from pathlib import Path
from tempfile import NamedTemporaryFile

from clir_bench.core import corpus, llm
from clir_bench.core.parallel import run_tasks
from clir_bench.core.prompts import load_prompt
from clir_bench.core.qagen import select_plan_rows
from clir_bench.domains.chemistry.vocabulary import MODES

JEV_MODEL = "~typesafe/jev-latest"
POLICY = "weighted_eligibility_v1"
DEFAULT_WEIGHTS = dict.fromkeys(MODES, 1)


def _eligibility_case_state(packet: dict) -> str:
    """Render one bounded teaching packet in the same form used by runtime input."""
    if not isinstance(packet, dict):
        raise TypeError("Eligibility teaching cases must contain a source_packet object")
    lines = ["TARGET PATENT PACKET (teaching example)"]
    publication_number = packet.get("publication_number")
    if publication_number:
        lines.append(f"publication_number: {publication_number}")
    title = packet.get("title")
    if title:
        lines.append(f"title: {title}")
    body_units = packet.get("body_units")
    if not isinstance(body_units, list) or not body_units:
        raise ValueError("Eligibility teaching cases must contain body_units")
    for unit in body_units:
        if not isinstance(unit, dict) or not all(
                isinstance(unit.get(key), str) and (key == "text" or unit[key])
                for key in ("unit_id", "language", "text")):
            raise ValueError("Eligibility teaching case body units need id, language and text")
        lines.extend(("", f"BODY UNIT {unit['unit_id']} [{unit['language']}]", unit["text"]))
    return "\n".join(lines)


def eligibility_prompt_text() -> str:
    """Return the effective Jev template with the companion example set merged in."""
    package = "clir_bench.domains.chemistry.qac.prompts"
    template = json.loads(load_prompt(package, "decider", "jev_eligibility.json"))
    cases = json.loads(load_prompt(package, "decider", "eligibility_cases.json"))
    if not isinstance(cases, list):
        raise TypeError("Chemistry eligibility cases must be a JSON list")
    questions = template.get("questions")
    if not isinstance(questions, dict) or set(questions) != set(MODES):
        raise ValueError("Eligibility prompt must define every chemistry persona")

    examples_by_mode = {mode: {} for mode in MODES}
    for case in cases:
        if not isinstance(case, dict) or case.get("mode") not in examples_by_mode:
            raise ValueError("Eligibility cases must name a known chemistry persona")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("Eligibility cases must have a nonempty case_id")
        example = {
            "case_id": case_id,
            "basis": case.get("kind"),
            "state": _eligibility_case_state(case.get("source_packet")),
            "expected_decision": case.get("expected_decision"),
            "why": case.get("why"),
        }
        if "witness" in case:
            example["attainable_witness"] = case["witness"]
        if "tempting_bad_attempt" in case:
            example["tempting_bad_attempt"] = case["tempting_bad_attempt"]
        mode_examples = examples_by_mode[case["mode"]]
        if case_id in mode_examples:
            raise ValueError(f"Duplicate chemistry eligibility case: {case_id}")
        mode_examples[case_id] = example

    for mode, question in questions.items():
        instructions = question.get("instructions")
        if not isinstance(instructions, dict) or not isinstance(instructions.get("examples"), list):
            raise TypeError(f"Eligibility instructions for {mode} must include examples")
        # The companion cases are canonical on duplicate IDs; any instruction-only
        # examples remain available, while case IDs are never sent twice.
        merged = {}
        for example in instructions["examples"]:
            if not isinstance(example, dict) or not isinstance(example.get("case_id"), str):
                raise TypeError(f"Eligibility prompt has an invalid example for {mode}")
            merged[example["case_id"]] = example
        merged.update(examples_by_mode[mode])
        instructions["examples"] = list(merged.values())
    return json.dumps(template, ensure_ascii=False, indent=2) + "\n"


def _probability(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not 0 <= value <= 1):
        raise ValueError("Eligibility probability must be finite and in [0, 1]")
    return value


def eligibility_policy() -> dict:
    """The prompt's local policy, with the same 0.5 fallback as legal eligibility."""
    template = json.loads(eligibility_prompt_text())
    policy = template.get("routing_policy", {"probability_threshold": 0.5})
    if not isinstance(policy, dict) or "probability_threshold" not in policy:
        raise ValueError("Eligibility routing policy must declare probability_threshold")
    _probability(policy["probability_threshold"])
    cutoff = policy.get("best_score_cutoff")
    if cutoff is not None and (isinstance(cutoff, bool) or not isinstance(cutoff, (int, float))
                               or not math.isfinite(cutoff) or not 0 <= cutoff <= 40):
        raise ValueError("Eligibility score cutoff must be finite and in [0, 40]")
    return policy


def build_eligibility_request(text: str) -> dict:
    request = json.loads(eligibility_prompt_text())
    # Local cutoff metadata is not part of the native Decisions API request.
    request.pop("routing_policy", None)
    questions = request.get("questions")
    if (not isinstance(questions, dict) or set(questions) != set(MODES)
            or any(not isinstance(question, dict) or question.get("type") != "noul"
                   for question in questions.values())):
        raise ValueError("Eligibility prompt must ask one noul question per chemistry persona")
    return dict(request, model=JEV_MODEL, state=text)


def parse_eligibility(data, *, threshold: float = 0.5) -> dict:
    """Independent Yes probabilities are not a normalized choice distribution."""
    _probability(threshold)
    answers = data.get("answers") if isinstance(data, dict) else None
    if not isinstance(answers, dict) or set(answers) != set(MODES):
        raise ValueError("Jev eligibility answers must cover exactly the seven chemistry personas")
    probabilities = {}
    for mode in MODES:
        answer = answers[mode]
        if not isinstance(answer, dict) or answer.get("type") != "noul":
            raise ValueError(f"Jev eligibility answer for {mode} must have type noul")
        probabilities[mode] = _probability(answer.get("noul"))
    return {
        "probabilities_yes": probabilities, "threshold": threshold,
        "selected_modes": [mode for mode, probability in probabilities.items()
                           if probability >= threshold],
        "model": JEV_MODEL, "response_model": data.get("model"),
        "backend": "jev_eligibility",
    }


def decide_eligibility(text: str, *, threshold: float | None = None, retries: int = 3) -> dict:
    if threshold is None:
        threshold = eligibility_policy()["probability_threshold"]
    _probability(threshold)
    request = build_eligibility_request(text)
    return llm.call_with_retries(
        lambda: parse_eligibility(llm.decisions(request), threshold=threshold),
        retries=retries, label="chemistry eligibility",
    )


def resolve_weights(configured=None) -> dict:
    if configured is not None and not isinstance(configured, dict):
        raise ValueError("persona_weights must be a table of positive weights")
    configured = configured or {}
    if set(configured) - set(MODES):
        raise ValueError(f"Unknown chemistry persona weights: {set(configured) - set(MODES)}")
    weights = DEFAULT_WEIGHTS | configured
    if any(isinstance(weight, bool) or not isinstance(weight, (int, float))
           or not math.isfinite(weight) or weight <= 0 for weight in weights.values()):
        raise ValueError("persona_weights must be finite and positive")
    if not math.isfinite(sum(weights.values())):
        raise ValueError("Sum of persona_weights must be finite")
    return weights


def choose(eligibility, counts, weights, *, seed, identity) -> dict:
    """Choose the eligible persona furthest below its requested share, as in legal."""
    eligible = eligibility["selected_modes"]
    before = {mode: counts[mode] for mode in MODES}
    total, weight_sum = sum(before.values()), sum(weights.values())

    def priority(mode):
        deficit = (total + 1) * weights[mode] - before[mode] * weight_sum
        tie = hashlib.sha256(json.dumps([seed, identity, mode]).encode()).hexdigest()
        return deficit, tie

    mode = max(eligible, key=priority) if eligible else "skip"
    return {
        **eligibility, "mode": mode, "selection_policy": POLICY,
        "reason": ("Eligible persona with greatest deficit relative to target mix."
                   if eligible else "No persona meets the eligibility threshold."),
        "confidence": eligibility["probabilities_yes"].get(mode),
        "eligible_modes": list(eligible), "persona_weights": dict(weights),
        "counts_before": before, "routing_task": identity,
    }


def row_metadata(decision, prompt_sha256) -> dict:
    result = {
        "decider_model": decision["model"], "decider_mode": decision["mode"],
        "decider_reason": decision["reason"], "decider_confidence": decision["confidence"],
        "decider_selection_policy": decision["selection_policy"],
        "decider_routing_task": decision["routing_task"],
        "decider_threshold": decision["threshold"], "decider_prompt_sha256": prompt_sha256,
    }
    for key in ("probabilities_yes", "eligible_modes", "persona_weights", "counts_before"):
        result[f"decider_{key}_json"] = json.dumps(decision[key], sort_keys=True)
    return result


def route_plan(*, context, source, args, grouped, plan, output):
    """Screen each selected document once and assign personas in sampled order.

    Explicit document selections use exactly the source row generation sees.
    Legacy plan items without a document identity retain their family packet.
    Provider or parsing failures propagate, never becoming a default persona.
    """
    if not getattr(args, "decider_model", None):
        return plan
    if args.decider_model != "jev" or getattr(args, "modes", None) is not None:
        raise ValueError("Chemistry supports --decider-model jev without --modes")
    weights = resolve_weights(context.setting("persona_weights"))
    policy = eligibility_policy()
    prompt = eligibility_prompt_text()
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    audit_path = Path(output).with_name(f"{Path(output).stem}_eligibility.json")
    audit = {"schema_version": 1, "runs": []}
    if args.append and audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if (not isinstance(audit, dict) or audit.get("schema_version") != 1
                or not isinstance(audit.get("runs"), list)):
            raise ValueError(f"Invalid eligibility audit: {audit_path}")

    unique = {}
    for item in plan:
        key = (item.document_id,) if item.document_id else (item.family, item.language)
        previous = unique.setdefault(key, item)
        if (previous.family, previous.language) != (item.family, item.language):
            raise ValueError(f"Conflicting chemistry source document selection: {item.document_id!r}")
    selected = {}
    for item in unique.values():
        key = item.document_id or item.family
        previous = selected.setdefault(key, item)
        if bool(previous.document_id) != bool(item.document_id):
            raise ValueError(f"Ambiguous chemistry screening identity: {key!r}")
    order = context.languages.priority or context.languages.working

    def assess(key):
        item = selected[key]
        rows = select_plan_rows(item, grouped.get(item.family, []), context.schema)
        text = corpus.build_passages_text(
            rows, context.schema, order=order, include_identifiers=True,
        )
        result = decide_eligibility(text, threshold=policy["probability_threshold"],
                                    retries=context.settings.llm.retries)
        return key, {**result, "source_sha256": hashlib.sha256(text.encode()).hexdigest()}

    eligibility = dict(run_tasks(list(selected), assess, workers=args.workers,
                                 description="eligibility"))
    counts = Counter()
    assignments, routed = [], []
    for item in unique.values():
        identity_parts = [source.name, item.family, item.language]
        if item.document_id:
            identity_parts.append(item.document_id)
        identity = json.dumps(identity_parts, ensure_ascii=False)
        decision = choose(eligibility[item.document_id or item.family], counts, weights,
                          seed=args.seed, identity=identity)
        assignments.append({"family": item.family, "language": item.language,
                            "document_id": item.document_id, **decision})
        if decision["mode"] != "skip":
            counts[decision["mode"]] += 1
            routed.append(replace(item, mode=decision["mode"],
                                  metadata={**item.metadata, **row_metadata(decision, digest)}))

    audit["runs"].append({
        "source": source.name, "seed": args.seed, "prompt": json.loads(prompt),
        "prompt_sha256": digest, "routing_policy": policy, "selection_policy": POLICY,
        "persona_weights": weights, "eligibility": eligibility, "assignments": assignments,
    })
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=audit_path.parent,
                            prefix=f".{audit_path.name}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
            handle.close()
            temporary.replace(audit_path)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"eligibility: {len(routed)} assigned, {len(unique) - len(routed)} skipped; "
          f"{len(selected)} documents screened -> {audit_path}")
    return routed
