"""
EUR-Lex question generation with resolved cross-references.

Differs from the generic pipeline in exactly two ways, both EUR-Lex specific and
both confined to this package:

1. **What is sent.** The generic pipeline sends one document's language versions
   as an undifferentiated block. Here the payload is three labelled blocks -- the
   target article, the articles of the same act it cites, and the articles of
   OTHER acts it cites when those acts are in the corpus -- built by
   ``eurlex_context``. Nothing in ``core/`` knows about this; the assembled
   string is handed to the same chat helper the rest of the pipeline uses.

2. **What comes back.** Candidates carry ``articles_involved``, the articles the
   generator says are needed to answer: bare numbers for the target's own act,
   ``CELEX:number`` keys for articles of other acts. It is validated here
   against the articles actually supplied: a token the model never received
   cannot be an honest citation, and the target article is always included
   because the question is by construction about it. The LLM grader judges
   whether the declaration is *semantically* right; this code checks that it is
   *structurally* valid, which is the part a rubric grades badly.

The prompts live in ``prompts_eurlex`` rather than ``prompts`` because the legal
pack forbids precisely what this flow now wants -- see that package's README.

Usage:
    python -m clir_bench.domains.legal.qac.eurlex_generate --celex 32009R1223 \
        --article 25 --mode lookup --language en --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import eurlex_context as ctx
from clir_bench.domains.legal.qac.env import load_env

PROMPTS = PromptPack("clir_bench.domains.legal.qac.prompts_eurlex")

# The two practitioner modes. Both are fact-extraction modes and share the
# technical quality columns; they differ in how the question reaches the act.
# ``lookup`` names the regime and carries a second, identifier-bearing rendering
# of the same question; ``fact_pattern`` describes a situation and never cites
# anything at all. Nothing else is generated for EUR-Lex.
MODE_LOOKUP = "lookup"
MODE_FACT_PATTERN = "fact_pattern"
MODES = (MODE_LOOKUP, MODE_FACT_PATTERN)

# ``particulars`` are phrases that routinely contain commas ("40 tonnes placed
# on the Spanish market last year"), so they cannot share the comma join the
# article lists use.
PARTICULAR_SEP = "|"


@dataclass
class Candidate:
    question: str
    answer: str
    classification: str
    articles_involved: list[str]
    involved_elis: list[str]
    rejected_involved: list[str]
    multi_article: bool
    # True when an article of ANOTHER act (a ``CELEX:number`` token) was used.
    cross_act: bool = False
    # ``lookup`` only: the same question with the TARGET act's identifier
    # inserted, that act's conventional short name, and the regime anchor.
    question_cited: str = ""
    instrument_short_name: str = ""
    anchor: str = ""
    # ``fact_pattern`` only: the concrete facts the situation was built from.
    particulars: list[str] = field(default_factory=list)


def _short_name(value: Any) -> str:
    """``instrument_short_name`` is null unless a conventional name is in use.

    JSON ``null`` arrives as ``None``, but a model that is told to write "null"
    sometimes writes the *string*; both mean "no established short name".
    """
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"", "null", "none"} else text


def is_skip(data: Any) -> bool:
    """True when the model declined the article, e.g. ``[{"skip_reason": ...}]``.

    Both prompts answer a boilerplate-only article with a single ``skip_reason``
    object rather than padding out three questions. That is a correct outcome,
    not a parse failure, and callers must be able to tell the two apart.
    """
    items = [data] if isinstance(data, Mapping) else list(data or [])
    return bool(items) and all(
        isinstance(item, Mapping) and item.get("skip_reason") and not item.get("question")
        for item in items)


def skip_reason(data: Any) -> str:
    """The phrase the model gave for declining, or ``""`` if it did not."""
    items = [data] if isinstance(data, Mapping) else list(data or [])
    for item in items:
        if isinstance(item, Mapping) and item.get("skip_reason"):
            return str(item["skip_reason"]).strip()
    return ""


def parse_candidates(data: Any, payload: ctx.GenerationPayload,
                     mode: str) -> list[Candidate]:
    """Validate the model's JSON, including the ``articles_involved`` field.

    ``mode`` selects which of the two prompts' extra fields are read, so a field
    belonging to the other mode cannot leak into a row: ``lookup`` carries
    ``question_cited`` / ``instrument_short_name`` / ``anchor``, ``fact_pattern``
    carries ``particulars``.
    """
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
        involved, rejected = ctx.normalise_involved(item.get("articles_involved"), payload)
        raw_particulars = item.get("particulars")
        if isinstance(raw_particulars, str):
            raw_particulars = [raw_particulars]
        out.append(Candidate(
            question=question,
            answer=answer,
            classification=str(item.get("question_type", "other")).strip(),
            articles_involved=involved,
            involved_elis=ctx.involved_elis(involved, payload),
            rejected_involved=rejected,
            multi_article=len(involved) > 1,
            # Own-act annex keys carry the target's own CELEX and are not
            # cross-act; any other key is.
            cross_act=any(":" in token
                          and not token.startswith(payload.target.celex_id + ":")
                          for token in involved),
            question_cited=(str(item.get("question_cited", "")).strip()
                            if mode == MODE_LOOKUP else ""),
            instrument_short_name=(_short_name(item.get("instrument_short_name"))
                                   if mode == MODE_LOOKUP else ""),
            anchor=(str(item.get("anchor", "")).strip()
                    if mode == MODE_LOOKUP else ""),
            particulars=([str(x).strip() for x in (raw_particulars or []) if str(x).strip()]
                         if mode == MODE_FACT_PATTERN else []),
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
        "question_type": c.classification,
        # Mode-specific columns. Each is empty in the mode that does not emit it,
        # so both modes share one schema and one CSV.
        "question_cited": c.question_cited,
        "instrument_short_name": c.instrument_short_name,
        "anchor": c.anchor,
        "particulars": PARTICULAR_SEP.join(c.particulars),
        # The deliverable: which articles a reader needs. One entry means the
        # target alone; more means the answer crossed a resolved cross-reference.
        "articles_involved": ",".join(c.articles_involved),
        "articles_involved_eli": ",".join(c.involved_elis),
        "multi_article": c.multi_article,
        "cross_act": c.cross_act,
        "reference_articles_supplied": ",".join(r.article_number for r in payload.references),
        "reference_articles_dropped": ",".join(payload.dropped_references),
        "external_references_supplied": ",".join(
            ctx.external_key(u) for u in payload.external_references),
        "external_references_dropped": ",".join(payload.dropped_external_references),
        "annex_references_supplied": ",".join(
            ctx.external_key(u) for u in payload.annexes),
        "annex_references_dropped": ",".join(payload.dropped_annex_references),
        "rejected_involved": ",".join(c.rejected_involved),
    } for c in candidates]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--celex", required=True)
    parser.add_argument("--article", required=True, help="target article number")
    parser.add_argument("--mode", default=MODE_LOOKUP, choices=list(MODES))
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
        print(f"other-act supplied    : {[ctx.external_key(u) for u in payload.external_references]}")
        print(f"other-act dropped     : {payload.dropped_external_references}")
        print(f"annexes supplied      : {[ctx.external_key(u) for u in payload.annexes]}")
        print(f"annexes dropped       : {payload.dropped_annex_references}")
        print(f"declarable universe   : {payload.involved_universe}")
        status = index.status.get(target_eli)
        if status is not None:
            print(f"reference-complete    : {status['complete']} "
                  f"(internal {status['n_internal']}, external {status['n_external_resolved']}, "
                  f"unresolved {status['unresolved_reasons']})")
        return

    from clir_bench.core.llm import client_for
    candidates = generate(payload, mode=args.mode, language=args.language,
                          model=args.model, client=client_for(args.model))
    for row in rows_for(payload, candidates, mode=args.mode, language=args.language):
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
