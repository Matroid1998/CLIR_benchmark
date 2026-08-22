"""Line classifier + packing invariants for the UN block builder.

Synthetic fixtures only -- no corpus dependency. The cases encode the
corpus-validated decisions: which line shapes are junk, which are headings,
the false positives the classifier must NOT eat ('Rule 44', 'Article 5(2)'
citations), and the contiguity rules of the packer.
"""

from __future__ import annotations

from clir_bench.domains.legal.un.blocks import (
    CLS_ADOPTION, CLS_CONTENT, CLS_FURNITURE, CLS_HEADING, CLS_MASTHEAD,
    CLS_TOC, CLS_VOTE, JUNK_CLASSES, Line, classify_lines, junk_flags, pack,
)


def make_lines(texts: list[str], start: int = 1,
               paragraphs: list[int] | None = None) -> list[Line]:
    return [
        Line(number=start + i,
             paragraph=paragraphs[i] if paragraphs else i + 1,
             text=t, tokens=len(t.split()))
        for i, t in enumerate(texts)
    ]


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify_texts(texts: list[str]) -> list[str]:
    return classify_lines(make_lines(texts))


def test_masthead_leading_run_ends_at_first_content():
    cls = classify_texts([
        "United Nations",
        "S/2024/612",
        "Security Council",
        "Distr.: General",
        "Original: English",
        "Report of the Secretary-General on the situation in Abyei",
        "S/2024/612",   # same shape as a bare symbol, but mid-document now
    ])
    assert cls[:5] == [CLS_MASTHEAD] * 5
    assert cls[5] == CLS_CONTENT
    assert cls[6] == CLS_CONTENT     # bare symbol after the run stays content


def test_bare_date_is_masthead_only_in_leading_run():
    cls = classify_texts([
        "12 May 2004",                                   # leading run
        "The Committee considered the report in detail today.",
        "17 May 1994",                                   # mid-doc chronology header
        "The Council met again and continued its debate.",
    ])
    assert cls[0] == CLS_MASTHEAD
    assert cls[2] == CLS_CONTENT


def test_adoption_formula_plenary_and_adjacent_date():
    cls = classify_texts([
        "Decides to remain actively seized of the matter.",
        "87th plenary meeting",
        "19 December 2000",
    ])
    assert cls[1] == CLS_ADOPTION
    assert cls[2] == CLS_ADOPTION


def test_trailing_bare_date_is_adoption():
    cls = classify_texts([
        "Requests the Secretary-General to report thereon.",
        "19 December 2000",
    ])
    assert cls[1] == CLS_ADOPTION


def test_chairmain_corpus_typo_in_masthead():
    cls = classify_texts([
        "Chairmain : Mr. Zyman (Poland)",
        "Agenda item 83: Scope of legal protection under the Convention",
        "1. Mrs. Muchiri (Kenya) said that Kenya appreciated the efforts made.",
    ])
    assert cls[0] == CLS_MASTHEAD
    assert cls[1] == CLS_MASTHEAD          # still inside the leading run
    assert cls[2] == CLS_CONTENT


def test_agenda_item_mid_doc_is_heading():
    cls = classify_texts([
        "The meeting began with a discussion of procedural matters generally.",
        "Agenda item 83: Scope of legal protection",
        "2. The representative of Japan said that the protocol was overdue.",
    ])
    assert cls[1] == CLS_HEADING


def test_toc_rows_including_em_dash_variant():
    cls = classify_texts([
        "The report begins after the table of contents shown below now.",
        "Contents",
        "Paragraphs Page",
        "Introduction 1 - 12 2",
        "Background of the mission 297 — 306 48",
        "II. List of documents 10",
    ])
    assert cls[1:] == [CLS_TOC] * 5


def test_rule_and_article_citations_are_not_toc():
    # The naive trailing-page-number rule was rejected for exactly these.
    cls = classify_texts([
        "The provisions applicable here are set out in the following texts.",
        "Rule 44",
        "Article 5",
    ])
    assert cls[1] == CLS_CONTENT
    assert cls[2] == CLS_HEADING           # 'Article N' opens a block, never junk
    assert cls[1] not in JUNK_CLASSES and cls[2] not in JUNK_CLASSES


def test_vote_roster_and_furniture():
    cls = classify_texts([
        "The draft resolution was then put to a recorded vote in the Council.",
        "In favour: Argentina, Brazil, Chile",
        "Albania, Austria, Belgium, Canada, Denmark, Estonia, France, Greece, Hungary, Iceland",
        "The meeting was called to order at 10.10 a.m.",
    ])
    assert cls[1] == CLS_VOTE
    assert cls[2] == CLS_VOTE
    assert cls[3] == CLS_FURNITURE


