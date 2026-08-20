"""Cross-act resolution: only in-corpus, unambiguously named acts get edges;
everything else is recorded with a reason; completeness follows from that."""

from __future__ import annotations

import json

import pytest

from clir_bench.domains.legal.structure import resolve_external as rx


def _corpus() -> rx.Corpus:
    corpus = rx.Corpus()
    corpus.act_eli = {
        "32004R0021": "http://data.europa.eu/eli/reg/2004/21/oj",
        "32004R0796": "http://data.europa.eu/eli/reg_impl/2004/796/oj",
        "32009R0999": "http://data.europa.eu/eli/reg/2009/999/oj",
    }
    for celex, numbers in (("32004R0021", ["1", "3", "5"]),
                           ("32004R0796", ["1", "2"]),
                           ("32009R0999", ["1"])):
        for lg in ("en", "fr", "de", "es"):
            corpus.inventories[celex][lg].update(numbers)
        corpus.articles_en[celex] = [
            (n, f"{corpus.act_eli[celex][:-3]}/art_{n}/oj") for n in numbers]
    # French version of 32004R0021 lacks Article 5.
    corpus.inventories["32004R0021"]["fr"].discard("5")
    corpus.quarantined.add("32009R0999")
    return corpus


def _row(surface_form: str, act: str, *, anaphoric=False, rule="external_of_act",
         source="http://data.europa.eu/eli/reg_impl/2004/796/art_2/oj",
         celex="32004R0796") -> dict:
    return {"source_article_id": source, "source_celex": celex,
            "source_unit_type": "article", "source_article_number": "2",
            "surface_form": surface_form, "char_start": 10, "char_end": 10 + len(surface_form),
            "target_act_surface": act, "target_act_anaphoric": anaphoric,
            "rule": rule, "resolved": False,
            "available_languages": ["en", "fr", "de", "es"], "surface_language": "en"}


def test_named_in_corpus_act_yields_edges_validated_against_its_inventory():
    edges, misses = rx.resolve_row(_row("Articles 3, 5 and 99", "Council Regulation (EC) No 21/2004"), _corpus())
    assert [e["target_article_number"] for e in edges] == ["3", "5"]
    assert edges[0]["target_article_id"] == "http://data.europa.eu/eli/reg/2004/21/art_3/oj"
    assert edges[0]["target_celex"] == "32004R0021"
    assert edges[0]["available_languages"] == ["en", "fr", "de", "es"]
    # Article 5 is missing from the French version, so the edge says so.
    assert edges[1]["available_languages"] == ["en", "de", "es"]
    assert [m["reason"] for m in misses] == ["target_article_not_in_inventory"]
    assert misses[0]["target_article_number"] == "99"


@pytest.mark.parametrize("row, reason", [
    (_row("Article 4", "that Regulation", anaphoric=True), "anaphoric"),
    (_row("Article 4", "", rule="external_thereof", anaphoric=True), "anaphoric"),
    (_row("Article 4", "the Directive"), "anaphoric"),
    (_row("Article 4", "Regulation (EC) No 2792/1999"), "out_of_corpus"),
    (_row("Article 4", "Decision 1999/468/EC"), "doc_type_not_in_corpus"),
    (_row("Article 87", "Treaty"), "designator_unsupported"),
    (_row("Article 87", "Financial Regulation"), "no_identifier"),
    (_row("Article 87", "Regulation (EU) No"), "truncated_surface"),
    (_row("Article 1", "Regulation (EC) No 796/2004"), "self_reference"),
    (_row("Article 1", "Regulation (EC) No 999/2009"), "target_act_quarantined"),
])
def test_unresolved_rows_carry_a_reason(row, reason):
    edges, misses = rx.resolve_row(row, _corpus())
    assert edges == []
    assert [m["reason"] for m in misses] == [reason]


def test_parsed_celex_is_recorded_even_when_unresolved():
    _, (miss,) = rx.resolve_row(_row("Article 4", "Regulation (EC) No 2792/1999"), _corpus())
    assert miss["parsed_celex"] == "31999R2792"


