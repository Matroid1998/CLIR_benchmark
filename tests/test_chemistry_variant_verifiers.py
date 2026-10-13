"""Chemistry control queries retain the current verifier contract and CSV audits."""

from __future__ import annotations

import csv
import json
from types import SimpleNamespace

import pytest

from clir_bench.core import corpus, grading, qagen
from clir_bench.core.config import LLMSettings, Settings
from clir_bench.core.context import AppContext
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.chemistry.codeswitch import variant_qa
from clir_bench.domains.chemistry.domain import SPEC

PACK = PromptPack(SPEC.prompts_package)
RUBRIC_VERSION = "chemistry-clir-exceptional-r1"


@pytest.fixture
def context(tmp_path):
    return AppContext.build(Settings(
        project_root=tmp_path, data_dir=tmp_path / "data", reports_dir=tmp_path / "reports",
        cluster_dir=tmp_path / "cluster", llm=LLMSettings(retries=1),
    ), SPEC)


def candidate(question="Which catalyst is used to crack diarylethanes to alkylstyrenes?"):
    return {
        "question": question,
        "answer": "a zeolite with the MWW framework",
        "anchor": "crack diarylethanes to alkylstyrenes",
        "evidence": "a zeolite with the MWW framework",
        "evidence_language": "en",
        "answer_is_translation": False,
        "question_type": "material_or_composition",
    }


def control_row():
    return {
        "id": "control-en", "publication_number": "EP-1234567-A1", "language": "en",
        "anchor_language": "en", "variant": "E", "source_id": "original-en",
        "concept_chebi_id": "CHEBI:1", "concept_name": "catalyst",
        "context": (
            "Title: Catalytic cracking\n\nAbstract: To crack diarylethanes to "
            "alkylstyrenes, the process uses a zeolite with the MWW framework."
        ),
    }


def offline_verifiers(monkeypatch, candidates, *, missing_stage=None, scores=None):
    """Exercise real candidate/grader parsing while replacing every model transport."""
    calls = []
    scores = scores or [4] * len(candidates)
    monkeypatch.setattr(variant_qa, "client_for", lambda model: None)

    def generate(client, model, messages, **kwargs):
        assert messages[0]["content"] == PACK.generation("lookup", "en")
        return json.dumps(candidates)

    def grade(client, settings, prompt, content):
        payload = json.loads(content)
        calls.append(prompt)
        assert payload["candidates"] == [
            dict(item, mode="lookup", question_language="en") for item in candidates
        ]
        if prompt == PACK.faithfulness():
            result = [
                dict.fromkeys(grading.FAITHFULNESS_KEYS, 4)
                | {"index": index, "reason": "The supplied excerpt supports the answer."}
                for index in range(len(candidates))
            ]
            if missing_stage == "faithfulness":
                result[0]["grounding"] = None
                result[0]["reason"] = "The decisive source unit is missing from the packet."
            return json.dumps(result)
        assert prompt == PACK.quality("lookup")
        keys = grading.rubric_keys(prompt)
        result = {
            "candidates": [
                {
                    "index": index, "candidate_id": item.get("candidate_id"),
                    "scores": dict.fromkeys(keys, scores[index]),
                    "score_notes": {key: "The question meets this criterion." for key in keys},
                    "checks": {"mode": "pass", "support": "pass", "metadata": "pass"},
                    "problems": [],
                }
                for index, item in enumerate(candidates)
            ],
            "batch_diversity": "not_applicable" if len(candidates) == 1 else "fail",
        }
        if missing_stage == "quality":
            first = result["candidates"][0]
            first["scores"][keys[2]] = None
            first["score_notes"][keys[2]] = "The decisive source unit is missing."
            first["checks"]["support"] = "uncertain"
            first["problems"] = ["support: The complete source unit is needed to assess the answer."]
        return json.dumps(result)

    monkeypatch.setattr(qagen, "chat", generate)
    monkeypatch.setattr(grading, "_invoke", grade)
    return calls


