"""
Parser for EPO ``<ep-patent-document>`` XML.

The EPO bulk archives carry the full patent as SGML-derived XML with the WIPO
ST.32 "B-tag" bibliography: ``B540`` holds titles, ``B300`` priorities, ``B710``
applicants, ``B840`` designated states. None of that is documented in the
delivery, so the XPaths below are the contract with the format and are the part
of this module most likely to break on a schema change.

Two things this module decides that the corpus never sees. First, whether a
document is chemistry at all: the archives carry no chemical annotation, so the
judgement is made here from classification codes plus title keywords rather than
in a query as it is for Google Patents. Second, whether a language version is
substantive enough to count -- see :func:`language_has_substantive_text`.

The record produced by :func:`parse_epo_patent_root` is wider than the 12-column
corpus row: applicants, inventors, representatives, priority numbers and dates,
filing date and designated states are all extracted and kept. They are dropped
at row-building time, not at parse time, so an analysis that wants them does not
have to re-parse the archives.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.text import clean_text_nfkc, truncate_text, word_count
from clir_bench.domains.chem_patents.schema import CONTEXT_LABELS, SCHEMA
from clir_bench.domains.chem_patents.vocabulary import (
    CHEMISTRY_LABELS,
    EPO_CHEMISTRY_KEYWORDS,
    EPO_CLASSIFICATION_PREFIXES,
    EPO_DESCRIPTION_MAX_CHARS,
    EPO_MIN_FIRST_CLAIM_WORDS,
    FIRST_CLAIM_MAX_CHARS,
    MIN_ABSTRACT_WORDS,
)

# An IPC/CPC code as it appears inside a <text> node, e.g. "C07D 401/12".
CLASSIFICATION_CODE_RE = re.compile(r"([A-HY]\d{2}[A-Z]?\s*\d+(?:/\d+)?)")

# Files an archive ships alongside each patent: a table of contents and the
# sequence listings (``__SL001.xml``). They parse as XML but are not documents,
# and skipping them by name is far cheaper than parsing and rejecting them.
AUXILIARY_XML_RE = re.compile(r"__(?:TOC|SL\d+)\.xml$", re.IGNORECASE)

_NOT_CHEMISTRY, _CHEMISTRY_RELATED, _CHEMISTRY_CORE = CHEMISTRY_LABELS


# --------------------------------------------------------------------------- #
# Field extraction
# --------------------------------------------------------------------------- #

def _normalize_code(raw_text: str) -> str:
    match = CLASSIFICATION_CODE_RE.search(clean_text_nfkc(raw_text))
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _normalized_prefix(value: str) -> str:
    return value.upper().replace(" ", "")


def _extract_title_localized(root: ET.Element) -> list[dict[str, str]]:
    """Titles from the B540 block.

    B541 (language) and B542 (text) are siblings rather than nested, so the
    language is carried forward from the preceding B541 instead of being read
    off the title element.
    """
    titles: list[dict[str, str]] = []
    title_block = root.find(".//B540")
    if title_block is None:
        return titles

    current_lang = ""
    for child in title_block:
        if child.tag == "B541":
            current_lang = clean_text_nfkc(child.text or "").lower()
        elif child.tag == "B542":
            text = clean_text_nfkc(child.text or "")
            if current_lang and text:
                titles.append({"language": current_lang, "text": text})
    return titles


def _extract_text_blocks(root: ET.Element, tag_name: str) -> list[dict[str, str]]:
    """Every ``<tag lang=...>`` block, flattened to text and deduplicated."""
    blocks: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for node in root.findall(f".//{tag_name}"):
        language = clean_text_nfkc(node.attrib.get("lang", "")).lower()
        text = clean_text_nfkc("".join(node.itertext()))
        if not text:
            continue
        key = (language, text)
        if key in seen:
            continue
        seen.add(key)
        blocks.append({"language": language, "text": text})
    return blocks


def _extract_first_claim_text(root: ET.Element) -> list[dict[str, str]]:
    """The first claim per language.

    Claim 1 is the broadest one and the only claim the corpus keeps; later
    claims narrow it and add length without adding retrievable content.
    """
    claims_by_lang: dict[str, str] = {}
    for claims_node in root.findall(".//claims"):
        language = clean_text_nfkc(claims_node.attrib.get("lang", "")).lower()
        claim_node = claims_node.find(".//claim")
        if claim_node is None:
            continue
        text = clean_text_nfkc("".join(claim_node.itertext()))
        if text and language not in claims_by_lang:
            claims_by_lang[language] = truncate_text(text, FIRST_CLAIM_MAX_CHARS)
    return [{"language": lang, "text": text} for lang, text in claims_by_lang.items()]


def _extract_classification_codes(root: ET.Element, tag_name: str) -> list[str]:
    codes: list[str] = []
    seen: set[str] = set()
    for node in root.findall(f".//{tag_name}"):
        code = _normalize_code(node.findtext("text", default=""))
        if code and code not in seen:
            seen.add(code)
            codes.append(code)
    return codes


def _extract_party_names(root: ET.Element, xpath: str) -> list[str]:
    """Organisation or person names (``snm``) under an applicant/inventor block."""
    names: list[str] = []
    seen: set[str] = set()
    for node in root.findall(xpath):
        name = clean_text_nfkc(node.findtext("snm", default=""))
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _extract_designated_states(root: ET.Element) -> list[str]:
    states: list[str] = []
    seen: set[str] = set()
    for node in root.findall(".//B840/ctry"):
        state = clean_text_nfkc(node.text or "").upper()
        if state and state not in seen:
            seen.add(state)
            states.append(state)
    return states


def _extract_priority_numbers(root: ET.Element) -> list[str]:
    numbers: list[str] = []
    seen: set[str] = set()
    for node in root.findall(".//B300/B310"):
        number = clean_text_nfkc("".join(node.itertext()))
        if number and number not in seen:
            seen.add(number)
            numbers.append(number)
    return numbers


def _extract_priority_dates(root: ET.Element) -> list[str]:
    dates: list[str] = []
    seen: set[str] = set()
    for node in root.findall(".//B300/B320/date"):
        date_value = clean_text_nfkc(node.text or "")
        if date_value and date_value not in seen:
            seen.add(date_value)
            dates.append(date_value)
    return dates


def text_for_language(blocks: Sequence[Mapping[str, str]], language: str) -> str:
    """The text of the first block tagged with ``language``, or ""."""
    language = (language or "").lower()
    for block in blocks:
        if block.get("language") == language and block.get("text"):
            return block["text"]
    return ""


# --------------------------------------------------------------------------- #
# Chemistry scoring
# --------------------------------------------------------------------------- #

def _classification_matches(codes: Sequence[str]) -> list[str]:
    prefixes = [_normalized_prefix(prefix) for prefix in EPO_CLASSIFICATION_PREFIXES]
    return [
        code for code in codes
        if any(_normalized_prefix(code).startswith(prefix) for prefix in prefixes)
    ]


def _keyword_hits(texts: Sequence[str]) -> list[str]:
    haystack = " ".join(clean_text_nfkc(text).lower() for text in texts if text)
    return [keyword for keyword in EPO_CHEMISTRY_KEYWORDS if keyword in haystack]


def analyze_epo_chemistry(record: Mapping[str, Any]) -> dict[str, Any]:
    """Score whether a parsed EPO record is chemistry.

    Classification codes are the trustworthy signal and alone earn
    ``chemistry_core``; title keywords only earn ``chemistry_related``, because
    they are matched as substrings against English titles and so both over-match
    (``acid`` inside a longer word) and under-match documents titled in French or
    German. The ingest's ``--strict`` mode is exactly "discard everything that
    rests on keywords".
    """
    ipc_matches = _classification_matches(record.get("ipc_codes", []))
    cpc_matches = _classification_matches(record.get("cpc_codes", []))
    keyword_hits = _keyword_hits([title["text"] for title in record.get("title_localized", [])])

    score = 0
    reasons: list[str] = []
    if ipc_matches:
        score += 2
        reasons.append(f"IPC match: {', '.join(ipc_matches[:5])}")
    if cpc_matches:
        score += 2
        reasons.append(f"CPC match: {', '.join(cpc_matches[:5])}")
    if keyword_hits:
        score += 1
        reasons.append(f"Title keywords: {', '.join(keyword_hits[:8])}")

    if ipc_matches or cpc_matches:
        label = _CHEMISTRY_CORE
    elif keyword_hits:
        label = _CHEMISTRY_RELATED
    else:
        label = _NOT_CHEMISTRY

    return {"score": score, "label": label, "keep": label != _NOT_CHEMISTRY, "reasons": reasons}


def chemistry_rank(label: str) -> int:
    """Strength of a chemistry label, for keeping the strongest across versions."""
    try:
        return CHEMISTRY_LABELS.index(label)
    except ValueError:
        return 0


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def parse_epo_patent_root(root: ET.Element, *, xml_name: str = "") -> dict[str, Any]:
    """Normalize an ``<ep-patent-document>`` root into a record dict.

    Raises ``ValueError`` for anything that is not a usable patent document --
    a different root tag, or missing identifiers or titles. The caller counts
    those separately from ``ET.ParseError`` because a bulk archive legitimately
    contains non-patent XML, while a parse error means damaged input.
    """
    if root.tag != "ep-patent-document":
        raise ValueError(f"Unsupported EPO XML root tag: {root.tag}")

    title_localized = _extract_title_localized(root)
    english_title = next((item["text"] for item in title_localized if item["language"] == "en"), "")
    primary_title = english_title or (title_localized[0]["text"] if title_localized else "")

    record: dict[str, Any] = {
        "xml_file": xml_name,
        "document_id": clean_text_nfkc(root.attrib.get("id", "")),
        "publication_number": clean_text_nfkc(root.attrib.get("doc-number", "")),
        "application_number": clean_text_nfkc(root.findtext(".//B200/B210", default="")),
        "country_code": clean_text_nfkc(root.attrib.get("country", ""))
            or clean_text_nfkc(root.findtext(".//B100/B190", default="")),
        "publication_date": clean_text_nfkc(root.attrib.get("date-publ", ""))
            or clean_text_nfkc(root.findtext(".//B140/date", default="")),
        "filing_date": clean_text_nfkc(root.findtext(".//B220/date", default="")),
        "priority_dates": _extract_priority_dates(root),
        "priority_numbers": _extract_priority_numbers(root),
        "kind": clean_text_nfkc(root.attrib.get("kind", "")),
        "source_language": clean_text_nfkc(root.attrib.get("lang", "")).lower(),
        "title": primary_title,
        "title_localized": title_localized,
        "abstract_localized": _extract_text_blocks(root, "abstract"),
        "description_localized": _extract_text_blocks(root, "description"),
        "first_claim_localized": _extract_first_claim_text(root),
        "ipc_codes": _extract_classification_codes(root, "classification-ipcr"),
        "cpc_codes": _extract_classification_codes(root, "classification-cpc"),
        "applicants": _extract_party_names(root, ".//B710/B711"),
        "inventors": _extract_party_names(root, ".//B720/B721"),
        "representatives": _extract_party_names(root, ".//B740/B741"),
        "designated_states": _extract_designated_states(root),
    }

    if not record["document_id"] or not record["publication_number"]:
        raise ValueError(f"Missing essential patent identifiers in {xml_name or '<stream>'}")
    if not record["title_localized"] and not record["title"]:
        raise ValueError(f"Missing title data in {xml_name or '<stream>'}")

    record["chemistry"] = analyze_epo_chemistry(record)
    return record


def parse_epo_patent_bytes(xml_bytes: bytes, *, xml_name: str = "") -> dict[str, Any]:
    """Parse XML bytes straight from an archive stream, without touching disk."""
    return parse_epo_patent_root(ET.fromstring(xml_bytes), xml_name=xml_name)


def parse_epo_patent_xml(xml_path: Path) -> dict[str, Any]:
    """Parse a local XML file. Used for inspecting a single extracted document."""
    xml_path = Path(xml_path)
    return parse_epo_patent_root(ET.parse(xml_path).getroot(), xml_name=xml_path.name)


# --------------------------------------------------------------------------- #
# Row building
# --------------------------------------------------------------------------- #

def language_has_substantive_text(
    record: Mapping[str, Any],
    language: str,
    *,
    min_abstract_words: int = MIN_ABSTRACT_WORDS,
    min_claim_words: int = EPO_MIN_FIRST_CLAIM_WORDS,
) -> bool:
    """True when the record carries a real abstract or first claim in ``language``.

    A title is not enough. The EPO publishes titles in all three official
    languages for almost every document, so counting them would make the
    ">= 2 languages" requirement trivially satisfied and fill the corpus with
    documents that are not actually translated. This gate is stricter than the
    Google Patents one for the same reason: the two sources are unequal in what
    "has this language" means, and the EPO side has to earn it.
    """
    abstract = text_for_language(record.get("abstract_localized", []), language)
    if word_count(abstract) >= min_abstract_words:
        return True
    first_claim = text_for_language(record.get("first_claim_localized", []), language)
    return word_count(first_claim) >= min_claim_words


def build_row_for_language(
    record: Mapping[str, Any],
    language: str,
    *,
    source: str = "epo",
) -> Optional[dict[str, str]]:
    """One corpus row for one language of a record, or None if that slot is empty.

    Only the 12 schema columns survive; the bibliographic fields the parser also
    extracted stay on the record for callers that want them.
    """
    language = (language or "").lower()
    title = text_for_language(record.get("title_localized", []), language)
    abstract = text_for_language(record.get("abstract_localized", []), language)
    first_claim = text_for_language(record.get("first_claim_localized", []), language)
    description = text_for_language(record.get("description_localized", []), language)

    if not abstract and not first_claim:
        return None

    if description:
        description = truncate_text(description, EPO_DESCRIPTION_MAX_CHARS)

    family = record["publication_number"]
    fields = {
        "title": title,
        "abstract": abstract,
        "first_claim": first_claim,
    }
    return {
        "id": SCHEMA.make_doc_id(family, language),
        "language": language,
        "title": title,
        "abstract": abstract,
        "description": description,
        "first_claim": first_claim,
        "context": corpus_io.build_context(fields, CONTEXT_LABELS),
        "publication_number": family,
        "country_code": record.get("country_code", ""),
        "publication_date": record.get("publication_date", ""),
        "source": source,
        "ipc_codes": "|".join(record.get("ipc_codes", [])),
    }


__all__ = [
    "AUXILIARY_XML_RE",
    "CLASSIFICATION_CODE_RE",
    "analyze_epo_chemistry",
    "build_row_for_language",
    "chemistry_rank",
    "language_has_substantive_text",
    "parse_epo_patent_bytes",
    "parse_epo_patent_root",
    "parse_epo_patent_xml",
    "text_for_language",
]
