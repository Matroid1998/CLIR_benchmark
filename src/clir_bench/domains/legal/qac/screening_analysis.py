"""Analyze a screening run without further provider calls."""
from __future__ import annotations

import argparse
import csv
import json
import random
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from clir_bench.core.llm import parse_json_response
from clir_bench.domains.legal.qac import decider
from clir_bench.domains.legal.qac.screening import task_id


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def avg(values):
    return mean(values) if values else None


def paired_ci(values):
    if not values:
        return None
    rng = random.Random(20260929)
    samples = sorted(mean(rng.choices(values, k=len(values))) for _ in range(5000))
    return [samples[125], samples[4874]]


def mode_summary(record, mode, outcome, *, meeting_modes='all'):
    candidates = outcome['rows'] if outcome else []
    graded = [r for r in candidates if r.get('grading_status') == 'completed'
              and r.get('total_score') is not None]
    grounded = [r for r in graded if record['corpus'] != 'un' or r['faith_grounding'] >= 3]
    audited = [r for r in grounded if r.get('quality_audit_status') in ('clear', 'minor_issues')]
    best = max(grounded, key=lambda r: r['total_score'], default=None)
    strict = max(audited, key=lambda r: r['total_score'], default=None)
    return {'corpus': record['corpus'], 'target_id': record['target_id'],
            'document_id': record['document_id'], 'symbol': record['symbol'],
            'is_meeting': record['is_meeting'], 'stratum': record['stratum'], 'mode': mode,
            'eligible': meeting_modes == 'all' or not record['is_meeting'] or mode in ('semantic', 'conceptual'),
            'status': outcome['status'] if outcome else 'pending',
            'error': outcome.get('error') or '' if outcome else '',
            'candidate_count': len(candidates), 'graded_count': len(graded),
            'grounded_count': len(grounded), 'audit_clear_count': len(audited),
            'mean_candidate_score': avg([r['total_score'] for r in graded]),
            'best_score': best['total_score'] if best else None,
            'best_faithfulness': best['faith_overall'] if best else None,
            'best_quality': best['qual_overall'] if best else None,
            'best_audit_status': best.get('quality_audit_status', '') if best else '',
            'best_question': best['question'] if best else '',
            'best_answer': best['answer'] if best else '',
            'audit_clear_best_score': strict['total_score'] if strict else None}


def compare_target(record, mode_rows, decisions):
    eligible = [r for r in mode_rows if r['eligible']]
    complete = all(r['status'] in ('completed', 'no_candidates') for r in eligible)
    available = [r for r in eligible if r['best_score'] is not None]
    top = max((r['best_score'] for r in available), default=None)
    winners = [r['mode'] for r in available if r['best_score'] == top]
    strict = max((r['audit_clear_best_score'] for r in eligible
                  if r['audit_clear_best_score'] is not None), default=None)
    result = {k: record[k] for k in ('corpus', 'target_id', 'document_id', 'symbol', 'title',
                                    'is_meeting', 'stratum', 'document_text')}
    result.update(all_eligible_modes_completed=complete, oracle_best_score=top,
                  oracle_modes='|'.join(winners), oracle_audit_clear_score=strict)
    for row in mode_rows:
        result[f"{row['mode']}_score"] = row['best_score']
        result[f"{row['mode']}_audit_clear_score"] = row['audit_clear_best_score']
        result[f"{row['mode']}_status"] = row['status']
    for backend in ('generator', 'jev'):
        outcome = decisions.get(backend)
        answer = outcome['rows'][0] if outcome and outcome['rows'] else {}
        mode = answer.get('mode')
        selected = next((r for r in eligible if r['mode'] == mode), None)
        score = selected['best_score'] if selected else None
        clear_score = selected['audit_clear_best_score'] if selected else None
        valid_decision = bool(mode) and outcome['status'] == 'completed'
        result.update({f'{backend}_mode': mode, f'{backend}_reason': answer.get('reason', ''),
            f'{backend}_confidence': answer.get('confidence'),
            f'{backend}_decision_status': outcome['status'] if outcome else 'pending',
            f'{backend}_selected_score': score,
            f'{backend}_matches_best': mode in winners if valid_decision and top is not None else None,
            f'{backend}_score_regret': top - score if top is not None and score is not None else None,
            f'{backend}_utility': (score or 0) if valid_decision and complete else None,
            f'{backend}_audit_clear_utility': (clear_score or 0) if valid_decision and complete else None,
            f'{backend}_selected_mode_unproductive': (mode != 'skip' and score is None
                and top is not None) if valid_decision and complete else None,
            f'{backend}_missed_opportunity': (mode == 'skip' and top is not None) if valid_decision else None})
    result['deciders_agree'] = (result['generator_mode'] == result['jev_mode']
                              if result['generator_mode'] and result['jev_mode'] else None)
    return result


