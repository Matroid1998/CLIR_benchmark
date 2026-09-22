"""Replay goes through the existing legal parsers, graders, ranking and exports."""

import csv
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest
from openai.types.chat import ChatCompletion

from clir_bench.core import grading, llm, parallel
from clir_bench.domains.legal.qac import eurlex_batch as eb
from clir_bench.domains.legal.qac import eurlex_context as ec
from clir_bench.domains.legal.qac import eurlex_generate as eg
from clir_bench.domains.legal.qac import un_batch as ub
from clir_bench.domains.legal.qac import un_context as uc
from clir_bench.domains.legal.qac import un_generate as ug
from clir_bench.domains.legal.qac.batch_recording import GenerationRecorder, messages_sha256

GENERATOR = "test/generator"
GRADER = "test/grader"


def response(content, model=GENERATOR):
    return ChatCompletion.model_validate({
        "id": "saved-generation" if model == GENERATOR else "fake-grading",
        "object": "chat.completion", "created": 123, "model": model,
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
                  "cost": 0.01},
    })


class Client:
    api_key = "integration-test-placeholder"

    def __init__(self, create):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))
        self.options = []

    def with_options(self, **options):
        self.options.append(options)
        return self


def case(corpus):
    if corpus == "eurlex":
        target = eb.Target("eli:test:article4", "32000R0001", "4", 1, "one_ref", "lookup", "en")
        article = ec.ArticleUnit(target.eli_id, target.celex_id, "4",
                                 texts={"en": "Compliance officers must report annually."})
        reference = ec.ArticleUnit("eli:test:article3", target.celex_id, "3",
                                   texts={"en": "Auditors check annual compliance reports."})
        payload = ec.GenerationPayload(article, [reference], [],
                                       ec.render_payload(article, [reference], languages=("en",)))
        candidates = [
            {"question": "Who checks annual compliance reports?", "answer": "Auditors",
             "question_type": "definition_actor_or_procedure", "anchor": "compliance reports",
             "question_cited": "Under Regulation1, who checks annual compliance reports?",
             "instrument_short_name": None, "articles_involved": ["4"]},
            {"question": "How often must compliance officers report?", "answer": "annually",
             "question_type": "monitoring_or_reporting", "anchor": "compliance officers",
             "question_cited": "Under Regulation1, how often must compliance officers report?",
             "instrument_short_name": "null", "articles_involved": ["Article 3"]},
        ]
        return eb, eg, target, payload, candidates
    target = ub.Target("1994/s/res/example", "1994/s/res/example#0", 0, 1,
                       "resolution", "semantic", "en")
    block = uc.BlockUnit(
        block_id=target.block_id, doc_id=target.doc_id, symbol="S/RES/1(1994)",
        title="Exampleland mission", block_index=0, n_blocks=1, line_start=0, line_end=1,
        token_count=20, texts={"en": "Exampleland received support. Peacekeepers protected civilians."},
        in_range=True,
    )
    payload = uc.GenerationPayload(target=block, context_blocks=[], n_context_dropped=0,
                                   references=[], dropped_references=[], text=uc.render_payload(block, []))
    candidates = [
        {"question": "How did Exampleland benefit from international assistance during 1994?",
         "answer": "Exampleland received support", "framing": "stakeholder", "anchor": "Exampleland"},
        {"question": "How did peacekeepers respond to the Exampleland crisis during 1994?",
         "answer": "Peacekeepers protected civilians", "framing": "response", "anchor": "Exampleland"},
    ]
    return ub, ug, target, payload, candidates