def test_bare_annex_is_heading_not_toc():
    cls = classify_texts([
        "The signatories set out their proposal in the annex to this letter.",
        "Annex II",
        "The concept of a cooperative management committee is described below.",
    ])
    assert cls[1] == CLS_HEADING


# ---------------------------------------------------------------------------
# Packing
# ---------------------------------------------------------------------------

def tok(block: list[Line]) -> int:
    return sum(l.tokens for l in block)


def line(number: int, paragraph: int, words: int, text: str | None = None) -> Line:
    text = text if text is not None else " ".join(["word"] * words)
    return Line(number=number, paragraph=paragraph, text=text, tokens=words)


def test_junk_is_hard_boundary_and_leaves_gap():
    lines = [line(1, 1, 8), line(2, 2, 8, "Contents"), line(3, 3, 8)]
    cls = [CLS_CONTENT, CLS_TOC, CLS_CONTENT]
    blocks = pack(lines, cls, min_tokens=5, max_tokens=20)
    assert [(b[0].number, b[-1].number) for b in blocks] == [(1, 1), (3, 3)]


def test_heading_opens_next_block():
    lines = [line(1, 1, 6), line(2, 2, 3, "II. Security situation"), line(3, 3, 6)]
    cls = [CLS_CONTENT, CLS_HEADING, CLS_CONTENT]
    blocks = pack(lines, cls, min_tokens=5, max_tokens=20)
    assert [(b[0].number, b[-1].number) for b in blocks] == [(1, 1), (2, 3)]
    assert blocks[1][0].text == "II. Security situation"


def test_heading_then_junk_falls_into_gap():
    lines = [line(1, 1, 8), line(2, 2, 3, "II. Heading"),
             line(3, 3, 2, "Contents"), line(4, 4, 8)]
    cls = [CLS_CONTENT, CLS_HEADING, CLS_TOC, CLS_CONTENT]
    blocks = pack(lines, cls, min_tokens=5, max_tokens=20)
    assert [(b[0].number, b[-1].number) for b in blocks] == [(1, 1), (4, 4)]


def test_heading_rides_inline_in_under_min_block():
    lines = [line(1, 1, 3), line(2, 2, 3, "A. Subheading"), line(3, 2, 3)]
    cls = [CLS_CONTENT, CLS_HEADING, CLS_CONTENT]
    blocks = pack(lines, cls, min_tokens=20, max_tokens=40)
    assert len(blocks) == 1 and len(blocks[0]) == 3


def test_no_tail_merge_across_junk_gap():
    # tail (line 4) is undersized and would merge with block(1..2), but the
    # junk line 3 between them forbids it: merging would swallow the gap.
    lines = [line(1, 1, 6), line(2, 1, 6), line(3, 2, 2, "Contents"), line(4, 3, 2)]
    cls = [CLS_CONTENT, CLS_CONTENT, CLS_TOC, CLS_CONTENT]
    blocks = pack(lines, cls, min_tokens=5, max_tokens=30)
    assert [(b[0].number, b[-1].number) for b in blocks] == [(1, 2), (4, 4)]
    assert tok(blocks[1]) < 5              # stays undersized, out of range


def test_tail_merge_when_adjacent():
    lines = [line(1, 1, 6), line(2, 2, 6), line(3, 3, 2)]
    cls = [CLS_CONTENT] * 3
    blocks = pack(lines, cls, min_tokens=10, max_tokens=30)
    assert len(blocks) == 1 and blocks[0][-1].number == 3


def test_blocks_are_contiguous_line_ranges():
    texts = ["Contents"] + [" ".join(["w"] * 7)] * 12 + ["In favour: A, B, C"] + \
            [" ".join(["w"] * 7)] * 6
    lines = make_lines(texts)
    cls = classify_lines(lines)
    blocks = pack(lines, cls, min_tokens=14, max_tokens=21)
    for block in blocks:
        numbers = [l.number for l in block]
        assert numbers == list(range(numbers[0], numbers[-1] + 1))


# ---------------------------------------------------------------------------
# Layer 2 flags
# ---------------------------------------------------------------------------

def test_flag_num_tail():
    text = "\n".join(f"Item {chr(65 + i)} costs {i * 100}" for i in range(6))
    assert "num_tail" in junk_flags(text)


def test_flag_short_table():
    text = "\n".join(["Military 2616", "Police 148", "Total 2764"] * 4)
    assert "short_table" in junk_flags(text)


def test_flag_country_list():
    names = ", ".join(f"Country{chr(65 + i % 26)}land" for i in range(20))
    assert "country_list" in junk_flags(names)


def test_flag_symbol_soup():
    text = " and ".join(f"see document A/56/{100 + i}/Add.1" for i in range(7))
    assert "symbol_soup" in junk_flags(text)


