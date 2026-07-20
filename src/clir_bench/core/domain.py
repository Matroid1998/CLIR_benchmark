"""
The domain contract.

A *domain* is a body of documents plus the vocabulary and conventions that go
with it: chemistry patents today, legal texts tomorrow. Everything a domain
knows is declared as data in a single ``DomainSpec`` instance; the core reads
that data and never names a domain itself.

The contract is deliberately small. A domain is:

  1. ``SPEC: DomainSpec``   -- pure data (required)
  2. ``register_cli(...)``  -- one wiring hook for domain-only commands (optional)

There are no base classes to subclass and no plugin registry to edit. Adding
``domains/legal/`` is a folder creation plus a ``[domains.legal]`` section in
clir.toml; no file under ``core/`` or ``cli/`` changes.

Import direction (checked by tests/test_import_direction.py):

    domains  ->  core        allowed
    core     ->  domains     NEVER
    cli      ->  domains     only via domains.load()

Core stages therefore touch documents exclusively through ``DomainSpec.schema``
and the other value objects below.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence


# --------------------------------------------------------------------------- #
# Corpus schema -- how core code reads a document row without knowing the domain
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class CorpusSchema:
    """Column contract for one domain's corpus CSV.

    The critical field is ``family_field``: the column that groups the
    cross-language versions of the same underlying document. For patents that
    is ``publication_number``; a legal domain would use a CELEX id. Every piece
    of core logic that needs "the other language versions of this document" --
    qrels construction, multilingual coverage filtering, cross-lingual metrics,
    haystack removal -- goes through ``family_of()`` rather than naming a column.

    ``fields`` is the writer's column order, so the on-disk CSV layout is
    reproduced exactly and existing data files stay readable unmodified.
    """

    fields: tuple[str, ...]
    family_field: str
    id_field: str = "id"
    language_field: str = "language"
    # Fallback chain used to turn a row into indexable/generatable text.
    text_fields: tuple[str, ...] = ("context", "abstract", "title")
    # Separator between family id and language in a document id ("EP-123-A1_en").
    id_language_separator: str = "_"
    # Separator used when minting query ids from a document id.
    query_id_infix: str = "_q_"
    # Optional canonical key for cross-source deduplication. Patent numbers need
    # normalizing (country code + bare number) before two sources can be
    # compared; a domain without that problem leaves this unset and dedup falls
    # back to the family key.
    dedup_key_fn: Optional[Callable[[Mapping[str, Any]], str]] = None

    # -- row accessors ------------------------------------------------------ #

    def family_of(self, row: Mapping[str, Any]) -> str:
        """The cross-language grouping key of a row (e.g. the patent family)."""
        return str(row.get(self.family_field, "") or "").strip()

    def id_of(self, row: Mapping[str, Any]) -> str:
        return str(row.get(self.id_field, "") or "").strip()

    def language_of(self, row: Mapping[str, Any]) -> str:
        return str(row.get(self.language_field, "") or "").strip().lower()

    def text_of(self, row: Mapping[str, Any]) -> str:
        """First non-empty field of the text fallback chain.

        Note the `or` chaining: a present-but-empty ``context`` correctly falls
        through to ``abstract``. (The legacy Option-A pipeline used dict-default
        chaining here and silently skipped non-empty abstracts.)
        """
        for name in self.text_fields:
            value = str(row.get(name, "") or "").strip()
            if value:
                return value
        return ""

    # -- id conventions ----------------------------------------------------- #

    def make_doc_id(self, family: str, language: str) -> str:
        return f"{family}{self.id_language_separator}{language}"

    def language_from_doc_id(self, doc_id: str) -> str:
        """Infer the language from a document id, or "" if it does not encode one.

        Used when a shared retrieval haystack contains documents that are not in
        the benchmark's own corpus config and so carry no language column.
        """
        head, sep, tail = str(doc_id).rpartition(self.id_language_separator)
        if not sep or not tail:
            return ""
        tail = tail.strip().lower()
        return tail if tail.isalpha() and 2 <= len(tail) <= 3 else ""

    def family_from_doc_id(self, doc_id: str) -> str:
        head, sep, tail = str(doc_id).rpartition(self.id_language_separator)
        return head if (sep and self.language_from_doc_id(doc_id)) else str(doc_id)

    def make_query_id(self, doc_id: str, language: str) -> str:
        return f"{doc_id}{self.query_id_infix}{language}"

    def dedup_key(self, row: Mapping[str, Any]) -> str:
        """Canonical identity of a document across sources."""
        if self.dedup_key_fn is not None:
            return self.dedup_key_fn(row)
        return self.family_of(row)


# --------------------------------------------------------------------------- #
# Languages -- membership is single-sourced, orderings stay named and distinct
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class LanguageSpec:
    """Language inventories for a domain.

    ``working`` is the set of languages the benchmark actually generates
    questions in. ``inventory`` is the wider set the source can yield.

    Orderings matter: several algorithms pick "the first available language" by
    a priority list, so orderings are preserved as separately named tuples
    rather than collapsed into one canonical order.
    """

    inventory: tuple[str, ...]
    working: tuple[str, ...]
    names: Mapping[str, str]
    priority: tuple[str, ...] = ()
    answer_order: tuple[str, ...] = ()

    def name_of(self, code: str) -> str:
        return self.names.get(code, code)

    def __post_init__(self) -> None:
        missing = [c for c in self.working if c not in self.names]
        if missing:
            raise ValueError(f"languages missing from name map: {missing}")


# --------------------------------------------------------------------------- #
# Sources -- where documents come from
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class SourceSpec:
    """One document source within a domain (e.g. Google Patents, EPO bulk data).

    Pure data. The ingest *function* is not stored here: sources have genuinely
    different options (BigQuery limits vs. bulk-archive batches), so each domain
    wires its own ingest subcommands in ``register_cli``.

    ``attribution_key`` selects the licensing block used when publishing data
    derived from this source, so an attribution can never be attached to the
    wrong provider's data.
    """

    name: str
    languages: tuple[str, ...]
    corpus_relpath: str
    qac_dir_relpath: str
    attribution_key: str
    description: str = ""
    # Value written into the corpus ``source`` column by this source's loader.
    source_value: str = ""

    def __post_init__(self) -> None:
        if not self.source_value:
            object.__setattr__(self, "source_value", self.name)


# --------------------------------------------------------------------------- #
# Analysis vocabulary -- keeps project-specific labels out of the analysis code
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class AnalysisVocab:
    """Labels and orderings the analysis layer reports by.

    Every breakdown degrades gracefully when its column is absent, so a domain
    that has no notion of "modes" simply leaves these empty.
    """

    modes: tuple[str, ...] = ()
    strategies: tuple[str, ...] = ()
    strategy_numbers: Mapping[int, str] = field(default_factory=dict)
    # Languages shown in the same-language-bias diagnostic.
    diagnostic_languages: tuple[str, ...] = ()


# --------------------------------------------------------------------------- #
# The domain itself
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class DomainSpec:
    """Everything the core needs to know about a domain. Pure data.

    A domain package exposes exactly one instance of this as ``SPEC``.
    """

    name: str
    title: str
    description: str

    schema: CorpusSchema
    languages: LanguageSpec
    sources: tuple[SourceSpec, ...]

    # Import anchor for prompt files, e.g. "clir_bench.domains.chem_patents.qac.prompts".
    prompts_package: str

    # source ``attribution_key`` -> licensing/attribution markdown for dataset cards.
    attributions: Mapping[str, str] = field(default_factory=dict)

    analysis: AnalysisVocab = field(default_factory=AnalysisVocab)

    # Named question-generation plans, e.g. {"balanced": build_balanced_plan}.
    # A plan decides which documents get asked about, in which languages and
    # modes -- the part that differs per dataset build rather than per domain.
    # Each callable takes (context, options) and returns a list of PlanItem.
    qac_plans: Mapping[str, Callable[..., Any]] = field(default_factory=dict)

    # Logical key -> path relative to the data root. Reproduces the legacy
    # on-disk names so existing data files keep working unmoved.
    data_layout: Mapping[str, str] = field(default_factory=dict)

    # Default HF repo ids, model ids and knobs; overridable per user under
    # [domains.<name>] in clir.toml.
    defaults: Mapping[str, Any] = field(default_factory=dict)

    def source(self, name: str) -> SourceSpec:
        for spec in self.sources:
            if spec.name == name:
                return spec
        available = ", ".join(s.name for s in self.sources)
        raise KeyError(f"unknown source {name!r} for domain {self.name!r}; available: {available}")

    @property
    def source_names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.sources)

    def attribution_for(self, source_name: str) -> str:
        """Attribution text for a source. Raises rather than silently omitting.

        Publishing data under the wrong licence statement is worse than failing
        the publish, so an unknown source is an error, not an empty string.
        """
        spec = self.source(source_name)
        try:
            return self.attributions[spec.attribution_key]
        except KeyError as exc:
            raise KeyError(
                f"domain {self.name!r} declares no attribution "
                f"{spec.attribution_key!r} for source {source_name!r}"
            ) from exc


# Signature of the optional CLI hook a domain may expose.
RegisterCli = Callable[..., None]


__all__ = [
    "AnalysisVocab",
    "CorpusSchema",
    "DomainSpec",
    "LanguageSpec",
    "RegisterCli",
    "SourceSpec",
]
