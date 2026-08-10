"""
EUR-Lex question generation: payload assembly and the ``articles_involved`` field.

The point of this flow is that an answer may legitimately cross a resolved
cross-reference, so the tests centre on the two things that makes possible:
the target/context separation in the payload, and the validation of what the
model declares it used.
"""

from __future__ import annotations

import pytest

from clir_bench.domains.legal.qac import eurlex_context as ctx
from clir_bench.domains.legal.qac import eurlex_generate as gen


def unit(number: str, text: str = "body", heading: str = "") -> ctx.ArticleUnit:
    return ctx.ArticleUnit(
        eli_id=f"http://data.europa.eu/eli/reg/2019/904/art_{number}/oj",
        celex_id="32019R0904", article_number=number,
        headings={"en": heading}, texts={"en": text},
    )


@pytest.fixture
def payload() -> ctx.GenerationPayload:
    target = unit("4", "prohibit the articles listed in Article 3", "Placing on the market")
    refs = [unit("3", "cotton bud sticks, cutlery, plates", "Covered products")]
    return ctx.GenerationPayload(target, refs, [], ctx.render_payload(target, refs))


# -- the payload keeps target and context apart ----------------------------- #

def test_target_and_references_are_separate_blocks(payload) -> None:
    """Concatenating them into one blob makes the model drift onto whichever
    article is most interesting, rather than the one we asked about."""
    text = payload.text
    assert ctx.TARGET_HEADER in text
    assert "### REFERENCED ARTICLES" in text
    assert text.index(ctx.TARGET_HEADER) < text.index("### REFERENCED ARTICLES")
    assert "Article 4 — Placing on the market" in text
    assert "Article 3 — Covered products" in text


def test_an_article_with_no_references_says_so_explicitly() -> None:
    target = unit("1", "scope")
    text = ctx.render_payload(target, [])
    assert "none" in text.lower()


def test_references_are_capped_and_the_drop_is_recorded() -> None:
    """One corpus article cites 256 others; sending them all buries the target."""
    index = object.__new__(ctx.ArticleIndex)
    index.by_eli = {}
    index.by_act = {"X": []}
    index.references = {}
    target = unit("1", "cites many")
    index.by_eli[target.eli_id] = target
    many = [unit(str(n), f"body {n}") for n in range(2, 12)]
    for u in many:
        index.by_eli[u.eli_id] = u
    index.references = {target.eli_id: [u.eli_id for u in many]}

    built = index.build(target.eli_id, max_references=3)
    assert [r.article_number for r in built.references] == ["2", "3", "4"]
    assert built.dropped_references == ["5", "6", "7", "8", "9", "10", "11"]


# -- articles_involved ------------------------------------------------------ #

def test_target_only_answer_declares_just_the_target(payload) -> None:
    accepted, rejected = ctx.normalise_involved(["4"], payload)
    assert accepted == ["4"] and rejected == []


def test_answer_crossing_a_reference_declares_both(payload) -> None:
    accepted, _ = ctx.normalise_involved(["3", "4"], payload)
    assert accepted == ["4", "3"]          # target first, then references in supply order


def test_target_is_added_even_if_the_model_forgets_it(payload) -> None:
    """The question is by construction about the target, so it is always involved."""
    accepted, _ = ctx.normalise_involved(["3"], payload)
    assert accepted == ["4", "3"]


def test_an_article_that_was_never_supplied_is_rejected(payload) -> None:
    """A number the model never received cannot be an honest citation."""
    accepted, rejected = ctx.normalise_involved(["4", "99"], payload)
    assert accepted == ["4"] and rejected == ["99"]


@pytest.mark.parametrize("raw", [["Article 3", "3"], "Article 3 and 4", ["  4 ", "3"]])
def test_surface_variants_are_normalised(raw) -> None:
    target = unit("4"); refs = [unit("3")]
    p = ctx.GenerationPayload(target, refs, [], ctx.render_payload(target, refs))
    accepted, _ = ctx.normalise_involved(raw, p)
    assert accepted == ["4", "3"]


def test_missing_field_degrades_to_target_only(payload) -> None:
    accepted, _ = ctx.normalise_involved(None, payload)
    assert accepted == ["4"]


def test_involved_numbers_map_back_to_eli_ids(payload) -> None:
    accepted, _ = ctx.normalise_involved(["3", "4"], payload)
    elis = ctx.involved_elis(accepted, payload)
    assert elis == [payload.target.eli_id, payload.references[0].eli_id]


# -- candidate parsing ------------------------------------------------------ #

def test_parse_candidates_flags_multi_article(payload) -> None:
    data = [
        {"question": "q1", "answer": "a1", "question_type": "scope_or_applicability",
         "articles_involved": ["4"]},
        {"question": "q2", "answer": "a2", "question_type": "obligation_or_prohibition",
         "articles_involved": ["3", "4"]},
    ]
    out = gen.parse_candidates(data, payload, gen.MODE_TECHNICAL)
    assert [c.multi_article for c in out] == [False, True]
    assert out[1].articles_involved == ["4", "3"]


def test_parse_candidates_drops_empty_pairs(payload) -> None:
    out = gen.parse_candidates(
        [{"question": "", "answer": "a"}, {"question": "q", "answer": ""}],
        payload, gen.MODE_TECHNICAL)
    assert out == []


# -- which language versions get sent --------------------------------------- #

def test_english_question_sends_english_only() -> None:
    assert ctx.payload_languages("en") == ("en",)


@pytest.mark.parametrize("language", ["fr", "de", "es"])
def test_non_english_question_sends_that_language_plus_english(language: str) -> None:
    """English is the pivot the references were extracted from, so it always
    travels with a non-English question language."""
    assert ctx.payload_languages(language) == (language, "en")


def test_payload_honours_the_language_selection() -> None:
    target = ctx.ArticleUnit(
        "eli/art_4", "32019R0904", "4",
        headings={"en": "Placing on the market", "fr": "Mise sur le marché",
                  "de": "Inverkehrbringen", "es": "Comercialización"},
        texts={"en": "EN body", "fr": "FR body", "de": "DE body", "es": "ES body"},
    )
    french = ctx.render_payload(target, [], languages=ctx.payload_languages("fr"))
    assert "[FR]" in french and "[EN]" in french
    assert "[DE]" not in french and "[ES]" not in french
    # the question language leads, English follows as the reference reading
    assert french.index("[FR]") < french.index("[EN]")

    english = ctx.render_payload(target, [], languages=ctx.payload_languages("en"))
    assert "[EN]" in english
    assert all(tag not in english for tag in ("[FR]", "[DE]", "[ES]"))
