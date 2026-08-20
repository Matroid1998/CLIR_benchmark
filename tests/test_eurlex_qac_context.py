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
    assert built.external_references == [] and built.dropped_external_references == []


# -- articles of other acts --------------------------------------------------- #

def other(number: str, text: str = "other body", celex: str = "32004R0021") -> ctx.ArticleUnit:
    return ctx.ArticleUnit(
        eli_id=f"http://data.europa.eu/eli/reg/2004/21/art_{number}/oj",
        celex_id=celex, article_number=number,
        headings={"en": f"Other {number}"}, texts={"en": text},
        act_titles={"en": "Council Regulation (EC) No 21/2004 on sheep and goats"},
    )


def test_external_articles_get_their_own_block_with_a_cite_as_key() -> None:
    target = unit("4", "checks under Article 5 of Council Regulation (EC) No 21/2004")
    same = [unit("3", "same act")]
    ext = [other("5", "on-the-spot checks")]
    text = ctx.render_payload(target, same, external=ext)
    assert text.index(ctx.TARGET_HEADER) < text.index(ctx.CONTEXT_HEADER) < text.index(ctx.EXTERNAL_HEADER)
    assert "Cite as: 32004R0021:5" in text
    # same-act blocks never carry a key
    assert text.count("Cite as:") == 1
    # and the block is explicit when empty
    assert ctx.EXTERNAL_NONE in ctx.render_payload(target, same)


def test_one_cap_over_both_kinds_ranked_by_first_mention() -> None:
    index = object.__new__(ctx.ArticleIndex)
    index.by_eli, index.by_act = {}, {}
    target = unit("1", "cites both kinds")
    same = [unit("2"), unit("3")]
    ext = [other("5"), other("6"), other("7")]
    for u in [target] + same + ext:
        index.by_eli[u.eli_id] = u
    index.references = {target.eli_id: [u.eli_id for u in same]}
    index.external_references = {target.eli_id: [u.eli_id for u in ext]}
    index.first_mention = {
        (target.eli_id, same[0].eli_id): 300, (target.eli_id, same[1].eli_id): 900,
        (target.eli_id, ext[0].eli_id): 100, (target.eli_id, ext[1].eli_id): 500,
        (target.eli_id, ext[2].eli_id): 950,
    }
    built = index.build(target.eli_id, max_references=3)
    # kept: ext5 (100), same2 (300), ext6 (500); dropped: same3 (900), ext7 (950)
    assert [r.article_number for r in built.references] == ["2"]
    assert [ctx.external_key(u) for u in built.external_references] == ["32004R0021:5", "32004R0021:6"]
    assert built.dropped_references == ["3"]
    assert built.dropped_external_references == ["32004R0021:7"]
    assert built.involved_universe == ["1", "2", "32004R0021:5", "32004R0021:6"]


def test_same_act_and_other_act_numbers_cannot_collide() -> None:
    target = unit("4")
    same = [unit("15", "same-act fifteen")]
    ext = [other("15", "other-act fifteen"), other("5")]
    p = ctx.GenerationPayload(target, same, [], ctx.render_payload(target, same, external=ext),
                              external_references=ext)
    accepted, rejected = ctx.normalise_involved(["15", "32004R0021:15"], p)
    assert accepted == ["4", "15", "32004R0021:15"] and rejected == []
    # a bare number that only exists in the other act is not an honest citation
    accepted, rejected = ctx.normalise_involved(["4", "5"], p)
    assert accepted == ["4"] and rejected == ["5"]
    # surface variants of the key are normalised
    accepted, _ = ctx.normalise_involved(["32004r0021: Article 5", "Article 4"], p)
    assert accepted == ["4", "32004R0021:5"]
    # a full ELI is accepted too
    accepted, _ = ctx.normalise_involved([ext[1].eli_id], p)
    assert accepted == ["4", "32004R0021:5"]
    # "Article" in front of a key, and a key that names the target's own act
    accepted, rejected = ctx.normalise_involved(["Article 32004R0021:5", "32019R0904:15"], p)
    assert accepted == ["4", "15", "32004R0021:5"] and rejected == []
    assert ctx.involved_elis(["4", "32004R0021:5"], p) == [target.eli_id, ext[1].eli_id]


