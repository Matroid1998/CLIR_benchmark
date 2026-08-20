"""
The EUR-Lex reference extractor, pinned to the cases that broke it.

Every test below except the basics comes from a defect the hand audit of the
first pilot run actually found, so each one is a regression guard rather than a
restatement of the implementation.
"""

from __future__ import annotations

import pytest

from clir_bench.domains.legal.structure import references as refs


def targets(text: str) -> list[str]:
    """Article numbers an enumeration resolves to, ignoring classification."""
    out: list[str] = []
    log: list[dict] = []
    for enumeration in refs.find_enumerations(text):
        out += [t["number"] for t in refs.expand(enumeration, log=log, source="t")]
    return out


def kinds(text: str) -> list[tuple[str, str]]:
    return [refs.classify(text, e)[:2] for e in refs.find_enumerations(text)]


# -- step 1 and 2: matching, ranges, lists ---------------------------------- #

def test_single_article() -> None:
    assert targets("as set out in Article 5 of the annex") == ["5"]


def test_list_is_expanded() -> None:
    assert targets("referred to in Articles 3, 5 and 7 hereof") == ["3", "5", "7"]


def test_range_is_expanded_inclusively() -> None:
    assert targets("in accordance with Articles 12 to 15") == ["12", "13", "14", "15"]


def test_mixed_list_and_range() -> None:
    assert targets("Articles 8, 11, 25 to 27 and 42") == ["8", "11", "25", "26", "27", "42"]


def test_paragraph_is_not_mistaken_for_an_article() -> None:
    # "(2)" is a paragraph of Article 5, not a reference to Article 2.
    assert targets("Article 5(1) and (2) shall apply") == ["5"]


def test_repeated_article_word_is_one_enumeration() -> None:
    assert targets("in violation of Article 16, Article 17 or Article 18") == ["16", "17", "18"]


# -- regression: list resuming after a parenthesised sub-reference ---------- #

def test_list_resumes_after_parenthesised_paragraph() -> None:
    """"Articles 2(2) and (3), 4 and 5(2)" cites articles 2, 4 and 5.

    Stopping at the first "(3)" lost articles 4 and 5 entirely.
    """
    assert targets("By way of derogation from Articles 2(2) and (3), 4 and 5(2),") == \
        ["2", "4", "5"]


# -- regression: overlapping heads -> duplicate edges ----------------------- #

def test_long_chain_is_a_single_enumeration() -> None:
    """A chain repeating "Article" must not be re-parsed from each repetition."""
    text = ("pursuant to Articles 110 and 111, Article 125(1), Article 127, "
            "Articles 132, 135 and 136, and Articles 380 to 382.")
    found = refs.find_enumerations(text)
    assert len(found) == 1
    assert targets(text) == ["110", "111", "125", "127", "132", "135", "136",
                             "380", "381", "382"]


# -- step 3 before step 4: the ordering the spec fixes ---------------------- #

def test_of_this_regulation_is_internal() -> None:
    assert kinds("pursuant to Article 34 of this Regulation shall") == \
        [("internal", "this_act_whitelist")]


def test_of_named_act_is_external() -> None:
    assert kinds("in Article 5 of Regulation (EC) No 1/2003 the") == \
        [("external", "external_of_act")]


def test_bare_article_is_internal() -> None:
    assert kinds("the procedure referred to in Article 34(2) applies") == \
        [("internal", "bare_article")]


# -- regression: anaphoric act determiners --------------------------------- #

@pytest.mark.parametrize("phrase", [
    "and Article 4 of that Regulation shall apply",
    "as provided for in Article 30 of that Regulation, the",
    "in Article 7 of the said Directive, and",
])
def test_anaphoric_act_determiner_is_external(phrase: str) -> None:
    """"of that Regulation" points at an act named earlier, not at this one."""
    assert kinds(phrase) == [("external", "external_of_act")]


# -- regression: proper-noun modifiers before the designator ---------------- #

@pytest.mark.parametrize("phrase", [
    "as referred to in Article 1 of the Seventh Council Directive 83/349/EEC of",
    "laid down in Article 26 of the OECD Model Tax Convention on Income and",
])
def test_modified_act_name_is_external(phrase: str) -> None:
    assert kinds(phrase) == [("external", "external_of_act")]


