"""Repairs preserve the original prompt version, identities and provider scores."""
import copy
import hashlib
import json
import os
import sqlite3
from types import SimpleNamespace

import pytest

from clir_bench.core import prompt_registry
from clir_bench.core.prompts import PromptPack
from clir_bench.domains.legal.qac import screening_repair as repair
from clir_bench.domains.legal.qac.batch_recording import RunState


def manifest(texts):
    return {
        'schema_version': 1, 'provider': 'mlflow', 'bundle': 'test', 'label': 'pinned',
        'registry_uri': 'sqlite:///unused-test-registry.db',
        'bundle_sha256': prompt_registry.bundle_digest(texts),
        'prompts': {key: {'name': prompt_registry.prompt_name(key), 'version': 1,
                          'sha256': prompt_registry.sha256(text), 'text': text}
                    for key, text in texts.items()},
    }


def test_saved_manifest_overrides_active_selection_and_restores_environment(tmp_path, monkeypatch):
    monkeypatch.setenv('CLIR_PROMPT_SOURCE', 'local')
    monkeypatch.delenv('CLIR_PROMPT_MANIFEST', raising=False)
    texts = {'un/faithfulness': 'Original pinned faithfulness'}
    metadata = {'prompts': texts, 'prompt_manifest': manifest(texts), 'config': {}}
    pack = PromptPack('clir_bench.domains.legal.qac.prompts_un')
    with repair.saved_prompts(metadata, tmp_path / 'repairs'):
        assert pack.faithfulness() == texts['un/faithfulness']
        assert 'CLIR_PROMPT_SOURCE' not in os.environ
        assert prompt_registry.read_manifest(prompt_registry.selection()) == metadata['prompt_manifest']
    assert os.environ['CLIR_PROMPT_SOURCE'] == 'local'
    assert 'CLIR_PROMPT_MANIFEST' not in os.environ


def test_snapshot_drift_fails_before_regrading(tmp_path, monkeypatch):
    monkeypatch.setenv('CLIR_PROMPT_SOURCE', 'local')
    texts = {'un/faithfulness': 'Pinned text'}
    metadata = {'prompts': {'un/faithfulness': 'Different original text'},
                'prompt_manifest': manifest(texts), 'config': {}}
    with (pytest.raises(ValueError, match='differs from the original snapshot'),
          repair.saved_prompts(metadata, tmp_path / 'repairs')):
        pytest.fail('Mismatched prompt must never reach a grading call')
    assert os.environ['CLIR_PROMPT_SOURCE'] == 'local'


@pytest.mark.parametrize('echo,extra,accepted', [
    ('en', {}, True), ('fr', {}, False), ('en', {'unknown_score': 5}, False),
])
def test_quality_recovery_removes_only_exactly_matching_language_echo(echo, extra, accepted):
    keys = ('search_realism', 'anchoring_and_time', 'consequence', 'lexical_distance', 'linguistic_quality')
    row = {'candidate_id': 'q1', 'question_language': 'en', 'question': 'Question', 'answer': 'Answer'}
    grade = {'index': 0, 'candidate_id': 'q1', 'scores': dict.fromkeys(keys, 4),
             'score_notes': dict.fromkeys(keys, 'Supported'),
             'checks': dict.fromkeys(('mode', 'support', 'metadata'), 'pass'), 'problems': []}
    example = {'candidates': [grade], 'batch_diversity': 'not_applicable'}
    prompt = 'OUTPUT\n' + json.dumps(example)
    reply = copy.deepcopy(example)
    del reply['candidates'][0]['index']
    reply['candidates'][0].update(question_language=echo, **extra)
    content = json.dumps(reply)
    raw = {'messages': [{'content': prompt}, {'content': json.dumps({'candidates': [row]})}],
           'response': {'choices': [{'message': {'content': content}}]}}
    recovered = repair.recover_quality(raw, prompt, [row], 'semantic')
    if accepted:
        assert recovered[0]['_response'] == grade
        assert raw['response']['choices'][0]['message']['content'] == content
    else:
        assert recovered is None
    del row['question_language']
    raw['messages'][1]['content'] = json.dumps({'candidates': [row]})
    assert repair.recover_quality(raw, prompt, [row], 'semantic') is None


