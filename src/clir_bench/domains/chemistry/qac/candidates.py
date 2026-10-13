"""The seven chemistry personas' generation JSON contracts."""

from __future__ import annotations

from typing import Any

COMMON_FIELDS = (
    "question", "answer", "anchor", "evidence", "evidence_language", "answer_is_translation",
)
MODE_FIELDS = {
    "lookup": ("question_type",),
    "process_retrieval": ("process_kind", "process_start", "process_goal"),
    "conceptual": ("relationship_type",),
    "constraint_search": ("solution_kind", "objective", "constraints"),
    "comparison": ("comparison_entities", "comparison_aspect"),
    "assertion_verification": ("assertion", "assertion_status"),
    "source_finding": ("source_identifier",),
}
ENUMS = {
    "question_type": (
        "parameter_or_condition", "material_or_composition", "structure", "biological_target",
        "reported_outcome", "method_detail", "application",
    ),
    "process_kind": (
        "synthesis_route", "formulation_or_processing", "separation_or_recycling",
        "fabrication_or_surface_treatment", "analytical_workflow", "diagnostic_or_corrective_workflow",
    ),
    "relationship_type": (
        "component_role", "modification_effect", "structure_property", "interaction", "stated_rationale",
    ),
    "solution_kind": (
        "material_or_formulation", "treatment_or_process", "analytical_or_control_system",
        "functional_device",
    ),
    "assertion_status": ("supported", "contradicted"),
}
LIST_FIELDS = ("constraints", "comparison_entities")
SUBSTRING_FIELDS = ("anchor", "process_start", "process_goal", "objective", "assertion")


def _text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")


def parse_candidates(data: Any, mode: str) -> list[dict[str, Any]]:
    """Preserve evidence verbatim; malformed output raises for the caller to retry.

    Abstention is a valid empty result. Scientific support and translation quality
    are judged by the verifiers, not by these structural checks.
    """
    if mode not in MODE_FIELDS:
        raise ValueError(f"Unknown chemistry persona: {mode}")
    if not isinstance(data, list) or not 1 <= len(data) <= 3:
        raise ValueError("Expected one to three candidates or one skip_reason object")
    if len(data) == 1 and isinstance(data[0], dict) and set(data[0]) == {"skip_reason"}:
        _text(data[0]["skip_reason"], "skip_reason")
        return []

    expected = set(COMMON_FIELDS + MODE_FIELDS[mode])
    candidates = []
    for candidate in data:
        if not isinstance(candidate, dict) or set(candidate) != expected:
            raise ValueError(f"{mode} candidate must contain exactly {sorted(expected)}")
        _text(candidate["question"], "question")
        for key, value in candidate.items():
            if key == "answer_is_translation":
                if type(value) is not bool:
                    raise ValueError("answer_is_translation must be a JSON boolean")
            elif key in LIST_FIELDS:
                if not isinstance(value, list) or not value:
                    raise ValueError(f"{key} must be a nonempty array")
                for part in value:
                    _text(part, key)
                if key == "comparison_entities" and (len(value) != 2 or value[0] == value[1]):
                    raise ValueError("comparison_entities must contain exactly two distinct strings")
                cursor = 0
                for part in value:
                    start = candidate["question"].find(part, cursor)
                    if start < 0:
                        raise ValueError(f"{key} must contain question substrings in appearance order")
                    cursor = start + len(part)
            else:
                _text(value, key)
            if key in ENUMS and value not in ENUMS[key]:
                raise ValueError(f"Invalid {key}: {value!r}")
            if key in SUBSTRING_FIELDS and value not in candidate["question"]:
                raise ValueError(f"{key} must be an exact question substring")
        if mode == "source_finding":
            if candidate["answer"] != candidate["source_identifier"]:
                raise ValueError("source_finding answer must equal source_identifier")
            if candidate["answer_is_translation"]:
                raise ValueError("source_finding answer_is_translation must be false")
        candidates.append(dict(candidate))
    return candidates
