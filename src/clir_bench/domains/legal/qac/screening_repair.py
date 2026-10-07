"""Regrade failed screening batches, retaining original attempts and successful grades.

Saved prompt versions and successful provider grades are preserved. Repairs
have their own log; the initial run.sqlite is opened read-only. A historical
faithfulness batch-size hint is available only through an explicit option.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from types import SimpleNamespace

from clir_bench.core import grading, prompt_registry
from clir_bench.core.prompts import load_prompt
from clir_bench.domains.legal.qac import decider
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.env import load_env
from clir_bench.domains.legal.qac.screening import BATCHES, task_id


def extract_grades(text, count):
    """Recover one unambiguous, fully valid grade array surrounded by prose."""
    valid = {}
    for position, char in enumerate(text):
        if char != '[':
            continue
        try:
            data, _ = json.JSONDecoder().raw_decode(text[position:])
            items = grading._strict_items(data, count, grading.FAITHFULNESS_KEYS)
        except (ValueError, TypeError, KeyError):
            continue
        valid[json.dumps(items, sort_keys=True)] = items
    if len(valid) != 1:
        return None
    return [dict(grading._normalize_faith(item), _response=item)
            for item in next(iter(valid.values()))]


def recover_quality(raw, prompt, rows, mode, *, provenance=None):
    """Recover one unique valid batch using only documented structural repairs."""
    try:
        if raw['messages'][0]['content'] != prompt:
            return None
        request_candidates = json.loads(raw['messages'][1]['content'])['candidates']
        ids = [c['candidate_id'] for c in request_candidates]
        if ids != [r['candidate_id'] for r in rows] or len(ids) != len(set(ids)):
            return None
        request_by_id = dict(zip(ids, request_candidates))
        text = raw['response']['choices'][0]['message']['content']
        if not isinstance(text, str):
            return None
        keys = grading.rubric_keys(prompt)
    except (ValueError, TypeError, KeyError, IndexError):
        return None
    valid, position = {}, 0
    while position < len(text):
        start = text.find('{', position)
        if start < 0:
            break
        try:
            data, length = json.JSONDecoder().raw_decode(text[start:])
        except ValueError:
            position = start + 1
            continue
        # Never discard fields of a decoded wrapper to select an inner object.
        position = start + length
        transforms = []
        try:
            if not isinstance(data, dict) or not isinstance(data.get('candidates'), list):
                continue
            candidates = data['candidates']
            if (len(request_candidates) == len(candidates) == 1
                    and 'batch_diversity' not in data and 'batch_diversity' in candidates[0]):
                data['batch_diversity'] = candidates[0].pop('batch_diversity')
                transforms.append({'operation': 'move', 'from': 'candidates[0].batch_diversity',
                                   'to': 'batch_diversity', 'value': data['batch_diversity']})
            for candidate in candidates:
                if 'index' not in candidate:
                    candidate['index'] = ids.index(candidate['candidate_id'])
                    transforms.append({'operation': 'restore_index_from_unique_candidate_id',
                                       'candidate_id': candidate['candidate_id'], 'index': candidate['index']})
                if 'question_language' in candidate:
                    original = request_by_id[candidate['candidate_id']]
                    if ('question_language' not in original
                            or candidate['question_language'] != original['question_language']):
                        raise ValueError('Language echo differs from input')
                    transforms.append({'operation': 'remove_matching_input_language_echo',
                                       'candidate_id': candidate['candidate_id'],
                                       'question_language': candidate.pop('question_language')})
            normalized = grading._normalize_compact_quality(data, keys, request_candidates, mode)
        except (ValueError, TypeError, KeyError, IndexError):
            continue
        if text[:start].strip() or text[position:].strip():
            transforms.insert(0, {'operation': 'extract_unique_complete_quality_object',
                                  'start_character': start, 'end_character': position})
        valid.setdefault(json.dumps(data, sort_keys=True), (normalized, transforms))
    if len(valid) != 1:
        return None
    result, transforms = next(iter(valid.values()))
    if provenance is not None:
        provenance.update(transforms=transforms)
    return result


@contextmanager
def saved_prompts(metadata, repair_dir):
    """Select the saved bundle, reject prompt drift, and restore caller settings."""
    previous = {key: os.environ.get(key) for key in ('CLIR_PROMPT_MANIFEST', 'CLIR_PROMPT_SOURCE')}
    try:
        manifest = metadata.get('prompt_manifest')
        if manifest is not None:
            path = repair_dir / 'prompt_manifest.json'
            prompt_registry.write_manifest(path, manifest)
            os.environ['CLIR_PROMPT_MANIFEST'] = str(path.resolve())
            os.environ.pop('CLIR_PROMPT_SOURCE', None)
        load_prompt.cache_clear()
        snapshot = metadata.get('prompts')
        if not isinstance(snapshot, dict) or not snapshot:
            raise ValueError('Repair requires the original prompt snapshot')
        for key, expected in snapshot.items():
            source, role, *parts = key.split('/')
            pack = BATCHES[source].gen.PROMPTS
            if role == 'decider':
                actual = decider.prompt_text(source, parts[0])
            elif role == 'faithfulness':
                actual = pack.faithfulness('batch')
            elif role == 'quality':
                actual = pack.quality(decider.generation_mode(parts[0]), 'batch')
            elif role == 'generation':
                actual = pack.generation(decider.generation_mode(parts[0]), metadata['config'].get('language', 'en'))
            else:
                raise ValueError(f'Unknown saved screening prompt: {key}')
            if actual != expected:
                raise ValueError(f'Repair prompt differs from the original snapshot: {key}')
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        load_prompt.cache_clear()


def repair(directory, *, legacy_count_hint=False, recovery_only=False):
    load_env()
    with sqlite3.connect((directory / 'run.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        db.execute('BEGIN')
        metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM metadata')}
        failed = {task: json.loads(rows) for task, rows in db.execute(
            'SELECT task,rows FROM outcomes WHERE status="failed" AND task LIKE "mode/%"')}
        stages = {(task, stage): json.loads(value) for task, stage, value in db.execute(
            'SELECT task,stage,value FROM stages WHERE status="completed"')}
        quality_responses = {}
        for task, request_id, raw in db.execute('SELECT task,id,record FROM requests WHERE stage="quality" '
                                              'ORDER BY json_extract(record,"$.timestamp"),id'):
            quality_responses.setdefault(task, []).append((request_id, json.loads(raw)))
        faith_responses = {}
        for task, request_id, raw in db.execute('SELECT task,id,record FROM requests WHERE stage="faithfulness" '
                                              'ORDER BY json_extract(record,"$.timestamp"),id'):
            faith_responses.setdefault(task, []).append((request_id, json.loads(raw)))
    repair_dir = directory / 'grade_repairs'
    with saved_prompts(metadata, repair_dir):
        _repair(directory, metadata, failed, stages, quality_responses, faith_responses,
                legacy_count_hint=legacy_count_hint, recovery_only=recovery_only)


def _repair(directory, metadata, failed, stages, quality_responses, faith_responses,
            *, legacy_count_hint, recovery_only):
    cfg = metadata['config']
    jobs, indexes = [], {}
    for record in metadata['targets']:
        source = record['corpus']
        for mode in (*decider.MODES[source], *(("semantic",) if source == "un" else ())):
            task = task_id('mode', record, mode)
            if task not in failed or not failed[task]:
                continue
            batch = BATCHES[source]
            if source not in indexes:
                indexes[source] = batch.ctx.BlockIndex() if source == 'un' else batch.ctx.ArticleIndex()
            target = batch.Target(**dict(record['target'], mode=decider.generation_mode(mode)))
            payload = batch.prepare_payload(target, indexes[source])
            if hashlib.sha256(payload.text.encode()).hexdigest() != record['source_payload_sha256']:
                raise ValueError('Source payload changed before repair')
            jobs.append((task, record, mode, target, payload))
    repair_dir = directory / 'grade_repairs'
    with RunState(repair_dir / 'run.sqlite') as state:
        policy = {'exact_prompt_snapshot': not legacy_count_hint,
                  'legacy_count_hint': legacy_count_hint,
                  'prompts_sha256': cfg['prompts_sha256']}
        previous_policy = state.get('repair_policy')
        if previous_policy is not None and previous_policy != policy:
            raise ValueError('Cannot resume repairs with a different prompt policy')
        if previous_policy is None and state.outcomes():
            raise ValueError('Existing historical repairs lack prompt-policy provenance; use a separate repair directory')
        state.put('repair_policy', policy)
        state.put('config', cfg)
        state.put('prompts', metadata['prompts'])
        if metadata.get('prompt_manifest') is not None:
            state.put('prompt_manifest', metadata['prompt_manifest'])
        state.put('parent_run', str(directory.resolve()))
        state.put('reason', 'Recover valid recorded grades, then retry only missing grading with saved prompts'
                  + ('; explicit legacy faithfulness count hint requested' if legacy_count_hint else ''))
        state.put('status', 'running')
        complete = {r['task'] for r in state.outcomes() if r['status'] == 'completed'}

        def work(job):
            task, record, _mode, target, payload = job
            if task in complete:
                return task, 'replayed'
            rows = failed[task]
            original_by_id = {row['candidate_id']: row for row in rows}
            if len(original_by_id) != len(rows):
                raise ValueError('Failed batch has duplicate candidate identities')
            real = state.checkpoint(task, retries=3)
            batch = BATCHES[record['corpus']]
            faith_prompt = batch.gen.PROMPTS.faithfulness('batch')
            recovered_quality = None
            if (task, 'quality') not in stages:
                with state.transaction() as db:
                    previous_quality = db.execute(
                        'SELECT id,record FROM requests WHERE task=? AND stage=?',
                        (task, 'quality')).fetchall()
                previous_quality = [(request_id, json.loads(raw)) for request_id, raw in previous_quality]
                previous_quality = quality_responses.get(task, []) + previous_quality
                previous_quality.sort(key=lambda pair: (pair[1].get('timestamp', ''), pair[0]))
                for request_id, raw in previous_quality:
                    quality_provenance = {}
                    recovered_quality = recover_quality(raw, batch.gen.PROMPTS.quality(target.mode, 'batch'),
                                                        rows, target.mode, provenance=quality_provenance)
                    if recovered_quality is not None:
                        state.put('index_recovery/' + task, {'source_request_id': request_id,
                                  'method': 'earliest response with one unique schema-valid quality batch; '
                                            'only explicitly recorded structural repairs', **quality_provenance})
                        break
            # Preserve provider grades when the sole defect is surrounding prose.
            # Earliest complete valid response wins; no extra or fabricated grades.
            recovered = None
            recovery_request = None
            recovered_prompt = None
            with state.transaction() as db:
                previous = db.execute('SELECT id,record FROM requests WHERE task=? AND stage=? '
                                      'ORDER BY json_extract(record,"$.timestamp"),id',
                                      (task, 'faithfulness')).fetchall()
            previous = [(request_id, json.loads(raw)) for request_id, raw in previous]
            previous = faith_responses.get(task, []) + previous
            previous.sort(key=lambda pair: (pair[1].get('timestamp', ''), pair[0]))
            if (task, 'faithfulness') in stages:
                previous = []
            suffix = (f'\n\nACTUAL BATCH SIZE: This request contains exactly {len(rows)} candidates. '
                      f'Return exactly {len(rows)} grade objects, using indices '
                      f'{list(range(len(rows)))}. Grade only supplied candidates. '
                      'Any references above to THREE pairs or three example objects describe a '
                      'typical batch; this actual batch size overrides those counts. '
                      'All scoring criteria and calibration remain unchanged.') if legacy_count_hint else ''
            for request_id, raw in previous:
                recorded_prompt = (raw.get('messages') or [{}])[0].get('content')
                if recorded_prompt not in (faith_prompt, faith_prompt + suffix):
                    continue
                body = raw.get('response') or {}
                for choice in body.get('choices', []):
                    recovered = extract_grades(choice.get('message', {}).get('content') or '', len(rows))
                    if recovered is not None:
                        recovery_request = request_id
                        recovered_prompt = recorded_prompt
                        break
                if recovered is not None:
                    break
            if recovered is not None:
                state.put('json_recovery/' + task, {'source_request_id': recovery_request,
                    'method': 'earliest response with exactly one schema-valid grade array'})
            # Failed batches preserve generation order (total_score is unset).
            for stage in ('faithfulness', 'quality'):
                if (task, stage) in stages:
                    real.run(stage, lambda s=stage: stages[task, s])
            class Checkpoint:
                def run(self, stage, fn):
                    if stage == 'faithfulness' and recovered is not None:
                        return real.run('faithfulness_json_recovery', lambda: recovered)
                    if stage == 'quality' and recovered_quality is not None:
                        return real.run('quality_index_recovery', lambda: recovered_quality)
                    if recovery_only:
                        with state.transaction() as db:
                            saved = db.execute('SELECT status,value FROM stages WHERE task=? AND stage=?',
                                               (task, stage)).fetchone()
                        if saved is not None and saved[0] == 'completed':
                            return json.loads(saved[1])
                        # Refusal is not a provider attempt. A later paid repair
                        # must retain its complete checkpoint retry budget.
                        raise ValueError(f'Recovery-only repair has no valid saved {stage} grade; no model call made')
                    return real.run(stage, fn)

                def client(self, stage, model, client):
                    recorded = real.client(stage, model, client)
                    if stage != 'faithfulness' or not suffix:
                        return recorded

                    def create(**kwargs):
                        messages = [dict(m) for m in kwargs['messages']]
                        messages[0]['content'] += suffix
                        return recorded.chat.completions.create(**dict(kwargs, messages=messages))
                    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

            batch = BATCHES[record['corpus']]
            limits = {'context_chars': 30000} if record['corpus'] == 'un' else {'max_references': 6}
            try:
                result = batch.run_one(target, None, payload=payload, gen_model=cfg['generator'],
                    grade_model=cfg['verifier'], keep=3, checkpoint=Checkpoint(),
                    existing_candidates=rows, **limits)
                for row in result:
                    original = original_by_id[row['candidate_id']]
                    for key in ('corpus', 'target_id', 'document_id', 'symbol',
                                'screening_mode', 'mode_eligible', 'is_meeting'):
                        if key in original:
                            row[key] = original[key]
                    if (task, 'faithfulness') not in stages:
                        prompt = recovered_prompt if recovered is not None else faith_prompt + suffix
                        row['faithfulness_verifier_prompt'] = prompt
                        row['faithfulness_verifier_prompt_sha256'] = hashlib.sha256(prompt.encode()).hexdigest()
                    row['screening_grade_repair'] = True
                error = '; '.join(sorted({r.get('grading_error', '') for r in result
                                         if r.get('grading_status') == 'failed'}))
                state.outcome(task, result, error)
                return task, 'failed' if error else 'completed'
            except Exception as error:  # noqa: BLE001 - preserve every paid repair attempt
                state.outcome(task, rows, str(error))
                return task, 'failed'
        with ThreadPoolExecutor(max_workers=4) as executor:
            for result in as_completed([executor.submit(work, job) for job in jobs]):
                print(*result.result(), flush=True)
        state.put('status', 'completed_with_errors' if any(r['status'] == 'failed'
                  for r in state.outcomes()) else 'completed')
        export_traces(repair_dir)


def main():
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--legacy-count-hint', action='store_true',
                        help='Explicitly append the historical faithfulness batch-count hint; not an exact prompt rerun')
    parser.add_argument('--recovery-only', action='store_true',
                        help='Recover recorded grades only; never make a model call')
    args = parser.parse_args()
    repair(args.directory, legacy_count_hint=args.legacy_count_hint, recovery_only=args.recovery_only)


if __name__ == '__main__':
    main()