def analyze(directory):
    with sqlite3.connect(directory / 'run.sqlite') as db:
        metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM metadata')}
        outcomes = {t: {'status': s, 'rows': json.loads(r), 'error': e}
                    for t, s, r, e in db.execute('SELECT task,status,rows,error FROM outcomes')}
        requests = [(stage, json.loads(record)) for stage, record in db.execute('SELECT stage,record FROM requests')]
        skip_reasons = {}
        for task, raw in db.execute('SELECT task,record FROM requests WHERE stage="generation"'):
            body = json.loads(raw).get('response') or {}
            for choice in body.get('choices', []):
                try:
                    parsed = parse_json_response(choice.get('message', {}).get('content') or '')
                except ValueError:
                    continue
                items = parsed if isinstance(parsed, list) else [parsed]
                reasons = [str(item['skip_reason']) for item in items
                           if isinstance(item, dict) and item.get('skip_reason')]
                if reasons:
                    skip_reasons[task] = ' | '.join(reasons)
    original_failures = sum(o['status'] == 'failed' for o in outcomes.values())
    repaired = []
    repairs_path = directory / 'grade_repairs' / 'run.sqlite'
    if repairs_path.exists():
        with sqlite3.connect(repairs_path) as db:
            for task, status, rows, error in db.execute('SELECT task,status,rows,error FROM outcomes'):
                if status == 'completed':
                    outcomes[task] = {'status': status, 'rows': json.loads(rows), 'error': error}
                    repaired.append(task)
            requests.extend((stage + '_repair', json.loads(record)) for stage, record in db.execute(
                'SELECT stage,record FROM requests'))
    run_modes = dict(decider.MODES)
    if any(task.startswith('mode/un/') and task.endswith('/semantic') for task in outcomes):
        run_modes['un'] = ('lookup', 'practitioner', 'semantic')
    entries = metadata['targets']
    write_csv(directory / 'documents.csv', [{k: v for k, v in e.items() if k != 'target'}
                                            for e in entries])
    decision_rows = []
    for entry in entries:
        for backend in ('generator', 'jev'):
            result = outcomes.get(task_id('decider', entry, backend))
            if not result:
                continue
            row = {k: v for k, v in entry.items() if k != 'target'}
            row.update(backend=backend, status=result['status'], error=result['error'] or '')
            if result['rows']:
                row.update(result['rows'][0])
            probabilities = row.pop('probabilities', None)
            row['probabilities_json'] = json.dumps(probabilities) if probabilities is not None else ''
            decision_rows.append(row)
    write_csv(directory / 'decisions.csv', decision_rows)
    modes, comparisons = [], []
    for entry in entries:
        rows = [mode_summary(entry, mode, outcomes.get(task_id('mode', entry, mode)),
                            meeting_modes=metadata['config'].get('meeting_modes', 'semantic_only'))
                for mode in run_modes[entry['corpus']]]
        for row in rows:
            row['generation_skip_reason'] = skip_reasons.get(task_id('mode', entry, row['mode']), '')
        modes.extend(rows)
        comparisons.append(compare_target(entry, rows, {b: outcomes.get(task_id('decider', entry, b))
                            for b in ('generator', 'jev')}))
    write_csv(directory / 'mode_scores.csv', modes)
    write_csv(directory / 'mode_runs.csv', [{k: r[k] for k in ('corpus', 'target_id', 'mode',
              'is_meeting', 'eligible', 'status', 'error', 'candidate_count')} for r in modes])
    write_csv(directory / 'document_comparison.csv', comparisons)
    write_csv(directory / 'all_mode_candidates.csv', [row for task, result in outcomes.items()
                                                     if task.startswith('mode/') for row in result['rows']])
    subsets = {}
    for source in dict.fromkeys(e['corpus'] for e in entries):
        subsets[f'{source}_all'] = [r for r in comparisons if r['corpus'] == source]
        if source == 'un':
            subsets['un_without_meetings'] = [r for r in comparisons if r['corpus'] == 'un' and not r['is_meeting']]
            subsets['un_meetings_only'] = [r for r in comparisons if r['corpus'] == 'un' and r['is_meeting']]
    distributions, policy, agreement, mode_aggregates, confusion = [], [], [], [], []
    for subset, records in subsets.items():
        source = records[0]['corpus'] if records else 'un'
        ids = {r['target_id'] for r in records}
        for backend in ('generator', 'jev'):
            counts = Counter(r[f'{backend}_mode'] or 'error' for r in records)
            for mode in (*run_modes[source], 'skip', 'error'):
                distributions.append({'subset': subset, 'backend': backend, 'mode': mode,
                    'count': counts[mode], 'n': len(records),
                    'percent': 100 * counts[mode] / len(records) if records else 0})
            evaluated = [r for r in records if r[f'{backend}_utility'] is not None]
            routed = [r for r in evaluated if r[f'{backend}_mode'] != 'skip']
            scorable = [r for r in routed if r[f'{backend}_selected_score'] is not None]
            oracle_available = [r for r in evaluated if r['oracle_best_score'] is not None]
            policy.append({'subset': subset, 'backend': backend, 'n': len(records),
                'complete_comparisons': len(evaluated), 'routed': len(routed),
                'scored_selected': len(scorable), 'skipped': sum(r[f'{backend}_mode'] == 'skip' for r in evaluated),
                'missed_score_opportunities': sum(bool(r[f'{backend}_missed_opportunity']) for r in evaluated),
                'selected_mode_unproductive_despite_alternative': sum(
                    bool(r[f'{backend}_selected_mode_unproductive']) for r in evaluated),
                'oracle_available': len(oracle_available),
                'matches_oracle': sum(bool(r[f'{backend}_matches_best']) for r in oracle_available),
                'mean_selected_score_when_available': avg([r[f'{backend}_selected_score'] for r in scorable]),
                'mean_regret_when_scored': avg([r[f'{backend}_score_regret'] for r in scorable]),
                'mean_utility_zero_for_skip_or_no_candidate': avg([r[f'{backend}_utility'] for r in evaluated]),
                'mean_audit_clear_utility': avg([r[f'{backend}_audit_clear_utility'] for r in evaluated]),
                'mean_oracle_utility': avg([r['oracle_best_score'] or 0 for r in evaluated])})
        paired = [r for r in records if r['generator_utility'] is not None and r['jev_utility'] is not None]
        delta = [r['generator_utility'] - r['jev_utility'] for r in paired]
        pairs = Counter((r['generator_mode'], r['jev_mode']) for r in records
                        if r['deciders_agree'] is not None)
        for (a, b), n in pairs.items():
            confusion.append({'subset': subset, 'generator_mode': a, 'jev_mode': b, 'count': n})
        agreement.append({'subset': subset, 'n': len(records), 'valid_pairs': sum(pairs.values()),
            'agree': sum(n for (a, b), n in pairs.items() if a == b),
            'generator_better_utility': sum(d > 0 for d in delta),
            'jev_better_utility': sum(d < 0 for d in delta), 'utility_ties': sum(d == 0 for d in delta),
            'mean_paired_utility_difference_generator_minus_jev': avg(delta),
            'bootstrap_95_interval': paired_ci(delta)})
        for mode in run_modes[source]:
            rows = [r for r in modes if r['corpus'] == source and r['target_id'] in ids and r['mode'] == mode]
            eligible = [r for r in rows if r['eligible']]
            completed = [r for r in eligible if r['status'] in ('completed', 'no_candidates')]
            scored = [r for r in completed if r['best_score'] is not None]
            mode_aggregates.append({'subset': subset, 'mode': mode, 'attempted': len(rows),
                'eligible': len(eligible), 'completed_eligible': len(completed), 'scored': len(scored),
                'generated_candidates': sum(r['candidate_count'] for r in eligible),
                'no_candidates': sum(r['status'] == 'no_candidates' for r in completed),
                'mean_best_score': avg([r['best_score'] for r in scored]),
                'mean_best_faithfulness': avg([r['best_faithfulness'] for r in scored]),
                'mean_best_quality': avg([r['best_quality'] for r in scored]),
                'mean_utility_zero_for_no_candidate': avg([r['best_score'] or 0 for r in completed]),
                'mean_audit_clear_utility': avg([r['audit_clear_best_score'] or 0 for r in completed]),
                'oracle_wins_including_ties': sum(mode in r['oracle_modes'].split('|') for r in records
                                                 if r['all_eligible_modes_completed']),
                'best_candidate_blocking': sum(r['best_audit_status'] == 'blocking' for r in scored),
                'audit_clear_targets': sum(r['audit_clear_best_score'] is not None for r in completed)})
    for filename, rows in [('mode_distribution.csv', distributions), ('decider_performance.csv', policy),
                           ('agreement.csv', agreement), ('mode_summary.csv', mode_aggregates),
                           ('confusion.csv', confusion)]:
        write_csv(directory / filename, rows)
    usage = defaultdict(lambda: {'calls': 0, 'provider_errors': 0, 'prompt_tokens': 0,
                                'completion_tokens': 0, 'reported_cost': 0, 'calls_missing_cost': 0,
                                'seconds': []})
    for stage, record in requests:
        cell = usage[stage, record['model']]
        cell['calls'] += 1
        cell['provider_errors'] += record['status'] == 'error'
        u = record.get('usage') or {}
        cell['prompt_tokens'] += u.get('prompt_tokens') or 0
        cell['completion_tokens'] += u.get('completion_tokens') or 0
        cell['reported_cost'] += u.get('provider_cost') or 0
        cell['calls_missing_cost'] += u.get('provider_cost') is None
        if record.get('seconds') is not None:
            cell['seconds'].append(record['seconds'])
    for cell in usage.values():
        seconds = sorted(cell.pop('seconds'))
        cell['mean_seconds'] = avg(seconds)
        cell['p95_seconds'] = seconds[min(len(seconds) - 1, int(len(seconds) * .95))] if seconds else None
    costs = [dict(stage=s, model=m, **v) for (s, m), v in usage.items()]
    write_csv(directory / 'usage.csv', costs)
    status = metadata['status']
    if status.startswith('completed') and not any(o['status'] == 'failed' for o in outcomes.values()):
        status = 'completed'
    summary = {'config': metadata['config'], 'status': status,
               'original_failed_tasks': original_failures, 'repaired_tasks': repaired,
               'outcomes': dict(Counter(o['status'] for o in outcomes.values())),
               'distributions': distributions, 'policies': policy, 'agreement': agreement,
               'modes': mode_aggregates, 'usage': costs}
    (directory / 'summary.json').write_text(json.dumps(summary, indent=2))
    plot(directory, distributions, mode_aggregates)
    report(directory, summary, comparisons)
    return summary


