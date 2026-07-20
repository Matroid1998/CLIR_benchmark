"""
Domain-independent machinery.

Nothing in this package may import from ``clir_bench.domains``: the core is what
every domain shares, so it cannot know about any particular one. Domain
knowledge reaches core code only as values on a :class:`~clir_bench.core.domain.DomainSpec`.
"""

from clir_bench.core.domain import (
    AnalysisVocab,
    CorpusSchema,
    DomainSpec,
    LanguageSpec,
    SourceSpec,
)

__all__ = [
    "AnalysisVocab",
    "CorpusSchema",
    "DomainSpec",
    "LanguageSpec",
    "SourceSpec",
]
