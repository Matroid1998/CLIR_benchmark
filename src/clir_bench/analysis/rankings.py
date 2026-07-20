"""
The run's rankings as one tidy table, ready for metrics nobody has written yet.

The evaluation saves raw MTEB prediction JSON: nested ``{query: {doc: score}}``
with no language and no relevance attached. That is enough to recompute
anything, but every new question has to re-do the same join. This does the join
once -- predictions x queries x corpus x qrels, no re-encoding -- and writes one
flat parquet with a row per ranked (query, document) pair.

From it, CLIR@k is a groupby: recall@k over the gold documents whose
``corpus_language`` differs from ``query_language``. Datasets without labelled
hard negatives simply never produce that relevance value.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence

from clir_bench.core.domain import CorpusSchema
from clir_bench.analysis.predictions import (
    corpus_language_column,
    discover_models,
    first_column,
    id_column,
    load_config,
    load_predictions,
    normalize_variant,
    query_language_column,
)

RANKINGS_NAME = "scored_rankings.parquet"
DEFAULT_TOP_K = 1000

COLUMNS = (
    "model", "query_id", "query_language", "concept_id",
    "rank", "corpus_id", "corpus_language", "score", "relevance",
)

_README = """# Retrieval results (embedding-model rankings)

`scored_rankings.parquet` — one row per ranked (query, document) pair, top-K per query per model.

Columns:
- `model` — embedding model name
- `query_id`, `query_language`, `concept_id` — the query and the concept it asks about
- `rank` (1 = top), `corpus_id`, `corpus_language`, `score` (cosine, higher = better)
- `relevance` — `gold` (a right document), `hard_negative` (a labelled look-alike), or `` (not judged)

Compute @k metrics by filtering `rank <= k`. CLIR@k (cross-lingual recall@k) = of the gold
documents whose `corpus_language != query_language`, the fraction with `rank <= k`.
"""


def save_scored_rankings(
    predictions_dir: str | Path,
    output_dir: str | Path,
    *,
    dataset_repo: str,
    variant: str = "multilingual",
    schema: CorpusSchema,
    model_names: Optional[Sequence[str]] = None,
    revision: str = "main",
    top_k: int = DEFAULT_TOP_K,
    concept_columns: Sequence[str] = ("concept_id",),
) -> Optional[Path]:
    """Write ``scored_rankings.parquet``; ``None`` when the run saved no predictions."""
    from datasets import Dataset

    predictions_dir = Path(predictions_dir)
    output_dir = Path(output_dir)
    variant = normalize_variant(variant)

    models = discover_models(predictions_dir, model_names)
    if not models:
        print(f"[retrieval results skipped] no predictions under {predictions_dir}")
        return None

    queries = load_config(dataset_repo, "queries", variant=variant, revision=revision)
    corpus = load_config(dataset_repo, "corpus", variant=variant, revision=revision)
    qrels = load_config(dataset_repo, "qrels", variant=variant, revision=revision)

    query_columns = list(queries.column_names)
    qid_col = id_column(query_columns, "query_id")
    q_lang_col = query_language_column(query_columns)
    # `concept_id` is the portable name; a published dataset may use its own
    # ontology's column instead, which the caller passes in.
    concept_col = first_column(query_columns, *concept_columns)
    query_language = {
        str(row[qid_col]): (str(row.get(q_lang_col) or "").strip().lower() if q_lang_col else "")
        for row in queries
    }
    query_concept = (
        {str(row[qid_col]): str(row.get(concept_col) or "") for row in queries} if concept_col else {}
    )

    corpus_columns = list(corpus.column_names)
    cid_col = id_column(corpus_columns, "corpus_id")
    c_lang_col = corpus_language_column(corpus_columns)
    corpus_language = {
        str(row[cid_col]): (
            (str(row.get(c_lang_col) or "").strip().lower() if c_lang_col else "")
            or schema.language_from_doc_id(str(row[cid_col]))
        )
        for row in corpus
    }

    relevance = {
        (str(row["query-id"]), str(row["corpus-id"])): (
            "gold" if float(row["score"]) > 0 else "hard_negative"
        )
        for row in qrels
    }

    rows: list[dict[str, Any]] = []
    for label, slug in models:
        preds = load_predictions(predictions_dir / slug)
        if preds is None:
            continue
        for query_id, doc_scores in preds.items():
            ranked = sorted(doc_scores.items(), key=lambda kv: -kv[1])[:top_k]
            language = query_language.get(query_id, "")
            concept = query_concept.get(query_id, "")
            for rank, (doc, score) in enumerate(ranked, start=1):
                rows.append({
                    "model": label,
                    "query_id": query_id,
                    "query_language": language,
                    "concept_id": concept,
                    "rank": rank,
                    "corpus_id": doc,
                    # Shared-haystack distractors need not be in the benchmark's
                    # own corpus config; their ids encode the language, so the
                    # schema's id convention is the fallback.
                    "corpus_language": corpus_language.get(doc) or schema.language_from_doc_id(doc),
                    "score": round(float(score), 6),
                    "relevance": relevance.get((query_id, doc), ""),
                })

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / RANKINGS_NAME
    Dataset.from_list(rows).to_parquet(str(path))
    (output_dir / "README.md").write_text(_README, encoding="utf-8")
    print(f"Saved {len(rows)} ranked (query, doc) rows for {len(models)} model(s) -> {path}")
    return path


__all__ = ["COLUMNS", "RANKINGS_NAME", "save_scored_rankings"]
