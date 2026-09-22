"""Offline checks for exact replay, billable calls and auditable generator output."""

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from openai.types.chat import ChatCompletion

from clir_bench.core.llm import chat
from clir_bench.domains.legal.qac import batch_recording
from clir_bench.domains.legal.qac.batch_recording import (
    GenerationRecorder,
    RunState,
    messages_sha256,
    read_run_metadata,
)

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


def test_interruption_stops_new_stages_without_spending_their_attempt_budget(tmp_path):
    from clir_bench.domains.legal.qac.batch_recording import RunState

    calls = []
    with RunState(tmp_path / "run.sqlite") as state:
        checkpoint = state.checkpoint("document", retries=1)
        checkpoint.run("generation", lambda: calls.append("generation") or ["question"])
        state.cancelled.set()
        with pytest.raises(InterruptedError):
            checkpoint.run("quality", lambda: calls.append("quality") or [5])
    assert calls == ["generation"]
    with RunState(tmp_path / "run.sqlite") as state:
        checkpoint = state.checkpoint("document", retries=1)
        assert checkpoint.run("generation", lambda: pytest.fail("generation repeated")) == ["question"]
        assert checkpoint.run("quality", lambda: calls.append("quality") or [5]) == [5]
    assert calls == ["generation", "quality"]


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


def test_single_file_replay_does_not_reconsume_a_response_after_interruption(tmp_path):
    from clir_bench.domains.legal.qac.batch_recording import RunState

    cache = cache_file(tmp_path, [cache_row(body("first response")), cache_row(body("second response"))])
    run = tmp_path / "run" / "run.sqlite"
    transport = fake_client(lambda **kwargs: pytest.fail("cache should avoid provider calls"))
    with RunState(run) as state:
        state.load_replay(cache, [MODEL])
        checkpoint = state.checkpoint("document", retries=2)
        client = checkpoint.client("generation", MODEL, transport)

        def interrupted_parse():
            assert chat(client, MODEL, MESSAGES) == "first response"
            raise KeyboardInterrupt

        with pytest.raises(KeyboardInterrupt):
            checkpoint.run("generation", interrupted_parse)
    with RunState(run) as state:
        state.load_replay(cache, [MODEL])
        checkpoint = state.checkpoint("document", retries=2)
        client = checkpoint.client("generation", MODEL, transport)
        assert checkpoint.run("generation", lambda: chat(client, MODEL, MESSAGES)) == "second response"
    assert sorted(path.name for path in run.parent.iterdir()) == ["run.sqlite"]


def test_provider_error_in_successful_http_response_records_context_capacity(tmp_path):
    from clir_bench.domains.legal.qac.batch_recording import RunState

    response = ChatCompletion.model_validate(body(error={"message": "Maximum context length exceeded"}))
    with RunState(tmp_path / "run.sqlite") as state:
        client = state.checkpoint("document").client("generation", MODEL, fake_client(lambda **kw: response))
        client.chat.completions.create(model=MODEL, messages=MESSAGES)
        with state.transaction() as db:
            record = json.loads(db.execute("SELECT record FROM requests").fetchone()[0])
        assert record["context_capacity_exceeded"] is True


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


def _state_requests(state):
    with state.transaction() as db:
        return [json.loads(row[0]) for row in db.execute("SELECT record FROM requests ORDER BY rowid")]


def test_run_state_replays_completed_stages_after_reopening_without_provider_calls(tmp_path):
    path = tmp_path / "run.sqlite"
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return ChatCompletion.model_validate(body('[{"question":"Saved question"}]'))

    with RunState(path) as state:
        state.put("config", {"generator_model": [MODEL]})
        checkpoint = state.checkpoint("one-target")
        proxy = checkpoint.client("generation", MODEL, fake_client(create))
        value = checkpoint.run("generation", lambda: json.loads(chat(proxy, MODEL, MESSAGES)))
        assert value == [{"question": "Saved question"}]
        request, = _state_requests(state)
        assert request["usage"]["prompt_tokens"] == 21
        assert request["response"]["choices"][0]["message"]["content"] == '[{"question":"Saved question"}]'
        assert request["context_capacity_exceeded"] is None
        state.outcome("one-target", value)

    with RunState(path) as resumed:
        result = resumed.checkpoint("one-target").run(
            "generation", lambda: pytest.fail("A completed stage must not execute again"))
        assert result == value
        assert resumed.outcomes()[0]["rows"] == value
        assert len(_state_requests(resumed)) == 1
    assert len(calls) == 1
    assert read_run_metadata(tmp_path)["config"]["generator_model"] == [MODEL]
    assert {file.name for file in tmp_path.iterdir()} == {"run.sqlite"}


def test_run_state_failed_attempt_budget_survives_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(batch_recording.time, "sleep", lambda _: None)
    calls = []

    def fail():
        calls.append(1)
        raise ValueError("Malformed verifier response")

    for _ in range(2):
        with RunState(tmp_path / "run.sqlite") as state:
            with pytest.raises(RuntimeError, match="quality failed after 3 attempts"):
                state.checkpoint("same-task", retries=3).run("quality", fail)
            with state.transaction() as db:
                assert db.execute("SELECT attempts,status,value,error FROM stages").fetchone() == (
                    3, "failed", None, "ValueError: Malformed verifier response")
    assert len(calls) == 3


