"""
Readers shared by every analysis: saved predictions and the dataset behind them.

Analyses never encode anything. They read the per-query rankings the evaluation
harness saved (``<run>/predictions/<model>/*_predictions.json``) and join them
against the benchmark's ``queries`` / ``corpus`` / ``qrels`` configs. Four
separate modules used to reach into a private ``_discover_models`` /
``_load_predictions`` / ``_load_config`` in each other; those three live here and
are public, because they are the interface between "a run on disk" and every
breakdown computed from it.

Nothing here knows what a document is about: column names are probed, not
assumed, so a dataset that predates a column simply loses that breakdown.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

from clir_bench.core.runs import slugify_model

# MTEB writes one such file per task inside the model's prediction folder.
PREDICTION_GLOB = "*_predictions.json"

VARIANTS = ("multilingual", "cross_language")


def normalize_variant(value: Optional[str]) -> str:
    """Canonical variant name, accepting the hyphenated spelling."""
    normalized = str(value or VARIANTS[0]).strip().lower().replace("-", "_")
    if normalized not in VARIANTS:
        raise ValueError(f"Unsupported dataset variant: {value}")
    return normalized


# --------------------------------------------------------------------------- #
# Saved predictions
# --------------------------------------------------------------------------- #

def discover_models(
    predictions_dir: Path, model_names: Optional[Sequence[str]] = None
) -> list[tuple[str, str]]:
    """Return ``[(label, slug)]`` for the models that actually have predictions.

    With ``model_names`` the labels are the real model ids (nicer in reports);
    without them the directory name is both label and slug. Either way a folder
    without a predictions file is dropped, so a model that crashed mid-run does
    not produce an empty column in every table.
    """
    predictions_dir = Path(predictions_dir)
    if not predictions_dir.is_dir():
        return []
    pairs: list[tuple[str, str]] = []
    if model_names:
        for name in model_names:
            for slug in (slugify_model(name), name):
                if (predictions_dir / slug).is_dir():
                    pairs.append((name, slug))
                    break
    else:
        pairs = [(child.name, child.name) for child in sorted(predictions_dir.iterdir()) if child.is_dir()]
    return [
        (label, slug)
        for label, slug in pairs
        if glob.glob(str(predictions_dir / slug / PREDICTION_GLOB))
    ]


def load_predictions(model_dir: Path) -> Optional[dict[str, dict[str, float]]]:
    """Merge one model's MTEB prediction JSON into ``{query_id: {doc_id: score}}``.

    The file is nested by subset and split; every split is merged because a run
    evaluates exactly one split, and keeping the nesting would push the same
    flattening into four callers.
    """
    files = glob.glob(str(Path(model_dir) / PREDICTION_GLOB))
    if not files:
        return None
    payload = json.loads(Path(files[0]).read_text(encoding="utf-8"))
    subsets = [key for key in payload if key != "mteb_model_meta"]
    if not subsets:
        return None
    merged: dict[str, dict[str, float]] = {}
    for subset in subsets:
        for split_preds in payload[subset].values():
            merged.update(split_preds)
    return merged


def ranked_docs(doc_scores: dict[str, float]) -> list[str]:
    """Document ids by descending score.

    Ties keep the order the retriever emitted them in (Python's sort is stable),
    which is what makes a re-analysis of the same predictions reproducible.
    """
    return [doc for doc, _ in sorted(doc_scores.items(), key=lambda kv: -kv[1])]


# --------------------------------------------------------------------------- #
# Dataset configs
# --------------------------------------------------------------------------- #

def dataset_config_name(
    dataset_repo: str, base_config: str, *, variant: str = VARIANTS[0], revision: str = "main"
) -> str:
    """Config name for one part of a benchmark, e.g. ``multilingual-qrels``.

    A dataset that ships a single variant exposes bare ``queries``/``corpus``/
    ``qrels`` configs, so the prefix is added only when the variant's qrels
    config actually exists.
    """
    subset = _resolve_subset(dataset_repo, revision, normalize_variant(variant))
    return f"{subset}-{base_config}" if subset is not None else base_config


def load_config(
    dataset: str, config: str, *, variant: str = VARIANTS[0], revision: str = "main"
):
    """Load one config of a benchmark from the Hub or a local dry-run export.

    The local branch keeps analyses runnable offline against a
    ``publish --dry-run`` directory, which is the only way to exercise them
    without network access.
    """
    from datasets import load_dataset

    path = Path(dataset)
    if path.is_dir():
        parquet = path / config / f"{config}.parquet"
        if not parquet.exists():
            parquet = path / f"{config}.parquet"
        return load_dataset("parquet", data_files=str(parquet), split="train")
    return load_dataset(
        dataset,
        dataset_config_name(dataset, config, variant=variant, revision=revision),
        split="train",
        revision=revision,
    )


def _resolve_subset(dataset_repo: str, revision: str, variant: str) -> Optional[str]:
    from datasets import get_dataset_config_names

    configs = set(get_dataset_config_names(dataset_repo, revision=revision))
    if f"{variant}-qrels" in configs:
        return variant
    if variant == VARIANTS[0]:
        return None
    raise ValueError(f"Dataset `{dataset_repo}` does not expose the `{variant}` retrieval variant.")


# --------------------------------------------------------------------------- #
# Column probing -- datasets differ in which names they use for the same thing
# --------------------------------------------------------------------------- #

def id_column(columns: Sequence[str], specific: str) -> str:
    """The id column: MTEB's ``_id``, else the dataset's own name, else column 0."""
    if "_id" in columns:
        return "_id"
    if specific in columns:
        return specific
    return columns[0] if columns else specific


def query_language_column(columns: Sequence[str]) -> Optional[str]:
    for name in ("query_language", "question_language", "language"):
        if name in columns:
            return name
    return None


def corpus_language_column(columns: Sequence[str]) -> Optional[str]:
    for name in ("corpus_language", "language"):
        if name in columns:
            return name
    return None


def first_column(columns: Sequence[str], *candidates: str) -> Optional[str]:
    """First candidate present in ``columns`` (for renamed/legacy columns)."""
    for name in candidates:
        if name in columns:
            return name
    return None


def mean(values: Iterable[Any]) -> float:
    """Arithmetic mean; NaN for an empty sequence so "no data" never reads as 0."""
    items = [float(v) for v in values]
    return sum(items) / len(items) if items else float("nan")


__all__ = [
    "PREDICTION_GLOB",
    "VARIANTS",
    "corpus_language_column",
    "dataset_config_name",
    "discover_models",
    "first_column",
    "id_column",
    "load_config",
    "load_predictions",
    "mean",
    "normalize_variant",
    "query_language_column",
    "ranked_docs",
]
