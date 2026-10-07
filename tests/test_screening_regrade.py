import json

import pytest

from clir_bench.core import grading
from clir_bench.domains.legal.qac.screening_regrade import merge_grades


def test_regrade_preserves_candidate_identity_and_replaces_old_scores_before_ranking():
    keys = ('search_realism', 'anchoring_and_time', 'consequence', 'lexical_distance', 'linguistic_quality')
    candidates = [{'candidate_id': name, 'question': f'Question {name}', 'answer': f'Answer {name}'}
                  for name in ('a', 'b')]
    originals = [dict(c, mode='comparison', generator_model_id='original-generator',
                      total_score=40, qual_obsolete=5, quality_audit_status='blocking',
                      evidence='Original evidence', comparison_entities='["x", "y"]')
                 for c in reversed(candidates)]
    faith = [dict(grounding=5, precision=5, numerical_fidelity=5, overall=15) for _ in candidates]
    response = {'candidates': [
        {'candidate_id': c['candidate_id'], 'index': i, 'scores': dict.fromkeys(keys, i + 3),
         'score_notes': dict.fromkeys(keys, 'Evidence'),
         'checks': dict.fromkeys(('mode', 'support', 'metadata'), 'pass'), 'problems': []}
        for i, c in enumerate(candidates)], 'batch_diversity': 'pass'}
    quality = grading._normalize_compact_quality(response, keys, candidates, 'comparison')
    before = json.dumps(originals, sort_keys=True)
    rows = merge_grades(originals, candidates, faith, quality, 'gpt-6-luna',
                        {'faithfulness': 'Saved faith prompt', 'quality': 'Saved quality prompt'})
    assert [r['candidate_id'] for r in rows] == ['b', 'a']
    assert [r['total_score'] for r in rows] == [35, 30]
    assert [r['candidate_rank'] for r in rows] == [1, 2]
    assert json.dumps(originals, sort_keys=True) == before
    for row in rows:
        assert row['question'] == f"Question {row['candidate_id']}"
        assert row['answer'] == f"Answer {row['candidate_id']}"
        assert row['evidence'] == 'Original evidence'
        assert row['generator_model_id'] == 'original-generator'
        assert row['quality_audit_status'] == 'clear'
        assert row['faithfulness_verifier_model'] == row['quality_verifier_model'] == 'gpt-6-luna'
        assert 'qual_obsolete' not in row


def test_verifier_comparison_pairs_by_id_and_rejects_changed_questions(tmp_path):
    from clir_bench.domains.legal.qac.screening_analysis import write_csv
    from clir_bench.domains.legal.qac.screening_regrade import compare_verifiers

    old_dir, new_dir = tmp_path / 'old', tmp_path / 'new'
    old_dir.mkdir()
    new_dir.mkdir()
    old = [dict(corpus='un', document_id='doc', target_id='doc#0', screening_mode='lookup',
                candidate_id=str(i), question=f'Question {i}', answer='Answer', total_score=score,
                faith_overall=15, qual_overall=score - 15, quality_audit_status='clear')
           for i, score in enumerate((35, 30))]
    new = [dict(old[1], total_score=34, qual_overall=19), dict(old[0], total_score=33, qual_overall=18)]
    write_csv(old_dir / 'all_mode_candidates.csv', old)
    write_csv(new_dir / 'all_mode_candidates.csv', new)
    summary = compare_verifiers(old_dir, new_dir)[0]
    assert summary['mean_total_delta'] == 1
    assert summary['new_higher'] == summary['new_lower'] == 1
    new[0]['question'] = 'Different question'
    write_csv(new_dir / 'all_mode_candidates.csv', new)
    with pytest.raises(ValueError, match='identity or text changed'):
        compare_verifiers(old_dir, new_dir)
