"""Regrade saved candidates, optionally replacing only the verifier system prompts."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

from clir_bench.core import grading, llm, prompt_registry
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.env import load_env
from clir_bench.domains.legal.qac.screening import digest


def compare_verifiers(parent, output):
    """Pair by immutable candidate ID, independent of either judge's ranking."""
    from clir_bench.domains.legal.qac.screening_analysis import write_csv

    def read(directory):
        with (directory / 'all_mode_candidates.csv').open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        indexed = {r['candidate_id']: r for r in rows}
        if len(indexed) != len(rows):
            raise ValueError('Duplicate candidate IDs in comparison')
        return indexed

    before, after = read(parent), read(output)
    if before.keys() != after.keys():
        raise ValueError('Regrade candidate population changed')
    pairs = []
    for candidate_id, old in before.items():
        new = after[candidate_id]
        identity = ('corpus', 'document_id', 'target_id', 'screening_mode', 'candidate_id', 'question', 'answer')
        if any(old[key] != new[key] for key in identity):
            raise ValueError(f'Regrade candidate identity or text changed: {candidate_id}')
        row = {key: old[key] for key in identity}
        for prefix, candidate in [('previous', old), ('new', new)]:
            for key in ('faith_overall', 'qual_overall', 'total_score', 'quality_audit_status',
                        'quality_checks_json', 'quality_problems_json', 'faith_reason',
                        'quality_score_notes_json', 'faithfulness_verifier_model', 'quality_verifier_model'):
                row[f'{prefix}_{key}'] = candidate.get(key, '')
        row['total_delta_new_minus_previous'] = (
            float(new['total_score']) - float(old['total_score'])
            if new['total_score'] and old['total_score'] else None)
        pairs.append(row)
    summaries = []
    for corpus, mode in dict.fromkeys((r['corpus'], r['screening_mode']) for r in pairs):
        rows = [r for r in pairs if (r['corpus'], r['screening_mode']) == (corpus, mode)]
        paired = [r for r in rows if r['total_delta_new_minus_previous'] is not None]
        summary = {'corpus': corpus, 'mode': mode, 'candidates': len(rows), 'paired_numeric_grades': len(paired)}
        for prefix in ('previous', 'new'):
            for field in ('faith_overall', 'qual_overall', 'total_score'):
                values = [float(r[f'{prefix}_{field}']) for r in paired]
                summary[f'{prefix}_mean_{field}'] = mean(values) if values else None
            summary[f'{prefix}_audit_clear_candidates'] = sum(
                r[f'{prefix}_quality_audit_status'] in ('clear', 'minor_issues') for r in rows)
        deltas = [r['total_delta_new_minus_previous'] for r in paired]
        summary.update(mean_total_delta=mean(deltas) if deltas else None,
                       new_higher=sum(d > 0 for d in deltas), new_lower=sum(d < 0 for d in deltas),
                       same_score=sum(d == 0 for d in deltas))
        summaries.append(summary)
    write_csv(output / 'verifier_candidate_comparison.csv', pairs)
    write_csv(output / 'verifier_mode_comparison.csv', summaries)
    return summaries


def load_parent(directory):
    with sqlite3.connect((directory / 'run.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM metadata')}
        outcomes = {t: {'status': s, 'rows': json.loads(r), 'error': e}
                    for t, s, r, e in db.execute('SELECT task,status,rows,error FROM outcomes')}
        messages, provenance = {}, {}
        skips = dict(metadata.get('generation_skip_reasons', {}))
        for request_id, task, stage, record in db.execute(
                'SELECT id,task,stage,record FROM requests ORDER BY json_extract(record,"$.timestamp"),id'):
            raw = json.loads(record)
            if stage in ('faithfulness', 'quality'):
                key = task, stage
                if key in messages and messages[key] != raw['messages']:
                    raise ValueError(f'Verifier inputs changed between attempts: {key}')
                messages[key] = raw['messages']
                provenance.setdefault(task, {}).setdefault(stage, request_id)
            elif stage == 'generation':
                try:
                    result = llm.parse_json_response(raw['response']['choices'][0]['message']['content'])
                    items = result if isinstance(result, list) else [result]
                    reasons = [str(item['skip_reason']) for item in items if isinstance(item, dict) and item.get('skip_reason')]
                    if reasons:
                        skips[task] = ' | '.join(reasons)
                except (ValueError, KeyError, IndexError, TypeError):
                    pass
    if metadata.get('status') != 'completed' or any(v['status'] == 'failed' for v in outcomes.values()):
        raise ValueError('Regrading requires a completed parent run with no unresolved failures')
    for task, result in outcomes.items():
        if not task.startswith('mode/') or not result['rows']:
            continue
        envelope = json.loads(messages[task, 'quality'][1]['content'])
        originals = {r['candidate_id']: r for r in result['rows']}
        candidates = envelope['candidates']
        if len(originals) != len(candidates) or set(originals) != {c['candidate_id'] for c in candidates}:
            raise ValueError(f'Recorded candidate identities differ: {task}')
        for candidate in candidates:
            original = originals[candidate['candidate_id']]
            if any(candidate[k] != original[k] for k in ('question', 'answer')):
                raise ValueError(f'Recorded candidate text differs: {task}')
        if len(messages[task, 'faithfulness']) != 2 or len(messages[task, 'quality']) != 2:
            raise ValueError(f'Expected system and user messages: {task}')
    return metadata, outcomes, messages, provenance, skips


