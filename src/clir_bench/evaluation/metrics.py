"""
The metric engine for retrieval runs.

MTEB reports its own metric family, but two things are missing for cross-language
work. The first is MAP over the full ranking rather than a cutoff. The second is
this project's own metric, and the reason this module exists:

``same_language_irrelevant_share_at_k``
    For one query, take the top-k ranked documents, drop the judged-relevant
    ones, and report the fraction of what remains that is written in the query's
    own language. A query whose top-k contains nothing irrelevant contributes
    0.0. The per-query values are averaged over all scored queries, and again
    over the queries of each diagnostic language separately.

It measures language collapse: a model that ranks by meaning scores near the
haystack's own language mix, while a model that ranks by surface language scores
near 1.0 -- it filled the ranking with same-language documents that answer
nothing. Lower is better, which is why every "best value" comparison has to
special-case this family.

Recall/MAP/nDCG are recomputed here rather than read from MTEB so that all
metrics come from one ranking, one qrels reading and one rounding convention.
Nothing here knows what a document is about: a document's language comes from the
corpus language lookup when the dataset carries one, and otherwise from the
domain's id convention via ``CorpusSchema.language_from_doc_id``.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from clir_bench.core.domain import CorpusSchema

RETRIEVAL_CUTOFFS: tuple[int, ...] = (10, 20, 50, 100)

# Scores are rounded before they are written, so a summary.json diff between two
# runs shows real movement instead of float noise.
SCORE_DIGITS = 5


def resolve_language(
    doc_id: str,
    languages: Mapping[str, str] | None,
    schema: CorpusSchema,
) -> str:
    """Language of a document (or query) id.

    The lookup table wins when it has an entry; ids are the fallback because a
    shared haystack holds documents that are not in the benchmark's own corpus
    config and so carry no language column at all.
    """
    if languages:
        language = str(languages.get(doc_id, "") or "").strip().lower()
        if language:
            return language
    return schema.language_from_doc_id(doc_id)


def is_lower_better(metric: str) -> bool:
    """Whether a smaller value of ``metric`` is the better result."""
    return metric.startswith("same_language_irrelevant_share_at_")


def compute_retrieval_metrics(
    *,
    results: Mapping[str, Mapping[str, float]],
    qrels: Mapping[str, Mapping[str, Any]],
    schema: CorpusSchema,
    query_languages: Mapping[str, str] | None = None,
    corpus_languages: Mapping[str, str] | None = None,
    diagnostic_languages: Sequence[str] = (),
    cutoffs: Sequence[int] = RETRIEVAL_CUTOFFS,
) -> dict[str, float]:
    """Score one model's rankings.

    ``results`` maps query id -> {doc id: score}; ``qrels`` maps query id ->
    {doc id: relevance}. Any relevance > 0 counts as relevant (the benchmark's
    qrels are binary, but floats survive a round-trip through parquet).
    """
    import pytrec_eval

    diagnostic = tuple(diagnostic_languages)
    metric_scores: dict[str, float] = {}

    # MAP over the untruncated ranking, from the reference implementation rather
    # than ours, so the headline number is comparable with published TREC-style
    # results.
    evaluator = pytrec_eval.RelevanceEvaluator(dict(qrels), {"map"})
    per_query_scores = evaluator.evaluate(dict(results))
    if per_query_scores:
        full_map = sum(
            float(item.get("map", 0.0)) for item in per_query_scores.values()
        ) / len(per_query_scores)
        metric_scores["map"] = round(full_map, SCORE_DIGITS)

    cutoff_list = list(cutoffs)
    recall_scores: dict[int, list[float]] = {cutoff: [] for cutoff in cutoff_list}
    map_scores: dict[int, list[float]] = {cutoff: [] for cutoff in cutoff_list}
    ndcg_scores: dict[int, list[float]] = {cutoff: [] for cutoff in cutoff_list}
    same_language_irrelevant_shares: dict[int, list[float]] = {
        cutoff: [] for cutoff in cutoff_list
    }
    same_language_irrelevant_shares_at_100_by_query_lang: dict[str, list[float]] = {
        lang: [] for lang in diagnostic
    }

    for query_id, doc_scores in results.items():
        query_language = resolve_language(query_id, query_languages, schema)
        # A query whose language cannot be determined is dropped from every
        # metric, not just the language ones: partial coverage would make the
        # averages disagree with each other.
        if not query_language:
            continue
        ranked_doc_ids = [
            doc_id
            for doc_id, _score in sorted(
                doc_scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]
        relevant_doc_ids = {
            doc_id
            for doc_id, relevance in qrels.get(query_id, {}).items()
            if float(relevance) > 0.0
        }
        if not relevant_doc_ids:
            continue

        for cutoff in cutoff_list:
            top_doc_ids = ranked_doc_ids[:cutoff]
            if not top_doc_ids:
                continue

            relevant_seen = 0
            precision_sum = 0.0
            dcg = 0.0
            for rank_idx, doc_id in enumerate(top_doc_ids, start=1):
                if doc_id in relevant_doc_ids:
                    relevant_seen += 1
                    precision_sum += relevant_seen / rank_idx
                    dcg += 1.0 / math.log2(rank_idx + 1)
            recall_scores[cutoff].append(relevant_seen / len(relevant_doc_ids))
            # Normalised by how many relevant documents could fit in the cutoff,
            # so a query with more positives than slots is not scored as a miss.
            map_scores[cutoff].append(
                precision_sum / min(len(relevant_doc_ids), cutoff)
                if relevant_doc_ids
                else 0.0
            )
            ideal_relevant = min(len(relevant_doc_ids), cutoff)
            ideal_dcg = sum(
                1.0 / math.log2(rank_idx + 1)
                for rank_idx in range(1, ideal_relevant + 1)
            )
            ndcg_scores[cutoff].append(dcg / ideal_dcg if ideal_dcg else 0.0)

            unrelated_doc_ids = [
                doc_id for doc_id in top_doc_ids if doc_id not in relevant_doc_ids
            ]
            if not unrelated_doc_ids:
                same_language_irrelevant_share = 0.0
            else:
                same_language_unrelated = sum(
                    1
                    for doc_id in unrelated_doc_ids
                    if resolve_language(doc_id, corpus_languages, schema) == query_language
                )
                same_language_irrelevant_share = same_language_unrelated / len(
                    unrelated_doc_ids
                )
            same_language_irrelevant_shares[cutoff].append(
                same_language_irrelevant_share
            )
            if cutoff == 100 and query_language in same_language_irrelevant_shares_at_100_by_query_lang:
                same_language_irrelevant_shares_at_100_by_query_lang[
                    query_language
                ].append(same_language_irrelevant_share)

    for cutoff in cutoff_list:
        if recall_scores[cutoff]:
            metric_scores[f"recall_at_{cutoff}"] = round(
                sum(recall_scores[cutoff]) / len(recall_scores[cutoff]),
                SCORE_DIGITS,
            )
        if map_scores[cutoff]:
            metric_scores[f"map_at_{cutoff}"] = round(
                sum(map_scores[cutoff]) / len(map_scores[cutoff]),
                SCORE_DIGITS,
            )
        if ndcg_scores[cutoff]:
            metric_scores[f"ndcg_at_{cutoff}"] = round(
                sum(ndcg_scores[cutoff]) / len(ndcg_scores[cutoff]),
                SCORE_DIGITS,
            )
        if same_language_irrelevant_shares[cutoff]:
            metric_scores[f"same_language_irrelevant_share_at_{cutoff}"] = round(
                sum(same_language_irrelevant_shares[cutoff])
                / len(same_language_irrelevant_shares[cutoff]),
                SCORE_DIGITS,
            )

    # The per-language breakdown is reported at 100 only: at smaller cutoffs a
    # single language's queries give too few irrelevant documents to average.
    for query_language in diagnostic:
        values = same_language_irrelevant_shares_at_100_by_query_lang[query_language]
        if values:
            metric_scores[
                f"same_language_irrelevant_share_at_100_lang_{query_language}"
            ] = round(sum(values) / len(values), SCORE_DIGITS)
    return metric_scores


__all__ = [
    "RETRIEVAL_CUTOFFS",
    "SCORE_DIGITS",
    "compute_retrieval_metrics",
    "is_lower_better",
    "resolve_language",
]
