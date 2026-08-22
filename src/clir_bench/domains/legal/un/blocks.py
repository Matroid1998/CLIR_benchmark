"""
Segment the UN 6-way corpus into generation blocks.

A block is a contiguous run of lines of one document, packed to a token window
(150-220 whitespace tokens by default). Paragraph boundaries come from the
``en:P:S`` tokens of the ``.ids`` file; document boundaries are runs of
consecutive lines sharing the ``.ids`` first token.

**The invariant everything depends on**: a block is a contiguous line range
``line_start..line_end`` into the original 6-way files, and every line inside
the range belongs to the block. The corpus files are never modified, so the
same range read from the ``.fr``/``.ar``/``.es``/``.ru``/``.zh`` file is the
exact translation of the block.

Text hygiene therefore happens *between* blocks, not inside them: a line
classifier marks mastheads, TOC rows, vote rosters, adoption formulas, and
meeting furniture as junk, and junk lines act as hard block boundaries -- they
fall into the gaps between blocks, owned by none. Section headings are soft
boundaries that close a full-enough block and open the next one, so a block
carries its section title. Blocks deliberately do NOT cover every line;
reconstructing a full document means reading its line range from the corpus
files, not concatenating its blocks.

Two files are written:

* ``blocks_en.jsonl`` -- one row per block: English text, the defining line
  range, and the Layer-2 ``usable`` flag (shape checks for rosters, flattened
  tables, symbol listings that survive inside otherwise-valid blocks).
* ``docs_en.jsonl``   -- one row per document: title (first *content* line),
  symbol, ``target_idxs`` (indices of blocks that are in-range AND usable,
  which is what the QAC batch samples from), and the byte offset of the
  document's first block row for seek-based access.

Usage:
    python -m clir_bench.domains.legal.un.blocks                 # full build
    python -m clir_bench.domains.legal.un.blocks --limit-docs 500 --out-dir /tmp/x
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from clir_bench.domains.legal.un import paths

MIN_TOKENS, MAX_TOKENS = 150, 220

TITLE_MAX_CHARS = 400
HEADING_MAX_CHARS = 200

# ---------------------------------------------------------------------------
# Line classification (Layer 1).
#
# Ordered, first match wins. JUNK classes are hard block boundaries; heading
# is a soft boundary; everything else is content. Rules are precision-first:
# the only expensive error is content->junk, which silently removes translated
# text from every language's block. Every pattern was validated against the
# corpus (117k-line systematic sample); the naive trailing-page-number rule
# was rejected there for false positives ("Rule 44", "Article 5").
# ---------------------------------------------------------------------------

CLS_MASTHEAD = "masthead"
CLS_TOC = "toc"
CLS_VOTE = "vote_roster"
CLS_ADOPTION = "adoption_formula"
CLS_FURNITURE = "furniture"
CLS_HEADING = "heading"
CLS_CONTENT = "content"

JUNK_CLASSES = {CLS_MASTHEAD, CLS_TOC, CLS_VOTE, CLS_ADOPTION, CLS_FURNITURE}

# Masthead patterns apply ONLY inside the unbroken leading run of a document:
# bare symbols are 84% mid-document content (citations) and bare dates 92%
# (chronology day-headers, letter dates), so these forms must never fire
# after the first content line.
MASTHEAD_RES = [re.compile(p) for p in (
    r"^(United Nations|UNITED NATIONS)\s*\*{0,3}$",
    r"^(General Assembly|Security Council|Economic and Social Council|Trusteeship Council"
    r"|Human Rights Council|Conference on Disarmament|GENERAL ASSEMBLY|SECURITY COUNCIL"
    r"|ECONOMIC AND SOCIAL COUNCIL)\s*$",
    r"^(First|Second|Third|Fourth|Fifth|Sixth) Committee$",
    r"^Distr\.?\s*:?\s*(GENERAL|General|LIMITED|Limited|RESTRICTED|Restricted)?\.?\s*$",
    r"^(GENERAL|LIMITED|RESTRICTED)$",   # the Distr. value printed on its own line

    r"^[A-Z]{1,4}(/[A-Za-z0-9.\-()]{1,20}){1,6}\*{0,3}$",       # bare document symbol
    r"(?i)^\[?\s*original\s*:\s*[a-z/, ]+\]?$",
    r"^\d{1,2} [A-Z][a-z]+ \d{4}$",                              # bare date
    r"(?i)^[a-z]+([-—–][a-z]+)*( special| regular| emergency special)? session$",
    r"(?i)^(agenda items? \d|items? \d+( and \d+)? of the provisional agenda)",
    r"(?i)^(summary|verbatim|provisional verbatim) record of the",
    r"^Held at\b",
    r"(?i)^(chair(man|person|main)?|president|rapporteur|vice-chair\w*|later)\s*:",  # 'Chairmain' is a real corpus typo
    r"^\[(on the report of|without reference to|on a proposal)",
    r"(?i)^(new york|geneva|vienna|nairobi|bangkok)[, ].{0,60}\d{4}$",
    r"^\*{1,3}$",
)]

TOC_RES = [re.compile(p) for p in (
    r"^(Contents|CONTENTS)$",
    r"^(Paragraphs\s+)?(Page|PAGE)$",
    r"^.{0,90}?[\.\s]\d{1,4}\s*[-–—]\s*\d{1,4}\s+\d{1,3}$",  # 'Title 12 - 15 7'
    r"\.{4,}\s*\d{1,4}$",                                              # dotted leader + page
    r"^([IVXLC]{1,6}|[A-H])\.\s+\D{3,70}\s\d{1,3}$",                   # heading row w/ page no.
)]

VOTE_RES = [re.compile(p) for p in (
    r"^(In favour|Against|Abstaining)\s*:",
    r"^(?:[A-Z][\w'’.\- ]{1,40},\s+){8,}[A-Z][\w'’.\- ]{1,40}[.,]?$",
)]

PLENARY_RE = re.compile(r"^\d{1,4}(st|nd|rd|th) (plenary |formal )?meeting$")
DATE_RE = re.compile(r"^\d{1,2} [A-Z][a-z]+ \d{4}$")
FURNITURE_RE = re.compile(
    r"^The meeting (was called to order|was suspended|was resumed|resumed|rose) at .{0,40}$")

# Bare 'Annex' is a heading (it legitimately precedes substantive annex text);
# Annex rows carrying a paragraph-range/page number match TOC first because
# TOC is tested before heading. ANNEX_HEADING_RE is the same first pattern with
# the label captured: it decides where a document's annex/appendix parts begin,
# so that every block can carry the part it belongs to.
ANNEX_HEADING_RE = re.compile(
    r"^(ANNEX|Annex|APPENDIX|Appendix)(?:\s+([IVXLC]+|\d{1,2}))?\s*$")

HEADING_RES = [re.compile(p) for p in (
    r"^(ANNEX|Annex|APPENDIX|Appendix)(\s+[IVXLC0-9]+)?$",
    r"^[IVXLC]{1,6}\.\s+\S",
    r"^[A-H]\.\s+[A-Z]",
    r"^Article \d+\s*$",
    r"^(Section|Chapter|Part)\s+[IVXLC0-9]+",
    r"(?i)^agenda items? \d+",  # mid-document: SR/PV agenda-section marker
)]


def _matches_any(patterns: list[re.Pattern], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def classify_lines(lines: list["Line"]) -> list[str]:
    """One class per line, aligned with ``lines``."""
    n = len(lines)
    cls = [CLS_CONTENT] * n

    # Leading run: masthead/TOC patterns hold until the first line matching
    # neither -- after that, masthead patterns never fire again.
    body_start = 0
    while body_start < n:
        text = lines[body_start].text.strip()
        if _matches_any(MASTHEAD_RES, text):
            cls[body_start] = CLS_MASTHEAD
        elif _matches_any(TOC_RES, text):
            cls[body_start] = CLS_TOC
        else:
            break
        body_start += 1

    for i in range(body_start, n):
        text = lines[i].text.strip()
        if _matches_any(TOC_RES, text):
            cls[i] = CLS_TOC
        elif _matches_any(VOTE_RES, text):
            cls[i] = CLS_VOTE
        elif PLENARY_RE.match(text):
            cls[i] = CLS_ADOPTION
        elif FURNITURE_RE.match(text):
            cls[i] = CLS_FURNITURE
        elif _matches_any(HEADING_RES, text):
            cls[i] = CLS_HEADING

    # Bare dates in the body are content (chronology day-headers, letter
    # dates) EXCEPT next to a plenary-meeting line or at the document tail --
    # the GA adoption formula, whose plenary line is sometimes lost.
    for i in range(body_start, n):
        if cls[i] == CLS_CONTENT and DATE_RE.match(lines[i].text.strip()):
            prev_plenary = i > 0 and PLENARY_RE.match(lines[i - 1].text.strip())
            next_plenary = i + 1 < n and PLENARY_RE.match(lines[i + 1].text.strip())
            if prev_plenary or next_plenary or i == n - 1:
                cls[i] = CLS_ADOPTION
    # Trailing scrub: a bare date whose following lines are all junk.
    i = n - 1
    while i >= body_start:
        if cls[i] in JUNK_CLASSES:
            i -= 1
        elif cls[i] == CLS_CONTENT and DATE_RE.match(lines[i].text.strip()):
            cls[i] = CLS_ADOPTION
            i -= 1
        else:
            break
    return cls


# ---------------------------------------------------------------------------
# Layer 2: shape flags on packed block text. A block with any flag is kept
# (context stays complete) but never becomes a generation target.
# ---------------------------------------------------------------------------

SYMBOL_RE = re.compile(r"\b[A-Z]{1,4}(?:/[A-Za-z0-9.\-]+){2,}")
BUDGET_RE = re.compile(r"^(Part [IVXL]+\.|Total, part|Grand total|\(United States dollars\))")
# Structural markers end in digits without being table rows: "Article 18" lines
# in annexed declarations tripped num_tail on purely substantive blocks
# (validated against UNDRIP in the LLM-vs-rules experiment).
STRUCT_MARKER_RE = re.compile(
    r"^(Article|Rule|Chapter|Section|Part|Annex|Principle|Guideline|Regulation)s? [IVXLC0-9]+\.?$")


def junk_flags(text: str) -> list[str]:
    flags: list[str] = []
    lines = [l for l in text.split("\n") if l.strip()]
    tokens = text.split()
    if text.count(", ") >= 15 and tokens:
        caps = sum(1 for t in tokens if t[:1].isupper())
        if caps / len(tokens) >= 0.45:
            flags.append("country_list")
    if len(SYMBOL_RE.findall(text)) >= 6:
        flags.append("symbol_soup")
    if len(lines) >= 5:
        tails = sum(1 for l in lines
                    if l.rstrip()[-1:].isdigit() and not STRUCT_MARKER_RE.match(l.strip()))
        if tails / len(lines) >= 0.5:
            flags.append("num_tail")
    # Structural markers ("Article 18", "Rule 44") are short lines without being
    # table rows -- same exclusion num_tail needed for annexed declarations.
    prose_lines = [l for l in lines if not STRUCT_MARKER_RE.match(l.strip())]
    if len(prose_lines) >= 9:
        per_line = sorted(len(l.split()) for l in prose_lines)
        short = sum(1 for l in prose_lines if len(l.split()) <= 6)
        if per_line[len(per_line) // 2] <= 6 and short / len(prose_lines) > 0.5:
            flags.append("short_table")
    if sum(1 for l in lines if BUDGET_RE.match(l.strip())) >= 3:
        flags.append("budget_labels")
    return flags


# ---------------------------------------------------------------------------
# Streaming and packing.
# ---------------------------------------------------------------------------


@dataclass
class Line:
    """One aligned line: its 1-based position in the corpus files and its
    paragraph number in the original English document."""

    number: int
    paragraph: int
    text: str
    tokens: int


def _en_paragraph(ids_line: str, fallback: int) -> int:
    """Paragraph number of the line's first ``en:P:S`` token."""
    for token in ids_line.split()[1:]:
        if token.startswith("en:"):
            parts = token.split(":")
            try:
                return int(parts[1])
            except (IndexError, ValueError):
                return fallback
    return fallback


