"""
A quality rubric and the code that sums its scores must agree on the criteria.

They drifted twice. ``quality_overall`` sums ``quality_keys(mode)`` and
``_normalize_quality`` defaults a missing criterion to 1, so a rubric edited to
score different criteria raises nothing -- every candidate simply collects the
same near-floor quality score and the ranking silently degrades to faithfulness
alone. It is invisible in the CSV, which only carries ``qual_overall``.

Worse, a mode NAME is not unique across packs: `lookup` scores different
criteria in prompts_eurlex than in prompts_un, and UN's `practitioners` shares
none of the technical five. So the mode name cannot be the source of truth --
the rubric is, via ``rubric_keys``.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy

import pytest

from clir_bench.core import grading
from clir_bench.core.grading import (
    _normalize_quality,
    grade_columns,
    quality_keys,
    rubric_keys,
)
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import eurlex_batch, un_batch

PACKS = {
    "un": (PromptPack("clir_bench.domains.legal.qac.prompts_un"),
           ("lookup", "practitioners", "semantic", "technical", "descriptive")),
    "eurlex": (PromptPack("clir_bench.domains.legal.qac.prompts_eurlex"),
               ("lookup", "fact_pattern")),
}
CASES = [(p, m) for p, (_, modes) in PACKS.items() for m in modes]


@pytest.mark.parametrize("pack,mode", CASES)
def test_every_rubric_declares_five_scored_criteria(pack: str, mode: str) -> None:
    keys = rubric_keys(PACKS[pack][0].quality(mode, "batch"))
    assert len(keys) == 5, (pack, mode, keys)
    assert len(set(keys)) == 5


@pytest.mark.parametrize("pack,mode", CASES)
def test_the_grade_is_summed_over_the_criteria_the_rubric_scores(pack: str, mode: str) -> None:
    """The regression: a perfect response must score 25, not silently less."""
    rubric = PACKS[pack][0].quality(mode, "batch")
    keys = rubric_keys(rubric)
    perfect = {k: 5 for k in keys}
    row = _normalize_quality(perfect, mode, keys)
    assert row["overall"] == 25, (pack, mode, row)


def test_the_same_mode_name_scores_differently_in_the_two_packs() -> None:
    """Why the mode name cannot be the source of truth."""
    un = rubric_keys(PACKS["un"][0].quality("lookup", "batch"))
    eurlex = rubric_keys(PACKS["eurlex"][0].quality("lookup", "batch"))
    assert un != eurlex
    assert "consequence" in un and "consequence" not in eurlex
    assert "focus" in eurlex and "focus" not in un


@pytest.mark.parametrize("mode", PACKS["un"][1])
def test_un_csv_has_a_column_for_every_criterion_its_rubrics_score(mode: str) -> None:
    """``FIELDS`` is a fixed tuple and DictWriter raises on an unknown key, so a
    rubric criterion with no column fails the write outright."""
    for key in rubric_keys(PACKS["un"][0].quality(mode, "batch")):
        assert f"qual_{key}" in un_batch.FIELDS, (mode, key)


@pytest.mark.parametrize("pack,mode", CASES)
def test_grade_columns_emits_the_rubric_criteria_not_the_mode_default(pack: str, mode: str) -> None:
    keys = rubric_keys(PACKS[pack][0].quality(mode, "batch"))
    quality = _normalize_quality({k: 4 for k in keys}, mode, keys)
    row = grade_columns({"grounding": 5, "precision": 5, "numerical_fidelity": 5},
                        quality, mode)
    for key in keys:
        assert row[f"qual_{key}"] == 4
    # nothing from the mode-name default leaks in when the rubric disagrees
    for stale in set(quality_keys(mode)) - set(keys):
        assert f"qual_{stale}" not in row


def test_both_batch_drivers_default_to_the_same_generator() -> None:
    assert un_batch.DEFAULT_GEN_MODEL == eurlex_batch.DEFAULT_GEN_MODEL == "gpt-5.6-luna"


V2_CASES = [(pack, mode) for pack, mode in CASES
            if "legal-qg-v2.0" in PACKS[pack][0].quality(mode, "batch")]


def _legal_example(pack="eurlex", mode="lookup"):
    prompt = PACKS[pack][0].quality(mode, "batch")
    keys = rubric_keys(prompt)
    rubric_mode = re.search(r"^# MODE: (\w+)", prompt, re.MULTILINE).group(1)
    metadata = re.search(r"^Required metadata_checks: ([\w, ]+)\.", prompt, re.MULTILINE).group(1).split(", ")
    candidate = {
        "candidate_id": "candidate-001", "question_language": "en",
        "question": "What is the minimum coverage?", "answer": "EUR 30,000",
        "anchor": "minimum coverage", "generator_model_id": "must-not-leak",
        "total_score": 39,
    }
    sources = [{"source_id": "target-1", "role": "target",
                "text": "Minimum insurance coverage is EUR 30,000.",
                "metadata": {"document_id": "document-1"}}]
    audit = {
        "index": 0, "candidate_id": candidate["candidate_id"],
        "rubric_version": "legal-qg-v2.0", "mode": rubric_mode,
        "evidence": [{"evidence_id": "e1", "source_id": "target-1", "quote": sources[0]["text"]}],
        "target_relation": "central", "reasoning_requirement": "extraction",
        "validity": {key: {"status": "pass", "evidence_ids": ["e1"], "note": "Supported by the supplied target."}
                     for key in grading._VALIDITY_KEYS},
        "scores": {key: 5 for key in keys},
        "score_notes": {key: "The requested rule is clear and precisely delimited." for key in keys},
        "metadata_checks": [{"field": field, "status": "ok", "note": "Consistent with the candidate."} for field in metadata],
        "issues": [], "suggested_repair": None, "suggested_mode": None, "confidence": "high",
    }
    return prompt, candidate, sources, audit


def _grade_legal(monkeypatch, response, *, pack="eurlex", mode="lookup", **kwargs):
    prompt, candidate, sources, _ = _legal_example(pack, mode)
    monkeypatch.setattr(grading, "_invoke", lambda *args: json.dumps(response))
    return grading.grade_quality(None, grading.GraderConfig("test"), prompt, "unused legacy text",
                                 [candidate], mode, sources=sources,
                                 target_source_id="target-1", **kwargs)


@pytest.mark.parametrize("pack,mode", V2_CASES)
def test_legal_v2_grades_follow_each_real_prompt_and_preserve_audits(monkeypatch, pack, mode):
    _, _, _, audit = _legal_example(pack, mode)
    rows = _grade_legal(monkeypatch, [audit], pack=pack, mode=mode)
    assert rows[0]["overall"] == 25
    assert rows[0]["_response"] == audit
    columns = grade_columns({"grounding": 5, "precision": 4, "numerical_fidelity": 3}, rows[0], mode)
    assert columns["total_score"] == 37
    assert columns["quality_audit_status"] == "clear"
    assert columns["quality_target_relevance_status"] == "pass"
    assert json.loads(columns["quality_verifier_response_json"]) == audit


def test_legal_v2_input_is_structured_and_model_blind(monkeypatch):
    prompt, candidate, sources, audit = _legal_example()
    captured = []

    def invoke(client, config, system_prompt, user_content):
        captured.append(json.loads(user_content))
        return json.dumps([audit])

    monkeypatch.setattr(grading, "_invoke", invoke)
    grading.grade_quality(None, grading.GraderConfig("test"), prompt, "ignored",
                          [candidate], "lookup", sources=sources, target_source_id="target-1",
                          policies={"target_granularity": "article", "answer_role": "evidence_span"})
    envelope = captured[0]
    assert envelope["sources"] == sources
    assert envelope["mode"] == "eurlex_lookup"
    assert envelope["target_granularity"] == "article"
    assert envelope["candidates"][0]["candidate_id"] == candidate["candidate_id"]
    assert "generator_model_id" not in envelope["candidates"][0]
    assert "total_score" not in envelope["candidates"][0]


@pytest.mark.parametrize("mutation", [
    lambda row: row.update(candidate_id="different"),
    lambda row: row.update(index=True),
    lambda row: row.update(rubric_version="old"),
    lambda row: row.update(mode="un_lookup"),
    lambda row: row.update(target_relation="valid"),
    lambda row: row.update(total_score=40),
    lambda row: row["scores"].pop("focus"),
    lambda row: row["scores"].update(focus=True),
    lambda row: row["scores"].update(focus=6),
    lambda row: row["scores"].update(focus="5"),
    lambda row: row["scores"].update(focus=None),
    lambda row: row["score_notes"].update(focus=""),
    lambda row: row["evidence"][0].update(source_id="invented"),
    lambda row: row["evidence"][0].update(quote="Invented exact quotation"),
    lambda row: row["evidence"].append(deepcopy(row["evidence"][0])),
    lambda row: row["validity"]["target_relevance"].update(evidence_ids=[]),
    lambda row: row["validity"]["question_premises"].update(evidence_ids=["invented"]),
    lambda row: row["validity"]["question_premises"].update(status="clear"),
    lambda row: row["metadata_checks"].pop(),
    lambda row: row["metadata_checks"][1].update(field="rendering"),
    lambda row: row["metadata_checks"][0].update(status="pass"),
    lambda row: row.update(suggested_mode="technical"),
])
def test_legal_v2_rejects_invalid_identity_scores_and_audits(monkeypatch, mutation):
    _, _, _, audit = _legal_example()
    mutation(audit)
    with pytest.raises(ValueError):
        _grade_legal(monkeypatch, [audit])


def test_legal_v2_nulls_remain_unranked_and_repairs_remain_audit_data(monkeypatch):
    _, candidate, _, audit = _legal_example()
    audit["scores"]["focus"] = None
    audit["issues"] = [{"code": "incomplete_evidence", "layer": "input", "severity": "review",
                        "affected_criteria": ["focus"], "evidence_ids": [], "note": "Additional context is needed."}]
    audit["suggested_repair"] = "Suggested wording, without altering the stored question."
    quality = _grade_legal(monkeypatch, [audit])[0]
    columns = grade_columns({"overall": 15}, quality, "lookup")
    assert columns["qual_focus"] is None
    assert columns["qual_overall"] is None
    assert columns["total_score"] is None
    assert columns["quality_audit_status"] == "review"
    assert candidate["question"] == "What is the minimum coverage?"
    ranked = grading.rank_candidates([candidate, {"question": "complete"}],
                                     [{"overall": 15}, {"overall": 10}],
                                     [quality, {"overall": 20}], "lookup")
    assert ranked[0].qa["question"] == "complete"


def test_legal_v2_requires_explicit_inputs_before_calling_verifier(monkeypatch):
    prompt, candidate, sources, _ = _legal_example()
    monkeypatch.setattr(grading, "_invoke", lambda *args: pytest.fail("Invalid input must fail before API access"))
    config = grading.GraderConfig("test")
    with pytest.raises(ValueError, match="labeled sources"):
        grading.grade_quality(None, config, prompt, "flat passage", [candidate], "lookup")
    with pytest.raises(ValueError, match="candidate_id"):
        grading.grade_quality(None, config, prompt, "", [{"question": "q", "answer": "a"}], "lookup",
                              sources=sources, target_source_id="target-1")
    with pytest.raises(ValueError, match="cannot override"):
        grading.grade_quality(None, config, prompt, "", [candidate], "lookup",
                              sources=sources, target_source_id="target-1", policies={"mode": "injected"})


def test_strict_legacy_grades_reject_missing_scores_and_keep_default_compatibility(monkeypatch):
    monkeypatch.setattr(grading, "_invoke", lambda *args: '[]')
    config = grading.GraderConfig("test")
    pairs = [{"question": "q", "answer": "a"}]
    with pytest.raises(ValueError, match="exactly 1"):
        grading.grade_faithfulness(None, config, "legacy", "source", pairs, strict=True)
    with pytest.raises(ValueError, match="exactly 1"):
        grading.grade_quality(None, config, "legacy", "source", pairs, "technical", strict=True)
    assert grading.grade_faithfulness(None, config, "legacy", "source", pairs)[0]["overall"] == 3
    assert grading.grade_quality(None, config, "legacy", "source", pairs, "technical")[0]["overall"] == 5


def test_strict_legacy_grades_keep_raw_response_and_candidate_order(monkeypatch):
    response = [{"index": 1, "grounding": 3, "precision": 3, "numerical_fidelity": 3, "reason": "Second."},
                {"index": 0, "grounding": 5, "precision": 5, "numerical_fidelity": 5, "reason": "First."}]
    monkeypatch.setattr(grading, "_invoke", lambda *args: json.dumps(response))
    rows = grading.grade_faithfulness(None, grading.GraderConfig("test"), "legacy", "source",
                                     [{"question": "q1"}, {"question": "q2"}], strict=True)
    assert [row["overall"] for row in rows] == [15, 9]
    assert rows[0]["_response"] == response[1]