def test_run_state_interrupted_attempt_counts_toward_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(batch_recording.time, "sleep", lambda _: None)
    calls = []

    def interrupted():
        calls.append("interrupted")
        raise KeyboardInterrupt

    with RunState(tmp_path / "run.sqlite") as state, pytest.raises(KeyboardInterrupt):
        state.checkpoint("task").run("generation", interrupted)

    def fail():
        calls.append("failed")
        raise ValueError("Unusable output")

    with (
        RunState(tmp_path / "run.sqlite") as state,
        pytest.raises(RuntimeError, match="generation failed after 3 attempts"),
    ):
        state.checkpoint("task").run("generation", fail)
    assert calls == ["interrupted", "failed", "failed"]


@pytest.mark.parametrize("result", [object(), {"score": float("nan")}])
def test_run_state_unserializable_stage_results_are_failed_attempts(tmp_path, monkeypatch, result):
    monkeypatch.setattr(batch_recording.time, "sleep", lambda _: None)
    calls = []

    def malformed():
        calls.append(1)
        return result

    with RunState(tmp_path / "run.sqlite") as state:
        with pytest.raises(RuntimeError, match="after 3 attempts"):
            state.checkpoint("task").run("quality", malformed)
        with state.transaction() as db:
            attempts, status, value, error = db.execute("SELECT attempts,status,value,error FROM stages").fetchone()
        assert (attempts, status, value) == (3, "failed", None)
        assert error.startswith(("TypeError:", "ValueError:"))
    assert len(calls) == 3


def test_run_state_records_and_redacts_capacity_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(batch_recording.time, "sleep", lambda _: None)
    secret = "only-a-test-provider-credential"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)
    calls = []
    options = []

    def create(**kwargs):
        calls.append(kwargs)
        error = RuntimeError(f"maximum context length exceeded; {secret}; Bearer another-private-token")
        error.status_code = 400
        raise error

    client = fake_client(create, secret)

    def with_options(**kwargs):
        options.append(kwargs)
        return client

    client.with_options = with_options
    with RunState(tmp_path / "run.sqlite") as state:
        checkpoint = state.checkpoint("large-target")
        proxy = checkpoint.client("quality", MODEL, client)
        with pytest.raises(RuntimeError, match="after 3 attempts") as raised:
            checkpoint.run("quality", lambda: chat(proxy, MODEL, MESSAGES))
        assert secret not in str(raised.value)
        requests = _state_requests(state)
        assert len(requests) == 3
        assert all(record["context_capacity_exceeded"] is True for record in requests)
        assert all(record["status_code"] == 400 for record in requests)
        assert all(record["input_characters"] == sum(len(message["content"]) for message in MESSAGES) for record in requests)
        assert all("[REDACTED]" in record["error"] for record in requests)
        state.outcome("large-target", [], str(raised.value))
        assert state.outcomes()[0]["status"] == "failed"
        with state.transaction() as db:
            dump = "\n".join(db.iterdump())
        assert secret not in dump
        assert "another-private-token" not in dump
    assert len(calls) == 3
    assert options == [{"max_retries": 0, "timeout": 180}]
    assert {file.name for file in tmp_path.iterdir()} == {"run.sqlite"}


def test_run_state_excludes_simultaneous_writers_but_allows_read_only_metadata(tmp_path):
    path = tmp_path / "run.sqlite"
    with RunState(path) as state:
        state.put("status", "running")
        assert read_run_metadata(tmp_path) == {"status": "running"}
        with pytest.raises(ValueError, match="already active"):
            RunState(path)
    with RunState(path) as reopened:
        assert reopened.get("status") == "running"


def test_run_state_does_not_confuse_token_rate_limits_with_context_capacity(tmp_path):
    def create(**kwargs):
        error = RuntimeError("Too many tokens per minute; reduce the request rate")
        error.status_code = 429
        raise error

    with RunState(tmp_path / "run.sqlite") as state:
        proxy = state.checkpoint("task").client("generation", MODEL, fake_client(create))
        with pytest.raises(RuntimeError):
            chat(proxy, MODEL, MESSAGES)
        request, = _state_requests(state)
        assert request["status_code"] == 429
        assert request["context_capacity_exceeded"] is None


def test_read_only_metadata_missing_path_creates_nothing(tmp_path):
    missing = tmp_path / "absent-run" / "run.sqlite"
    with pytest.raises(sqlite3.OperationalError):
        read_run_metadata(missing)
    assert not missing.parent.exists()
    with pytest.raises(sqlite3.OperationalError):
        read_run_metadata(tmp_path)
    assert not list(tmp_path.iterdir())


def test_run_state_parallel_cases_share_one_database(tmp_path):
    path = tmp_path / "run.sqlite"
    with RunState(path) as state:
        def run(index):
            value = state.checkpoint(f"target-{index}").run("generation", lambda: [{"index": index}])
            state.outcome(f"target-{index}", value)
            return value

        with ThreadPoolExecutor(max_workers=5) as pool:
            outputs = list(pool.map(run, range(20)))
        assert len(outputs) == len(state.outcomes()) == 20
        with state.transaction() as db:
            assert db.execute("SELECT COUNT(*) FROM stages WHERE status='completed'").fetchone()[0] == 20
    assert {file.name for file in tmp_path.iterdir()} == {"run.sqlite"}
