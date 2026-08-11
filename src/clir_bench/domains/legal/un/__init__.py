"""
UN Parallel Corpus source for the legal domain.

The corpus (``data/legal/un_parallel/6way/``) is six line-aligned files, one per
official UN language: line N is the same sentence group in every language. There
is no per-document markup -- document boundaries and paragraph structure are
recovered from the ``.ids`` sidecar, whose ``en:P:S`` tokens give each line's
paragraph and sentence position in the original English document.

Everything downstream builds on one property: a **block is a line range**, so a
segmentation computed once from the English text applies verbatim to all six
languages. English is built first; other languages are the same line ranges read
from their own file.
"""

from __future__ import annotations

UN_LANGUAGES: tuple[str, ...] = ("ar", "en", "es", "fr", "ru", "zh")

__all__ = ["UN_LANGUAGES"]
