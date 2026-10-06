"""Compare saved UN runs only; no model calls or changes to pipeline prompts."""
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from statistics import mean
import csv
import json

from summarize_run import ROOT, average, best, mode, read_csv, statistics, table, fmt

OUT = ROOT / 'comparison'
HISTORY = ROOT.parent / 'legal_20260930'
RUNS = {
    'Original': ROOT.parents[1] / 'decider_screening/fresh100_20260930_examples',
    'Revised': HISTORY / 'debiased/run',
    'Simple': HISTORY / 'simple/run',
}
VERSIONS = (*RUNS, 'v4')
MODES = ('lookup', 'practitioner', 'semantic')
ACCEPTED = ('clear', 'minor_issues')


def csv_out(name, rows):
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def metrics(rows, attempted):
    result = statistics(rows)
    selected = best(rows)
    generated = len({row['target_id'] for row in rows})
    accepted = [row for row in rows if row.get('quality_audit_status') in ACCEPTED
                and row.get('grading_status') == 'completed' and float(row['faith_grounding']) >= 3]
    result.update(attempted_documents=attempted, documents_without_questions=attempted-generated,
                  documents_with_no_eligible_best=attempted-len(selected),
                  accepted_candidates=len(accepted),
                  accepted_best=sum(row.get('quality_audit_status') in ACCEPTED for row in selected),
                  accepted_targets=len({row['target_id'] for row in accepted}),
                  candidate_count_distribution=dict(Counter(Counter(row['target_id'] for row in rows).values())))
    return result


