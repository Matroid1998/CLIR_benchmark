"""
The chemistry-patents domain: one wiring point.

Everything the core needs is assembled here from the modules alongside. Reading
this file should be enough to understand what the domain is; the details live in
``vocabulary.py`` (what chemistry means), ``schema.py`` (what a document is),
``attribution.py`` (whose data it is), ``sources/`` (where it comes from) and
``qac/`` (how questions are made).
"""

from __future__ import annotations

from clir_bench.core.domain import (
    AnalysisVocab,
    DomainSpec,
    LanguageSpec,
    SourceSpec,
)
from clir_bench.domains.chem_patents import vocabulary as vocab
from clir_bench.domains.chem_patents.attribution import ATTRIBUTIONS
from clir_bench.domains.chem_patents.qac.plans import PLANS
from clir_bench.domains.chem_patents.schema import SCHEMA

LANGUAGES = LanguageSpec(
    inventory=vocab.EXTRACTION_LANGUAGES,
    working=vocab.WORKING_LANGUAGES,
    names=vocab.LANGUAGE_NAMES,
    priority=vocab.LANGUAGE_PRIORITY,
    answer_order=vocab.ANSWER_LANGUAGE_ORDER,
)

SOURCES = (
    SourceSpec(
        name="gp",
        description="Google Patents Public Data (BigQuery)",
        languages=vocab.WORKING_LANGUAGES,
        corpus_relpath="google_patents/multilingual_corpus.csv",
        qac_dir_relpath="google_patents/qac",
        attribution_key="google_patents",
        source_value="google_patents",
    ),
    SourceSpec(
        name="epo",
        description="EPO bulk full-text data (BDDS product 32)",
        languages=vocab.EPO_LANGUAGES,
        corpus_relpath="EPO/multilingual_corpus.csv",
        qac_dir_relpath="EPO/qac",
        attribution_key="epo",
        source_value="epo",
    ),
)

ANALYSIS = AnalysisVocab(
    modes=vocab.MODES,
    strategies=vocab.STRATEGY_ORDER,
    strategy_numbers=vocab.STRATEGY_NUMBERS,
    diagnostic_languages=vocab.DIAGNOSTIC_LANGUAGES,
)

# Logical name -> path under the data root. These reproduce the existing on-disk
# layout exactly, so the current data/ tree works without being moved.
DATA_LAYOUT = {
    "gp_raw": "google_patents/chemistry_patents.ndjson",
    "gp_preprocessed": "google_patents/preprocessed",
    "gp_corpus": "google_patents/multilingual_corpus.csv",
    "gp_qac": "google_patents/qac",
    "epo_manifest": "EPO/manifest.json",
    "epo_corpus": "EPO/multilingual_corpus.csv",
    "epo_qac": "EPO/qac",
    "chebi": "chebi",
    "alias_graph": "alias_graph",
    "code_switched": "code_switched",
    "progressive": "progressive_cs",
    "human_eval": "human_eval",
    "baselines": "baselines",
}

# Defaults a user can override in clir.toml under [domains.chem_patents].
DEFAULTS = {
    "corpus_repo": "MehdiAstaraki/multilingual_GP",
    "benchmark_repo": "MehdiAstaraki/multi-lingual-qac-chem-patents",
    "gp_benchmark_repo": "MehdiAstaraki/multi-lingual-qac-chem-patents",
    "epo_benchmark_repo": "MehdiAstaraki/multi-lingual-qac-epo",
    "alias_graph_repo": "MehdiAstaraki/multi-lingual-qac-alias-graph",
    "progressive_repo": "MehdiAstaraki/progressive-code-switch",
    "chebi_variant": "full",
    # Read by the evaluation harness when it builds the MTEB task: the language
    # tags it validates eval_langs against, and the subject tags of the task
    # itself. Supplied as domain data so the harness never names a subject.
    "mteb_language_codes": vocab.MTEB_LANGUAGE_CODES,
    "mteb_task_domains": ("Chemistry", "Engineering"),
    # Column names in this domain's already-published datasets. The analysis
    # layer is ontology-agnostic and asks for candidates rather than assuming
    # ChEBI, so the historical names are declared here instead.
    "concept_columns": ("concept_id", "chebi_id"),
    "negative_name_columns": ("neighbor_name", "neighbor_concept_id", "neighbor_chebi_id"),
    "eval_models": (
        "Qwen/Qwen3-Embedding-0.6B",
        "intfloat/multilingual-e5-large-instruct",
        "BAAI/bge-m3",
        "jinaai/jina-embeddings-v3",
        "google/embeddinggemma-300m",
        "ibm-granite/granite-embedding-278m-multilingual",
        "jinaai/jina-colbert-v2",
        "cambridgeltl/SapBERT-UMLS-2020AB-all-lang-from-XLMR",
        "sentence-transformers/LaBSE",
        "nomic-ai/nomic-embed-text-v2-moe",
    ),
}


SPEC = DomainSpec(
    name="chem_patents",
    title="Chemistry patents",
    description=(
        "Multilingual chemistry-patent retrieval built from Google Patents "
        "Public Data and EPO bulk full-text data. Documents exist in several "
        "languages as human translations of one another, which is what makes "
        "cross-language retrieval measurable rather than simulated."
    ),
    schema=SCHEMA,
    languages=LANGUAGES,
    sources=SOURCES,
    prompts_package="clir_bench.domains.chem_patents.qac.prompts",
    attributions=ATTRIBUTIONS,
    analysis=ANALYSIS,
    data_layout=DATA_LAYOUT,
    defaults=DEFAULTS,
    qac_plans=PLANS,
)


__all__ = ["SPEC"]
