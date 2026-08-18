"""
Assemble the model input for UN question generation.

A question is generated *about one block* -- 150-220 tokens of one UN document
-- but a block cut from the middle of a report is often uninterpretable alone:
"the Mission", "the present report", "the reporting period" all point outside
it. So the payload carries the rest of the document as context.

The contract differs from ``eurlex_context`` in one deliberate way: there the
referenced articles may *complete* an answer; here the DOCUMENT CONTEXT is
disambiguation-only, and the prompts (``prompts_un``) instruct the model that
every answer must come from the target block itself. The faithfulness verifier
enforces it. What travels in the context is therefore a coverage decision, not
a grounding one: send the whole document when it fits the budget, otherwise the
document opening (which resolves document-level references) plus the passages
nearest the target (which resolve local ones).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from clir_bench.domains.legal.un import paths
from clir_bench.domains.legal.qac import un_references as refs

# Whole-document context fits this budget for roughly three quarters of the
# corpus (median document is ~8k chars, p75 ~29k). Beyond it, context becomes
# the opening plus a window around the target.
DEFAULT_CONTEXT_CHARS = 30_000

TARGET_HEADER = "### TARGET BLOCK — write the questions about THIS text"
REFERENCES_HEADER = ("### REFERENCED DOCUMENTS — other documents CITED by the target "
                     "block, supplied so you can UNDERSTAND those citations. Context "
                     "only: never a source of answers, never the subject of a question.")
REFERENCES_NONE = ("### REFERENCED DOCUMENTS — none. "
                   "The target block cites no other document available in the corpus.")
CONTEXT_HEADER = ("### DOCUMENT CONTEXT — surrounding text of the SAME document, "
                  "supporting context only. It resolves what the target block "
                  "leaves implicit; it is never a source of answers.")
CONTEXT_NONE = ("### DOCUMENT CONTEXT — none. "
                "The target block is the whole document.")
TARGET_PLACEHOLDER = "[... the TARGET BLOCK appears here ...]"
GAP = "[... passages omitted ...]"


def payload_languages(question_language: str) -> tuple[str, ...]:
    """Which language versions to send, given the question's language.

    Same policy as EUR-Lex: English only when asking in English, otherwise the
    question language first plus English as the pivot reading. Only English
    blocks are extracted today, so non-English versions join once their line
    ranges are read from the other 6-way files.
    """
    if question_language == "en":
        return ("en",)
    return (question_language, "en")


@dataclass
class BlockUnit:
    """One block, with the document metadata the prompts expect.

    Junk lines (mastheads, TOC rows, vote rosters) live in the gaps between
    blocks, so they are silently absent from any rendered context -- a block's
    text is always exactly the corpus lines of its range.
    """

    block_id: str
    doc_id: str
    symbol: str
    title: str
    block_index: int
    n_blocks: int
    line_start: int
    line_end: int
    token_count: int
    in_range: bool
    usable: bool = True
    heading: str = ""
    texts: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: dict) -> "BlockUnit":
        return cls(
            block_id=row["block_id"], doc_id=row["doc_id"],
            symbol=row.get("symbol", row["doc_id"]), title=row.get("title", ""),
            block_index=row["block_index"], n_blocks=row["n_blocks"],
            line_start=row["line_start"], line_end=row["line_end"],
            token_count=row["token_count"], in_range=row.get("in_range", True),
            usable=row.get("usable", True), heading=row.get("heading", ""),
            texts={"en": row["text"]},
        )


@dataclass
class ReferencedDoc:
    """A document cited by the target block, rendered for the payload."""

    symbol: str
    doc_id: str
    title: str
    text: str                   # anchored-paragraph block or head block, capped
    paragraph: int | None       # set only when the anchor was actually located


@dataclass
class GenerationPayload:
    """What gets sent, plus the bookkeeping to interpret what comes back."""

    target: BlockUnit
    context_blocks: list[BlockUnit]     # in document order, target excluded
    n_context_dropped: int              # blocks that did not fit the budget
    references: list[ReferencedDoc]     # cited documents, first-mention order
    dropped_references: list[str]       # resolved but beyond the cap
    text: str


class BlockIndex:
    """Documents in memory, blocks on disk behind per-document seeks.

    ``docs_en.jsonl`` (86k rows) is small enough to hold; ``blocks_en.jsonl``
    (the whole English corpus plus overhead) is not, so each document's block
    rows are read on demand at the byte offset the builder recorded. A fresh
    file handle per read keeps this safe under the batch driver's threads.
    """

    def __init__(self, blocks_path: Path | None = None,
                 docs_path: Path | None = None) -> None:
        self.blocks_path = Path(blocks_path or paths.BLOCKS_JSONL)
        self.docs: dict[str, dict] = {}
        with open(docs_path or paths.DOCS_JSONL, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                self.docs[row["doc_id"]] = row
        # Collision-free over the whole corpus; the resolution mechanism for
        # cross-references found in target-block text.
        self.symbol_map: dict[str, str] = {
            refs.normalise_symbol(row["symbol"]): doc_id
            for doc_id, row in self.docs.items()}

    def blocks_for(self, doc_id: str) -> list[BlockUnit]:
        doc = self.docs[doc_id]
        units: list[BlockUnit] = []
        with open(self.blocks_path, "rb") as fh:
            fh.seek(doc["offset"])
            for _ in range(doc["n_blocks"]):
                units.append(BlockUnit.from_row(json.loads(fh.readline())))
        return units

    def build(self, doc_id: str, block_index: int, *,
              context_chars: int = DEFAULT_CONTEXT_CHARS,
              max_references: int = refs.DEFAULT_MAX_REFERENCES,
              reference_chars: int | None = refs.DEFAULT_REFERENCE_CHARS,
              languages: tuple[str, ...] = ("en",)) -> GenerationPayload | None:
        blocks = self.blocks_for(doc_id)
        if not 0 <= block_index < len(blocks):
            return None
        target = blocks[block_index]
        if not target.texts.get("en"):
            return None

        citations = refs.resolve_citations(
            refs.extract_citations(target.texts["en"]), self.symbol_map,
            citing_doc_id=doc_id)
        kept, dropped = refs.referenced_docs(citations, max_references)
        references = [self._render_reference(c, reference_chars) for c in kept]

        chosen = _select_context(blocks, block_index, context_chars)
        text = render_payload(target, chosen, references=references,
                              languages=languages)
        return GenerationPayload(target, chosen, len(blocks) - 1 - len(chosen),
                                 references, dropped, text)

    def _render_reference(self, citation: refs.Citation,
                          limit: int | None) -> ReferencedDoc:
        """The cited material that travels.

        With a character limit (the windowed pipeline): one excerpt -- the
        paragraph-anchored block when the citation names a paragraph we can
        locate (and is not a lettered section, where the anchor is
        unreliable), else the document's opening block.

        With ``limit=None`` (the whole-fit pipeline): the ENTIRE cited
        document, blocks joined in order -- the fit filter has already
        guaranteed it fits the budget.
        """
        doc = self.docs[citation.doc_id]
        blocks = self.blocks_for(citation.doc_id)
        hit = None
        if (citation.paragraph is not None and citation.section_letter is None
                and blocks):
            hit = refs.anchored_block_index(
                [b.texts["en"] for b in blocks], citation.paragraph)
        paragraph = citation.paragraph if hit is not None else None
        if limit is None:
            text = "\n\n".join(b.texts["en"] for b in blocks)
        else:
            body = blocks[hit] if hit is not None else (blocks[0] if blocks else None)
            text = body.texts["en"] if body else ""
            if len(text) > limit:
                text = text[:limit].rstrip() + " […truncated]"
        return ReferencedDoc(symbol=citation.symbol or doc["symbol"],
                             doc_id=citation.doc_id, title=doc["title"],
                             text=text, paragraph=paragraph)


def _select_context(blocks: list[BlockUnit], target_index: int,
                    budget: int) -> list[BlockUnit]:
    """Context blocks within the character budget, in document order.

    Priority: the document opening first (it resolves "the present report" and
    names the mission), then neighbours expanding outward from the target (they
    resolve local anaphora). For most documents the budget admits everything
    and the context is simply the whole rest of the document.
    """
    candidates: list[int] = []
    if target_index != 0:
        candidates.append(0)
    step = 1
    while len(candidates) < len(blocks) - 1:
        for index in (target_index - step, target_index + step):
            if 0 <= index < len(blocks) and index != target_index and index not in candidates:
                candidates.append(index)
        step += 1

    chosen: set[int] = set()
    remaining = budget
    for index in candidates:
        cost = len(blocks[index].texts.get("en", ""))
        if cost > remaining:
            break
        chosen.add(index)
        remaining -= cost
    return [blocks[i] for i in sorted(chosen)]


def _metadata(unit: BlockUnit, language: str) -> str:
    # No block numbering in the payload: the model has no use for the block's
    # position beyond the placeholder in the context, and a number invites
    # questions about it. Position stays in the data (block_index), not the prompt.
    lines = [f"[{language.upper()}] Document: {unit.symbol}"]
    if unit.title:
        lines.append(f"  Title: {unit.title}")
    return "\n".join(lines)


def render_payload(target: BlockUnit, context_blocks: list[BlockUnit], *,
                   references: list[ReferencedDoc] = (),
                   languages: tuple[str, ...] = ("en",)) -> str:
    """The user message: target block, referenced documents, then the document
    context, clearly separated -- the literal ``###`` markers are the contract
    pinned by the ``prompts_un`` pack.

    The context is rendered in document order with a placeholder where the
    target sits and gap markers where blocks were dropped for budget, so the
    model can see the passage's position without receiving it twice.
    """
    present = [lg for lg in languages if target.texts.get(lg)]
    parts = [TARGET_HEADER]
    for language in present:
        parts.append(f"{_metadata(target, language)}\n{target.texts[language]}")

    if references:
        parts.append(REFERENCES_HEADER)
        for r in references:
            anchor = f" (cited paragraph {r.paragraph})" if r.paragraph else ""
            parts.append(f"Reference: {r.symbol} — {r.title}{anchor}\n{r.text}")
    else:
        parts.append(REFERENCES_NONE)

    if not context_blocks:
        parts.append(CONTEXT_NONE)
        return "\n\n".join(parts)

    parts.append(CONTEXT_HEADER)
    for language in present:
        pieces: list[str] = []
        previous = -1
        placed = False
        for unit in context_blocks:
            if not placed and unit.block_index > target.block_index:
                if target.block_index - previous > 1:
                    pieces.append(GAP)
                pieces.append(TARGET_PLACEHOLDER)
                previous = target.block_index
                placed = True
            if unit.block_index - previous > 1:
                pieces.append(GAP)
            pieces.append(unit.texts.get(language, ""))
            previous = unit.block_index
        if not placed:
            if target.block_index - previous > 1:
                pieces.append(GAP)
            pieces.append(TARGET_PLACEHOLDER)
            if target.block_index < target.n_blocks - 1:
                pieces.append(GAP)
        elif previous < target.n_blocks - 1:
            pieces.append(GAP)
        body = "\n\n".join(pieces)
        pieces_header = f"[{language.upper()}] Document {target.symbol} — surrounding passages"
        parts.append(f"{pieces_header}\n{body}")
    return "\n\n".join(parts)


__all__ = [
    "BlockIndex", "BlockUnit", "GenerationPayload", "ReferencedDoc",
    "render_payload", "payload_languages", "DEFAULT_CONTEXT_CHARS",
    "TARGET_HEADER", "REFERENCES_HEADER", "CONTEXT_HEADER",
]
