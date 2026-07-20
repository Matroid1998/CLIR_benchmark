"""
Re-score saved predictions under alternative definitions of "relevant".

A retrieval score is a statement about a relevance judgement, not about a model
alone, and a benchmark usually ships one judgement out of several defensible
ones. This re-scores the rankings a run already saved under each *lens* -- an
alternative gold set -- with pytrec_eval. No model is re-run, so the comparison
is exactly like-for-like: same encodings, same rankings, different question.

Two lenses ship by default:

  concept_level    the benchmark as published: a query's gold is every document
                   of every family that attests the query's concept. "Find all
                   documents about X." Recall@10 is mechanically capped when a
                   query has far more than 10 relevant documents.

  per_publication  gold is the language variants of the ONE document family the
                   query was generated from (the dataset's source-family
                   column), leaving ~2-3 gold documents per query. "Find this
                   document's cross-language versions." The name is kept from
                   the published artifact so old and new outputs line up.

Register more with ``LENSES[name] = Lens(...)``; the report generalises to any
number of them.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from clir_bench.core.domain import CorpusSchema
from clir_bench.analysis.predictions import (
    discover_models,
    first_column,
    id_column,
    load_config,
    load_predictions,
    normalize_variant,
)

# pytrec_eval measure names -> the keys they produce in its per-query output.
MEASURES = {"map", "recip_rank", "ndcg_cut.10", "recall.10", "recall.100", "P.10"}
OUT_KEYS = ("recall_10", "recall_100", "P_10", "ndcg_cut_10", "recip_rank", "map")
PRETTY = {
    "recall_10": "Recall@10",
    "recall_100": "Recall@100",
    "P_10": "Precision@10",
    "ndcg_cut_10": "nDCG@10",
    "recip_rank": "MRR",
    "map": "MAP",
}
# Metrics shown side by side across lenses in comparison.md.
COMPARISON_KEYS = ("recall_10", "ndcg_cut_10", "recip_rank")

COMPARISON_NAME = "comparison.md"


@dataclass(frozen=True)
class LensInputs:
    """What every lens gets to decide a query's gold set."""

    gold: Mapping[str, set[str]]
    family_of_doc: Mapping[str, str]
    source_family: Mapping[str, str]
    schema: CorpusSchema

    def family(self, doc_id: str) -> str:
        """The family (cross-language group) a document belongs to."""
        return self.family_of_doc.get(doc_id) or self.schema.family_from_doc_id(doc_id)


@dataclass(frozen=True)
class Lens:
    name: str
    description: str
    # (inputs, query_id, the query's published gold docs) -> gold docs to score against
    select_gold: Callable[[LensInputs, str, set[str]], set[str]]
    # Lenses needing a column the dataset may not have are skipped, not fatal.
    needs_source_family: bool = False


def _concept_gold(inputs: LensInputs, query_id: str, gold: set[str]) -> set[str]:
    return gold


def _source_family_gold(inputs: LensInputs, query_id: str, gold: set[str]) -> set[str]:
    family = inputs.source_family.get(query_id)
    return {doc for doc in gold if inputs.family(doc) == family} if family else set()


LENSES: dict[str, Lens] = {
    "concept_level": Lens(
        name="concept_level",
        description=(
            "Gold = every document of every family attesting the query's concept "
            '("find all documents about X"). This is the benchmark as shipped; Recall@10 is '
            "mechanically capped because there are many relevant docs per query."
        ),
        select_gold=_concept_gold,
    ),
    "per_publication": Lens(
        name="per_publication",
        description=(
            "Gold = the language variants of the query's OWN source document -- the single "
            "publication each query was generated from (the dataset's source-family column). "
            "One eval unit per query (~2-3 gold docs). Standard full-corpus ranking: every "
            "other document, including the concept's other gold families, counts as "
            "non-relevant."
        ),
        select_gold=_source_family_gold,
        needs_source_family=True,
    ),
}

DEFAULT_LENSES = ("concept_level", "per_publication")


