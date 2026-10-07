import csv
import json

from clir_bench.domains.legal.qac.screening_analysis import write_csv
from clir_bench.domains.legal.qac.screening_blinded import export_blinded


def test_export_preserves_all_grades_skips_and_removes_model_names(tmp_path):
    models = ['anthropic/claude-sonnet-5.5', 'gpt-6-luna', 'anthropic/claude-haiku-5.5',
              'google/gemini-3.8-flash', 'z-ai/glm-5.3-flash']
    directories = []
    for i, model in enumerate(models):
        path = tmp_path / f'input{i}'
        path.mkdir()
        directories.append(path)
        (path / 'config.json').write_text(json.dumps({'verifier': model, 'modes_by_source': {'un': ['lookup']}}))
        write_csv(path / 'all_mode_candidates.csv', [{
            'corpus': 'un', 'document_id': 'doc', 'target_id': 'doc#0', 'candidate_id': 'q1',
            'screening_mode': 'lookup', 'question': 'Which, exactly?', 'answer': 'The answer',
            'grading_status': 'completed', 'faith_overall': 15, 'qual_overall': 20 + i,
            'total_score': 35 + i, 'quality_audit_status': 'clear',
            'faith_reason': f'{model}: supported', 'quality_verifier_model': model,
            'quality_verifier_response_json': json.dumps({'scores': {'criterion': 4}}),
        }])
    write_csv(directories[0] / 'documents.csv', [
        {'corpus': 'un', 'document_id': d, 'target_id': d + '#0', 'document_text': 'Source, text\nnext line'}
        for d in ('doc', 'skipped')])
    write_csv(directories[0] / 'decisions.csv', [
        {'corpus': 'un', 'target_id': d + '#0', 'backend': 'jev', 'mode': 'lookup'}
        for d in ('doc', 'skipped')])
    write_csv(directories[0] / 'mode_scores.csv', [
        {'corpus': 'un', 'target_id': d + '#0', 'mode': 'lookup', 'status': status,
         'candidate_count': count, 'generation_skip_reason': 'No eligible content' if not count else ''}
        for d, status, count in [('doc', 'completed', 1), ('skipped', 'no_candidates', 0)]])
    output = tmp_path / 'blinded'
    result = export_blinded(directories, output)
    assert result['candidates'] == 1 and result['long_rows'] == result['wide_rows'] == 2
    with (output / 'all_verifier_grades.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]['question'] == 'Which, exactly?'
    assert rows[0]['document_text'] == 'Source, text\nnext line'
    for i in range(1, 6):
        assert rows[0][f'verifier {i}__total_40'] == str(34 + i)
        assert rows[0][f'verifier {i}__faithfulness_reason'] == f'verifier {i}: supported'
        assert rows[1][f'verifier {i}__total_40'] == ''
    assert rows[1]['mode_status'] == 'no_candidates'
    assert rows[1]['generation_skip_reason'] == 'No eligible content'
    for file in output.iterdir():
        for model in models:
            assert model not in file.read_text(encoding='utf-8-sig')
