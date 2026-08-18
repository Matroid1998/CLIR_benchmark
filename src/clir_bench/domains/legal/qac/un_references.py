"""
Extract and resolve cross-references from UN block text.

UN documents cite each other in rigidly formulaic ways -- "resolution 918
(1994)", "resolution 51/210", "(S/PRST/1994/16)", "paragraph 11 (j) of
Security Council resolution 1244 (1999)" -- which makes regex extraction
reliable. This module finds those citations in a target block's English text
and resolves them to documents in our own corpus via the symbol index that
``blocks.py`` already writes, so the cited material can travel in the
generation payload as supporting context (the EUR-Lex pattern: the target
block stays fixed; references complete, never replace, it).

Everything here was measured before it was written (60,328 target blocks):
the regex inventory, the body allowlist that kills non-UN symbols
(OEA/..., MSC/..., IMO circulars), and the resolution chain for slash-form
citations -- ``A/RES -> A/HRC/RES -> E/RES`` is safe because those three key
spaces are fully disjoint in this corpus (GA sessions >= 51, HRC <= 27,
ECOSOC year-like; zero collisions), so the chain can never pick a wrong
document, only miss. Internal references ("paragraph 5 above", "the present
resolution") never match by construction: every pattern requires an explicit
resolution/symbol token.

Usage (validation harness -- writes a manual-review file):
    python -m clir_bench.domains.legal.qac.un_references --sample 400
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from clir_bench.domains.legal.un import paths

# References must stay visibly smaller than the same-document context
# (30k chars): cap 4 carries 96.3% of citing blocks whole (p95 of the
# measured references-per-block distribution, the same place EUR-Lex put
# its cap); one UN block is ~1.0-1.4k chars, so 1500 fits it untruncated.
DEFAULT_MAX_REFERENCES = 4
DEFAULT_REFERENCE_CHARS = 1500

KIND_SC = "sc_resolution"
KIND_SLASH = "slash_resolution"
KIND_DECISION = "decision"
KIND_SYMBOL = "symbol"
KIND_ROMAN = "roman_resolution"
KIND_ES = "es_resolution"

_NUM_YR = r"\d{1,4}\s*\(\s*\d{4}\s*\)"
SC_RUN_RE = re.compile(
    rf"\bresolutions?\s+((?:{_NUM_YR})(?:(?:\s*,\s*|\s*,?\s+and\s+)(?:{_NUM_YR}))*)",
    re.IGNORECASE)
SC_ITEM_RE = re.compile(r"(\d{1,4})\s*\(\s*(\d{4})\s*\)")

_SLASH_ITEM = r"\d{1,4}/\d{1,4}(?:\s+[A-Z](?![\w/]))?"
SLASH_RUN_RE = re.compile(
    rf"\bresolutions?\s+((?:{_SLASH_ITEM})(?:(?:\s*,\s*|\s*,?\s+and\s+)(?:{_SLASH_ITEM}))*)")
SLASH_ITEM_RE = re.compile(r"(\d{1,4})/(\d{1,4})(?:\s+([A-Z])(?![\w/]))?")

DEC_RUN_RE = re.compile(
    r"\bdecisions?\s+((?:\d{1,4}/\d{1,4})(?:(?:\s*,\s*|\s*,?\s+and\s+)(?:\d{1,4}/\d{1,4}))*)")

SYMBOL_RE = re.compile(r"\b([A-Z]{1,6}(?:/[A-Za-z0-9.\-]+){2,7})(\s?\(\d{4}\))?")
SYMBOL_BODIES = frozenset({
    "A", "S", "E", "ST", "CEDAW", "CERD", "CAT", "CRC", "CCPR", "CMW", "CRPD",
    "CED", "HRI", "DP", "TD", "CD", "FCCC", "NPT", "ISBA", "SPLOS", "PCNICC",
    "CTOC", "CAC", "CCW", "APLC", "BWC", "UNEP", "HSP", "PBC", "ICCD", "JIU",
    "UNW", "SAICM", "CLCS",
})

ROMAN_RES_RE = re.compile(r"\bresolutions?\s+\d{1,4}\s*(?:[A-Z]\s+)?\(\s*[IVXLC]+\s*\)")
ES_RES_RE = re.compile(r"\bresolutions?\s+((?:ES|S)-\d+/\d+)")

PARA_OF_RE = re.compile(
    r"\b(?:operative\s+)?paragraphs?\s+(\d+(?:\s*\([a-z]\))?)"
    r"(?:(?:\s*,\s*|\s*,?\s+and\s+)\d+(?:\s*\([a-z]\))?)*"
    r"\s+(?:of|in)\s+"
    r"((?:its\s+|General\s+Assembly\s+|Security\s+Council\s+|Council\s+|Assembly\s+)?"
    r"resolutions?\s+[^,;.]{0,40})", re.IGNORECASE)

_ORGANS = ("General Assembly", "Security Council", "Human Rights Council",
           "Economic and Social Council", "Commission on Human Rights",
           "Sub-Commission")


@dataclass
class Citation:
    """One cross-reference found in a block's English text."""

    start: int
    end: int
    raw: str
    kind: str
    symbol: str | None = None           # constructed + normalized, when known
    doc_id: str | None = None           # in-corpus document, filled by resolve
    paragraph: int | None = None        # cited operative paragraph, if anchored
    section_letter: str | None = None   # "B" in "resolution 57/270 B"
    organ_hint: str | None = None       # from the 60-char pre-window; metadata
    candidates: tuple[str, ...] = field(default=())


