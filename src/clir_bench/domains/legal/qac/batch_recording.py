"""Optional generation transport recording for the existing legal batch pipelines.

Wrap only the generator client; generation, parsing, grading and retry decisions
stay in the existing pipeline. A cache is an explicitly supplied, read-only JSONL
manifest, not a replacement generation workflow. Each cached response is replayed
at most once per recorder instance, so a parser retry can proceed to a later cached
attempt or the live provider instead of repeating one malformed answer forever.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import threading
import time
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from openai.types.chat import ChatCompletion

from clir_bench.core.llm import extract_usage


def messages_sha256(messages: Sequence[Mapping[str, Any]]) -> str:
    """Hash exact message values, independent of object-key insertion order."""
    encoded = json.dumps(list(messages), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


_SECRET_FIELDS = {
    "api_key", "apikey", "authorization", "x_api_key", "access_token",
    "refresh_token", "token", "password", "secret", "client_secret",
}
_SETTING_FIELDS = {
    "reasoning_effort", "max_tokens", "max_completion_tokens", "temperature",
    "top_p", "seed", "frequency_penalty", "presence_penalty", "stop",
    "response_format", "extra_body", "n", "stream",
}
_CONTEXT_FIELDS = {
    "corpus", "mode", "language", "doc_id", "target_id", "block_id", "eli_id",
    "slot_id", "sample_id", "run_id", "stage",
}


def _redact(value: Any, secrets: set[str]) -> Any:
    if isinstance(value, dict):
        return {str(key): "[REDACTED]" if str(key).lower().replace("-", "_")
                in _SECRET_FIELDS else _redact(item, secrets)
                for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, str):
        for secret in sorted(secrets, key=len, reverse=True):
            value = value.replace(secret, "[REDACTED]")
        value = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", value)
        return re.sub(r"\bsk-[A-Za-z0-9_-]{8,}\b", "[REDACTED]", value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _redact(str(value), secrets)


def _successful_response(body: dict) -> bool:
    choices = body.get("choices") or []
    if body.get("error") or not choices or not isinstance(choices[0], dict):
        return False
    choice = choices[0]
    message = choice.get("message") or {}
    return (not choice.get("error") and choice.get("finish_reason") == "stop"
            and isinstance(message.get("content"), str) and bool(message["content"].strip()))


def _capacity_error(message: str, status_code=None) -> bool | None:
    if status_code == 429 or re.search(r"per minute|per second|rate.limit|\bTPM\b", message, re.IGNORECASE):
        return None
    if re.search(r"context[_ ]length[_ ]exceeded|maximum context length|exceeds?.{0,40}context|"
                 r"too many (?:input )?tokens|input.{0,30}too long", message, re.IGNORECASE):
        return True
    return None


class GenerationRecorder:
    """Record generator requests and optionally replay exact cached inputs.

    Cache rows contain ``model``, ``messages_sha256``, ``response`` (the raw
    completion object), and optional ``source_request_id``, ``source_path``,
    ``original_settings``, ``original_usage``, ``original_seconds``. Matching uses
    the exact requested model ID and exact canonical messages, not settings.
    Settings differences are explicitly recorded on replay. Aliases and paid/free
    endpoint IDs are never treated as interchangeable cache keys.

    ``client(real_client, context=...)`` supports the synchronous
    ``client.chat.completions.create(**kwargs)`` interface used by core.llm.chat.
    It forwards live kwargs unchanged and raises the original provider exception.
    It does not retry, grade candidates or append to the supplied cache manifest.
    """

    def __init__(self, cache_path: Path | None, records_dir: Path | None, model: str):
        self.model = model
        self.records_dir = Path(records_dir) if records_dir is not None else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._cache: dict[tuple[str, str], deque[dict]] = defaultdict(deque)
        self.cache_summary: dict[str, Any] = {"path": str(cache_path) if cache_path else None,
                                             "loaded": 0, "ignored": []}
        self._secrets = {value for key, value in os.environ.items()
                         if value and any(part in key.upper() for part in
                                          ("API_KEY", "ACCESS_TOKEN", "AUTH_TOKEN", "SECRET"))}
        if cache_path is not None:
            self._load_cache(Path(cache_path))

    def _load_cache(self, path: Path) -> None:
        data = path.read_bytes()
        self.cache_summary["sha256"] = hashlib.sha256(data).hexdigest()
        for line_number, line in enumerate(data.splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict) or row.get("model") != self.model:
                    continue
                digest = row.get("messages_sha256")
                if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                    raise ValueError("invalid messages_sha256")
                body = row.get("response")
                if not isinstance(body, dict) or not _successful_response(body):
                    raise ValueError("response is not a completed non-error text response")
                ChatCompletion.model_validate(body)
                row["_cache_line"] = line_number
                self._cache[(self.model, digest)].append(row)
                self.cache_summary["loaded"] += 1
            except (ValueError, TypeError, AttributeError) as exc:
                self.cache_summary["ignored"].append({"line": line_number,
                                                      "reason": _redact(str(exc), self._secrets)})

    def client(self, real_client: Any, *, context: dict | None = None) -> Any:
        """Return a generator-only proxy bound to optional source identifiers."""
        key = getattr(real_client, "api_key", None)
        if isinstance(key, str) and key:
            with self._lock:
                self._secrets.add(key)
        context = {key: value for key, value in (context or {}).items()
                   if key in _CONTEXT_FIELDS}

        def create(**kwargs):
            return self._create(real_client, context, kwargs)

        return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    def _append(self, record: dict, filename: str = "generation_attempts.jsonl") -> None:
        with self._lock:
            safe = _redact(record, self._secrets.copy())
            with (self.records_dir / filename).open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(safe, ensure_ascii=False) + "\n")

    def _save_response(self, request_id: str, body: dict) -> str:
        path = self.records_dir / "raw" / (request_id + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            safe = _redact(body, self._secrets.copy())
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(safe, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        temporary.replace(path)
        return str(path.relative_to(self.records_dir))

    def _create(self, real_client: Any, context: dict, kwargs: dict) -> Any:
        if kwargs.get("model") != self.model:
            raise ValueError("GenerationRecorder is bound to the generator model; use the original client for graders")
        if kwargs.get("stream"):
            raise ValueError("GenerationRecorder supports non-streaming generation only")
        digest = messages_sha256(kwargs["messages"])
        started = time.monotonic()
        request_id = uuid4().hex
        settings = {key: value for key, value in kwargs.items() if key in _SETTING_FIELDS}
        record = {"request_id": request_id, "model": self.model,
                  "timestamp": datetime.now(timezone.utc).isoformat(),
                  "messages_sha256": digest, "request_settings": settings, "context": context}
        with self._lock:
            entries = self._cache.get((self.model, digest))
            cached = entries.popleft() if entries else None
        self._append({**record, "status": "started", "cached": cached is not None,
                      "source": "cache" if cached is not None else "live"},
                     "generation_requests.jsonl")
        if cached is not None:
            response = ChatCompletion.model_validate(cached["response"])
            record.update(cached=True, source="cache", status="response",
                          source_request_id=cached.get("source_request_id"),
                          source_path=cached.get("source_path"),
                          original_settings=cached.get("original_settings"),
                          original_usage=cached.get("original_usage") or extract_usage(response),
                          original_seconds=cached.get("original_seconds"),
                          settings_match=cached.get("original_settings") == settings,
                          usage={"provider_cost": 0.0}, seconds_kind="local_replay")
        else:
            record.update(cached=False, source="live", seconds_kind="live_request")
            try:
                response = real_client.chat.completions.create(**kwargs)
            except Exception as exc:
                record.update(status="error", seconds=round(time.monotonic() - started, 6),
                              error_type=type(exc).__name__, status_code=getattr(exc, "status_code", None),
                              error=str(exc))
                self._append(record)
                raise
            record.update(status="response", usage=extract_usage(response))
        body = response.model_dump()
        record.update(seconds=round(time.monotonic() - started, 6),
                      raw_file=self._save_response(request_id, body),
                      response_id=body.get("id"), response_model=body.get("model"),
                      finish_reason=(body.get("choices") or [{}])[0].get("finish_reason"),
                      provider_error=bool(body.get("error") or any(c.get("error")
                                          or c.get("finish_reason") == "error"
                                          for c in body.get("choices", []))))
        self._append(record)
        return response


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


class RunState:
    """One transactional file for a legal run, including interrupted attempts.

    Completed stage values are replayed without a model call. The attempt budget
    survives interruption and resume; retrying a failed run cannot reset it.
    Historical imports can use metadata without inventing completed stages.
    """

    def __init__(self, path: Path):
        import fcntl

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("a+b")
        try:
            fcntl.flock(self._file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._file.close()
            raise ValueError(f"run is already active: {self.path.parent}") from None
        self._lock = threading.RLock()
        self._verification_locks: dict[str, Any] = {}
        self.cancelled = threading.Event()
        self.replay: dict[str, GenerationRecorder] = {}
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS stages (
                task TEXT, stage TEXT, attempts INTEGER NOT NULL, status TEXT NOT NULL,
                value TEXT, error TEXT, PRIMARY KEY(task, stage));
            CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY, task TEXT, stage TEXT, record TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS outcomes (
                task TEXT PRIMARY KEY, status TEXT NOT NULL, rows TEXT NOT NULL, error TEXT);
            CREATE TABLE IF NOT EXISTS verification_cache (
                key TEXT PRIMARY KEY, value TEXT NOT NULL, source_task TEXT, source_position INTEGER);
            CREATE TABLE IF NOT EXISTS verification_reuse (
                task TEXT, stage TEXT, position INTEGER, cache_key TEXT, reused INTEGER,
                PRIMARY KEY(task, stage, position));
        """)
        self._secrets = {value for key, value in os.environ.items() if value and
                         any(part in key.upper() for part in
                             ("API_KEY", "ACCESS_TOKEN", "AUTH_TOKEN", "SECRET"))}

    def close(self) -> None:
        self._db.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @contextmanager
    def transaction(self):
        with self._lock, self._db:
            yield self._db

    def get(self, key: str, default: Any = None) -> Any:
        with self.transaction() as db:
            row = db.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def put(self, key: str, value: Any) -> None:
        with self.transaction() as db:
            db.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", (key, _json(value)))

    def outcome(self, task: str, rows: list[dict], error: str = "") -> None:
        status = "failed" if error else ("completed" if rows else "no_candidates")
        with self.transaction() as db:
            db.execute("INSERT OR REPLACE INTO outcomes VALUES (?,?,?,?)",
                       (task, status, _json(rows), _redact(error, self._secrets)))

    def outcomes(self) -> list[dict]:
        with self.transaction() as db:
            records = db.execute("SELECT task,status,rows,error FROM outcomes ORDER BY task").fetchall()
        return [{"task": t, "status": s, "rows": json.loads(r), "error": e} for t, s, r, e in records]

    def checkpoint(self, task: str, *, retries: int = 3):
        return StageCheckpoint(self, task, retries)

    def load_replay(self, path: Path, models: Sequence[str]) -> None:
        self.replay = {model: GenerationRecorder(path, None, model) for model in models}
        with self.transaction() as db:
            previous = [json.loads(row[0]) for row in db.execute(
                "SELECT record FROM requests WHERE stage='generation'")]
        used = {(record.get("model"), record.get("cache_line")) for record in previous if record.get("cached")}
        for model, recorder in self.replay.items():
            for key, entries in recorder._cache.items():
                recorder._cache[key] = deque(row for row in entries if (model, row["_cache_line"]) not in used)


