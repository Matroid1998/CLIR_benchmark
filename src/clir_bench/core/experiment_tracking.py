"""Publish completed comparison metrics to the account-free local MLflow database.

The file report remains authoritative. Only numeric aggregates and prompt version
references are logged; prompt text, source passages, and generated questions are not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from pathlib import Path
from urllib.parse import urlsplit


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _metric_component(value):
    return re.sub(r"[^A-Za-z0-9_. /-]", "_", str(value))


def version_metrics(data, version):
    """Flatten report aggregates without assigning values to missing scores/costs."""
    values = {}
    tables = (("routing", "routing", ("corpus", "backend", "mode")),
              ("mode_summary", "mode", ("corpus", "mode")),
              ("selected_summary", "selected", ("corpus", "backend")),
              ("usage", "usage", ("stage", "model")))
    for table, prefix, dimensions in tables:
        for row in data.get(table, []):
            if row.get("version") != version:
                continue
            namespace = "/".join([prefix, *(_metric_component(row.get(key, "unknown"))
                                            for key in dimensions)])
            for field, value in row.items():
                if field in (*dimensions, "version"):
                    continue
                name = namespace + "/" + field
                if value is None:
                    values[name + "__available"] = 0.0
                elif isinstance(value, (int, float)) and math.isfinite(value):
                    values[name] = float(value)
                    if field.endswith("_mean") or field in ("total_cost", "reported_cost_subtotal"):
                        values[name + "__available"] = 1.0
    values["evaluation/common_available"] = float(data.get("common_evaluation", {}).get("available", False))
    return values


def _version_references(data, version, experiment_root):
    registry = data.get("run_configs", {}).get(version, {}).get("prompt_registry")
    # Original baseline runs are immutable; their subsequent registration is stored beside them.
    manifest_path = experiment_root / version / "manifest.json"
    if registry is None and manifest_path.exists():
        from .prompt_registry import validate_manifest
        registry = validate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
    if not registry:
        return {"registered": False, "prompts": {}}
    return {"registered": True,
            **{key: registry.get(key) for key in ("provider", "bundle", "label", "registry_uri", "bundle_sha256")},
            "prompts": {key: {field: entry.get(field) for field in ("name", "version", "sha256")}
                        for key, entry in registry.get("prompts", {}).items()}}


def publish_comparison_metrics(summary_path, registry_uri, *, experiment_root=None):
    """Idempotently log each version as one MLflow run, using only a local SQLite URI."""
    if not registry_uri.startswith("sqlite:///") or registry_uri == "sqlite:///:memory:":
        raise ValueError("Comparison tracking requires a persistent local sqlite:/// database")
    database = Path(registry_uri[len("sqlite:///"):]).expanduser().resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    registry_uri = "sqlite:///" + str(database)
    try:
        from mlflow import MlflowClient
        from mlflow.entities import Metric, RunTag
    except ImportError:
        raise RuntimeError("Install local tracking with uv sync --extra prompts") from None
    summary_path = Path(summary_path).resolve()
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    if not data.get("verification", {}).get("identical_selections"):
        raise ValueError("Refusing to track an unverified comparison")
    default_root = summary_path.parent.parent if summary_path.parent.name == "comparison" else summary_path.parent
    experiment_root = Path(experiment_root or default_root).resolve()
    root_hash = _hash(str(experiment_root))
    client = MlflowClient(tracking_uri=registry_uri, registry_uri=registry_uri)
    experiment_name = f"clir/legal/{experiment_root.name}-{root_hash[:12]}"
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        artifact_root = database.parent / "comparison_artifacts" / root_hash
        experiment_id = client.create_experiment(
            experiment_name, artifact_location=artifact_root.as_uri(),
            tags={"clir.experiment_root": str(experiment_root), "clir.root_sha256": root_hash})
    else:
        artifact_uri = urlsplit(experiment.artifact_location or "")
        if artifact_uri.scheme not in ("", "file") or artifact_uri.netloc not in ("", "localhost"):
            raise ValueError("Existing experiment has a remote artifact store; local tracking refused")
        experiment_id = experiment.experiment_id
    report_hash = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    result = {}
    for version in data.get("run_configs", {}):
        metrics = version_metrics(data, version)
        references = _version_references(data, version, experiment_root)
        common_config = data.get("common_evaluation", {}).get("config")
        snapshot = {"version": version, "metrics": metrics, "prompt_versions": references,
                    "common_evaluation_config": common_config,
                    "selection_sha256": data["verification"].get("selection_sha256")}
        snapshot_hash, run_key = _hash(snapshot), _hash([str(experiment_root), version])
        matches = client.search_runs([experiment_id], filter_string=f"tags.`clir.run_key` = '{run_key}'",
                                     max_results=2)
        if len(matches) > 1:
            raise ValueError(f"Multiple MLflow runs match version {version}; resolve duplicates before publishing")
        run = matches[0] if matches else client.create_run(experiment_id, run_name=version,
            tags={"clir.run_key": run_key, "clir.experiment_root": str(experiment_root),
                  "clir.version": version, "clir.root_sha256": root_hash})
        run_id = run.info.run_id
        result[version] = run_id
        if run.data.tags.get("clir.metrics_snapshot_sha256") == snapshot_hash:
            continue
        step = int(run.data.tags.get("clir.metrics_revision", "-1")) + 1
        tags = {"clir.bundle": str(references.get("bundle") or "unregistered"),
                "clir.bundle_sha256": str(references.get("bundle_sha256") or ""),
                "clir.prompt_refs_sha256": _hash(references),
                "clir.selection_sha256": str(data["verification"].get("selection_sha256") or ""),
                "clir.report_path": str(summary_path), "clir.report_sha256": report_hash,
                "clir.metrics_revision": str(step),
                "clir.common_evaluation_available": str(data.get("common_evaluation", {}).get("available", False)).lower()}
        timestamp = int(time.time() * 1000)
        records = [Metric(key, value, timestamp, step) for key, value in sorted(metrics.items())]
        # Stay below the public API's batch limits even if later reports add more metrics.
        for start in range(0, len(records), 500):
            client.log_batch(run_id, metrics=records[start:start + 500], synchronous=True)
        client.log_batch(run_id, tags=[RunTag(key, value) for key, value in tags.items()], synchronous=True)
        client.log_dict(run_id, references, "prompt_versions.json")
        client.log_dict(run_id, snapshot, "metric_snapshot.json")
        client.set_terminated(run_id, status="FINISHED")
        # Commit marker last: interrupted publication can be retried against the same run.
        client.set_tag(run_id, "clir.metrics_snapshot_sha256", snapshot_hash, synchronous=True)
    return {"registry_uri": registry_uri, "experiment_id": experiment_id,
            "experiment_name": experiment_name, "runs": result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--mlflow-registry-uri", required=True)
    parser.add_argument("--experiment-root", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(publish_comparison_metrics(args.summary, args.mlflow_registry_uri,
                                              experiment_root=args.experiment_root), indent=2))


if __name__ == "__main__":
    main()
