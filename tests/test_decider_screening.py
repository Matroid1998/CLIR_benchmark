from clir_bench.domains.legal.qac.screening_analysis import compare_target, mode_summary


def test_document_export_keeps_all_modes_candidates_and_skip_reasons(tmp_path):
    import csv

    from clir_bench.domains.legal.qac.screening import task_id
    from clir_bench.domains.legal.qac.screening_analysis import document_question_rows, write_csv

    source = dict(record(), source_payload='Full context, with\nmultiple lines')
    lookup = dict(candidate(), candidate_id='lookup-1', question='Which, exactly?')
    conceptual = dict(candidate(37), candidate_id='conceptual-1', question='Why this measure?')
    outcomes = {
        task_id('decider', source, 'jev'): outcome([{'mode': 'lookup', 'confidence': .8}]),
        task_id('mode', source, 'lookup'): outcome([lookup]),
        task_id('mode', source, 'conceptual'): outcome([conceptual]),
        task_id('mode', source, 'comparison'): outcome([], 'no_candidates'),
    }
    rows = document_question_rows([source], outcomes,
        {'un': ['lookup', 'conceptual', 'comparison'], 'eurlex': ['fact_pattern', 'lookup']},
        {task_id('mode', source, 'comparison'): 'No supported comparison'})
    path = tmp_path / 'wide.csv'
    write_csv(path, rows)
    with path.open(encoding='utf-8-sig', newline='') as stream:
        exported = list(csv.DictReader(stream))
    assert len(exported) == 1
    row = exported[0]
    assert row['source_payload'] == source['source_payload']
    assert row['jev_pick'] == 'lookup'
    assert row['lookup__question_1'] == lookup['question']
    assert row['conceptual__question_1'] == conceptual['question']
    assert row['conceptual__total_40_1'] == '37'
    assert row['lookup__question_2'] == row['lookup__question_3'] == ''
    assert row['comparison__status'] == 'no_candidates'
    assert row['comparison__no_question_reason'] == 'No supported comparison'
    assert row['fact_pattern__status'] == 'not_applicable_to_corpus'


def record(meeting=False):
    return {'corpus': 'un', 'target_id': 'doc#0', 'document_id': 'doc', 'symbol': 'S/PV.1' if meeting else 'S/RES/1',
                'title': 'Source', 'is_meeting': meeting, 'stratum': 'meeting' if meeting else 'resolution',
                'document_text': 'Evidence'}


def candidate(score=35, grounding=4, audit='clear'):
    return {'grading_status': 'completed', 'total_score': score, 'faith_grounding': grounding,
                'faith_overall': 13, 'qual_overall': score - 13, 'quality_audit_status': audit,
                'question': 'Question', 'answer': 'Answer'}


def outcome(rows, status='completed'):
    return {'rows': rows, 'status': status, 'error': ''}


def test_best_score_enforces_grounding_and_exposes_audit_sensitivity():
    summary = mode_summary(record(), 'lookup', outcome([
        candidate(40, grounding=2), candidate(38, audit='blocking'), candidate(35)]))
    assert summary['best_score'] == 38
    assert summary['audit_clear_best_score'] == 35
    assert summary['best_audit_status'] == 'blocking'
    assert summary['graded_count'] == 3 and summary['grounded_count'] == 2


def test_meeting_all_modes_can_be_observed_winner():
    source = record(meeting=True)
    modes = [mode_summary(source, mode, outcome([candidate(score)]))
             for mode, score in [('lookup', 40), ('practitioner', 39), ('semantic', 32)]]
    row = compare_target(source, modes, {'generator': outcome([{'mode': 'semantic'}]),
                                         'jev': outcome([{'mode': 'skip'}])})
    assert row['oracle_modes'] == 'lookup' and row['oracle_best_score'] == 40
    assert row['generator_matches_best'] is False
    assert row['jev_utility'] == 0 and row['jev_missed_opportunity'] is True
    assert row['jev_selected_score'] is None