def read_run_metadata(path: Path) -> dict:
    """Read without creating an empty database or taking the writer's lock."""
    path = Path(path)
    path = path / "run.sqlite" if path.is_dir() else path
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        return {key: json.loads(value) for key, value in db.execute("SELECT key,value FROM metadata")}


class StageCheckpoint:
    def __init__(self, state: RunState, task: str, retries: int):
        if retries < 1:
            raise ValueError("retries is the total attempt count and must be positive")
        self.state, self.task, self.retries = state, task, retries

    def run(self, stage: str, fn):
        with self.state.transaction() as db:
            saved = db.execute("SELECT attempts,status,value,error FROM stages WHERE task=? AND stage=?",
                               (self.task, stage)).fetchone()
        attempts, status, value, error = saved or (0, "pending", None, "")
        if status == "completed":
            return json.loads(value)
        while attempts < self.retries:
            if self.state.cancelled.is_set():
                raise InterruptedError("run interrupted before the next model attempt")
            attempts += 1
            with self.state.transaction() as db:
                db.execute("INSERT OR REPLACE INTO stages VALUES (?,?,?,?,?,?)",
                           (self.task, stage, attempts, "running", None, None))
            try:
                result = fn()
                encoded = _json(result)
            except Exception as exc:  # noqa: BLE001 - parser and provider failures share the attempt budget
                error = _redact(f"{type(exc).__name__}: {exc}", self.state._secrets)
                with self.state.transaction() as db:
                    db.execute("UPDATE stages SET status='failed',error=? WHERE task=? AND stage=?",
                               (error, self.task, stage))
                if attempts < self.retries:
                    self.state.cancelled.wait(min(2 ** (attempts - 1), 8))
            else:
                with self.state.transaction() as db:
                    db.execute("UPDATE stages SET status='completed',value=? WHERE task=? AND stage=?",
                               (encoded, self.task, stage))
                return result
        raise RuntimeError(f"{stage} failed after {attempts} attempts: {error or 'interrupted attempt'}")

    def reuse_verification(self, stage, identity, candidates, grade):
        """Grade only unseen verifier inputs and restore each caller's identities.

        Serialize competing batches for the same verifier/context, while other
        documents still run concurrently. Only parsed, validated grades are cached.
        """
        scope = hashlib.sha256(_json([stage, identity]).encode()).hexdigest()
        keys = [hashlib.sha256(_json([scope, {k: v for k, v in candidate.items()
                if k not in ("candidate_id", "_candidate_index")}]).encode()).hexdigest()
                for candidate in candidates]
        with self.state._lock:
            lock = self.state._verification_locks.setdefault(scope, threading.Lock())
        with lock:
            cached = {}
            with self.state.transaction() as db:
                for key in dict.fromkeys(keys):
                    record = db.execute("SELECT value FROM verification_cache WHERE key=?", (key,)).fetchone()
                    if record:
                        cached[key] = json.loads(record[0])
            pending = {}
            for key, candidate in zip(keys, candidates):
                if key not in cached:
                    pending.setdefault(key, candidate)
            reused = set(cached)
            if pending:
                if self.state.cancelled.is_set():
                    raise InterruptedError("run interrupted before verification")
                values = grade(list(pending.values()))
                if len(values) != len(pending):
                    raise ValueError("Verifier returned a different number of grades than unique candidates")
                # Encode everything before the transaction: malformed results must
                # never leave a partially committed cache behind.
                encoded = [_json(value) for value in values]
                with self.state.transaction() as db:
                    for position, (key, value) in enumerate(zip(pending, encoded)):
                        db.execute("INSERT INTO verification_cache VALUES (?,?,?,?)",
                                   (key, value, self.task, position))
                        cached[key] = json.loads(value)
            changed_batch = len(pending) != len(candidates)
            result = []
            with self.state.transaction() as db:
                for position, (key, candidate) in enumerate(zip(keys, candidates)):
                    value = json.loads(_json(cached[key]))
                    response = value.get("_response")
                    if isinstance(response, dict):
                        if "index" in response:
                            response["index"] = position
                        if "candidate_id" in response:
                            response["candidate_id"] = candidate.get("candidate_id")
                    if changed_batch and "_batch_diversity" in value:
                        value["_batch_diversity"] = "not_evaluated"
                    db.execute("INSERT OR REPLACE INTO verification_reuse VALUES (?,?,?,?,?)",
                               (self.task, stage, position, key, int(key in reused)))
                    reused.add(key)
                    result.append(value)
            return result

    def decisions(self, request: dict) -> dict:
        """Record a native Decisions request and response without chat conversion."""
        from clir_bench.core.llm import OPENROUTER_DECISIONS_URL, decisions

        request_id, started = uuid4().hex, time.monotonic()
        record = {"model": request["model"], "timestamp": datetime.now(timezone.utc).isoformat(),
                  "endpoint": OPENROUTER_DECISIONS_URL, "request": request,
                  "messages": [], "request_settings": {}, "status": "running",
                  "input_characters": len(_json(request)), "context_capacity_exceeded": None}

        def save():
            with self.state.transaction() as db:
                db.execute("INSERT OR REPLACE INTO requests VALUES (?,?,?,?)",
                           (request_id, self.task, "decider",
                            _json(_redact(record, self.state._secrets))))

        save()
        try:
            response = decisions(request)
            usage = response.get("usage") or {}
            record.update(status="response", response=response,
                          usage={"prompt_tokens": usage.get("input_tokens"),
                                 "completion_tokens": usage.get("output_tokens"),
                                 "provider_cost": usage.get("cost")})
            return response
        except Exception as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            record.update(status="error", error_type=type(exc).__name__, error=str(exc),
                          status_code=status, context_capacity_exceeded=_capacity_error(str(exc), status))
            raise
        finally:
            record["seconds"] = round(time.monotonic() - started, 6)
            save()

    def client(self, stage: str, model: str, client: Any) -> Any:
        if hasattr(client, "with_options"):
            client = client.with_options(max_retries=0, timeout=180)
        key = getattr(client, "api_key", None)
        if isinstance(key, str) and key:
            self.state._secrets.add(key)

        def create(**kwargs):
            if kwargs.get("model") != model:
                raise ValueError("request model differs from the configured stage model")
            request_id, started = uuid4().hex, time.monotonic()
            record = {"model": model, "timestamp": datetime.now(timezone.utc).isoformat(),
                      "messages": kwargs["messages"], "messages_sha256": messages_sha256(kwargs["messages"]),
                      "request_settings": {k: v for k, v in kwargs.items() if k in _SETTING_FIELDS},
                      "input_characters": sum(len(str(m.get("content", ""))) for m in kwargs["messages"]),
                      "context_capacity_exceeded": None, "status": "running"}

            def save():
                with self.state.transaction() as db:
                    db.execute("INSERT OR REPLACE INTO requests VALUES (?,?,?,?)",
                               (request_id, self.task, stage,
                                _json(_redact(record, self.state._secrets))))

            save()
            try:
                cache = self.state.replay.get(model) if stage == "generation" else None
                cached = None
                if cache is not None:
                    with cache._lock:
                        matches = cache._cache.get((model, record["messages_sha256"]))
                        cached = matches.popleft() if matches else None
                if cached:
                    response = ChatCompletion.model_validate(cached["response"])
                    record.update(cached=True, source_path=cached.get("source_path"),
                                  cache_line=cached["_cache_line"],
                                  original_usage=cached.get("original_usage") or extract_usage(response),
                                  original_settings=cached.get("original_settings"),
                                  settings_match=cached.get("original_settings") == record["request_settings"])
                else:
                    response = client.chat.completions.create(**kwargs)
                record.update(status="response", response=response.model_dump(),
                              usage={"provider_cost": 0.0} if cached else extract_usage(response))
                body = record["response"]
                if body.get("error") or any(choice.get("error") or choice.get("finish_reason") == "error"
                                            for choice in body.get("choices", [])):
                    record["context_capacity_exceeded"] = _capacity_error(_json(body))
                return response
            except Exception as exc:
                message = str(exc)
                record.update(status="error", error_type=type(exc).__name__, error=message,
                              status_code=getattr(exc, "status_code", None))
                record["context_capacity_exceeded"] = _capacity_error(message, getattr(exc, "status_code", None))
                raise
            finally:
                record["seconds"] = round(time.monotonic() - started, 6)
                save()

        proxy = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        if stage in ("faithfulness", "quality"):
            proxy.reuse_verification = lambda identity, candidates, grade: self.reuse_verification(
                stage, identity, candidates, grade)
        return proxy


