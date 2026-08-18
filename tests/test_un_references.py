"""Citation extraction and resolution for the UN corpus.

Positive cases are real corpus citation strings; negative cases are the
look-alikes the extractor must ignore (internal references, dates, non-UN
symbols). Resolution tests use a small in-memory symbol map.
"""

from __future__ import annotations

from clir_bench.domains.legal.qac.un_references import (
    KIND_DECISION, KIND_ES, KIND_ROMAN, KIND_SC, KIND_SLASH, KIND_SYMBOL,
    Citation, anchored_block_index, extract_citations, normalise_symbol,
    referenced_docs, resolve_citations,
)

MAP = {
    "S/RES/872(1993)": "1993/s/res/872_1993_",
    "S/RES/1265(1999)": "1999/s/res/1265_1999_",
    "S/RES/1296(2000)": "2000/s/res/1296_2000_",
    "S/RES/1244(1999)": "1999/s/res/1244_1999_",
    "A/RES/51/210": "1997/a/res/51/210",
    "A/RES/57/270": "2003/a/res/57/270",
    "A/HRC/RES/17/4": "2011/a/hrc/res/17/4",
    "S/PRST/1994/16": "1994/s/prst/1994/16",
    "S/1994/565": "1994/s/1994/565",
    "A/53/500/ADD.1": "1998/a/53/500/add_1",
}


def kinds(cites):
    return [c.kind for c in cites]


def by_kind(cites, kind):
    return [c for c in cites if c.kind == kind]


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #

def test_sc_resolution_single():
    text = ("Reaffirming its resolution 872 (1993) of 5 October 1993 by which "
            "it established UNAMIR,")
    (c,) = extract_citations(text)
    assert c.kind == KIND_SC and c.symbol == "S/RES/872(1993)"


def test_sc_resolution_plural_run():
    text = "Recalling its resolutions 1265 (1999) and 1296 (2000) on the protection of civilians,"
    cites = extract_citations(text)
    assert [c.symbol for c in cites] == ["S/RES/1265(1999)", "S/RES/1296(2000)"]


def test_slash_resolution_with_candidates_chain():
    text = "the General Assembly, by its resolution 51/210 of 17 December 1996, established"
    (c,) = extract_citations(text)
    assert c.kind == KIND_SLASH
    assert c.candidates == ("A/RES/51/210", "A/HRC/RES/51/210", "E/RES/51/210")
    assert c.organ_hint == "General Assembly"


def test_section_letter_captured():
    text = "pursuant to resolution 57/270 B of 23 June 2003 on integrated follow-up"
    (c,) = extract_citations(text)
    assert c.section_letter == "B"


def test_bare_symbols_and_parenthesised():
    text = ("statements by the President (S/PRST/1994/16) and the report of "
            "the Secretary-General dated 13 May 1994 (S/1994/565)")
    cites = by_kind(extract_citations(text), KIND_SYMBOL)
    assert [c.symbol for c in cites] == ["S/PRST/1994/16", "S/1994/565"]


def test_symbol_addendum_suffix_kept():
    (c,) = extract_citations("as noted in A/53/500/Add.1 to the report")
    assert c.symbol == "A/53/500/ADD.1"


def test_prose_form_symbol_with_year_tail():
    (c,) = extract_citations("acting under S/RES/918 (1994) the Council imposed")
    assert c.symbol == "S/RES/918(1994)"


def test_explicit_symbol_not_doubled_as_slash_item():
    cites = extract_citations("as set out in resolution A/RES/51/210 of the Assembly")
    assert len(by_kind(cites, KIND_SYMBOL)) == 1
    assert not by_kind(cites, KIND_SLASH)


def test_non_un_symbols_rejected():
    text = ("compare OEA/Ser.L/III.15 and MSC/72/13/2 as well as HIV/AIDS "
            "figures and a 24/7 presence")
    assert extract_citations(text) == []


def test_roman_and_es_forms_are_unresolvable_kinds():
    cites = extract_citations(
        "recalling resolution 2819 (XXVI) and resolution ES-10/2 of the Assembly")
    assert kinds(cites) == [KIND_ROMAN, KIND_ES]
    assert all(c.candidates == () for c in cites)


def test_decision_kind():
    (c,) = extract_citations("Notwithstanding General Assembly decision 51/421, there was")
    assert c.kind == KIND_DECISION
    assert c.candidates == ("A/HRC/DEC/51/421",)


def test_paragraph_anchor_attached():
    text = ("as required by paragraph 11 (j) of Security Council resolution "
            "1244 (1999) of 10 June 1999")
    (c,) = extract_citations(text)
    assert c.kind == KIND_SC and c.symbol == "S/RES/1244(1999)"
    assert c.paragraph == 11


def test_internal_references_never_match():
    text = ("as noted in paragraph 5 above and in paragraph 3 of the present "
            "resolution, and again on 17 December 1996")
    assert extract_citations(text) == []


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #

def test_resolution_chain_and_normalisation():
    cites = resolve_citations(extract_citations(
        "by its resolution 51/210 and Human Rights Council resolution 17/4"), MAP)
    assert cites[0].doc_id == "1997/a/res/51/210"
    assert cites[1].doc_id == "2011/a/hrc/res/17/4"
    assert cites[1].symbol == "A/HRC/RES/17/4"


def test_normalise_symbol_variants():
    assert normalise_symbol("S/RES/1234 (2005)") == "S/RES/1234(2005)"
    assert normalise_symbol("s/1994/565.") == "S/1994/565"


def test_self_citation_dropped():
    cites = resolve_citations(extract_citations("RESOLUTION 872 (1993)"), MAP,
                              citing_doc_id="1993/s/res/872_1993_")
    assert cites[0].doc_id is None


def test_unresolved_citation_keeps_symbol():
    (c,) = resolve_citations(extract_citations("its resolution 48/141 of 1993"), MAP)
    assert c.doc_id is None and c.symbol == "A/RES/48/141"


def test_unresolved_symbol_follows_organ_hint():
    (c,) = resolve_citations(extract_citations(
        "pursuant to Human Rights Council resolution 10/27 of March 2009"), MAP)
    assert c.doc_id is None and c.symbol == "A/HRC/RES/10/27"


def test_referenced_docs_cap_and_order():
    text = ("Recalling its resolutions 1265 (1999) and 1296 (2000), resolution "
            "51/210, resolution 57/270, Human Rights Council resolution 17/4 "
            "and the statement S/PRST/1994/16")
    cites = resolve_citations(extract_citations(text), MAP)
    kept, dropped = referenced_docs(cites, max_references=4)
    assert [c.symbol for c in kept] == [
        "S/RES/1265(1999)", "S/RES/1296(2000)", "A/RES/51/210", "A/RES/57/270"]
    assert dropped == ["A/HRC/RES/17/4", "S/PRST/1994/16"]


def test_referenced_docs_deduplicates():
    text = "resolution 872 (1993) ... recalled resolution 872 (1993) again"
    cites = resolve_citations(extract_citations(text), MAP)
    kept, dropped = referenced_docs(cites)
    assert len(kept) == 1 and not dropped


# --------------------------------------------------------------------------- #
# Paragraph anchoring
# --------------------------------------------------------------------------- #

def test_anchored_block_first_match_wins():
    texts = [
        "Preamble text with no numbering at all here.",
        "1. Decides to establish the mission;\n2. Requests the Secretary-General to report;",
        "Annex\n1. The committee shall meet twice a year.",   # numbering restart
    ]
    assert anchored_block_index(texts, 2) == 1
    assert anchored_block_index(texts, 1) == 1                # first match, not the annex
    assert anchored_block_index(texts, 9) is None
