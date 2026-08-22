"""Genre and whole-fit selection filters for the UN question batch."""

from __future__ import annotations

from clir_bench.domains.legal.qac.un_batch import (
    FIT_BUDGET, GENRE_STRATA, _excluded_doc, genre_for,
)


# --------------------------------------------------------------------------- #
# Genre filter
# --------------------------------------------------------------------------- #

def test_resolutions_and_decisions():
    assert genre_for("1994/s/res/918_1994_", "RESOLUTION 918 (1994)") == "resolution"
    assert genre_for("2013/a/hrc/res/22/23", "Resolution adopted by...") == "resolution"
    assert genre_for("2010/a/hrc/dec/13/117", "Decision adopted by...") == "resolution"


def test_meeting_records():
    assert genre_for("2002/a/c_3/57/sr_49", "(b) Human rights questions") == "meeting"
    assert genre_for("2010/a/65/pv_18", "The President: I declare open") == "meeting"


def test_letters_by_title_prefix():
    assert genre_for("2001/s/2001/535", "Letter dated 1 June 2001 from...") == "letter"
    assert genre_for("2005/s/2005/57", "letter dated 28 January 2005") == "letter"
    assert genre_for("2009/s/2009/693", "Identical letters dated 31 December") == "letter"
    assert genre_for("2014/e/2014/ngo/14", "Note verbale dated 5 May 2014") == "letter"


def test_reports_and_budget_are_ineligible():
    assert genre_for("1994/s/1994/565", "Report of the Secretary-General") is None
    assert genre_for("2007/a/62/6_sect_21_", "Programme budget") is None
    assert genre_for("2011/a/hrc/17/27", "This report explores key trends") is None


def test_logistics_classes_still_excluded_separately():
    assert _excluded_doc("1998/s/agenda/3848")
    assert _excluded_doc("1997/journal_no_1997/193")
    assert _excluded_doc("2002/a/57/307/corr_1")
    assert not _excluded_doc("1994/s/res/918_1994_")


def test_genre_shares_sum_to_one():
    assert abs(sum(share for _, share in GENRE_STRATA) - 1.0) < 1e-9


# --------------------------------------------------------------------------- #
# Whole-fit filter (via a fake index)
# --------------------------------------------------------------------------- #

class _FakeBlock:
    def __init__(self, text: str) -> None:
        self.texts = {"en": text}


class _FakeIndex:
    """Just enough of BlockIndex for _fits_whole: docs + symbol_map."""

    def __init__(self, docs: dict[str, dict]) -> None:
        self.docs = docs
        from clir_bench.domains.legal.qac.un_references import normalise_symbol
        self.symbol_map = {normalise_symbol(d["symbol"]): did
                           for did, d in docs.items()}


def fits(doc: dict, text: str, index: _FakeIndex) -> bool:
    from clir_bench.domains.legal.qac.un_batch import _fits_whole
    return _fits_whole(doc, text, index)


DOCS = {
    "1994/s/res/918_1994_": {"doc_id": "1994/s/res/918_1994_",
                             "symbol": "S/RES/918(1994)", "char_count": 9_000},
    "1993/s/res/872_1993_": {"doc_id": "1993/s/res/872_1993_",
                             "symbol": "S/RES/872(1993)", "char_count": 8_000},
    "1999/s/res/1265_1999_": {"doc_id": "1999/s/res/1265_1999_",
                              "symbol": "S/RES/1265(1999)", "char_count": 25_000},
}


def test_fits_without_references():
    index = _FakeIndex(DOCS)
    doc = DOCS["1994/s/res/918_1994_"]
    assert fits(doc, "Demands that all parties cease hostilities forthwith.", index)


def test_fits_with_small_reference():
    index = _FakeIndex(DOCS)
    doc = DOCS["1994/s/res/918_1994_"]
    # 9,000 + 8,000 = 17,000 <= 30,000
    assert fits(doc, "Recalling its resolution 872 (1993) on Rwanda,", index)


def test_fails_when_reference_bursts_budget():
    index = _FakeIndex(DOCS)
    doc = DOCS["1994/s/res/918_1994_"]
    # 9,000 + 25,000 > 30,000
    assert not fits(doc, "Recalling its resolution 1265 (1999) on civilians,", index)


def test_fails_when_document_alone_bursts_budget():
    index = _FakeIndex(DOCS)
    big = {"doc_id": "x", "symbol": "X/1", "char_count": FIT_BUDGET + 1}
    assert not fits(big, "No citations at all here.", index)