def plot(directory, distributions, modes):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    subsets = list(dict.fromkeys(r['subset'] for r in distributions))
    fig, axes = plt.subplots(1, len(subsets), figsize=(5 * len(subsets), 4.5), squeeze=False)
    for ax, subset in zip(axes[0], subsets):
        labels = list(dict.fromkeys(r['mode'] for r in distributions if r['subset'] == subset and r['mode'] != 'error'))
        x = np.arange(len(labels))
        for i, backend in enumerate(('generator', 'jev')):
            rows = {r['mode']: r for r in distributions if r['subset'] == subset and r['backend'] == backend}
            bars = ax.bar(x + (i - .5) * .36, [rows[m]['count'] for m in labels], .36,
                          label='GPT-5.6 Luna' if backend == 'generator' else 'Jev',
                          color=('#3976af', '#df893c')[i])
            ax.bar_label(bars, padding=3, fontsize=9)
        ax.set_xticks(x, labels, rotation=25, ha='right')
        ax.set_title(subset.replace('_', ' ') + f" (n={rows[labels[0]]['n']})")
        ax.set_ylabel('Targets')
        ax.spines[['top', 'right']].set_visible(False)
    axes[0][0].legend()
    fig.suptitle('Decider choices on the same target passages')
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(directory / f'mode_distribution.{ext}', dpi=180)
    plt.close(fig)
    rows = [r for r in modes if r['subset'].endswith('without_meetings')]
    if not rows:
        rows = [r for r in modes if r['subset'].endswith('all')]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar([r['mode'] for r in rows], [r['mean_best_score'] or 0 for r in rows], color='#3976af')
    ax.bar_label(bars, labels=[f"{r['mean_best_score'] or 0:.2f}\nn={r['scored']}" for r in rows], padding=4)
    ax.set_ylim(0, 44)
    ax.set_ylabel('Mean best candidate score (out of 40)')
    ax.set_title('Mode comparison: non-meeting targets with a scored candidate')
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(directory / f'mode_scores.{ext}', dpi=180)
    plt.close(fig)


