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
RUBRIC_VERSION = "chemistry-clir-exceptional-r1"


def verifier_response(prompt, candidates, score=4, *, metadata_status="pass"):
    """Use the supplied verifier contracts, including their audit diagnostics."""
    if prompt == PACK.faithfulness():
        return json.dumps([
            dict.fromkeys(grading.FAITHFULNESS_KEYS, score)
            | {"index": index, "reason": f"Supported at score {score}"}
            for index in range(len(candidates))
        ])
    keys = grading.rubric_keys(prompt)
    return json.dumps({
        "candidates": [
            {
                "index": index,
                "candidate_id": candidate.get("candidate_id"),
                "scores": dict.fromkeys(keys, score),
                "score_notes": {key: f"{key} assessed at score {score}" for key in keys},
                "checks": {"mode": "pass", "support": "pass", "metadata": metadata_status},
                "problems": ([] if metadata_status == "pass" else [
                    "metadata: The evidence has a harmless literal whitespace mismatch.",
                ]),
            }
            for index, candidate in enumerate(candidates)
        ],
        # The multi-candidate integration fixture deliberately repeats one need.
        "batch_diversity": "not_applicable" if len(candidates) == 1 else "fail",
    })


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
    assert all(f"qual_{key}" in qagen.output_fieldnames(SCHEMA, prompts=PACK, modes=MODES)
               for key in keys)


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
        payload = json.loads(content)
        calls.append(prompt)
        assert f"publication_number: {item.family}" in payload["passages"]
        assert candidate["evidence"] in payload["passages"]
        assert payload["candidates"] == [
            dict(candidate, mode=mode, question_language="en") for _ in range(count)
        ]
        return verifier_response(prompt, payload["candidates"])

    monkeypatch.setattr(qagen, "chat", generate)
    monkeypatch.setattr(grading, "_invoke", grade)
    generated = qagen.generate_for_document(
        item, [row], schema=SCHEMA, prompts=PACK, config=config(),
        generation_client=None, grading_client=None,
    )
    assert len(generated) == count
    assert calls == [PACK.faithfulness(), PACK.quality(mode)]
    fields = qagen.output_fieldnames(SCHEMA, prompts=PACK, modes=MODES)
    path = tmp_path / "results.csv"
    corpus.write_rows(path, [qagen.normalize_row(row, fields) for row in generated], fields)
    for saved in corpus.read_rows(path):
        restored = qagen.candidate_from_row(saved)
        assert restored == dict(candidate, mode=mode, question_language="en")
        assert saved["total_score"] == "32"
        assert saved["faith_overall"] == "12"
        assert saved["qual_overall"] == "20"
        assert saved["faithfulness_rubric_version"] == RUBRIC_VERSION
        assert saved["quality_rubric_version"] == RUBRIC_VERSION
        assert json.loads(saved["faithfulness_verifier_response_json"])["grounding"] == 4
        audit = json.loads(saved["quality_verifier_response_json"])
        assert audit["scores"] == dict.fromkeys(grading.rubric_keys(PACK.quality(mode)), 4)
        for key in audit["scores"]:
            assert saved[f"qual_{key}"] == "4"
        assert json.loads(saved["quality_score_notes_json"]) == audit["score_notes"]
        assert json.loads(saved["quality_checks_json"]) == audit["checks"]
        assert json.loads(saved["quality_problems_json"]) == []
        assert saved["quality_batch_diversity"] == ("not_applicable" if count == 1 else "fail")
        assert saved["quality_audit_status"] == "clear"
        assert all(saved[f"quality_{key}_status"] == "pass" for key in audit["checks"])


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


@pytest.mark.parametrize("value", [None, "", "not a score", "NaN", "Infinity", "-Infinity",
                                  float("nan"), float("inf"), -float("inf")])
def test_invalid_and_nonfinite_totals_never_win_best_selection(value):
    unscored = {"publication_number": "EP-1234567-A1", "question_language": "en",
                "mode": "lookup", "total_score": value}
    scored = dict(unscored, total_score="32")
    assert qagen.select_best([unscored], SCHEMA) == []
    assert qagen.select_best([unscored, scored], SCHEMA) == [scored]
    assert qagen.select_best([scored, unscored], SCHEMA) == [scored]