def quality_fixture(count):
    keys = ('situation', 'regime_fixing', 'terminology_and_distance', 'focus', 'linguistic_quality')
    rows = [{'candidate_id': f'q{i}', 'question_language': 'en', 'question': 'Question', 'answer': 'Answer'}
            for i in range(count)]
    grades = [{'index': i, 'candidate_id': row['candidate_id'], 'scores': dict.fromkeys(keys, 4),
               'score_notes': dict.fromkeys(keys, 'Supported'),
               'checks': dict.fromkeys(('mode', 'support', 'metadata'), 'pass'), 'problems': []}
              for i, row in enumerate(rows)]
    example = {'candidates': grades[:1], 'batch_diversity': 'not_applicable'}
    prompt = 'OUTPUT\n' + json.dumps(example)
    batch = {'candidates': grades, 'batch_diversity': 'not_applicable' if count == 1 else 'pass'}
    raw = {'messages': [{'content': prompt}, {'content': json.dumps({'candidates': rows})}],
           'response': {'choices': [{'message': {'content': ''}}]}}
    return prompt, rows, batch, raw


@pytest.mark.parametrize('prefix', ['incomplete', 'different_valid', 'identical_valid', 'prose'])
def test_quality_extraction_requires_one_unambiguous_complete_batch(prefix):
    prompt, rows, batch, raw = quality_fixture(2)
    other = copy.deepcopy(batch)
    if prefix == 'incomplete':
        other['candidates'].pop()
    elif prefix == 'different_valid':
        other['candidates'][0]['scores']['focus'] = 3
    content = ('Here are the grades:' if prefix == 'prose' else json.dumps(other))
    content += '\nCorrection:\n' + json.dumps(batch) + '\n</br>'
    raw['response']['choices'][0]['message']['content'] = content
    provenance = {}
    recovered = repair.recover_quality(raw, prompt, rows, 'fact_pattern', provenance=provenance)
    if prefix == 'different_valid':
        assert recovered is None and not provenance
    else:
        assert [item['_response'] for item in recovered] == batch['candidates']
        assert provenance['transforms'][0]['operation'] == 'extract_unique_complete_quality_object'
    assert raw['response']['choices'][0]['message']['content'] == content


@pytest.mark.parametrize('defect', ['misplaced', 'root_and_nested', 'invalid_value', 'multiple',
                                  'unknown_field', 'missing_score', 'unknown_wrapper'])
def test_quality_diversity_relocation_is_single_candidate_and_fully_valid(defect):
    prompt, rows, batch, raw = quality_fixture(2 if defect == 'multiple' else 1)
    changed = copy.deepcopy(batch)
    changed['candidates'][0]['batch_diversity'] = changed.pop('batch_diversity')
    if defect == 'root_and_nested':
        changed['batch_diversity'] = 'not_applicable'
    elif defect == 'invalid_value':
        changed['candidates'][0]['batch_diversity'] = 'pass'
    elif defect == 'unknown_field':
        changed['candidates'][0]['unknown_score'] = 5
    elif defect == 'missing_score':
        del changed['candidates'][0]['scores']['focus']
    elif defect == 'unknown_wrapper':
        changed = {'unknown': changed}
    content = json.dumps(changed)
    raw['response']['choices'][0]['message']['content'] = content
    provenance = {}
    recovered = repair.recover_quality(raw, prompt, rows, 'fact_pattern', provenance=provenance)
    if defect == 'misplaced':
        assert recovered[0]['_response'] == batch['candidates'][0]
        assert provenance['transforms'] == [{'operation': 'move', 'from': 'candidates[0].batch_diversity',
                                            'to': 'batch_diversity', 'value': 'not_applicable'}]
    else:
        assert recovered is None and not provenance
    assert raw['response']['choices'][0]['message']['content'] == content


