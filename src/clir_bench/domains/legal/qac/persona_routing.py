"""Reproducible, shared persona assignments from independent eligibility checks."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict

from . import decider

POLICY = "weighted_eligibility_v1"
DEFAULT_WEIGHTS = {"lookup": 5, "conceptual": 5, "fact_pattern": 4, "practitioner": 4,
                   "source_finding": 4, "comparison": 3, "claim_verification": 3}


def resolve_weights(configured=None):
    if configured is not None and not isinstance(configured, dict):
        raise ValueError("persona_weights must be a table of positive weights")
    configured = configured or {}
    if set(configured) - set(DEFAULT_WEIGHTS):
        raise ValueError(f"unknown personas in persona_weights: {set(configured) - set(DEFAULT_WEIGHTS)}")
    weights = DEFAULT_WEIGHTS | configured
    if any(isinstance(w, bool) or not isinstance(w, (int, float))
           or not math.isfinite(w) or w <= 0 for w in weights.values()):
        raise ValueError("persona_weights must be finite and positive")
    if not math.isfinite(sum(weights.values())):
        raise ValueError("sum of persona_weights must be finite")
    return weights


def task_id(entry):
    target = entry["target"]
    identity = [entry["corpus"], target.get("eli_id") or target["block_id"], target["language"]]
    return "persona/" + hashlib.sha256(json.dumps(identity).encode()).hexdigest()


def require_safe_targets(selections, indexes):
    """Use the same authoritative completeness indexes as the safe samplers.

    Imported plans must pass this gate too; a saved 'complete' label alone is
    insufficient. UN status files list incomplete blocks, so an empty loaded
    mapping is valid, whereas a missing status file is not.
    """
    for entry in selections:
        source, target = entry["corpus"], entry["target"]
        index = indexes[source]
        if source == "eurlex":
            status = getattr(index, "status", None)
            safe = (status is not None
                    and status.get(target["eli_id"], {}).get("complete") is True
                    and target.get("complete", True) is True)
        else:
            incomplete = getattr(index, "incomplete", None)
            safe = (incomplete is not None and target["block_id"] not in incomplete
                    and target.get("reference_complete", True) is True
                    and target.get("n_unresolved", 0) == 0)
        if not safe:
            identity = target.get("eli_id") or target.get("block_id")
            raise ValueError(f"weighted persona routing requires verified reference-complete targets: "
                             f"{source}/{identity}; incomplete or missing reference status")


def choose(source, eligibility, counts, weights, *, seed, identity):
    weights = {mode: weights[mode] for mode in decider.MODES[source]}
    eligible = eligibility["selected_modes"]
    if set(eligible) - set(weights):
        raise ValueError("eligibility contains unsupported personas")
    before = {mode: counts[mode] for mode in weights}
    total, weight_sum = sum(before.values()), sum(weights.values())

    def priority(mode):
        # Scale the deficit by weight_sum, preserving the ranking and avoiding
        # rounding differences between equivalent integer-weight deficits.
        deficit = (total + 1) * weights[mode] - before[mode] * weight_sum
        tie = hashlib.sha256(json.dumps([seed, identity, mode]).encode()).hexdigest()
        return deficit, tie

    mode = max(eligible, key=priority) if eligible else "skip"
    return {"mode": mode, "generation_mode": decider.generation_mode(mode),
            "model": eligibility["model"], "response_model": eligibility.get("response_model"),
            "backend": "jev_eligibility", "selection_policy": POLICY,
            "reason": ("Eligible persona with greatest deficit relative to target mix."
                       if eligible else "No persona meets the eligibility threshold."),
            "confidence": eligibility["probabilities_yes"].get(mode), "probabilities": None,
            "probabilities_yes": eligibility["probabilities_yes"],
            "eligible_modes": list(eligible), "threshold": eligibility["threshold"],
            "persona_weights": weights, "counts_before": before, "routing_task": identity}


def route_targets(state, targets, *, weights, seed, retries, executor):
    """Yield one committed decision/error per target, in fixed sampled order.

    Eligibility calls run in parallel. Selections run serially and reuse their
    checkpoints, rebuilding counts exactly once, independently of model output.
    These shared tasks have stages only, never generation outcomes.
    """
    def assess(entry, payload):
        return decider.decide_eligibility(entry["corpus"], payload.text,
            checkpoint=state.checkpoint(task_id(entry), retries=retries))

    futures = [(entry, executor.submit(assess, entry, payload)) for entry, payload in targets]
    counts = defaultdict(Counter)
    for entry, future in futures:
        key, source = task_id(entry), entry["corpus"]
        try:
            eligibility = future.result()
        except InterruptedError:
            raise
        except Exception as exc:  # noqa: BLE001 - retain provider/parser failures, never pick a fallback
            yield key, None, str(exc)
            continue
        # The local choice has no provider attempt budget. Commit it atomically:
        # an interruption before commit must leave it safe to recompute.
        with state.transaction() as db:
            saved = db.execute("SELECT value FROM stages WHERE task=? AND stage='persona_selection' "
                               "AND status='completed'", (key,)).fetchone()
            if saved:
                decision = json.loads(saved[0])
            else:
                decision = choose(source, eligibility, counts[source], weights, seed=seed, identity=key)
                db.execute("INSERT OR REPLACE INTO stages VALUES (?,?,?,?,?,?)",
                           (key, "persona_selection", 0, "completed", json.dumps(decision), None))
        if decision["counts_before"] != {mode: counts[source][mode] for mode in decider.MODES[source]}:
            raise ValueError("persisted persona assignments disagree with sampled target order")
        if decision["mode"] != "skip":
            counts[source][decision["mode"]] += 1
        yield key, decision, None


def balance_summary(source, decisions, weights, *, failures=0):
    counts = Counter(d["mode"] for d in decisions)
    weights = {mode: weights[mode] for mode in decider.MODES[source]}
    total = sum(counts[mode] for mode in weights)
    weight_sum = sum(weights.values())
    return {"policy": POLICY, "unit": "target_language_assignment", "assigned": total,
            "no_eligible_persona": counts["skip"], "eligibility_failures": failures,
            "personas": {mode: {"weight": weight, "assigned": counts[mode],
                                 "target_share": weight / weight_sum,
                                 "actual_share": counts[mode] / total if total else 0}
                         for mode, weight in weights.items()}}