def merge_grades(originals, candidates, faith, quality, model, prompts):
    by_id = {r['candidate_id']: r for r in originals}
    mode = originals[0]['mode']
    rows = []
    for rank, graded in enumerate(grading.rank_candidates(candidates, faith, quality, mode), 1):
        row = {k: v for k, v in by_id[graded.qa['candidate_id']].items()
               if not k.startswith(('faith_', 'qual_', 'quality_', 'faithfulness_verifier_', 'grading_'))}
        row.update(grading.grade_columns(graded.faith, graded.quality, mode))
        row.update(candidate_rank=rank if graded.total is not None else '', is_best=False,
                   grading_status='completed', grading_error='')
        for stage in ('faithfulness', 'quality'):
            row[f'{stage}_verifier_model'] = model
            row[f'{stage}_verifier_prompt'] = prompts[stage]
            row[f'{stage}_verifier_prompt_sha256'] = hashlib.sha256(prompts[stage].encode()).hexdigest()
        rows.append(row)
    return rows


def replace_verifier_prompts(metadata, outcomes, messages, manifest_path):
    """Pin new rubric text while retaining every recorded source/candidate message."""
    manifest = prompt_registry.read_manifest(str(Path(manifest_path).resolve()))
    metadata, messages = copy.deepcopy(metadata), copy.deepcopy(messages)
    used = {}
    for task, result in outcomes.items():
        if not task.startswith('mode/') or not result['rows']:
            continue
        source = task.split('/')[1]
        mode = result['rows'][0].get('screening_mode', result['rows'][0]['mode'])
        mode = 'practitioner' if mode == 'practitioners' else mode
        for stage in ('faithfulness', 'quality'):
            key = f'{source}/faithfulness' if stage == 'faithfulness' else f'{source}/quality/{mode}'
            prompt = prompt_registry.resolve_prompt(key, str(Path(manifest_path).resolve()))
            recorded = messages[task, stage]
            if len(recorded) != 2 or [m.get('role') for m in recorded] != ['system', 'user']:
                raise ValueError(f'Expected system and user messages: {task}/{stage}')
            if stage == 'quality' and len(grading.rubric_keys(prompt)) != 5:
                raise ValueError(f'Expected five quality criteria: {key}')
            recorded[0]['content'] = prompt
            used[key] = prompt
    metadata.setdefault('prompts', {}).update(used)
    metadata['verifier_prompt_manifest'] = manifest
    return metadata, messages, {
        'verifier_prompt_source': 'registered_override',
        'verifier_prompt_registry': {k: manifest[k] for k in ('bundle', 'label', 'bundle_sha256')},
        'verifier_prompts_sha256': digest(used),
        'prompts_sha256': digest(metadata['prompts']),
    }


