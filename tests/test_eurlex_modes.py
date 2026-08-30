"""
EUR-Lex generation is exactly two practitioner modes: ``lookup`` and
``fact_pattern``. The three earlier modes (technical, semantic, descriptive) are
gone from this pack -- ``descriptive`` survives only in the UN pack.

Both new modes are fact-extraction modes and therefore reuse the *technical*
quality columns, so ``core.grading`` needs no per-mode branch. What is new is
that each mode emits fields the other does not: ``lookup`` renders every
question twice (with and without the target act's identifier) and reports its
regime anchor; ``fact_pattern`` reports the particulars its situation was built
from. These tests pin that split, because a field leaking across modes is
invisible in the CSV -- it just silently fills the wrong column.
"""

from __future__ import annotations

import pytest

from clir_bench.core.grading import (
    TECHNICAL_QUALITY_FIELDS, TECHNICAL_QUALITY_KEYS, quality_fields, quality_keys,
)
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import eurlex_batch as batch
from clir_bench.domains.legal.qac import eurlex_context as ctx
from clir_bench.domains.legal.qac import eurlex_generate as gen

EURLEX = PromptPack("clir_bench.domains.legal.qac.prompts_eurlex")
LANGUAGES = ("de", "en", "es", "fr", "zh")


def unit(number: str, text: str = "body", heading: str = "") -> ctx.ArticleUnit:
    return ctx.ArticleUnit(
        eli_id=f"http://data.europa.eu/eli/reg/2019/904/art_{number}/oj",
        celex_id="32019R0904", article_number=number,
        headings={"en": heading}, texts={"en": text},
    )


@pytest.fixture
def payload() -> ctx.GenerationPayload:
    target = unit("4", "prohibit the articles listed in Article 3", "Placing on the market")
    return ctx.GenerationPayload(target, [], [], ctx.render_payload(target, []))


# -- the pack holds two modes and only two ---------------------------------- #

def test_the_pack_declares_exactly_the_two_modes() -> None:
    assert gen.MODES == (gen.MODE_LOOKUP, gen.MODE_FACT_PATTERN)
    assert not hasattr(gen, "MODE_TECHNICAL")
    assert not hasattr(gen, "MODE_SEMANTIC")
    assert not hasattr(gen, "MODE_DESCRIPTIVE")


@pytest.mark.parametrize("mode", gen.MODES)
def test_every_mode_has_a_prompt_in_every_language(mode: str) -> None:
    assert EURLEX.available_languages(mode) == LANGUAGES
    for language in LANGUAGES:
        assert EURLEX.generation(mode, language)


@pytest.mark.parametrize("mode", ("technical", "semantic", "descriptive"))
def test_the_retired_modes_are_gone(mode: str) -> None:
    """A leftover file would still be loadable, so absence has to be asserted."""
    assert EURLEX.available_languages(mode) == ()
    assert not EURLEX.has("verifiers", f"{mode}_batch.txt")


# -- the graders ------------------------------------------------------------ #

@pytest.mark.parametrize("mode", gen.MODES)
def test_both_modes_use_the_technical_quality_columns(mode: str) -> None:
    assert quality_keys(mode) == TECHNICAL_QUALITY_KEYS
    assert quality_fields(mode) == TECHNICAL_QUALITY_FIELDS


@pytest.mark.parametrize("mode", gen.MODES)
def test_every_mode_has_a_quality_verifier_emitting_those_columns(mode: str) -> None:
    rubric = EURLEX.quality(mode, "batch")
    for key in TECHNICAL_QUALITY_KEYS:
        assert f'"{key}": <1-5>' in rubric
    assert "retrievability" not in rubric.lower()   # that is the semantic rubric


def test_each_verifier_carries_its_defining_check() -> None:
    assert "ANCHOR CHECK" in EURLEX.quality(gen.MODE_LOOKUP, "batch")
    assert "FACT-PATTERN CHECK" in EURLEX.quality(gen.MODE_FACT_PATTERN, "batch")
    for mode in gen.MODES:
        # both modes forbid identifiers in the question they are shown
        assert "identifier-leak" in EURLEX.quality(mode, "batch")


# -- the mode-specific fields do not cross over ----------------------------- #

