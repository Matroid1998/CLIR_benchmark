"""Persona generation, metadata transport, abstention and multilingual resource contracts."""

from __future__ import annotations

import json
import re
from types import SimpleNamespace

import pytest

from clir_bench.core import corpus, grading, qagen
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.chemistry.domain import SPEC
from clir_bench.domains.chemistry.qac.candidates import parse_candidates
from clir_bench.domains.chemistry.qac.plans import PLANS
from clir_bench.domains.chemistry.schema import SCHEMA
from clir_bench.domains.chemistry.vocabulary import MODES, WORKING_LANGUAGES

PACK = PromptPack(SPEC.prompts_package)


def examples(mode, language="en"):
    prompt = PACK.generation(mode, language)
    # The first array is the schema; the rest are two worked examples and a skip.
    return [
        json.JSONDecoder().raw_decode(prompt[match.start():])[0]
        for match in re.finditer(r"^\[\n", prompt, re.MULTILINE)
    ][1:]


def config():
    return qagen.GenerationConfig("test", grading.GraderConfig("test"), retries=1,
                                  candidate_parser=SPEC.qac_candidate_parser)


def document(candidate):
    family = candidate.get("source_identifier", "EP-1234567-A1")
    language = candidate["evidence_language"]
    return {"publication_number": family, "doc_id": f"{family}_{language}",
            "language": language, "context": candidate["evidence"]}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("language", WORKING_LANGUAGES)
def test_supplied_worked_examples_and_abstentions_obey_the_parser(mode, language):
    first, second, skip = examples(mode, language)
    assert parse_candidates(first, mode) == first
    assert parse_candidates(second, mode) == second
    assert parse_candidates(skip, mode) == []
    assert set(PACK.available_languages(mode)) == set(WORKING_LANGUAGES)
    # Every mode has a matching rubric; generic mode-name defaults may differ.
    keys = grading.rubric_keys(PACK.quality(mode))
    assert len(keys) == 5
    assert all(f"qual_{key}" in qagen.output_fieldnames(SCHEMA) for key in keys)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("count", [1, 2, 3])
def test_generate_grade_and_csv_round_trip_keeps_persona_evidence(
    monkeypatch, tmp_path, mode, count,
):
    candidate = examples(mode)[0][0]
    candidates = [dict(candidate) for _ in range(count)]
    row = document(candidate)
    item = qagen.PlanItem(row["publication_number"], "en", mode)
    calls = []

    def generate(client, model, messages, **kwargs):
        assert messages[0]["content"] == PACK.generation(mode, "en")
        assert f"publication_number: {item.family}" in messages[1]["content"]
        assert candidate["evidence"] in messages[1]["content"]
        return json.dumps(candidates)

    def grade(client, settings, prompt, content):
        calls.append(content)
        assert f"publication_number: {item.family}" in content
        assert f"Mode: {mode}" in content
        assert "Question language: en" in content
        for key, value in candidate.items():
            if key not in ("question", "answer"):
                assert str(value[0] if isinstance(value, list) else value) in content
        keys = (grading.FAITHFULNESS_KEYS if prompt == PACK.faithfulness()
                else grading.rubric_keys(prompt))
        return json.dumps([dict.fromkeys(keys, 5) | {"index": index, "reason": "Supported"}
                           for index in range(count)])

    monkeypatch.setattr(qagen, "chat", generate)
    monkeypatch.setattr(grading, "_invoke", grade)
    generated = qagen.generate_for_document(
        item, [row], schema=SCHEMA, prompts=PACK, config=config(),
        generation_client=None, grading_client=None,
    )
    assert len(generated) == count
    assert len(calls) == 2
    fields = qagen.output_fieldnames(SCHEMA)
    path = tmp_path / "results.csv"
    corpus.write_rows(path, [qagen.normalize_row(row, fields) for row in generated], fields)
    for saved in corpus.read_rows(path):
        restored = qagen.candidate_from_row(saved)
        assert restored == dict(candidate, mode=mode, question_language="en")
        assert saved["total_score"] == "40"
        assert json.loads(saved["faithfulness_verifier_response_json"])["grounding"] == 5
        assert json.loads(saved["quality_verifier_response_json"])["focus"] == 5


def test_abstention_does_not_call_graders(monkeypatch):
    monkeypatch.setattr(qagen, "chat", lambda *a, **k: '[{"skip_reason":"No stated route"}]')
    monkeypatch.setattr(grading, "_invoke", lambda *a: pytest.fail("graded an abstention"))
    row = document(examples("lookup")[0][0])
    assert qagen.generate_for_document(
        qagen.PlanItem(row["publication_number"], "en", "process_retrieval"), [row],
        schema=SCHEMA, prompts=PACK, config=config(), generation_client=None, grading_client=None,
    ) == []


@pytest.mark.parametrize("mutate", [
    lambda item: [],
    lambda item: item,
    lambda item: [item] * 4,
    lambda item: [item, {"skip_reason": "Mixed skip"}],
    lambda item: [dict(item, answer_is_translation="false")],
    lambda item: [dict(item, anchor="not in question")],
    lambda item: [dict(item, question_type="material")],
    lambda item: [dict(item, question=None)],
    lambda item: [dict(item, extra="unexpected")],
    lambda item: [{key: value for key, value in item.items() if key != "evidence"}],
])
def test_malformed_generation_is_rejected_for_retry(mutate):
    with pytest.raises(ValueError):
        parse_candidates(mutate(examples("lookup")[0][0]), "lookup")


