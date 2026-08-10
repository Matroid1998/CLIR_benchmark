"""
EUR-Lex question generation with resolved cross-references.

Differs from the generic pipeline in exactly two ways, both EUR-Lex specific and
both confined to this package:

1. **What is sent.** The generic pipeline sends one document's language versions
   as an undifferentiated block. Here the payload is two labelled blocks -- the
   target article, then the articles it cites -- built by ``eurlex_context``.
   Nothing in ``core/`` knows about this; the assembled string is handed to the
   same chat helper the rest of the pipeline uses.

2. **What comes back.** Candidates carry ``articles_involved``, the articles the
   generator says are needed to answer. It is validated here against the
   articles actually supplied: a number the model never received cannot be an
   honest citation, and the target article is always included because the
   question is by construction about it. The LLM grader judges whether the
   declaration is *semantically* right; this code checks that it is
   *structurally* valid, which is the part a rubric grades badly.

The prompts live in ``prompts_eurlex`` rather than ``prompts`` because the legal
pack forbids precisely what this flow now wants -- see that package's README.

Usage:
    python -m clir_bench.domains.legal.qac.eurlex_generate --celex 32009R1223 \
        --article 25 --mode technical --language en --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import eurlex_context as ctx
from clir_bench.domains.legal.qac.env import load_env

PROMPTS = PromptPack("clir_bench.domains.legal.qac.prompts_eurlex")

MODE_TECHNICAL = "technical"
MODE_SEMANTIC = "semantic"


@dataclass
class Candidate:
    question: str
    answer: str
    classification: str
    articles_involved: list[str]
    involved_elis: list[str]
    rejected_involved: list[str]
    multi_article: bool


def parse_candidates(data: Any, payload: ctx.GenerationPayload,
                     mode: str) -> list[Candidate]:
    """Validate the model's JSON, including the new ``articles_involved`` field."""
    if isinstance(data, Mapping):
        data = [data]
    out: list[Candidate] = []
    for item in list(data or []):
        if not isinstance(item, Mapping):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if not question or not answer:
            continue
        key = "question_type" if mode == MODE_TECHNICAL else "framing"
        involved, rejected = ctx.normalise_involved(item.get("articles_involved"), payload)
        out.append(Candidate(
            question=question,
            answer=answer,
            classification=str(item.get(key, "other")).strip(),
            articles_involved=involved,
            involved_elis=ctx.involved_elis(involved, payload),
            rejected_involved=rejected,
            multi_article=len(involved) > 1,
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
    return parse_candidates(parse_json_response(raw), payload, mode)


def rows_for(payload: ctx.GenerationPayload, candidates: Sequence[Candidate], *,
             mode: str, language: str) -> list[dict[str, Any]]:
    """QAC rows. ``articles_involved`` is what makes multi-article gold possible."""
    return [{
        "celex_id": payload.target.celex_id,
        "target_article_id": payload.target.eli_id,
        "target_article_number": payload.target.article_number,
        "question_language": language,
        "mode": mode,
        "question": c.question,
        "answer": c.answer,
        ("question_type" if mode == MODE_TECHNICAL else "framing"): c.classification,
        # The deliverable: which articles a reader needs. One entry means the
        # target alone; more means the answer crossed a resolved cross-reference.
        "articles_involved": ",".join(c.articles_involved),
        "articles_involved_eli": ",".join(c.involved_elis),
        "multi_article": c.multi_article,
        "reference_articles_supplied": ",".join(r.article_number for r in payload.references),
        "reference_articles_dropped": ",".join(payload.dropped_references),
        "rejected_involved": ",".join(c.rejected_involved),
    } for c in candidates]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--celex", required=True)
    parser.add_argument("--article", required=True, help="target article number")
    parser.add_argument("--mode", default=MODE_TECHNICAL,
                        choices=[MODE_TECHNICAL, MODE_SEMANTIC])
    parser.add_argument("--language", default="en")
    parser.add_argument("--max-references", type=int, default=ctx.DEFAULT_MAX_REFERENCES)
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the exact payload and prompt instead of calling the model")
    args = parser.parse_args()
    load_env()

    index = ctx.ArticleIndex()
    target_eli = None
    for eli in index.by_act.get(args.celex, []):
        if index.by_eli[eli].article_number == args.article:
            target_eli = eli
            break
    if target_eli is None:
        raise SystemExit(f"no article {args.article} in {args.celex}")

    payload = index.build(target_eli, max_references=args.max_references,
                          languages=ctx.payload_languages(args.language))
    if payload is None:
        raise SystemExit("target article has no text")

    if args.dry_run:
        print("=" * 78)
        print(f"SYSTEM PROMPT: prompts_eurlex/generation/{args.mode}/{args.language}.txt")
        print(f"  ({len(PROMPTS.generation(args.mode, args.language)):,} chars)")
        print("=" * 78)
        print("USER MESSAGE:")
        print(payload.text)
        print("=" * 78)
        print(f"target                : Article {payload.target.article_number} "
              f"({payload.target.eli_id})")
        print(f"references supplied   : {[r.article_number for r in payload.references]}")
        print(f"references dropped    : {payload.dropped_references}")
        print(f"declarable universe   : {payload.involved_universe}")
        return

    from clir_bench.core.llm import client_for
    candidates = generate(payload, mode=args.mode, language=args.language,
                          model=args.model, client=client_for(args.model))
    for row in rows_for(payload, candidates, mode=args.mode, language=args.language):
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
