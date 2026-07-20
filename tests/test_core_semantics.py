"""
Behaviour that datasets already depend on.

These cover the parts where a subtle change would silently alter published data
rather than raise: relevance semantics, grading arithmetic, and the guards
around appending to an existing dataset.
"""

from __future__ import annotations

import pytest

from clir_bench.core import corpus as corpus_io
from clir_bench.core import grading, publish, qagen
from clir_bench.core.domain import CorpusSchema

SCHEMA = CorpusSchema(
    fields=("id", "language", "title", "abstract", "context", "family"),
    family_field="family",
    text_fields=("context", "abstract", "title"),
)


def _corpus() -> list[dict]:
    return [
        {"id": "P1_en", "language": "en", "title": "T-en", "context": "C-en", "family": "P1"},
        {"id": "P1_de", "language": "de", "title": "T-de", "context": "C-de", "family": "P1"},
        {"id": "P1_fr", "language": "fr", "title": "T-fr", "context": "C-fr", "family": "P1"},
        {"id": "P2_en", "language": "en", "title": "T2", "context": "C2", "family": "P2"},
    ]


# --------------------------------------------------------------------------- #
# Relevance
# --------------------------------------------------------------------------- #

def test_every_language_version_is_relevant() -> None:
    """A query about a document is answered by any of its translations."""
    qac = [{"corpus_id": "P1_en", "question_language": "de", "question": "q", "answer": "a", "family": "P1"}]
    configs = publish.build_retrieval_configs(_corpus(), qac, SCHEMA)

    relevant = {row["corpus-id"] for row in configs.qrels}
    assert relevant == {"P1_en", "P1_de", "P1_fr"}
    assert "P2_en" not in relevant


def test_cross_language_variant_drops_same_language_versions() -> None:
    qac = [{"corpus_id": "P1_en", "question_language": "de", "question": "q", "answer": "a", "family": "P1"}]
    configs = publish.build_retrieval_configs(_corpus(), qac, SCHEMA)

    cross = {row["corpus-id"] for row in configs.cross_language_qrels}
    assert cross == {"P1_en", "P1_fr"}, "the German version must not count for a German query"


def test_cross_language_falls_back_rather_than_leaving_a_query_unanswerable() -> None:
    """A query with no cross-language target keeps its positives.

    Emptying the set would make the query unscoreable and quietly depress recall.
    """
    corpus = [{"id": "P3_en", "language": "en", "context": "C", "family": "P3"}]
    qac = [{"corpus_id": "P3_en", "question_language": "en", "question": "q", "answer": "a", "family": "P3"}]
    configs = publish.build_retrieval_configs(corpus, qac, SCHEMA)

    assert {row["corpus-id"] for row in configs.cross_language_qrels} == {"P3_en"}


def test_query_ids_are_deterministic_and_unique() -> None:
    qac = [
        {"corpus_id": "P1_en", "question_language": "de", "question": "q1", "answer": "a", "family": "P1"},
        {"corpus_id": "P1_en", "question_language": "de", "question": "q2", "answer": "a", "family": "P1"},
    ]
    configs = publish.build_retrieval_configs(_corpus(), qac, SCHEMA)
    ids = [row["_id"] for row in configs.queries]

    assert ids[0] == "P1_en_q_de"
    assert len(set(ids)) == len(ids), "a collision must be disambiguated, not silently reused"


def test_translated_queries_are_flagged() -> None:
    qac = [
        {"corpus_id": "P1_en", "question_language": "de", "question": "q", "answer": "a", "family": "P1"},
        {"corpus_id": "P1_en", "question_language": "en", "question": "q", "answer": "a", "family": "P1"},
    ]
    configs = publish.build_retrieval_configs(_corpus(), qac, SCHEMA)

    assert configs.queries[0]["is_synthetic_translation"] is True
    assert configs.queries[1]["is_synthetic_translation"] is False


# --------------------------------------------------------------------------- #
# Grading
# --------------------------------------------------------------------------- #

def test_scores_are_sums_of_their_sub_scores() -> None:
    faith = {"grounding": 5, "precision": 4, "numerical_fidelity": 3}
    quality = {
        "search_bar_realism": 5,
        "specificity": 4,
        "phrasing_economy": 3,
        "focus": 2,
        "linguistic_quality": 1,
    }
    assert grading.faith_overall(faith) == 12
    assert grading.quality_overall(quality, grading.MODE_TECHNICAL) == 15
    assert grading.total_score(faith, quality, grading.MODE_TECHNICAL) == 27