@pytest.mark.parametrize("stage", ["faithfulness", "quality"])
def test_unassessable_candidates_keep_null_totals_and_cannot_become_scored_winners(
    monkeypatch, tmp_path, stage,
):
    first = examples("lookup")[0][0]
    second = dict(first, question=first["question"] + " ")
    row = document(first)
    candidates = [first, second]
    monkeypatch.setattr(qagen, "chat", lambda *a, **k: json.dumps(candidates))

    def grade(client, settings, prompt, content):
        payload = json.loads(content)
        result = json.loads(verifier_response(prompt, payload["candidates"]))
        if stage == "faithfulness" and prompt == PACK.faithfulness():
            result[0]["grounding"] = None
            result[0]["reason"] = "The supplied source unit is truncated before decisive evidence."
        elif stage == "quality" and prompt == PACK.quality("lookup"):
            item = result["candidates"][0]
            key = grading.rubric_keys(prompt)[2]
            item["scores"][key] = None
            item["score_notes"][key] = "The supplied source unit omits decisive evidence."
            item["checks"]["support"] = "uncertain"
            item["problems"] = ["support: The full source unit is needed to assess this answer."]
        return json.dumps(result)

    monkeypatch.setattr(grading, "_invoke", grade)
    generated = qagen.generate_for_document(
        qagen.PlanItem(row["publication_number"], "en", "lookup"), [row],
        schema=SCHEMA, prompts=PACK, config=config(), generation_client=None, grading_client=None,
    )
    scored, unassessable = generated
    assert scored["question"] == second["question"]
    assert scored["total_score"] == 32 and scored["candidate_rank"] == 1
    assert unassessable["question"] == first["question"]
    assert unassessable["total_score"] is None
    assert unassessable["faith_overall" if stage == "faithfulness" else "qual_overall"] is None
    assert qagen.select_best(generated, SCHEMA) == [scored]
    assert qagen.select_best([unassessable], SCHEMA) == []

    fields = qagen.output_fieldnames(SCHEMA, prompts=PACK, modes=MODES)
    path = tmp_path / "unassessable.csv"
    corpus.write_rows(path, [qagen.normalize_row(unassessable, fields)], fields)
    saved = corpus.read_rows(path)
    assert saved[0]["total_score"] == ""
    assert qagen.select_best(saved, SCHEMA) == []


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
    score = 4
    metadata_status = "pass"

    def grade(client, settings, prompt, content):
        payload = json.loads(content)
        assert payload["candidates"] == [
            dict(candidate, mode="constraint_search", question_language="en"),
        ]
        assert f"publication_number: {source['publication_number']}" in payload["passages"]
        return verifier_response(prompt, payload["candidates"], score,
                                 metadata_status=metadata_status)

    monkeypatch.setattr(grading, "_invoke", grade)
    output = tmp_path / "generated.csv"
    args = parser.parse_args([
        "qac", "generate", "--source", "gp", "--langs", "en", "--modes", "constraint_search",
        "--questions", "1", "--limit", "1", "--output", str(output),
    ])
    assert args.handler(args, context) == 0
    saved = corpus.read_rows(output)
    assert len(saved) == 1
    assert saved[0]["total_score"] == "32"
    assert saved[0]["quality_audit_status"] == "clear"

    # Simulate an input exported by an older rubric: regrading clears old metrics.
    saved[0]["qual_focus"] = "5"
    saved[0]["qual_failure_type"] = "obsolete rubric diagnosis"
    corpus.write_rows(output, saved, tuple(saved[0]))

    # Regrading must update stored raw responses, not retain the generator run's grades.
    score = 3
    metadata_status = "fail"
    regraded = tmp_path / "regraded.csv"
    args = parser.parse_args([
        "qac", "regrade", "--source", "gp", "--input", str(output), "--output", str(regraded),
    ])
    assert args.handler(args, context) == 0
    saved = corpus.read_rows(regraded)[0]
    assert saved["total_score"] == "24"
    assert saved["faithfulness_rubric_version"] == RUBRIC_VERSION
    assert saved["quality_rubric_version"] == RUBRIC_VERSION
    assert json.loads(saved["faithfulness_verifier_response_json"])["grounding"] == 3
    audit = json.loads(saved["quality_verifier_response_json"])
    assert audit["scores"] == dict.fromkeys(grading.rubric_keys(PACK.quality("constraint_search")), 3)
    assert json.loads(saved["quality_score_notes_json"]) == audit["score_notes"]
    assert json.loads(saved["quality_checks_json"]) == audit["checks"]
    assert json.loads(saved["quality_problems_json"]) == audit["problems"]
    assert saved["quality_metadata_status"] == "fail"
    assert saved["quality_audit_status"] == "repair"
    assert saved["quality_batch_diversity"] == "not_applicable"
    assert saved["qual_focus"] == ""
    assert saved["qual_failure_type"] == ""
    assert qagen.candidate_from_row(saved) == dict(
        candidate, mode="constraint_search", question_language="en",
    )
