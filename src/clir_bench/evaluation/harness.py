"""
The retrieval evaluation harness.

One run evaluates several models against one benchmark and leaves behind
everything the analysis layer needs, so that no question is ever answered by
re-encoding a corpus. The shape of a run is defined in ``core.runs``; this module
fills it in.

Two decisions here are load-bearing:

**The benchmark is a custom MTEB task.** Queries and qrels are read from a Hub
repo that MTEB's static registry knows nothing about, which is why the task is
constructed at runtime and why its metadata sets ``prompt`` explicitly (see
:func:`build_task`).

**Retrieval happens against one shared haystack.** Each benchmark ships its own
small corpus, but scoring against it would make numbers from different benchmarks
incomparable -- a model looks strong when the distractors are few. So the corpus
config is replaced by a shared corpus repo, with any judged document missing from
it unioned back in, and every evaluation therefore searches the same documents.
Passing an empty ``corpus_repo`` opts back into the dataset's own corpus.

A model that fails to load or crashes mid-encode is reported and skipped rather
than losing the whole run: a set of models takes GPU-hours, and one gated
checkpoint should not cost the other results.
"""

from __future__ import annotations

import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from datasets import get_dataset_config_names, load_dataset

from clir_bench.core.context import AppContext
from clir_bench.core.domain import CorpusSchema
from clir_bench.core.runs import (
    INDEX_FILENAME,
    append_index,
    git_info,
    slugify_model,
    update_latest,
    write_metadata,
    write_summary,
)
from clir_bench.evaluation import metrics as metrics_engine
from clir_bench.evaluation import models as model_loading

DEFAULT_VARIANT = "multilingual"
VARIANTS = ("multilingual", "cross_language")
DEFAULT_MAIN_SCORE = "recall_at_10"
DEFAULT_REVISION = "main"

# Instruction handed to instruction-based models (Qwen3-Embedding, e5-instruct) for our
# CUSTOM Hub task. Set on TaskMetadata.prompt so MTEB's get_instruction() returns it
# directly instead of falling back to get_task(name) -- which KeyErrors because our task
# is not in MTEB's static registry. The value mirrors AbsTaskRetrieval.abstask_prompt, so
# behaviour matches a built-in retrieval task. Instruct wrappers apply it to queries only.
DEFAULT_RETRIEVAL_PROMPT = "Retrieve text based on user query."

# ISO-639-1 -> the ISO-639-3 + script tags MTEB validates ``eval_langs`` against.
# This is a property of MTEB's tagging, not of any domain; a domain that works in
# other languages supplies its own table through the ``mteb_language_codes``
# setting rather than editing this fallback.
MTEB_LANGUAGE_CODES: Mapping[str, str] = {
    "ar": "arb-Arab",
    "bg": "bul-Cyrl",
    "cs": "ces-Latn",
    "da": "dan-Latn",
    "de": "deu-Latn",
    "el": "ell-Grek",
    "en": "eng-Latn",
    "es": "spa-Latn",
    "et": "est-Latn",
    "fa": "pes-Arab",
    "fi": "fin-Latn",
    "fr": "fra-Latn",
    "hi": "hin-Deva",
    "hu": "hun-Latn",
    "it": "ita-Latn",
    "ja": "jpn-Jpan",
    "ko": "kor-Hang",
    "lt": "lit-Latn",
    "lv": "lav-Latn",
    "mt": "mlt-Latn",
    "nl": "nld-Latn",
    "pl": "pol-Latn",
    "pt": "por-Latn",
    "ro": "ron-Latn",
    "ru": "rus-Cyrl",
    "sk": "slk-Latn",
    "sl": "slv-Latn",
    "sv": "swe-Latn",
    "tr": "tur-Latn",
    "zh": "zho-Hans",
}


# --------------------------------------------------------------------------- #
# Dataset layout
# --------------------------------------------------------------------------- #

def _slug(value: str) -> str:
    """Slug used in MTEB task names.

    Deliberately not ``core.runs.slugify_model``: a task name ends up inside
    MTEB's own result paths and in every prediction file, so its spelling is
    frozen and must keep collapsing every non-alphanumeric run to a hyphen.
    """
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "default"


def normalize_variant(value: Optional[str]) -> str:
    normalized = str(value or DEFAULT_VARIANT).strip().lower().replace("-", "_")
    if normalized not in VARIANTS:
        raise ValueError(f"Unsupported dataset variant: {value}")
    return normalized