def table(rows, columns):
    def fmt(value):
        if value is None:
            return '—'
        if isinstance(value, float):
            return f'{value:.2f}'
        return str(value).replace('|', ', ')
    return '\n'.join(['| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join('---' for _ in columns) + ' |']
        + ['| ' + ' | '.join(fmt(r.get(c)) for c in columns) + ' |' for r in rows])


def report(directory, summary, comparisons):
    cfg = summary['config']
    parts = ['# Decider screening',
        (f"Run status: **{summary['status']}**. Seed {cfg['seed']}; "
        f"{cfg['un']} UN documents and {cfg['eurlex']} EUR-Lex acts, one English target per document/act. "
        f"Generator/standard decider: `{cfg['generator']}`. Verifier: `{cfg['verifier']}`. "
        f"Jev: `{cfg['jev_model']}`."),
        '## Design and interpretation',
        ('The sample is deterministic and stratified, not a representative corpus-frequency estimate. '
        'UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit '
        'and reference-completeness filters. The complete assembled payload is identical across '
        'both deciders and every generation mode. Each mode gets one generation batch (up to three '
        'candidates), followed by the existing faithfulness and mode-specific quality verifiers. '
        'Generation does not see either decider’s answer.'),
        ('“All modes” means the modes offered to the decider: lookup/practitioner/conceptual (formerly semantic) for UN '
        'and fact_pattern/lookup for EUR-Lex. Legacy technical/descriptive modes are outside this comparison. '
        + ('All three modes are eligible on UN meeting records, as on other UN documents.'
           if cfg.get('meeting_modes') == 'all' else
           'In this historical run, meeting records permit only semantic or skip; '
           'lookup/practitioner trials are diagnostic and cannot win.')),
        ('Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. '
        'For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed '
        'eligible mode in this single run, retaining ties—not human-labeled ground truth. '
        'Different quality rubrics assess different properties, so score comparisons are screening evidence. '
        'A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking '
        'candidates are excluded there.'),
        ('Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; '
        '0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete '
        'eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means '
        'a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. '
        'No accuracy claim or optimal-skip threshold is possible without human labels. '
        'Bootstrap intervals resample these targets and do not capture model rerun variability.'),
        (f"Original failed tasks: {summary['original_failed_tasks']}; successfully repaired: "
         f"{len(summary['repaired_tasks'])}. Repairs reuse generation and successful verifier stages. "
         'The faithfulness retry adds only an explicit actual-batch-size instruction to avoid '
         'fabricated extra grade objects when fewer than three candidates were supplied. '
         'The grading rubric is unchanged. Original calls remain in `run.sqlite`; '
         'repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). '
         'Where surrounding prose prevented parsing, an unambiguous grade array was recovered '
         'only after validating the exact count, indices, score ranges, and required fields; '
         'no extra grade objects were silently discarded. '
         'One quality response omitted positional indices; those were restored from exact, '
         'unique candidate IDs in the recorded input, followed by full schema validation. '
         'The earliest valid recorded response was used, without changing its scores. '
         'Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome '
         'rather than an isolated causal effect of framing.'),
        '## Mode distributions',
        table(summary['distributions'], ['subset', 'backend', 'mode', 'count', 'n', 'percent']),
        '![Mode distribution](mode_distribution.png)',
        '## All-mode score comparison',
        table(summary['modes'], ['subset', 'mode', 'eligible', 'scored', 'generated_candidates', 'no_candidates',
             'mean_best_score', 'mean_best_faithfulness', 'mean_best_quality',
             'oracle_wins_including_ties', 'best_candidate_blocking', 'audit_clear_targets']),
        '![Mode scores](mode_scores.png)',
        '## Decider performance against observed scores',
        table(summary['policies'], ['subset', 'backend', 'routed', 'scored_selected', 'skipped',
            'matches_oracle', 'oracle_available', 'missed_score_opportunities',
            'selected_mode_unproductive_despite_alternative',
            'mean_selected_score_when_available', 'mean_regret_when_scored',
            'mean_utility_zero_for_skip_or_no_candidate', 'mean_audit_clear_utility', 'mean_oracle_utility']),
        '## Paired Jev versus standard-decider comparison',
        table(summary['agreement'], ['subset', 'valid_pairs', 'agree', 'generator_better_utility',
            'jev_better_utility', 'utility_ties', 'mean_paired_utility_difference_generator_minus_jev',
            'bootstrap_95_interval']),
        '## Disagreements for manual review',
        table([r for r in comparisons if r['deciders_agree'] is False],
              ['symbol', 'target_id', 'generator_mode', 'jev_mode', 'oracle_modes',
               'lookup_score', 'practitioner_score', 'conceptual_score', 'semantic_score']),
        '## Recorded usage',
        table(summary['usage'], ['stage', 'model', 'calls', 'provider_errors', 'prompt_tokens',
             'completion_tokens', 'reported_cost', 'calls_missing_cost']),
        'Reported cost is in USD where provided. Missing provider costs are unknown, not zero.',
        '## Artifacts',
        ('- [Documents and full source payloads](documents.csv)\n'
        '- [Documents and decisions, including reasons/probabilities](decisions.csv)\n'
        '- [Per-document comparison and regrets](document_comparison.csv)\n'
        '- [All generated questions and verifier grades](all_mode_candidates.csv)\n'
        '- [Per-target mode scores, questions, answers and statuses](mode_scores.csv)\n'
        '- [Mode distributions](mode_distribution.csv)\n'
        '- [Decider metrics](decider_performance.csv)\n'
        '- [Pairwise confusion counts](confusion.csv)\n'
        '- [Provider call trace](trace.md) and [raw trace](llm_calls.json)\n'
        '- [Reproducible configuration](config.json), [selection](selection.json), and `run.sqlite`'),
    ]
    (directory / 'analysis.md').write_text('\n\n'.join(parts) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    summary = analyze(args.directory)
    print(json.dumps({'status': summary['status'], 'outcomes': summary['outcomes'],
                      'agreement': summary['agreement']}, indent=2))


if __name__ == '__main__':
    main()
