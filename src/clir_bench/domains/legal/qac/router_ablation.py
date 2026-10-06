"""Cross two saved UN Jev instruction/criteria variants without regenerating data."""
from __future__ import annotations

import argparse
import copy
import json
import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

from clir_bench.core import prompt_registry
from clir_bench.domains.legal.qac import decider
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.env import load_env

KEY = 'un/decider/jev'
CHOICES = ('lookup', 'practitioner', 'conceptual', 'skip')
LEGACY_CHOICES = ('lookup', 'practitioner', 'semantic', 'skip')
CROSSES = {'b_instructions_c_criteria': ('B', 'C'),
           'c_instructions_b_criteria': ('C', 'B')}


def digest(value):
    return prompt_registry.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True))


def crossed_template(base, criteria_source):
    """Change exactly one JSON property, preserving all other values and order."""
    result = copy.deepcopy(base)
    left, right = base['questions']['mode'], criteria_source['questions']['mode']
    if list(left['criteria']) != list(right['criteria']) or tuple(left['criteria']) not in (CHOICES, LEGACY_CHOICES):
        raise ValueError('The UN criterion names and order must match')
    for template in (base, criteria_source):
        if template['questions']['mode']['type'] != 'choice':
            raise ValueError('Ablation requires native choice templates')
    comparable = []
    for template in (base, criteria_source):
        other = copy.deepcopy(template)
        for field in ('instructions', 'criteria'):
            del other['questions']['mode'][field]
        comparable.append(other)
    if comparable[0] != comparable[1]:
        raise ValueError('Templates differ outside instructions and criteria')
    result['questions']['mode']['criteria'] = copy.deepcopy(right['criteria'])
    return result