def test_bare_distr_value_is_masthead():
    cls = classify_texts([
        "GENERAL",                        # 'Distr.:' value printed alone
        "E/CN.4/1997/93",
        "The Commission considered the item at its fifty-third session today.",
    ])
    assert cls[0] == CLS_MASTHEAD
    assert cls[1] == CLS_MASTHEAD
    assert cls[2] == CLS_CONTENT


def test_rules_of_procedure_are_not_short_table():
    # "Rule N" markers are short lines without being table rows.
    text = "\n".join(x for i in range(5) for x in (
        f"Rule {40 + i}",
        "The Committee shall elect its officers for a term of two years of service.",
    ))
    assert "short_table" not in junk_flags(text)


def test_declaration_articles_are_not_num_tail():
    # "Article N" structural markers end in digits without being table rows.
    text = "\n".join([
        "Article 41",
        "The organs and specialized agencies of the United Nations system shall contribute.",
        "Article 42",
        "The United Nations and its bodies shall promote respect for this Declaration.",
        "Article 43",
        "The rights recognized herein constitute the minimum standards for survival.",
    ])
    assert "num_tail" not in junk_flags(text)


def test_prose_with_figures_is_usable():
    text = ("The Security Council authorized an expansion of the UNAMIR force "
            "level up to 5,500 troops and requested the Secretary-General to "
            "report by 31 March on the deployment, including the cooperation "
            "of the parties and progress towards a ceasefire in Rwanda.")
    assert junk_flags(text) == []


# ---------------------------------------------------------------------------
# Annex / appendix part assignment
# ---------------------------------------------------------------------------

def test_appendix_heading_recognised():
    from clir_bench.domains.legal.un.blocks import classify_lines
    lines = make_lines(["Appendix II", "technical detail follows here now"])
    assert classify_lines(lines)[0] == CLS_HEADING


def test_assign_parts_body_annex_appendix():
    from clir_bench.domains.legal.un.blocks import assign_parts, classify_lines
    lines = make_lines([
        "The Security Council decides to act with resolve today",
        "Annex I",
        "one two three four five six seven eight nine ten",
        "Appendix",
        "appendix content line with several more words here",
    ])
    cls = classify_lines(lines)
    parts = assign_parts(lines, cls)
    assert parts[0] == ("body", "", "")
    assert parts[1] == ("annex", "anx_1", "Annex I")
    assert parts[2] == ("annex", "anx_1", "Annex I")
    assert parts[3] == ("appendix", "app_pos1", "Appendix")
    assert parts[4] == ("appendix", "app_pos1", "Appendix")


def test_assign_parts_labels_normalise_and_position_fallback():
    from clir_bench.domains.legal.un.blocks import assign_parts, classify_lines
    lines = make_lines([
        "Annex 2",
        "content of the second annex with words enough",
        "Annex",
        "content of the unlabelled annex with words enough",
    ])
    cls = classify_lines(lines)
    parts = assign_parts(lines, cls)
    assert parts[0][1] == "anx_2"
    assert parts[2][1] == "anx_pos2"      # positional: second annex heading


def test_build_writes_parts_and_annex_inventory(tmp_path):
    import json
    from clir_bench.domains.legal.un import blocks as B
    ids = tmp_path / "ids.txt"
    en = tmp_path / "en.txt"
    body = ["The Council, recalling all of its previous relevant resolutions "
            "and statements, decides to keep the situation under review now"] * 6
    annex = ["Annex I"] + ["The annexed plan sets out the detailed technical "
                           "arrangements for implementation of the mission"] * 6
    lines = body + annex
    ids.write_text("".join(f"1999/s/res/1__1999_ en:{i+1}:1\n" for i in range(len(lines))))
    en.write_text("".join(t + "\n" for t in lines))
    B.build(ids_path=ids, text_path=en, out_dir=tmp_path / "out",
            min_tokens=10, max_tokens=40)
    blocks = [json.loads(l) for l in (tmp_path / "out" / "blocks_en.jsonl").open()]
    (doc,) = [json.loads(l) for l in (tmp_path / "out" / "docs_en.jsonl").open()]
    assert doc["symbol"] == "S/RES/1(1999)"      # doubled underscore cleaned
    assert {b["part"] for b in blocks} == {"body", "annex"}
    annex_blocks = [b for b in blocks if b["part"] == "annex"]
    assert all(b["part_id"] == "anx_1" and b["part_label"] == "Annex I"
               for b in annex_blocks)
    (inv,) = doc["annexes"]
    assert inv["part_id"] == "anx_1" and inv["kind"] == "annex" and inv["label"] == "I"
    assert inv["block_start"] == annex_blocks[0]["block_index"]
    assert inv["block_end"] == annex_blocks[-1]["block_index"]
