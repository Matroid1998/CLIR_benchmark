"""
Text normalization helpers.

Two ``clean_text`` variants existed under the same name in two loaders, so the
two corpora were cleaned differently. That divergence is real and already baked
into published data, so both survive here under distinct names and a source
chooses one explicitly rather than inheriting whichever module it imported.
"""

from __future__ import annotations

import html
import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+([,;:.)\]])")
_SPACE_AFTER_OPEN_RE = re.compile(r"([(\[])\s+")


def clean_text_simple(value: str) -> str:
    """HTML-unescape and collapse whitespace. Used by the Google Patents loader."""
    if not value:
        return ""
    return _WHITESPACE_RE.sub(" ", html.unescape(value)).strip()


def clean_text_nfkc(value: str) -> str:
    """Aggressive clean used by the EPO XML parser.

    Adds NFKC normalization, control-character stripping and punctuation-spacing
    repair on top of :func:`clean_text_simple` -- XML full text needs it in a way
    BigQuery's already-normalized fields do not.
    """
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", html.unescape(value))
    text = _CONTROL_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    text = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", text)
    text = _SPACE_AFTER_OPEN_RE.sub(r"\1", text)
    return text.strip()


def word_count(text: str) -> int:
    return len((text or "").split())


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate on a word boundary when one is reasonably close to the limit."""
    value = (text or "").strip()
    if len(value) <= max_chars:
        return value
    cut = value[:max_chars]
    space = cut.rfind(" ")
    if space > max_chars * 0.8:
        cut = cut[:space]
    return cut.rstrip() + "..."


__all__ = [
    "clean_text_nfkc",
    "clean_text_simple",
    "truncate_text",
    "word_count",
]