def main():
    OUT.mkdir(exist_ok=True)
    selection = json.loads((ROOT / 'selection.json').read_text())
    assert len(selection) == len({r['document_id'] for r in selection}) == 50
    ids = {row['target_id'] for row in selection}
    hashes = {row['target_id']: row['source_payload_sha256'] for row in selection}
    strata = {row['target_id']: row['stratum'] for row in selection}
    banks = {version: [row for row in read_csv(path / 'all_mode_candidates.csv') if row['corpus'] == 'un']
             for version, path in RUNS.items()}
    banks['v4'] = read_csv(ROOT / 'results.csv')
    decisions = {version: [row for row in read_csv(path / 'decisions.csv') if row['corpus'] == 'un']
                 for version, path in RUNS.items()}
    decisions['v4'] = [dict(row, backend='jev', status='completed')
                       for row in json.loads((ROOT / 'decisions.json').read_text())]
    for rows in banks.values():
        assert all(row['target_id'] in ids and row['source_payload_sha256'] == hashes[row['target_id']]
                   and row['grading_status'] == 'completed' for row in rows)
    for version in RUNS:
        old_selection = [row for row in json.loads((RUNS[version] / 'selection.json').read_text()) if row['corpus'] == 'un']
        assert {row['target_id']: row['source_payload_sha256'] for row in old_selection} == hashes
    routes = {}
    routing = []
    for version, rows in decisions.items():
        for backend in ('jev', 'generator'):
            subset = [row for row in rows if row['backend'] == backend]
            if not subset:
                continue
            assert len(subset) == 50 and all(row['status'] == 'completed' for row in subset)
            routes[version, backend] = {row['target_id']: row['mode'] for row in subset}
            counts = Counter(row['mode'] for row in subset)
            routing.append({'version': version, 'router': backend, 'documents': 50,
                            **{m: counts[m] for m in (*MODES, 'skip')}})
    v4_routes = routes['v4', 'jev']
    assert v4_routes == routes['Revised', 'jev']

    # Every historical persona was attempted on all50 documents. v4 contains only routed modes.
    observed = []
    for version, rows in banks.items():
        for persona in MODES:
            attempted = 50 if version != 'v4' else sum(chosen == persona for chosen in v4_routes.values())
            observed.append({'version': version, 'mode': persona, **metrics([r for r in rows if mode(r) == persona], attempted)})
    cohort = []
    cohorts = {persona: {target for target, chosen in v4_routes.items() if chosen == persona} for persona in MODES}
    for persona, targets in cohorts.items():
        if not targets:
            continue
        subsets = {version: [r for r in rows if r['target_id'] in targets and mode(r) == persona]
                   for version, rows in banks.items()}
        generated_intersection = set.intersection(*({r['target_id'] for r in rows} for rows in subsets.values()))
        best_intersection = set.intersection(*({r['target_id'] for r in best(rows)} for rows in subsets.values()))
        for population, target_set in [('v4_routed_documents', targets),
                                       ('all_versions_generated', generated_intersection),
                                       ('all_versions_have_eligible_best', best_intersection)]:
            for version, rows in subsets.items():
                cohort.append({'version': version, 'mode': persona, 'population': population,
                               **metrics([r for r in rows if r['target_id'] in target_set], len(target_set))})

    routed, routed_rows = [], {}
    for version, rows in banks.items():
        chosen = routes[version, 'jev']
        subset = [row for row in rows if mode(row) == chosen[row['target_id']]]
        routed_rows[version] = subset
        routed.append({'version': version, 'router': 'jev', **metrics(subset, 50),
                       'decider_skips': sum(value == 'skip' for value in chosen.values())})
    accuracy = []
    for version, path in RUNS.items():
        for row in read_csv(path / 'decider_performance.csv'):
            if row['subset'] != 'un_all':
                continue
            n, hits = int(row['oracle_available']), int(row['matches_oracle'])
            accuracy.append({'version': version, 'router': row['backend'], 'scorable_documents': n,
                             'best_mode_matches_including_ties': hits, 'match_percent': hits / n * 100})
    accuracy.append({'version': 'v4', 'router': 'jev', 'scorable_documents': None,
                     'best_mode_matches_including_ties': None, 'match_percent': None})

    check_rows, components, genre = [], [], []
    for version in ('Revised', 'v4'):
        for persona in MODES:
            rows = [r for r in routed_rows[version] if mode(r) == persona]
            if not rows:
                continue
            for aggregation, values in [('all_candidates', rows), ('best_per_document', best(rows))]:
                for check in ('mode', 'support', 'metadata'):
                    for status in ('pass', 'fail', 'uncertain'):
                        affected = [r for r in values if r.get(f'quality_{check}_status') == status]
                        check_rows.append({'version': version, 'mode': persona, 'aggregation': aggregation,
                                           'check': check, 'status': status, 'count': len(affected),
                                           'denominator': len(values), 'percent': len(affected) / len(values) * 100,
                                           'affected_documents': len({r['target_id'] for r in affected})})
                fields = sorted({key for r in values for key, value in r.items()
                                 if key.startswith(('faith_', 'qual_')) and value and
                                 key not in ('faith_reason', 'qual_reason', 'qual_failure_type', 'faith_overall', 'qual_overall')})
                for key in fields:
                    numeric = []
                    for row in values:
                        try:
                            numeric.append(float(row[key]))
                        except (KeyError, ValueError, TypeError):
                            pass
                    if numeric:
                        components.append({'version': version, 'mode': persona, 'aggregation': aggregation,
                                           'criterion': key, 'n': len(numeric), 'mean_5': mean(numeric)})
        for stratum in ('resolution', 'meeting', 'letter'):
            subset = [r for r in routed_rows[version] if strata[r['target_id']] == stratum]
            genre.append({'version': version, 'stratum': stratum,
                          **metrics(subset, sum(s == stratum for s in strata.values()))})

    paired = []
    previous_best = {r['target_id']: r for r in best(routed_rows['Revised'])}
    current_best = {r['target_id']: r for r in best(routed_rows['v4'])}
    for persona in ('all', 'practitioner', 'semantic'):
        targets = ids if persona == 'all' else cohorts[persona]
        common = sorted(targets & previous_best.keys() & current_best.keys())
        for score in ('faith_overall', 'qual_overall', 'total_score'):
            differences = [float(current_best[target][score]) - float(previous_best[target][score]) for target in common]
            paired.append({'mode': persona, 'score': score, 'matched_documents': len(common),
                           'mean_difference_v4_minus_revised': mean(differences),
                           'v4_higher': sum(v > 0 for v in differences), 'tied': sum(v == 0 for v in differences),
                           'v4_lower': sum(v < 0 for v in differences)})
    manual = [row for row in json.loads((HISTORY / 'manual_review/summary.json').read_text())['mode_summaries'] if row['corpus'] == 'un']
    details = {
        'method': {'documents': 50, 'language': 'en', 'strata': dict(Counter(strata.values())),
                   'input_hashes_match': True, 'new_provider_calls': 0,
                   'native_best_rule': 'Completed grades; grounding >=3; highest total; stable recorded rank breaks ties. Audit acceptance is separate.',
                   'acceptance_rule': 'Completed grades; grounding >=3; quality audit clear or minor_issues.',
                   'mean_rule': 'No zero imputation for missing candidates, scores or unrun modes. All-candidate means weight questions; best means weight eligible documents.',
                   'v4_prompt_scope': 'UN practitioner generation and quality plus UN faithfulness v4; Jev remains Revised v2. Other generation/quality prompts remain Revised v2.',
                   'limitations': ['Native verifiers differ across variants; score changes are not causal estimates of quality or verifier accuracy.',
                                   'v4 ran only the selected mode; no current lookup observations or best-mode accuracy estimate.',
                                   'Candidate counts vary; choosing the best of a larger batch can change best-candidate means.',
                                   'The old all-mode sample attempts 50 documents per mode; v4 attempts44 practitioner and6 semantic. Matched-cohort tables address that coverage difference.',
                                   'Historical manual review covered20 UN documents and did not include v4. The v4 four-question spot check is not comparable to that review.']},
        'routing': routing, 'observed_mode_scores': observed, 'matched_cohort_scores': cohort,
        'jev_routed_pipeline': routed, 'native_best_mode_matches': accuracy,
        'check_results': check_rows, 'criterion_means': components, 'genre_scores': genre,
        'paired_best_changes': paired, 'historical_manual_review': manual,
        'v4_spot_check': json.loads((ROOT / 'manual_spot_check.json').read_text()),
    }
    (OUT / 'analysis.json').write_text(json.dumps(details, ensure_ascii=False, indent=2) + '\n')
    for name, rows in [('routing', routing), ('observed_mode_scores', observed), ('matched_cohort_scores', cohort),
                       ('jev_routed_pipeline', routed), ('native_best_mode_matches', accuracy),
                       ('check_results', check_rows), ('criterion_means', components),
                       ('genre_scores', genre), ('paired_best_changes', paired)]:
        # Nested distributions remain explicit JSON cells in the CSV.
        csv_out(name + '.csv', [{k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows])

    sections = []
    def section(title, prose, headers, rows):
        sections.append('<section><h2>' + escape(title) + '</h2><p>' + escape(prose) + '</p>' + table(headers, rows) + '</section>')
    section('Persona choices: Jev', 'Counts out of the same50 documents. All50 v4 choices exactly match Revised. The v4 update did not change the decider prompt.',
            ['Version', 'Lookup', 'Practitioner', 'Semantic', 'Skip'],
            [[r['version'], r['lookup'], r['practitioner'], r['semantic'], r['skip']] for r in routing if r['router'] == 'jev'])
    section('Historical generator-router choices', 'The current run used Jev only. These are the earlier generator-router results, not new measurements.',
            ['Version', 'Lookup', 'Practitioner', 'Semantic', 'Skip'],
            [[r['version'], r['lookup'], r['practitioner'], r['semantic'], r['skip']] for r in routing if r['router'] == 'generator'])
    section('Scores by persona: all observed candidates', 'F=faithfulness/15; Q=quality/25. Original, Revised and Simple attempted50 documents for EACH mode, including alternatives not selected by the router. v4 generated only its selected modes. An unrun mode is unavailable, not a zero score.',
            ['Version', 'Persona', 'Attempted docs', 'Docs with questions', 'Questions', 'All F', 'All Q', 'Best docs', 'Best F', 'Best Q'],
            [[r['version'], r['mode'], r['attempted_documents'], r['targets_with_candidates'], r['candidates'],
              fmt(r['mean_candidate_faithfulness_15']), fmt(r['mean_candidate_quality_25']), r['best_candidates'],
              fmt(r['mean_best_faithfulness_15']), fmt(r['mean_best_quality_25'])] for r in observed])
    for persona in ('practitioner', 'semantic'):
        section(f'Matched {persona} documents selected by v4', 'Every historical bank is restricted to these exact v4-routed documents, whether or not its historical router chose this persona. Missing or ungrounded outputs are excluded from means and shown in coverage.',
                ['Version', 'Attempted docs', 'Docs with questions', 'Questions', 'All F /15', 'All Q /25', 'Best docs', 'Best F /15', 'Best Q /25'],
                [[r['version'], r['attempted_documents'], r['targets_with_candidates'], r['candidates'],
                  fmt(r['mean_candidate_faithfulness_15']), fmt(r['mean_candidate_quality_25']), r['best_candidates'],
                  fmt(r['mean_best_faithfulness_15']), fmt(r['mean_best_quality_25'])]
                 for r in cohort if r['mode'] == persona and r['population'] == 'v4_routed_documents'])
    section('Strict matched practitioner comparison', 'Only documents where ALL four variants have a grounding-eligible best candidate. This controls differing output coverage, but cannot control rubric changes or differing numbers of candidates.',
            ['Version', 'Same documents', 'Best F /15', 'Best Q /25', 'Best total /40'],
            [[r['version'], r['attempted_documents'], fmt(r['mean_best_faithfulness_15']), fmt(r['mean_best_quality_25']), fmt(r['mean_best_total_40'])]
             for r in cohort if r['mode'] == 'practitioner' and r['population'] == 'all_versions_have_eligible_best'])
    section('Normal Jev-routed pipeline comparison', 'Historical pipelines are reconstructed by taking only the persona Jev selected for each document. Best means condition on an eligible output; acceptance is an automated audit result, not human validation.',
            ['Version', 'Skip', 'Questions', 'Best docs /50', 'Best F /15', 'Best Q /25', 'Accepted questions', 'Docs with accepted option /50', 'Accepted selected best'],
            [[r['version'], r['decider_skips'], r['candidates'], r['best_candidates'], fmt(r['mean_best_faithfulness_15']),
              fmt(r['mean_best_quality_25']), f"{r['accepted_candidates']}/{r['candidates']}", r['accepted_targets'], f"{r['accepted_best']}/{r['best_candidates']}"] for r in routed])
    section('Did the decider pick the highest-scoring persona?', 'Historical rates compare native best scores across all generated personas; ties count as matches. Original excludes3 documents with no scorable persona. v4 lacks the alternative generations, so its match rate cannot be measured.',
            ['Version', 'Router', 'Matches', 'Scorable documents', 'Percent'],
            [[r['version'], r['router'], r['best_mode_matches_including_ties'], r['scorable_documents'], fmt(r['match_percent'])] for r in accuracy])
    section('Checks on the selected best practitioner question', 'Counts are out of44 in both versions. A question can fail more than one check. Normal ranking uses total score and grounding; a failed mode or metadata check does not automatically remove it.',
            ['Version', 'Check', 'Status', 'Affected /44', 'Percent'],
            [[r['version'], r['check'], r['status'], r['count'], fmt(r['percent'])] for r in check_rows
             if r['mode'] == 'practitioner' and r['aggregation'] == 'best_per_document' and r['status'] != 'pass'])
    section('Practitioner component scores: all candidates in matched44', 'Each component is /5. The faithfulness and practitioner quality rubrics changed; these are observed scores, not a fixed-question test of grader accuracy.',
            ['Version', 'Criterion', 'Questions', 'Mean /5'],
            [[r['version'], r['criterion'], r['n'], fmt(r['mean_5'])] for r in components
             if r['mode'] == 'practitioner' and r['aggregation'] == 'all_candidates'])
    section('Results by document genre', 'Same routed document groups before and after. Resolutions25, meeting records20, letters5.',
            ['Version', 'Genre', 'Documents', 'Questions', 'Best F /15', 'Best Q /25', 'Accepted selected best'],
            [[r['version'], r['stratum'], r['best_candidates'], r['candidates'], fmt(r['mean_best_faithfulness_15']),
              fmt(r['mean_best_quality_25']), r['accepted_best']] for r in genre])
    section('Paired changes in selected-best scores', 'Each document contributes once. Higher or lower refers to native score, not established true quality.',
            ['Persona', 'Score', 'Paired docs', 'Mean change', 'v4 higher', 'Tied', 'v4 lower'],
            [[r['mode'], r['score'], r['matched_documents'], fmt(r['mean_difference_v4_minus_revised']),
              r['v4_higher'], r['tied'], r['v4_lower']] for r in paired])
    section('Earlier agent review of question quality', 'Scores /5; document-balanced averages on the old review subsets where all3 variants generated questions. These are agent judgments, not human gold labels. v4 has not received the same full blinded review.',
            ['Persona', 'Matched review docs', 'Original', 'Revised', 'Simple', 'v4'],
            [[r['mode'], r['matched_families'], *[fmt(r['versions'][v]['matched_family_mean']) for v in ('original', 'revised', 'simple')], 'Not reviewed equivalently'] for r in manual])
    example_ids = {
        'q_eacd96ee77ace8bd839be3a9': 'Supported answer, but a dated resolution locator and largely decorative practitioner role; selected best despite mode failure.',
        'q_a07f99ba7aeda0eb2dd1ff05': 'Attribution error: the trafficking-task-force request continues Ms Hazelle; Ms Khan starts in the next paragraph.',
        'q_5f07222f57e9be1c2dc3e330': 'False premise: asks which nationality-based limitation applied while the source states reimbursement was irrespective of nationality.',
        'q_423ccc1c9939dc02a7b50674': 'Verifier mistake: its rationale says Colombia is missing, although the question explicitly says Colombian Government. Other timing or attribution concerns are separate.',
    }
    examples = []
    for candidate, finding in example_ids.items():
        row = next(r for r in banks['v4'] if r['candidate_id'] == candidate)
        examples.append({'candidate_id': candidate, 'target_id': row['target_id'], 'question': row['question'], 'answer': row['answer'],
                         'is_best': row['is_best'], 'faithfulness_15': row['faith_overall'], 'quality_25': row['qual_overall'],
                         'agent_observation': finding, 'verifier_notes': row['qual_reason']})
    (OUT / 'diagnostic_examples.json').write_text(json.dumps(examples, ensure_ascii=False, indent=2) + '\n')
    sections.append('<section><h2>Concrete remaining problems</h2><p>Source-checked agent observations; examples are illustrative, not prevalence estimates.</p>' + ''.join(
        '<article><p><strong>' + escape(r['target_id']) + '</strong> · ' + escape(r['candidate_id']) + '</p><p>' + escape(r['agent_observation']) + '</p><p>Question: ' + escape(r['question'])
        + '</p><blockquote>' + escape(r['answer']) + '</blockquote><p>Faithfulness ' + escape(r['faithfulness_15']) + '/15; quality ' + escape(r['quality_25']) + '/25; selected best: ' + escape(r['is_best']) + '</p></article>' for r in examples) + '</section>')
    body = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>UN persona and verifier comparison: Original, Revised, Simple, v4</title>'
            '<style>body{font:15px/1.55 system-ui;max-width:1450px;margin:30px auto;padding:0 20px;color:#1b2939}table{border-collapse:collapse;width:100%;font-size:14px}'
            'th,td{border-bottom:1px solid #dce1e7;padding:8px;text-align:left}th{background:#edf2f8}section{margin-top:36px;overflow-x:auto}'
            'article{padding:12px 20px;background:#f3f5f8;margin:14px 0}blockquote{border-left:3px solid #657b94;padding-left:15px}.lead{padding:18px;background:#edf3f9}</style>'
            '<h1>UN persona and verifier comparison</h1><p>Same50 UN documents; English; gpt-5.6-luna generation; Claude Sonnet5.5 verification. '
            'This analysis uses existing saved results only.</p><div class="lead"><strong>Main finding:</strong> v4 retains Revised routing: '
            '44 practitioner,6 semantic,0 lookup,0 skip. Its practitioner questions receive higher average faithfulness scores and fewer audit flags, '
            'but the best-question quality score does not improve. The observed acceptance gain is not a measured improvement in verifier accuracy.</div>'
            '<p><a href="analysis.json">Full metrics JSON</a> · <a href="matched_cohort_scores.csv">Matched-cohort scores CSV</a> · '
            '<a href="observed_mode_scores.csv">All persona scores CSV</a> · <a href="check_results.csv">Verifier checks CSV</a> · '
            '<a href="../report.html">All v4 questions and sources</a></p>' + ''.join(sections)
            + '<section><h2>Interpretation limits</h2><ul>' + ''.join('<li>' + escape(item) + '</li>' for item in details['method']['limitations']) + '</ul></section></html>')
    (OUT / 'report.html').write_text(body, encoding='utf-8')
    show = ('version', 'mode', 'attempted_documents', 'targets_with_candidates', 'candidates',
            'mean_candidate_faithfulness_15', 'mean_candidate_quality_25', 'best_candidates',
            'mean_best_faithfulness_15', 'mean_best_quality_25')
    print(json.dumps({'routing': routing, 'matched_v4_cohorts': [{key: r[key] for key in show} for r in cohort if r['population'] == 'v4_routed_documents'],
                      'paired_best_changes': paired, 'report': str(OUT / 'report.html')}, indent=2))


if __name__ == '__main__':
    main()