def export_traces(directory: Path) -> None:
    """Export every recorded call, retry and parsed stage without making model calls."""
    directory = Path(directory)
    with sqlite3.connect((directory / "run.sqlite").resolve().as_uri() + "?mode=ro", uri=True) as db:
        metadata = {key: json.loads(value) for key, value in db.execute("SELECT key,value FROM metadata")}
        calls = [{"request_id": i, "task_id": t, "stage": s, "record": json.loads(r)}
                 for i, t, s, r in db.execute(
                     "SELECT id,task,stage,record FROM requests "
                     "ORDER BY json_extract(record,'$.timestamp'),id")]
        stages = [{"task_id": t, "stage": s, "attempts": a, "status": status,
                   "parsed_output": json.loads(v) if v is not None else None, "error": e}
                  for t, s, a, status, v, e in db.execute(
                      "SELECT task,stage,attempts,status,value,error FROM stages ORDER BY task,stage")]
        outcomes = [{"task_id": t, "status": s, "rows": json.loads(r), "error": e}
                    for t, s, r, e in db.execute("SELECT task,status,rows,error FROM outcomes ORDER BY task")]
        reuse = []
        if db.execute("SELECT 1 FROM sqlite_master WHERE name='verification_reuse'").fetchone():
            reuse = [{"task_id": t, "stage": s, "candidate_index": p, "cache_key": k,
                      "reused": bool(r), "source_task_id": origin, "source_candidate_index": index}
                     for t, s, p, k, r, origin, index in db.execute(
                         "SELECT r.task,r.stage,r.position,r.cache_key,r.reused,c.source_task,c.source_position "
                         "FROM verification_reuse r JOIN verification_cache c ON c.key=r.cache_key "
                         "ORDER BY r.task,r.stage,r.position")]
    bundle = {"metadata": metadata, "calls": calls, "stages": stages, "outcomes": outcomes,
              "verification_reuse": reuse}
    capacities = metadata.get("context_capacity_reference", {}).get("model_context_tokens", {})
    inputs, generation_models = {}, {}
    for call in calls:
        record = call["record"]
        model = record["model"]
        observed = inputs.setdefault(model, {"calls": 0, "provider_errors": 0,
            "capacity_errors": 0, "max_input_characters": 0, "max_reported_prompt_tokens": None,
            "reference_context_tokens": capacities.get(model)})
        observed["calls"] += 1
        observed["provider_errors"] += record["status"] == "error"
        observed["capacity_errors"] += record.get("context_capacity_exceeded") is True
        observed["max_input_characters"] = max(observed["max_input_characters"], record.get("input_characters", 0))
        tokens = record.get("usage", {}).get("prompt_tokens")
        if tokens is not None:
            observed["max_reported_prompt_tokens"] = max(observed["max_reported_prompt_tokens"] or 0, tokens)
        if call["stage"] == "generation":
            generation_models[call["task_id"]] = model
    for observed in inputs.values():
        tokens, capacity = observed["max_reported_prompt_tokens"], observed["reference_context_tokens"]
        observed["reported_input_exceeds_reference_context"] = (
            tokens > capacity if tokens is not None and capacity is not None else None)
    overproduction = [{"task_id": stage["task_id"], "model": generation_models.get(stage["task_id"]),
                       "returned_candidates": len(stage["parsed_output"]), "prompt_maximum": 3}
                      for stage in stages if stage["stage"] == "generation"
                      and isinstance(stage["parsed_output"], list) and len(stage["parsed_output"]) > 3]
    bundle["diagnostics"] = {"inputs_by_model": inputs, "generation_overproduction": overproduction}

    def block(value, kind="text"):
        content = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        fence = "`" * max(4, 1 + max((len(run) for run in re.findall(r"`+", content)), default=0))
        return f"{fence}{kind}\n{content}\n{fence}"

    lines = ["# Legal question generation and grading: complete call trace",
             f"Run status: **{metadata.get('status', 'unknown')}**. Recorded calls: **{len(calls)}**.",
             (f"[Questions and grades]({metadata.get('output', 'results.csv')}) · "
             "[Full provider responses and run data](llm_calls.json) · Resumable state: `run.sqlite`."),
             ("Every recorded call, including retries, appears in chronological order. "
             "API status describes transport; stage status describes final parsing and validation. "
             "The JSON export retains every recorded provider response field. "
             "Any candidates beyond a requested quota remain in the raw outcomes."),
             "## Run configuration and source targets", block(metadata.get("config", {}), "json"),
             "## Run summary", block(metadata.get("summary", {}), "json"),
             "## Input capacity and generation diagnostics",
             ("Character counts are not token counts. Missing token usage or capacity remains unknown; "
             "provider capacity errors are recorded separately from rate limits and timeouts."),
             block(bundle["diagnostics"], "json")]
    table = ["| Task | Stage | Attempts | Final status | Error |", "|---|---|---:|---|---|"]
    for stage in stages:
        error = (stage["error"] or "").replace("|", "\\|").replace("\n", " ")
        table.append(f"| {stage['task_id']} | {stage['stage']} | {stage['attempts']} | "
                     f"{stage['status']} | {error} |")
    lines.extend(["## Final stage results", "\n".join(table)])
    if reuse:
        lines.extend(["## Shared verifier grades",
                      ("Reused candidate grades refer to the original task and request candidate index. "
                       "They are not additional provider calls. Batch diversity is not reused across batches."),
                      block(reuse, "json")])
    for number, call in enumerate(calls, 1):
        record = call["record"]
        lines.extend([f"## Call {number:03d}: {call['stage']}",
                      f"Request: `{call['request_id']}`. Task: `{call['task_id']}`.",
                      f"Model: `{record['model']}`. UTC: {record.get('timestamp', 'unknown')}.",
                      f"API status: **{record['status']}**. Duration: {record.get('seconds', 'unknown')} seconds.",
                      "### Request settings", block(record.get("request_settings", {}), "json")])
        for position, message in enumerate(record["messages"], 1):
            lines.extend([f"### Input {position}: {message['role']}", block(message.get("content", ""))])
        response = record.get("response") or {}
        if record.get("request"):
            lines.extend(["### Decisions request", block(record["request"], "json"),
                          "### Decisions response", block(response, "json")])
        for choice in response.get("choices", []):
            lines.extend([f"### Output: choice {choice.get('index', 0)}",
                          f"Finish reason: `{choice.get('finish_reason')}`.",
                          block((choice.get("message") or {}).get("content") or "(No assistant content returned.)")])
        if record.get("error") or response.get("error"):
            lines.extend(["### Provider error", block(record.get("error") or response["error"])])
        lines.extend(["### Recorded usage", block(record.get("usage", {}), "json"),
                      "### Input size diagnostics", block({key: record.get(key) for key in (
                          "input_characters", "context_capacity_exceeded")}, "json")])
    lines.append("## Parsed pipeline outputs")
    for stage in stages:
        lines.extend([f"### {stage['task_id']}: {stage['stage']} — {stage['status']}",
                      block(stage["parsed_output"], "json")])
    for filename, content in (("llm_calls.json", json.dumps(bundle, ensure_ascii=False, indent=2)),
                              ("trace.md", "\n\n".join(lines))):
        temporary = directory / (filename + ".tmp")
        temporary.write_text(content + "\n", encoding="utf-8")
        temporary.replace(directory / filename)


__all__ = ["GenerationRecorder", "RunState", "StageCheckpoint", "export_traces", "messages_sha256", "read_run_metadata"]