def test_reversed_order_is_not_a_resolution():
    # 32004R0021 exists; "No 21/2004" names it. "No 2004/21" is not read the
    # other way round: a two-digit year below 52 is not a year, so it is refused
    # outright rather than flipped into a hit.
    edges, misses = rx.resolve_row(_row("Article 3", "Regulation (EC) No 2004/21"), _corpus())
    assert edges == [] and misses[0]["reason"] == "malformed_surface"


def test_status_complete_only_when_every_citation_is_resolved():
    complete = rx.status_row("e", "c", "1", None)
    assert complete["complete"] and complete["n_internal"] == 0

    tally = rx._Tally()
    tally.internal.add("x"); tally.external.add("y")
    tally.annex_targets.add("anx")
    row = rx.status_row("e", "c", "1", tally)
    assert row["complete"] and row["cites_annex"] and row["n_external_resolved"] == 1

    tally.unresolved["out_of_corpus"] += 1
    assert not rx.status_row("e", "c", "1", tally)["complete"]

    tally2 = rx._Tally(); tally2.internal_not_in_inventory = 1
    assert not rx.status_row("e", "c", "1", tally2)["complete"]


def test_resolve_end_to_end(tmp_path):
    corpus = _corpus()
    src = "http://data.europa.eu/eli/reg_impl/2004/796/art_2/oj"
    other = "http://data.europa.eu/eli/reg_impl/2004/796/art_1/oj"
    ext = tmp_path / "external.jsonl"
    ext.write_text("\n".join(json.dumps(r) for r in [
        _row("Articles 3 and 5", "Council Regulation (EC) No 21/2004"),
        _row("Article 4", "Regulation (EC) No 2792/1999", source=other),
        _row("Article 87", "Treaty"),
    ]) + "\n")
    internal = tmp_path / "internal.jsonl"
    internal.write_text(json.dumps({
        "source_article_id": src, "target_article_id": other, "source_celex": "32004R0796",
        "source_unit_type": "article", "target_unit_type": "article", "char_start": 3}) + "\n")
    dropped = tmp_path / "dropped.jsonl"
    dropped.write_text("")
    edges_out, unres_out, status_out = (tmp_path / n for n in ("e.jsonl", "u.jsonl", "s.jsonl"))
    summary = rx.resolve(external_path=ext, internal_path=internal, dropped_path=dropped,
                         corpus=corpus, edges_out=edges_out, unresolved_out=unres_out,
                         status_out=status_out, stats_out=tmp_path / "stats.json")
    assert (tmp_path / "stats.json").exists()
    assert summary["edges"] == 2 and summary["unresolved"] == 2
    assert summary["distinct_target_acts"] == 1
    status = {json.loads(l)["eli_id"]: json.loads(l) for l in status_out.read_text().splitlines()}
    assert len(status) == 6  # every English article in the corpus fixture
    # art_2 cites art_1 (internal), Articles 3+5 of 21/2004 (external), and the Treaty (unresolved).
    assert status[src]["n_internal"] == 1
    assert status[src]["n_external_resolved"] == 2
    assert status[src]["unresolved_reasons"] == {"designator_unsupported": 1}
    assert status[src]["complete"] is False
    # art_1 cites only an out-of-corpus act -> incomplete; untouched articles are complete.
    assert status[other]["complete"] is False
    assert status["http://data.europa.eu/eli/reg/2004/21/art_1/oj"]["complete"] is True


# -- annex resolution --------------------------------------------------------- #

def _annex_corpus() -> rx.Corpus:
    corpus = _corpus()
    # 32004R0021 has labelled Annexes 1 and 2 (Annex 2 missing in French);
    # 32009R0999 (quarantined) irrelevant; give 32004R0796 a single unlabelled annex.
    corpus.annex_eli["32004R0021"] = {
        "1": "http://data.europa.eu/eli/reg/2004/21/anx_1/oj",
        "2": "http://data.europa.eu/eli/reg/2004/21/anx_2/oj"}
    for lg in ("en", "fr", "de", "es"):
        corpus.annex_langs["32004R0021"][lg].update({"1", "2"})
    corpus.annex_langs["32004R0021"]["fr"].discard("2")
    corpus.annexes_en["32004R0021"] = [
        ("1", "http://data.europa.eu/eli/reg/2004/21/anx_1/oj"),
        ("2", "http://data.europa.eu/eli/reg/2004/21/anx_2/oj")]
    corpus.annexes_en["32009R0999"] = []
    return corpus


