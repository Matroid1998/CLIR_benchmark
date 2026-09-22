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
import threading
import time
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
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

    def __init__(self, cache_path: Path | None, records_dir: Path, model: str):
        self.model = model
        self.records_dir = Path(records_dir)
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


__all__ = ["GenerationRecorder", "messages_sha256"]