def test_annex_units_are_never_question_targets() -> None:
    from clir_bench.domains.legal.qac import eurlex_batch as batch
    index = object.__new__(ctx.ArticleIndex)
    anx = annex_unit(text="x" * 700)
    anx.texts = {lg: "x" * 700 for lg in ("en", "fr", "de", "es")}
    index.by_eli = {anx.eli_id: anx}
    index.by_act = {}
    index.references, index.annex_references, index.external_references = {}, {}, {}
    index.first_mention, index.status = {}, {anx.eli_id: {"complete": True}}
    chosen = batch.select(index, n=4, seed=1, languages=["en", "fr", "de", "es"],
                          modes=["technical"], include_amending=True)
    assert chosen == []
    assert index.build(anx.eli_id) is None


def test_own_act_annex_key_is_not_cross_act() -> None:
    target = unit("4")
    anx = annex_unit()           # same act as the target
    ext = other("5")             # another act
    p = ctx.GenerationPayload(target, [], [],
                              ctx.render_payload(target, [], annexes=[anx], external=[ext]),
                              external_references=[ext], annexes=[anx])
    out = gen.parse_candidates([
        {"question": "q", "answer": "a", "question_type": "x",
         "articles_involved": ["4", "32019R0904:anx_1"]},
        {"question": "q2", "answer": "a2", "question_type": "x",
         "articles_involved": ["4", "32004R0021:5"]},
    ], p, gen.MODE_TECHNICAL)
    assert [c.cross_act for c in out] == [False, True]
    assert [c.multi_article for c in out] == [True, True]


def test_parse_candidates_flags_cross_act() -> None:
    target = unit("4"); ext = [other("5")]
    p = ctx.GenerationPayload(target, [], [], ctx.render_payload(target, [], external=ext),
                              external_references=ext)
    out = gen.parse_candidates([
        {"question": "q", "answer": "a", "question_type": "x", "articles_involved": ["4", "32004R0021:5"]},
        {"question": "q2", "answer": "a2", "question_type": "x", "articles_involved": ["4"]},
    ], p, gen.MODE_TECHNICAL)
    assert [c.cross_act for c in out] == [True, False]
    assert [c.multi_article for c in out] == [True, False]
    assert out[0].involved_elis == [target.eli_id, ext[0].eli_id]


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


# -- annexes travel as keyed units --------------------------------------------- #

def annex_unit(subdiv: str = "anx_1", celex: str = "32019R0904",
               heading: str = "ANNEX I", text: str = "annex body") -> ctx.ArticleUnit:
    return ctx.ArticleUnit(
        eli_id=f"http://data.europa.eu/eli/reg/2019/904/{subdiv}/oj",
        celex_id=celex, article_number="",
        headings={"en": heading}, texts={"en": text},
        act_titles={"en": "Regulation (EU) 2019/904 on single-use plastics"},
        unit_type="annex",
    )


def test_annex_key_is_the_eli_subdivision() -> None:
    assert ctx.external_key(annex_unit()) == "32019R0904:anx_1"
    assert ctx.external_key(annex_unit("anx_pos1")) == "32019R0904:anx_pos1"


def test_annex_block_is_rendered_with_its_key() -> None:
    target = unit("4", "amounts fixed in the Annex")
    anx = annex_unit()
    text = ctx.render_payload(target, [], annexes=[anx])
    assert ctx.ANNEX_HEADER in text
    assert text.index(ctx.EXTERNAL_NONE) < text.index(ctx.ANNEX_HEADER)
    assert "[EN] ANNEX I" in text and "Cite as: 32019R0904:anx_1" in text
    # empty annex block is explicit
    assert ctx.ANNEX_NONE in ctx.render_payload(target, [])


