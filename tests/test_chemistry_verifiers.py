"""Chemistry verifier contracts, missing evidence, and structured audit transport."""

from __future__ import annotations

import json

import pytest

from clir_bench.core import grading
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.chemistry.domain import SPEC

PACK = PromptPack(SPEC.prompts_package)
VERSION = "chemistry-clir-exceptional-r1"
CONFIG = grading.GraderConfig("test")
PERSONA_KEYS = {
    "lookup": ("technical_search_realism", "standalone_anchoring", "information_value"),
    "process_retrieval": ("process_search_realism", "start_goal_anchoring", "route_completeness"),
    "conceptual": ("relationship_search_realism", "subject_anchoring", "explicit_relationship"),
    "constraint_search": ("requirement_search_realism", "task_and_constraint_anchoring", "candidate_fit"),
    "comparison": ("comparative_search_realism", "two_sided_anchoring", "common_dimension_value"),
    "assertion_verification": ("checking_search_realism", "assertion_scope", "verdict_decisiveness"),
    "source_finding": ("disclosure_search_realism", "technical_clue_anchoring", "clue_identity_fit"),
}


def quality_fixture(mode="lookup", count=1):
    keys = (*PERSONA_KEYS[mode], "focus_and_economy", "linguistic_quality")
    candidates = [{"candidate_id": f"qa-{index}", "mode": mode, "question_language": "en",
                   "question": "Which catalyst cracks diarylethanes?", "answer": "MWW zeolite"}
                  for index in range(count)]
    response = {
        "candidates": [
            {"index": index, "candidate_id": candidate["candidate_id"],
             "scores": dict.fromkeys(keys, 4),
             "score_notes": dict.fromkeys(keys, "The submitted wording and evidence suffice."),
             "checks": dict.fromkeys(("mode", "support", "metadata"), "pass"), "problems": []}
            for index, candidate in enumerate(candidates)
        ],
        "batch_diversity": "not_applicable" if count <= 1 else "pass",
    }
    return candidates, response


def grade_quality(monkeypatch, response, *, mode="lookup", count=1):
    candidates, _ = quality_fixture(mode, count)
    monkeypatch.setattr(grading, "_invoke", lambda *args: json.dumps(response))
    return grading.grade_quality(None, CONFIG, PACK.quality(mode), "Patent packet", candidates, mode)


def faith_fixture(count=1):
    return [{"index": index, "grounding": 4, "precision": 4, "numerical_fidelity": 4,
             "reason": "Routine correct catalyst evidence. Numerical fidelity not applicable; 4 is a compatibility value."}
            for index in range(count)]


def grade_faith(monkeypatch, response, count=1):
    candidates, _ = quality_fixture(count=count)
    monkeypatch.setattr(grading, "_invoke", lambda *args: json.dumps(response))
    return grading.grade_faithfulness(None, CONFIG, PACK.faithfulness(), "Patent packet", candidates)


@pytest.mark.parametrize("mode", PERSONA_KEYS)
@pytest.mark.parametrize("count", (1, 2, 3, 4))
def test_persona_criteria_and_compact_audit_are_preserved(monkeypatch, mode, count):
    _, response = quality_fixture(mode, count)
    assert grading.rubric_keys(PACK.quality(mode)) == (*PERSONA_KEYS[mode], "focus_and_economy", "linguistic_quality")
    rows = grade_quality(monkeypatch, response, mode=mode, count=count)
    for index, row in enumerate(rows):
        columns = grading.grade_columns({"overall": 12}, row, mode)
        assert columns["qual_overall"] == 20
        assert columns["total_score"] == 32
        assert columns["quality_rubric_version"] == VERSION
        assert columns["quality_audit_status"] == "clear"
        assert columns["quality_batch_diversity"] == response["batch_diversity"]
        assert json.loads(columns["quality_verifier_response_json"]) == response["candidates"][index]
        for field in ("score_notes", "checks", "problems"):
            assert json.loads(columns[f"quality_{field}_json"]) == response["candidates"][index][field]