def resolve_dataset_subset(dataset_repo: str, revision: str, variant: str) -> Optional[str]:
    """Config-name prefix for a variant, or ``None`` for an unprefixed dataset.

    Older single-variant datasets expose bare ``queries``/``corpus``/``qrels``
    configs; newer ones prefix each with the variant. ``None`` selects the bare
    layout, which only the default variant can fall back to.
    """
    variant = normalize_variant(variant)
    dataset_configs = set(get_dataset_config_names(dataset_repo, revision=revision))
    if f"{variant}-qrels" in dataset_configs:
        return variant
    if variant == DEFAULT_VARIANT:
        return None
    raise ValueError(
        f"Dataset `{dataset_repo}` does not expose the `{variant}` retrieval variant."
    )


def dataset_config_name(
    dataset_repo: str,
    revision: str,
    variant: str,
    base_config: str,
) -> str:
    subset = resolve_dataset_subset(dataset_repo, revision, variant)
    return f"{subset}-{base_config}" if subset is not None else base_config


def query_language_column(column_names: Sequence[str]) -> Optional[str]:
    for name in ("query_language", "question_language", "language"):
        if name in column_names:
            return name
    return None


def corpus_language_column(column_names: Sequence[str]) -> Optional[str]:
    for name in ("corpus_language", "language"):
        if name in column_names:
            return name
    return None


def load_corpus_dataset(corpus_repo: str, revision: str):
    """Load a shared ``corpus`` config from a Hub repo or a local directory.

    Local directories use the dry-run export layout
    (``<dir>/corpus/corpus.parquet`` or ``<dir>/corpus.parquet``), so a shared
    haystack can be exercised entirely offline.
    """
    path = Path(corpus_repo)
    if path.is_dir():
        parquet = path / "corpus" / "corpus.parquet"
        if not parquet.exists():
            parquet = path / "corpus.parquet"
        corpus = load_dataset("parquet", data_files=str(parquet), split="train")
    else:
        config = dataset_config_name(corpus_repo, revision, DEFAULT_VARIANT, "corpus")
        corpus = load_dataset(corpus_repo, config, split="train", revision=revision)
    if "id" not in corpus.column_names and "_id" in corpus.column_names:
        corpus = corpus.rename_column("_id", "id")
    return corpus


def detect_query_languages(
    dataset_repo: str,
    revision: str,
    variant: str,
    language_codes: Mapping[str, str],
) -> list[str]:
    """MTEB language tags actually present in the benchmark's queries."""
    config = dataset_config_name(dataset_repo, revision, variant, "queries")
    queries = load_dataset(dataset_repo, config, split="train", revision=revision)
    column = query_language_column(list(queries.column_names))
    if column is None:
        return [language_codes["en"]]

    langs = sorted(
        {str(value).strip().lower() for value in queries[column] if str(value).strip()}
    )
    mapped = [language_codes[lang] for lang in langs if lang in language_codes]
    return mapped or [language_codes["en"]]


def dataset_sizes(dataset_repo: str, revision: str, variant: str) -> dict[str, int]:
    """Row counts for queries/corpus/qrels: a cheap content fingerprint of the run.

    ``-1`` marks a count that could not be read, so a metadata file always has
    the key and a missing size never aborts a finished evaluation.
    """
    sizes: dict[str, int] = {}
    for base in ("queries", "corpus", "qrels"):
        try:
            config = dataset_config_name(dataset_repo, revision, variant, base)
            sizes[base] = load_dataset(
                dataset_repo, config, split="train", revision=revision
            ).num_rows
        except Exception:
            sizes[base] = -1
    return sizes


# --------------------------------------------------------------------------- #
# The custom MTEB task
# --------------------------------------------------------------------------- #

_TASK_CLASS: Any = None


