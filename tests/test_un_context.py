"""Payload assembly: priority context slots and annex-anchored references."""

from __future__ import annotations

import json

from clir_bench.domains.legal.qac import un_context as ctx
from clir_bench.domains.legal.qac import un_references as refs


def _unit(i, text, part_id="", part_label=""):
    return ctx.BlockUnit(
        block_id=f"d#{i}", doc_id="d", symbol="S/RES/1(1999)", title="t",
        block_index=i, n_blocks=6, line_start=i, line_end=i, token_count=10,
        in_range=True, part_id=part_id, part_label=part_label,
        texts={"en": text})


def test_select_context_priority_beats_neighbours():
    blocks = [_unit(i, f"block {i} " + "x" * 90) for i in range(6)]
    # budget fits the opening plus ONE more block; the anchored sibling (4)
    # must win over the immediate neighbours of target 1.
    chosen = ctx._select_context(blocks, 1, budget=2 * 105, priority=[4])
    assert [b.block_index for b in chosen] == [0, 4]


def test_select_context_without_priority_keeps_neighbour_order():
    blocks = [_unit(i, f"block {i} " + "x" * 90) for i in range(6)]
    chosen = ctx._select_context(blocks, 1, budget=2 * 105)
    assert [b.block_index for b in chosen] == [0, 2]


class _MiniIndex(ctx.BlockIndex):
    """BlockIndex over in-memory rows, no files."""

    def __init__(self, docs, blocks_by_doc, tmp_path):
        docs_path = tmp_path / "docs.jsonl"
        docs_path.write_text("".join(json.dumps(d) + "\n" for d in docs.values()))
        self._rows = blocks_by_doc
        super().__init__(blocks_path=tmp_path / "missing_blocks.jsonl",
                         docs_path=docs_path,
                         status_path=tmp_path / "missing_status.jsonl")

    def blocks_for(self, doc_id):
        return [ctx.BlockUnit.from_row(r) for r in self._rows[doc_id]]


def _row(doc_id, i, text, part="body", part_id="", part_label=""):
    return {"block_id": f"{doc_id}#{i}", "doc_id": doc_id,
            "symbol": "S/RES/1265(1999)" if "1265" in doc_id else "S/RES/1(1999)",
            "title": "PROTECTION OF CIVILIANS", "block_index": i, "n_blocks": 3,
            "line_start": i, "line_end": i, "token_count": 10,
            "in_range": True, "usable": True, "part": part, "part_id": part_id,
            "part_label": part_label, "text": text}


def test_reference_renders_the_cited_annex_block(tmp_path):
    cited = "1999/s/res/1265_1999_"
    citing = "1999/s/res/1_1999_"
    docs = {
        cited: {"doc_id": cited, "symbol": "S/RES/1265(1999)",
                "title": "PROTECTION OF CIVILIANS", "n_blocks": 3,
                "n_targets": 3, "target_idxs": [0, 1, 2],
                "annexes": [{"part_id": "anx_1", "kind": "annex", "label": "I",
                             "block_start": 2, "block_end": 2}], "offset": 0},
        citing: {"doc_id": citing, "symbol": "S/RES/1(1999)", "title": "T",
                 "n_blocks": 1, "n_targets": 1, "target_idxs": [0],
                 "annexes": [], "offset": 0},
    }
    blocks = {
        cited: [_row(cited, 0, "1. Head block of the cited resolution;"),
                _row(cited, 1, "2. Second operative paragraph;"),
                _row(cited, 2, "Annex I\nTHE ANNEXED FRAMEWORK TEXT",
                     part="annex", part_id="anx_1", part_label="Annex I")],
        citing: [_row(citing, 0,
                      "Recalling annex I to resolution 1265 (1999), decides;")],
    }
    index = _MiniIndex(docs, blocks, tmp_path)
    payload = index.build(citing, 0)
    (ref,) = payload.references
    assert ref.part_label == "Annex I"
    assert "ANNEXED FRAMEWORK" in ref.text
    assert "(cited annex Annex I)" in payload.text
    assert index.incomplete is None    # status file absent -> gate unavailable


def test_priority_anchor_overflow_does_not_end_the_walk():
    blocks = [_unit(i, f"block {i} " + "x" * 90) for i in range(6)]
    blocks[4] = _unit(4, "y" * 5000)          # oversized anchor
    chosen = ctx._select_context(blocks, 1, budget=2 * 105, priority=[4, 3])
    # anchor 4 does not fit; anchor 3 and the opening still do
    assert [b.block_index for b in chosen] == [0, 3]


def test_custom_paths_do_not_gate_against_the_production_status(tmp_path):
    import json as _json
    docs_path = tmp_path / "docs.jsonl"
    docs_path.write_text(_json.dumps({
        "doc_id": "d", "symbol": "S/RES/1(1999)", "title": "t",
        "n_blocks": 0, "n_targets": 0, "target_idxs": [], "offset": 0}) + "\n")
    index = ctx.BlockIndex(blocks_path=tmp_path / "blocks.jsonl",
                           docs_path=docs_path)
    assert index.incomplete is None