def assert_current_audit(row):
    assert row["quality_rubric_version"] == RUBRIC_VERSION
    assert row["faithfulness_rubric_version"] == RUBRIC_VERSION
    assert row["quality_audit_status"] == "clear"
    quality = json.loads(row["quality_verifier_response_json"])
    assert quality["scores"] == dict.fromkeys(grading.rubric_keys(PACK.quality("lookup")), 4)
    assert json.loads(row["quality_score_notes_json"]) == quality["score_notes"]
    assert json.loads(row["quality_checks_json"]) == quality["checks"]
    assert json.loads(row["quality_problems_json"]) == []
    assert json.loads(row["faithfulness_verifier_response_json"])["grounding"] == 4
    for check in ("mode", "support", "metadata"):
        assert row[f"quality_{check}_status"] == "pass"


def test_control_document_ranks_lookup_scores_and_keeps_evidence_and_audits(context, monkeypatch):
    first = candidate()
    best = candidate("What catalyst is used to crack diarylethanes to alkylstyrenes?")
    calls = offline_verifiers(monkeypatch, [first, best], scores=[3, 4])
    generator = variant_qa._Generator(context, SimpleNamespace(model="test-model"))

    rows = generator.control_document(control_row())

    assert len(rows) == 1
    result = rows[0]
    for key, value in best.items():
        assert result[key] == value
    assert result["mode"] == "lookup"
    assert result["question_language"] == result["query_language"] == "en"
    assert result["variant"] == "E"
    assert result["gold_id"] == "control-en"
    assert result["source_id"] == "original-en"
    assert result["total_score"] == 32
    assert result["qual_overall"] == 20
    for key in grading.rubric_keys(PACK.quality("lookup")):
        assert result[f"qual_{key}"] == 4
    assert result["quality_batch_diversity"] == "fail"
    assert_current_audit(result)
    assert calls == [PACK.faithfulness(), PACK.quality("lookup")]


@pytest.mark.parametrize("missing_stage", ["faithfulness", "quality"])
@pytest.mark.parametrize("has_assessable_candidate", [False, True])
def test_control_document_excludes_null_total_candidates(
    context, monkeypatch, missing_stage, has_assessable_candidate,
):
    candidates = [candidate()]
    if has_assessable_candidate:
        candidates.append(candidate("What catalyst is used to crack diarylethanes to alkylstyrenes?"))
    offline_verifiers(monkeypatch, candidates, missing_stage=missing_stage)
    generator = variant_qa._Generator(context, SimpleNamespace(model="test-model"))

    rows = generator.control_document(control_row())

    if has_assessable_candidate:
        assert len(rows) == 1
        assert rows[0]["question"] == candidates[1]["question"]
        assert rows[0]["total_score"] == 32
    else:
        assert rows == []


def test_variant_csv_preserves_lookup_columns_audits_and_json_metadata(context, monkeypatch):
    item = candidate()
    offline_verifiers(monkeypatch, [item])
    workdir = context.workspace.data("code_switched")
    row = control_row()
    corpus.write_rows(workdir / variant_qa.builder.CORPUS_FILENAME, [row], tuple(row))
    corpus.write_rows(context.workspace.corpus_csv("gp"), [], context.schema.fields)
    monkeypatch.setattr(variant_qa.builder, "load_concepts", lambda path: [])
    monkeypatch.setattr(variant_qa.builder, "alias_graph_path", lambda context: workdir / "unused.json")
    args = SimpleNamespace(model="test-model", source="gp", limit=None, workers=1)

    assert variant_qa.generate_variant_qa(context, args) == 0

    path = workdir / variant_qa.builder.QAC_FILENAME
    saved, = corpus.read_rows(path)
    assert qagen.candidate_from_row(saved) == dict(item, mode="lookup", question_language="en")
    assert saved["answer_is_translation"] == "false"
    assert saved["total_score"] == "32"
    assert saved["quality_batch_diversity"] == "not_applicable"
    for key in grading.rubric_keys(PACK.quality("lookup")):
        assert saved[f"qual_{key}"] == "4"
    assert_current_audit(saved)
    with path.open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle))
    assert len(header) == len(set(header))
    assert set(qagen.CANDIDATE_METADATA_FIELDS) <= set(header)
    assert set(qagen.grading_fieldnames(prompts=PACK, modes=("lookup",))) <= set(header)