def test_unresolved_citations_cost_nothing_in_the_fit_check():
    # The FIT check only budgets material that will actually travel; an
    # unresolvable citation contributes 0 chars here because the completeness
    # gate upstream (select(require_complete=True)) has already excluded such
    # blocks from the pool -- this function never sees one in production.
    index = _FakeIndex(DOCS)
    doc = DOCS["1994/s/res/918_1994_"]
    assert fits(doc, "Recalling General Assembly resolution 48/141,", index)


# --------------------------------------------------------------------------- #
# Completeness gate
# --------------------------------------------------------------------------- #

class _GateIndex(_FakeIndex):
    def __init__(self, docs, incomplete):
        super().__init__(docs)
        self.incomplete = incomplete

    def blocks_for(self, doc_id):
        raise AssertionError("gate tests never read block text")


def _gate_docs():
    return {
        "1999/s/res/1_1999_": {
            "doc_id": "1999/s/res/1_1999_", "symbol": "S/RES/1(1999)",
            "char_count": 100, "n_blocks": 3, "title": "RESOLUTION 1",
            "target_idxs": [0, 1, 2]},
    }


def test_select_exits_without_status_file():
    import pytest
    from clir_bench.domains.legal.qac.un_batch import select
    index = _GateIndex(_gate_docs(), incomplete=None)
    with pytest.raises(SystemExit, match="references_status"):
        select(index, n=2, seed=1, languages=["en"], modes=["technical"],
               fit_filter=False)


def test_select_skips_incomplete_blocks():
    from clir_bench.domains.legal.qac.un_batch import select
    bad = {"1999/s/res/1_1999_#1": {"complete": False,
                                    "reasons": {"out_of_corpus": 2}}}
    index = _GateIndex(_gate_docs(), incomplete=bad)
    chosen = select(index, n=3, seed=1, languages=["en"], modes=["technical"],
                    fit_filter=False, genre_filter=False)
    assert {t.block_id for t in chosen} == {"1999/s/res/1_1999_#0",
                                            "1999/s/res/1_1999_#2"}
    assert all(t.reference_complete for t in chosen)


def test_allow_incomplete_lifts_the_gate_and_labels_the_rows():
    from clir_bench.domains.legal.qac.un_batch import select
    bad = {"1999/s/res/1_1999_#1": {"complete": False,
                                    "reasons": {"out_of_corpus": 2}}}
    index = _GateIndex(_gate_docs(), incomplete=bad)
    chosen = select(index, n=3, seed=1, languages=["en"], modes=["technical"],
                    fit_filter=False, genre_filter=False, require_complete=False)
    assert len(chosen) == 3
    flagged = next(t for t in chosen if t.block_id == "1999/s/res/1_1999_#1")
    assert not flagged.reference_complete
    assert flagged.n_unresolved == 2
    assert flagged.unresolved_reasons == "out_of_corpus:2"


# --------------------------------------------------------------------------- #
# Reject floor: best candidate must clear MIN_GROUNDING_FOR_BEST
# --------------------------------------------------------------------------- #

def _row(block_id: str, grounding, total: int) -> dict:
    return {"block_id": block_id, "faith_grounding": grounding, "total_score": total}


def test_pick_best_skips_ungrounded_leader():
    from clir_bench.domains.legal.qac.un_batch import pick_best
    grouped = {"d#0": [_row("d#0", 2, 30), _row("d#0", 3, 27), _row("d#0", 4, 20)]}
    best, rejected = pick_best(grouped)
    # ranked leader has grounding 2 -> skipped; the grounding-3 runner-up wins
    assert [r["total_score"] for r in best] == [27]
    assert rejected == 0


def test_pick_best_rejects_target_with_no_grounded_candidate():
    from clir_bench.domains.legal.qac.un_batch import pick_best
    grouped = {
        "d#0": [_row("d#0", 2, 30), _row("d#0", 1, 25), _row("d#0", 2, 20)],
        "d#1": [_row("d#1", 5, 29)],
    }
    best, rejected = pick_best(grouped)
    assert [r["block_id"] for r in best] == ["d#1"]
    assert rejected == 1


def test_pick_best_tolerates_missing_or_malformed_grades():
    from clir_bench.domains.legal.qac.un_batch import pick_best
    grouped = {"d#0": [_row("d#0", None, 30), _row("d#0", "n/a", 28), _row("d#0", "4", 26)]}
    best, rejected = pick_best(grouped)
    assert [r["total_score"] for r in best] == [26] and rejected == 0
