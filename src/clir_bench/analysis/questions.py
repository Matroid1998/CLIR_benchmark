"""
Question-level analysis of saved retrieval predictions.

An aggregate Recall@10 says a model is good; it does not say *for whom*. This
breaks the same saved rankings down by the properties of the question:

  1. query language
  2. question mode and generation strategy
  3. query origin (natively written vs machine-translated)
  4. same- vs cross-language relevant documents
  5. the query-language x document-language matrix for the best model

Domain labels (which modes exist, how strategies are ordered) arrive as an
``AnalysisVocab``; nothing here names a domain. Every breakdown is skipped when
its column is absent, so an older dataset export still yields the rest of the
report instead of failing.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.domain import AnalysisVocab, CorpusSchema
from clir_bench.core.runs import read_summary, slugify_model
from clir_bench.analysis.predictions import (
    corpus_language_column,
    discover_models,
    id_column,
    load_config,
    load_predictions,
    mean,
    normalize_variant,
    query_language_column,
    ranked_docs,
)

DEFAULT_K = 10
REPORT_NAME = "question_level_analysis.md"
METRICS_CSV_NAME = "question_level_metrics.csv"

TRUE_VALUES = {"true", "1", "yes"}


@dataclass(frozen=True)
class PairMatrix:
    """Per-(query language, doc language) retrieval outcomes for one model.

    Built once and consumed by both the markdown table and the heatmap: the
    predecessor recomputed this loop separately for each, which was the only
    place the report and the plot could silently disagree.
    """

    rows: list[str]
    cols: list[str]
    hits: Mapping[tuple[str, str], list[float]]

    def score(self, query_lang: str, doc_lang: str) -> Optional[float]:
        values = self.hits.get((query_lang, doc_lang))
        return mean(values) if values else None

    def count(self, query_lang: str, doc_lang: str) -> int:
        return len(self.hits.get((query_lang, doc_lang), ()))


def analyze_questions(
    predictions_dir: str | Path,
    output_dir: str | Path,
    *,
    dataset_repo: str,
    variant: str = "multilingual",
    schema: CorpusSchema,
    vocab: Optional[AnalysisVocab] = None,
    k: int = DEFAULT_K,
    make_plots: bool = True,
    query_metadata_csv: Optional[str | Path] = None,
    model_names: Optional[Sequence[str]] = None,
    revision: str = "main",
) -> Path:
    """Write the question-level report and per-query CSV. Returns the report path."""
    predictions_dir = Path(predictions_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    variant = normalize_variant(variant)
    vocab = vocab or AnalysisVocab()
    run_dir = output_dir.parent

    if model_names is None:
        # Recover the real model ids from the run's summary so tables read
        # `BAAI/bge-m3` rather than the slugified directory name.
        model_names = _summary_model_names(run_dir) or None

    models = discover_models(predictions_dir, model_names)
    if not models:
        raise ValueError(
            f"No per-query predictions found under {predictions_dir}. "
            "Run the evaluation with prediction saving enabled first."
        )

    queries = load_config(dataset_repo, "queries", variant=variant, revision=revision)
    corpus = load_config(dataset_repo, "corpus", variant=variant, revision=revision)
    qrels = load_config(dataset_repo, "qrels", variant=variant, revision=revision)

    attrs = _query_attributes(queries, schema, vocab, query_metadata_csv)
    corpus_lang = _corpus_languages(corpus, schema)
    relevant = _relevant_docs(qrels)

    per_model: dict[str, dict[str, dict[str, Any]]] = {}
    for label, slug in models:
        preds = load_predictions(predictions_dir / slug)
        if preds is None:
            continue
        per_model[label] = _per_query_metrics(preds, relevant, attrs.language, corpus_lang, k)
    labels = list(per_model)
    if not labels:
        raise ValueError(
            f"Found prediction folders under {predictions_dir} but none contained usable "
            "per-query rankings."
        )

    langs = sorted({v for v in attrs.language.values() if v})
    best = max(labels, key=lambda lb: mean(pq["recall"] for pq in per_model[lb].values()))
    matrix = (
        _pair_matrix(per_model[best], attrs.language, corpus_lang, langs)
        if (attrs.language and corpus_lang)
        else None
    )

    report_path = output_dir / REPORT_NAME
    report_path.write_text(
        _render_report(
            dataset_repo=dataset_repo,
            variant=variant,
            k=k,
            labels=labels,
            langs=langs,
            per_model=per_model,
            attrs=attrs,
            corpus_lang=corpus_lang,
            relevant=relevant,
            vocab=vocab,
            best=best,
            matrix=matrix,
        ),
        encoding="utf-8",
    )

    csv_path = output_dir / METRICS_CSV_NAME
    corpus_io.write_rows(
        csv_path,
        _metric_rows(per_model, attrs, k),
        [
            "model", "query_id", "query_language", "mode", "strategy",
            "is_synthetic_translation",
            f"recall_at_{k}", f"rr_at_{k}", f"hit_at_{k}", "n_relevant",
        ],
    )
    print(f"Question-level analysis written to {report_path} and {csv_path}")

    if make_plots:
        try:
            _plot(
                output_dir,
                per_model=per_model,
                labels=labels,
                langs=langs,
                attrs=attrs,
                matrix=matrix,
                best=best,
                summary_metrics=_summary_metrics(run_dir),
                vocab=vocab,
                k=k,
            )
        except Exception as exc:  # plotting must never break the analysis itself
            print(f"[plots skipped] {exc}")
    return report_path


# --------------------------------------------------------------------------- #
# Query attributes
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class QueryAttributes:
    language: dict[str, str]
    mode: dict[str, str]
    strategy: dict[str, str]
    synthetic: dict[str, bool]
    has_origin: bool


def _query_attributes(
    queries,
    schema: CorpusSchema,
    vocab: AnalysisVocab,
    query_metadata_csv: Optional[str | Path],
) -> QueryAttributes:
    columns = list(queries.column_names)
    qid_col = id_column(columns, "query_id")
    lang_col = query_language_column(columns)
    synth_col = "is_synthetic_translation" if "is_synthetic_translation" in columns else None
    mode_col, strategy_col = _metadata_columns(columns)

    # An already-published dataset whose export predates the mode/strategy
    # columns can still be broken down, by joining a QAC metadata CSV.
    by_text: dict[str, tuple[str, str]] = {}
    by_doc_lang: dict[tuple[str, str], tuple[str, str]] = {}
    if (mode_col is None or strategy_col is None) and query_metadata_csv:
        try:
            by_text, by_doc_lang = _load_query_metadata_csv(query_metadata_csv, vocab)
        except Exception as exc:
            print(f"[query-metadata skipped] {exc}")

    language: dict[str, str] = {}
    mode: dict[str, str] = {}
    strategy: dict[str, str] = {}
    synthetic: dict[str, bool] = {}
    for row in queries:
        qid = str(row[qid_col])
        lang = str(row.get(lang_col) or "").strip().lower() if lang_col else ""
        lang = lang or schema.language_from_doc_id(qid)  # ids encode the language
        if lang:
            language[qid] = lang
        if synth_col is not None:
            synthetic[qid] = str(row.get(synth_col)).strip().lower() in TRUE_VALUES
        mode_value = str(row.get(mode_col) or "").strip().lower() if mode_col else ""
        strategy_value = (
            _strategy_display(row.get(strategy_col), vocab)
            if strategy_col and row.get(strategy_col) not in (None, "")
            else ""
        )
        if (not mode_value or not strategy_value) and (by_text or by_doc_lang):
            meta = by_text.get(str(row.get("text") or "").strip()) or by_doc_lang.get(
                (str(row.get("corpus_id") or "").strip(), lang)
            )
            if meta:
                mode_value = mode_value or meta[0]
                strategy_value = strategy_value or meta[1]
        if mode_value:
            mode[qid] = mode_value
        if strategy_value:
            strategy[qid] = strategy_value
    return QueryAttributes(language, mode, strategy, synthetic, synth_col is not None)


def _metadata_columns(columns: Sequence[str]) -> tuple[Optional[str], Optional[str]]:
    mode_col = "mode" if "mode" in columns else None
    if "strategy_name" in columns:
        return mode_col, "strategy_name"
    return mode_col, ("strategy" if "strategy" in columns else None)


def _strategy_display(value: Any, vocab: AnalysisVocab) -> str:
    """Canonical strategy label, resolving the numeric encoding via the domain."""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]  # strategy survives CSV/parquet round-trips as a float
    try:
        return vocab.strategy_numbers[int(text)]
    except (ValueError, KeyError):
        return text


def _load_query_metadata_csv(
    csv_path: str | Path, vocab: AnalysisVocab
) -> tuple[dict[str, tuple[str, str]], dict[tuple[str, str], tuple[str, str]]]:
    """Map question text -> (mode, strategy), with a (corpus_id, language) fallback."""
    rows = corpus_io.read_rows(Path(csv_path))
    columns = list(rows[0]) if rows else []
    text_col = "question" if "question" in columns else ("text" if "text" in columns else None)
    mode_col, strategy_col = _metadata_columns(columns)
    doc_col = "corpus_id" if "corpus_id" in columns else None
    lang_col = query_language_column(columns)

    by_text: dict[str, tuple[str, str]] = {}
    by_doc_lang: dict[tuple[str, str], tuple[str, str]] = {}
    for row in rows:
        mode_value = str(row.get(mode_col) or "").strip().lower() if mode_col else ""
        strategy_value = (
            _strategy_display(row.get(strategy_col), vocab)
            if strategy_col and str(row.get(strategy_col) or "").strip()
            else ""
        )
        meta = (mode_value, strategy_value)
        if text_col and str(row.get(text_col) or "").strip():
            by_text[str(row[text_col]).strip()] = meta
        if doc_col and lang_col and str(row.get(doc_col) or "").strip() and str(row.get(lang_col) or "").strip():
            by_doc_lang[(str(row[doc_col]).strip(), str(row[lang_col]).strip().lower())] = meta
    return by_text, by_doc_lang


def _corpus_languages(corpus, schema: CorpusSchema) -> dict[str, str]:
    columns = list(corpus.column_names)
    cid_col = id_column(columns, "corpus_id")
    lang_col = corpus_language_column(columns)
    languages: dict[str, str] = {}
    for row in corpus:
        cid = str(row[cid_col])
        lang = str(row.get(lang_col) or "").strip().lower() if lang_col else ""
        lang = lang or schema.language_from_doc_id(cid)
        if lang:
            languages[cid] = lang
    return languages


def _relevant_docs(qrels) -> dict[str, set[str]]:
    columns = list(qrels.column_names)
    qid_col = "query-id" if "query-id" in columns else columns[0]
    cid_col = "corpus-id" if "corpus-id" in columns else (columns[1] if len(columns) > 1 else columns[0])
    score_col = "score" if "score" in columns else (columns[2] if len(columns) > 2 else None)
    relevant: dict[str, set[str]] = defaultdict(set)
    for row in qrels:
        # No score column means binary relevance; score 0 marks a labelled hard
        # negative, which is judged but not relevant.
        if score_col is None or float(row[score_col]) > 0:
            relevant[str(row[qid_col])].add(str(row[cid_col]))
    return relevant


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #

def _per_query_metrics(
    preds: Mapping[str, dict[str, float]],
    relevant: Mapping[str, set[str]],
    query_lang: Mapping[str, str],
    corpus_lang: Mapping[str, str],
    k: int,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for qid, rel_set in relevant.items():
        if qid not in preds or not rel_set:
            continue
        ranking = ranked_docs(preds[qid])
        top = set(ranking[:k])
        rr = 0.0
        for rank, doc in enumerate(ranking[:k], start=1):  # MRR@k: only the top k count
            if doc in rel_set:
                rr = 1.0 / rank
                break
        lang = query_lang.get(qid)
        same = {doc for doc in rel_set if corpus_lang.get(doc) == lang} if corpus_lang else set()
        cross = (rel_set - same) if corpus_lang else set()
        out[qid] = {
            "recall": len(rel_set & top) / len(rel_set),
            "rr": rr,
            "hit": 1.0 if (rel_set & top) else 0.0,
            "same_recall": (len(same & top) / len(same)) if same else None,
            "cross_recall": (len(cross & top) / len(cross)) if cross else None,
            "top": top,
            "rel": rel_set,
        }
    return out


def _pair_matrix(
    per_query: Mapping[str, dict[str, Any]],
    query_lang: Mapping[str, str],
    corpus_lang: Mapping[str, str],
    langs: Sequence[str],
) -> PairMatrix:
    hits: dict[tuple[str, str], list[float]] = defaultdict(list)
    for qid, pq in per_query.items():
        ql = query_lang.get(qid)
        for doc in pq["rel"]:
            hits[(ql, corpus_lang.get(doc, "?"))].append(1.0 if doc in pq["top"] else 0.0)
    return PairMatrix(rows=list(langs), cols=sorted({dl for (_, dl) in hits}), hits=hits)


def _metric_rows(
    per_model: Mapping[str, Mapping[str, dict[str, Any]]], attrs: QueryAttributes, k: int
) -> Iterable[dict[str, Any]]:
    for label, per_query in per_model.items():
        for qid, pq in per_query.items():
            yield {
                "model": label,
                "query_id": qid,
                "query_language": attrs.language.get(qid, ""),
                "mode": attrs.mode.get(qid, ""),
                "strategy": attrs.strategy.get(qid, ""),
                "is_synthetic_translation": attrs.synthetic.get(qid, "") if attrs.has_origin else "",
                f"recall_at_{k}": round(pq["recall"], 5),
                f"rr_at_{k}": round(pq["rr"], 5),
                f"hit_at_{k}": int(pq["hit"]),
                "n_relevant": len(pq["rel"]),
            }


def _ordered(values: Iterable[str], order: Sequence[str]) -> list[str]:
    """Domain order first, then anything the data contains that it does not list."""
    present = set(values)
    return [v for v in order if v in present] + sorted(present - set(order))


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #

def _render_report(
    *,
    dataset_repo: str,
    variant: str,
    k: int,
    labels: Sequence[str],
    langs: Sequence[str],
    per_model: Mapping[str, Mapping[str, dict[str, Any]]],
    attrs: QueryAttributes,
    corpus_lang: Mapping[str, str],
    relevant: Mapping[str, set[str]],
    vocab: AnalysisVocab,
    best: str,
    matrix: Optional[PairMatrix],
) -> str:
    lines: list[str] = []

    def emit(text: str = "") -> None:
        lines.append(text)

    emit(f"# Question-level analysis ({dataset_repo}, `{variant}`, Recall@{k} / MRR@{k})\n")

    qids = [q for q in relevant if (not attrs.language or q in attrs.language)]
    emit("## Dataset structure")
    emit(f"- Queries with relevance judgements: {len(qids)}")
    if attrs.has_origin:
        n_synth = sum(1 for q in qids if attrs.synthetic.get(q))
        emit(f"- Original: {len(qids) - n_synth}  |  synthetic-translation: {n_synth}")
    for title, mapping, order in (
        ("mode", attrs.mode, vocab.modes),
        ("strategy", attrs.strategy, vocab.strategies),
    ):
        if not mapping:
            continue
        counts: dict[str, int] = defaultdict(int)
        for q in qids:
            if mapping.get(q):
                counts[mapping[q]] += 1
        keys = _ordered(counts, order)
        emit(f"- Questions by {title}: " + ", ".join(f"{key}={counts[key]}" for key in keys))
    if attrs.language:
        by_lang: dict[str, int] = defaultdict(int)
        for q in qids:
            by_lang[attrs.language.get(q, "?")] += 1
        emit("- Queries by language: " + ", ".join(f"{lng}={by_lang[lng]}" for lng in langs if by_lang.get(lng)))
    pairs = sum(len(relevant[q]) for q in qids)
    emit(f"- Relevant (query, doc) pairs: {pairs} (avg {pairs / max(len(qids), 1):.2f}/query)")
    emit("- Models analysed: " + ", ".join(labels))
    emit("")

    def grouped_table(
        title: str,
        group_of: Callable[[str], Optional[str]],
        key: str,
        order: Sequence[str] = (),
    ) -> None:
        emit(f"## {title}")
        groups = {
            group_of(qid)
            for label in labels
            for qid, pq in per_model[label].items()
            if group_of(qid) is not None and pq.get(key) is not None
        }
        emit("| Group | n | " + " | ".join(labels) + " |")
        emit("|" + "---|" * (len(labels) + 2))
        for group in _ordered(groups, order):
            reference = labels[0]
            n = sum(
                1
                for qid, pq in per_model[reference].items()
                if group_of(qid) == group and pq.get(key) is not None
            )
            cells = []
            for label in labels:
                values = [
                    pq[key]
                    for qid, pq in per_model[label].items()
                    if group_of(qid) == group and pq.get(key) is not None
                ]
                cells.append(f"{mean(values):.3f}" if values else " - ")
            emit(f"| {group} | {n} | " + " | ".join(cells) + " |")
        emit("")

    if attrs.language and len(langs) > 1:
        grouped_table(f"1) Recall@{k} by query language", attrs.language.get, "recall")
        grouped_table(f"   MRR@{k} by query language", attrs.language.get, "rr")
    if attrs.mode:
        grouped_table(f"2) Recall@{k} by question mode", attrs.mode.get, "recall", vocab.modes)
    if attrs.strategy:
        grouped_table(
            f"3) Recall@{k} by question strategy", attrs.strategy.get, "recall", vocab.strategies
        )
    if attrs.has_origin:
        grouped_table(
            f"4) Recall@{k} by query origin (original vs synthetic-translation)",
            lambda q: "synthetic-translation" if attrs.synthetic.get(q) else "original",
            "recall",
            ("original", "synthetic-translation"),
        )

    if corpus_lang:
        emit(f"## 5) Cross-lingual targets: same- vs cross-language (mean Recall@{k})")
        emit("| Target | " + " | ".join(labels) + " |")
        emit("|" + "---|" * (len(labels) + 1))
        for name, key in (("same-language target", "same_recall"), ("cross-language target", "cross_recall")):
            cells = []
            for label in labels:
                values = [pq[key] for pq in per_model[label].values() if pq.get(key) is not None]
                cells.append(f"{mean(values):.3f}" if values else " - ")
            emit(f"| {name} | " + " | ".join(cells) + " |")
        emit("")

    if matrix is not None and len(langs) > 1:
        emit(f"## 6) Language-pair Recall@{k} matrix — {best} (best model)")
        emit("Rows = query language, Cols = relevant-doc language; cell = fraction of those")
        emit(f"relevant docs retrieved in the top {k} (n = #relevant pairs).")
        emit("")
        emit("| q\\d | " + " | ".join(matrix.cols) + " |")
        emit("|" + "---|" * (len(matrix.cols) + 1))
        for ql in matrix.rows:
            cells = []
            for dl in matrix.cols:
                score = matrix.score(ql, dl)
                cells.append(f"{score:.2f} ({matrix.count(ql, dl)})" if score is not None else " - ")
            emit(f"| **{ql}** | " + " | ".join(cells) + " |")
        emit("")

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Run summary (for the overall-metrics and language-bias plots)
# --------------------------------------------------------------------------- #

def _summary_models(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Model name -> metrics from a run's summary.json ({} when absent)."""
    models = read_summary(run_dir).get("models") or {}
    if isinstance(models, list):  # legacy shape: a list of {model_name, metrics}
        return {
            str(item.get("model_name", "")): dict(item.get("metrics") or {})
            for item in models
            if item.get("model_name")
        }
    return {str(name): dict(metrics) for name, metrics in models.items() if isinstance(metrics, dict)}


