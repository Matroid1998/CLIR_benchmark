"""
Run registry.

Evaluations are repeated over months against changing datasets and model sets,
so every run records what it was: which dataset revision, which models, which
commit, which machine. The layout is a contract the analysis layer depends on::

    reports/runs/<run_id>/
        run_metadata.json     provenance
        summary.json          per-model scores
        predictions/<model>/  saved rankings (analysis re-runs from these)
        mteb_tables/          comparison tables
        question_analysis/    per-question breakdowns
    reports/runs/index.csv    one row per (run, model) -- the trend log
    reports/runs/latest       pointer to the newest run

Analysis is deliberately decoupled from evaluation: everything downstream reads
saved predictions, so re-analysing never re-runs a model.
"""

from __future__ import annotations

import csv
import json
import os
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

INDEX_FILENAME = "index.csv"
LATEST_POINTER = "latest"
METADATA_FILENAME = "run_metadata.json"
SUMMARY_FILENAME = "summary.json"

INDEX_COLUMNS = (
    "run_id",
    "created_at",
    "domain",
    "dataset_repo",
    "dataset_variant",
    "corpus_repo",
    "model",
    "main_score",
    "queries",
    "corpus",
    "git_commit",
)


def make_run_id(label: Optional[str] = None, *, now: Optional[datetime] = None) -> str:
    """Sortable UTC run id, optionally suffixed with a slugified label."""
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    if not label:
        return stamp
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", label).strip("-").lower()
    return f"{stamp}_{slug}" if slug else stamp


def git_info(project_root: Path) -> tuple[str, bool]:
    """Short commit hash and whether the tree is dirty."""
    def _git(*args: str) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    commit = _git("rev-parse", "--short", "HEAD") or ""
    status = _git("status", "--porcelain")
    return commit, bool(status)


def write_metadata(
    run_dir: Path,
    *,
    run_id: str,
    domain: str,
    created_at: str,
    dataset_repo: str,
    dataset_variant: str,
    corpus_repo: str,
    models: Sequence[str],
    scores: Mapping[str, Mapping[str, Any]],
    sizes: Mapping[str, int],
    project_root: Path,
    extra: Optional[Mapping[str, Any]] = None,
) -> Path:
    """Write ``run_metadata.json`` so a run can be interpreted months later."""
    commit, dirty = git_info(project_root)
    payload = {
        "run_id": run_id,
        "domain": domain,
        "created_at": created_at,
        "dataset_repo": dataset_repo,
        "dataset_variant": dataset_variant,
        "corpus_repo": corpus_repo,
        "models": list(models),
        "scores": {k: dict(v) for k, v in scores.items()},
        "sizes": dict(sizes),
        "git_commit": commit,
        "git_dirty": dirty,
        "hostname": platform.node(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID", ""),
        **(dict(extra) if extra else {}),
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / METADATA_FILENAME
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def read_metadata(run_dir: Path) -> dict[str, Any]:
    """Run metadata, or ``{}`` when absent.

    Lets an analysis command target whatever dataset the run used without the
    user having to re-specify it.
    """
    path = Path(run_dir) / METADATA_FILENAME
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def append_index(
    index_path: Path,
    *,
    run_id: str,
    domain: str,
    created_at: str,
    dataset_repo: str,
    dataset_variant: str,
    corpus_repo: str,
    scores: Mapping[str, Mapping[str, Any]],
    sizes: Mapping[str, int],
    git_commit: str,
    main_score_key: str = "main_score",
) -> None:
    """Append one row per model to the rolling trend log."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not index_path.exists()
    with index_path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(INDEX_COLUMNS), extrasaction="ignore")
        if is_new:
            writer.writeheader()
        for model, metrics in scores.items():
            writer.writerow(
                {
                    "run_id": run_id,
                    "created_at": created_at,
                    "domain": domain,
                    "dataset_repo": dataset_repo,
                    "dataset_variant": dataset_variant,
                    "corpus_repo": corpus_repo,
                    "model": model,
                    "main_score": metrics.get(main_score_key, ""),
                    "queries": sizes.get("queries", ""),
                    "corpus": sizes.get("corpus", ""),
                    "git_commit": git_commit,
                }
            )


def update_latest(runs_root: Path, run_id: str) -> None:
    """Point ``latest`` at a run (symlink, with a text file fallback)."""
    runs_root.mkdir(parents=True, exist_ok=True)
    pointer = runs_root / LATEST_POINTER
    try:
        if pointer.is_symlink() or pointer.exists():
            pointer.unlink()
        pointer.symlink_to(run_id, target_is_directory=True)
    except (OSError, NotImplementedError):
        (runs_root / "latest.txt").write_text(run_id, encoding="utf-8")


def resolve_run_dir(runs_root: Path, run: Optional[str] = None) -> Path:
    """Resolve a run reference: explicit path or id, else the latest run."""
    if run:
        candidate = Path(run)
        if candidate.exists():
            return candidate
        by_id = runs_root / run
        if by_id.exists():
            return by_id
        raise FileNotFoundError(f"no run found for {run!r} (looked in {runs_root})")
    latest = runs_root / LATEST_POINTER
    if latest.exists():
        return latest.resolve()
    pointer = runs_root / "latest.txt"
    if pointer.exists():
        return runs_root / pointer.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(f"no runs found under {runs_root}")


def list_runs(runs_root: Path) -> list[dict[str, Any]]:
    """Every run directory with its metadata, newest first."""
    if not runs_root.exists():
        return []
    runs = []
    for entry in sorted(runs_root.iterdir(), reverse=True):
        if not entry.is_dir() or entry.name == LATEST_POINTER:
            continue
        metadata = read_metadata(entry)
        runs.append(
            {
                "run_id": metadata.get("run_id", entry.name),
                "path": entry,
                "created_at": metadata.get("created_at", ""),
                "domain": metadata.get("domain", ""),
                "models": metadata.get("models", []),
                "dataset_repo": metadata.get("dataset_repo", ""),
            }
        )
    return runs


def write_summary(run_dir: Path, scores: Mapping[str, Mapping[str, Any]]) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / SUMMARY_FILENAME
    path.write_text(json.dumps({"models": dict(scores)}, indent=2), encoding="utf-8")
    return path


def read_summary(run_dir: Path) -> dict[str, Any]:
    path = Path(run_dir) / SUMMARY_FILENAME
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def slugify_model(name: str) -> str:
    """Filesystem-safe model directory name (``org/model`` -> ``org__model``)."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "__", name).strip("_")


__all__ = [
    "INDEX_COLUMNS",
    "INDEX_FILENAME",
    "append_index",
    "git_info",
    "list_runs",
    "make_run_id",
    "read_metadata",
    "read_summary",
    "resolve_run_dir",
    "slugify_model",
    "update_latest",
    "write_metadata",
    "write_summary",
]
