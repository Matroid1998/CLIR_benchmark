"""New legal generation contracts survive routing, grading and CSV regrading."""

import csv
import io
import json
import re
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from clir_bench.core import grading, llm, prompt_registry
from clir_bench.domains.legal.qac import decider
from clir_bench.domains.legal.qac import generation_metadata as annotations
from test_legal_batch_replay_integration import Client, MemoryCheckpoint, case, response


@pytest.fixture(autouse=True)
def local_prompts(monkeypatch):
    monkeypatch.delenv("CLIR_PROMPT_MANIFEST", raising=False)
    monkeypatch.setenv("CLIR_PROMPT_SOURCE", "local")


@pytest.mark.parametrize("source", ["eurlex", "un"])
def test_all_supplied_prompt_variants_are_packaged_verbatim(source):
    _, generator, _, _, _ = case(source)
    document = Path(__file__).resolve().parents[1] / f"{source.upper()}_ALL_LANGUAGES.md"
    sections = re.split(r"^## .+ \((en|de|fr|es|zh)\)\s*$", document.read_text(), flags=re.MULTILINE)
    inventory = prompt_registry.local_legal_prompts()
    found = set()
    for language, section in zip(sections[1::2], sections[2::2]):
        for mode, prompt in re.findall(
            r"^### [^\n]+ — `(comparison|claim_verification|source_finding)`\n\n"
            r"```text\n(.*?)\n```", section, re.MULTILINE | re.DOTALL,
        ):
            assert generator.PROMPTS.generation(mode, language) == prompt.strip()
            key = f"{source}/generation/{mode}" + (f"/{language}" if language != "en" else "")
            assert inventory[key] == prompt.strip()
            found.add((mode, language))
    assert found == {(mode, lang) for mode in annotations.NEW_MODES
                     for lang in ("en", "de", "fr", "es", "zh")}


@pytest.mark.parametrize("source", ["eurlex", "un"])
@pytest.mark.parametrize("mode", annotations.NEW_MODES)
@pytest.mark.parametrize("backend", ["generator", "jev"])
def test_deciders_accept_new_modes(source, mode, backend):
    data = {"mode": mode, "reason": "The target establishes the required evidence."}
    if backend == "jev":
        criteria = json.loads(decider.prompt_text(source, backend))["questions"]["mode"]["criteria"]
        data = {"answers": {"mode": {"type": "choice", "choice": mode,
                "probabilities": {key: float(key == mode) for key in criteria}}}}
    assert decider.parse_decision(data, source, backend)["generation_mode"] == mode


@pytest.mark.parametrize("source", ["eurlex", "un"])
def test_previous_decider_probabilities_remain_replayable(source):
    modes = [mode for mode in decider.MODES[source] if mode not in annotations.NEW_MODES]
    data = {"answers": {"mode": {"type": "choice", "choice": "lookup",
            "probabilities": {key: float(key == "lookup") for key in (*modes, "skip")}}}}
    assert decider.parse_decision(data, source, "jev")["generation_mode"] == "lookup"


def candidate_for(source, mode, payload, translated):
    item = {
        "question": "How are officers, including auditors and inspectors treated in reporting?",
        "answer": payload.target.texts["en"], "anchor": "reporting",
        "question_type": "actor_body_or_procedure", "articles_involved": ["4"],
        "comparison_entities": ["officers, including auditors", "inspectors"],
        "comparison_aspect": "reporting duties", "claim": "inspectors report annually",
        "claim_status": "supported", "answer_is_translation": translated,
        "source_identifier": "Regulation (EU) 2000/1" if source == "eurlex" else payload.target.symbol,
        "source_article": "4", "evidence": payload.target.texts["en"],
        "evidence_is_translation": translated,
    }
    if mode == "source_finding":
        item.update(question="Which source establishes these reporting duties?",
                    answer=("Article 4 — " if source == "eurlex" else "") + item["source_identifier"],
                    question_type="source_finding")
    elif mode == "claim_verification":
        item["question"] = "Is the claim that inspectors report annually accurate for reporting?"
    return item


