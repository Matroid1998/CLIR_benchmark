"""
LLM-as-judge grading.

Six near-identical grading shells existed across the old repo (OpenAI batch,
OpenRouter batch, single-pair OpenAI, single-pair Claude, and two normalizers in
comparison scripts). They differed only in transport and arity, so those are the
two parameters here; the rubric, the score arithmetic, the pad-with-1 fallback
and the field names are defined once.

Two rubric arities exist on purpose and must not be merged: the main pipeline
grades three candidates in one call (prompt returns a JSON list), while the
concept/variant pipelines grade one pair (prompt returns a JSON object). They
are different prompt files with different output contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from clir_bench.core.llm import (
    chat,
    chat_with_thinking,
    parse_json_response,
    provider_of,
)

MODE_TECHNICAL = "technical"
MODE_SEMANTIC = "semantic"

# CSV column names. Load-bearing: published datasets carry these headers.
FAITHFULNESS_FIELDS = (
    "faith_grounding",
    "faith_precision",
    "faith_numerical_fidelity",
    "faith_overall",
)
TECHNICAL_QUALITY_FIELDS = (
    "qual_search_bar_realism",
    "qual_specificity",
    "qual_phrasing_economy",
    "qual_focus",
    "qual_linguistic_quality",
    "qual_overall",
)
SEMANTIC_QUALITY_FIELDS = (
    "qual_search_realism",
    "qual_lexical_distance",
    "qual_conceptual_framing",
    "qual_retrievability",
    "qual_linguistic_quality",
    "qual_overall",
)

# Rubric sub-scores summed into each aggregate.
FAITHFULNESS_KEYS = ("grounding", "precision", "numerical_fidelity")
TECHNICAL_QUALITY_KEYS = (
    "search_bar_realism",
    "specificity",
    "phrasing_economy",
    "focus",
    "linguistic_quality",
)
SEMANTIC_QUALITY_KEYS = (
    "search_realism",
    "lexical_distance",
    "conceptual_framing",
    "retrievability",
    "linguistic_quality",
)


def quality_keys(mode: str) -> tuple[str, ...]:
    return TECHNICAL_QUALITY_KEYS if mode == MODE_TECHNICAL else SEMANTIC_QUALITY_KEYS


def quality_fields(mode: str) -> tuple[str, ...]:
    return TECHNICAL_QUALITY_FIELDS if mode == MODE_TECHNICAL else SEMANTIC_QUALITY_FIELDS


def faith_overall(scores: Mapping[str, Any]) -> int:
    return sum(int(scores.get(key, 0)) for key in FAITHFULNESS_KEYS)


def quality_overall(scores: Mapping[str, Any], mode: str) -> int:
    return sum(int(scores.get(key, 0)) for key in quality_keys(mode))


def total_score(faith: Mapping[str, Any], quality: Mapping[str, Any], mode: str) -> int:
    """Faithfulness aggregate plus quality aggregate (the ranking key)."""
    return int(faith.get("overall", faith_overall(faith))) + int(
        quality.get("overall", quality_overall(quality, mode))
    )


# --------------------------------------------------------------------------- #
# Grader
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class GraderConfig:
    """Which model grades, over which transport, with what knobs."""

    model: str
    reasoning_effort: str = "low"
    thinking_budget_tokens: int = 8000
    thinking_max_tokens: int = 12000
    # Force the Claude extended-thinking transport even for a non-default model.
    use_thinking: Optional[bool] = None

    @property
    def thinking(self) -> bool:
        if self.use_thinking is not None:
            return self.use_thinking
        return provider_of(self.model) == "openrouter"


def candidates_block(qa_pairs: Sequence[Mapping[str, str]]) -> str:
    """The candidate serialization every grader prompt expects."""
    return "\n\n".join(
        f"Candidate {i}:\n  Question: {qa.get('question', '')}\n  Answer: {qa.get('answer', '')}"
        for i, qa in enumerate(qa_pairs)
    )


def _invoke(client: Any, config: GraderConfig, system_prompt: str, user_content: str) -> str:
    if config.thinking:
        return chat_with_thinking(
            client,
            config.model,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            budget_tokens=config.thinking_budget_tokens,
            max_tokens=config.thinking_max_tokens,
        )
    return chat(
        client,
        config.model,
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        reasoning_effort=config.reasoning_effort,
    )


def _as_list(data: Any) -> list[dict]:
    if isinstance(data, dict):
        return [data]
    return [item for item in (data or []) if isinstance(item, dict)]


def _normalize_faith(item: Mapping[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {key: _int_or(item.get(key), 1) for key in FAITHFULNESS_KEYS}
    row["reason"] = str(item.get("reason", "")).strip()
    row["overall"] = faith_overall(row)
    return row


def _normalize_quality(item: Mapping[str, Any], mode: str) -> dict[str, Any]:
    row: dict[str, Any] = {key: _int_or(item.get(key), 1) for key in quality_keys(mode)}
    row["failure_type"] = str(item.get("failure_type", "none")).strip()
    row["reason"] = str(item.get("reason", "")).strip()
    row["overall"] = quality_overall(row, mode)
    return row


def _int_or(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _missing_faith() -> dict[str, Any]:
    row: dict[str, Any] = {key: 1 for key in FAITHFULNESS_KEYS}
    row["reason"] = "missing"
    row["overall"] = faith_overall(row)
    return row


def _missing_quality(mode: str) -> dict[str, Any]:
    row: dict[str, Any] = {key: 1 for key in quality_keys(mode)}
    row["failure_type"] = "missing"
    row["reason"] = "missing"
    row["overall"] = quality_overall(row, mode)
    return row


def grade_faithfulness(
    client: Any,
    config: GraderConfig,
    prompt: str,
    passages: str,
    qa_pairs: Sequence[Mapping[str, str]],
    *,
    expected: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Grade answers for grounding, precision and numerical fidelity.

    ``expected`` is the candidate count to return (defaults to ``len(qa_pairs)``).
    Short or malformed responses are padded with score-1 rows rather than raising:
    a grader hiccup must not lose the rest of a document's work.
    """
    want = expected if expected is not None else len(qa_pairs)
    raw = _invoke(client, config, prompt, f"{passages}\n\n{candidates_block(qa_pairs)}")
    items = sorted(_as_list(parse_json_response(raw))[:want], key=lambda x: x.get("index", 0))
    rows = [_normalize_faith(item) for item in items]
    while len(rows) < want:
        rows.append(_missing_faith())
    return rows