def regrade(parent, output, model, *, workers=16, retries=3, verifier_prompt_manifest=None):
    if parent.resolve() == output.resolve():
        raise ValueError('Regrade output must be separate from its parent')
    load_env()
    metadata, outcomes, messages, provenance, skips = load_parent(parent)
    prompt_config = {}
    if verifier_prompt_manifest:
        metadata, messages, prompt_config = replace_verifier_prompts(
            metadata, outcomes, messages, verifier_prompt_manifest)
    config = dict(metadata['config'], verifier=model, parent_run=str(parent.resolve()),
                  operation='verifier_only', verifier_reasoning_effort='medium', retries=retries)
    config.update(prompt_config)
    fingerprint = digest({'config': config, 'parent_outcomes': outcomes, 'messages': list(messages.values())})
    output.mkdir(parents=True, exist_ok=True)
    with RunState(output / 'run.sqlite') as state:
        if state.get('fingerprint') not in (None, fingerprint):
            raise ValueError('Regrade source or configuration changed')
        state.put('fingerprint', fingerprint)
        for key in ('targets', 'prompts', 'prompt_manifest', 'verifier_prompt_manifest'):
            if key in metadata:
                state.put(key, metadata[key])
        state.put('config', config)
        state.put('generation_skip_reasons', skips)
        state.put('regrade_source_requests', provenance)
        state.put('status', 'running')
        for filename, value in [('config.json', config), ('selection.json', metadata['targets']),
                                ('prompt_manifest.json', metadata['prompt_manifest'])]:
            (output / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        if 'verifier_prompt_manifest' in metadata:
            prompt_registry.write_manifest(output / 'verifier_prompt_manifest.json',
                                           metadata['verifier_prompt_manifest'])
        completed = {r['task'] for r in state.outcomes() if r['status'] == 'completed'}
        jobs = []
        for task, result in outcomes.items():
            if task.startswith('decider/') or not result['rows']:
                state.outcome(task, result['rows'], result['error'] or '')
            elif task not in completed:
                jobs.append(task)

        def work(task):
            original = outcomes[task]['rows']
            candidates = json.loads(messages[task, 'quality'][1]['content'])['candidates']
            checkpoint = state.checkpoint(task, retries=retries)
            grades, errors = {}, []
            for stage in ('faithfulness', 'quality'):
                def call(stage=stage):
                    client = checkpoint.client(stage, model, llm.client_for(model))
                    raw = llm.chat(client, model, messages[task, stage], reasoning_effort='medium')
                    data = llm.parse_json_response(raw)
                    if stage == 'quality':
                        return grading._normalize_compact_quality(data,
                            grading.rubric_keys(messages[task, stage][0]['content']), candidates, original[0]['mode'])
                    items = grading._strict_items(data, len(candidates), grading.FAITHFULNESS_KEYS)
                    return [dict(grading._normalize_faith(item), _response=item) for item in items]
                try:
                    grades[stage] = checkpoint.run(stage, call)
                except Exception as error:  # noqa: BLE001 - persist provider and parser failures
                    errors.append(f'{stage}: {type(error).__name__}: {error}')
            if errors:
                # A failed new grade must never be mistaken for the parent's grade.
                rows = [{k: v for k, v in r.items() if not k.startswith(
                    ('faith_', 'qual_', 'quality_', 'faithfulness_verifier_', 'grading_'))}
                    for r in original]
                for row in rows:
                    row.update(total_score=None, candidate_rank='', is_best=False,
                               grading_status='failed', grading_error='; '.join(errors))
            else:
                rows = merge_grades(original, candidates, grades['faithfulness'], grades['quality'], model,
                                    {stage: messages[task, stage][0]['content'] for stage in grades})
            state.outcome(task, rows, '; '.join(errors))
            return task, 'failed' if errors else 'completed'

        # Verify one real batch from each corpus before scaling up.
        smoke = list({task.split('/')[1]: task for task in jobs}.values())
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(work, smoke))
        for result in results:
            print('PREFLIGHT', *result, flush=True)
        if any(status == 'failed' for _, status in results):
            state.put('status', 'preflight_failed')
            export_traces(output)
            raise RuntimeError('Verifier preflight failed; inspect recorded calls before resuming')
        rest = [task for task in jobs if task not in smoke]
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for index, future in enumerate(as_completed([executor.submit(work, task) for task in rest]), 1):
                print(f'{index}/{len(rest)}', *future.result(), flush=True)
        failures = sum(r['status'] == 'failed' for r in state.outcomes())
        state.put('status', 'completed_with_errors' if failures else 'completed')
    export_traces(output)
    print(f'DONE verifier-only regrade; {failures} failed batches', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verifier', required=True)
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--verifier-prompt-manifest', type=Path,
                        help='Replace verifier system prompts only; replay source/candidate inputs exactly')
    args = parser.parse_args()
    regrade(args.parent, args.output, args.verifier, workers=args.workers,
            verifier_prompt_manifest=args.verifier_prompt_manifest)
    from clir_bench.domains.legal.qac.screening_analysis import analyze
    analyze(args.output)
    compare_verifiers(args.parent, args.output)


if __name__ == '__main__':
    main()