def read_documents(ids_path: Path, text_path: Path) -> Iterator[tuple[str, list[Line]]]:
    """Stream (document id, lines) pairs, one document at a time.

    Documents are consecutive runs of one ``.ids`` first token -- verified over
    the full corpus: 86,307 runs for 86,307 distinct ids.
    """
    doc_id: str | None = None
    lines: list[Line] = []
    paragraph = 0
    with open(ids_path, encoding="utf-8") as ids_fh, \
            open(text_path, encoding="utf-8") as text_fh:
        for number, (ids_line, text_line) in enumerate(zip(ids_fh, text_fh), start=1):
            this_doc = ids_line.split(" ", 1)[0].strip()
            if this_doc != doc_id:
                if doc_id is not None and lines:
                    yield doc_id, lines
                doc_id, lines, paragraph = this_doc, [], 0
            paragraph = _en_paragraph(ids_line, paragraph)
            text = text_line.rstrip("\n")
            lines.append(Line(number, paragraph, text, len(text.split())))
    if doc_id is not None and lines:
        yield doc_id, lines


def pack(lines: list[Line], cls: list[str] | None = None, *,
         min_tokens: int = MIN_TOKENS, max_tokens: int = MAX_TOKENS) -> list[list[Line]]:
    """Pack classified lines into contiguous blocks within the token window.

    Junk lines are hard boundaries (they fall into the gaps between blocks and
    clear any pending heading). Heading lines are soft boundaries: they close
    a block that already holds ``min_tokens`` and open the next one, so the
    block carries its section title; against an under-min block they ride
    inline. Content packs under the existing rules: close at a paragraph
    boundary once >= min, or immediately before overflowing max. A single
    line longer than ``max_tokens`` becomes its own oversize block. An
    undersize tail merges into the previous block only when the two are
    line-adjacent -- never across a junk gap.
    """
    if cls is None:
        cls = [CLS_CONTENT] * len(lines)

    blocks: list[list[Line]] = []
    current: list[Line] = []
    current_tokens = 0
    pending: list[Line] = []            # heading lines that open the next block

    def close() -> None:
        nonlocal current, current_tokens
        if current:
            blocks.append(current)
        current, current_tokens = [], 0

    for line, kind in zip(lines, cls):
        if kind in JUNK_CLASSES:
            close()
            pending.clear()             # heading followed by junk -> gap
        elif kind == CLS_HEADING:
            if current_tokens >= min_tokens or (
                    current and current_tokens + line.tokens > max_tokens):
                close()
            if current:                 # under-min block: heading rides inline
                current.append(line)
                current_tokens += line.tokens
            else:
                pending.append(line)
        else:
            if pending:
                current = pending[:]
                current_tokens = sum(l.tokens for l in pending)
                pending = []
            if current:
                starts_paragraph = line.paragraph != current[-1].paragraph
                if current_tokens + line.tokens > max_tokens or (
                        current_tokens >= min_tokens and starts_paragraph):
                    close()
            current.append(line)
            current_tokens += line.tokens
    pending.clear()                     # trailing headings with no content -> gap
    close()

    if len(blocks) > 1:
        tail, prev = blocks[-1], blocks[-2]
        tail_tokens = sum(l.tokens for l in tail)
        prev_tokens = sum(l.tokens for l in prev)
        if (prev[-1].number + 1 == tail[0].number
                and tail_tokens < min_tokens
                and prev_tokens + tail_tokens <= max_tokens):
            prev.extend(blocks.pop())
    return blocks