def _annex_row(surface_form: str, act: str, **kw) -> dict:
    row = _row(surface_form, act, **kw)
    row["rule"] = "external_annex_of_act"
    return row


def test_labelled_annex_resolves_against_the_target_acts_inventory():
    edges, misses = rx.resolve_row(
        _annex_row("Annexes I and III", "Council Regulation (EC) No 21/2004"), _annex_corpus())
    assert [(e["target_annex_id"], e["target_unit_type"]) for e in edges] == [("1", "annex")]
    assert edges[0]["target_article_id"].endswith("/anx_1/oj")
    assert edges[0]["available_languages"] == ["en", "fr", "de", "es"]
    assert [m["reason"] for m in misses] == ["target_annex_not_in_inventory"]
    assert misses[0]["target_annex_id"] == "3"


def test_annex_language_availability_follows_the_target_annex():
    edges, _ = rx.resolve_row(
        _annex_row("Annex II", "Council Regulation (EC) No 21/2004"), _annex_corpus())
    assert edges[0]["available_languages"] == ["en", "de", "es"]


def test_bare_annex_resolves_only_against_a_single_annex():
    corpus = _annex_corpus()
    # two annexes -> ambiguous
    edges, misses = rx.resolve_row(
        _annex_row("the Annex", "Council Regulation (EC) No 21/2004"), corpus)
    assert edges == [] and misses[0]["reason"] == "target_annex_ambiguous"
    # exactly one -> resolved
    corpus.annexes_en["32004R0021"] = [("pos1", "http://data.europa.eu/eli/reg/2004/21/anx_pos1/oj")]
    corpus.annex_langs["32004R0021"] = {lg: {"pos1"} for lg in ("en", "fr", "de", "es")}
    edges, misses = rx.resolve_row(
        _annex_row("the Annex", "Council Regulation (EC) No 21/2004"), corpus)
    assert misses == [] and edges[0]["target_annex_id"] == "pos1"


def test_annex_thereto_is_anaphoric():
    row = _annex_row("Annex I", "", anaphoric=True)
    row["rule"] = "external_annex_thereto"
    edges, misses = rx.resolve_row(row, _annex_corpus())
    assert edges == [] and misses[0]["reason"] == "anaphoric"


def test_unresolved_annex_citations_block_completeness():
    tally = rx._Tally()
    tally.annex_targets.add("anx")
    assert rx.status_row("e", "c", "1", tally)["complete"]
    tally.unresolved["annex_bare_ambiguous"] += 1
    tally.annex_unresolved += 1
    row = rx.status_row("e", "c", "1", tally)
    assert not row["complete"] and row["cites_annex"]


def test_act_level_annex_misses_still_count_as_citing_an_annex():
    tally = rx._Tally()
    tally.unresolved["out_of_corpus"] += 1
    tally.annex_unresolved += 1
    row = rx.status_row("e", "c", "1", tally)
    assert not row["complete"] and row["cites_annex"]


def test_colliding_annex_labels_never_resolve():
    corpus = _annex_corpus()
    corpus.annex_eli["32004R0021"]["1"] = None   # label seen twice at load
    edges, misses = rx.resolve_row(
        _annex_row("Annex I", "Council Regulation (EC) No 21/2004"), corpus)
    assert edges == [] and misses[0]["reason"] == "target_annex_not_in_inventory"


def test_bare_annex_against_an_act_with_no_annexes_has_its_own_reason():
    corpus = _annex_corpus()
    corpus.annexes_en["32004R0021"] = []
    edges, misses = rx.resolve_row(
        _annex_row("the Annex", "Council Regulation (EC) No 21/2004"), corpus)
    assert edges == [] and misses[0]["reason"] == "target_annex_bare_no_annex"
