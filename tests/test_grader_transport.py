import pytest

from clir_bench.core import grading


@pytest.mark.parametrize('model,extended_thinking', [
    ('google/gemini-3.8-flash', False),
    ('gpt-6-luna', False),
    ('z-ai/glm-5.3-flash', False),
    ('anthropic/claude-sonnet-5.5', True),
    ('~anthropic/claude-haiku-latest', True),
])
def test_grader_selects_reasoning_transport_by_model(monkeypatch, model, extended_thinking):
    calls = []
    monkeypatch.setattr(grading, 'chat', lambda *a, **kw: calls.append(('reasoning', kw)) or 'reply')
    monkeypatch.setattr(grading, 'chat_with_thinking',
                        lambda *a, **kw: calls.append(('thinking', kw)) or 'reply')
    config = grading.GraderConfig(model, reasoning_effort='low')
    assert grading._invoke(None, config, 'rubric', 'candidates') == 'reply'
    assert calls[0][0] == ('thinking' if extended_thinking else 'reasoning')
    if not extended_thinking:
        assert calls[0][1] == {'reasoning_effort': 'low'}


def test_explicit_transport_override_remains_available():
    assert grading.GraderConfig('google/gemini-3.8-flash', use_thinking=True).thinking
    assert not grading.GraderConfig('anthropic/claude-sonnet-5.5', use_thinking=False).thinking