def test_historical_meeting_restriction_is_preserved_when_reanalyzing_old_runs():
    source = record(meeting=True)
    modes = [mode_summary(source, mode, outcome([candidate(score)]), meeting_modes='semantic_only')
             for mode, score in [('lookup', 40), ('practitioner', 39), ('semantic', 32)]]
    row = compare_target(source, modes, {'generator': outcome([{'mode': 'semantic'}])})
    assert row['oracle_modes'] == 'semantic' and row['oracle_best_score'] == 32
    assert row['generator_matches_best'] is True


def test_ties_are_retained_and_regret_measures_selected_best_candidate():
    source = record()
    modes = [mode_summary(source, mode, outcome([candidate(score)]))
             for mode, score in [('lookup', 37), ('practitioner', 37), ('semantic', 34)]]
    row = compare_target(source, modes, {'generator': outcome([{'mode': 'lookup'}]),
                                         'jev': outcome([{'mode': 'semantic'}])})
    assert row['oracle_modes'] == 'lookup|practitioner'
    assert row['generator_matches_best'] is True and row['generator_score_regret'] == 0
    assert row['jev_score_regret'] == 3 and row['jev_matches_best'] is False


def test_failed_eligible_mode_excludes_policy_comparison_instead_of_becoming_zero():
    source = record()
    modes = [mode_summary(source, 'lookup', outcome([], 'failed')),
             mode_summary(source, 'semantic', outcome([candidate()]))]
    row = compare_target(source, modes, {'generator': outcome([{'mode': 'semantic'}]),
                                         'jev': outcome([{'mode': 'skip'}])})
    assert row['generator_utility'] is None and row['jev_utility'] is None
    assert row['all_eligible_modes_completed'] is False


def test_grade_recovery_accepts_prose_but_never_extra_or_ambiguous_grades():
    import json

    from clir_bench.domains.legal.qac.screening_repair import extract_grades
    grade = {'index': 0, 'grounding': 4, 'precision': 4, 'numerical_fidelity': 5, 'reason': 'Supported'}
    raw = 'Explanation.\n```json\n' + json.dumps([grade]) + '\n```'
    assert extract_grades(raw, 1)[0]['overall'] == 13
    assert extract_grades(json.dumps([grade, dict(grade, index=1)]), 1) is None
    assert extract_grades(raw + '\n' + json.dumps([dict(grade, grounding=2)]), 1) is None
    assert extract_grades(json.dumps([dict(grade, grounding=8)]), 1) is None


def test_quality_recovery_uses_authoritative_candidate_identity_without_changing_scores():
    import json

    from clir_bench.core.grading import rubric_keys
    from clir_bench.domains.legal.qac.screening_repair import recover_quality
    from clir_bench.domains.legal.qac.un_generate import PROMPTS

    prompt = PROMPTS.quality('lookup', 'batch')
    row = {'candidate_id': 'q1', 'question': 'Which deadline?', 'answer': '1999'}
    grade = {'candidate_id': 'q1', 'scores': dict.fromkeys(rubric_keys(prompt), 4),
             'score_notes': dict.fromkeys(rubric_keys(prompt), 'Supported'),
             'checks': dict.fromkeys(('mode', 'support', 'metadata'), 'pass'), 'problems': []}
    body = {'candidates': [grade], 'batch_diversity': 'not_applicable'}
    request = {'messages': [{'content': prompt}, {'content': json.dumps({'candidates': [row]})}],
               'response': {'choices': [{'message': {'content': json.dumps(body)}}]}}
    result = recover_quality(request, prompt, [row], 'lookup')
    assert result[0]['overall'] == 20
    assert result[0]['_response']['index'] == 0
    assert result[0]['_response']['scores'] == grade['scores']
    assert recover_quality(request, prompt, [dict(row, candidate_id='unknown')], 'lookup') is None
