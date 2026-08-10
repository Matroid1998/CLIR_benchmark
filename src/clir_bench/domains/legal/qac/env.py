"""
Load ``.env`` for the EUR-Lex modules run as ``python -m ...``.

``clir_bench.cli`` loads the project ``.env`` for the ``clir`` console script,
but these stages are invoked directly as modules and never go through it. Without
this, every API call raises "OPENAI_API_KEY is not set", the per-target guard
catches each one, and a 100-article build writes a header row and exits 0 --
which is the worst way to fail.
"""

from __future__ import annotations

from clir_bench.domains.legal.structure.paths import ROOT


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover
        return
    load_dotenv(ROOT / ".env")


__all__ = ["load_env"]