@pytest.mark.parametrize("source", ["eurlex", "un"])
@pytest.mark.parametrize("mode", annotations.NEW_MODES)
@pytest.mark.parametrize("translated", [False, True])
def test_generation_grading_csv_and_regrade_preserve_annotations(monkeypatch, source, mode, translated):
    batch, generator, target, payload, _ = case(source)
    target = replace(target, mode=mode)
    item = candidate_for(source, mode, payload, translated)
    # New verifier text is supplied separately. Exercise only the transport/schema
    # using a test rubric, so no unrelated mode's rubric is used in production.
    original = generator.PROMPTS
    template = grading._quality_output_example(original.quality("conceptual"))
    placeholder = "Test-only annotation transport rubric\nOUTPUT\n" + json.dumps(template)
    monkeypatch.setattr(generator, "PROMPTS", SimpleNamespace(
        generation=original.generation, faithfulness=original.faithfulness,
        quality=lambda *args: placeholder))
    calls = []

    def create(**kwargs):
        prompt = kwargs["messages"][0]["content"]
        body = kwargs["messages"][1]["content"]
        calls.append((prompt, body))
        if prompt == generator.PROMPTS.generation(mode, "en"):
            return response(json.dumps([item]))
        if prompt == generator.PROMPTS.faithfulness():
            assert f"Mode: {mode}" in body
            if mode == "source_finding":
                assert f"evidence: {item['evidence']}" in body
                assert f"source_identifier: {item['source_identifier']}" in body
            flag = "evidence_is_translation" if mode == "source_finding" else "answer_is_translation"
            assert f"{flag}: {translated}" in body
            return response(json.dumps([dict(index=0, **dict.fromkeys(grading.FAITHFULNESS_KEYS, 5))]))
        assert prompt == generator.PROMPTS.quality(mode)
        for key in annotations.parse_metadata(item, mode, eurlex=source == "eurlex"):
            assert key in body
        result = deepcopy(grading._quality_output_example(prompt))
        result["candidates"][0]["candidate_id"] = json.loads(body)["candidates"][0]["candidate_id"]
        result["candidates"][0]["scores"] = dict.fromkeys(grading.rubric_keys(prompt), 5)
        return response(json.dumps(result))

    monkeypatch.setattr(llm, "client_for", lambda _: Client(create))
    options = {"max_references": 6} if source == "eurlex" else {"context_chars": 30000}
    rows = batch.run_one(target, None, payload=payload, gen_model="gpt-test", grade_model="gpt-judge",
                         keep=3, checkpoint=MemoryCheckpoint(), retries=1, **options)
    assert len(rows) == 1 and rows[0]["grading_status"] == "completed", rows[0]["grading_error"]
    row = rows[0]
    assert row["question"] == item["question"] and row["answer"] == item["answer"]
    assert row["anchor"] == item["anchor"]
    expected = annotations.parse_metadata(item, mode, eurlex=source == "eurlex")
    assert annotations.restore_metadata(row, mode, eurlex=source == "eurlex") == expected
    assert row["claim"] == (item["claim"] if mode == "claim_verification" else "")
    assert row["source_identifier"] == (item["source_identifier"] if mode == "source_finding" else "")
    if source == "eurlex":
        assert row["articles_involved"] == "4"
        assert row["articles_involved_eli"] == payload.target.eli_id
    assert set(annotations.FIELDS) <= set(batch.FIELDS)
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=row)
    writer.writeheader()
    writer.writerows(rows)
    saved = list(csv.DictReader(io.StringIO(stream.getvalue())))
    calls.clear()
    regraded = batch.run_one(target, None, payload=payload, gen_model="gpt-test",
                             grade_model="gpt-judge", keep=3, existing_candidates=saved,
                             retries=1, **options)
    assert len(calls) == 2  # Regrading must not regenerate the question.
    assert regraded[0]["grading_status"] == "completed"
    assert regraded[0]["answer"] == item["answer"]
    assert annotations.restore_metadata(regraded[0], mode, eurlex=source == "eurlex") == expected
    candidates = (generator.parse_candidates([item], payload, mode) if source == "eurlex"
                  else generator.parse_candidates([item], mode))
    direct_row, = generator.rows_for(payload, candidates, mode=mode, language="en")
    assert annotations.restore_metadata(direct_row, mode, eurlex=source == "eurlex") == expected
