"""Compare fixed-target legal prompt experiments; common blinded scores are primary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import random
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean

MODES = {"eurlex": ("fact_pattern", "lookup"),
         "un": ("lookup", "practitioner", "semantic")}
CRITERIA = ("grounding", "answer_resolution", "retrievability", "information_value", "clarity")
SCORE_FIELDS = ("legacy_best", "legacy_best_accepted", "common_best_any", "common_best_usable",
                "common_native_rank1", "common_native_rank1_usable")
REPLAY_SCORE_FIELDS = ("common_native_rank1", "common_native_rank1_usable",
                       "common_best_any", "common_best_usable")
ROUTER_VARIANTS = {"B": ("B", "B"), "C": ("C", "C"),
                   "b_instructions_c_criteria": ("B", "C"),
                   "c_instructions_b_criteria": ("C", "B")}
ACTIVE_KEYS = {f"{source}/{role}/{mode}" for source, modes in MODES.items()
               for role in ("generation", "quality") for mode in modes} | {
                   f"{source}/decider/{backend}" for source in MODES for backend in ("generator", "jev")
               } | {f"{source}/faithfulness" for source in MODES}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def number(value):
    return float(value) if value not in (None, "") else None


def average(values):
    values = [value for value in values if value is not None]
    return mean(values) if values else None


def truth(value):
    return str(value).lower() in ("true", "1")


def target_key(row):
    corpus = row.get("corpus") or ("eurlex" if row.get("celex_id") else "un")
    target = row.get("target_id") or row.get("target_article_id") or row.get("block_id")
    if corpus not in MODES or not target:
        raise ValueError("row lacks a supported corpus/target identity")
    return corpus, target


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def sqlite_metadata(directory):
    path = directory / "run.sqlite"
    if not path.exists():
        return {}
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        return {key: json.loads(value) for key, value in db.execute("SELECT key,value FROM metadata")}


def load_run(version, directory):
    selection = json.loads((directory / "selection.json").read_text())
    targets = {}
    for record in selection:
        key = target_key(record)
        if key in targets:
            raise ValueError(f"{version}: duplicate target {key}")
        actual_hash = hashlib.sha256(record["source_payload"].encode()).hexdigest()
        if actual_hash != record["source_payload_sha256"]:
            raise ValueError(f"{version}: source hash mismatch for {key}")
        targets[key] = record
    candidates = read_csv(directory / "all_mode_candidates.csv")
    identities = set()
    for row in candidates:
        key = target_key(row)
        identity = row["candidate_id"]
        if key not in targets or identity in identities:
            raise ValueError(f"{version}: unknown target or duplicate candidate {identity}")
        identities.add(identity)
        if (row.get("source_payload_sha256") and row["source_payload_sha256"]
                != targets[key]["source_payload_sha256"]):
            raise ValueError(f"{version}: candidate source hash mismatch for {identity}")
        row["corpus"], row["target_id"] = key
        row["screening_mode"] = row.get("screening_mode") or row["mode"]
        if row["screening_mode"] == "practitioners":
            row["screening_mode"] = "practitioner"
        if row["screening_mode"] not in MODES[key[0]]:
            raise ValueError(f"{version}: unknown screening mode")
    modes = {(target_key(r), r["mode"]): r for r in read_csv(directory / "mode_scores.csv")}
    decisions = {(target_key(r), r["backend"]): r for r in read_csv(directory / "decisions.csv")}
    metadata = sqlite_metadata(directory)
    config = json.loads((directory / "config.json").read_text())
    return {"version": version, "directory": directory, "selection": selection,
            "targets": targets, "candidates": candidates, "modes": modes,
            "decisions": decisions, "config": config, "metadata": metadata}


def check_pairing(runs):
    first = next(iter(runs.values()))
    expected = first["targets"]
    for version, run in runs.items():
        if run["targets"] != expected:
            raise ValueError(f"{version}: selections/source payloads differ; paired report refused")
    setting_differences = {key: {version: run["config"].get(key) for version, run in runs.items()}
                           for key in ("generator", "verifier", "keep", "language", "meeting_modes")
                           if len({json.dumps(run["config"].get(key)) for run in runs.values()}) > 1}
    return {"identical_selections": True, "verified_payload_hashes": True,
            "model_or_generation_setting_differences": setting_differences,
            "targets": len(expected), "selection_sha256": digest(first["selection"]),
            "corpus_counts": dict(Counter(key[0] for key in expected)),
            "strata": {corpus: dict(Counter(r.get("stratum", "unknown")
                                            for key, r in expected.items() if key[0] == corpus))
                       for corpus in MODES}}


def common_scores(path, runs):
    if path is None:
        return {}, {"available": False}
    rows = read_csv(path)
    candidates = {(version, r["candidate_id"]): r
                  for version, run in runs.items() for r in run["candidates"]}
    indexed, seen, blind_scores = {}, set(), {}
    for row in rows:
        if row["version"] not in runs:
            raise ValueError("common evaluation contains an unrequested version")
        key = row["version"], row["candidate_id"]
        if key not in candidates or key in seen:
            raise ValueError("common evaluation has unknown/duplicate candidate membership")
        seen.add(key)
        original = candidates[key]
        if (target_key(row) != target_key(original) or row["mode"] != original["screening_mode"]
                or row["question"] != original["question"] or row["answer"] != original["answer"]):
            raise ValueError("common evaluation candidate content/identity mismatch")
        if row.get("evaluation_status") != "completed":
            continue
        scores = {criterion: number(row.get(criterion)) for criterion in CRITERIA}
        if any(v is None or not 1 <= v <= 5 or not v.is_integer() for v in scores.values()):
            raise ValueError("common evaluation contains invalid criterion scores")
        total = sum(scores.values())
        usable = (scores["grounding"] >= 4 and scores["answer_resolution"] >= 4
                  and all(scores[key] >= 3 for key in ("retrievability", "information_value", "clarity")))
        if total != number(row.get("total")) or usable != truth(row.get("usable")):
            raise ValueError("common evaluation total/usability gate does not match its scores")
        if row["blind_id"] in blind_scores and blind_scores[row["blind_id"]] != scores:
            raise ValueError("identical blinded candidates received inconsistent exported scores")
        blind_scores[row["blind_id"]] = scores
        indexed[key] = row | scores | {"total": total, "usable": usable}
    return indexed, {"available": True, "path": str(path.resolve()),
                     "candidate_memberships": len(candidates), "rows_present": len(seen),
                     "completed_memberships": len(indexed),
                     "missing_memberships": len(candidates) - len(indexed),
                     "unique_graded_pairs": len({r["blind_id"] for r in indexed.values()}),
                     "config": (json.loads((path.parent / "config.json").read_text())
                                if (path.parent / "config.json").exists() else None),
                     "usability_gate": "grounding>=4, answer_resolution>=4, retrievability>=3, information_value>=3, clarity>=3"}


def per_target_modes(runs, common):
    result = []
    for version, run in runs.items():
        grouped = defaultdict(list)
        for candidate in run["candidates"]:
            grouped[target_key(candidate), candidate["screening_mode"]].append(candidate)
        for key, source in run["targets"].items():
            for mode in MODES[key[0]]:
                candidates = grouped[key, mode]
                original = run["modes"].get((key, mode), {})
                scored = [r for r in candidates if r.get("grading_status") == "completed"
                          and number(r.get("total_score")) is not None]
                accepted = [r for r in scored if r.get("quality_audit_status") in ("clear", "minor_issues")
                            and (key[0] != "un" or (number(r.get("faith_grounding")) or 0) >= 3)]
                evaluated = [common[version, r["candidate_id"]] for r in candidates
                             if (version, r["candidate_id"]) in common]
                usable = [r for r in evaluated if r["usable"]]
                rank_one = [r for r in candidates if number(r.get("candidate_rank")) == 1]
                if len(rank_one) > 1:
                    raise ValueError(f"{version}: duplicate candidate_rank=1 for {key}/{mode}")
                native = rank_one[0] if rank_one else None
                if native and (native.get("grading_status") != "completed"
                               or number(native.get("total_score")) is None):
                    raise ValueError(f"{version}: candidate_rank=1 lacks completed grades for {key}/{mode}")
                native_common = common.get((version, native["candidate_id"])) if native else None
                row = {"version": version, "corpus": key[0], "target_id": key[1],
                       "symbol": source.get("symbol", ""), "mode": mode,
                       "is_meeting": source.get("is_meeting", False),
                       "status": original.get("status", "missing"),
                       "generated_candidates": len(candidates), "graded_candidates": len(scored),
                       "accepted_candidates": len(accepted),
                       "audit_blocking_candidates": sum(r.get("quality_audit_status") == "blocking" for r in candidates),
                       "legacy_best": number(original.get("best_score")),
                       "legacy_best_accepted": max((number(r["total_score"]) for r in accepted), default=None),
                       "common_evaluated_candidates": len(evaluated),
                       "common_usable_candidates": len(usable),
                       "native_rank1_candidate_id": native["candidate_id"] if native else None,
                       "native_rank1_status": "rank1" if native else "unranked" if candidates else "no_candidates",
                       "common_native_rank1": native_common["total"] if native_common else None,
                       "common_native_rank1_usable": (native_common["total"]
                           if native_common and native_common["usable"] else None),
                       "common_native_rank1_missed_usable": (not native_common["usable"] and bool(usable)
                           if native_common else None)}
                for kind, pool in (("any", evaluated), ("usable", usable)):
                    best = max(pool, key=lambda r: (r["total"], r["candidate_id"]), default=None)
                    row[f"common_best_{kind}"] = best["total"] if best else None
                    row[f"common_best_{kind}_candidate_id"] = best["candidate_id"] if best else None
                    for criterion in CRITERIA:
                        row[f"common_best_{kind}_{criterion}"] = best[criterion] if best else None
                row["common_native_rank1_regret"] = (row["common_best_any"] - native_common["total"]
                                                     if native_common else None)
                result.append(row)
    return result


def mode_summaries(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["version"], row["corpus"], row["mode"]].append(row)
    result = []
    for (version, corpus, mode), group in groups.items():
        summary = {"version": version, "corpus": corpus, "mode": mode, "targets": len(group),
                   "generated_targets": sum(r["generated_candidates"] > 0 for r in group),
                   "no_candidate_targets": sum(r["status"] == "no_candidates" for r in group),
                   "failed_or_pending_targets": sum(r["status"] not in ("completed", "no_candidates") for r in group),
                   "accepted_targets": sum(r["accepted_candidates"] > 0 for r in group),
                   "native_rank1_targets": sum(r["native_rank1_status"] == "rank1" for r in group),
                   "native_unranked_generated_targets": sum(r["native_rank1_status"] == "unranked" for r in group),
                   "common_native_rank1_regret_mean": average(r["common_native_rank1_regret"] for r in group),
                   "common_native_rank1_missed_usable_targets": sum(r["common_native_rank1_missed_usable"] is True for r in group)}
        for field in ("generated_candidates", "graded_candidates", "accepted_candidates",
                      "audit_blocking_candidates", "common_evaluated_candidates", "common_usable_candidates"):
            summary[field] = sum(r[field] for r in group)
        for field in SCORE_FIELDS:
            summary[field + "_n"] = sum(r[field] is not None for r in group)
            summary[field + "_mean"] = average(r[field] for r in group)
        summary["common_usable_target_percent"] = 100 * summary["common_best_usable_n"] / len(group)
        summary["common_native_rank1_usable_target_percent"] = 100 * summary["common_native_rank1_usable_n"] / len(group)
        for kind in ("any", "usable"):
            for criterion in CRITERIA:
                field = f"common_best_{kind}_{criterion}"
                summary[field + "_mean"] = average(r[field] for r in group)
        result.append(summary)
    return result


def paired_stats(pairs):
    """Complete pairs only; failed, absent, skipped, and unusable entries are never zero."""
    pairs = [(left, right) for left, right in pairs if left is not None and right is not None]
    differences = [left - right for left, right in pairs]
    rng = random.Random(20260930)
    bootstrap = sorted(mean(rng.choices(differences, k=len(differences))) for _ in range(2000)) if pairs else []
    return {"paired_targets": len(pairs), "left_mean": average(p[0] for p in pairs),
            "right_mean": average(p[1] for p in pairs), "mean_left_minus_right": average(differences),
            "left_wins": sum(v > 0 for v in differences), "ties": differences.count(0),
            "right_wins": sum(v < 0 for v in differences),
            "bootstrap95_low": bootstrap[50] if bootstrap else None,
            "bootstrap95_high": bootstrap[-51] if bootstrap else None}


def comparisons(rows, versions):
    index = {(r["version"], r["corpus"], r["target_id"], r["mode"]): r for r in rows}
    version_pairs, mode_pairs = [], []
    fields = SCORE_FIELDS
    for right, left in combinations(versions, 2):
        for corpus, modes in MODES.items():
            for mode in modes:
                pairs = [(r, index[right, corpus, r["target_id"], mode]) for r in rows
                         if r["version"] == left and r["corpus"] == corpus and r["mode"] == mode]
                for field in fields:
                    version_pairs.append({"left_version": left, "right_version": right,
                        "corpus": corpus, "mode": mode, "score": field,
                        **paired_stats((a[field], b[field]) for a, b in pairs)})
    for version in versions:
        for corpus, mode_a, mode_b in (("eurlex", "lookup", "fact_pattern"),
                ("un", "lookup", "practitioner"), ("un", "semantic", "practitioner"),
                ("un", "semantic", "lookup")):
            pairs = [(r, index[version, corpus, r["target_id"], mode_b]) for r in rows
                     if r["version"] == version and r["corpus"] == corpus and r["mode"] == mode_a]
            for field in fields:
                mode_pairs.append({"version": version, "corpus": corpus, "left_mode": mode_a,
                    "right_mode": mode_b, "score": field,
                    **paired_stats((a[field], b[field]) for a, b in pairs)})
    return version_pairs, mode_pairs


def routing_and_selected(runs, mode_rows):
    index = {(r["version"], r["corpus"], r["target_id"], r["mode"]): r for r in mode_rows}
    routes, selected = [], []
    for version, run in runs.items():
        for corpus, modes in MODES.items():
            keys = [key for key in run["targets"] if key[0] == corpus]
            if not keys:
                continue
            for backend in ("generator", "jev"):
                counts = Counter()
                for key in keys:
                    decision = run["decisions"].get((key, backend), {})
                    choice = decision.get("mode") if decision.get("status") == "completed" else "error"
                    if choice not in (*modes, "skip"):
                        choice = "error"
                    counts[choice] += 1
                    mode = index.get((version, corpus, key[1], choice), {})
                    selected.append({"version": version, "corpus": corpus, "target_id": key[1],
                        "backend": backend, "selected_mode": choice,
                        "native_rank1_status": mode.get("native_rank1_status", choice),
                        "common_native_rank1_regret": mode.get("common_native_rank1_regret"),
                        "common_native_rank1_missed_usable": mode.get("common_native_rank1_missed_usable"),
                        **{field: mode.get(field) for field in SCORE_FIELDS}})
                for mode in (*modes, "skip", "error"):
                    routes.append({"version": version, "corpus": corpus, "backend": backend,
                                   "mode": mode, "count": counts[mode], "targets": len(keys),
                                   "percent": 100 * counts[mode] / len(keys)})
    summaries, pairs = [], []
    for version in runs:
        for corpus, allowed_modes in MODES.items():
            for backend in ("generator", "jev"):
                group = [r for r in selected if (r["version"], r["corpus"], r["backend"])
                         == (version, corpus, backend)]
                if not group:
                    continue
                summary = {"version": version, "corpus": corpus, "backend": backend,
                           "targets": len(group), "skips": sum(r["selected_mode"] == "skip" for r in group),
                           "errors": sum(r["selected_mode"] == "error" for r in group),
                           "native_rank1_missing_routed_targets": sum(r["selected_mode"] in allowed_modes
                               and r["native_rank1_status"] != "rank1" for r in group),
                           "common_native_rank1_regret_mean": average(r["common_native_rank1_regret"] for r in group),
                           "common_native_rank1_missed_usable_targets": sum(r["common_native_rank1_missed_usable"] is True for r in group)}
                for field in SCORE_FIELDS:
                    summary[field + "_n"] = sum(r[field] is not None for r in group)
                    summary[field + "_mean"] = average(r[field] for r in group)
                summaries.append(summary)
    selected_index = {(r["version"], r["corpus"], r["target_id"], r["backend"]): r for r in selected}
    for right, left in combinations(runs, 2):
        for corpus in MODES:
            for backend in ("generator", "jev"):
                group = [(r, selected_index[right, corpus, r["target_id"], backend]) for r in selected
                         if (r["version"], r["corpus"], r["backend"]) == (left, corpus, backend)]
                for field in ("legacy_best", "common_best_any", "common_best_usable",
                              "common_native_rank1", "common_native_rank1_usable"):
                    pairs.append({"left_version": left, "right_version": right, "corpus": corpus,
                                  "backend": backend, "score": field,
                                  **paired_stats((a[field], b[field]) for a, b in group)})
    return routes, selected, summaries, pairs


def router_replay(runs, mode_rows, ablation):
    """Replay observed UN routers over fixed banks; do not generate or rerank anything."""
    expected = {key: value for key, value in next(iter(runs.values()))["targets"].items()
                if key[0] == "un"}
    targets = ablation["targets"]
    keys = [("un", row["target_id"]) for row in targets]
    if (len(keys) != len(set(keys)) or set(keys) != set(expected)
            or ablation["target_count"] != len(keys)):
        raise ValueError("router replay targets differ from saved UN selections")
    banks = {}
    for label in ("B", "C"):
        directory = Path(ablation["original_prompts"][label]["run_directory"]).resolve()
        matches = [version for version, run in runs.items() if run["directory"].resolve() == directory]
        if len(matches) > 1:
            raise ValueError("router replay candidate bank has multiple version names")
        if matches:
            banks[label] = matches[0]
    if len(set(banks.values())) != len(banks):
        raise ValueError("router replay B and C must identify distinct candidate banks")
    templates = {label: ablation["original_prompts"][label]["template_sha256"] for label in ("B", "C")}
    for label, (instructions, criteria) in ROUTER_VARIANTS.items():
        if label in ("B", "C"):
            continue
        crossed = ablation["crossed_runs"][label]
        swap = crossed["swap"]
        if (swap["base_template"] != instructions or swap["instructions_from"] != instructions
                or swap["criteria_from"] != criteria):
            raise ValueError(f"router replay provenance mismatch for {label}")
        templates[label] = crossed["template_sha256"]
    for row in targets:
        key = "un", row["target_id"]
        source_hash = expected[key]["source_payload_sha256"]
        if row["source_payload_sha256"] != source_hash:
            raise ValueError(f"router replay target source hash mismatch for {key}")
        if set(row["variants"]) != set(ROUTER_VARIANTS):
            raise ValueError(f"router replay needs all four observed variants for {key}")
        for label, decision in row["variants"].items():
            if decision["source_payload_sha256"] != source_hash:
                raise ValueError(f"router replay decision state hash mismatch for {label}/{key}")
            if decision["mode"] not in (*MODES["un"], "skip"):
                raise ValueError(f"router replay invalid observed mode for {label}/{key}")
            if decision["resolved_backend"] != ablation["resolved_backend"]:
                raise ValueError(f"router replay resolved backend mismatch for {label}/{key}")
            if label in banks:
                original = runs[banks[label]]["decisions"].get((key, "jev"), {})
                if original.get("status") != "completed" or original.get("mode") != decision["mode"]:
                    raise ValueError(f"router replay original decision mismatch for {label}/{key}")
    index = {(r["version"], r["corpus"], r["target_id"], r["mode"]): r for r in mode_rows}
    rows, summaries = [], []
    for bank_label, version in banks.items():
        for router, (instructions, criteria) in ROUTER_VARIANTS.items():
            group = []
            identity = {"router_variant": router, "router_parent_bundle": instructions,
                        "router_instructions_from": instructions, "router_criteria_from": criteria,
                        "router_prompt_sha256": templates[router],
                        "candidate_bank": version, "candidate_bank_label": bank_label,
                        "corpus": "un", "router_backend": ablation["resolved_backend"]}
            for target in targets:
                decision = target["variants"][router]
                choice = decision["mode"]
                mode = (index[version, "un", target["target_id"], choice] if choice != "skip" else {})
                row = identity | {"target_id": target["target_id"], "symbol": target.get("symbol", ""),
                    "source_payload_sha256": target["source_payload_sha256"], "selected_mode": choice,
                    "native_rank1_status": mode.get("native_rank1_status", choice),
                    **{field: mode.get(field) for field in (*REPLAY_SCORE_FIELDS,
                        "native_rank1_candidate_id", "common_best_any_candidate_id", "common_best_usable_candidate_id",
                        "generated_candidates", "common_evaluated_candidates", "common_usable_candidates")}}
                group.append(row)
            rows.extend(group)
            summary = identity | {"targets": len(group),
                "routed_targets": sum(r["selected_mode"] != "skip" for r in group),
                "skips": sum(r["selected_mode"] == "skip" for r in group),
                "no_candidate_routed_targets": sum(r["generated_candidates"] == 0 for r in group),
                "native_rank1_missing_routed_targets": sum(r["selected_mode"] != "skip"
                    and r["native_rank1_status"] != "rank1" for r in group),
                "common_native_rank1_missing_evaluation_targets": sum(r["native_rank1_status"] == "rank1"
                    and r["common_native_rank1"] is None for r in group),
                "common_incomplete_routed_targets": sum(r["selected_mode"] != "skip"
                    and r["common_evaluated_candidates"] < r["generated_candidates"] for r in group)}
            summary.update({"routes_" + mode: sum(r["selected_mode"] == mode for r in group)
                            for mode in MODES["un"]})
            for field in REPLAY_SCORE_FIELDS:
                summary[field + "_n"] = sum(r[field] is not None for r in group)
                summary[field + "_mean"] = average(r[field] for r in group)
                summary[field + "_target_percent"] = (100 * summary[field + "_n"] / len(group)
                                                        if group else None)
            summaries.append(summary)
    metadata = {"available": bool(banks), "corpus": "un", "targets": len(targets),
        "candidate_banks": banks, "router_variants": list(ROUTER_VARIANTS),
        "excluded_bank_labels": [label for label in ("B", "C") if label not in banks],
        "verified_target_and_decision_payload_hashes": True,
        "verified_original_router_choices": list(banks), "sensitivity_content_sha256": digest(ablation),
        "definition": "Counterfactual replay of four observed routers over existing B/C candidate banks; not a fresh joint generation run. Native rank1 is the exported verifier ranking, not a claimed delivered winner. Common best scores are oracle selections within the chosen mode.",
        "missing_scores": "Skips, absent candidates, missing common evaluations and unusable candidates are excluded from the relevant score means, never zero-imputed. Coverage uses all matched UN targets; incomplete evaluation makes usable coverage provisional."}
    return rows, summaries, metadata


def prompt_lengths(runs):
    result = []
    for version, run in runs.items():
        prompts = run["metadata"].get("prompts", {})
        if not prompts and (run["directory"] / "prompt_manifest.json").exists():
            manifest = json.loads((run["directory"] / "prompt_manifest.json").read_text())
            prompts = {key: entry["text"] for key, entry in manifest["prompts"].items()}
        for key, text in prompts.items():
            if key not in ACTIVE_KEYS:
                continue
            result.append({"version": version, "prompt": key, "characters": len(text),
                           "words": len(text.split()), "sha256": hashlib.sha256(text.encode()).hexdigest()})
    return result


def usage(directory, version):
    if (directory / "usage.csv").exists():
        source = read_csv(directory / "usage.csv")
    elif (directory / "run.sqlite").exists():
        grouped = defaultdict(lambda: Counter())
        with sqlite3.connect((directory / "run.sqlite").resolve().as_uri() + "?mode=ro", uri=True) as db:
            for stage, raw in db.execute("SELECT stage,record FROM requests"):
                record = json.loads(raw)
                cell = grouped[stage, record.get("model", "unknown")]
                cell["calls"] += 1
                cell["provider_errors"] += record.get("status") == "error"
                values = record.get("usage") or {}
                cell["prompt_tokens"] += values.get("prompt_tokens") or 0
                cell["completion_tokens"] += values.get("completion_tokens") or 0
                cell["reported_cost"] += values.get("provider_cost") or 0
                cell["calls_missing_cost"] += values.get("provider_cost") is None
        source = [{"stage": stage, "model": model, **values} for (stage, model), values in grouped.items()]
    else:
        return [{"version": version, "stage": "unknown", "cost_complete": False,
                 "reported_cost_subtotal": None, "total_cost": None}]
    result = []
    for row in source:
        missing = number(row.get("calls_missing_cost"))
        subtotal = number(row.get("reported_cost"))
        result.append({"version": version, "stage": row["stage"], "model": row["model"],
                       **{field: number(row.get(field)) for field in (
                           "calls", "provider_errors", "prompt_tokens", "completion_tokens")},
                       "calls_missing_cost": missing, "reported_cost_subtotal": subtotal,
                       "cost_complete": missing == 0 and subtotal is not None,
                       "total_cost": subtotal if missing == 0 else None})
    return result


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def table(rows, fields):
    def display(value):
        if value is None:
            return "—"
        return html.escape(f"{value:.2f}" if isinstance(value, float) else str(value))
    head = "".join("<th>" + html.escape(field.replace("_", " ")) + "</th>" for field in fields)
    body = "".join("<tr>" + "".join("<td>" + display(row.get(field)) + "</td>" for field in fields)
                   + "</tr>" for row in rows)
    return '<div class="scroll"><table><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table></div>"


def score_chart(summaries, common_available):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    field = "common_best_usable" if common_available else "legacy_best"
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    colors = ("#2e5fa5", "#bd653b", "#34856b", "#9164a2")
    versions = list(dict.fromkeys(r["version"] for r in summaries))
    for ax, (corpus, modes) in zip(axes, MODES.items()):
        for offset, version in enumerate(versions):
            rows = {r["mode"]: r for r in summaries if r["version"] == version and r["corpus"] == corpus}
            x, y = [], []
            for position, mode in enumerate(modes):
                value = rows.get(mode, {}).get(field + "_mean")
                if value is not None:
                    x.append(position + (offset - (len(versions) - 1) / 2) * .23)
                    y.append(value)
            bars = ax.bar(x, y, width=.21, color=colors[offset % len(colors)], label=version)
            ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=8)
        ax.set_xticks(range(len(modes)), modes)
        ax.set_ylim(0, 28 if common_available else 43)
        ax.set_title(corpus.upper())
        ax.set_ylabel("Best available usable common score /25 (oracle)" if common_available else "Legacy mode-specific score /40")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=8)
    stream = io.StringIO()
    fig.savefig(stream, format="svg")
    plt.close(fig)
    return "<svg" + stream.getvalue().split("<svg", 1)[1]


def render_html(output, data):
    available = data["common_evaluation"]["available"]
    sections = ["<h1>Legal prompt experiment comparison</h1>",
        ("<p>Identical saved selections and source payload hashes were verified across versions. "
        "Scores exclude missing candidates, skips, failed evaluations and unusable candidates where indicated; "
        "none is assigned zero. Coverage is reported separately.</p>"),
        "<p>" + ("The frozen, blinded common rubric is the primary comparison. Usable requires grounding ≥4, "
                  "answer resolution ≥4, retrievability ≥3, information value ≥3 and clarity ≥3." if available else
                  "Common blinded evaluation is not available yet. The following legacy scores use different "
                  "mode/version rubrics and cannot establish unbiased question quality.") + "</p>",
        ("<p>One generation draw per mode/target. Best-of-batch metrics can favor modes with more candidates. "
        "Bootstrap intervals resample matched targets (2,000 draws); they do not include model rerun variability. "
        "This stratified sample is not a corpus-frequency estimate.</p>"),
        score_chart(data["mode_summary"], available), "<h2>Availability and scores</h2>"]
    if available and data["common_evaluation"]["missing_memberships"]:
        common = data["common_evaluation"]
        sections.insert(1, "<p><strong>Shared quality evaluation is incomplete: "
                        f"{common['completed_memberships']} of {common['candidate_memberships']} candidate memberships "
                        "have completed scores. These partial results cannot establish an overall quality ranking "
                        "between versions or modes.</strong></p>")
    fields = ["version", "corpus", "mode", "targets", "generated_targets", "generated_candidates", "accepted_targets"]
    fields += (["common_best_any_n", "common_best_any_mean", "common_best_usable_n", "common_best_usable_mean"]
               if available else ["legacy_best_n", "legacy_best_mean"])
    sections.append(table(data["mode_summary"], fields))
    if available and data["common_evaluation"]["missing_memberships"]:
        sections.append("<p>Common evaluation is incomplete: " +
                        str(data["common_evaluation"]["missing_memberships"]) +
                        " candidate memberships have no completed common score. Interpret coverage and means accordingly.</p>")
    if data["verification"]["model_or_generation_setting_differences"]:
        sections.append("<p>Model or generation settings also differ between runs: " +
                        html.escape(json.dumps(data["verification"]["model_or_generation_setting_differences"])) +
                        ". Effects cannot be attributed solely to prompt changes.</p>")
    if (output.parent / "rationale.html").exists():
        sections.append('<p><a href="../rationale.html">Exact original clauses, revisions and remaining routing caveats</a>.</p>')
    limitations = data.get("experiment_design", {}).get("limitations", [
        "The common judge uses the same verifier model with a fixed rubric; this is not human validation or a measured retrieval test.",
    ])
    sections.append("<h2>Interpretation limits</h2><ul>" +
                    "".join("<li>" + html.escape(item) + "</li>" for item in limitations) + "</ul>" +
                    "<p>Generation, grading and router prompts change together in the three full bundles; "
                    "that comparison cannot isolate their individual causal effects.</p>")
    if (output.parent / "eurlex_case_review.json").exists():
        sections.append('<p><a href="../eurlex_case_review.json">Three inspected EUR-Lex cases: residual grading penalties and real defects</a>.</p>')
    if (output.parent / "common_judge_audit.json").exists():
        sections.append('<p><a href="../common_judge_audit.json">Documented errors in the common judge</a>: '
                        'its scores are diagnostic model judgments, not gold labels.</p>')
    if (output.parent / "un_case_review.json").exists():
        sections.append('<p><a href="../un_case_review.json">Four manually inspected UN practitioner blocking cases</a> '
                        '(a targeted diagnostic review, not a representative human evaluation).</p>')
    if data.get("router_ablation"):
        ablation = data["router_ablation"]
        cells = [{"variant": label, **cell["mode_counts"],
                  "mean_practitioner_probability": cell["mean_probabilities"]["practitioner"]}
                 for label, cell in ablation["summaries"].items()]
        sections += [("<h2>Controlled UN Jev instruction/criteria swaps</h2>"
                     "<p>B means the bias-adjusted prompt; C means the simple prompt. All four cells use the same "
                     "50 source states and resolved backend. These are routing outcomes, not question-quality scores.</p>"),
                     table(cells, ["variant", "lookup", "practitioner", "semantic", "skip", "mean_practitioner_probability"]),
                     "<p>" + html.escape(ablation["finding"]) + "</p>",
                     '<p><a href="../un_router_sensitivity.json">Exact swaps, per-target probabilities, backend checks and registered versions</a>.</p>']
    if available and data.get("router_replay_summary"):
        sections += [("<h2>UN router replay over fixed candidate banks</h2>"
                      "<p>Each of the four observed routers selects a mode from the same saved B or C candidate bank. "
                      "This is a counterfactual replay of existing candidates, not a fresh joint generation run. "
                      "Native rank1 follows the bank's original verifier ranking; best-any and best-usable are common-evaluator "
                      "oracle selections within the chosen mode. Means exclude skipped, missing and (for usable scores) "
                      "unusable outputs. Usable coverage retains all matched targets in the denominator.</p>"),
                     table(data["router_replay_summary"], ["router_variant", "candidate_bank", "targets", "skips",
                           "common_native_rank1_n", "common_native_rank1_mean", "common_native_rank1_usable_n",
                           "common_native_rank1_usable_target_percent", "common_best_any_mean",
                           "common_best_usable_n", "common_best_usable_mean", "common_incomplete_routed_targets"])]
    if available:
        sections += [("<h2>Verifier rank diagnostic</h2><p>Common best-any and best-usable scores select the best available "
                      "candidate under the common evaluator (an oracle). Native rank1 instead evaluates the exported "
                      "candidate_rank=1 from the original grader ranking. It is not an actual delivered winner: screening "
                      "exports leave is_best false until a separate best export. No ranking is reconstructed here. "
                      "Regret is the common oracle score minus the common score of native rank1. Missed usable counts "
                      "targets where rank1 failed the common usability gate although another candidate passed.</p>"),
                     table(data["mode_summary"], ["version", "corpus", "mode", "native_rank1_targets",
                           "native_unranked_generated_targets", "common_native_rank1_n", "common_native_rank1_mean",
                           "common_native_rank1_usable_n", "common_native_rank1_regret_mean",
                           "common_native_rank1_missed_usable_targets"])]
    sections += ["<h2>Paired version changes</h2><p>Differences are left version minus right version.</p>",
        table([r for r in data["paired_versions"] if r["score"] in (("common_best_usable", "common_native_rank1") if available else ("legacy_best",))],
              ["left_version", "right_version", "corpus", "mode", "score", "paired_targets", "mean_left_minus_right", "bootstrap95_low", "bootstrap95_high"]),
        "<h2>Mode differences within each version</h2>",
        table([r for r in data["mode_gaps"] if r["score"] == ("common_best_any" if available else "legacy_best")],
              ["version", "corpus", "left_mode", "right_mode", "paired_targets", "mean_left_minus_right", "bootstrap95_low", "bootstrap95_high"]),
        "<h2>Decider routing</h2>", table(data["routing"], ["version", "corpus", "backend", "mode", "count", "percent"]),
        "<h2>Quality of the originally selected modes</h2>",
        table(data["selected_summary"], ["version", "corpus", "backend", "targets", "skips", "errors"] +
              (["common_best_any_n", "common_best_any_mean", "common_best_usable_n", "common_best_usable_mean",
                "common_native_rank1_n", "common_native_rank1_mean", "common_native_rank1_usable_n"] if available
               else ["legacy_best_n", "legacy_best_mean"])),
        ("<h2>Usage and reported cost</h2><p>Reported cost is a subtotal when a provider omits cost. "
        "Missing provider costs are unknown, not free. Common evaluation is listed separately.</p>"),
        table(data["usage"], ["version", "stage", "model", "calls", "prompt_tokens", "completion_tokens", "reported_cost_subtotal", "calls_missing_cost", "total_cost"]),
        "<details><summary>Active English prompt lengths and exact hashes (16 per run)</summary>",
        table(data["prompt_lengths"], ["version", "prompt", "characters", "words", "sha256"]), "</details>",
        "<h2>Download data</h2><p>" + " · ".join(f'<a href="{name}.csv">{name}</a>' for name in data if isinstance(data[name], list))
        + ' · <a href="summary.json">summary.json</a></p>']
    css = "body{font:15px system-ui,sans-serif;max-width:1450px;margin:40px auto;padding:0 24px;color:#18212b}h1{font-size:30px}h2{margin-top:36px}p{line-height:1.6;max-width:1100px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:12px}th,td{text-align:left;border-bottom:1px solid #dce2e8;padding:8px;white-space:nowrap}th{background:#edf2f7}svg{max-width:100%;height:auto}summary{cursor:pointer;font-weight:600}a{color:#2e5fa5}"
    (output / "report.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Legal prompt experiment</title><style>'
                                        + css + "</style><main>" + "\n".join(sections) + "</main></html>", encoding="utf-8")


def compare(runs, common_path=None):
    verification = check_pairing(runs)
    common, common_info = common_scores(common_path, runs)
    modes = per_target_modes(runs, common)
    paired, gaps = comparisons(modes, list(runs))
    routing, selected, selected_summary, selected_pairs = routing_and_selected(runs, modes)
    costs = [row for version, run in runs.items() for row in usage(run["directory"], version)]
    if common_path:
        costs.extend(usage(common_path.parent, "common_evaluation"))
    return {"verification": verification, "common_evaluation": common_info,
            "native_rank_diagnostic": {"definition": "Unique exported candidate_rank=1 with completed grades; never a reconstructed ranking or claimed delivered winner.",
                                       "is_best_true_by_version": {version: sum(truth(r.get("is_best")) for r in run["candidates"])
                                                                   for version, run in runs.items()},
                                       "oracle_definition": "common_best_any/common_best_usable choose the best available candidate under the common evaluator."},
            "run_configs": {version: run["config"] for version, run in runs.items()},
            "per_target_mode": modes, "mode_summary": mode_summaries(modes),
            "routing": routing, "paired_versions": paired, "mode_gaps": gaps,
            "selected_mode_scores": selected, "selected_summary": selected_summary,
            "selected_paired_versions": selected_pairs, "prompt_lengths": prompt_lengths(runs),
            "usage": costs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", required=True, help="VERSION=RUN_DIRECTORY")
    parser.add_argument("--common", type=Path, help="Frozen evaluator candidate_scores.csv")
    parser.add_argument("--router-sensitivity", type=Path,
                        help="Saved UN router sensitivity JSON; defaults to the output parent's un_router_sensitivity.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mlflow-registry-uri",
                        help="Optionally log aggregate metrics to the local sqlite:/// prompt registry")
    args = parser.parse_args()
    locations = dict(value.split("=", 1) for value in args.run)
    if len(locations) != len(args.run):
        raise ValueError("run version names must be unique")
    runs = {version: load_run(version, Path(path)) for version, path in locations.items()}
    data = compare(runs, args.common)
    args.output.mkdir(parents=True, exist_ok=True)
    design_path = args.output.parent / "experiment_design.json"
    if design_path.exists():
        data["experiment_design"] = json.loads(design_path.read_text(encoding="utf-8"))
    ablation_path = args.router_sensitivity or args.output.parent / "un_router_sensitivity.json"
    if args.router_sensitivity and not ablation_path.is_file():
        raise FileNotFoundError(ablation_path)
    if ablation_path.exists():
        ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
        data["router_ablation"] = {key: ablation[key] for key in
                                  ("summaries", "finding", "factorial_comparisons", "interpretation_caveat")}
        if data["common_evaluation"]["available"]:
            rows, summaries, metadata = router_replay(runs, data["per_target_mode"], ablation)
            data.update(router_replay_rows=rows, router_replay_summary=summaries, router_replay=metadata)
    for name, rows in data.items():
        if isinstance(rows, list):
            write_csv(args.output / f"{name}.csv", rows)
    (args.output / "summary.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    render_html(args.output, data)
    if args.mlflow_registry_uri:
        from clir_bench.core.experiment_tracking import publish_comparison_metrics
        tracking = publish_comparison_metrics(args.output / "summary.json", args.mlflow_registry_uri)
        (args.output / "mlflow_runs.json").write_text(json.dumps(tracking, indent=2) + "\n")
    print(json.dumps({"targets": data["verification"]["targets"],
                      "versions": list(runs), "common": data["common_evaluation"],
                      "report": str((args.output / "report.html").resolve())}, indent=2))


if __name__ == "__main__":
    main()
