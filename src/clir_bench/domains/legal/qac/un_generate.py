"""
UN question generation: one target block, cited documents and the rest of the
document as understanding-only context.

The payload separates the TARGET BLOCK (questions are about it, and every
answer must exist fully inside it), REFERENCED DOCUMENTS (cited instruments,
supplied only so the model understands the block's citations), and DOCUMENT
CONTEXT (the surrounding document). Neither supporting section may contribute
answer substance -- the faithfulness verifier caps grounding when one does,
and the batch driver refuses to keep a best candidate below that floor.

Usage:
    python -m clir_bench.domains.legal.qac.un_generate \
        --doc 1994/s/res/918_1994_ --block 1 --mode technical --language en --dry-run
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import un_context as ctx
from clir_bench.domains.legal.qac.env import load_env
from clir_bench.domains.legal.un import UN_LANGUAGES
from clir_bench.domains.legal.un import paths as un_paths

PROMPTS = PromptPack("clir_bench.domains.legal.qac.prompts_un")

MODE_TECHNICAL = "technical"
MODE_SEMANTIC = "semantic"
MODE_DESCRIPTIVE = "descriptive"
MODE_LOOKUP = "lookup"
MODE_PRACTITIONERS = "practitioners"

# ``particulars``-style multi-valued fields are joined for the CSV; ``anchors``
# routinely contains commas ("Abkhazia, Georgia"), so it cannot use one.
ANCHOR_SEP = " | "


@dataclass
class Candidate:
    question: str
    answer: str
    classification: str     # question_type (technical) or framing (semantic)
    # ``lookup`` only: the same question with the instrument's official
    # identifier swapped in for the description, plus the subject anchor.
    question_cited: str = ""
    anchor: str = ""
    # ``practitioners`` only: the two-or-more substantive anchor phrases.
    anchors: list[str] = field(default_factory=list)


def is_skip(data: Any) -> bool:
    """True when the model declined the block, e.g. ``[{"skip_reason": ...}]``.

    The ``lookup`` and ``practitioners`` prompts answer a meeting record or a
    boilerplate-only block with a single ``skip_reason`` object instead of an
    empty list, so a skip is distinguishable from a parse failure.
    """
    items = [data] if isinstance(data, Mapping) else list(data or [])
    return bool(items) and all(
        isinstance(item, Mapping) and item.get("skip_reason") and not item.get("question")
        for item in items)


def skip_reason(data: Any) -> str:
    items = [data] if isinstance(data, Mapping) else list(data or [])
    for item in items:
        if isinstance(item, Mapping) and item.get("skip_reason"):
            return str(item["skip_reason"]).strip()
    return ""


def parse_candidates(data: Any, mode: str) -> list[Candidate]:
    """Validate the model's JSON.

    ``mode`` selects which of the prompts' extra fields are read, so a field
    belonging to another mode cannot leak into a row: ``lookup`` carries
    ``question_cited`` and ``anchor``, ``practitioners`` carries ``anchors``.
    """
    if isinstance(data, Mapping):
        data = [data]
    key = "framing" if mode == MODE_SEMANTIC else "question_type"
    out: list[Candidate] = []
    for item in list(data or []):
        if not isinstance(item, Mapping):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if not question or not answer:
            continue
        raw_anchors = item.get("anchors")
        if isinstance(raw_anchors, str):
            raw_anchors = [raw_anchors]
        out.append(Candidate(
            question=question,
            answer=answer,
            classification=str(item.get(key, "other")).strip(),
            question_cited=(str(item.get("question_cited", "")).strip()
                            if mode == MODE_LOOKUP else ""),
            # ``lookup`` and ``semantic`` both carry a single ``anchor``;
            # ``practitioners`` carries the ``anchors`` list instead.
            anchor=(str(item.get("anchor", "")).strip()
                    if mode in (MODE_LOOKUP, MODE_SEMANTIC) else ""),
            anchors=([str(x).strip() for x in (raw_anchors or []) if str(x).strip()]
                     if mode == MODE_PRACTITIONERS else []),
        ))
    return out


def build_messages(payload: ctx.GenerationPayload, mode: str,
                   language: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": PROMPTS.generation(mode, language)},
        {"role": "user", "content": payload.text},
    ]


def generate(payload: ctx.GenerationPayload, *, mode: str, language: str,
             model: str, client: Any, reasoning_effort: str = "medium") -> list[Candidate]:
    from clir_bench.core.llm import chat, parse_json_response

    raw = chat(client, model, build_messages(payload, mode, language),
               reasoning_effort=reasoning_effort)
    return parse_candidates(parse_json_response(raw), mode)


def rows_for(payload: ctx.GenerationPayload, candidates: list[Candidate], *,
             mode: str, language: str) -> list[dict[str, Any]]:
    return [{
        "doc_id": payload.target.doc_id,
        "symbol": payload.target.symbol,
        "block_id": payload.target.block_id,
        "block_index": payload.target.block_index,
        "n_blocks": payload.target.n_blocks,
        "line_start": payload.target.line_start,
        "line_end": payload.target.line_end,
        "question_language": language,
        "mode": mode,
        "question": c.question,
        "answer": c.answer,
        ("framing" if mode == MODE_SEMANTIC else "question_type"): c.classification,
        "references_supplied": ",".join(r.symbol for r in payload.references),
        "references_dropped": ",".join(payload.dropped_references),
        "context_blocks_supplied": len(payload.context_blocks),
        "context_blocks_dropped": payload.n_context_dropped,
    } for c in candidates]


def _cited_docs(index: ctx.BlockIndex, doc_id: str, block_index: int) -> set[str]:
    """In-corpus documents this block cites -- the references that will travel."""
    from clir_bench.domains.legal.qac import un_references as refs
    blocks = index.blocks_for(doc_id)
    if not 0 <= block_index < len(blocks):
        return set()
    citations = refs.resolve_citations(
        refs.extract_citations(blocks[block_index].texts["en"], doc_id=doc_id),
        index.symbols, citing_doc_id=doc_id)
    kept, _ = refs.referenced_docs(citations)
    return {c.doc_id for c in kept if c.doc_id}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc", required=True, help="document id (`.ids` first token)")
    parser.add_argument("--block", type=int, required=True, help="target block index (0-based)")
    parser.add_argument("--mode", default=MODE_TECHNICAL,
                        choices=[MODE_TECHNICAL, MODE_SEMANTIC, MODE_DESCRIPTIVE])
    parser.add_argument("--language", default="en")
    parser.add_argument("--context-chars", type=int, default=ctx.DEFAULT_CONTEXT_CHARS)
    parser.add_argument("--blocks", default=None, help="override blocks_en.jsonl path")
    parser.add_argument("--docs", default=None, help="override docs_en.jsonl path")
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the exact payload and prompt instead of calling the model")
    args = parser.parse_args()
    load_env()

    index = ctx.BlockIndex(blocks_path=args.blocks, docs_path=args.docs)
    if args.doc not in index.docs:
        raise SystemExit(f"unknown document: {args.doc}")
    if args.language != "en":
        if not un_paths.text_file(args.language).exists():
            raise SystemExit(
                f"no 6-way corpus file for '{args.language}': the UN corpus carries "
                f"{', '.join(UN_LANGUAGES)}.")
        # The target document AND the documents it cites, so a non-English
        # dry-run shows the real payload rather than an English-only stand-in.
        cited = _cited_docs(index, args.doc, args.block)
        index.preload_translations([args.language], {args.doc} | cited)
    payload = index.build(args.doc, args.block, context_chars=args.context_chars,
                          languages=ctx.payload_languages(args.language))
    if payload is None:
        raise SystemExit(f"no block {args.block} in {args.doc} "
                         f"({index.docs[args.doc]['n_blocks']} blocks)")

    if args.dry_run:
        print("=" * 78)
        print(f"SYSTEM PROMPT: prompts_un/generation/{args.mode}/{args.language}.txt")
        print(f"  ({len(PROMPTS.generation(args.mode, args.language)):,} chars)")
        print("=" * 78)
        print("USER MESSAGE:")
        print(payload.text)
        print("=" * 78)
        print(f"target          : {payload.target.block_id} "
              f"({payload.target.token_count} tokens, "
              f"lines {payload.target.line_start}-{payload.target.line_end})")
        print(f"references      : {[r.symbol for r in payload.references]}")
        print(f"references drop : {payload.dropped_references}")
        print(f"context supplied: {len(payload.context_blocks)} blocks")
        print(f"context dropped : {payload.n_context_dropped} blocks")
        return

    from clir_bench.core.llm import client_for
    candidates = generate(payload, mode=args.mode, language=args.language,
                          model=args.model, client=client_for(args.model))
    for row in rows_for(payload, candidates, mode=args.mode, language=args.language):
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
