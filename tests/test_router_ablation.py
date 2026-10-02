"""Offline controls for the bounded router-only instruction/criteria experiment."""
import copy
import json

import pytest

from clir_bench.core import llm, prompt_registry
from clir_bench.domains.legal.qac import router_ablation as ablation


def template(task='B', criterion='B'):
    return {'model': 'jev-latest', 'state': '<state>', 'questions': {'mode': {
        'type': 'choice', 'instructions': {'task': task},
        'criteria': {key: f'{criterion}: {key}' for key in ablation.CHOICES}}}}


def registered(prompt):
    text = json.dumps(prompt)
    return {'schema_version': 1, 'provider': 'mlflow', 'bundle': 'test', 'label': 'test-ablation',
            'registry_uri': 'sqlite:///unused-test-registry.db',
            'bundle_sha256': prompt_registry.bundle_digest({ablation.KEY: text}),
            'prompts': {ablation.KEY: {'name': prompt_registry.prompt_name(ablation.KEY),
                                      'version': 1, 'sha256': prompt_registry.sha256(text), 'text': text}}}


def samples():
    return [{'corpus': 'un', 'target_id': f'doc#{i}', 'document_id': 'doc', 'symbol': 'S/TEST/1',
             'is_meeting': False, 'stratum': 'report', 'source_payload': f'Original source {i}',
             'source_payload_sha256': prompt_registry.sha256(f'Original source {i}')}
            for i in range(50)]


def response(backend='test-snapshot'):
    return {'model': backend, 'provider': 'Test', 'id': 'test-response',
            'answers': {'mode': {'type': 'choice', 'choice': 'practitioner', 'confidence': 1,
                                'probabilities': {key: float(key == 'practitioner') for key in ablation.CHOICES}}},
            'usage': {'input_tokens': 2, 'output_tokens': 2, 'cost': 0}}


def test_cross_changes_only_criteria_and_preserves_order():
    b, c = template(), template('C', 'C')
    crossed = ablation.crossed_template(b, c)
    assert crossed['questions']['mode']['instructions'] == b['questions']['mode']['instructions']
    assert crossed['questions']['mode']['criteria'] == c['questions']['mode']['criteria']
    assert list(crossed['questions']['mode']['criteria']) == list(ablation.CHOICES)
    restored = copy.deepcopy(crossed)
    restored['questions']['mode']['criteria'] = b['questions']['mode']['criteria']
    assert restored == b
    assert b == template() and c == template('C', 'C')
    bad = copy.deepcopy(c)
    bad['state'] = 'Different'
    with pytest.raises(ValueError, match='outside instructions and criteria'):
        ablation.crossed_template(b, bad)
    bad = copy.deepcopy(c)
    bad['questions']['mode']['criteria'] = dict(reversed(list(bad['questions']['mode']['criteria'].items())))
    with pytest.raises(ValueError, match='names and order'):
        ablation.crossed_template(b, bad)


def test_fifty_calls_include_preflight_resume_without_calls_and_refuse_source_drift(tmp_path, monkeypatch):
    calls = []

    def call(request):
        calls.append(request)
        return response()

    monkeypatch.setattr(llm, 'decisions', call)
    manifest = registered(template())
    rows = samples()
    ablation.run_variant(tmp_path, manifest, rows, 'test-snapshot', swap={'changed_property': 'criteria'})
    assert len(calls) == 50
    assert calls[0]['state'] == rows[0]['source_payload']
    assert {r['state'] for r in calls} == {r['source_payload'] for r in rows}
    assert all(r['questions'] == template()['questions'] for r in calls)
    result = ablation.read_run(tmp_path)
    assert len(result['decisions']) == 50
    assert ablation.summarize(result['decisions'])['mode_counts']['practitioner'] == 50
    ablation.run_variant(tmp_path, manifest, rows, 'test-snapshot', swap={'changed_property': 'criteria'})
    assert len(calls) == 50
    changed = copy.deepcopy(rows)
    changed[0]['source_payload'] += ' changed'
    with pytest.raises(ValueError, match='Source hash drift'):
        ablation.run_variant(tmp_path, manifest, changed, 'test-snapshot', swap={'changed_property': 'criteria'})
    changed[0]['source_payload_sha256'] = prompt_registry.sha256(changed[0]['source_payload'])
    with pytest.raises(ValueError, match='Refusing to resume changed'):
        ablation.run_variant(tmp_path, manifest, changed, 'test-snapshot', swap={'changed_property': 'criteria'})
    assert len(calls) == 50


def test_backend_drift_fails_preflight_without_fanout(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(llm, 'decisions', lambda request: (calls.append(request), response('wrong-snapshot'))[1])
    with pytest.raises(RuntimeError, match='preflight failed'):
        ablation.run_variant(tmp_path, registered(template()), samples(), 'test-snapshot',
                             swap={}, retries=1)
    assert len(calls) == 1
