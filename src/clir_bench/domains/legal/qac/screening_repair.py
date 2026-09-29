"""Regrade failed screening batches, retaining original attempts and successful grades.

The only prompt change is an explicit actual-batch-size instruction for the
faithfulness grader. Generation, quality rubrics, and scoring remain unchanged.
The initial experiment stays intact in run.sqlite; repairs have their own log.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace

from clir_bench.core import grading
from clir_bench.core.llm import parse_json_response
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


def recover_quality(raw, prompt, rows, mode):
    """Restore a missing positional index from an exact, unique candidate ID."""
    try:
        request_candidates = json.loads(raw['messages'][1]['content'])['candidates']
        ids = [c['candidate_id'] for c in request_candidates]
        if ids != [r['candidate_id'] for r in rows] or len(ids) != len(set(ids)):
            return None
        data = parse_json_response(raw['response']['choices'][0]['message']['content'])
        if not isinstance(data, dict) or not isinstance(data.get('candidates'), list):
            return None
        for candidate in data['candidates']:
            if 'index' not in candidate:
                candidate['index'] = ids.index(candidate['candidate_id'])
        return grading._normalize_compact_quality(data, grading.rubric_keys(prompt), request_candidates, mode)
    except (ValueError, TypeError, KeyError, IndexError):
        return None


def repair(directory):
    load_env()
    with sqlite3.connect(directory / 'run.sqlite') as db:
        metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM metadata')}
        failed = {task: json.loads(rows) for task, rows in db.execute(
            'SELECT task,rows FROM outcomes WHERE status="failed" AND task LIKE "mode/%"')}
        stages = {(task, stage): json.loads(value) for task, stage, value in db.execute(
            'SELECT task,stage,value FROM stages WHERE status="completed"')}
        quality_responses = {}
        for task, request_id, raw in db.execute('SELECT task,id,record FROM requests WHERE stage="quality" '
                                              'ORDER BY json_extract(record,"$.timestamp"),id'):
            quality_responses.setdefault(task, []).append((request_id, json.loads(raw)))
    cfg = metadata['config']
    jobs, indexes = [], {}
    for record in metadata['targets']:
        source = record['corpus']
        for mode in decider.MODES[source]:
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
        state.put('config', cfg)
        state.put('parent_run', str(directory.resolve()))
        state.put('reason', 'Retry failed grading only; explicit actual candidate count for faithfulness')
        state.put('status', 'running')
        complete = {r['task'] for r in state.outcomes() if r['status'] == 'completed'}

        def work(job):
            task, record, _mode, target, payload = job
            if task in complete:
                return task, 'replayed'
            rows = failed[task]
            real = state.checkpoint(task, retries=3)
            batch = BATCHES[record['corpus']]
            recovered_quality = None
            if (task, 'quality') not in stages:
                for request_id, raw in quality_responses.get(task, []):
                    recovered_quality = recover_quality(raw, batch.gen.PROMPTS.quality(target.mode, 'batch'),
                                                        rows, target.mode)
                    if recovered_quality is not None:
                        state.put('index_recovery/' + task, {'source_request_id': request_id,
                                  'method': 'restore index from exact unique candidate_id; validate full schema'})
                        break
            # Preserve provider grades when the sole defect is surrounding prose.
            # Earliest complete valid response wins; no extra or fabricated grades.
            recovered = None
            recovery_request = None
            with state.transaction() as db:
                previous = db.execute('SELECT id,record FROM requests WHERE task=? AND stage=? '
                                      'ORDER BY json_extract(record,"$.timestamp"),id',
                                      (task, 'faithfulness')).fetchall()
            for request_id, raw in previous:
                body = json.loads(raw).get('response') or {}
                for choice in body.get('choices', []):
                    recovered = extract_grades(choice.get('message', {}).get('content') or '', len(rows))
                    if recovered is not None:
                        recovery_request = request_id
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
            suffix = (f'\n\nACTUAL BATCH SIZE: This request contains exactly {len(rows)} candidates. '
                      f'Return exactly {len(rows)} grade objects, using indices '
                      f'{list(range(len(rows)))}. Grade only supplied candidates. '
                      'Any references above to THREE pairs or three example objects describe a '
                      'typical batch; this actual batch size overrides those counts. '
                      'All scoring criteria and calibration remain unchanged.')

            class Checkpoint:
                def run(self, stage, fn):
                    if stage == 'faithfulness' and recovered is not None:
                        return real.run('faithfulness_json_recovery', lambda: recovered)
                    if stage == 'quality' and recovered_quality is not None:
                        return real.run('quality_index_recovery', lambda: recovered_quality)
                    return real.run(stage, fn)

                def client(self, stage, model, client):
                    recorded = real.client(stage, model, client)
                    if stage != 'faithfulness':
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
                    if (task, 'faithfulness') not in stages:
                        prompt = batch.gen.PROMPTS.faithfulness('batch') + suffix
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
    args = parser.parse_args()
    repair(args.directory)


if __name__ == '__main__':
    main()