def _task_class() -> Any:
    """Define the task class on first use.

    It has to subclass ``mteb.abstasks.AbsTaskRetrieval``, and importing mteb at
    module level would drag torch into every CLI invocation.
    """
    global _TASK_CLASS
    if _TASK_CLASS is not None:
        return _TASK_CLASS

    from mteb.abstasks import AbsTaskRetrieval

    class HubDatasetRetrievalTask(AbsTaskRetrieval):
        """A retrieval task whose queries/qrels come from an arbitrary Hub repo."""

        def __init__(
            self,
            metadata: Any,
            *,
            dataset_repo: str,
            revision: str,
            dataset_variant: str,
            schema: CorpusSchema,
            corpus_repo: str = "",
            diagnostic_languages: Sequence[str] = (),
        ):
            self.metadata = metadata
            self.dataset_repo = dataset_repo
            # A shared haystack equal to the dataset's own repo is not a swap.
            self.corpus_repo = corpus_repo if corpus_repo and corpus_repo != dataset_repo else ""
            self.revision = revision
            self.dataset_variant = dataset_variant
            self.schema = schema
            self.diagnostic_languages = tuple(diagnostic_languages)
            self._query_language_by_id: Optional[dict[str, str]] = None
            self._corpus_language_by_id: Optional[dict[str, str]] = None
            super().__init__()

        def load_data(self, num_proc: Optional[int] = None, **kwargs: Any) -> None:
            if self.data_loaded:
                return
            with model_loading.offline_safe_loader_configs(self.dataset_repo, self.revision):
                super().load_data(num_proc=num_proc, **kwargs)
            if self.corpus_repo:
                self._swap_in_shared_corpus()

        def _swap_in_shared_corpus(self) -> None:
            """Replace each split's corpus with the shared haystack.

            Judged documents missing from the shared corpus are unioned in from
            the dataset's own corpus, so a gold or look-alike document stays
            retrievable even when a benchmark's qrels reference ids that were
            never published to the shared repo. Without that union a model would
            be scored on documents it could not possibly return.
            """
            from datasets import concatenate_datasets

            shared = load_corpus_dataset(self.corpus_repo, self.revision)
            keep = [c for c in ("id", "title", "text") if c in shared.column_names]
            shared = shared.select_columns(keep)
            shared_ids = set(shared["id"])
            for subset, splits in self.dataset.items():
                for split, data in splits.items():
                    judged: set[str] = set()
                    for docs in data["relevant_docs"].values():
                        judged.update(str(d) for d in docs)
                    missing = judged - shared_ids
                    corpus = shared
                    if missing:
                        own = data["corpus"]
                        extra = own.filter(lambda r: str(r["id"]) in missing).select_columns(
                            [c for c in keep if c in own.column_names]
                        )
                        corpus = concatenate_datasets([shared, extra])
                        print(
                            f"[corpus] {subset}/{split}: unioned {len(extra)} judged doc(s) "
                            f"missing from {self.corpus_repo}"
                        )
                    data["corpus"] = corpus
            print(f"[corpus] retrieval haystack = {self.corpus_repo} ({len(shared_ids)} docs)")

        def _language_by_id(
            self, base_config: str, pick_column, id_fallback: str
        ) -> dict[str, str]:
            config = dataset_config_name(
                self.dataset_repo, self.revision, self.dataset_variant, base_config
            )
            data = load_dataset(
                self.dataset_repo, config, split="train", revision=self.revision
            )
            column = pick_column(list(data.column_names))
            if column is None:
                return {}
            id_column = "_id" if "_id" in data.column_names else id_fallback
            mapping: dict[str, str] = {}
            for row in data:
                row_id = str(row.get(id_column, "") or "").strip()
                language = str(row.get(column, "") or "").strip().lower()
                # Rows with no language are simply left out: the metric engine
                # falls back to the domain's id convention for anything absent.
                if row_id and language:
                    mapping[row_id] = language
            return mapping

        def _get_query_language_by_id(self) -> dict[str, str]:
            if self._query_language_by_id is None:
                self._query_language_by_id = self._language_by_id(
                    "queries", query_language_column, "query_id"
                )
            return self._query_language_by_id

        def _get_corpus_language_by_id(self) -> dict[str, str]:
            if self._corpus_language_by_id is None:
                self._corpus_language_by_id = self._language_by_id(
                    "corpus", corpus_language_column, "corpus_id"
                )
            return self._corpus_language_by_id

        def task_specific_scores(
            self,
            scores: dict[str, dict[str, float]],
            qrels: dict[str, dict[str, Any]],
            results: dict[str, dict[str, float]],
            hf_split: str,
            hf_subset: str,
        ) -> dict[str, float]:
            del scores, hf_split, hf_subset
            return metrics_engine.compute_retrieval_metrics(
                results=results,
                qrels=qrels,
                schema=self.schema,
                query_languages=self._get_query_language_by_id(),
                corpus_languages=self._get_corpus_language_by_id(),
                diagnostic_languages=self.diagnostic_languages,
            )

    _TASK_CLASS = HubDatasetRetrievalTask
    return _TASK_CLASS


def task_name(dataset_repo: str, variant: str) -> str:
    owner, _, name = dataset_repo.partition("/")
    return f"{_slug(owner or 'hf')}_{_slug(name or dataset_repo)}_{_slug(variant)}_retrieval"


