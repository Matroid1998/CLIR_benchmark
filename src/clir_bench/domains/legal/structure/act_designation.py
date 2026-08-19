"""
Turn the surface form of an act citation into a CELEX id -- and refuse to guess.

"Article 15 of Regulation (EC) No 2792/1999" names an act by designator and
identifier. The identifier encodes a year and a serial number, but in two
different orders depending on the era and the instrument type: regulations
before 2015 are numbered ``No 2792/1999`` (number/year), directives
``2004/109/EC`` (year/number), and everything adopted from 1 January 2015 is
``(EU) 2015/560`` (year/number). Read the components in the wrong order and the
result is a *different, plausible* act -- ``Regulation (EC) No 2004/2003``
reversed is 32004R2003, which exists in this corpus. Checking the candidate
against the corpus therefore does not make a guess safe; only the shape does.

So this module never guesses. Each identifier shape fixes the ordering, the
first matching shape wins, and a surface that matches no shape is rejected with
a reason rather than tried the other way round. Measured over the 2,293 distinct
act surfaces cited from articles in the corpus, this resolves 13,390 citations
(43.7 %) to 790 acts with zero order-ambiguous cases; the remainder are acts
outside the corpus, unnumbered instruments (Treaty, Financial Regulation) or
back-references ("of that Regulation") that carry no identifier at all.

Only regulations (CELEX letter R) and directives (L) can resolve here because
those are the only instrument types the corpus holds; decisions and framework
decisions parse but are reported as ``doc_type_not_in_corpus``.

The module is deliberately free of I/O and of imports from the rest of the
package so that both the extractor (``references.py``, to recognise an act
citing itself by identifier) and the resolver (``resolve_external.py``) can use
it without a dependency cycle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Container

# The instrument types that carry a numeric identifier. Word boundaries and
# optional plurals so that "Regulations" (Staff Regulations) still names the
# designator and can be reported as an unnumbered surface.
_DESIG = r"(?P<desig>Framework\s+Decision|Regulations?|Directives?|Decisions?)"
# "(EC)", "(EU)", "(EEC)", "(EU, Euratom)", "(ECSC, EEC, Euratom)", "(CE)" (a
# Romance-language tag leaking into English text). Any comma list of the known
# treaty codes; the code itself carries no information the parser needs.
_ONE_CODE = r"(?:Euratom|EURATOM|ECSC|EEC|EC|EU|CEE|CE)"
_CODE = rf"\(\s*(?P<code>{_ONE_CODE}(?:\s*,\s*{_ONE_CODE})*)\s*\)"
_YEAR4 = r"(?:19|20)\d{2}"
_YEAR4_RE = re.compile(_YEAR4)
_SUFFIX = r"(?P<suffix>Euratom|EEC|EC|EU|CEE|CE|JHA|CFSP|ECSC)"

# Shape A/C/E: "[(CODE)] No N/YYYY[/SUFFIX]" -> number first. This is the
# pre-2015 regulation style ("Regulation (EC) No 2792/1999") and the numbered
# decision style ("Decision No 280/2004/EC"). "No" is what fixes the order.
_NUM_FIRST = re.compile(
    rf"{_DESIG}\s*(?:{_CODE})?\s*No\.?\s*(?P<num>\d{{1,4}})\s*/\s*"
    rf"(?P<yr>{_YEAR4}|\d{{2}})(?!\d)(?:\s*/\s*{_SUFFIX}\b)?", re.I)

# Shape D: "[(CODE)] YYYY/N/SUFFIX" or "YY/N/SUFFIX" -> year first. The trailing
# suffix ("/EC", "/EEC", "/EU") is what fixes the order: this is the directive
# and unnumbered-decision style ("Directive 2004/109/EC", "Directive 83/349/EEC").
_YEAR_FIRST_SUFFIX = re.compile(
    rf"{_DESIG}\s*(?:{_CODE})?\s*(?P<yr>{_YEAR4}|\d{{2}})\s*/\s*"
    rf"(?P<num>\d{{1,4}})\s*/\s*{_SUFFIX}\b", re.I)

# Shape B: "(EU) 2015/N" -> year first, no "No", no suffix. Year-first numbering
# without a suffix only exists from 1 January 2015, so the year is required to
# be >= 2015; anything else with this surface is left to the next shape.
_CODE_YEAR_FIRST = re.compile(
    rf"{_DESIG}\s*{_CODE}\s*(?P<yr>20(?:1[5-9]|[2-9]\d))\s*/\s*"
    rf"(?P<num>\d{{1,4}})(?![\d/])", re.I)

# Shape A': "Regulation (CODE) N/YYYY" -- the pre-2015 regulation style with the
# "No" omitted by the drafter ("Regulation (EC) 601/2004"). Number first, and
# the second component must be a full four-digit year. Regulations only: no
# directive was ever numbered this way.
_CODE_NUM_FIRST = re.compile(
    rf"(?P<desig>Regulations?)\s*{_CODE}\s*(?P<num>\d{{1,4}})\s*/\s*"
    rf"(?P<yr>{_YEAR4})(?![\d/])", re.I)

# Shape D': "Directive YYYY/N" with the suffix omitted ("Directive 2014/65",
# "Directive 86/635"). Directives have only ever been numbered year-first, so
# the missing suffix costs nothing; the second component may not itself look
# like a four-digit year, which is the one surface that would be ambiguous.
_DIR_YEAR_FIRST = re.compile(
    rf"(?P<desig>Directives?)\s*(?P<yr>{_YEAR4}|\d{{2}})\s*/\s*"
    rf"(?P<num>\d{{1,4}})(?![\d/])", re.I)

# Shape A'': "Regulation N/YYYY" with both the code and the "No" omitted
# ("Regulation 1303/2013"). Accepted only when exactly one component is a
# four-digit year, so the order is still fixed by the surface, not guessed:
# "Regulation 2004/2003" matches neither branch and is refused.
_BARE_REG_NUM_FIRST = re.compile(
    rf"(?P<desig>Regulations?)\s+(?P<num>\d{{1,4}})\s*/\s*(?P<yr>{_YEAR4})(?![\d/])", re.I)
_BARE_REG_YEAR_FIRST = re.compile(
    rf"(?P<desig>Regulations?)\s+(?P<yr>20(?:1[5-9]|[2-9]\d))\s*/\s*(?P<num>\d{{1,4}})(?![\d/])", re.I)

_SHAPES = (
    ("num_first", _NUM_FIRST),
    ("year_first_suffix", _YEAR_FIRST_SUFFIX),
    ("code_year_first", _CODE_YEAR_FIRST),
    ("code_num_first", _CODE_NUM_FIRST),
    ("dir_year_first", _DIR_YEAR_FIRST),
    ("bare_reg_num_first", _BARE_REG_NUM_FIRST),
    ("bare_reg_year_first", _BARE_REG_YEAR_FIRST),
)

# "Regulation (EU) No" -- the extractor once lost the digits after a space
# before the slash. The surface is not wrong, it is incomplete.
_TRUNCATED_RE = re.compile(r"\bNo\.?\s*$", re.I)
# "the Directive", "Regulation" -- a definite back-reference to an act named
# earlier, mislabelled as non-anaphoric upstream because it lacks a determiner.
_BARE_DESIGNATOR_RE = re.compile(
    r"(?:the\s+)?(?:Council\s+|Commission\s+)?(?:Regulation|Directive|Decision)s?", re.I)
# Instruments the corpus does not hold and that carry no CELEX-shaped number
# in citations: "Article 87 of the Treaty", "Article 12 of the Convention".
_UNSUPPORTED_RE = re.compile(
    r"\b(?:Treaty|Treaties|TFEU|TEU|Protocol|Convention|Charter|Agreement"
    r"|Recommendation|Act\s+of\s+Accession|Statute)\b", re.I)
_DIGITS_RE = re.compile(r"\d")

LETTER = {"regulation": "R", "regulations": "R",
          "directive": "L", "directives": "L",
          "decision": "D", "decisions": "D",
          "framework decision": "F"}

# CELEX doc types the corpus contains. Anything else parses but cannot resolve.
CORPUS_LETTERS = frozenset("RL")


@dataclass(frozen=True)
class ActRef:
    """A parsed act identifier. ``shape`` records which rule fixed the order.

    ``plural`` is set when the designator was "Regulations"/"Directives": the
    citation names several acts ("Articles 3 and 5 of Regulations (EU) No
    1093/2010, No 1094/2010 and No 1095/2010") and only the first identifier is
    in the surface, so resolving it would attach the articles to one act and
    silently lose the others.
    """

    letter: str
    year: int
    number: int
    shape: str
    plural: bool = False

    @property
    def celex(self) -> str:
        return f"3{self.year}{self.letter}{self.number:04d}"


def parse_act_designation(surface: str) -> ActRef | None:
    """Parse "Regulation (EC) No 2792/1999"-style surfaces; None if no shape fits.

    Two-digit years are read as 19yy only for 52..99 (the Communities date from
    1952); "No 5/07" is refused rather than read as 2007, because that surface
    is not something the drafting rules produce.
    """
    text = " ".join(surface.split())
    for shape, pattern in _SHAPES:
        match = pattern.search(text)
        if not match:
            continue
        designator = " ".join(match.group("desig").lower().split())
        letter = LETTER[designator]
        year_raw, number_raw = match.group("yr"), match.group("num")
        if shape.startswith("bare_reg") and _YEAR4_RE.fullmatch(number_raw) \
                and _YEAR4_RE.fullmatch(year_raw):
            return None   # "Regulation 2004/2003": both components read as years
        year, number = int(year_raw), int(number_raw)
        if len(year_raw) == 2:
            if not 52 <= year <= 99:
                return None
            year += 1900
        return ActRef(letter=letter, year=year, number=number, shape=shape,
                      plural=designator.endswith("s"))
    return None


def unresolvable_reason(surface: str) -> str:
    """Why a surface that parsed to nothing cannot be resolved."""
    text = " ".join(surface.split())
    if _UNSUPPORTED_RE.search(text):
        return "designator_unsupported"
    if _TRUNCATED_RE.search(text):
        return "truncated_surface"
    if not _DIGITS_RE.search(text):
        return "no_identifier"
    return "malformed_surface"


def is_bare_designator(surface: str) -> bool:
    """"the Directive", "Regulation": a back-reference with no identifier."""
    return bool(_BARE_DESIGNATOR_RE.fullmatch(" ".join(surface.split())))


def resolve_celex(surface: str, corpus: Container[str], *,
                  source_celex: str | None = None) -> tuple[str | None, str | None]:
    """(celex, None) when the surface names an act in ``corpus``; else (None, reason).

    ``corpus`` is any container of CELEX ids (a set, or a dict keyed by CELEX).
    Reasons: ``truncated_surface``, ``designator_unsupported``, ``no_identifier``,
    ``malformed_surface``, ``compound_surface`` (several acts named, only the
    first identified), ``doc_type_not_in_corpus``, ``self_reference``,
    ``out_of_corpus``.
    """
    ref = parse_act_designation(surface)
    if ref is None:
        return None, unresolvable_reason(surface)
    if ref.plural:
        return None, "compound_surface"
    if ref.letter not in CORPUS_LETTERS:
        return None, "doc_type_not_in_corpus"
    if source_celex is not None and ref.celex == source_celex:
        return None, "self_reference"
    if ref.celex not in corpus:
        return None, "out_of_corpus"
    return ref.celex, None


__all__ = ["ActRef", "parse_act_designation", "resolve_celex",
           "unresolvable_reason", "is_bare_designator", "LETTER", "CORPUS_LETTERS"]