@pytest.mark.parametrize("corpus", ["eurlex", "un"])
def test_cached_run_one_uses_existing_parse_grade_rank_and_rows(tmp_path, monkeypatch, corpus):
    batch, generator, target, payload, candidates = case(corpus)
    messages = generator.build_messages(payload, target.mode, target.language)
    body = response("```json\n" + json.dumps(candidates) + "\n```").model_dump()
    cache = tmp_path / "cache.jsonl"
    cache.write_text(json.dumps({"model": GENERATOR, "messages_sha256": messages_sha256(messages),
                                 "response": body, "source_request_id": "original-request"}) + "\n")
    recorder = GenerationRecorder(cache, tmp_path / "recorded", GENERATOR)
    generator_client = Client(lambda **kwargs: pytest.fail("cache hit contacted generator transport"))
    calls = []

    def grade_transport(**kwargs):
        calls.append(kwargs)
        assert kwargs["model"] == GRADER
        prompt = kwargs["messages"][0]["content"]
        if prompt == generator.PROMPTS.faithfulness("batch"):
            keys = grading.FAITHFULNESS_KEYS
        else:
            assert prompt == generator.PROMPTS.quality(target.mode, "batch")
            keys = grading.rubric_keys(prompt) or grading.quality_keys(target.mode)
        return response(json.dumps([dict(index=index, **{key: score for key in keys})
                                    for index, score in enumerate((2, 5))]), model=GRADER)

    grader_client = Client(grade_transport)
    monkeypatch.setattr(llm, "client_for", lambda model: generator_client if model == GENERATOR else grader_client)
    parsed_calls = []
    original_parse = generator.parse_candidates

    def observe_parse(*args, **kwargs):
        parsed_calls.append(args[0])
        return original_parse(*args, **kwargs)

    monkeypatch.setattr(generator, "parse_candidates", observe_parse)
    builds = []

    def build(*args, **kwargs):
        builds.append((args, kwargs))
        return payload

    options = {"max_references": 6} if corpus == "eurlex" else {"context_chars": 30000}
    rows = batch.run_one(target, SimpleNamespace(build=build), gen_model=GENERATOR,
                         grade_model=GRADER, keep=3, generation_recorder=recorder, **options)

    assert parsed_calls == [candidates]
    assert len(builds) == 1 and builds[0][1]["languages"] == ("en",)
    assert generator_client.options == [{"max_retries": 0, "timeout": 180}]
    assert grader_client.options == []  # The grader was not wrapped in the generator recorder.
    assert len(calls) == 2
    assert all(call["messages"][1]["content"].startswith(payload.text) for call in calls)
    assert all(candidates[0]["question"] in call["messages"][1]["content"] for call in calls)
    assert [row["question"] for row in rows] == [candidates[1]["question"], candidates[0]["question"]]
    assert rows[0]["faith_grounding"] == 5
    assert rows[0]["total_score"] > rows[1]["total_score"]
    assert all(set(row) <= set(batch.FIELDS) for row in rows)
    if corpus == "eurlex":
        # These transformations prove the normal EUR-Lex parser ran on replay.
        assert rows[0]["articles_involved"] == "4,3"
        assert rows[0]["instrument_short_name"] == ""
        assert rows[0]["target_article_id"] == target.eli_id
        assert payload.target.texts["en"] in rows[0]["target_article_text"]
        assert "Articles involved (declared): 4, 3" in calls[0]["messages"][1]["content"]
    else:
        assert rows[0]["framing"] == "response" and rows[0]["question_type"] == ""
        assert rows[0]["anchor"] == "Exampleland"
        assert payload.target.texts["en"] in rows[0]["target_block_text"]
        best, rejected = ub.pick_best({(target.block_id, target.mode, target.language): rows})
        assert best == rows[:1] and rejected == 0
    records = [json.loads(line) for line in (tmp_path / "recorded" / "generation_attempts.jsonl").open()]
    assert len(records) == 1
    recorded = records[0]
    assert recorded["cached"] and recorded["source_request_id"] == "original-request"
    assert recorded["context"]["corpus"] == corpus
    assert recorded["context"]["target_id"] == (target.eli_id if corpus == "eurlex" else target.block_id)
    assert recorded["context"]["mode"] == target.mode and recorded["context"]["language"] == "en"
    assert recorded["messages_sha256"] == messages_sha256(messages)
    assert recorded["usage"]["provider_cost"] == 0