def test_source_identity_and_ordered_substring_metadata_are_checked():
    source = examples("source_finding")[0][0]
    with pytest.raises(ValueError, match="equal source_identifier"):
        parse_candidates([dict(source, answer="EP-WRONG")], "source_finding")
    with pytest.raises(ValueError, match="must be false"):
        parse_candidates([dict(source, answer_is_translation=True)], "source_finding")
    comparison = examples("comparison")[0][0]
    with pytest.raises(ValueError, match="appearance order"):
        parse_candidates([dict(comparison, comparison_entities=comparison["comparison_entities"][::-1])],
                         "comparison")


@pytest.mark.parametrize("plan_name", PLANS)
def test_all_plans_default_to_the_seven_personas_and_reject_old_modes(plan_name):
    row = document(examples("lookup")[0][0])
    context = SimpleNamespace(schema=SCHEMA, languages=SPEC.languages)
    args = SimpleNamespace(seed=42, questions=4, pool=1, modes=None, langs=["en"])
    kwargs = {"context": context, "source": SPEC.source("gp"),
              "grouped": {row["publication_number"]: [row]}, "args": args}
    assert {item.mode for item in PLANS[plan_name](**kwargs)} == set(MODES)
    args.modes = ["technical"]
    with pytest.raises(ValueError, match="Unknown chemistry modes"):
        PLANS[plan_name](**kwargs)


def test_best_selection_keeps_different_personas_for_the_same_document():
    rows = [{"publication_number": "EP-1234567-A1", "question_language": "en", "mode": mode,
             "total_score": score}
            for mode, score in [("lookup", 30), ("lookup", 40), ("conceptual", 35)]]
    assert {(row["mode"], row["total_score"]) for row in qagen.select_best(rows, SCHEMA)} == {
        ("lookup", 40), ("conceptual", 35),
    }


def test_legacy_default_parser_still_supports_semantic_generation(monkeypatch):
    # The shared parser previously referenced MODE_SEMANTIC without importing it.
    candidate = {"question": "Question?", "answer": "Answer", "framing": "solution"}
    monkeypatch.setattr(qagen, "chat", lambda *a, **k: json.dumps([candidate]))
    legacy = qagen.GenerationConfig("test", grading.GraderConfig("test"))
    assert qagen.generate_candidates(None, legacy, "prompt", "passage", "semantic") == [candidate]


def test_cli_generation_and_regrading_preserve_translation_and_replace_grade_audits(
    monkeypatch, tmp_path,
):
    from clir_bench import domains
    from clir_bench.cli import build_parser
    from clir_bench.cli import qac as cli
    from clir_bench.core.config import Settings
    from clir_bench.core.context import AppContext

    context = AppContext.build(Settings(
        project_root=tmp_path, data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports", cluster_dir=tmp_path / "cluster",
    ), SPEC)
    parser = build_parser(context, domains.load_module("chemistry"))
    # The second English example translates French evidence and has array metadata.
    candidate = examples("constraint_search")[1][0]
    assert candidate["answer_is_translation"] is True
    source = document(candidate)
    corpus.write_rows(context.workspace.corpus_csv("gp"), [source], tuple(source))
    monkeypatch.setattr(cli, "client_for", lambda model: None)
    monkeypatch.setattr(qagen, "chat", lambda *a, **k: json.dumps([candidate]))
    score = 5

    def grade(client, settings, prompt, content):
        assert "answer_is_translation: True" in content
        assert f"evidence_language: {candidate['evidence_language']}" in content
        assert candidate["constraints"][0] in content
        assert f"publication_number: {source['publication_number']}" in content
        keys = (grading.FAITHFULNESS_KEYS if prompt == PACK.faithfulness()
                else grading.rubric_keys(prompt))
        return json.dumps([dict.fromkeys(keys, score) | {"index": 0, "reason": f"Score {score}"}])

    monkeypatch.setattr(grading, "_invoke", grade)
    output = tmp_path / "generated.csv"
    args = parser.parse_args([
        "qac", "generate", "--source", "gp", "--langs", "en", "--modes", "constraint_search",
        "--questions", "1", "--limit", "1", "--output", str(output),
    ])
    assert args.handler(args, context) == 0
    saved = corpus.read_rows(output)
    assert len(saved) == 1
    assert saved[0]["total_score"] == "40"

    # Regrading must update stored raw responses, not retain the generator run's grades.
    score = 4
    regraded = tmp_path / "regraded.csv"
    args = parser.parse_args([
        "qac", "regrade", "--source", "gp", "--input", str(output), "--output", str(regraded),
    ])
    assert args.handler(args, context) == 0
    saved = corpus.read_rows(regraded)[0]
    assert saved["total_score"] == "32"
    assert json.loads(saved["faithfulness_verifier_response_json"])["grounding"] == 4
    assert json.loads(saved["quality_verifier_response_json"])["focus"] == 4
    assert qagen.candidate_from_row(saved) == dict(
        candidate, mode="constraint_search", question_language="en",
    )