def test_prose_cannot_bridge_to_a_later_designator() -> None:
    """A designator far right, reached only through ordinary prose, does not govern.

    The capitalisation guard is what stops this; under `re.I` a bare `[A-Z]`
    would match the lowercase words and make this external.
    """
    assert kinds("in Article 5 and the products listed in a regulation adopted later") == \
        [("internal", "bare_article")]


def test_thereof_is_routed_to_external() -> None:
    assert kinds("having regard to Article 43(2) thereof, and") == \
        [("external", "external_thereof")]


# -- segmentation: footnote apparatus must not contaminate text ------------- #

def test_footnote_marker_does_not_glue_a_digit_onto_the_text() -> None:
    """A footnote marker flush against a number must not extend it.

    "Article 5<sup>1</sup>" reading as "Article 51" would silently retarget the
    edge to a different article.
    """
    from clir_bench.domains.legal.structure.segment import html_to_text
    html = ('<p>referred to in Article 5<sup class="fmx-footnote-ref">'
            '<a href="#n1">1</a></sup>. Next sentence.</p>')
    assert "Article 51" not in html_to_text(html)
    assert "Article 5" in html_to_text(html)


def test_footnote_body_is_not_part_of_article_text() -> None:
    from clir_bench.domains.legal.structure.segment import html_to_text
    html = ('<p>the enacting text.</p><section class="fmx-footnotes"><ol><li>'
            '<p>OJ L 302, 19.10.1992, p. 1.</p></li></ol></section>')
    out = html_to_text(html)
    assert "enacting text" in out
    assert "OJ L 302" not in out


# -- annex identity: the label, not the position in the zip ----------------- #

def test_annex_label_is_read_from_the_heading_not_the_position() -> None:
    from clir_bench.domains.legal.structure.segment import annex_label
    assert annex_label("ANNEX I") == "1"
    assert annex_label("ANNEX VII") == "7"
    assert annex_label("ANNEX VIIa") == "7a"
    # A preamble document ships alongside the annexes and carries no label; it
    # must not silently take the next annex's identifier.
    assert annex_label("Preamble to Annexes II to VI") is None


@pytest.mark.parametrize("heading,language", [
    ("ANNEX II", "en"), ("ANNEXE II", "fr"), ("ANHANG II", "de"), ("ANEXO II", "es"),
])
def test_annex_label_is_language_independent(heading: str, language: str) -> None:
    """The heading word differs per language; the identifier must not.

    Matching only the English word gave German and Spanish positional fallback
    ids, and every annex edge then failed the cross-language join.
    """
    from clir_bench.domains.legal.structure.segment import annex_label
    assert annex_label(heading, language) == "2"


@pytest.mark.parametrize("heading,language", [
    ("ANNEX 13a", "en"), ("ANHANG 13a", "de"),
    ("ANNEXE 13 bis", "fr"), ("ANEXO 13 bis", "es"),
])
def test_latin_ordinal_and_letter_suffixes_agree(heading: str, language: str) -> None:
    """"ANNEXE 13 bis" is "ANNEX 13a" -- same annex, so the same identifier."""
    from clir_bench.domains.legal.structure.segment import annex_label
    assert annex_label(heading, language) == "13a"


# -- annex references ------------------------------------------------------- #

def test_annex_reference_resolves_roman_numerals() -> None:
    found = refs.find_annex_references("as set out in Annex III to this Regulation")
    assert [refs.expand_annexes(r) for r in found] == [["3"]]
    assert found[0]["raw"] == "Annex III"


def test_annex_range_is_expanded() -> None:
    found = refs.find_annex_references("listed in Annexes II to V")
    assert refs.expand_annexes(found[0]) == ["2", "3", "4", "5"]


def test_correlation_table_is_not_a_source_of_edges() -> None:
    """A correlation table maps a repealed act's articles onto this one's.

    Every cell reads as a citation, so extracting from one would manufacture
    hundreds of edges the drafter never wrote.
    """
    table = " ".join(f"Article {i} Article {i + 100}" for i in range(1, 40))
    assert refs.looks_like_correlation_table(table)
    assert not refs.looks_like_correlation_table(
        "The requirements of Article 5 apply, and Article 7 sets the deadline.")


def test_sub_reference_does_not_absorb_a_list_marker_on_the_next_line() -> None:
    """"ARTICLE 13(1)\\n\\n(1) Telecommunications" -- the trailing (1) is a list
    marker for the next item, not a further sub-reference of Article 13."""
    found = refs.find_enumerations("REFERRED TO IN ARTICLE 13(1)\n\n(1) Telecommunications")
    assert found[0]["raw"] == "ARTICLE 13(1)"


