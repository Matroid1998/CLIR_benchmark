"""
"How often does a labelled look-alike beat the right document?" -- per language.

This is the analysis a hard-negative benchmark is built for. Each query has gold
documents (score 1) and, when the dataset ships them, labelled hard negatives
(score 0): documents chosen to be confusable with the gold ones. Given a
retriever's saved rankings, we ask whether a hard negative ranks above *every*
gold document. Aggregated per query language, that is the confusion rate.

It reads the predictions the standard run already saved, so it costs no
encoding and lands in the same ``reports/runs/<id>/`` folder as the standard
metrics. The optional ``hard_negatives`` config supplies a human-readable label
per (query, document) pair, which is what makes the "most frequent confusions"
table interpretable.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.domain import CorpusSchema
from clir_bench.analysis.predictions import (
    discover_models,
    id_column,
    load_config,
    load_predictions,
    normalize_variant,
    query_language_column,
    ranked_docs,
)

SUMMARY_NAME = "summary.md"
PER_QUERY_NAME = "per_query.csv"
BY_LANGUAGE_NAME = "confusion_by_language.csv"

PER_QUERY_COLUMNS = (
    "model", "query_id", "query_language", "concept_name",
    "best_gold_rank", "best_hardneg_rank", "win",
    "top_neighbor_name", "top_relation",
)
BY_LANGUAGE_COLUMNS = (
    "model", "query_language", "n_queries", "n_wins", "confusion_rate",
    "mean_best_gold_rank", "mean_best_hardneg_rank",
)

_INF = float("inf")
_MAX_CONFUSIONS = 30


def _first_value(row: Mapping[str, Any], columns: Sequence[str]) -> str:
    """First non-empty value among ``columns``.

    Published datasets name the look-alike concept differently depending on the
    ontology they were built from, so the caller supplies the candidates rather
    than this module knowing any of them.
    """
    for column in columns:
        value = str(row.get(column, "") or "").strip()
        if value:
            return value
    return ""


def analyze_confusion(
    predictions_dir: str | Path,
    output_dir: str | Path,
    *,
    dataset_repo: str,
    variant: str = "multilingual",
    schema: CorpusSchema,
    make_plots: bool = True,
    model_names: Optional[Sequence[str]] = None,
    revision: str = "main",
    negative_name_columns: Sequence[str] = ("neighbor_name",),
) -> Path:
    """Write the confusion report. Returns the path to the markdown summary."""
    predictions_dir = Path(predictions_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    variant = normalize_variant(variant)

    models = discover_models(predictions_dir, model_names)
    if not models:
        raise ValueError(
            f"No per-query predictions under {predictions_dir}. Run the evaluation with "
            "prediction saving enabled first."
        )

    queries = load_config(dataset_repo, "queries", variant=variant, revision=revision)
    qrels = load_config(dataset_repo, "qrels", variant=variant, revision=revision)
    try:
        hard_negatives = load_config(dataset_repo, "hard_negatives", variant=variant, revision=revision)
    except Exception:
        hard_negatives = []  # dataset ships no hard-negative labels

    columns = list(queries.column_names)
    qid_col = id_column(columns, "query_id")
    lang_col = query_language_column(columns)
    query_lang: dict[str, str] = {}
    query_concept: dict[str, str] = {}
    for row in queries:
        qid = str(row[qid_col])
        lang = str(row.get(lang_col) or "").strip().lower() if lang_col else ""
        query_lang[qid] = lang or schema.language_from_doc_id(qid)
        query_concept[qid] = str(row.get("concept_name", "") or "")

    gold: dict[str, set[str]] = defaultdict(set)
    negatives: dict[str, set[str]] = defaultdict(set)
    for row in qrels:
        target = gold if float(row["score"]) > 0 else negatives
        target[str(row["query-id"])].add(str(row["corpus-id"]))
    labels = {
        (str(row["query-id"]), str(row["corpus-id"])): {
            "name": _first_value(row, negative_name_columns),
            "relation": row.get("relation", ""),
        }
        for row in hard_negatives
    }

    per_query: list[dict[str, Any]] = []
    for label, slug in models:
        preds = load_predictions(predictions_dir / slug)
        if preds is None:
            continue
        for qid, gold_docs in gold.items():
            negative_docs = negatives.get(qid)
            if not gold_docs or not negative_docs or qid not in preds:
                continue
            rank = {doc: i + 1 for i, doc in enumerate(ranked_docs(preds[qid]))}
            best_gold = min((rank.get(doc, _INF) for doc in gold_docs), default=_INF)
            best_negative_doc = sorted(negative_docs, key=lambda doc: rank.get(doc, _INF))[0]
            best_negative = rank.get(best_negative_doc, _INF)
            if best_gold == _INF and best_negative == _INF:
                continue  # neither side retrieved -- no signal either way
            win = best_negative < best_gold
            annotation = labels.get((qid, best_negative_doc), {}) if win else {}
            per_query.append({
                "model": label,
                "query_id": qid,
                "query_language": query_lang.get(qid, ""),
                "concept_name": query_concept.get(qid, ""),
                "best_gold_rank": best_gold if best_gold != _INF else "",
                "best_hardneg_rank": best_negative if best_negative != _INF else "",
                "win": int(win),
                "top_neighbor_name": annotation.get("name", ""),
                "top_relation": annotation.get("relation", ""),
            })

    return _write(output_dir, per_query, [label for label, _ in models], make_plots)


def _write(
    output_dir: Path, per_query: list[dict[str, Any]], models: Sequence[str], make_plots: bool
) -> Path:
    if per_query:
        corpus_io.write_rows(output_dir / PER_QUERY_NAME, per_query, PER_QUERY_COLUMNS)

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in per_query:
        grouped[(row["model"], row["query_language"])].append(row)
        grouped[(row["model"], "ALL")].append(row)

    rows: list[dict[str, Any]] = []
    for (model, lang), items in sorted(grouped.items()):
        n = len(items)
        wins = sum(row["win"] for row in items)
        gold_ranks = [row["best_gold_rank"] for row in items if isinstance(row["best_gold_rank"], (int, float))]
        negative_ranks = [
            row["best_hardneg_rank"] for row in items if isinstance(row["best_hardneg_rank"], (int, float))
        ]
        rows.append({
            "model": model,
            "query_language": lang,
            "n_queries": n,
            "n_wins": wins,
            "confusion_rate": round(wins / n, 4) if n else 0.0,
            "mean_best_gold_rank": round(sum(gold_ranks) / len(gold_ranks), 2) if gold_ranks else "",
            "mean_best_hardneg_rank": (
                round(sum(negative_ranks) / len(negative_ranks), 2) if negative_ranks else ""
            ),
        })
    corpus_io.write_rows(output_dir / BY_LANGUAGE_NAME, rows, BY_LANGUAGE_COLUMNS)

    languages = sorted({row["query_language"] for row in per_query if row["query_language"]})
    by_key = {(row["model"], row["query_language"]): row for row in rows}
    lines = [
        "# Confusion analysis — does a labelled look-alike beat the right document?",
        "",
        "Confusion rate = fraction of queries where a hard negative ranks above every gold document.",
        "",
        "| model | " + " | ".join(languages) + " | ALL |",
        "| --- | " + " | ".join(["---:"] * (len(languages) + 1)) + " |",
    ]
    for model in models:
        cells = [
            (f"{by_key[(model, lang)]['confusion_rate']:.1%} (n={by_key[(model, lang)]['n_queries']})"
             if (model, lang) in by_key else "—")
            for lang in [*languages, "ALL"]
        ]
        lines.append(f"| `{model}` | " + " | ".join(cells) + " |")

    confusions = Counter(
        (row["concept_name"], row["top_neighbor_name"], row["top_relation"])
        for row in per_query
        if row["win"] and row["top_neighbor_name"]
    )
    lines += ["", "## Most frequent confusions (winning look-alike, all models)", ""]
    if confusions:
        lines += ["| right answer | beaten by (look-alike) | relation | count |", "| --- | --- | --- | ---: |"]
        lines += [
            f"| {concept} | {neighbor} | {relation} | {count} |"
            for (concept, neighbor, relation), count in confusions.most_common(_MAX_CONFUSIONS)
        ]
    else:
        lines.append("_No confusions (no look-alike outranked the gold)._")

    summary_path = output_dir / SUMMARY_NAME
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if make_plots and rows:
        _plot(output_dir / "plots", rows, models, languages)
    print(f"Confusion analysis written to {output_dir}")
    return summary_path


def _plot(plots_dir: Path, rows: Sequence[dict[str, Any]], models: Sequence[str], languages: Sequence[str]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"[plots skipped] matplotlib unavailable: {exc}")
        return
    plots_dir.mkdir(parents=True, exist_ok=True)
    by_key = {(row["model"], row["query_language"]): row["confusion_rate"] for row in rows}
    groups = [*languages, "ALL"]
    n = max(len(models), 1)
    fig, ax = plt.subplots(figsize=(1.7 * max(len(groups), 3) + 1.5, 4.3))
    width = 0.8 / n
    xs = list(range(len(groups)))
    for i, model in enumerate(models):
        offs = [x + (i - (n - 1) / 2) * width for x in xs]
        values = [by_key.get((model, group), 0.0) for group in groups]
        ax.bar(offs, values, width=width, label=model.split("/")[-1])
        for off, value in zip(offs, values):
            ax.text(off, value + 0.01, f"{value:.2f}", ha="center", va="bottom", fontsize=6)
    ax.set_xticks(xs)
    ax.set_xticklabels(groups)
    ax.set_ylabel("confusion rate")
    ax.set_title("Confusion rate by query language (lower = better)")
    ax.set_ylim(0, max(1.0, max(by_key.values() or [0]) * 1.15))
    ax.legend(fontsize=7, ncol=min(n, 4), loc="upper center", bbox_to_anchor=(0.5, -0.07))
    fig.tight_layout()
    fig.savefig(plots_dir / "confusion_by_language.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot written to {plots_dir / 'confusion_by_language.png'}")


__all__ = ["analyze_confusion"]
