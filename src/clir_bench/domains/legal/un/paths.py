"""Where the UN stages read and write.

Mirrors ``structure/paths.py``: the legal domain still has no ``DomainSpec``,
so these constants stand in for the ``data_layout`` entry a spec would declare.
Wiring them into the spec later is a rename, not a move.
"""

from __future__ import annotations

from pathlib import Path

from clir_bench.domains.legal.structure.paths import ROOT

UN_DIR = ROOT / "data/legal/un_parallel"
SIXWAY_DIR = UN_DIR / "6way"

IDS_FILE = SIXWAY_DIR / "UNv1.0.6way.ids"


def text_file(language: str) -> Path:
    """The line-aligned corpus file for one language."""
    return SIXWAY_DIR / f"UNv1.0.6way.{language}"


BLOCKS_DIR = UN_DIR / "blocks"
BLOCKS_JSONL = BLOCKS_DIR / "blocks_en.jsonl"    # one row per block, with text
DOCS_JSONL = BLOCKS_DIR / "docs_en.jsonl"        # one row per document + offset

QAC_DIR = UN_DIR / "qac"


def ensure_dirs() -> None:
    for path in (BLOCKS_DIR, QAC_DIR):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "UN_DIR", "SIXWAY_DIR", "IDS_FILE", "text_file",
    "BLOCKS_DIR", "BLOCKS_JSONL", "DOCS_JSONL", "QAC_DIR", "ensure_dirs",
]