def rescore_run(
    predictions_dir: str | Path,
    output_dir: str | Path,
    *,
    dataset_repo: str,
    variant: str = "multilingual",
    schema: CorpusSchema,
    lenses: Optional[Sequence[str]] = None,
    drop_models: Optional[Sequence[str]] = None,
    model_names: Optional[Sequence[str]] = None,
    revision: str = "main",
) -> Path:
    """Re-score saved predictions under each lens. Returns the comparison report path."""
    predictions_dir = Path(predictions_dir)
    output_dir = Path(output_dir)
    variant = normalize_variant(variant)

    selected = [_lens(name) for name in (lenses or DEFAULT_LENSES)]
    models = discover_models(predictions_dir, model_names)
    if drop_models:
        # Used to exclude a model whose predictions are a loading artifact rather
        # than real performance (a degenerate encoder that fails trivial
        # same-language self-retrieval would otherwise anchor every table).
        patterns = [p.lower() for p in drop_models]
        models = [
            (label, slug) for label, slug in models
            if not any(p in label.lower() or p in slug.lower() for p in patterns)
        ]
    if not models:
        raise ValueError(f"No per-query predictions under {predictions_dir}.")

    inputs = _load_inputs(dataset_repo, variant, revision, schema)
    if not inputs.source_family:
        skipped = [lens.name for lens in selected if lens.needs_source_family]
        if skipped:
            print(f"[lens skipped] {', '.join(skipped)}: queries carry no source-family column")
        selected = [lens for lens in selected if not lens.needs_source_family]
    if not selected:
        raise ValueError("No applicable lens for this dataset.")

    print(f">> {len(models)} model(s) with predictions, {len(selected)} lens(es)")
    results: dict[str, dict[str, Any]] = {lens.name: {"rows": [], "units": 0, "avg_gold": 0.0}
                                          for lens in selected}
    for label, slug in models:
        preds = load_predictions(predictions_dir / slug)
        if not preds:
            print(f"   [skip] {label}: no predictions")
            continue
        scored = []
        for lens in selected:
            metrics, units, avg_gold, missing = _score(preds, inputs, lens)
            if missing:
                print(f"   [warn] {lens.name}: {missing} query/ies had no gold doc under this lens")
            bucket = results[lens.name]
            bucket["rows"].append({"model": label, "metrics": metrics})
            bucket["units"], bucket["avg_gold"] = units, avg_gold
            scored.append(f"{lens.name} R@10={metrics['recall_10']:.4f}")
        print(f"   {label:48s} " + "  ".join(scored))

    output_dir.mkdir(parents=True, exist_ok=True)
    for lens in selected:
        bucket = results[lens.name]
        _write_lens(output_dir, lens, bucket["rows"], bucket["units"], bucket["avg_gold"])
    report = _write_comparison(output_dir, selected, results)
    print(f"\n>> wrote {output_dir}")
    return report


def _lens(name: str) -> Lens:
    try:
        return LENSES[name]
    except KeyError as exc:
        raise KeyError(f"unknown lens {name!r}; available: {', '.join(sorted(LENSES))}") from exc


def _load_inputs(dataset_repo: str, variant: str, revision: str, schema: CorpusSchema) -> LensInputs:
    queries = load_config(dataset_repo, "queries", variant=variant, revision=revision)
    corpus = load_config(dataset_repo, "corpus", variant=variant, revision=revision)
    qrels = load_config(dataset_repo, "qrels", variant=variant, revision=revision)

    corpus_columns = list(corpus.column_names)
    cid_col = id_column(corpus_columns, "corpus_id")
    family_col = schema.family_field if schema.family_field in corpus_columns else None
    family_of_doc = (
        {str(row[cid_col]): str(row[family_col]) for row in corpus} if family_col else {}
    )

    query_columns = list(queries.column_names)
    qid_col = id_column(query_columns, "query_id")
    source_col = first_column(query_columns, "source_family", "source_publication")
    source_family = (
        {str(row[qid_col]): str(row[source_col]) for row in queries} if source_col else {}
    )

    gold: dict[str, set[str]] = defaultdict(set)
    for row in qrels:
        if float(row["score"]) > 0:
            gold[str(row["query-id"])].add(str(row["corpus-id"]))
    return LensInputs(gold=gold, family_of_doc=family_of_doc, source_family=source_family, schema=schema)