def normalise_symbol(text: str) -> str:
    """Canonical symbol form: uppercase, no whitespace, no trailing punctuation.

    "S/RES/1234 (2005)" and "S/RES/1234(2005)" collapse to one key. ADD./CORR./
    REV. suffixes are kept -- they name their own documents in the index.
    """
    s = text.upper().strip()
    s = re.sub(r"[.,;:\-]+$", "", s)
    return "".join(s.split())


def build_symbol_map(docs_path: Path | None = None) -> dict[str, str]:
    """normalise_symbol(symbol) -> doc_id over the whole corpus (collision-free)."""
    out: dict[str, str] = {}
    with open(docs_path or paths.DOCS_JSONL, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            out[normalise_symbol(row["symbol"])] = row["doc_id"]
    return out


def _organ_hint(text: str, start: int) -> str | None:
    window = text[max(0, start - 60):start]
    found = None
    for organ in _ORGANS:
        pos = window.rfind(organ)
        if pos >= 0 and (found is None or pos > found[0]):
            found = (pos, organ)
    return found[1] if found else None


def extract_citations(text: str) -> list[Citation]:
    """Pure regex pass over one block's text. ``doc_id`` stays None here."""
    citations: list[Citation] = []
    symbol_spans: list[tuple[int, int]] = []

    # Literal symbols first: an explicit "A/RES/51/210" must not double as a
    # slash-form item of a surrounding "resolution ..." phrase.
    for m in SYMBOL_RE.finditer(text):
        raw = m.group(1)
        if raw.split("/")[0] not in SYMBOL_BODIES:
            continue
        symbol = raw
        if m.group(2) and "/RES/" in raw.upper():
            symbol = raw + m.group(2)           # prose form "S/RES/918 (1994)"
        citations.append(Citation(
            start=m.start(), end=m.end(), raw=m.group(0).strip(),
            kind=KIND_SYMBOL, symbol=normalise_symbol(symbol),
            organ_hint=_organ_hint(text, m.start()),
            candidates=(normalise_symbol(symbol),)))
        symbol_spans.append((m.start(), m.end()))

    def covered(a: int, b: int) -> bool:
        return any(s <= a and b <= e for s, e in symbol_spans)

    for m in SC_RUN_RE.finditer(text):
        for item in SC_ITEM_RE.finditer(m.group(1)):
            a = m.start(1) + item.start()
            b = m.start(1) + item.end()
            if covered(a, b):
                continue
            symbol = normalise_symbol(f"S/RES/{item.group(1)}({item.group(2)})")
            citations.append(Citation(
                start=a, end=b, raw=item.group(0), kind=KIND_SC, symbol=symbol,
                organ_hint=_organ_hint(text, m.start()), candidates=(symbol,)))

    for m in SLASH_RUN_RE.finditer(text):
        for item in SLASH_ITEM_RE.finditer(m.group(1)):
            a = m.start(1) + item.start()
            b = m.start(1) + item.end()
            if covered(a, b):
                continue
            x, y = item.group(1), item.group(2)
            citations.append(Citation(
                start=a, end=b, raw=item.group(0), kind=KIND_SLASH,
                section_letter=item.group(3),
                organ_hint=_organ_hint(text, m.start()),
                # Safe by measurement: these three key spaces are disjoint in
                # this corpus, so at most one candidate can ever resolve.
                candidates=(normalise_symbol(f"A/RES/{x}/{y}"),
                            normalise_symbol(f"A/HRC/RES/{x}/{y}"),
                            normalise_symbol(f"E/RES/{x}/{y}"))))

    for m in DEC_RUN_RE.finditer(text):
        for item in SLASH_ITEM_RE.finditer(m.group(1)):
            a = m.start(1) + item.start()
            b = m.start(1) + item.end()
            if covered(a, b):
                continue
            citations.append(Citation(
                start=a, end=b, raw=item.group(0), kind=KIND_DECISION,
                organ_hint=_organ_hint(text, m.start()),
                candidates=(normalise_symbol(
                    f"A/HRC/DEC/{item.group(1)}/{item.group(2)}"),)))

    for regex, kind in ((ROMAN_RES_RE, KIND_ROMAN), (ES_RES_RE, KIND_ES)):
        for m in regex.finditer(text):
            if covered(m.start(), m.end()):
                continue
            citations.append(Citation(
                start=m.start(), end=m.end(), raw=m.group(0), kind=kind,
                organ_hint=_organ_hint(text, m.start())))

    # Paragraph anchors: "paragraph 11 (j) of ... resolution 1244 (1999)"
    # annotates the first citation inside the phrase's resolution part.
    for m in PARA_OF_RE.finditer(text):
        number = int(re.match(r"\d+", m.group(1)).group(0))
        lo, hi = m.start(2), m.end(2)
        for c in citations:
            if lo <= c.start < hi and c.paragraph is None:
                c.paragraph = number
                break

    citations.sort(key=lambda c: c.start)
    return citations


def resolve_citations(citations: list[Citation], symbol_map: dict[str, str], *,
                      citing_doc_id: str | None = None) -> list[Citation]:
    """Fill ``symbol``/``doc_id`` from the candidate chains.

    Self-references stay in the list with ``doc_id=None`` -- the document's own
    header line matches the SC pattern, and its own material already travels as
    document context.
    """
    hint_prefix = {"Human Rights Council": "A/HRC/RES/",
                   "Economic and Social Council": "E/RES/"}
    for c in citations:
        for candidate in c.candidates:
            if candidate in symbol_map:
                c.symbol = candidate
                c.doc_id = symbol_map[candidate]
                break
        else:
            if c.symbol is None and c.candidates:
                # Unresolved: record the organ-appropriate symbol when the
                # 60-char window names one, else the first candidate.
                prefix = hint_prefix.get(c.organ_hint or "")
                c.symbol = next(
                    (x for x in c.candidates if prefix and x.startswith(prefix)),
                    c.candidates[0])
        if citing_doc_id is not None and c.doc_id == citing_doc_id:
            c.doc_id = None
    return citations


def referenced_docs(citations: Iterable[Citation],
                    max_references: int = DEFAULT_MAX_REFERENCES,
                    ) -> tuple[list[Citation], list[str]]:
    """(kept citations, dropped symbols): one per resolved document,
    first-mention order -- the order of mention tracks how central a cited
    instrument is, same rationale as eurlex_context."""
    kept: list[Citation] = []
    dropped: list[str] = []
    seen: set[str] = set()
    for c in citations:
        if c.doc_id is None or c.doc_id in seen:
            continue
        seen.add(c.doc_id)
        if len(kept) < max_references:
            kept.append(c)
        else:
            dropped.append(c.symbol or c.doc_id)
    return kept, dropped


def anchored_block_index(block_texts: Sequence[str], paragraph: int) -> int | None:
    """First block (document order) containing a line that starts the cited
    operative paragraph. Measured: 91% unique, 94% found; first-match wins
    because operative numbering precedes annex/section restarts."""
    pattern = re.compile(rf"(?m)^\s*{paragraph}\.\s")
    for index, text in enumerate(block_texts):
        if pattern.search(text):
            return index
    return None


# --------------------------------------------------------------------------- #
# Validation harness: sample citing blocks, write a manual-review file.
# --------------------------------------------------------------------------- #

def _context(text: str, start: int, end: int, width: int = 80) -> str:
    before = text[max(0, start - width):start].replace("\n", " ")
    after = text[end:end + width].replace("\n", " ")
    return f"…{before}«{text[start:end]}»{after}…"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=int, default=400,
                        help="citing target blocks to include in the review file")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--docs", default=None)
    parser.add_argument("--blocks", default=None)
    parser.add_argument("--out", default=str(
        paths.UN_DIR / "references_review_sample.md"))
    args = parser.parse_args()

    import random
    from collections import Counter
    from clir_bench.domains.legal.qac.un_context import BlockIndex

    random.seed(args.seed)
    index = BlockIndex(blocks_path=args.blocks, docs_path=args.docs)
    symbol_map = {normalise_symbol(d["symbol"]): did
                  for did, d in index.docs.items()}

    doc_ids = [d for d, row in index.docs.items() if row.get("n_targets", 0)]
    random.shuffle(doc_ids)

    kinds: Counter = Counter()
    resolved_kinds: Counter = Counter()
    anchors_found = anchors_missed = self_cites = 0
    blocks_seen = 0
    sections: list[str] = []

    for doc_id in doc_ids:
        if len(sections) >= args.sample:
            break
        doc = index.docs[doc_id]
        blocks = index.blocks_for(doc_id)
        for idx in doc.get("target_idxs", []):
            if len(sections) >= args.sample:
                break
            block = blocks[idx]
            blocks_seen += 1
            cites = resolve_citations(extract_citations(block.texts["en"]),
                                      symbol_map, citing_doc_id=doc_id)
            if not cites:
                continue
            lines = [f"## {block.block_id}", ""]
            for c in cites:
                kinds[c.kind] += 1
                if c.doc_id:
                    resolved_kinds[c.kind] += 1
                    title = index.docs[c.doc_id]["title"][:100]
                    status = f"→ **{c.symbol}** — {title}"
                    if c.paragraph is not None and c.section_letter is None:
                        cited = index.blocks_for(c.doc_id)
                        hit = anchored_block_index(
                            [b.texts["en"] for b in cited], c.paragraph)
                        if hit is None:
                            anchors_missed += 1
                            status += f"  ·  ¶{c.paragraph}: NOT FOUND (head block fallback)"
                        else:
                            anchors_found += 1
                            preview = cited[hit].texts["en"].split("\n")[0][:90]
                            status += f"  ·  ¶{c.paragraph} → block {hit}: “{preview}”"
                elif c.kind in (KIND_ROMAN, KIND_ES):
                    status = "→ UNRESOLVED (pre-1994 / no such docs in corpus)"
                elif c.symbol and normalise_symbol(index.docs[doc_id]["symbol"]) == c.symbol:
                    self_cites += 1
                    status = "→ SELF-CITATION (dropped)"
                else:
                    status = f"→ UNRESOLVED ({c.symbol or c.raw}: not in corpus)"
                lines.append(f"- `{c.kind}` {_context(block.texts['en'], c.start, c.end)}")
                lines.append(f"  {status}")
            lines.append("")
            sections.append("\n".join(lines))

    total = sum(kinds.values())
    resolved = sum(resolved_kinds.values())
    header = [
        "# UN cross-reference extraction — manual review sample",
        "",
        f"Scanned {blocks_seen:,} target blocks (seed {args.seed}); "
        f"{len(sections)} citing blocks shown; {total} citations, "
        f"{resolved} resolved ({resolved / max(total, 1):.0%}); "
        f"{self_cites} self-citations dropped.",
        "",
        "| kind | found | resolved |", "|---|---|---|",
    ]
    for kind, n in kinds.most_common():
        header.append(f"| {kind} | {n} | {resolved_kinds.get(kind, 0)} |")
    header.append(
        f"\nParagraph anchors: {anchors_found} located, {anchors_missed} "
        "fell back to the head block.\n")

    out = Path(args.out)
    out.write_text("\n".join(header) + "\n" + "\n".join(sections),
                   encoding="utf-8")
    print(f"wrote {len(sections)} citing blocks -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