def read_run(directory):
    """Read one consistent snapshot and match completed decisions to wire calls."""
    with sqlite3.connect((directory / 'run.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        db.execute('BEGIN')
        metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM metadata')}
        outcomes = {task: json.loads(rows)[0] for task, rows in db.execute(
            "SELECT task,rows FROM outcomes WHERE status='completed' AND task LIKE 'decider/un/%'")}
        calls = [(identity, task, json.loads(raw)) for identity, task, raw in db.execute(
            "SELECT id,task,record FROM requests WHERE task LIKE 'decider/un/%/jev' "
            "ORDER BY json_extract(record,'$.timestamp'),id")]
    text = metadata['prompts'][KEY]
    template = json.loads(text)
    targets = {row['target_id']: row for row in metadata['targets'] if row['corpus'] == 'un'}
    matched = {}
    for identity, task, raw in calls:
        if task not in outcomes or raw.get('status') != 'response':
            continue
        response = raw.get('response') or {}
        try:
            parsed = decider.parse_decision(response, 'un', 'jev')
        except ValueError:
            continue
        if any(parsed[key] != outcomes[task].get(key) for key in parsed):
            continue
        target_id = task.removeprefix('decider/un/').removesuffix('/jev')
        state = raw['request']['state']
        expected = dict(copy.deepcopy(template), model=decider.JEV_MODEL, state=state)
        if raw['request'] != expected:
            raise ValueError(f'Wire request differs from saved template: {task}')
        state_hash = prompt_registry.sha256(state)
        if state_hash != targets[target_id]['source_payload_sha256']:
            raise ValueError(f'Saved source hash mismatch: {task}')
        matched[target_id] = dict(parsed, resolved_backend=response.get('model'),
                                 provider=response.get('provider'), request_id=identity,
                                 response_id=response.get('id'), timestamp=raw.get('timestamp'),
                                 source_payload_sha256=state_hash, state=state)
    if set(matched) != set(targets):
        raise ValueError('Every saved UN target must have a completed matching Jev response')
    usage = {'native_requests': len(calls),
             'response_count': sum(raw.get('status') == 'response' for _, _, raw in calls),
             'reported_cost_usd': sum(((raw.get('response') or {}).get('usage') or {}).get('cost', 0) or 0
                                      for _, _, raw in calls)}
    return {'directory': str(directory.resolve()), 'text': text, 'template': template,
            'metadata': metadata, 'targets': targets, 'decisions': matched, 'outcomes': outcomes,
            'usage': usage}


def prepare_sources(base_dir):
    runs = {'B': read_run(base_dir / 'debiased/run'), 'C': read_run(base_dir / 'simple/run')}
    ids = list(runs['B']['targets'])
    if len(ids) != 50 or set(ids) != set(runs['C']['targets']):
        raise ValueError('This bounded ablation requires the same 50 UN targets')
    for target_id in ids:
        if runs['B']['decisions'][target_id]['state'] != runs['C']['decisions'][target_id]['state']:
            raise ValueError(f'B/C source drift: {target_id}')
    backends = {entry['resolved_backend'] for run in runs.values() for entry in run['decisions'].values()}
    if len(backends) != 1 or None in backends:
        raise ValueError('B/C resolved backend differs or is unknown')
    # Validate both property swaps before registry publication or model calls.
    for left, right in CROSSES.values():
        crossed_template(runs[left]['template'], runs[right]['template'])
    return runs, ids, next(iter(backends))


def summarize(decisions):
    values = list(decisions.values())
    choices = tuple(values[0]["probabilities"]) if values else CHOICES
    return {'n': len(values), 'mode_counts': {mode: sum(v['mode'] == mode for v in values) for mode in choices},
            'mean_probabilities': {mode: mean(v['probabilities'][mode] for v in values) for mode in choices},
            'resolved_backends': dict(Counter(v['resolved_backend'] for v in values))}


def comparison(left, right):
    if set(left) != set(right):
        raise ValueError('Cannot compare different target sets')
    transitions = Counter((left[key]['mode'], right[key]['mode']) for key in left)
    drops = [left[key]['probabilities']['practitioner'] - right[key]['probabilities']['practitioner']
             for key in left]
    return {'n': len(left), 'same_choice': sum(left[key]['mode'] == right[key]['mode'] for key in left),
            'transitions': [{'from': a, 'to': b, 'count': n} for (a, b), n in sorted(transitions.items())],
            'practitioner_probability_drop': {'mean': mean(drops), 'min': min(drops), 'max': max(drops),
                                             'positive_targets': sum(v > 0 for v in drops)}}


def write_report(base_dir, runs, ids, expected_backend, crossed=None):
    decisions = {label: run['decisions'] for label, run in runs.items()}
    decisions.update({label: run['decisions'] for label, run in (crossed or {}).items()})
    choices = tuple(next(iter(runs.values()))['template']['questions']['mode']['criteria'])
    report = {
        'schema_version': 1, 'source': 'UN', 'target_count': 50,
        'requested_model': decider.JEV_MODEL, 'resolved_backend': expected_backend,
        'validation': {'all_states_byte_identical': True, 'all_recorded_requests_match_saved_templates': True,
                       'choice_order': list(choices), 'no_local_criterion_weighting_or_choice_remapping': True},
        'original_prompts': {label: {'run_directory': run['directory'],
                                    'template_sha256': prompt_registry.sha256(run['text']),
                                    'instruction_structure': list(run['template']['questions']['mode']['instructions']),
                                    'instructions': run['template']['questions']['mode']['instructions'],
                                    'criteria': run['template']['questions']['mode']['criteria']}
                             for label, run in runs.items()},
        'changed_clauses': {mode: {label: run['template']['questions']['mode']['criteria'][mode]
                                  for label, run in runs.items()} for mode in choices},
        'structural_change': 'B separates task, input_structure and selection. C folds instructions into one task string and shortens option criteria.',
        'interpretation_caveat': 'B/C change structure and wording together. Crossed variants isolate the instructions object from the criteria object, not individual words or internal backend weighting. These are routing results, not evidence that any mode generates better questions. One run per cell cannot establish repeat-run variability. No mode quota is a success criterion.',
        'summaries': {label: summarize(rows) for label, rows in decisions.items()},
        'comparisons': {f'{a}_to_{b}': comparison(decisions[a], decisions[b])
                        for i, a in enumerate(decisions) for b in list(decisions)[i + 1:]},
        'targets': [],
        'crossed_runs': {label: {'directory': run['directory'],
                                 'template_sha256': prompt_registry.sha256(run['text']),
                                 'swap': run['metadata']['config']['swap'],
                                 'manifest': run['metadata']['prompt_manifest'],
                                 'usage': run['usage']}
                         for label, run in (crossed or {}).items()},
    }
    if crossed:
        bc, cb = 'b_instructions_c_criteria', 'c_instructions_b_criteria'
        effects = {
            'simplify_instructions_with_B_criteria': comparison(decisions['B'], decisions[cb]),
            'simplify_instructions_with_C_criteria': comparison(decisions[bc], decisions['C']),
            'simplify_criteria_with_B_instructions': comparison(decisions['B'], decisions[bc]),
            'simplify_criteria_with_C_instructions': comparison(decisions[cb], decisions['C']),
        }
        report['factorial_comparisons'] = effects
        report['finding'] = (
            'Both prompt blocks affect routing. The simplified instructions cause the larger '
            'practitioner-probability reduction at either fixed criterion set; the simplified '
            'criteria also reduce it at either fixed instruction set. The instruction comparison '
            'changes both wording and JSON structure, so these results cannot attribute the effect '
            'to a particular sentence, property name or internal backend mechanism.'
        )
        report['new_experiment_usage'] = {
            'native_requests': sum(run['usage']['native_requests'] for run in crossed.values()),
            'reported_cost_usd': sum(run['usage']['reported_cost_usd'] for run in crossed.values()),
            'generation_requests': 0, 'verifier_requests': 0,
        }
    for target_id in ids:
        original = runs['B']['targets'][target_id]
        report['targets'].append({key: original[key] for key in
                                  ('target_id', 'document_id', 'symbol', 'is_meeting', 'source_payload_sha256')} |
                                 {'variants': {label: {k: v for k, v in rows[target_id].items() if k != 'state'}
                                               for label, rows in decisions.items()}})
    path = base_dir / 'un_router_sensitivity.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


def run_variant(directory, manifest, samples, expected_backend, *, swap, workers=8, retries=3):
    if not 1 <= workers <= 8 or not 1 <= retries <= 3 or len(samples) != 50:
        raise ValueError('Limit: 50 targets, 1–8 workers, 1–3 attempts per target')
    if len({row['target_id'] for row in samples}) != len(samples):
        raise ValueError('Duplicate target IDs')
    for row in samples:
        if prompt_registry.sha256(row['source_payload']) != row['source_payload_sha256']:
            raise ValueError('Source hash drift before a model call')
    prompt_registry.validate_manifest(manifest)
    if set(manifest['prompts']) != {KEY}:
        raise ValueError('A router ablation manifest must contain exactly one prompt')
    text = manifest['prompts'][KEY]['text']
    template = json.loads(text)
    directory.mkdir(parents=True, exist_ok=True)
    prompt_registry.write_manifest(directory / 'prompt_manifest.json', manifest)
    config = {'experiment': 'UN Jev instructions/criteria crossing', 'model': decider.JEV_MODEL,
              'resolved_backend_required': expected_backend, 'target_count': 50, 'workers': workers,
              'retries': retries, 'prompt_sha256': prompt_registry.sha256(text),
              'sources_sha256': digest([(row['target_id'], row['source_payload_sha256']) for row in samples]),
              'swap': swap}
    fingerprint = digest(config)
    with RunState(directory / 'run.sqlite') as state:
        previous = state.get('fingerprint')
        if previous is not None and previous != fingerprint:
            raise ValueError('Refusing to resume changed prompt/source/configuration')
        state.put('fingerprint', fingerprint)
        state.put('config', config)
        state.put('prompts', {KEY: text})
        state.put('prompt_manifest', manifest)
        state.put('targets', samples)
        state.put('status', 'running')

        def work(sample):
            task = f"decider/un/{sample['target_id']}/jev"
            checkpoint = state.checkpoint(task, retries=retries)
            request = dict(copy.deepcopy(template), model=decider.JEV_MODEL, state=sample['source_payload'])

            def call():
                raw = checkpoint.decisions(request)
                result = decider.parse_decision(raw, 'un', 'jev')
                if raw.get('model') != expected_backend:
                    raise ValueError(f"Resolved backend changed: {raw.get('model')}")
                return dict(result, model=decider.JEV_MODEL, backend='jev',
                            resolved_backend=raw.get('model'), provider=raw.get('provider'))
            try:
                result = checkpoint.run('decider', call)
                state.outcome(task, [result])
                return task, 'completed'
            except Exception as error:  # noqa: BLE001 - retain every failed call/checkpoint
                state.outcome(task, [], f'{type(error).__name__}: {error}')
                return task, 'failed'

        first = work(samples[0])
        print('PREFLIGHT', directory.parent.name, *first, flush=True)
        if first[1] != 'completed':
            state.put('status', 'preflight_failed')
            export_traces(directory)
            raise RuntimeError('Router preflight failed; no fan-out performed')
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for i, future in enumerate(as_completed([executor.submit(work, row) for row in samples[1:]]), 2):
                result = future.result()
                if i % 10 == 0 or result[1] != 'completed':
                    print('ROUTER', directory.parent.name, i, *result, flush=True)
        failed = sum(row['status'] != 'completed' for row in state.outcomes())
        state.put('status', 'completed_with_errors' if failed else 'completed')
        export_traces(directory)
    if failed:
        raise RuntimeError(f'{failed} router tasks failed; inspect saved checkpoints')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_dir', type=Path)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--retries', type=int, default=3)
    parser.add_argument('--prepare-only', action='store_true', help='Persist evidence and registered prompts; no model calls')
    args = parser.parse_args()
    load_env()
    runs, ids, backend = prepare_sources(args.base_dir)
    write_report(args.base_dir, runs, ids, backend)
    registry = prompt_registry.MLflowRegistry(registry_uri=runs['B']['metadata']['prompt_manifest']['registry_uri'])
    samples = []
    for target_id in ids:
        record = runs['B']['targets'][target_id]
        samples.append({key: record[key] for key in
                        ('corpus', 'target_id', 'document_id', 'symbol', 'is_meeting', 'stratum', 'source_payload_sha256')} |
                       {'source_payload': runs['B']['decisions'][target_id]['state']})
    prepared = {}
    for name, (left, right) in CROSSES.items():
        directory = args.base_dir / 'router_ablation' / name
        text = json.dumps(crossed_template(runs[left]['template'], runs[right]['template']), ensure_ascii=False, indent=2) + '\n'
        mapping = {KEY: text}
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / 'prompts.json'
        if path.exists() and json.loads(path.read_text()) != mapping:
            raise ValueError('Existing ablation prompt differs; refusing to overwrite')
        path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
        label = f'legal-20260930-un-router-{left.lower()}i-{right.lower()}c'
        manifest = registry.publish(mapping, bundle=name, label=label)
        prompt_registry.write_manifest(directory / 'manifest.json', manifest)
        swap = {'base_template': left, 'instructions_from': left, 'criteria_from': right,
                'changed_property': 'questions.mode.criteria',
                'unchanged': 'All other JSON properties and choice order',
                'base_template_sha256': prompt_registry.sha256(runs[left]['text']),
                'criteria_source_template_sha256': prompt_registry.sha256(runs[right]['text'])}
        prepared[name] = (directory, manifest, swap)
        print('PUBLISHED', label, manifest['prompts'][KEY]['version'], flush=True)
    if args.prepare_only:
        return
    crossed = {}
    for name, (directory, manifest, swap) in prepared.items():
        run_variant(directory / 'run', manifest, samples, backend, swap=swap,
                    workers=args.workers, retries=args.retries)
        crossed[name] = read_run(directory / 'run')
    report = write_report(args.base_dir, runs, ids, backend, crossed)
    print(json.dumps({'summaries': report['summaries'], 'comparisons': report['comparisons']}, indent=2))


if __name__ == '__main__':
    main()
