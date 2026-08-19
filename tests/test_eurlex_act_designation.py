"""The act-designation parser must fix the year/number order from the shape
alone and refuse anything it cannot read -- never fall back to the reverse."""

import pytest

from clir_bench.domains.legal.structure import act_designation as ad

CORPUS = {"32004R2003", "32015R0560", "32012R1268", "32004R0021", "32004R0601",
          "32003R1954", "32007R1234", "32012R0966", "32015L2366", "32014R0640",
          "32004L0109", "32014L0006"}


@pytest.mark.parametrize("surface, celex", [
    ("Regulation (EC) No 2792/1999", "31999R2792"),
    ("Regulation (EU) 2015/560", "32015R0560"),
    ("Regulation (EU) No 1268/2012", "32012R1268"),
    ("Council Regulation (EC) No 21/2004", "32004R0021"),
    ("Regulation (EU, Euratom) No 966/2012", "32012R0966"),
    ("Directive (EU) 2015/2366", "32015L2366"),
    ("Delegated Regulation (EU) No 640/2014", "32014R0640"),
    ("Directive 83/349/EEC", "31983L0349"),
    ("Directive 98/8/EC", "31998L0008"),
    ("Directive 2004/109/EC", "32004L0109"),
    ("Directive 2014/6/EU", "32014L0006"),
    ("Regulation (EEC) No 2913/92", "31992R2913"),
    ("Regulation (EC) 601/2004", "32004R0601"),
    ("Regulation (EC) 1954/2003", "32003R1954"),
    ("Regulation (EU) No 1303 /2013", "32013R1303"),
    ("Decision No 280/2004/EC", "32004D0280"),
    ("Decision 1999/468/EC", "31999D0468"),
    ("Framework Decision 2002/584/JHA", "32002F0584"),
    ("Council Regulation (ECSC, EEC, Euratom) No 300/76", "31976R0300"),
    ("Regulation (Euratom, EC) No 2185/96", "31996R2185"),
    ("Directive 2014/65", "32014L0065"),
    ("Directive 86/635", "31986L0635"),
    ("Regulation 1303/2013", "32013R1303"),
    ("Regulation 2015/1589", "32015R1589"),
])
def test_shape_fixes_the_order(surface, celex):
    assert ad.parse_act_designation(surface).celex == celex


def test_reversed_order_is_never_tried():
    # 32004R2003 is in the corpus; the surface names 32003R2004, which is not.
    ref = ad.parse_act_designation("Regulation (EC) No 2004/2003")
    assert ref.celex == "32003R2004"
    assert ad.resolve_celex("Regulation (EC) No 2004/2003", CORPUS) == (None, "out_of_corpus")


@pytest.mark.parametrize("surface, reason", [
    ("Decision 1999/468/EC", "doc_type_not_in_corpus"),
    ("Decision No 1082/2013/EU", "doc_type_not_in_corpus"),
    ("Treaty", "designator_unsupported"),
    ("EC Treaty", "designator_unsupported"),
    ("Protocol No 4", "designator_unsupported"),
    ("Financial Regulation", "no_identifier"),
    ("Staff Regulations", "no_identifier"),
    ("Directive", "no_identifier"),
    ("Regulation (EU) No", "truncated_surface"),
    ("Regulation 2004/2003", "malformed_surface"),
    ("Regulation 136/66/EEC", "malformed_surface"),
    ("Regulation (EC) No 5/07", "malformed_surface"),
])
def test_unresolvable_reasons(surface, reason):
    assert ad.resolve_celex(surface, CORPUS) == (None, reason)


def test_resolution_against_corpus():
    assert ad.resolve_celex("Council Regulation (EC) No 21/2004", CORPUS) == ("32004R0021", None)
    assert ad.resolve_celex("Directive 83/349/EEC", CORPUS) == (None, "out_of_corpus")
    assert ad.resolve_celex("Regulation (EC) No 1234/2007", CORPUS,
                            source_celex="32007R1234") == (None, "self_reference")
    assert ad.resolve_celex("Regulation (EC) No 1234/2007", CORPUS,
                            source_celex="32004R0021") == ("32007R1234", None)


def test_several_acts_in_one_citation_are_not_resolved_to_the_first():
    ref = ad.parse_act_designation("Regulations (EU) No 1093/2010")
    assert ref.plural and ref.celex == "32010R1093"
    assert ad.resolve_celex("Regulations (EU) No 1093/2010", {"32010R1093"}) == (None, "compound_surface")
    assert not ad.parse_act_designation("Regulation (EU) No 1093/2010").plural


def test_bare_designators_are_back_references():
    assert ad.is_bare_designator("Directive")
    assert ad.is_bare_designator("the Regulation")
    assert ad.is_bare_designator("Council Directive")
    assert not ad.is_bare_designator("Directive 2004/109/EC")
    assert not ad.is_bare_designator("Financial Regulation")


def test_modifiers_and_whitespace_are_ignored():
    assert ad.parse_act_designation("Seventh Council Directive 83/349/EEC").celex == "31983L0349"
    assert ad.parse_act_designation("Commission Implementing Regulation (EU) No 543/2011").celex == "32011R0543"
    assert ad.parse_act_designation("Regulation  (EC)  No  1234 / 2007").celex == "32007R1234"
