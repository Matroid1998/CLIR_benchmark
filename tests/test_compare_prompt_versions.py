"""Paired report integrity: missing values, blinded scores, and source identity."""

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "reports/prompt_experiments/compare_versions.py"
spec = importlib.util.spec_from_file_location("compare_prompt_versions", SCRIPT)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_run(directory, version, *, missing_second=False):
    directory.mkdir()
    selection = [{"corpus": "un", "target_id": f"target#{i}", "source_payload": f"source {i}",
                  "source_payload_sha256": hashlib.sha256(f"source {i}".encode()).hexdigest(),
                  "symbol": f"A/{i}", "is_meeting": i == 2, "stratum": "meeting" if i == 2 else "resolution"}
                 for i in (1, 2)]
    (directory / "selection.json").write_text(json.dumps(selection))
    (directory / "config.json").write_text(json.dumps({"generator": "test"}))
    candidates, modes, decisions = [], [], []
    for source in selection:
        i = source["target_id"][-1]
        for mode in report.MODES["un"]:
            missing = missing_second and i == "2" and mode == "practitioner"
            if not missing:
                candidates.append({"corpus": "un", "target_id": source["target_id"],
                    "screening_mode": mode, "candidate_id": f"{version}-{i}-{mode}",
                    "question": f"Which {mode} {i}?", "answer": f"{mode} answer {i}",
                    "source_payload_sha256": source["source_payload_sha256"],
                    "grading_status": "completed", "total_score": 32 if version == "baseline" else 35,
                    "faith_grounding": 5, "quality_audit_status": "clear"})
            modes.append({"corpus": "un", "target_id": source["target_id"], "mode": mode,
                          "best_score": "" if missing else 32 if version == "baseline" else 35,
                          "status": "no_candidates" if missing else "completed"})
        for backend in ("generator", "jev"):
            decisions.append({"corpus": "un", "target_id": source["target_id"],
                              "backend": backend, "status": "completed",
                              "mode": "skip" if missing_second and i == "2" else "practitioner"})
    write_csv(directory / "all_mode_candidates.csv", candidates)
    write_csv(directory / "mode_scores.csv", modes)
    write_csv(directory / "decisions.csv", decisions)
    return report.load_run(version, directory)


@pytest.fixture
def runs(tmp_path):
    return {"baseline": make_run(tmp_path / "baseline", "baseline"),
            "debiased": make_run(tmp_path / "debiased", "debiased", missing_second=True)}


def make_common(path, runs):
    rows = []
    for version, run in runs.items():
        for candidate in run["candidates"]:
            scores = dict.fromkeys(report.CRITERIA, 4)
            if version == "debiased":
                scores["clarity"] = 5
            row = {key: candidate[key] for key in ("corpus", "target_id", "candidate_id", "question", "answer")}
            rows.append(row | {"version": version, "mode": candidate["screening_mode"],
                               "blind_id": candidate["candidate_id"], **scores,
                               "total": sum(scores.values()), "usable": True,
                               "evaluation_status": "completed"})
    write_csv(path, rows)
    return rows


def test_missing_mode_outputs_and_skips_are_never_zero_imputed(runs):
    data = report.compare(runs)
    pair = next(r for r in data["paired_versions"] if r["corpus"] == "un"
                and r["mode"] == "practitioner" and r["score"] == "legacy_best")
    assert pair["paired_targets"] == 1
    assert pair["mean_left_minus_right"] == 3
    selected = next(r for r in data["selected_summary"] if r["version"] == "debiased"
                    and r["corpus"] == "un" and r["backend"] == "jev")
    assert selected["skips"] == 1
    assert selected["legacy_best_mean"] == 35
    assert selected["legacy_best_n"] == 1


def test_common_scores_use_frozen_gate_and_keep_coverage_separate(runs, tmp_path):
    path = tmp_path / "common.csv"
    rows = make_common(path, runs)
    rows[0]["grounding"], rows[0]["total"], rows[0]["usable"] = 3, 19, False
    rows[1]["information_value"], rows[1]["total"], rows[1]["usable"] = 2, 18, False
    write_csv(path, rows)
    data = report.compare(runs, path)
    assert data["common_evaluation"]["missing_memberships"] == 0
    lookup = next(r for r in data["mode_summary"] if r["version"] == "baseline" and r["mode"] == "lookup")
    assert lookup["common_best_any_n"] == 2
    assert lookup["common_best_usable_n"] == 1
    assert lookup["common_best_usable_mean"] == 20
    assert data["usage"][-1]["total_cost"] is None