@pytest.mark.parametrize('recoverable', [True, False])
@pytest.mark.parametrize('response_source', ['original', 'repair'])
def test_recovery_only_keeps_successful_faith_and_recovers_recorded_quality(
        tmp_path, monkeypatch, recoverable, response_source):
    keys = ('practitioner_realism', 'anchoring', 'consequence', 'informativeness', 'linguistic_quality')
    grade = {'index': 0, 'candidate_id': 'q1', 'scores': dict.fromkeys(keys, 4),
             'score_notes': dict.fromkeys(keys, 'Supported'),
             'checks': dict.fromkeys(('mode', 'support', 'metadata'), 'pass'), 'problems': []}
    example = {'candidates': [grade], 'batch_diversity': 'not_applicable'}
    quality_prompt = 'OUTPUT\n' + json.dumps(example)
    texts = {'un/faithfulness': 'Original faith prompt', 'un/quality/lookup': quality_prompt}
    source = 'Original source payload'
    screening_fields = {'corpus': 'un', 'target_id': 'doc#0', 'document_id': 'doc',
                        'symbol': 'S/TEST/1', 'screening_mode': 'lookup',
                        'mode_eligible': True, 'is_meeting': False}
    row = {'candidate_id': 'q1', 'question': 'Which deadline?', 'answer': '1999', **screening_fields}
    original_faith = [{'index': 0, 'grounding': 3, 'precision': 4, 'numerical_fidelity': 5,
                      'overall': 12, 'reason': 'Original successful grade'}]
    task = 'mode/un/doc#0/lookup'
    record = {'corpus': 'un', 'target_id': 'doc#0', 'target': {},
              'source_payload_sha256': hashlib.sha256(source.encode()).hexdigest()}
    raw = {'messages': [{'content': quality_prompt},
                        {'content': json.dumps({'candidates': [row]})}], 'timestamp': '0',
           'response': {'choices': [{'message': {'content': ''}}]}}
    missing_index = copy.deepcopy(example)
    del missing_index['candidates'][0]['index']
    if not recoverable:
        del missing_index['candidates'][0]['scores'][keys[0]]
    raw['response']['choices'][0]['message']['content'] = json.dumps(missing_index)
    with RunState(tmp_path / 'run.sqlite') as state:
        state.put('config', {'generator': 'unused-generator', 'verifier': 'unused-verifier',
                             'prompts_sha256': 'snapshot', 'language': 'en'})
        state.put('prompts', texts)
        state.put('prompt_manifest', manifest(texts))
        state.put('targets', [record])
        state.checkpoint(task).run('faithfulness', lambda: original_faith)
        state.outcome(task, [row], 'Missing quality index')
    response_db = tmp_path / ('run.sqlite' if response_source == 'original' else 'grade_repairs/run.sqlite')
    with RunState(response_db) as state:
        with state.transaction() as db:
            db.execute('INSERT INTO requests VALUES (?,?,?,?)',
                       (response_source + '-response', task, 'quality', json.dumps(raw)))

    allow_retry, calls = [], []

    def simulated_new_grade():
        assert allow_retry, 'Recovery-only must refuse before invoking the stage callback'
        calls.append('quality')
        return [{'_response': grade, 'overall': 20}]

    def run_one(target, _, *, checkpoint, existing_candidates, **kwargs):
        assert fake.gen.PROMPTS.quality('lookup') == quality_prompt
        faith = checkpoint.run('faithfulness', lambda: pytest.fail('Must reuse successful faithfulness'))
        quality = checkpoint.run('quality', simulated_new_grade)
        assert faith == original_faith
        assert quality[0]['_response'] == grade
        # Real batch.run_one rebuilds rows without the screening export fields.
        return [{'candidate_id': 'q1', 'grading_status': 'completed', 'total_score': 32}]

    fake = SimpleNamespace(gen=SimpleNamespace(PROMPTS=PromptPack('clir_bench.domains.legal.qac.prompts_un')),
                           ctx=SimpleNamespace(BlockIndex=lambda: None),
                           Target=lambda **kw: SimpleNamespace(**kw),
                           prepare_payload=lambda *args: SimpleNamespace(text=source), run_one=run_one)
    monkeypatch.setattr(repair, 'BATCHES', {'un': fake})
    monkeypatch.setattr(repair, 'load_env', lambda: None)
    monkeypatch.setattr(repair, 'export_traces', lambda _: None)
    before = hashlib.sha256((tmp_path / 'run.sqlite').read_bytes()).hexdigest()
    repair.repair(tmp_path, recovery_only=True)
    assert hashlib.sha256((tmp_path / 'run.sqlite').read_bytes()).hexdigest() == before
    with sqlite3.connect(tmp_path / 'grade_repairs/run.sqlite') as db:
        assert db.execute('SELECT status FROM outcomes').fetchone()[0] == ('completed' if recoverable else 'failed')
        policy = json.loads(db.execute("SELECT value FROM metadata WHERE key='repair_policy'").fetchone()[0])
        assert policy['exact_prompt_snapshot'] is True
        assert policy['legacy_count_hint'] is False
        if recoverable:
            provenance = json.loads(db.execute("SELECT value FROM metadata WHERE key=?",
                                               ('index_recovery/' + task,)).fetchone()[0])
            assert provenance['source_request_id'] == response_source + '-response'
        else:
            assert db.execute("SELECT count(*) FROM stages WHERE stage='quality'").fetchone()[0] == 0
    assert not calls
    if not recoverable:
        allow_retry.append(True)
        repair.repair(tmp_path, recovery_only=False)
        assert calls == ['quality']
    with sqlite3.connect(tmp_path / 'grade_repairs/run.sqlite') as db:
        status, repaired = db.execute('SELECT status,rows FROM outcomes').fetchone()
        assert status == 'completed'
        assert {key: json.loads(repaired)[0][key] for key in screening_fields} == screening_fields
        if not recoverable:
            assert db.execute("SELECT attempts FROM stages WHERE stage='quality'").fetchone()[0] == 1
    changed = copy.deepcopy(raw)
    changed['messages'][0]['content'] += '\nChanged calibration'
    assert repair.recover_quality(changed, quality_prompt, [row], 'lookup') is None