@pytest.mark.parametrize("corpus", ["eurlex", "un"])
def test_cached_skip_still_uses_parser_and_does_not_grade(tmp_path, monkeypatch, corpus):
    batch, generator, target, payload, _ = case(corpus)
    messages = generator.build_messages(payload, target.mode, target.language)
    cache = tmp_path / "cache.jsonl"
    cache.write_text(json.dumps({"model": GENERATOR, "messages_sha256": messages_sha256(messages),
                                 "response": response('[{"skip_reason":"no qualifying content"}]').model_dump()}) + "\n")
    recorder = GenerationRecorder(cache, tmp_path / "recorded", GENERATOR)
    client = Client(lambda **kwargs: pytest.fail("skip called a live generator or a grader"))
    monkeypatch.setattr(llm, "client_for", lambda _: client)
    options = {"max_references": 6} if corpus == "eurlex" else {"context_chars": 30000}
    assert batch.run_one(target, SimpleNamespace(build=lambda *a, **kw: payload),
                         gen_model=GENERATOR, grade_model=GRADER, keep=3,
                         generation_recorder=recorder, **options) == []


@pytest.mark.parametrize("corpus", ["eurlex", "un"])
def test_existing_cli_preserves_same_source_across_modes_languages_and_outcomes(tmp_path, monkeypatch, corpus):
    batch, _, first, _, _ = case(corpus)
    second_mode = "fact_pattern" if corpus == "eurlex" else "descriptive"
    targets = [first, replace(first, mode=second_mode), replace(first, language="fr")]
    manifest, out = tmp_path / "targets.json", tmp_path / f"qac_{corpus}_test_model.csv"
    batch.write_targets(manifest, targets)
    monkeypatch.setattr("sys.argv", ["batch", "--targets-in", str(manifest), "--out", str(out),
                                     "--gen-model", GENERATOR, "--grade-model", GRADER])
    monkeypatch.setattr(batch, "load_env", lambda: None)
    monkeypatch.setattr(llm, "client_for", lambda _: Client(lambda **kw: pytest.fail("unexpected network call")))
    monkeypatch.setattr(parallel, "run_tasks", lambda targets, fn, **kw: map(fn, targets))
    if corpus == "eurlex":
        unit = ec.ArticleUnit(first.eli_id, first.celex_id, first.article_number,
                              texts={"en": "Source", "fr": "Source française"})
        monkeypatch.setattr(batch.ctx, "ArticleIndex", lambda: SimpleNamespace(by_eli={first.eli_id: unit}))
    else:
        index = SimpleNamespace(docs={first.doc_id: {"n_blocks": first.n_blocks}}, incomplete=None,
                                preload_translations=lambda *a: None)
        monkeypatch.setattr(batch.ctx, "BlockIndex", lambda **kw: index)
        monkeypatch.setattr(batch, "_cited_doc_ids", lambda *a: set())

    def row_for(target, index, **kwargs):
        row = {"mode": target.mode, "question_language": target.language,
               "question": f"{target.mode}/{target.language}", "answer": "Source",
               "stratum": target.stratum, "faith_grounding": 5}
        if corpus == "eurlex":
            row.update(celex_id=target.celex_id, target_article_number=target.article_number,
                       multi_article=False, cross_act=False)
        else:
            row.update(block_id=target.block_id)
        return [row]

    monkeypatch.setattr(batch, "run_one", row_for)
    batch.main()
    with out.with_name(out.stem + "_best.csv").open(newline="") as stream:
        best = list(csv.DictReader(stream))
    assert len(best) == 3
    assert {(row["mode"], row["question_language"]) for row in best} == {
        (target.mode, target.language) for target in targets}
    outcomes = [json.loads(line) for line in out.with_suffix(".outcomes.jsonl").open()]
    assert len(outcomes) == 3 and all(row["status"] == "generated" for row in outcomes)
    assert all(row["generation_model"] == GENERATOR and row["grade_model"] == GRADER for row in outcomes)
    assert {(row["target"]["mode"], row["target"]["language"]) for row in outcomes} == {
        (target.mode, target.language) for target in targets}