def build_task(
    dataset_repo: str,
    *,
    schema: CorpusSchema,
    revision: str = DEFAULT_REVISION,
    variant: str = DEFAULT_VARIANT,
    corpus_repo: str = "",
    diagnostic_languages: Sequence[str] = (),
    language_codes: Optional[Mapping[str, str]] = None,
    task_domains: Sequence[str] = (),
    subject: str = "",
    main_score: str = DEFAULT_MAIN_SCORE,
) -> Any:
    """Build the MTEB task for one benchmark repo and variant."""
    from mteb.abstasks.task_metadata import TaskMetadata

    variant = normalize_variant(variant)
    codes = language_codes or MTEB_LANGUAGE_CODES
    subset = resolve_dataset_subset(dataset_repo, revision, variant)
    eval_langs = detect_query_languages(dataset_repo, revision, variant, codes)
    described = f" ({subject})" if subject else ""
    metadata = TaskMetadata(
        name=task_name(dataset_repo, variant),
        dataset={"path": dataset_repo, "revision": revision},
        description=(
            f"Custom {variant.replace('_', '-')} retrieval evaluation over the "
            f"dataset `{dataset_repo}`{described}. Cross-lingual relevance treats every "
            f"corpus document sharing a question's {schema.family_field} as a positive."
        ),
        reference=f"https://huggingface.co/datasets/{dataset_repo}",
        type="Retrieval",
        category="t2t",
        modalities=["text"],
        eval_splits=["train"],
        eval_langs={subset or "default": eval_langs},
        main_score=main_score,
        prompt=DEFAULT_RETRIEVAL_PROMPT,  # short-circuits get_instruction() -> no registry KeyError
        domains=list(task_domains) or None,
        task_subtypes=["Question Answering Retrieval"],
        license="not specified",
        annotations_creators="LM-generated and reviewed",
        sample_creation="LM-generated and verified",
        is_public=True,
        contributed_by="clir-bench",
    )
    return _task_class()(
        metadata,
        dataset_repo=dataset_repo,
        revision=revision,
        dataset_variant=variant,
        schema=schema,
        corpus_repo=corpus_repo,
        diagnostic_languages=diagnostic_languages,
    )


# --------------------------------------------------------------------------- #
# Running an evaluation
# --------------------------------------------------------------------------- #

def _numeric_metrics(result: Any) -> dict[str, float]:
    """Flatten one MTEB TaskResult to its numeric scores (first scored subset)."""
    metrics: dict[str, float] = {}
    for split_rows in result.scores.values():
        for row in split_rows:
            for key, value in row.items():
                if key in {"hf_subset", "languages"}:
                    continue
                if isinstance(value, (int, float)):
                    metrics[key] = float(value)
            if metrics:
                return metrics
    return metrics