LOOKUP_JSON = {
    "question": "Must a UCITS management company disclose indirect holdings?",
    "question_cited": "Under Directive 2009/65/EC, must a UCITS management company disclose indirect holdings?",
    "instrument_short_name": "UCITS Directive",
    "anchor": "UCITS management company",
    "answer": "the identities of the shareholders",
    "question_type": "condition_or_prerequisite",
    "articles_involved": ["4"],
}
FACT_PATTERN_JSON = {
    "question": "A water utility runs a design contest and the jury adds new criteria. Is that allowed?",
    "particulars": ["water utility", "design contest", "criteria not in the contest notice"],
    "answer": "solely on the basis of the criteria indicated in the contest notice",
    "question_type": "obligation_or_prohibition",
    "articles_involved": ["4"],
}


def test_lookup_captures_its_own_fields(payload) -> None:
    (c,) = gen.parse_candidates([LOOKUP_JSON], payload, gen.MODE_LOOKUP)
    assert c.question_cited.startswith("Under Directive 2009/65/EC")
    assert c.instrument_short_name == "UCITS Directive"
    assert c.anchor == "UCITS management company"
    assert c.particulars == []


def test_fact_pattern_captures_its_own_fields(payload) -> None:
    (c,) = gen.parse_candidates([FACT_PATTERN_JSON], payload, gen.MODE_FACT_PATTERN)
    assert c.particulars == ["water utility", "design contest",
                             "criteria not in the contest notice"]
    assert (c.question_cited, c.instrument_short_name, c.anchor) == ("", "", "")


def test_a_field_from_the_other_mode_is_discarded(payload) -> None:
    """The prompts are near-identical siblings, so a model that has seen both
    can emit the wrong extra field. It must not reach the row."""
    (c,) = gen.parse_candidates([LOOKUP_JSON | {"particulars": ["x", "y"]}],
                                payload, gen.MODE_LOOKUP)
    assert c.particulars == []
    (c2,) = gen.parse_candidates([FACT_PATTERN_JSON | {"anchor": "leaked"}],
                                 payload, gen.MODE_FACT_PATTERN)
    assert c2.anchor == ""


@pytest.mark.parametrize("raw", [None, "null", "None", "  ", "NULL"])
def test_absent_short_name_is_empty_not_the_word_null(raw, payload) -> None:
    """The prompt says to write null when no conventional short name exists; a
    model told that sometimes writes the *string*, which would land in the CSV."""
    (c,) = gen.parse_candidates([LOOKUP_JSON | {"instrument_short_name": raw}],
                                payload, gen.MODE_LOOKUP)
    assert c.instrument_short_name == ""


def test_particulars_join_on_a_separator_that_is_not_the_comma(payload) -> None:
    """Particulars routinely contain commas, so the comma join used for article
    lists would split one particular into several."""
    (c,) = gen.parse_candidates(
        [FACT_PATTERN_JSON | {"particulars": ["40 tonnes, placed last year", "not reported"]}],
        payload, gen.MODE_FACT_PATTERN)
    (row,) = gen.rows_for(payload, [c], mode=gen.MODE_FACT_PATTERN, language="en")
    assert row["particulars"].split(gen.PARTICULAR_SEP) == [
        "40 tonnes, placed last year", "not reported"]


# -- skipping a boilerplate-only article is a result, not a failure --------- #

def test_a_skip_is_recognised_and_yields_no_candidates(payload) -> None:
    data = [{"skip_reason": "transposition clause only"}]
    assert gen.is_skip(data)
    assert gen.skip_reason(data) == "transposition clause only"
    assert gen.parse_candidates(data, payload, gen.MODE_LOOKUP) == []


def test_real_candidates_are_not_mistaken_for_a_skip() -> None:
    assert not gen.is_skip([LOOKUP_JSON])
    assert not gen.is_skip([])
    assert gen.skip_reason([LOOKUP_JSON]) == ""


# -- the CSV schema carries the new columns --------------------------------- #

def test_the_batch_schema_covers_every_generated_column(payload) -> None:
    (c,) = gen.parse_candidates([LOOKUP_JSON], payload, gen.MODE_LOOKUP)
    (row,) = gen.rows_for(payload, [c], mode=gen.MODE_LOOKUP, language="en")
    for column in ("question_cited", "instrument_short_name", "anchor", "particulars"):
        assert column in row
        assert column in batch.FIELDS
    assert "framing" not in row and "framing" not in batch.FIELDS
