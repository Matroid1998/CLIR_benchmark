"""
LLM transports.

Collapses five copies of the OpenAI/OpenRouter client construction, three copies
of the Claude extended-thinking call, three copies of the markdown-fence JSON
parser, and two copies of the OpenRouter reasoning-parameter fallback ladder.

Two providers are in play by design: questions are generated on OpenAI, and the
feedback verifiers run Claude via OpenRouter. Only the transport differs --
OpenAI takes ``reasoning_effort``, Claude takes a thinking budget -- so that
difference is the only thing these functions branch on.
"""

from __future__ import annotations

import json
import os
import random
import time
from functools import lru_cache
from typing import Any, Callable, Mapping, Optional, Sequence, TypeVar

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

T = TypeVar("T")


# --------------------------------------------------------------------------- #
# Clients
# --------------------------------------------------------------------------- #

@lru_cache(maxsize=None)
def openai_client() -> Any:
    """OpenAI client from ``OPENAI_API_KEY``."""
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set (add it to .env)")
    return OpenAI(api_key=key)


@lru_cache(maxsize=None)
def openrouter_client() -> Any:
    """OpenRouter client (OpenAI-compatible) from ``OPENROUTER_API_KEY``."""
    from openai import OpenAI

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set (add it to .env)")
    return OpenAI(api_key=key, base_url=OPENROUTER_BASE_URL)


def provider_of(model: str) -> str:
    """Which transport a model id belongs to."""
    return "openai" if model.startswith("gpt-") or model.startswith("o1") else "openrouter"


def client_for(model: str) -> Any:
    return openai_client() if provider_of(model) == "openai" else openrouter_client()


# --------------------------------------------------------------------------- #
# Calls
# --------------------------------------------------------------------------- #

def chat(
    client: Any,
    model: str,
    messages: Sequence[Mapping[str, str]],
    *,
    reasoning_effort: Optional[str] = None,
    max_tokens: Optional[int] = None,
    extra_body: Optional[Mapping[str, Any]] = None,
) -> str:
    """One chat completion, returning the message text.

    On OpenRouter the reasoning parameter is not accepted uniformly across
    providers, so it degrades through a ladder rather than failing the call.
    """
    kwargs: dict[str, Any] = {"model": model, "messages": list(messages)}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if extra_body:
        kwargs["extra_body"] = dict(extra_body)

    if reasoning_effort and provider_of(model) == "openai":
        kwargs["reasoning_effort"] = reasoning_effort
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    if reasoning_effort:
        from openai import BadRequestError

        ladder: list[Optional[dict[str, Any]]] = [
            {"effort": reasoning_effort},
            {"enabled": True},
            None,
        ]
        for reasoning in ladder:
            body = dict(kwargs.get("extra_body") or {})
            if reasoning is not None:
                body["reasoning"] = reasoning
            attempt = dict(kwargs)
            if body:
                attempt["extra_body"] = body
            try:
                response = client.chat.completions.create(**attempt)
                return response.choices[0].message.content or ""
            except BadRequestError:
                continue

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def chat_with_thinking(
    client: Any,
    model: str,
    messages: Sequence[Mapping[str, str]],
    *,
    budget_tokens: int = 8000,
    max_tokens: int = 12000,
) -> str:
    """Claude extended-thinking call via OpenRouter.

    The budget/max pair is the grading comparability contract across every
    dataset this project has published; it is configured in one place
    (``LLMSettings``) and threaded through here.
    """
    response = client.chat.completions.create(
        model=model,
        messages=list(messages),
        max_tokens=max_tokens,
        extra_body={"thinking": {"type": "enabled", "budget_tokens": budget_tokens}},
    )
    return response.choices[0].message.content or ""


# --------------------------------------------------------------------------- #
# Response handling
# --------------------------------------------------------------------------- #

def parse_json_response(text: str) -> Any:
    """Parse a JSON body that may be wrapped in a markdown code fence."""
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0]
        if cleaned.lstrip().startswith("json"):
            cleaned = cleaned.lstrip()[4:]
    return json.loads(cleaned.strip())


def parse_json_object(text: str) -> dict:
    """Parse a JSON response expected to be one object.

    Graders sometimes return a single-element list even when asked for an
    object; every legacy call site unwrapped that the same way.
    """
    data = parse_json_response(text)
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else {}


def call_with_retries(
    fn: Callable[[], T],
    *,
    retries: int = 3,
    label: str = "llm call",
    base_delay: float = 2.0,
    max_delay: float = 30.0,
) -> T:
    """Retry ``fn`` with exponential backoff and jitter."""
    last: Optional[BaseException] = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - transport errors vary by provider
            last = exc
            if attempt == retries:
                break
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay += random.uniform(0, delay * 0.1)
            print(f"[retry {attempt}/{retries}] {label}: {exc} (sleeping {delay:.1f}s)")
            time.sleep(delay)
    raise RuntimeError(f"{label} failed after {retries} attempts") from last


def extract_usage(response: Any) -> dict[str, Any]:
    """Token counts and provider-reported cost from a completion response."""
    try:
        payload = response.model_dump()
    except AttributeError:
        return {}
    usage = payload.get("usage") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    return {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": completion_details.get("reasoning_tokens"),
        "cached_tokens": prompt_details.get("cached_tokens"),
        "provider_cost": usage.get("cost"),
    }


__all__ = [
    "OPENROUTER_BASE_URL",
    "call_with_retries",
    "chat",
    "chat_with_thinking",
    "client_for",
    "extract_usage",
    "openai_client",
    "openrouter_client",
    "parse_json_object",
    "parse_json_response",
    "provider_of",
]
