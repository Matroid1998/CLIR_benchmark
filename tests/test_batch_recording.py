"""Offline checks for exact replay, billable calls and auditable generator output."""

import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from openai.types.chat import ChatCompletion

from clir_bench.core.llm import chat
from clir_bench.domains.legal.qac.batch_recording import GenerationRecorder, messages_sha256

MODEL = "~openai/example"
MESSAGES = [{"role": "system", "content": "Generate a question."},
            {"role": "user", "content": "Une disposition légale."}]


def body(content="[]", **updates):
    response = {"id": "original-response", "object": "chat.completion", "created": 123,
                "model": "openai/resolved-alias", "choices": [{"index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": content}}],
                "usage": {"prompt_tokens": 21, "completion_tokens": 8, "total_tokens": 29,
                          "cost": 0.0123, "completion_tokens_details": {"reasoning_tokens": 3}}}
    response.update(updates)
    return response


def fake_client(create, key="test-key-never-persist-this"):
    return SimpleNamespace(api_key=key, chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def records(directory, name="generation_attempts.jsonl"):
    return [json.loads(line) for line in (directory / name).read_text().splitlines()]


def cache_row(response=None, **updates):
    row = {"model": MODEL, "messages_sha256": messages_sha256(MESSAGES),
           "response": response or body(), "source_request_id": "old-request",
           "source_path": "old/raw.json", "original_settings": {"max_tokens": 12000},
           "original_seconds": 17.5}
    row.update(updates)
    return row


def cache_file(tmp_path, rows):
    path = tmp_path / "cache.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    return path


def test_hash_preserves_message_values_and_order_but_not_mapping_key_order():
    assert messages_sha256(MESSAGES) == messages_sha256([
        {"content": m["content"], "role": m["role"]} for m in MESSAGES])
    assert messages_sha256(MESSAGES) != messages_sha256(MESSAGES[::-1])
    changed = [*MESSAGES[:-1], {**MESSAGES[-1], "content": MESSAGES[-1]["content"] + " "}]
    assert messages_sha256(changed) != messages_sha256(MESSAGES)


def test_cache_replays_empty_json_without_network_and_preserves_original_accounting(tmp_path):
    path = cache_file(tmp_path, [cache_row()])
    original = path.read_bytes()
    directory = tmp_path / "records"
    recorder = GenerationRecorder(path, directory, MODEL)

    def unexpected(**kwargs):
        pytest.fail("cache hit must not call the provider")

    proxy = recorder.client(fake_client(unexpected), context={"corpus": "un", "target_id": "T1"})
    # Exercise the actual shared chat transport, including reasoning parameters.
    assert chat(proxy, MODEL, MESSAGES, reasoning_effort="medium", max_tokens=12000) == "[]"
    row, = records(directory)
    assert row["cached"] and row["source"] == "cache"
    assert row["usage"] == {"provider_cost": 0.0}
    assert row["original_usage"]["provider_cost"] == 0.0123
    assert row["original_usage"]["prompt_tokens"] == 21
    assert row["original_seconds"] == 17.5 and row["seconds_kind"] == "local_replay"
    assert row["source_request_id"] == "old-request"
    assert row["response_model"] == "openai/resolved-alias"  # aliases may resolve
    assert not row["settings_match"]
    assert row["context"]["target_id"] == "T1"
    assert json.loads((directory / row["raw_file"]).read_text())["choices"][0]["message"]["content"] == "[]"
    assert path.read_bytes() == original
    assert records(directory, "generation_requests.jsonl")[0]["request_id"] == row["request_id"]


def test_miss_forwards_original_kwargs_and_records_live_usage(tmp_path):
    calls = []
    response = ChatCompletion.model_validate(body('[{"question":"Live"}]'))

    def create(**kwargs):
        calls.append(kwargs)
        return response

    recorder = GenerationRecorder(None, tmp_path, MODEL)
    proxy = recorder.client(fake_client(create))
    kwargs = {"model": MODEL, "messages": MESSAGES, "max_tokens": 24000,
              "extra_body": {"reasoning": {"enabled": True}, "provider": {"sort": "latency"}}}
    assert proxy.chat.completions.create(**kwargs) is response
    assert calls == [kwargs]
    row, = records(tmp_path)
    assert not row["cached"] and row["usage"]["provider_cost"] == 0.0123
    assert row["usage"]["reasoning_tokens"] == 3
    assert row["request_settings"]["max_tokens"] == 24000
    assert "messages" not in row


@pytest.mark.parametrize("invalid", [
    body(choices=[{"index": 0, "finish_reason": "error", "error": {"code": 502},
                   "message": {"role": "assistant", "content": "[]"}}]),
    body(choices=[{"index": 0, "finish_reason": "length",
                   "message": {"role": "assistant", "content": "[]"}}]),
    body(error={"message": "provider error"}),
    body(choices=[]),
])
def test_failed_or_truncated_cache_is_not_replayed(tmp_path, invalid):
    path = cache_file(tmp_path, [cache_row(invalid)])
    recorder = GenerationRecorder(path, tmp_path / "records", MODEL)
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return ChatCompletion.model_validate(body())

    recorder.client(fake_client(create)).chat.completions.create(model=MODEL, messages=MESSAGES)
    assert len(calls) == 1
    assert recorder.cache_summary["loaded"] == 0
    assert len(recorder.cache_summary["ignored"]) == 1


def test_cache_is_model_specific_and_consumed_once_for_parser_retries(tmp_path):
    path = cache_file(tmp_path, [cache_row(model="other/model"), cache_row(body("not JSON"))])
    recorder = GenerationRecorder(path, tmp_path / "records", MODEL)
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return ChatCompletion.model_validate(body("[]"))

    proxy = recorder.client(fake_client(create))
    assert chat(proxy, MODEL, MESSAGES) == "not JSON"
    assert chat(proxy, MODEL, MESSAGES) == "[]"
    assert len(calls) == 1
    assert [r["cached"] for r in records(tmp_path / "records")] == [True, False]


def test_model_or_messages_mismatch_cannot_replay_cached_output(tmp_path):
    path = cache_file(tmp_path, [cache_row()])
    recorder = GenerationRecorder(path, tmp_path / "records", MODEL)
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return ChatCompletion.model_validate(body())

    proxy = recorder.client(fake_client(create))
    with pytest.raises(ValueError, match="original client for graders"):
        chat(proxy, "grader/model", MESSAGES)
    assert not calls
    chat(proxy, MODEL, [{"role": "user", "content": "Different source"}])
    assert len(calls) == 1


def test_errors_propagate_unchanged_and_records_do_not_expose_credentials(tmp_path, monkeypatch):
    key = "private-credential-for-test-only"
    monkeypatch.setenv("OPENROUTER_API_KEY", key)
    error = RuntimeError(f"failed with {key}; Authorization: Bearer another-private-token")

    def create(**kwargs):
        raise error

    recorder = GenerationRecorder(None, tmp_path, MODEL)
    proxy = recorder.client(fake_client(create, key), context={"api_key": key, "target_id": "T"})
    with pytest.raises(RuntimeError) as caught:
        proxy.chat.completions.create(model=MODEL, messages=MESSAGES,
                                      extra_headers={"Authorization": key},
                                      extra_body={"api_key": key, "reasoning": {"effort": "medium"}})
    assert caught.value is error
    row, = records(tmp_path)
    assert row["status"] == "error" and row["error_type"] == "RuntimeError"
    assert "[REDACTED]" in row["error"]
    text = "".join(path.read_text() for path in tmp_path.glob("*.jsonl"))
    assert key not in text and "another-private-token" not in text
    assert "extra_headers" not in text


def test_concurrent_calls_record_distinct_raw_responses(tmp_path):
    def create(**kwargs):
        return ChatCompletion.model_validate(body(kwargs["messages"][-1]["content"]))

    recorder = GenerationRecorder(None, tmp_path, MODEL)
    proxy = recorder.client(fake_client(create))
    with ThreadPoolExecutor(max_workers=5) as pool:
        outputs = list(pool.map(lambda i: chat(proxy, MODEL, [{"role": "user", "content": str(i)}]), range(20)))
    assert outputs == [str(i) for i in range(20)]
    rows = records(tmp_path)
    assert len(rows) == len({r["request_id"] for r in rows}) == 20
    assert len(records(tmp_path, "generation_requests.jsonl")) == 20
    assert len(list((tmp_path / "raw").glob("*.json"))) == 20
