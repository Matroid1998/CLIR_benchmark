"""
Assemble the model input for EUR-Lex question generation.

A question is generated *about one article*, but EU legislation cross-references
constantly, so an article read alone is often not answerable: "processing is
lawful only if ... Article 9(2) applies" means nothing without Article 9. The
extracted reference graph is what lets those articles travel together.

Two things this module is careful about, because both change what the model can
do:

**The target and the context are separated in the payload.** They are not
concatenated into one blob. The prompt tells the model to write the question
about the TARGET block; the REFERENCED block exists so the answer can be
complete. Without the separation the model drifts and asks about whichever
article happened to be most interesting.

**References are capped.** One article in the corpus cites 345 others -- the
delegated-powers articles enumerate half the act. Sending all of them would
bury the target, blow the context window, and make "which articles are involved"
meaningless. References are taken in order of first mention (which tracks how
central they are to the article's argument) and capped; whatever is dropped is
recorded, never silently discarded.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from clir_bench.domains.legal.structure import ACT_LANGUAGES, paths

# Beyond this the target stops being the subject of the payload. Measured over
# the 16,701 citing articles in the corpus: median 1 reference, p90 = 5,
# p95 = 7, max 256. A cap of 6 carries 95.0% of citing articles whole; raising
# it to 10 buys 3 points more and lets a single delegated-powers article drag in
# an entire act.
DEFAULT_MAX_REFERENCES = 6

# Per-reference character budget. The target is never truncated.
DEFAULT_REFERENCE_CHARS = 4000

TARGET_HEADER = "### TARGET ARTICLE — write the questions about THIS article"
CONTEXT_HEADER = ("### REFERENCED ARTICLES — supporting context only, cited by the "
                  "target article. Do not write questions *about* these.")


@dataclass
class ArticleUnit:
    """One article, in every language version that exists.

    Carries its own document metadata -- act title and structural position --
    because an article shown to a model without them is a page torn out of a
    book: the generator cannot tell a cosmetics regulation from a customs one,
    and writes questions that are unanswerable once the document is out of view.
    Every field here is per-language except the article number, which is
    language-independent by drafting rule.
    """

    eli_id: str
    celex_id: str
    article_number: str
    headings: dict[str, str] = field(default_factory=dict)
    texts: dict[str, str] = field(default_factory=dict)
    act_titles: dict[str, str] = field(default_factory=dict)
    locations: dict[str, str] = field(default_factory=dict)

    def languages(self) -> list[str]:
        return [lg for lg in ACT_LANGUAGES if self.texts.get(lg)]


@dataclass
class GenerationPayload:
    """What gets sent, plus the bookkeeping needed to interpret what comes back."""

    target: ArticleUnit
    references: list[ArticleUnit]
    dropped_references: list[str]
    text: str

    @property
    def involved_universe(self) -> list[str]:
        """Article numbers the model is allowed to name as involved."""
        return [self.target.article_number] + [r.article_number for r in self.references]


class ArticleIndex:
    """Articles and their intra-act reference edges, keyed for lookup."""

    def __init__(self, articles_path=None, edges_path=None) -> None:
        self.by_eli: dict[str, ArticleUnit] = {}
        self.by_act: dict[str, list[str]] = defaultdict(list)
        self._load_articles(articles_path or paths.ARTICLES_JSONL)
        self.references: dict[str, list[str]] = defaultdict(list)
        self._load_edges(edges_path or paths.INTERNAL_EDGES_JSONL)

    def _load_articles(self, path) -> None:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if row["unit_type"] != "article" or not row.get("eli_id"):
                    continue
                unit = self.by_eli.get(row["eli_id"])
                if unit is None:
                    unit = ArticleUnit(row["eli_id"], row["celex_id"], row["article_number"])
                    self.by_eli[row["eli_id"]] = unit
                    self.by_act[row["celex_id"]].append(row["eli_id"])
                unit.texts[row["language"]] = row["text"]
                unit.headings[row["language"]] = row.get("heading", "")
                unit.act_titles[row["language"]] = row.get("act_title", "")
                unit.locations[row["language"]] = structural_location(row)

    def _load_edges(self, path) -> None:
        # Ordered by first mention: char_start tracks how central a reference is
        # to the article's argument better than any ranking we could invent.
        rows = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                edge = json.loads(line)
                if edge.get("source_unit_type") != "article":
                    continue
                if edge.get("target_unit_type") != "article":
                    continue
                rows.append(edge)
        rows.sort(key=lambda e: (e["source_article_id"], e["char_start"]))
        for edge in rows:
            targets = self.references[edge["source_article_id"]]
            if edge["target_article_id"] not in targets:
                targets.append(edge["target_article_id"])

    def build(self, target_eli: str, *,
              max_references: int = DEFAULT_MAX_REFERENCES,
              reference_chars: int = DEFAULT_REFERENCE_CHARS,
              languages: Sequence[str] = ACT_LANGUAGES) -> GenerationPayload | None:
        target = self.by_eli.get(target_eli)
        if target is None or not target.languages():
            return None

        wanted = [t for t in self.references.get(target_eli, []) if t != target_eli]
        kept, dropped = wanted[:max_references], wanted[max_references:]
        references = [self.by_eli[e] for e in kept if e in self.by_eli]

        text = render_payload(target, references, languages=languages,
                              reference_chars=reference_chars)
        return GenerationPayload(target, references,
                                 [self.by_eli[e].article_number for e in dropped
                                  if e in self.by_eli],
                                 text)


def structural_location(row: dict) -> str:
    """"PART TWO › TITLE I › CHAPTER 2 › SECTION 3" -- whichever levels exist.

    All four grouping levels are optional in EU acts and most acts have none, so
    this is built from what is present rather than from a fixed template.
    """
    parts = []
    for number_key, title_key in (("", "part"), ("", "title_division"),
                                  ("chapter_number", "chapter"),
                                  ("section_number", "section")):
        number = (row.get(number_key) or "").strip() if number_key else ""
        title = (row.get(title_key) or "").strip()
        if number and title:
            parts.append(f"{number} {title}")
        elif number or title:
            parts.append(number or title)
    return " › ".join(parts)


def _block(unit: ArticleUnit, language: str, *, limit: int | None) -> str:
    heading = unit.headings.get(language) or ""
    body = unit.texts.get(language, "")
    if limit and len(body) > limit:
        body = body[:limit].rstrip() + " […truncated]"
    label = f"Article {unit.article_number}"
    if heading:
        label += f" — {heading}"
    lines = [f"[{language.upper()}] {label}"]
    act = unit.act_titles.get(language) or ""
    if act:
        lines.append(f"  Act: {act}")
    location = unit.locations.get(language) or ""
    if location:
        lines.append(f"  Location: {location}")
    lines.append(body)
    return "\n".join(lines)


def render_payload(target: ArticleUnit, references: Iterable[ArticleUnit], *,
                   languages: Sequence[str] = ACT_LANGUAGES,
                   reference_chars: int | None = DEFAULT_REFERENCE_CHARS) -> str:
    """The user message: target block, then reference blocks, clearly separated.

    Every language version of each article is included, preserving the
    pipeline's cross-lingual grounding property -- the generator and the graders
    see the same act in all its language versions rather than one translation.
    """
    present = [lg for lg in languages if target.texts.get(lg)]
    parts = [TARGET_HEADER,
             "\n\n".join(_block(target, lg, limit=None) for lg in present)]

    references = list(references)
    if references:
        parts.append(CONTEXT_HEADER)
        for unit in references:
            unit_langs = [lg for lg in languages if unit.texts.get(lg)]
            parts.append("\n\n".join(
                _block(unit, lg, limit=reference_chars) for lg in unit_langs))
    else:
        parts.append("### REFERENCED ARTICLES — none. "
                     "The target article cites no other article of this act.")
    return "\n\n".join(parts)


def normalise_involved(raw, payload: GenerationPayload) -> tuple[list[str], list[str]]:
    """(accepted article numbers, rejected tokens) from the model's answer.

    The model names plain article numbers because that is what it can see in the
    text. They are validated against the articles actually supplied -- a number
    the model never received cannot be an honest citation -- and the target is
    always included, since the question is by construction about it.
    """
    universe = set(payload.involved_universe)
    accepted: list[str] = []
    rejected: list[str] = []
    items: list[str] = []
    if isinstance(raw, str):
        items = [p.strip() for p in raw.replace(" and ", ",").split(",")]
    elif isinstance(raw, Iterable):
        items = [str(p).strip() for p in raw]
    for item in items:
        token = item.lower().removeprefix("article").strip(" .()")
        if not token:
            continue
        if token in universe:
            if token not in accepted:
                accepted.append(token)
        else:
            rejected.append(item)
    if payload.target.article_number not in accepted:
        accepted.insert(0, payload.target.article_number)
    order = {n: i for i, n in enumerate(payload.involved_universe)}
    accepted.sort(key=lambda n: order.get(n, 999))
    return accepted, rejected


def involved_elis(numbers: Sequence[str], payload: GenerationPayload) -> list[str]:
    """Map involved article numbers back to ELI ids, for downstream qrels."""
    lookup = {payload.target.article_number: payload.target.eli_id}
    lookup.update({r.article_number: r.eli_id for r in payload.references})
    return [lookup[n] for n in numbers if n in lookup]


__all__ = [
    "ArticleIndex", "ArticleUnit", "GenerationPayload", "render_payload",
    "normalise_involved", "involved_elis",
    "DEFAULT_MAX_REFERENCES", "DEFAULT_REFERENCE_CHARS",
]
