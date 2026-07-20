"""
Cross-model leaderboards for a finished run, in four formats.

A run's ``summary.json`` is one object per model; comparing eight of them by eye
is what tables are for. The same ranking is emitted as json (machine-readable),
csv (spreadsheets), markdown (the repo's reports) and LaTeX (the paper), so a
number in the paper and a number in the report cannot drift apart -- they are
rendered from one ranking, computed once.

The headline table is a fixed short metric list; every other metric a run
recorded still reaches the json and csv, so nothing is silently dropped.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.runs import read_metadata, read_summary

# The headline table: enough to rank models, short enough to read.
TABLE_METRICS = (
    "main_score",
    "recall_at_10",
    "recall_at_100",
    "map_at_10",
    "map_at_100",
    "map",
    "ndcg_at_10",
    "ndcg_at_100",
    "same_language_irrelevant_share_at_100",
)

# Column order for the full json/csv export; anything else a run recorded is
# appended alphabetically (per-language diagnostics arrive that way).
COMPARISON_METRICS = (
    "main_score",
    "recall_at_10",
    "recall_at_20",
    "recall_at_50",
    "recall_at_100",
    "map_at_10",
    "map_at_20",
    "map_at_50",
    "map_at_100",
    "map",
    "ndcg_at_10",
    "ndcg_at_20",
    "ndcg_at_50",
    "ndcg_at_100",
    "mrr_at_10",
    "hit_rate_at_10",
    "hit_rate_at_100",
    "same_language_irrelevant_share_at_10",
    "same_language_irrelevant_share_at_20",
    "same_language_irrelevant_share_at_50",
    "same_language_irrelevant_share_at_100",
)

# Diagnostics where a smaller number is the better one, so "best" must not be a max.
LOWER_IS_BETTER_PREFIXES = ("same_language_irrelevant_share_at_",)

TIME_KEY = "evaluation_time_seconds"
MAIN_SCORE_KEY = "main_score"

METRIC_LABELS = {
    "main_score": "Main score",
    "map": "MAP",
    "same_language_irrelevant_share_at_100": "Same-lang irr@100",
}
_CUTOFF_NAMES = {"recall": "Recall", "map": "MAP", "ndcg": "nDCG", "mrr": "MRR", "hit_rate": "Hit"}
_CUTOFF_RE = re.compile(r"([a-z_]+)_at_(\d+)")


@dataclass(frozen=True)
class ModelScores:
    model_name: str
    main_score: float
    metrics: Mapping[str, float]
    evaluation_time_seconds: Optional[float]

    def value(self, metric: str) -> Optional[float]:
        if metric == MAIN_SCORE_KEY:
            return self.main_score
        return self.metrics.get(metric)


def build_comparison_tables(run_dir: str | Path, output_dir: str | Path) -> Path:
    """Render the leaderboard of ``run_dir`` into ``output_dir``. Returns that directory."""
    run_dir = Path(run_dir)
    output_dir = Path(output_dir)
    metadata = read_metadata(run_dir)
    ranked = sorted(_load_scores(run_dir), key=lambda item: item.main_score, reverse=True)
    if not ranked:
        raise ValueError(f"No model scores found in `{run_dir}` (looked for summary.json).")

    dataset_repo = str(metadata.get("dataset_repo", "") or "(unknown dataset)")
    metric_keys = _ordered_metric_keys(ranked)
    best = _best_values(ranked, TABLE_METRICS)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": metadata.get("run_id", run_dir.name),
        "dataset_repo": dataset_repo,
        "dataset_variant": metadata.get("dataset_variant", ""),
        "run_dir": str(run_dir),
        "metrics": list(metric_keys),
        "table_metrics": list(TABLE_METRICS),
        "models": [
            {
                "rank": index,
                "model_name": item.model_name,
                "main_score": item.main_score,
                TIME_KEY: item.evaluation_time_seconds,
                "metrics": {metric: item.value(metric) for metric in metric_keys},
            }
            for index, item in enumerate(ranked, start=1)
        ],
    }
    (output_dir / "model_comparison.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    corpus_io.write_rows(
        output_dir / "model_comparison.csv",
        (
            {
                "rank": index,
                "model_name": item.model_name,
                TIME_KEY: item.evaluation_time_seconds,
                **{metric: _blank_if_none(item.value(metric)) for metric in metric_keys},
            }
            for index, item in enumerate(ranked, start=1)
        ),
        ["rank", "model_name", TIME_KEY, *metric_keys],
    )

    (output_dir / "model_comparison.md").write_text(
        _markdown(dataset_repo, ranked, best), encoding="utf-8"
    )
    (output_dir / "model_comparison.tex").write_text(
        _latex(dataset_repo, ranked, best), encoding="utf-8"
    )
    return output_dir


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def _load_scores(run_dir: Path) -> list[ModelScores]:
    """Per-model scores from summary.json, falling back to the run metadata.

    The metadata carries the same scores, so a run whose summary was lost (or
    was never written because the process died after the metadata) still tables.
    """
    models: Any = read_summary(run_dir).get("models")
    if not models:
        models = read_metadata(run_dir).get("scores") or {}
    if isinstance(models, list):  # legacy shape: [{model_name, metrics}, ...]
        models = {
            str(item.get("model_name", "")): item.get("metrics") or {}
            for item in models
            if item.get("model_name")
        }
    scores: list[ModelScores] = []
    for name, raw in models.items():
        if not isinstance(raw, dict):  # a run may record a bare score per model
            continue
        metrics = {str(k): float(v) for k, v in raw.items() if isinstance(v, (int, float))}
        elapsed = metrics.pop(TIME_KEY, None)
        scores.append(
            ModelScores(
                model_name=str(name),
                main_score=float(metrics.get(MAIN_SCORE_KEY, 0.0)),
                metrics=metrics,
                evaluation_time_seconds=elapsed,
            )
        )
    return scores


def _ordered_metric_keys(ranked: Sequence[ModelScores]) -> list[str]:
    known = list(COMPARISON_METRICS)
    seen = set(known)
    return known + sorted({key for item in ranked for key in item.metrics if key not in seen})


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #

def _lower_is_better(metric: str) -> bool:
    return metric.startswith(LOWER_IS_BETTER_PREFIXES)


def _best_values(ranked: Sequence[ModelScores], metrics: Iterable[str]) -> dict[str, float]:
    best: dict[str, float] = {}
    for metric in metrics:
        values = [item.value(metric) for item in ranked]
        numeric = [value for value in values if value is not None]
        if numeric:
            best[metric] = min(numeric) if _lower_is_better(metric) else max(numeric)
    return best


def _metric_label(metric: str) -> str:
    if metric in METRIC_LABELS:
        return METRIC_LABELS[metric]
    match = _CUTOFF_RE.fullmatch(metric)
    if match:
        name, cutoff = match.groups()
        return f"{_CUTOFF_NAMES.get(name, name)}@{cutoff}"
    return metric


def _blank_if_none(value: Optional[float]) -> Any:
    return "" if value is None else value


def _format(value: Optional[float]) -> str:
    return "" if value is None else f"{value:.4f}"


def _elapsed(item: ModelScores, missing: str = "") -> str:
    return f"{item.evaluation_time_seconds:.1f}" if item.evaluation_time_seconds is not None else missing


def _cell(item: ModelScores, metric: str, best: Mapping[str, float], emphasis: str) -> str:
    value = item.value(metric)
    formatted = _format(value)
    if value is not None and best.get(metric) == value:
        return emphasis.format(formatted)
    return formatted


def _markdown(dataset_repo: str, ranked: Sequence[ModelScores], best: Mapping[str, float]) -> str:
    headers = [_metric_label(metric) for metric in TABLE_METRICS]
    lines = [
        "# Model comparison",
        "",
        "## Leaderboard",
        "",
        "### Overview",
        "",
        f"- Dataset: `{dataset_repo}`",
        f"- Models compared: `{len(ranked)}`",
        f"- Best model: `{ranked[0].model_name}` ({ranked[0].main_score:.4f})",
        "",
        "### Ranking",
        "",
        "| Rank | Model | " + " | ".join(headers) + " | Time (s) |",
        "| ---: | --- | " + " | ".join(["---:"] * len(headers)) + " | ---: |",
    ]
    for index, item in enumerate(ranked, start=1):
        cells = [
            str(index),
            f"`{item.model_name}`",
            *[_cell(item, metric, best, "**{}**") for metric in TABLE_METRICS],
            _elapsed(item),
        ]
        lines.append("| " + " | ".join(cells) + " |")

    lines += ["", "### Metric Winners", "", "| Metric | Best model | Score |", "| --- | --- | ---: |"]
    for metric in TABLE_METRICS:
        if metric not in best:
            continue
        winner = next(item for item in ranked if item.value(metric) == best[metric])
        lines.append(f"| `{_metric_label(metric)}` | `{winner.model_name}` | {best[metric]:.4f} |")
    return "\n".join(lines) + "\n"


def _latex(dataset_repo: str, ranked: Sequence[ModelScores], best: Mapping[str, float]) -> str:
    column_spec = "r l " + " ".join(["r"] * len(TABLE_METRICS)) + " r"
    headers = " & ".join(_latex_escape(_metric_label(metric)) for metric in TABLE_METRICS)
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        rf"\begin{{tabular}}{{{column_spec}}}",
        r"\hline",
        rf"Rank & Model & {headers} & Time (s) \\",
        r"\hline",
    ]
    for index, item in enumerate(ranked, start=1):
        cells = [
            str(index),
            r"\texttt{" + _latex_escape(item.model_name) + "}",
            *[_cell(item, metric, best, r"\textbf{{{}}}") for metric in TABLE_METRICS],
            _elapsed(item, missing="--"),
        ]
        lines.append(" & ".join(cells) + r" \\")
    lines += [
        r"\hline",
        r"\end{tabular}",
        rf"\caption{{Retrieval comparison on \texttt{{{_latex_escape(dataset_repo)}}}. "
        r"Bold marks the best score per metric.}}",
        r"\label{tab:model-comparison}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


def _latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


__all__ = ["COMPARISON_METRICS", "TABLE_METRICS", "ModelScores", "build_comparison_tables"]
