"""
Segment the UN 6-way corpus into generation blocks.

A block is a run of consecutive whole paragraphs of one document, packed to a
token window (150-220 whitespace tokens by default). Paragraph boundaries come
from the ``en:P:S`` tokens of the ``.ids`` file; document boundaries are runs of
consecutive lines sharing the ``.ids`` first token. Because every block is a
line range into the aligned files, the segmentation computed here from English
applies to all six languages unchanged.

Two files are written:

* ``blocks_en.jsonl`` -- one row per block, carrying the English text and the
  line range that defines it in every language.
* ``docs_en.jsonl``   -- one row per document with its title, symbol, and the
  byte offset of its first block row, so a consumer can load one document's
  blocks with a seek instead of holding 2 GB in memory.

Out-of-window blocks are kept but flagged (``in_range: false``) rather than
dropped: a document must remain fully reconstructable from its blocks, and the
QAC batch samples only in-range targets anyway.

Usage:
    python -m clir_bench.domains.legal.un.blocks                 # full build
    python -m clir_bench.domains.legal.un.blocks --limit-docs 500 --out-dir /tmp/x
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from clir_bench.domains.legal.un import paths

MIN_TOKENS, MAX_TOKENS = 150, 220

# Titles are stored on every block for prompt metadata; documents whose opening
# line is a whole paragraph of prose get cut, not carried.
TITLE_MAX_CHARS = 400


@dataclass
class Line:
    """One aligned line: its 1-based position in the corpus files and its
    paragraph number in the original English document."""

    number: int
    paragraph: int
    text: str
    tokens: int


def _en_paragraph(ids_line: str, fallback: int) -> int:
    """Paragraph number of the line's first ``en:P:S`` token.

    Every 6-way line should carry an ``en:`` token; the fallback covers
    malformed tokens so one bad line cannot abort an 11M-line pass.
    """
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
    the full corpus: 86,307 runs for 86,307 distinct ids, so no regrouping is
    needed.
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


def pack(lines: list[Line], *, min_tokens: int = MIN_TOKENS,
         max_tokens: int = MAX_TOKENS) -> list[list[Line]]:
    """Greedy paragraph packing into the token window.

    A block closes at a paragraph boundary once it holds ``min_tokens``, or
    mid-paragraph when the next line would push it past ``max_tokens`` -- lines
    are the alignment unit, so a mid-paragraph cut is still a clean line range.
    A single line longer than ``max_tokens`` becomes its own oversize block:
    there is nothing below a line to cut at. An undersize tail is merged back
    into the previous block when that stays within the window.
    """
    blocks: list[list[Line]] = []
    current: list[Line] = []
    current_tokens = 0
    for line in lines:
        if current:
            starts_paragraph = line.paragraph != current[-1].paragraph
            if current_tokens + line.tokens > max_tokens or (
                    current_tokens >= min_tokens and starts_paragraph):
                blocks.append(current)
                current, current_tokens = [], 0
        current.append(line)
        current_tokens += line.tokens
    if current:
        blocks.append(current)

    if len(blocks) > 1:
        tail_tokens = sum(l.tokens for l in blocks[-1])
        prev_tokens = sum(l.tokens for l in blocks[-2])
        if tail_tokens < min_tokens and prev_tokens + tail_tokens <= max_tokens:
            blocks[-2].extend(blocks.pop())
    return blocks


def symbol_for(doc_id: str) -> str:
    """Best-effort ODS document symbol from the ``.ids`` path form.

    ``1994/s/res/918_1994_`` -> ``S/RES/918(1994)``;
    ``2005/a/c_6/60/sr_9``   -> ``A/C.6/60/SR.9``.
    A trailing underscore marks a parenthesised suffix; interior underscores
    are dots. Heuristic only -- the raw ``doc_id`` stays the join key.
    """
    parts = doc_id.split("/")[1:] or doc_id.split("/")
    out = []
    for part in parts:
        if part.endswith("_") and "_" in part[:-1]:
            head, rest = part[:-1].split("_", 1)
            part = f"{head}({rest.replace('_', '.')})"
        else:
            part = part.rstrip("_").replace("_", ".")
        out.append(part.upper())
    return "/".join(out)


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

    n_docs = n_blocks = n_in_range = 0
    with open(blocks_path, "wb") as blocks_fh, open(docs_path, "wb") as docs_fh:
        for doc_id, lines in read_documents(ids_path, text_path):
            packed = pack(lines, min_tokens=min_tokens, max_tokens=max_tokens)
            title = lines[0].text[:TITLE_MAX_CHARS]
            pieces = doc_id.split("/")
            offset = blocks_fh.tell()
            doc_in_range = 0
            for index, block in enumerate(packed):
                tokens = sum(l.tokens for l in block)
                text = "\n".join(l.text for l in block)
                in_range = min_tokens <= tokens <= max_tokens
                doc_in_range += in_range
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
                    "splits_paragraph": starts_mid or ends_mid,
                    "title": title,
                    "text": text,
                }
                blocks_fh.write(json.dumps(row, ensure_ascii=False).encode() + b"\n")
            docs_fh.write(json.dumps({
                "doc_id": doc_id,
                "symbol": symbol_for(doc_id),
                "body": pieces[1] if len(pieces) > 1 else "",
                "year": pieces[0],
                "title": title,
                "n_blocks": len(packed),
                "n_in_range": doc_in_range,
                "n_lines": len(lines),
                "line_start": lines[0].number,
                "line_end": lines[-1].number,
                "token_count": sum(l.tokens for l in lines),
                "char_count": sum(len(l.text) + 1 for l in lines),
                "offset": offset,
            }, ensure_ascii=False).encode() + b"\n")

            n_docs += 1
            n_blocks += len(packed)
            n_in_range += doc_in_range
            if n_docs % 10000 == 0:
                print(f"  {n_docs:,} documents, {n_blocks:,} blocks", file=sys.stderr)
            if limit_docs and n_docs >= limit_docs:
                break

    print(f"wrote {n_blocks:,} blocks ({n_in_range:,} in the {min_tokens}-{max_tokens} "
          f"token window) across {n_docs:,} documents", file=sys.stderr)
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
