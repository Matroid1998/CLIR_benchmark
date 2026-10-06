"""Retain raw run; recover recorded schemas and retry only missing quality grades."""
from pathlib import Path
import csv
import json
import sqlite3

from clir_bench.core import grading, llm
from clir_bench.core.prompt_registry import read_manifest, write_manifest
from clir_bench.domains.legal.qac import _rank, _write_csv
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.env import load_env
from clir_bench.domains.legal.qac.screening_repair import recover_quality

ROOT = Path(__file__).resolve().parent


def main():
    load_env()
    with sqlite3.connect(f"file:{ROOT / 'run/run.sqlite'}?mode=ro", uri=True) as db:
        metadata = {key: json.loads(value) for key, value in db.execute("SELECT key,value FROM metadata")}
        assert metadata['status'] in ('completed', 'completed_with_errors')
        failed = [(task, json.loads(rows), error) for task, rows, error in db.execute(
            "SELECT task,rows,error FROM outcomes WHERE status='failed'")]
        requests = {}
        for task, request_id, raw in db.execute("SELECT task,id,record FROM requests WHERE stage='quality' "
                "ORDER BY json_extract(record,'$.timestamp'),id"):
            requests.setdefault(task, []).append((request_id, json.loads(raw)))
    with (ROOT / 'run/results.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    originals = {row['candidate_id']: row for row in rows}
    recovered_rows = {}
    repairs = []
    manifest = read_manifest(str(ROOT / 'manifest.json'))
    repair_dir = ROOT / 'grade_repairs'
    write_manifest(repair_dir / 'prompt_manifest.json', manifest)
    with RunState(repair_dir / 'run.sqlite') as state:
        state.put('parent_run', str(ROOT / 'run'))
        state.put('prompt_manifest', manifest)
        state.put('policy', 'Earliest recoverable recorded response; otherwise retry the exact quality request only. Preserve source, questions, faithfulness, prompts and raw run.')
        state.put('status', 'running')
        for task, batch, original_error in failed:
            assert batch and all(row['grading_status'] == 'failed' for row in batch)
            assert 'quality:' in original_error and 'faithfulness:' not in original_error
            prompt = batch[0]['quality_verifier_prompt']
            mode = batch[0]['mode']
            logical_mode = 'practitioner' if mode == 'practitioners' else mode
            assert prompt == manifest['prompts'][f'un/quality/{logical_mode}']['text']
            recovery = {'task': task, 'target_id': batch[0]['target_id'], 'original_error': original_error}
            values = None
            for request_id, raw in requests[task]:
                provenance = {}
                values = recover_quality(raw, prompt, batch, mode, provenance=provenance)
                if values is not None:
                    recovery.update(method='recorded_schema_recovery', source_request_id=request_id, **provenance)
                    break
            if values is None:
                raw = requests[task][0][1]
                assert raw['messages'][0]['content'] == prompt
                envelope = json.loads(raw['messages'][1]['content'])
                assert [item['candidate_id'] for item in envelope['candidates']] == [row['candidate_id'] for row in batch]
                config = grading.GraderConfig(model=raw['model'], thinking_budget_tokens=16000, thinking_max_tokens=32000)
                assert raw['request_settings'] == {'extra_body': {'thinking': {'budget_tokens':16000, 'type':'enabled'}}, 'max_tokens':32000}
                checkpoint = state.checkpoint(task, retries=3)
                def grade():
                    return grading.grade_quality(checkpoint.client('quality', raw['model'], llm.client_for(raw['model'])),
                        config, prompt, envelope['passages'], envelope['candidates'], mode, strict=True)
                values = checkpoint.run('quality', grade)
                recovery.update(method='quality_only_retry_same_request', original_request_id=requests[task][0][0])
            by_id = {value['_response']['candidate_id']: value for value in values}
            assert set(by_id) == {row['candidate_id'] for row in batch}
            fixed = []
            for original in batch:
                faith = {key: original[f'faith_{key}'] for key in grading.FAITHFULNESS_KEYS}
                faith.update(overall=original['faith_overall'], reason=original.get('faith_reason', ''))
                if original.get('faithfulness_verifier_response_json'):
                    faith['_response'] = json.loads(original['faithfulness_verifier_response_json'])
                row = dict(original)
                row.update(grading.grade_columns(faith, by_id[row['candidate_id']], mode))
                row.update(grading_status='completed', grading_error='',
                           original_grading_error=original_error, grade_recovery_method=recovery['method'])
                assert row['question'] == originals[row['candidate_id']]['question']
                assert row['answer'] == originals[row['candidate_id']]['answer']
                assert str(row['faith_overall']) == originals[row['candidate_id']]['faith_overall']
                recovered_rows[row['candidate_id']] = row
                fixed.append(row)
            state.put('recovery/' + task, recovery)
            state.outcome(task, fixed)
            repairs.append(recovery)
            print(recovery['target_id'], recovery['method'], len(fixed), flush=True)
        state.put('status', 'completed')
    result = [recovered_rows.get(row['candidate_id'], row) for row in rows]
    assert len(result) == len(rows) and all(row['grading_status'] == 'completed' for row in result)
    _rank(result)
    _write_csv(ROOT / 'results.csv', result)
    (ROOT / 'recovery_log.json').write_text(json.dumps(repairs, ensure_ascii=False, indent=2) + '\n')
    export_traces(repair_dir)
    print(f'Final export: {len(result)} graded candidates; original run retained unchanged.')


if __name__ == '__main__':
    main()