def symbol_for(doc_id: str) -> str:
    """Best-effort ODS document symbol from the ``.ids`` path form.

    ``1994/s/res/918_1994_`` -> ``S/RES/918(1994)``;
    ``2005/a/c_6/60/sr_9``   -> ``A/C.6/60/SR.9``.
    """
    parts = doc_id.split("/")[1:] or doc_id.split("/")
    out = []
    for part in parts:
        if part.endswith("_") and "_" in part[:-1]:
            head, rest = part[:-1].split("_", 1)
            # "1173__1998_" carries a doubled underscore; without the strip the
            # symbol came out "S/RES/1173(.1998)" and the document was
            # unreachable behind a key nothing ever cites.
            part = f"{head}({rest.strip('_').replace('_', '.')})"
        else:
            part = part.rstrip("_").replace("_", ".")
        out.append(part.upper())
    return "/".join(out)


_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def _label_int(label: str) -> int | None:
    if label.isdigit():
        return int(label)
    total, previous = 0, 0
    for char in reversed(label):
        digit = _ROMAN_VALUES.get(char)
        if digit is None:
            return None
        total = total - digit if digit < previous else total + digit
        previous = max(previous, digit)
    return total or None


def assign_parts(lines: list[Line], cls: list[str]) -> list[tuple[str, str, str]]:
    """(part, part_id, part_label) per line: "body" until an ANNEX/APPENDIX
    heading, then that part until the next such heading or document end.

    Labels normalise to integers ("Annex I" and "Annex 1" both become anx_1);
    an unlabelled heading gets a positional id (anx_pos1). The resolver treats
    duplicate ids as ambiguous, so collisions are represented, never hidden.
    """
    parts: list[tuple[str, str, str]] = []
    current = ("body", "", "")
    counters = {"annex": 0, "appendix": 0}
    for line, kind in zip(lines, cls):
        if kind == CLS_HEADING:
            heading = ANNEX_HEADING_RE.match(line.text.strip())
            if heading:
                word = heading.group(1).lower()
                part_kind = "appendix" if word.startswith("append") else "annex"
                counters[part_kind] += 1
                prefix = "app" if part_kind == "appendix" else "anx"
                label = heading.group(2) or ""
                number = _label_int(label) if label else None
                part_id = (f"{prefix}_{number}" if number is not None
                           else f"{prefix}_pos{counters[part_kind]}")
                current = (part_kind, part_id, line.text.strip())
        parts.append(current)
    return parts