def test_modes_have_different_quality_rubrics() -> None:
    technical = set(grading.quality_keys(grading.MODE_TECHNICAL))
    semantic = set(grading.quality_keys(grading.MODE_SEMANTIC))
    assert technical != semantic
    assert "linguistic_quality" in technical & semantic


def test_candidates_rank_by_total_score() -> None:
    pairs = [{"question": "q1", "answer": "a"}, {"question": "q2", "answer": "a"}]
    faith = [{"overall": 3}, {"overall": 9}]
    quality = [{"overall": 5}, {"overall": 5}]

    ranked = grading.rank_candidates(pairs, faith, quality, grading.MODE_TECHNICAL)
    assert [c.qa["question"] for c in ranked] == ["q2", "q1"]


# --------------------------------------------------------------------------- #
# Generation plumbing
# --------------------------------------------------------------------------- #

def test_random_missing_asks_in_a_language_the_document_lacks() -> None:
    """This strategy is what makes queries genuinely cross-lingual."""
    for _ in range(20):
        chosen = qagen.pick_target_languages(
            qagen.STRATEGY_RANDOM_MISSING, ["en", "de"], ["en", "de", "fr", "zh"]
        )
        assert chosen[0] in {"fr", "zh"}


def test_strategy_all_asks_in_every_language() -> None:
    chosen = qagen.pick_target_languages(qagen.STRATEGY_ALL, ["en"], ["en", "de", "fr"])
    assert chosen == ["en", "de", "fr"]


def test_quotas_are_even_and_exhaustive() -> None:
    quotas = qagen.allocate_quotas(10, (1, 2, 3, 4))
    assert sum(quotas.values()) == 10
    assert max(quotas.values()) - min(quotas.values()) <= 1


def test_best_selection_is_per_document_and_language() -> None:
    rows = [
        {"family": "P1", "question_language": "en", "total_score": 10, "question": "low"},
        {"family": "P1", "question_language": "en", "total_score": 30, "question": "high"},
        {"family": "P1", "question_language": "de", "total_score": 20, "question": "de-only"},
    ]
    best = qagen.select_best(rows, SCHEMA)

    assert len(best) == 2
    assert {r["question"] for r in best} == {"high", "de-only"}


def test_output_schema_covers_both_modes() -> None:
    """One header for both modes, or their outputs cannot be merged."""
    fields = qagen.output_fieldnames(SCHEMA)
    assert "qual_search_bar_realism" in fields  # technical
    assert "qual_conceptual_framing" in fields  # semantic
    assert len(fields) == len(set(fields)), "duplicate column in the output schema"


# --------------------------------------------------------------------------- #
# Corpus I/O
# --------------------------------------------------------------------------- #

def test_multilingual_filter_keeps_whole_documents() -> None:
    kept, summary = corpus_io.filter_multilingual(
        _corpus(), SCHEMA, languages=["en", "de", "fr"], min_languages=2
    )
    assert {row["family"] for row in kept} == {"P1"}
    assert len(kept) == 3, "all language versions of a kept document must survive"
    assert summary["families_kept"] == 1


def test_appending_under_a_changed_schema_is_refused(tmp_path) -> None:
    """Appending rows with different columns silently corrupts a dataset."""
    path = tmp_path / "qac.csv"
    corpus_io.write_rows(path, [{"a": 1, "b": 2}], ["a", "b"])

    corpus_io.ensure_header(path, ["a", "b"])
    with pytest.raises(ValueError, match="unexpected header"):
        corpus_io.ensure_header(path, ["a", "b", "c"])


def test_passages_include_every_language(tmp_path) -> None:
    """Generators and graders see all versions, which grounds grading cross-lingually."""
    text = corpus_io.build_passages_text(_corpus()[:3], SCHEMA, order=("en", "de", "fr"))
    assert "[EN]" in text and "[DE]" in text and "[FR]" in text
    assert text.index("[EN]") < text.index("[DE]") < text.index("[FR]")


def test_publishing_without_an_attribution_is_refused() -> None:
    bundle = publish.DatasetBundle()
    bundle.add("corpus", [{"_id": "P1_en"}])
    with pytest.raises(ValueError, match="attribution"):
        publish.build_card(title="T", description="D", attribution="  ", bundle=bundle)