def test_emphasis_boundary_does_not_glue_a_latin_ordinal_to_the_next_word() -> None:
    """Formex drops the space at an italic boundary.

    The OJ reads "artículos 97 octies y 97 nonies", but the XML holds
    `97 <HT TYPE="ITALIC">octies</HT>y 97` -- and EU drafting italicises exactly
    the Latin ordinals that suffix article numbers, so naive tag-stripping
    corrupts the identifiers this pipeline resolves.
    """
    from clir_bench.domains.legal.structure.segment import html_to_text
    out = html_to_text("<p>los artículos 97 <em>octies</em>y 97 <em>nonies</em>, la</p>")
    assert "octiesy" not in out
    assert "97 octies y 97 nonies" in out


@pytest.mark.parametrize("ordinal,letter", [
    ("bis", "a"), ("ter", "b"), ("quater", "c"), ("sexdecies", "o"),
    ("septdecies", "p"), ("vicies", "s"), ("tervicies", "v"),
])
def test_latin_ordinal_paradigm_matches_english_letters(ordinal, letter) -> None:
    """Confirmed by matched counts across the parallel corpus.

    A partial map mis-identifies the higher ordinals, and they are not rare --
    the pilot alone uses sixteen distinct ones.
    """
    from clir_bench.domains.legal.structure.segment import annex_label
    assert annex_label(f"ANNEXE 13 {ordinal}", "fr") == f"13{letter}"
    assert annex_label(f"ANNEX 13{letter}", "en") == f"13{letter}"


def test_longer_ordinal_is_not_shadowed_by_a_shorter_prefix() -> None:
    """"terdecies" must not parse as "ter" -- alternation is first-match."""
    from clir_bench.domains.legal.structure.segment import annex_label
    assert annex_label("ANNEXE 13 terdecies", "fr") == "13l"
    assert annex_label("ANNEXE 13 ter", "fr") == "13b"


# -- act identifiers: recall gaps and self-citation --------------------------- #

def surfaces(text: str) -> list[str]:
    return [refs.classify(text, e)[2] for e in refs.find_enumerations(text)]


def test_one_digit_act_number_is_kept_in_the_surface() -> None:
    assert surfaces("in Article 4 of Directive 98/8/EC the") == ["Directive 98/8/EC"]
    assert surfaces("under Article 2 of Directive 2014/6/EU,") == ["Directive 2014/6/EU"]


def test_whitespace_around_the_slash_does_not_truncate_the_surface() -> None:
    assert surfaces("Article 9 of Regulation (EU) No 1303 /2013 shall") == [
        "Regulation (EU) No 1303 /2013"]


def test_own_act_cited_by_identifier_is_internal() -> None:
    text = "as provided in Article 3 of Regulation (EC) No 1334/2008 and"
    (enum,) = refs.find_enumerations(text)
    assert refs.classify(text, enum, own_celex="32008R1334")[:2] == ("internal", "own_act_identifier")
    assert refs.classify(text, enum, own_celex="32009R0001")[:2] == ("external", "external_of_act")
    assert refs.classify(text, enum)[:2] == ("external", "external_of_act")


def test_anaphoric_citation_is_never_claimed_as_own_act() -> None:
    text = "Article 4 of that Regulation shall"
    (enum,) = refs.find_enumerations(text)
    kind, rule, _, anaphoric = refs.classify(text, enum, own_celex="32008R1334")
    assert (kind, rule, anaphoric) == ("external", "external_of_act", True)


def test_paragraph_range_is_not_an_article_range() -> None:
    # "41(2) to (5)" spans paragraphs of Article 41; 45 is the next list item,
    # not the end of a 41-45 range.
    assert targets("Articles 28(1) and (2), 38, 41(2) to (5), 45(1) and (3), 48") == [
        "28", "38", "41", "45", "48"]
    # A genuine article range still expands.
    assert targets("Articles 41(2) to 45(1)") == ["41", "42", "43", "44", "45"]


# -- annex citations: governing act and the bare "the Annex" ------------------- #

def annex_kinds(text: str) -> list[tuple[str, str]]:
    return [refs.classify_annex(text, r["start"], r["end"])[:2]
            for r in refs.find_annex_references(text)]