def _score(
    preds: Mapping[str, dict[str, float]], inputs: LensInputs, lens: Lens
) -> tuple[dict[str, float], int, float, int]:
    import pytrec_eval

    qrels: dict[str, dict[str, int]] = {}
    run: dict[str, dict[str, float]] = {}
    gold_sizes: list[int] = []
    missing = 0
    for query_id, docs in inputs.gold.items():
        if query_id not in preds:
            continue
        selected = lens.select_gold(inputs, query_id, docs)
        if not selected:
            missing += 1
            continue
        qrels[query_id] = {doc: 1 for doc in selected}
        run[query_id] = preds[query_id]
        gold_sizes.append(len(selected))
    scores = pytrec_eval.RelevanceEvaluator(qrels, MEASURES).evaluate(run)
    metrics = {key: _avg([scores[q][key] for q in scores]) for key in OUT_KEYS}
    return metrics, len(qrels), _avg(gold_sizes), missing


def _avg(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _write_lens(
    output_dir: Path, lens: Lens, rows: Sequence[dict[str, Any]], units: int, avg_gold: float
) -> None:
    directory = output_dir / lens.name
    directory.mkdir(parents=True, exist_ok=True)
    ranked = sorted(rows, key=lambda row: row["metrics"]["recall_10"], reverse=True)
    payload = {
        "interpretation": lens.name,
        "description": lens.description,
        "eval_units": units,
        "avg_relevant_per_unit": round(avg_gold, 2),
        "ranked_by": "recall_10",
        "models": [
            {"model_name": row["model"], "metrics": {k: round(row["metrics"][k], 5) for k in OUT_KEYS}}
            for row in ranked
        ],
    }
    (directory / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# Interpretation: {lens.name}", "", lens.description, "",
        f"- Eval units: **{units}**  ·  avg relevant docs per unit: **{avg_gold:.1f}**",
        "- Models ranked by Recall@10 (re-scored from the saved predictions; no model re-run).",
        "",
        "| Rank | Model | " + " | ".join(PRETTY[k] for k in OUT_KEYS) + " |",
        "| ---: | --- | " + " | ".join(["---:"] * len(OUT_KEYS)) + " |",
    ]
    for index, row in enumerate(ranked, start=1):
        cells = [str(index), f"`{row['model']}`", *[f"{row['metrics'][k]:.4f}" for k in OUT_KEYS]]
        lines.append("| " + " | ".join(cells) + " |")
    (directory / "leaderboard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_comparison(
    output_dir: Path, lenses: Sequence[Lens], results: Mapping[str, Mapping[str, Any]]
) -> Path:
    by_lens = {
        lens.name: {row["model"]: row["metrics"] for row in results[lens.name]["rows"]}
        for lens in lenses
    }
    # Rank by the last lens: the default pair puts the uncapped, per-document
    # reading second, and that is the ordering the published report used.
    anchor = lenses[-1].name
    models = sorted(
        by_lens[anchor], key=lambda model: by_lens[anchor][model]["recall_10"], reverse=True
    )

    headers = [f"{lens.name} {PRETTY[key]}" for key in COMPARISON_KEYS for lens in lenses]
    lines = [
        "# Relevance interpretations of one run", "",
        "Same models, same saved rankings — only the definition of *relevant* differs.", "",
    ]
    for lens in lenses:
        bucket = results[lens.name]
        lines.append(
            f"- **{lens.name}**: {bucket['units']} queries, ~{bucket['avg_gold']:.1f} gold docs each."
        )
    lines += [
        "", f"## Side by side (ranked by {anchor} Recall@10)", "",
        "| Model | " + " | ".join(headers) + " |",
        "| --- | " + " | ".join(["---:"] * len(headers)) + " |",
    ]
    for model in models:
        cells = [
            f"{by_lens[lens.name].get(model, {}).get(key, float('nan')):.4f}"
            for key in COMPARISON_KEYS
            for lens in lenses
        ]
        lines.append(f"| `{model}` | " + " | ".join(cells) + " |")

    report = output_dir / COMPARISON_NAME
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    readme = ["# Relevance interpretations of this run", ""]
    for lens in lenses:
        readme += [lens.description, ""]
    readme += ["Files:", ""]
    readme += [f"- `{lens.name}/` — leaderboard.md + summary.json" for lens in lenses]
    readme += [
        f"- `{COMPARISON_NAME}` — every lens side by side",
        "",
        "All lenses are re-scored from `../predictions/` with pytrec_eval; the models were NOT re-run.",
    ]
    (output_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    return report


__all__ = ["LENSES", "Lens", "LensInputs", "rescore_run"]
