"""Actual local MLflow lifecycle; no service, account, or model calls."""

import json

import pytest

from clir_bench.core.experiment_tracking import publish_comparison_metrics, version_metrics


def summary():
    return {"verification": {"identical_selections": True, "selection_sha256": "selection"},
            "run_configs": {"baseline": {"prompt_registry": {
                "provider": "mlflow", "bundle": "baseline", "bundle_sha256": "bundle",
                "prompts": {"un/generation/lookup": {"name": "registered-prompt", "version": 1,
                                                       "sha256": "hash", "text": "DO NOT LOG"}}}},
                            "debiased": {}},
            "common_evaluation": {"available": True, "config": {"model": "test"}},
            "routing": [{"version": "baseline", "corpus": "un", "backend": "jev",
                         "mode": "lookup", "count": 30, "percent": 60.0}],
            "mode_summary": [{"version": "baseline", "corpus": "un", "mode": "lookup",
                              "common_best_usable_mean": 22, "common_best_usable_n": 30,
                              "common_usable_target_percent": 60.0,
                              "legacy_best_mean": 35, "common_best_any_mean": None}],
            "selected_summary": [],
            "usage": [{"version": "baseline", "stage": "generation", "model": "gpt/test",
                       "calls": 10, "prompt_tokens": 100, "completion_tokens": 50,
                       "reported_cost_subtotal": .1, "calls_missing_cost": 2,
                       "total_cost": None, "cost_complete": False}]}


def test_missing_scores_and_costs_are_availability_flags_not_zero_values():
    metrics = version_metrics(summary(), "baseline")
    assert "mode/un/lookup/common_best_any_mean" not in metrics
    assert metrics["mode/un/lookup/common_best_any_mean__available"] == 0
    assert "usage/generation/gpt/test/total_cost" not in metrics
    assert metrics["usage/generation/gpt/test/calls_missing_cost"] == 2


def test_local_mlflow_reuses_run_and_logs_new_revision_without_prompt_text(tmp_path, monkeypatch):
    monkeypatch.setenv("MLFLOW_DISABLE_AGENT_HINT", "1")
    mlflow = pytest.importorskip("mlflow")
    output = tmp_path / "experiment" / "comparison"
    output.mkdir(parents=True)
    path = output / "summary.json"
    data = summary()
    path.write_text(json.dumps(data))
    uri = "sqlite:///" + str(tmp_path / "registry.db")
    first = publish_comparison_metrics(path, uri)
    second = publish_comparison_metrics(path, uri)
    assert first == second
    client = mlflow.MlflowClient(tracking_uri=uri, registry_uri=uri)
    runs = client.search_runs([first["experiment_id"]])
    assert len(runs) == 2
    baseline_id = first["runs"]["baseline"]
    baseline = client.get_run(baseline_id)
    assert baseline.info.status == "FINISHED"
    assert baseline.data.tags["clir.bundle"] == "baseline"
    assert baseline.data.tags["clir.experiment_root"] == str(output.parent)
    assert baseline.data.metrics["mode/un/lookup/common_best_usable_mean"] == 22
    history = client.get_metric_history(baseline_id, "mode/un/lookup/common_best_usable_mean")
    assert len(history) == 1
    artifacts = tmp_path / "downloads"
    artifacts.mkdir()
    artifact = client.download_artifacts(baseline_id, "prompt_versions.json", str(artifacts))
    with open(artifact) as stream:
        recorded = json.load(stream)
    assert "text" not in recorded["prompts"]["un/generation/lookup"]
    assert "DO NOT LOG" not in json.dumps(recorded)
    data["mode_summary"][0]["common_best_usable_mean"] = 23
    path.write_text(json.dumps(data))
    updated = publish_comparison_metrics(path, uri)
    assert updated["runs"] == first["runs"]
    assert len(client.search_runs([first["experiment_id"]])) == 2
    assert client.get_run(baseline_id).data.metrics["mode/un/lookup/common_best_usable_mean"] == 23
    assert len(client.get_metric_history(baseline_id, "mode/un/lookup/common_best_usable_mean")) == 2


@pytest.mark.parametrize("uri", ["https://external.example", "file:///tmp/example", "sqlite:///:memory:"])
def test_tracking_rejects_remote_or_ephemeral_storage(tmp_path, uri):
    with pytest.raises(ValueError, match="persistent local"):
        publish_comparison_metrics(tmp_path / "missing-summary.json", uri)