def test_source_selection_or_hash_mismatch_refuses_report(runs):
    runs["debiased"]["targets"]["un", "target#1"]["source_payload"] = "changed"
    with pytest.raises(ValueError, match="selections/source payloads differ"):
        report.compare(runs)


def test_common_misattribution_and_gate_changes_are_rejected(runs, tmp_path):
    path = tmp_path / "common.csv"
    rows = make_common(path, runs)
    rows[0]["question"] = "Different question"
    write_csv(path, rows)
    with pytest.raises(ValueError, match="content/identity mismatch"):
        report.compare(runs, path)
    rows = make_common(path, runs)
    rows[0]["clarity"], rows[0]["total"] = 2, 18
    write_csv(path, rows)
    with pytest.raises(ValueError, match="total/usability gate"):
        report.compare(runs, path)


def test_native_rank1_diagnostic_differs_from_common_oracle_without_reranking(runs, tmp_path):
    original = runs["baseline"]["candidates"][0]
    original["candidate_rank"] = "2"
    native = original | {"candidate_id": "native-rank1", "candidate_rank": "1", "is_best": "False",
                         "question": "Native preferred question?", "total_score": 36}
    runs["baseline"]["candidates"].append(native)
    path = tmp_path / "common.csv"
    rows = make_common(path, runs)
    for row in rows:
        if row["candidate_id"] == original["candidate_id"]:
            row.update(dict.fromkeys(report.CRITERIA, 5))
            row["total"] = 25
        if row["candidate_id"] == "native-rank1":
            row.update(grounding=3, total=19, usable=False)
    write_csv(path, rows)
    data = report.compare(runs, path)
    target = next(r for r in data["per_target_mode"] if r["version"] == "baseline"
                  and r["target_id"] == original["target_id"] and r["mode"] == original["screening_mode"])
    assert target["common_best_any"] == 25
    assert target["common_native_rank1"] == 19
    assert target["common_native_rank1_usable"] is None
    assert target["common_native_rank1_regret"] == 6
    assert target["common_native_rank1_missed_usable"] is True
    assert data["native_rank_diagnostic"]["is_best_true_by_version"]["baseline"] == 0


def test_unexported_native_rank_stays_missing_and_duplicate_rank1_is_rejected(runs):
    data = report.compare(runs)
    assert all(r["common_native_rank1"] is None for r in data["per_target_mode"])
    original = runs["baseline"]["candidates"][0]
    original["candidate_rank"] = "1"
    runs["baseline"]["candidates"].append(original | {"candidate_id": "duplicate", "candidate_rank": "1"})
    with pytest.raises(ValueError, match="duplicate candidate_rank=1"):
        report.compare(runs)


def make_router_sensitivity(runs):
    banks = {"B": "debiased", "C": "baseline"}
    targets = []
    for key, source in runs["baseline"]["targets"].items():
        variants = {}
        for router in report.ROUTER_VARIANTS:
            if router in banks:
                mode = runs[banks[router]]["decisions"][key, "jev"]["mode"]
            elif router == "b_instructions_c_criteria":
                mode = "lookup" if key[1] == "target#1" else "practitioner"
            else:
                mode = "semantic" if key[1] == "target#1" else "skip"
            variants[router] = {"mode": mode, "source_payload_sha256": source["source_payload_sha256"],
                                "resolved_backend": "test-jev"}
        targets.append({"target_id": key[1], "symbol": source["symbol"],
                        "source_payload_sha256": source["source_payload_sha256"], "variants": variants})
    return {"target_count": len(targets), "targets": targets, "resolved_backend": "test-jev",
            "original_prompts": {label: {"run_directory": str(runs[version]["directory"]),
                                          "template_sha256": report.digest(label)}
                                 for label, version in banks.items()},
            "crossed_runs": {label: {"template_sha256": report.digest(label),
                "swap": {"base_template": instructions, "instructions_from": instructions, "criteria_from": criteria}}
                for label, (instructions, criteria) in report.ROUTER_VARIANTS.items() if label not in banks}}