def test_annex_tokens_are_keys_never_bare_numbers() -> None:
    target = unit("4")
    anx = annex_unit()   # same act as the target
    p = ctx.GenerationPayload(target, [], [], ctx.render_payload(target, [], annexes=[anx]),
                              annexes=[anx])
    assert p.involved_universe == ["4", "32019R0904:anx_1"]
    accepted, rejected = ctx.normalise_involved(["4", "32019R0904:anx_1"], p)
    assert accepted == ["4", "32019R0904:anx_1"] and rejected == []
    # the own-act collapse never turns an annex key into a bare number,
    # and surface variants normalise onto the subdivision
    accepted, _ = ctx.normalise_involved(["32019r0904:ANX 1"], p)
    assert accepted == ["4", "32019R0904:anx_1"]
    assert ctx.involved_elis(["32019R0904:anx_1"], p) == [anx.eli_id]


def test_shared_cap_ranks_annexes_with_everything_else() -> None:
    index = object.__new__(ctx.ArticleIndex)
    index.by_eli, index.by_act = {}, {}
    target = unit("1")
    same = unit("2")
    anx = annex_unit()
    ext = other("5")
    for u in (target, same, anx, ext):
        index.by_eli[u.eli_id] = u
    index.references = {target.eli_id: [same.eli_id]}
    index.annex_references = {target.eli_id: [anx.eli_id]}
    index.external_references = {target.eli_id: [ext.eli_id]}
    index.first_mention = {
        (target.eli_id, same.eli_id): 500,
        (target.eli_id, anx.eli_id): 100,
        (target.eli_id, ext.eli_id): 300,
    }
    built = index.build(target.eli_id, max_references=2)
    assert [ctx.external_key(u) for u in built.annexes] == ["32019R0904:anx_1"]
    assert [ctx.external_key(u) for u in built.external_references] == ["32004R0021:5"]
    assert built.references == [] and built.dropped_references == ["2"]
    assert built.involved_universe == ["1", "32004R0021:5", "32019R0904:anx_1"]


# -- target selection honours reference completeness --------------------------- #

def test_select_samples_only_reference_complete_articles(monkeypatch) -> None:
    from clir_bench.domains.legal.qac import eurlex_batch as batch

    monkeypatch.setattr(batch, "_quarantined", lambda: set())
    index = object.__new__(ctx.ArticleIndex)
    index.by_eli, index.by_act = {}, {}
    body = "x" * 700
    units = {n: ctx.ArticleUnit(f"eli/act{n}/art_1", f"ACT{n}", "1",
                                texts={lg: body for lg in ("en", "fr", "de", "es")})
             for n in range(6)}
    for u in units.values():
        index.by_eli[u.eli_id] = u
    index.references = {units[1].eli_id: [units[2].eli_id]}
    index.external_references = {units[3].eli_id: [units[4].eli_id]}
    index.first_mention = {}
    # 0: complete, no refs; 1: complete, one same-act ref; 3: complete, one
    # other-act ref; 2, 4: incomplete; 5: no status row at all
    index.status = {units[0].eli_id: {"complete": True},
                    units[1].eli_id: {"complete": True},
                    units[3].eli_id: {"complete": True, "cites_annex": True},
                    units[2].eli_id: {"complete": False},
                    units[4].eli_id: {"complete": False}}
    strata = (("no_refs", 0, 0, 0.5), ("one_ref", 1, 1, 0.5))
    chosen = batch.select(index, n=4, seed=1, languages=["en", "fr", "de", "es"],
                          modes=["technical"], strata=strata, include_amending=True)
    picked = {t.eli_id for t in chosen}
    assert picked == {units[0].eli_id, units[1].eli_id, units[3].eli_id}
    by_eli = {t.eli_id: t for t in chosen}
    assert by_eli[units[3].eli_id].n_external == 1 and by_eli[units[3].eli_id].n_refs == 0
    assert by_eli[units[3].eli_id].stratum == "one_ref" and by_eli[units[3].eli_id].cites_annex
    assert all(t.complete for t in chosen)

    everything = batch.select(index, n=6, seed=1, languages=["en", "fr", "de", "es"],
                              modes=["technical"], strata=strata, include_amending=True,
                              require_complete=False)
    # 3 wanted from no_refs (4 available incl. incomplete/unknown), 2 from one_ref
    assert len(everything) == 5
    assert not all(t.complete for t in everything)

    index.status = {}
    with pytest.raises(SystemExit):
        batch.select(index, n=4, seed=1, languages=["en"], modes=["technical"],
                     strata=strata, include_amending=True)
