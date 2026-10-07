"""Export fixed-candidate verifier comparisons without model identities."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean

from clir_bench.domains.legal.qac.screening_analysis import write_csv, table


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def grade_fields(candidate):
    response = json.loads(candidate.get('quality_verifier_response_json') or '{}')
    result = {name: candidate.get(key, '') for name, key in {
        'grading_status': 'grading_status', 'grounding_5': 'faith_grounding',
        'precision_5': 'faith_precision', 'numerical_fidelity_5': 'faith_numerical_fidelity',
        'faithfulness_15': 'faith_overall', 'quality_25': 'qual_overall', 'total_40': 'total_score',
        'audit_status': 'quality_audit_status', 'mode_check': 'quality_mode_status',
        'support_check': 'quality_support_status', 'metadata_check': 'quality_metadata_status',
        'batch_diversity': 'quality_batch_diversity', 'faithfulness_reason': 'faith_reason',
        'quality_score_notes_json': 'quality_score_notes_json', 'problems_json': 'quality_problems_json',
        'grading_error': 'grading_error', 'candidate_rank': 'candidate_rank',
    }.items()}
    notes = json.loads(candidate.get('quality_score_notes_json') or '{}')
    problems = json.loads(candidate.get('quality_problems_json') or '[]')
    result['quality_reason'] = '\n'.join(f'{criterion}: {reason}' for criterion, reason in notes.items())
    result['audit_reason'] = '\n'.join(problems) if problems else ('No problems reported.' if candidate else '')
    result['quality_scores_json'] = json.dumps(response.get('scores', {}), ensure_ascii=False)
    return result


def statistics(rows, label, *, corpus='all', mode='all'):
    selected = [r for r in rows if (corpus == 'all' or r['corpus'] == corpus)
                and (mode == 'all' or r['screening_mode'] == mode)]
    scored = [r for r in selected if r['grading_status'] == 'completed' and r.get('total_score')]
    audits = Counter(r.get('quality_audit_status') for r in selected if r['grading_status'] == 'completed')
    result = {'verifier': label, 'corpus': corpus, 'mode': mode, 'candidates': len(selected),
              'completed': sum(r['grading_status'] == 'completed' for r in selected), 'scored': len(scored)}
    for field, column in [('faith_overall', 'mean_faithfulness_15'), ('qual_overall', 'mean_quality_25'),
                          ('total_score', 'mean_total_40')]:
        result[column] = mean(float(r[field]) for r in scored) if scored else None
    for status in ('clear', 'minor_issues', 'repair', 'blocking', 'review'):
        result[status] = audits[status]
    result['audit_pass'] = audits['clear'] + audits['minor_issues']
    result['audit_pass_percent'] = 100 * result['audit_pass'] / len(selected) if selected else None
    result['perfect_40'] = sum(float(r['total_score']) == 40 for r in scored)
    return result


def export_blinded(directories, output):
    datasets = [read_csv(p / 'all_mode_candidates.csv') for p in directories]
    indexes = [{r['candidate_id']: r for r in rows} for rows in datasets]
    baseline = indexes[0]
    identity = ('corpus', 'document_id', 'target_id', 'screening_mode', 'question', 'answer')
    models = []
    for directory, rows, index in zip(directories, datasets, indexes):
        if len(index) != len(rows) or index.keys() != baseline.keys():
            raise ValueError('Candidate populations must be identical and unique')
        for cid, candidate in index.items():
            if any(candidate[key] != baseline[cid][key] for key in identity):
                raise ValueError(f'Candidate content changed: {cid}')
        models.append(json.loads((directory / 'config.json').read_text())['verifier'])
    # Remove identities even if a verifier happens to name itself in an explanation.
    replacements = {}
    for position, model in enumerate(models, 1):
        label = f'verifier {position}'
        replacements[model] = replacements[model.rsplit('/', 1)[-1]] = label
        replacements[model.rsplit('/', 1)[-1].replace('-', ' ')] = label
    pattern = re.compile('|'.join(re.escape(k) for k in sorted(replacements, key=len, reverse=True)), re.I)
    lower_replacements = {k.lower(): v for k, v in replacements.items()}

    def scrub(value):
        return pattern.sub(lambda m: lower_replacements[m.group().lower()], value) if isinstance(value, str) else value

    documents = read_csv(directories[0] / 'documents.csv')
    decisions = {(r['corpus'], r['target_id']): r for r in read_csv(directories[0] / 'decisions.csv')
                 if r['backend'] == 'jev'}
    modes = read_csv(directories[0] / 'mode_scores.csv')
    config = json.loads((directories[0] / 'config.json').read_text())
    run_modes = config['modes_by_source']
    all_modes = list(dict.fromkeys(mode for values in run_modes.values() for mode in values))
    shared = ('candidate_id', 'question', 'answer', 'question_cited', 'evidence', 'claim', 'claim_status',
              'comparison_entities', 'comparison_aspect', 'source_identifier', 'source_article',
              'anchor', 'anchors', 'particulars', 'framing', 'question_type', 'instrument_short_name',
              'articles_involved', 'answer_is_translation', 'evidence_is_translation')
    long_rows, wide_rows = [], []
    for document in documents:
        key = document['corpus'], document['target_id']
        decision = decisions[key]
        common = {k: document.get(k, '') for k in ('corpus', 'document_id', 'target_id', 'symbol', 'title',
                                                  'document_text', 'source_payload')}
        common.update(decider_pick=decision['mode'], decider_confidence=decision.get('confidence', ''))
        wide = dict(common)
        for mode in all_modes:
            result = next((r for r in modes if (r['corpus'], r['target_id'], r['mode']) == (*key, mode)), None)
            group = [r for r in datasets[0] if (r['corpus'], r['target_id'], r['screening_mode']) == (*key, mode)]
            wide[f'{mode}__status'] = result['status'] if result else 'not_applicable_to_corpus'
            wide[f'{mode}__no_question_reason'] = result.get('generation_skip_reason', '') if result else ''
            wide[f'{mode}__candidate_count'] = len(group) if result else ''
            for slot in range(max(3, len(group))):
                candidate = group[slot] if slot < len(group) else {}
                row = dict(common, mode=mode, mode_status=wide[f'{mode}__status'],
                           generation_skip_reason=wide[f'{mode}__no_question_reason'])
                for field in shared:
                    row[field] = candidate.get(field, '')
                    wide[f'{mode}__{field}_{slot + 1}'] = row[field]
                for position, index in enumerate(indexes, 1):
                    label = f'verifier {position}'
                    grades = grade_fields(index[candidate['candidate_id']]) if candidate else dict.fromkeys(grade_fields({}), '')
                    for field, value in grades.items():
                        row[f'{label}__{field}'] = value
                        wide[f'{mode}__{label}__{field}_{slot + 1}'] = value
                if candidate or (slot == 0 and result and result['status'] == 'no_candidates'):
                    long_rows.append(row)
            if result and len(group) != int(result['candidate_count']):
                raise ValueError('Mode and candidate counts disagree')
        wide_rows.append(wide)
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in [('all_verifier_grades.csv', long_rows), ('all_modes_per_document.csv', wide_rows)]:
        write_csv(output / name, [{k: scrub(v) for k, v in row.items()} for row in rows])
    overall, by_mode, by_corpus, deltas = [], [], [], []
    for position, rows in enumerate(datasets, 1):
        label = f'verifier {position}'
        overall.append(statistics(rows, label))
        for corpus, values in run_modes.items():
            by_corpus.append(statistics(rows, label, corpus=corpus))
            by_mode.extend(statistics(rows, label, corpus=corpus, mode=mode) for mode in values)
        differences = [float(r['total_score']) - float(baseline[r['candidate_id']]['total_score'])
                       for r in rows if r['grading_status'] == 'completed' and r.get('total_score')
                       and baseline[r['candidate_id']].get('total_score')]
        deltas.append({'verifier': label, 'paired_candidates': len(differences),
                       'mean_delta_vs_verifier_1': mean(differences) if differences else None,
                       'higher': sum(d > 0 for d in differences), 'lower': sum(d < 0 for d in differences),
                       'equal': sum(d == 0 for d in differences)})
    for name, rows in [('overall_statistics.csv', overall), ('corpus_statistics.csv', by_corpus),
                       ('mode_statistics.csv', by_mode), ('comparison_to_verifier_1.csv', deltas)]:
        write_csv(output / name, rows)
    skip_count = sum(r['status'] == 'no_candidates' for r in modes)
    report = [f'# {len(datasets)}-verifier comparison',
        f'{len(baseline)} unchanged questions from {len(documents)} documents. Each verifier assessed both '
        'faithfulness and mode-specific quality. Generation and decider choices are fixed. '
        f'The original {skip_count} generation skips are represented explicitly in the exports, with blank grade cells.',
        'Statistics average all candidates, paired by candidate ID; they are not best-per-document averages. '
        'A numeric total /40 is faithfulness /15 plus quality /25. Audit pass means clear or minor issues. '
        'A high score does not override a failed audit check.',
        table(overall, ['verifier', 'scored', 'mean_faithfulness_15', 'mean_quality_25', 'mean_total_40',
                        'perfect_40', 'audit_pass', 'audit_pass_percent']),
        '## Audit outcomes', table(overall, ['verifier', 'clear', 'minor_issues', 'repair', 'blocking', 'review']),
        '## Changes relative to verifier 1', table(deltas, list(deltas[0])),
        '## Per-mode candidate averages', table(by_mode, ['verifier', 'corpus', 'mode', 'candidates',
                                                         'mean_total_40', 'audit_pass', 'audit_pass_percent']),
        '## Files', '- [All five grades per question](all_verifier_grades.csv)\n'
        '- [All modes side by side per document](all_modes_per_document.csv)\n'
        '- [Overall statistics](overall_statistics.csv)\n- [Per-mode statistics](mode_statistics.csv)']
    (output / 'statistics.md').write_text('\n\n'.join(report) + '\n')
    for path in output.iterdir():
        if path.suffix in ('.csv', '.md') and pattern.search(path.read_text(encoding='utf-8-sig')):
            raise ValueError(f'Model identity leaked into {path.name}')
    return {'documents': len(documents), 'candidates': len(baseline), 'verifiers': len(datasets),
            'long_rows': len(long_rows), 'wide_rows': len(wide_rows), 'statistics': overall}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, action='append', required=True,
                        help='Ordered run directories; their order defines verifier numbers')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export_blinded(args.run, args.output), indent=2))


if __name__ == '__main__':
    main()