def test_chemistry_transports_all_persona_metadata_to_both_verifiers(monkeypatch):
    candidates, response = quality_fixture()
    candidate = candidates[0]
    candidate.update(anchor="diarylethanes", evidence="原文", evidence_language="zh",
                     answer_is_translation=True, question_type="material_or_composition",
                     process_kind="synthesis_route", process_start="substrate", process_goal="product",
                     relationship_type="effect", solution_kind="material", objective="objective",
                     constraints=["constraint one", "constraint two"], comparison_entities=["A", "B"],
                     comparison_aspect="stability", assertion="claim", assertion_status="supported",
                     source_identifier="EP-123-A1", generator_model_id="hidden", total_score=40)
    captured = []

    def invoke(client, config, prompt, content):
        captured.append(json.loads(content))
        return json.dumps(faith_fixture() if prompt == PACK.faithfulness() else response)

    monkeypatch.setattr(grading, "_invoke", invoke)
    grading.grade_faithfulness(None, CONFIG, PACK.faithfulness(), "Original packet", candidates)
    grading.grade_quality(None, CONFIG, PACK.quality("lookup"), "Original packet", candidates, "lookup")
    expected = {key: value for key, value in candidate.items() if key not in ("generator_model_id", "total_score")}
    assert captured == [{"passages": "Original packet", "candidates": [expected]}] * 2


@pytest.mark.parametrize("mutation", [
    lambda data: data["candidates"].clear(),
    lambda data: data["candidates"].reverse(),
    lambda data: data["candidates"][0].update(index=True),
    lambda data: data["candidates"][0].update(candidate_id="other"),
    lambda data: data["candidates"][0].update(extra="unsupported"),
    lambda data: data["candidates"][0]["scores"].update(information_value=True),
    lambda data: data["candidates"][0]["scores"].update(information_value="4"),
    lambda data: data["candidates"][0]["scores"].update(information_value=6),
    lambda data: data["candidates"][0]["scores"].update(information_value=0),
    lambda data: data["candidates"][0]["scores"].update(information_value=5),
    lambda data: data["candidates"][0]["score_notes"].update(information_value=""),
    lambda data: data["candidates"][0]["checks"].update(metadata="fail"),
    lambda data: data["candidates"][0]["checks"].update(support="uncertain"),
    lambda data: data["candidates"][0].update(problems=[False]),
    lambda data: data.update(batch_diversity="not_applicable"),
])
def test_quality_rejects_malformed_contract_without_lenient_fallback(monkeypatch, mutation):
    _, response = quality_fixture(count=2)
    mutation(response)
    with pytest.raises(ValueError):
        grade_quality(monkeypatch, response, count=2)


@pytest.mark.parametrize("status,score,problem,audit", [
    ("fail", 2, "support: The required catalyst is absent.", "blocking"),
    ("uncertain", None, "support: The supplied source is truncated.", "review"),
    ("uncertain", 3, "support: The condition is only partly assessable.", "review"),
])
def test_support_problems_and_null_totals_remain_visible(monkeypatch, status, score, problem, audit):
    _, response = quality_fixture()
    item = response["candidates"][0]
    item["checks"]["support"] = status
    item["scores"]["information_value"] = score
    item["score_notes"]["information_value"] = problem
    item["problems"] = [problem]
    row = grade_quality(monkeypatch, response)[0]
    columns = grading.grade_columns({"overall": 12}, row, "lookup")
    assert columns["quality_audit_status"] == audit
    assert columns["total_score"] == (None if score is None else 28 + score)
    item["problems"] = ["metadata: This does not explain the support check."]
    with pytest.raises(ValueError, match="support:"):
        grade_quality(monkeypatch, response)


def test_exceptional_quality_score_requires_its_own_nonempty_evidence(monkeypatch):
    _, response = quality_fixture()
    item = response["candidates"][0]
    item["scores"]["information_value"] = 5
    item["score_notes"]["information_value"] = "Exceptional evidence:"
    with pytest.raises(ValueError, match="Exceptional evidence"):
        grade_quality(monkeypatch, response)
    item["score_notes"]["information_value"] += " The selection preserves a consequential route boundary."
    assert grade_quality(monkeypatch, response)[0]["overall"] == 21


@pytest.mark.parametrize("key", grading.FAITHFULNESS_KEYS)
def test_faithfulness_null_is_unassessable_not_a_fabricated_failure(monkeypatch, key):
    response = faith_fixture()
    response[0][key] = None
    response[0]["reason"] = "Necessary evidence was not supplied for this criterion."
    row = grade_faith(monkeypatch, response)[0]
    columns = grading.grade_columns(row, {"overall": 20}, "lookup")
    assert row[key] is None
    assert columns["faith_overall"] is None
    assert columns["total_score"] is None
    assert columns["faithfulness_rubric_version"] == VERSION
    assert json.loads(columns["faithfulness_verifier_response_json"]) == response[0]