def build(*, ids_path: Path = paths.IDS_FILE,
          text_path: Path | None = None,
          out_dir: Path = paths.BLOCKS_DIR,
          min_tokens: int = MIN_TOKENS, max_tokens: int = MAX_TOKENS,
          limit_docs: int = 0) -> tuple[int, int]:
    """Write blocks_en.jsonl and docs_en.jsonl. Returns (documents, blocks)."""
    text_path = text_path or paths.text_file("en")
    out_dir.mkdir(parents=True, exist_ok=True)
    blocks_path = out_dir / paths.BLOCKS_JSONL.name
    docs_path = out_dir / paths.DOCS_JSONL.name

    n_docs = n_blocks = n_targets_total = n_junk_total = 0
    with open(blocks_path, "wb") as blocks_fh, open(docs_path, "wb") as docs_fh:
        for doc_id, lines in read_documents(ids_path, text_path):
            cls = classify_lines(lines)
            kind_of = dict(zip((l.number for l in lines), cls))
            n_junk = sum(1 for k in cls if k in JUNK_CLASSES)
            packed = pack(lines, cls, min_tokens=min_tokens, max_tokens=max_tokens)
            part_of = dict(zip((l.number for l in lines), assign_parts(lines, cls)))

            title = next((l.text for l, k in zip(lines, cls) if k == CLS_CONTENT),
                         lines[0].text)[:TITLE_MAX_CHARS]
            pieces = doc_id.split("/")
            offset = blocks_fh.tell()
            target_idxs: list[int] = []
            for index, block in enumerate(packed):
                numbers = [l.number for l in block]
                assert numbers == list(range(numbers[0], numbers[-1] + 1)), \
                    f"non-contiguous block in {doc_id}"
                tokens = sum(l.tokens for l in block)
                text = "\n".join(l.text for l in block)
                in_range = min_tokens <= tokens <= max_tokens
                flags = junk_flags(text)
                usable = not flags
                if in_range and usable:
                    target_idxs.append(index)
                heading_lines = []
                for l in block:
                    if kind_of[l.number] == CLS_HEADING:
                        heading_lines.append(l.text.strip())
                    else:
                        break
                part, part_id, part_label = part_of[block[0].number]
                starts_mid = index > 0 and block[0].paragraph == packed[index - 1][-1].paragraph
                ends_mid = (index + 1 < len(packed)
                            and block[-1].paragraph == packed[index + 1][0].paragraph)
                row = {
                    "block_id": f"{doc_id}#{index}",
                    "doc_id": doc_id,
                    "symbol": symbol_for(doc_id),
                    "body": pieces[1] if len(pieces) > 1 else "",
                    "year": pieces[0],
                    "block_index": index,
                    "n_blocks": len(packed),
                    "line_start": block[0].number,
                    "line_end": block[-1].number,
                    "n_lines": len(block),
                    "para_start": block[0].paragraph,
                    "para_end": block[-1].paragraph,
                    "token_count": tokens,
                    "char_count": len(text),
                    "in_range": in_range,
                    "usable": usable,
                    "junk_flags": flags,
                    "splits_paragraph": starts_mid or ends_mid,
                    "part": part,
                    "part_id": part_id,
                    "part_label": part_label,
                    "heading": " / ".join(heading_lines)[:HEADING_MAX_CHARS],
                    "title": title,
                    "text": text,
                }
                blocks_fh.write(json.dumps(row, ensure_ascii=False).encode() + b"\n")

            # The document's annex inventory, from the block-level parts:
            # contiguous runs of one part_id, in block order. Duplicate labels
            # stay duplicated -- the resolver's ">1 match" rule reads that as
            # ambiguous, which is the truthful answer.
            annexes: list[dict] = []
            for index, block in enumerate(packed):
                part, part_id, part_label = part_of[block[0].number]
                if part == "body":
                    continue
                if annexes and annexes[-1]["part_id"] == part_id \
                        and annexes[-1]["block_end"] == index - 1:
                    annexes[-1]["block_end"] = index
                    continue
                label_match = ANNEX_HEADING_RE.match(part_label)
                label = (label_match.group(2) or "") if label_match else ""
                annexes.append({"part_id": part_id, "kind": part,
                                "label": label, "block_start": index,
                                "block_end": index})
            docs_fh.write(json.dumps({
                "doc_id": doc_id,
                "symbol": symbol_for(doc_id),
                "body": pieces[1] if len(pieces) > 1 else "",
                "year": pieces[0],
                "title": title,
                "n_blocks": len(packed),
                "n_targets": len(target_idxs),
                "target_idxs": target_idxs,
                "n_in_range": sum(1 for i in range(len(packed))
                                  if min_tokens <= sum(l.tokens for l in packed[i]) <= max_tokens),
                "n_lines": len(lines),
                "n_junk_lines": n_junk,
                "line_start": lines[0].number,
                "line_end": lines[-1].number,
                "token_count": sum(l.tokens for l in lines),
                "char_count": sum(len(l.text) + 1 for l in lines),
                "annexes": annexes,
                "offset": offset,
            }, ensure_ascii=False).encode() + b"\n")

            n_docs += 1
            n_blocks += len(packed)
            n_targets_total += len(target_idxs)
            n_junk_total += n_junk
            if n_docs % 10000 == 0:
                print(f"  {n_docs:,} documents, {n_blocks:,} blocks", file=sys.stderr)
            if limit_docs and n_docs >= limit_docs:
                break

    print(f"wrote {n_blocks:,} blocks ({n_targets_total:,} targets: in the "
          f"{min_tokens}-{max_tokens} token window AND usable) across {n_docs:,} documents; "
          f"{n_junk_total:,} junk lines left in gaps", file=sys.stderr)
    print(f"  -> {blocks_path}\n  -> {docs_path}", file=sys.stderr)
    return n_docs, n_blocks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", default=str(paths.IDS_FILE))
    parser.add_argument("--text", default=str(paths.text_file("en")))
    parser.add_argument("--out-dir", default=str(paths.BLOCKS_DIR))
    parser.add_argument("--min-tokens", type=int, default=MIN_TOKENS)
    parser.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    parser.add_argument("--limit-docs", type=int, default=0,
                        help="stop after this many documents (0 = all)")
    args = parser.parse_args()
    build(ids_path=Path(args.ids), text_path=Path(args.text),
          out_dir=Path(args.out_dir), min_tokens=args.min_tokens,
          max_tokens=args.max_tokens, limit_docs=args.limit_docs)


if __name__ == "__main__":
    main()