def test_annex_to_named_act_is_external() -> None:
    assert annex_kinds("set out in Annex I to Regulation (EC) No 376/2008.") == [
        ("external", "external_annex_of_act")]
    text = "fixed by Annex IV to Regulation (EC) No 2792/1999 for such aid"
    (r,) = refs.find_annex_references(text)
    kind, rule, surface, anaphoric = refs.classify_annex(text, r["start"], r["end"])
    assert (kind, surface, anaphoric) == ("external", "Regulation (EC) No 2792/1999", False)


def test_annex_to_this_act_is_internal() -> None:
    assert annex_kinds("listed in Annex II to this Regulation shall") == [
        ("internal", "annex_this_act")]
    assert annex_kinds("listed in Annex II of this Directive shall") == [
        ("internal", "annex_this_act")]


def test_annex_own_act_identifier_is_internal() -> None:
    text = "listed in Annex I to Regulation (EC) No 1334/2008 shall"
    (r,) = refs.find_annex_references(text)
    assert refs.classify_annex(text, r["start"], r["end"],
                               own_celex="32008R1334")[:2] == ("internal", "annex_own_act_identifier")


def test_annex_anaphora_is_split_by_direction() -> None:
    assert annex_kinds("in Annex III to that Regulation") == [("external", "external_annex_of_act")]
    assert annex_kinds("in Annex III thereto,") == [("external", "external_annex_thereto")]
    assert annex_kinds("in Annex III hereto,") == [("internal", "annex_this_act")]


def test_annex_bridge_carries_a_part_over_to_the_governing_act() -> None:
    assert annex_kinds("in Annex I, part A, to Regulation (EU) No 543/2011") == [
        ("external", "external_annex_of_act")]


def test_bare_annex_is_found_only_without_a_label() -> None:
    assert [r["raw"] for r in refs.find_bare_annex_references(
        "listed in the Annex. See the Annexes I and II and the Annex I")] == ["the Annex"]
    text = "amounts fixed in the Annex to this Regulation"
    (r,) = refs.find_bare_annex_references(text)
    assert refs.classify_annex(text, r["start"], r["end"])[:2] == ("internal", "annex_this_act")
    text2 = "amounts fixed in the Annex to Regulation (EC) No 376/2008"
    (r2,) = refs.find_bare_annex_references(text2)
    assert refs.classify_annex(text2, r2["start"], r2["end"])[0] == "external"


def test_roman_item_never_swallows_the_next_words_capital() -> None:
    # "C" of "Council" is not annex 100, and the governing act stays visible.
    text = "set out in Annex I to Council Regulation (EC) No 1234/2007"
    (r,) = refs.find_annex_references(text)
    assert r["raw"] == "Annex I"
    assert refs.classify_annex(text, r["start"], r["end"])[0] == "external"
    text2 = "listed in Annex II to Implementing Regulation (EU) No 543/2011"
    (r2,) = refs.find_annex_references(text2)
    assert r2["raw"] == "Annex II"
    assert refs.classify_annex(text2, r2["start"], r2["end"])[0] == "external"


def test_annex_citation_never_crosses_a_blank_line() -> None:
    assert refs.find_annex_references("header\n\nAnnex\n\nII to IV\n\nDefinition") == []
    (r,) = refs.find_annex_references("Annexes II\nto IV")
    assert r["raw"] == "Annexes II"


def test_bare_annex_survives_prose_starting_with_a_roman_letter() -> None:
    assert [r["raw"] for r in refs.find_bare_annex_references(
        "the Annex is amended and the Annex contains rules")] == ["the Annex", "the Annex"]
    assert refs.find_bare_annex_references("in the Annex I and the Annex V") == []


def test_non_act_governor_is_external_not_a_self_edge() -> None:
    text = "calculated as in Annex I to the standard IOC/T 20/Doc. No 15."
    (r,) = refs.find_annex_references(text)
    kind, rule, surface, _ = refs.classify_annex(text, r["start"], r["end"])
    assert (kind, rule) == ("external", "external_annex_nonact")
    # datives and infinitives stay internal
    for ok in ("amounts in Annex I to the competent authority",
               "criteria of Annex III to determine whether"):
        (rr,) = refs.find_annex_references(ok)
        assert refs.classify_annex(ok, rr["start"], rr["end"])[0] == "internal"


def test_annex_range_is_capped() -> None:
    ref = {"items": [
        {"label": "1", "number": 1, "suffix": "", "end": 0, "via_range": False},
        {"label": "500", "number": 500, "suffix": "", "end": 0, "via_range": True}]}
    assert refs.expand_annexes(ref) == ["1", "500"]