def run_evaluation(
    models: Sequence[str],
    dataset_repo: str,
    corpus_repo: str,
    variant: str,
    run_dir: Path,
    run_id: str,
    batch_size: int,
    context: AppContext,
    *,
    revision: str = DEFAULT_REVISION,
) -> dict[str, dict[str, Any]]:
    """Evaluate ``models`` and write a complete run directory.

    Returns model id -> metrics (including ``main_score``), which is also what
    lands in ``summary.json``. Models that fail are absent from both.
    """
    from mteb import MTEB

    if not models:
        raise ValueError("Provide at least one model for evaluation.")

    variant = normalize_variant(variant)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    prediction_dir = run_dir / "predictions"
    created_at = datetime.now(timezone.utc).isoformat()

    task = build_task(
        dataset_repo,
        schema=context.schema,
        revision=revision,
        variant=variant,
        corpus_repo=corpus_repo,
        diagnostic_languages=context.domain.analysis.diagnostic_languages,
        language_codes=context.setting("mteb_language_codes", None),
        task_domains=context.setting("mteb_task_domains", ()) or (),
        subject=context.domain.title,
        main_score=context.settings.eval.main_score or DEFAULT_MAIN_SCORE,
    )
    evaluator = MTEB(tasks=[task])
    cache_dir = model_loading.configure_hf_cache(context.project_root)
    eval_languages = detect_query_languages(
        dataset_repo,
        revision,
        variant,
        context.setting("mteb_language_codes", None) or MTEB_LANGUAGE_CODES,
    )

    # Load queries/qrels (and swap in the shared haystack) once, up front, so a
    # dataset or corpus error fails fast and clearly instead of being swallowed
    # by the per-model resilience loop below -- and so every model is scored
    # against exactly the same documents.
    try:
        task.load_data()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load evaluation data (dataset_repo={dataset_repo}, "
            f"corpus_repo={corpus_repo or dataset_repo}). If using the shared haystack, "
            "publish it first with `clir publish corpus`, or pass --corpus-repo '' to use "
            f"the dataset's own corpus. Original error: {exc}"
        ) from exc

    scores: dict[str, dict[str, Any]] = {}
    failed: list[tuple[str, str]] = []
    for model_name in models:
        print(f"Evaluating `{model_name}` on `{dataset_repo}` ({variant})...")
        try:
            model, _model_meta = model_loading.load_model(
                model_name,
                cache_dir=cache_dir,
                meta_factory=evaluator.create_model_meta,
            )
            results = evaluator.run(
                model,
                verbosity=2,
                output_folder=str(run_dir),
                eval_splits=["train"],
                overwrite_results=True,
                encode_kwargs={"batch_size": batch_size},
                # Per-query rankings, one folder per model. Every downstream
                # analysis reads these, so nothing re-encodes a corpus.
                prediction_folder=prediction_dir / slugify_model(model_name),
            )
            if not results:
                raise ValueError(f"MTEB returned no results for model `{model_name}`.")

            result = results[0]
            entry: dict[str, Any] = dict(_numeric_metrics(result))
            entry["main_score"] = float(result.main_score)
            entry["evaluation_time_seconds"] = result.evaluation_time
            scores[model_name] = entry
        except Exception as exc:  # noqa: BLE001 - resilience: skip the model, keep going
            failed.append((model_name, f"{type(exc).__name__}: {exc}"))
            print(
                f"\n[WARNING] Skipping `{model_name}` — evaluation failed: "
                f"{type(exc).__name__}: {exc}"
            )
            traceback.print_exc()
            print()

    if failed:
        print(f"\n{len(failed)} model(s) skipped due to errors:")
        for name, error in failed:
            print(f"  - {name}: {error}")

    # A tidy (query, document, rank, score, relevance) table alongside the raw
    # prediction JSON. Written here rather than on demand because it is what
    # later metrics are computed from, and recomputing it needs the dataset the
    # run was scored against -- which is only unambiguous at run time.
    if scores:
        try:
            from clir_bench.analysis.rankings import save_scored_rankings

            save_scored_rankings(
                run_dir / "predictions",
                run_dir / "retrieval_results",
                dataset_repo=dataset_repo,
                variant=variant,
                schema=context.schema,
                model_names=list(scores),
                revision=revision,
                concept_columns=context.setting("concept_columns", ("concept_id",)),
            )
        except Exception as exc:  # noqa: BLE001 - a reporting extra must not fail the run
            print(f"[rankings export skipped] {exc}")

    sizes = dataset_sizes(dataset_repo, revision, variant)
    write_summary(run_dir, scores)
    write_metadata(
        run_dir,
        run_id=run_id,
        domain=context.domain.name,
        created_at=created_at,
        dataset_repo=dataset_repo,
        dataset_variant=variant,
        corpus_repo=corpus_repo or dataset_repo,
        models=list(models),
        scores=scores,
        sizes=sizes,
        project_root=context.project_root,
        extra={
            "dataset_revision": revision,
            "batch_size": batch_size,
            "eval_languages": eval_languages,
            "failed_models": {name: error for name, error in failed},
        },
    )

    if not scores:
        print("\n[WARNING] No model evaluated successfully; the run was not indexed.")
        return scores

    # The rolling trend log and the `latest` pointer describe the managed runs
    # tree only, so an evaluation written elsewhere stays an unindexed one-off.
    runs_root = context.workspace.runs_dir
    if run_dir.resolve().parent == Path(runs_root).resolve():
        commit, _dirty = git_info(context.project_root)
        append_index(
            Path(runs_root) / INDEX_FILENAME,
            run_id=run_id,
            domain=context.domain.name,
            created_at=created_at,
            dataset_repo=dataset_repo,
            dataset_variant=variant,
            corpus_repo=corpus_repo or dataset_repo,
            scores=scores,
            sizes=sizes,
            git_commit=commit,
            main_score_key="main_score",
        )
        update_latest(Path(runs_root), run_id)
    return scores


__all__ = [
    "DEFAULT_MAIN_SCORE",
    "DEFAULT_RETRIEVAL_PROMPT",
    "DEFAULT_VARIANT",
    "MTEB_LANGUAGE_CODES",
    "VARIANTS",
    "build_task",
    "dataset_config_name",
    "dataset_sizes",
    "detect_query_languages",
    "load_corpus_dataset",
    "normalize_variant",
    "query_language_column",
    "corpus_language_column",
    "resolve_dataset_subset",
    "run_evaluation",
    "task_name",
]