def _summary_model_names(run_dir: Path) -> list[str]:
    return [name for name in _summary_models(run_dir) if name]


def _summary_metrics(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Metrics keyed by model slug, so they join against prediction folder names."""
    return {slugify_model(name): metrics for name, metrics in _summary_models(run_dir).items()}


# --------------------------------------------------------------------------- #
# Plots
# --------------------------------------------------------------------------- #

def _short_label(name: str) -> str:
    base = name.split("/")[-1]
    return base.replace("paraphrase-multilingual-", "").replace("multilingual-", "")


def _plot(
    output_dir: Path,
    *,
    per_model: Mapping[str, Mapping[str, dict[str, Any]]],
    labels: Sequence[str],
    langs: Sequence[str],
    attrs: QueryAttributes,
    matrix: Optional[PairMatrix],
    best: str,
    summary_metrics: Mapping[str, Mapping[str, Any]],
    vocab: AnalysisVocab,
    k: int,
) -> Optional[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"[plots skipped] matplotlib unavailable: {exc}")
        return None

    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    for stale in ("mode_same_vs_cross.png", "strategy_original_vs_translation.png"):
        (plots_dir / stale).unlink(missing_ok=True)  # superseded by renamed plots
    short = [_short_label(label) for label in labels]
    n = len(labels)

    def grouped_bar(fname, group_labels, values_by_label, ylabel, title, ymax=1.0):
        if not group_labels:
            return
        fig, ax = plt.subplots(figsize=(1.7 * max(len(group_labels), 3) + 1.5, 4.3))
        width = 0.8 / max(n, 1)
        xs = list(range(len(group_labels)))
        for i in range(n):
            offs = [x + (i - (n - 1) / 2) * width for x in xs]
            ax.bar(offs, [v if v is not None else 0.0 for v in values_by_label[i]], width=width, label=short[i])
            for off, value in zip(offs, values_by_label[i]):
                if value is not None:
                    ax.text(off, value + 0.012, f"{value:.2f}", ha="center", va="bottom", fontsize=6)
        ax.set_xticks(xs)
        ax.set_xticklabels(group_labels)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_ylim(0, ymax)
        ax.legend(fontsize=7, ncol=min(n, 4), loc="upper center", bbox_to_anchor=(0.5, -0.07))
        fig.tight_layout()
        fig.savefig(plots_dir / fname, dpi=130, bbox_inches="tight")
        plt.close(fig)

    def mean_where(label, predicate, key="recall"):
        values = [
            pq[key]
            for qid, pq in per_model[label].items()
            if predicate(qid, pq) and pq.get(key) is not None
        ]
        return mean(values) if values else None

    if summary_metrics:
        keys = [("recall_at_10", "Recall@10"), ("ndcg_at_10", "nDCG@10"), ("map_at_10", "MAP@10")]
        values = [[summary_metrics.get(slugify_model(lb), {}).get(mk) for mk, _ in keys] for lb in labels]
        grouped_bar("overall_metrics.png", [lbl for _, lbl in keys], values, "score",
                    f"Overall retrieval metrics (k={k})")
    else:
        groups = [f"Recall@{k}", f"MRR@{k}", f"hit@{k}"]
        values = [[mean(pq["recall"] for pq in per_model[lb].values()),
                   mean(pq["rr"] for pq in per_model[lb].values()),
                   mean(pq["hit"] for pq in per_model[lb].values())] for lb in labels]
        grouped_bar("overall_metrics.png", groups, values, "score", f"Overall (k={k})")

    if langs:
        values = [[mean_where(lb, lambda q, pq, lng=lng: attrs.language.get(q) == lng) for lng in langs]
                  for lb in labels]
        grouped_bar("recall_by_language.png", langs, values, f"Recall@{k}", f"Recall@{k} by query language")

    for fname, mapping, order, title in (
        ("mode.png", attrs.mode, vocab.modes, "question mode"),
        ("strategy.png", attrs.strategy, vocab.strategies, "question strategy"),
    ):
        if not mapping:
            continue
        present = _ordered(mapping.values(), order)
        values = [[mean_where(lb, lambda q, pq, g=g: mapping.get(q) == g) for g in present] for lb in labels]
        grouped_bar(fname, present, values, f"Recall@{k}", f"Recall@{k} by {title}")

    def target_mean(label, key):
        values = [pq[key] for pq in per_model[label].values() if pq.get(key) is not None]
        return mean(values) if values else None

    if any(target_mean(lb, "same_recall") is not None or target_mean(lb, "cross_recall") is not None
           for lb in labels):
        values = [[target_mean(lb, "same_recall"), target_mean(lb, "cross_recall")] for lb in labels]
        grouped_bar("cross_lingual_targets.png", ["same-language", "cross-language"], values,
                    f"Recall@{k}", f"Cross-lingual targets: same vs cross (Recall@{k})")

    if attrs.has_origin and attrs.synthetic:
        values = [[mean_where(lb, lambda q, pq, want=want: q in attrs.synthetic and attrs.synthetic[q] is want)
                   for want in (False, True)] for lb in labels]
        grouped_bar("query_origin.png", ["original", "synthetic-translation"], values,
                    f"Recall@{k}", f"Query origin: original vs synthetic (Recall@{k})")

    if matrix is not None and matrix.cols and matrix.rows:
        values = [[matrix.score(ql, dl) for dl in matrix.cols] for ql in matrix.rows]
        fig, ax = plt.subplots(figsize=(1.0 * len(matrix.cols) + 2.5, 1.0 * len(matrix.rows) + 2))
        image = ax.imshow(
            [[float("nan") if v is None else v for v in row] for row in values],
            vmin=0, vmax=1, cmap="viridis", aspect="auto",
        )
        ax.set_xticks(range(len(matrix.cols)), labels=matrix.cols)
        ax.set_yticks(range(len(matrix.rows)), labels=matrix.rows)
        ax.set_xlabel("relevant-doc language")
        ax.set_ylabel("query language")
        ax.set_title(f"{_short_label(best)}: Recall@{k} by query x doc language")
        for i, ql in enumerate(matrix.rows):
            for j, dl in enumerate(matrix.cols):
                value = values[i][j]
                text = "-" if value is None else f"{value:.2f}\n(n={matrix.count(ql, dl)})"
                ax.text(j, i, text, ha="center", va="center", fontsize=7,
                        color="white" if (value is not None and value < 0.6) else "black")
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(plots_dir / f"language_pair_heatmap_{slugify_model(best)}.png", dpi=130,
                    bbox_inches="tight")
        plt.close(fig)

    # Same-language bias diagnostic: emitted by the evaluation harness per
    # language, so it exists only when the run recorded those metrics.
    if summary_metrics and langs:
        candidates = [lng for lng in (vocab.diagnostic_languages or langs) if lng in langs]
        bias_langs = [
            lng for lng in candidates
            if any(summary_metrics.get(slugify_model(lb), {}).get(
                f"same_language_irrelevant_share_at_100_lang_{lng}") is not None for lb in labels)
        ]
        if bias_langs:
            values = [[summary_metrics.get(slugify_model(lb), {}).get(
                f"same_language_irrelevant_share_at_100_lang_{lng}") for lng in bias_langs] for lb in labels]
            grouped_bar("same_language_bias_by_language.png", bias_langs, values, "same-lang share",
                        "Same-language irrelevant share @100 (lower = less language bias)")

    print(f"Plots written to {plots_dir}")
    return plots_dir


__all__ = ["PairMatrix", "analyze_questions"]
