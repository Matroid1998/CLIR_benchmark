"""
A quality rubric and the code that sums its scores must agree on the criteria.

They drifted twice. ``quality_overall`` sums ``quality_keys(mode)`` and
``_normalize_quality`` defaults a missing criterion to 1, so a rubric edited to
score different criteria raises nothing -- every candidate simply collects the
same near-floor quality score and the ranking silently degrades to faithfulness
alone. It is invisible in the CSV, which only carries ``qual_overall``.

Worse, a mode NAME is not unique across packs: `lookup` scores different
criteria in prompts_eurlex than in prompts_un, and UN's `practitioners` shares
none of the technical five. So the mode name cannot be the source of truth --
the rubric is, via ``rubric_keys``.
"""

from __future__ import annotations

import pytest

from clir_bench.core.grading import (
    _normalize_quality, grade_columns, quality_keys, rubric_keys,
)
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import un_batch, eurlex_batch

PACKS = {
    "un": (PromptPack("clir_bench.domains.legal.qac.prompts_un"),
           ("lookup", "practitioners", "semantic", "technical", "descriptive")),
    "eurlex": (PromptPack("clir_bench.domains.legal.qac.prompts_eurlex"),
               ("lookup", "fact_pattern")),
}
CASES = [(p, m) for p, (_, modes) in PACKS.items() for m in modes]


@pytest.mark.parametrize("pack,mode", CASES)
def test_every_rubric_declares_five_scored_criteria(pack: str, mode: str) -> None:
    keys = rubric_keys(PACKS[pack][0].quality(mode, "batch"))
    assert len(keys) == 5, (pack, mode, keys)
    assert len(set(keys)) == 5


@pytest.mark.parametrize("pack,mode", CASES)
def test_the_grade_is_summed_over_the_criteria_the_rubric_scores(pack: str, mode: str) -> None:
    """The regression: a perfect response must score 25, not silently less."""
    rubric = PACKS[pack][0].quality(mode, "batch")
    keys = rubric_keys(rubric)
    perfect = {k: 5 for k in keys}
    row = _normalize_quality(perfect, mode, keys)
    assert row["overall"] == 25, (pack, mode, row)


def test_the_same_mode_name_scores_differently_in_the_two_packs() -> None:
    """Why the mode name cannot be the source of truth."""
    un = rubric_keys(PACKS["un"][0].quality("lookup", "batch"))
    eurlex = rubric_keys(PACKS["eurlex"][0].quality("lookup", "batch"))
    assert un != eurlex
    assert "consequence" in un and "consequence" not in eurlex
    assert "focus" in eurlex and "focus" not in un


@pytest.mark.parametrize("mode", PACKS["un"][1])
def test_un_csv_has_a_column_for_every_criterion_its_rubrics_score(mode: str) -> None:
    """``FIELDS`` is a fixed tuple and DictWriter raises on an unknown key, so a
    rubric criterion with no column fails the write outright."""
    for key in rubric_keys(PACKS["un"][0].quality(mode, "batch")):
        assert f"qual_{key}" in un_batch.FIELDS, (mode, key)


@pytest.mark.parametrize("pack,mode", CASES)
def test_grade_columns_emits_the_rubric_criteria_not_the_mode_default(pack: str, mode: str) -> None:
    keys = rubric_keys(PACKS[pack][0].quality(mode, "batch"))
    quality = _normalize_quality({k: 4 for k in keys}, mode, keys)
    row = grade_columns({"grounding": 5, "precision": 5, "numerical_fidelity": 5},
                        quality, mode)
    for key in keys:
        assert row[f"qual_{key}"] == 4
    # nothing from the mode-name default leaks in when the rubric disagrees
    for stale in set(quality_keys(mode)) - set(keys):
        assert f"qual_{stale}" not in row


def test_both_batch_drivers_default_to_the_same_generator() -> None:
    assert un_batch.DEFAULT_GEN_MODEL == eurlex_batch.DEFAULT_GEN_MODEL == "gpt-5.6-luna"
