"""
Question generation engine.

The shape of the pipeline is fixed and domain-independent: for a document and a
target language, generate N candidate questions, grade them all in batched
calls, rank by total score, keep the best. What changes per domain is the
prompts; what changes per dataset is the plan (which documents, which languages,
which mode).

Design properties preserved from the original pipeline, each load-bearing:

* generators *and* graders see every language version of a document, so grading
  is grounded cross-lingually rather than against one translation;
* candidates are generated in one call and graded in one call per rubric, then
  ranked -- not generated-and-graded one at a time;
* language selection is strategy-driven, which is what makes the benchmark
  contain both same-language and cross-language queries by construction.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.domain import CorpusSchema
from clir_bench.core.grading import (
    GraderConfig,
    MODE_TECHNICAL,
    grade_columns,
    grade_faithfulness,
    grade_quality,
    rank_candidates,
)
from clir_bench.core.llm import call_with_retries, chat, parse_json_response
from clir_bench.core.prompts import PromptPack

CANDIDATES_PER_DOCUMENT = 3

# Query-language selection strategies. The numbering is published in dataset
# metadata, so the values are fixed.
STRATEGY_RANDOM_ANY = 1
STRATEGY_RANDOM_MISSING = 2
STRATEGY_RANDOM_EXISTING = 3
STRATEGY_ALL = 4

STRATEGY_NAMES = {
    STRATEGY_RANDOM_ANY: "random_any",
    STRATEGY_RANDOM_MISSING: "random_missing",
    STRATEGY_RANDOM_EXISTING: "random_existing",
    STRATEGY_ALL: "all",
}


def pick_target_languages(
    strategy: int,
    available: Sequence[str],
    languages: Sequence[str],
    *,
    rng: Optional[random.Random] = None,
) -> list[str]:
    """Choose the language(s) to ask in, given what the document exists in.

    ``random_missing`` is what produces genuinely cross-lingual queries: it asks
    in a language the document is *not* available in, so a retriever cannot
    succeed by lexical overlap with the query's own language.
    """
    chooser = rng or random
    universe = list(languages)
    if not universe:
        raise ValueError("no candidate languages configured for this domain")
    present = set(available) & set(universe)
    missing = [lang for lang in universe if lang not in present]

    if strategy == STRATEGY_RANDOM_ANY:
        return [chooser.choice(universe)]
    if strategy == STRATEGY_RANDOM_MISSING:
        return [chooser.choice(missing or universe)]
    if strategy == STRATEGY_RANDOM_EXISTING:
        existing = [lang for lang in universe if lang in present]
        return [chooser.choice(existing or universe)]
    if strategy == STRATEGY_ALL:
        return list(universe)
    raise ValueError(f"unknown strategy: {strategy}")


@dataclass(frozen=True)
class GenerationConfig:
    """Models and knobs for one generation run."""

    generation_model: str
    grader: GraderConfig
    generation_reasoning_effort: str = "medium"
    candidates: int = CANDIDATES_PER_DOCUMENT
    retries: int = 3


@dataclass(frozen=True)
class PlanItem:
    """One unit of work: ask about this document, in this language, this way."""

    family: str
    language: str
    mode: str = MODE_TECHNICAL
    strategy: int = STRATEGY_RANDOM_ANY
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def strategy_name(self) -> str:
        return str(self.metadata.get("strategy_name") or STRATEGY_NAMES.get(self.strategy, ""))


def generate_candidates(
    client: Any,
    config: GenerationConfig,
    prompt: str,
    passages: str,
    mode: str,
) -> list[dict[str, str]]:
    """Generate candidate Q/A pairs in one call.

    ``question_type`` (technical) and ``framing`` (semantic) are per-mode
    classification fields the prompts emit and the analysis layer reports by.
    """
    raw = chat(
        client,
        config.generation_model,
        [{"role": "system", "content": prompt}, {"role": "user", "content": passages}],
        reasoning_effort=config.generation_reasoning_effort,
    )
    data = parse_json_response(raw)
    if isinstance(data, dict):
        data = [data]

    out: list[dict[str, str]] = []
    for item in list(data)[: config.candidates]:
        if not isinstance(item, Mapping):
            continue
        row = {
            "question": str(item.get("question", "")).strip(),
            "answer": str(item.get("answer", "")).strip(),
        }
        if mode == MODE_TECHNICAL:
            row["question_type"] = str(item.get("question_type", "other")).strip()
        else:
            row["framing"] = str(item.get("framing", "other")).strip()
        out.append(row)
    return out


def generate_for_document(
    item: PlanItem,
    rows: Sequence[Mapping[str, str]],
    *,
    schema: CorpusSchema,
    prompts: PromptPack,
    config: GenerationConfig,
    generation_client: Any,
    grading_client: Any,
    language_order: Sequence[str] = (),
) -> list[dict[str, Any]]:
    """Generate, grade and rank candidates for one plan item.

    Returns rows sorted best-first. Callers keep the top row per
    (family, language) for the published set and may keep the rest for audit.
    """
    passages = corpus_io.build_passages_text(rows, schema, order=language_order)
    if not passages:
        return []

    qa_pairs = call_with_retries(
        lambda: generate_candidates(
            generation_client,
            config,
            prompts.generation(item.mode, item.language),
            passages,
            item.mode,
        ),
        retries=config.retries,
        label=f"generate {item.family}/{item.language}",
    )
    qa_pairs = [qa for qa in qa_pairs if qa.get("question") and qa.get("answer")]
    if not qa_pairs:
        return []

    faith = call_with_retries(
        lambda: grade_faithfulness(
            grading_client, config.grader, prompts.faithfulness("batch"), passages, qa_pairs
        ),
        retries=config.retries,
        label=f"grade faithfulness {item.family}/{item.language}",
    )
    quality = call_with_retries(
        lambda: grade_quality(
            grading_client,
            config.grader,
            prompts.quality(item.mode, "batch"),
            passages,
            qa_pairs,
            item.mode,
        ),
        retries=config.retries,
        label=f"grade quality {item.family}/{item.language}",
    )

    context_row = corpus_io.pick_context_row(rows, schema, item.language) or rows[0]
    ranked = rank_candidates(qa_pairs, faith, quality, item.mode)

    out: list[dict[str, Any]] = []
    for rank, candidate in enumerate(ranked, start=1):
        row: dict[str, Any] = {
            schema.family_field: item.family,
            "corpus_id": schema.id_of(context_row),
            "question_language": item.language,
            "context_language": schema.language_of(context_row),
            "context_languages": corpus_io.serialize_languages(rows, schema, order=language_order),
            "mode": item.mode,
            "strategy": item.strategy,
            "strategy_name": item.strategy_name,
            "candidate_rank": rank,
            "question": candidate.qa.get("question", ""),
            "answer": candidate.qa.get("answer", ""),
            "question_type": candidate.qa.get("question_type", ""),
            "framing": candidate.qa.get("framing", ""),
        }
        row.update(grade_columns(candidate.faith, candidate.quality, item.mode))
        row.update(item.metadata)
        out.append(row)
    return out


def output_fieldnames(schema: CorpusSchema) -> tuple[str, ...]:
    """The QAC CSV schema, covering both modes' score columns.

    One writer schema for every generation flow: a mode-specific schema would
    make the technical and semantic outputs unmergeable.
    """
    from clir_bench.core.grading import (
        FAITHFULNESS_FIELDS,
        SEMANTIC_QUALITY_FIELDS,
        TECHNICAL_QUALITY_FIELDS,
    )

    identity = (
        schema.family_field,
        "corpus_id",
        "question_language",
        "context_language",
        "context_languages",
        "mode",
        "strategy",
        "strategy_name",
        "candidate_rank",
        "question",
        "answer",
        "question_type",
        "framing",
    )
    scores = tuple(
        dict.fromkeys(FAITHFULNESS_FIELDS + TECHNICAL_QUALITY_FIELDS + SEMANTIC_QUALITY_FIELDS)
    )
    trailing = ("faith_reason", "qual_failure_type", "qual_reason", "total_score")
    return identity + scores + trailing


def normalize_row(row: Mapping[str, Any], fieldnames: Sequence[str]) -> dict[str, Any]:
    """Pad a row to the full schema so mixed-mode rows share one header."""
    return {name: row.get(name, "") for name in fieldnames}


def select_best(
    rows: Sequence[Mapping[str, Any]], schema: CorpusSchema
) -> list[dict[str, Any]]:
    """Highest-scoring row per (family, question language).

    Sorts explicitly by score rather than relying on upstream ordering, which
    the old implementation did implicitly.
    """
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get(schema.family_field, "")), str(row.get("question_language", "")))
        current = best.get(key)
        if current is None or _score(row) > _score(current):
            best[key] = dict(row)
    return list(best.values())


def _score(row: Mapping[str, Any]) -> float:
    try:
        return float(row.get("total_score") or 0)
    except (TypeError, ValueError):
        return 0.0


def allocate_quotas(total: int, strategies: Sequence[int]) -> dict[int, int]:
    """Split a question budget evenly across strategies.

    ``STRATEGY_ALL`` yields one question per language rather than one per
    document, so its share is handled by the caller when sizing a plan.
    """
    if total <= 0:
        raise ValueError("total questions must be positive")
    if not strategies:
        raise ValueError("no strategies to allocate across")
    base, remainder = divmod(total, len(strategies))
    quotas = {strategy: base for strategy in strategies}
    for strategy in list(strategies)[:remainder]:
        quotas[strategy] += 1
    return quotas


__all__ = [
    "CANDIDATES_PER_DOCUMENT",
    "GenerationConfig",
    "PlanItem",
    "STRATEGY_ALL",
    "STRATEGY_NAMES",
    "STRATEGY_RANDOM_ANY",
    "STRATEGY_RANDOM_EXISTING",
    "STRATEGY_RANDOM_MISSING",
    "allocate_quotas",
    "generate_candidates",
    "generate_for_document",
    "normalize_row",
    "output_fieldnames",
    "pick_target_languages",
    "select_best",
]