@pytest.mark.parametrize("mutation", [
    lambda data: data.reverse(),
    lambda data: data[0].update(index=True),
    lambda data: data[0].update(grounding=True),
    lambda data: data[0].update(grounding="4"),
    lambda data: data[0].update(grounding=0),
    lambda data: data[0].update(grounding=6),
    lambda data: data[0].update(reason=""),
    lambda data: data[0].update(candidate_id="extra-field"),
    lambda data: data[0].update(precision=5),
    lambda data: data.pop(),
])
def test_faithfulness_rejects_malformed_contract_without_padding(monkeypatch, mutation):
    response = faith_fixture(2)
    mutation(response)
    with pytest.raises(ValueError):
        grade_faith(monkeypatch, response, count=2)


@pytest.mark.parametrize("key,label", [
    ("grounding", "Grounding exceptional:"),
    ("precision", "Precision exceptional:"),
    ("numerical_fidelity", "Numerical fidelity exceptional:"),
])
def test_faithfulness_exceptional_scores_require_specific_evidence(monkeypatch, key, label):
    response = faith_fixture()
    response[0][key] = 5
    response[0]["reason"] = label
    with pytest.raises(ValueError, match="evidence in reason"):
        grade_faith(monkeypatch, response)
    response[0]["reason"] += " The span preserves the delicate stage-to-duration association."
    assert grade_faith(monkeypatch, response)[0]["overall"] == 13


def test_empty_candidates_do_not_call_models(monkeypatch):
    monkeypatch.setattr(grading, "_invoke", lambda *args: pytest.fail("graded an empty list"))
    assert grading.grade_faithfulness(None, CONFIG, PACK.faithfulness(), "packet", []) == []
    assert grading.grade_quality(None, CONFIG, PACK.quality("lookup"), "packet", [], "lookup") == []


def test_prompt_mode_version_and_count_mismatches_fail_before_inference(monkeypatch):
    monkeypatch.setattr(grading, "_invoke", lambda *args: pytest.fail("called malformed rubric"))
    candidates, _ = quality_fixture()
    with pytest.raises(ValueError, match="mode"):
        grading.grade_quality(None, CONFIG, PACK.quality("lookup"), "packet", candidates, "comparison")
    with pytest.raises(ValueError, match="versions"):
        grading.grade_quality(None, CONFIG, PACK.quality("lookup").replace(VERSION, "chemistry-unknown"),
                              "packet", candidates, "lookup")
    for function, prompt, args in ((grading.grade_quality, PACK.quality("lookup"), ("lookup",)),
                                    (grading.grade_faithfulness, PACK.faithfulness(), ())):
        with pytest.raises(ValueError, match="expected count"):
            function(None, CONFIG, prompt, "packet", candidates, *args, expected=3)


def test_optional_ids_and_missing_answer_remain_assessable(monkeypatch):
    candidates, response = quality_fixture()
    candidates[0].pop("candidate_id")
    candidates[0].pop("answer")
    item = response["candidates"][0]
    item.update(candidate_id=None)
    item["scores"]["information_value"] = 1
    item["checks"].update(support="fail", metadata="fail")
    item["problems"] = ["support: The answer is missing.", "metadata: Required answer is absent."]
    monkeypatch.setattr(grading, "_invoke", lambda *args: json.dumps(response))
    rows = grading.grade_quality(None, CONFIG, PACK.quality("lookup"), "packet", candidates, "lookup")
    assert rows[0]["_response"]["candidate_id"] is None


def test_ranking_keeps_unassessable_rows_last_for_audit():
    candidates, _ = quality_fixture(count=2)
    faith = [dict.fromkeys(grading.FAITHFULNESS_KEYS, 4) for _ in candidates]
    faith[0]["grounding"] = None
    quality = [{"overall": 20}, {"overall": 15}]
    ranked = grading.rank_candidates(candidates, faith, quality, "lookup")
    assert [row.qa["candidate_id"] for row in ranked] == ["qa-1", "qa-0"]
    assert ranked[-1].total is None