def grade_quality(
    client: Any,
    config: GraderConfig,
    prompt: str,
    passages: str,
    qa_pairs: Sequence[Mapping[str, str]],
    mode: str,
    *,
    expected: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Grade questions against the mode-specific quality rubric."""
    want = expected if expected is not None else len(qa_pairs)
    raw = _invoke(client, config, prompt, f"{passages}\n\n{candidates_block(qa_pairs)}")
    items = sorted(_as_list(parse_json_response(raw))[:want], key=lambda x: x.get("index", 0))
    rows = [_normalize_quality(item, mode) for item in items]
    while len(rows) < want:
        rows.append(_missing_quality(mode))
    return rows


def grade_one(
    client: Any,
    config: GraderConfig,
    faith_prompt: str,
    quality_prompt: str,
    passages: str,
    qa_pair: Mapping[str, str],
    mode: str = MODE_TECHNICAL,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Grade a single pair with the single-object rubric prompts.

    Used by the concept/variant/progressive pipelines, whose prompts return one
    JSON object rather than a list of three.
    """
    faith = grade_faithfulness(client, config, faith_prompt, passages, [qa_pair], expected=1)[0]
    quality = grade_quality(
        client, config, quality_prompt, passages, [qa_pair], mode, expected=1
    )[0]
    return faith, quality


def grade_columns(
    faith: Mapping[str, Any], quality: Mapping[str, Any], mode: str
) -> dict[str, Any]:
    """Flatten grades into the ``faith_*`` / ``qual_*`` / ``total_score`` columns."""
    row: dict[str, Any] = {}
    for key in FAITHFULNESS_KEYS:
        row[f"faith_{key}"] = faith.get(key, "")
    row["faith_overall"] = faith.get("overall", faith_overall(faith))
    for key in quality_keys(mode):
        row[f"qual_{key}"] = quality.get(key, "")
    row["qual_overall"] = quality.get("overall", quality_overall(quality, mode))
    row["faith_reason"] = faith.get("reason", "")
    row["qual_failure_type"] = quality.get("failure_type", "")
    row["qual_reason"] = quality.get("reason", "")
    row["total_score"] = total_score(faith, quality, mode)
    return row


@dataclass(frozen=True)
class GradedCandidate:
    """One generated Q/A pair with its grades, ranked by ``total_score``."""

    qa: Mapping[str, str]
    faith: Mapping[str, Any]
    quality: Mapping[str, Any]
    mode: str

    @property
    def total(self) -> int:
        return total_score(self.faith, self.quality, self.mode)


def rank_candidates(
    qa_pairs: Sequence[Mapping[str, str]],
    faith_rows: Sequence[Mapping[str, Any]],
    quality_rows: Sequence[Mapping[str, Any]],
    mode: str,
) -> list[GradedCandidate]:
    """Zip candidates with their grades, best total score first."""
    graded = [
        GradedCandidate(qa=qa, faith=faith_rows[i], quality=quality_rows[i], mode=mode)
        for i, qa in enumerate(qa_pairs)
        if i < len(faith_rows) and i < len(quality_rows)
    ]
    return sorted(graded, key=lambda c: c.total, reverse=True)


__all__ = [
    "FAITHFULNESS_FIELDS",
    "FAITHFULNESS_KEYS",
    "GradedCandidate",
    "GraderConfig",
    "MODE_SEMANTIC",
    "MODE_TECHNICAL",
    "SEMANTIC_QUALITY_FIELDS",
    "TECHNICAL_QUALITY_FIELDS",
    "candidates_block",
    "faith_overall",
    "grade_columns",
    "grade_faithfulness",
    "grade_one",
    "grade_quality",
    "quality_fields",
    "quality_keys",
    "quality_overall",
    "rank_candidates",
    "total_score",
]