def test_router_replay_follows_observed_modes_in_fixed_banks_without_zero_imputation(runs, tmp_path):
    for run in runs.values():
        for candidate in run["candidates"]:
            candidate["candidate_rank"] = 1
    original = runs["debiased"]["candidates"][0]
    runs["debiased"]["candidates"].append(original | {"candidate_id": "lookup-alternative", "candidate_rank": 2,
        "question": "Alternative lookup question?", "total_score": 30})
    common_path = tmp_path / "common.csv"
    scores = make_common(common_path, runs)
    for row in scores:
        if row["candidate_id"] == original["candidate_id"]:
            row.update(grounding=3, total=20, usable=False)
        if row["candidate_id"] == "lookup-alternative":
            row.update(dict.fromkeys(report.CRITERIA, 5))
            row["total"] = 25
    write_csv(common_path, scores)
    data = report.compare(runs, common_path)
    rows, summaries, metadata = report.router_replay(runs, data["per_target_mode"], make_router_sensitivity(runs))
    assert len(rows) == 16 and len(summaries) == 8
    assert metadata["verified_target_and_decision_payload_hashes"]
    selected = next(r for r in rows if r["candidate_bank"] == "debiased"
                    and r["router_variant"] == "b_instructions_c_criteria" and r["target_id"] == "target#1")
    assert selected["selected_mode"] == "lookup"
    assert selected["native_rank1_candidate_id"] == original["candidate_id"]
    assert selected["common_native_rank1"] == 20
    assert selected["common_native_rank1_usable"] is None
    assert selected["common_best_any"] == selected["common_best_usable"] == 25
    missing = next(r for r in rows if r["candidate_bank"] == "debiased"
                   and r["router_variant"] == "b_instructions_c_criteria" and r["target_id"] == "target#2")
    assert missing["selected_mode"] == "practitioner"
    assert missing["generated_candidates"] == 0 and missing["common_best_any"] is None
    summary = next(r for r in summaries if r["candidate_bank"] == "debiased"
                   and r["router_variant"] == "b_instructions_c_criteria")
    assert summary["targets"] == 2 and summary["no_candidate_routed_targets"] == 1
    assert summary["common_native_rank1_n"] == 1 and summary["common_native_rank1_mean"] == 20
    assert summary["common_native_rank1_usable_n"] == 0 and summary["common_native_rank1_usable_mean"] is None
    assert summary["common_best_usable_mean"] == 25 and summary["common_best_usable_target_percent"] == 50
    skipped = next(r for r in summaries if r["candidate_bank"] == "debiased"
                   and r["router_variant"] == "c_instructions_b_criteria")
    assert skipped["skips"] == 1 and skipped["common_native_rank1_mean"] == 21
    other_bank = next(r for r in summaries if r["candidate_bank"] == "baseline"
                     and r["router_variant"] == "b_instructions_c_criteria")
    assert other_bank["common_native_rank1_n"] == 2 and other_bank["common_native_rank1_mean"] == 20
    data.update(router_replay_rows=rows, router_replay_summary=summaries, router_replay=metadata)
    report.render_html(tmp_path, data)
    assert "not a fresh joint generation run" in (tmp_path / "report.html").read_text()


@pytest.mark.parametrize("tamper,error", [("state", "decision state hash"), ("source", "target source hash"),
                                          ("target", "targets differ"), ("choice", "original decision mismatch")])
def test_router_replay_rejects_source_or_original_decision_mismatches(runs, tamper, error):
    ablation = make_router_sensitivity(runs)
    row = ablation["targets"][0]
    if tamper == "state":
        row["variants"]["b_instructions_c_criteria"]["source_payload_sha256"] = "wrong"
    elif tamper == "source":
        row["source_payload_sha256"] = "wrong"
    elif tamper == "target":
        row["target_id"] = "other-target"
    else:
        row["variants"]["B"]["mode"] = "semantic"
    with pytest.raises(ValueError, match=error):
        report.router_replay(runs, report.compare(runs)["per_target_mode"], ablation)


def test_legacy_target_identifiers_are_supported():
    assert report.target_key({"celex_id": "32000R0001", "target_article_id": "eli"}) == ("eurlex", "eli")
    assert report.target_key({"block_id": "un#1"}) == ("un", "un#1")


def test_partial_cost_is_not_reported_as_complete(runs):
    directory = runs["baseline"]["directory"]
    write_csv(directory / "usage.csv", [{"stage": "generation", "model": "test", "calls": 2,
        "provider_errors": 0, "prompt_tokens": 100, "completion_tokens": 20,
        "reported_cost": .25, "calls_missing_cost": 1}])
    row = report.usage(directory, "baseline")[0]
    assert row["reported_cost_subtotal"] == .25
    assert row["total_cost"] is None and row["cost_complete"] is False


def test_html_is_self_contained_and_escapes_provider_values(runs, tmp_path):
    data = report.compare(runs)
    data["usage"][0]["model"] = "<script>bad()</script>"
    report.render_html(tmp_path, data)
    text = (tmp_path / "report.html").read_text()
    assert "<svg" in text
    assert "&lt;script&gt;bad()&lt;/script&gt;" in text
    assert "<script>bad()" not in text
    assert "cannot establish unbiased question quality" in text
