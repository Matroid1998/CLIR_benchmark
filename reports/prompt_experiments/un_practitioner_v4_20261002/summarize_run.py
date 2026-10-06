"""Summarize the pinned, normally routed UN run without making model calls."""
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from statistics import mean
import csv
import json
import sqlite3

from clir_bench.domains.legal.qac import _digest
from clir_bench.core.prompt_registry import read_manifest, write_manifest

ROOT = Path(__file__).resolve().parent
BASELINE = ROOT.parent / "legal_20260930/debiased/run"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def number(row, key):
    return float(row[key]) if row.get(key) not in (None, "") else None


def mode(row):
    return "practitioner" if row["mode"] == "practitioners" else row["mode"]


def average(rows, key):
    values = [number(row, key) for row in rows if number(row, key) is not None]
    return mean(values) if values else None


def best(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["target_id"]].append(row)
    selected = []
    for group in groups.values():
        # Preserve recorded native rank as the stable tie order.
        group.sort(key=lambda row: int(row.get("candidate_rank") or 999))
        valid = [row for row in group if row.get("grading_status") == "completed"
                 and number(row, "total_score") is not None
                 and (number(row, "faith_grounding") or 0) >= 3]
        if valid:
            selected.append(max(valid, key=lambda row: number(row, "total_score")))
    return selected


def statistics(rows):
    selected = best(rows)
    return {
        "candidates": len(rows),
        "targets_with_candidates": len({row["target_id"] for row in rows}),
        "fully_graded_candidates": sum(row.get("grading_status") == "completed" for row in rows),
        "mean_candidate_faithfulness_15": average(rows, "faith_overall"),
        "mean_candidate_quality_25": average(rows, "qual_overall"),
        "mean_candidate_total_40": average(rows, "total_score"),
        "best_candidates": len(selected),
        "mean_best_faithfulness_15": average(selected, "faith_overall"),
        "mean_best_quality_25": average(selected, "qual_overall"),
        "mean_best_total_40": average(selected, "total_score"),
        "candidate_audit_status": dict(Counter(row.get("quality_audit_status", "") for row in rows)),
        "best_audit_status": dict(Counter(row.get("quality_audit_status", "") for row in selected)),
        "targets_with_an_accepted_candidate": len({row["target_id"] for row in rows
                                                   if row.get("quality_audit_status") in ("clear", "minor_issues")}),
    }


def table(headers, rows):
    return "<table><thead><tr>" + "".join(f"<th>{escape(str(h))}</th>" for h in headers) + (
        "</tr></thead><tbody>" + "".join("<tr>" + "".join(
            f"<td>{escape(str(value))}</td>" for value in row) + "</tr>" for row in rows)
        + "</tbody></table>")


def fmt(value):
    return "—" if value is None else f"{value:.2f}"


def main():
    db = sqlite3.connect(f"file:{ROOT / 'run/run.sqlite'}?mode=ro", uri=True)
    metadata = {key: json.loads(value) for key, value in db.execute("SELECT key,value FROM metadata")}
    if metadata.get("status") not in ("completed", "completed_with_errors"):
        raise SystemExit("Run is not complete; refusing a premature final report")
    selection = json.loads((ROOT / "selection.json").read_text())
    assert len(selection) == len({row["document_id"] for row in selection}) == 50
    selected_ids = {row["target_id"] for row in selection}
    source_hashes = {row["target_id"]: row["source_payload_sha256"] for row in selection}
    recovery_path = ROOT / "recovery_log.json"
    repairs = json.loads(recovery_path.read_text()) if recovery_path.exists() else []
    final_csv = ROOT / "results.csv" if repairs else ROOT / "run/results.csv"
    current = read_csv(final_csv)
    assert all(row["target_id"] in selected_ids and row["source_payload_sha256"] == source_hashes[row["target_id"]]
               for row in current)
    manifest = read_manifest(str(ROOT / "manifest.json"))
    assert metadata["config"]["prompt_registry"]["bundle_sha256"] == manifest["bundle_sha256"]
    write_manifest(ROOT / "run/prompt_manifest.json", manifest)
    task_targets = {}
    for entry in metadata["targets"]:
        for generator in metadata["config"]["generation_model"]:
            task_targets[_digest([entry["corpus"], entry["target"], generator, []])] = entry["target"]["block_id"]
    routes = {}
    decisions = []
    for task, value in db.execute("SELECT task,value FROM stages WHERE stage='decider' AND status='completed'"):
        decision = json.loads(value)
        target_id = task_targets[task]
        routes[target_id] = decision["mode"]
        decisions.append({"target_id": target_id, **decision})
    assert set(routes) <= selected_ids
    (ROOT / "decisions.json").write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n")
    prior_routes = {row["target_id"]: row["mode"] for row in read_csv(BASELINE / "decisions.csv")
                    if row["corpus"] == "un" and row["backend"] == "jev" and row["status"] == "completed"}
    prior = [row for row in read_csv(BASELINE / "all_mode_candidates.csv")
             if row["corpus"] == "un" and row["target_id"] in selected_ids
             and mode(row) == prior_routes[row["target_id"]]]
    assert all(row["source_payload_sha256"] == source_hashes[row["target_id"]] for row in prior)
    outcome_counts = dict(db.execute("SELECT status,count(*) FROM outcomes GROUP BY status"))
    outcomes = [{"target_id": task_targets[task], "status": status, "error": error}
                for task, status, error in db.execute("SELECT task,status,error FROM outcomes")]
    assert len(outcomes) == 50
    usage = defaultdict(lambda: {"calls": 0, "errors": 0, "reported_cost_usd": 0,
                                 "calls_without_reported_cost": 0, "prompt_tokens": 0, "completion_tokens": 0})
    calls = list(db.execute("SELECT stage,record FROM requests"))
    repair_db = ROOT / "grade_repairs/run.sqlite"
    if repair_db.exists():
        with sqlite3.connect(f"file:{repair_db}?mode=ro", uri=True) as repair_connection:
            calls.extend(repair_connection.execute("SELECT stage,record FROM requests").fetchall())
    for stage, record in calls:
        record = json.loads(record)
        item = usage[stage + ":" + record["model"]]
        item["calls"] += 1
        item["errors"] += record["status"] == "error"
        values = record.get("usage") or {}
        for key in ("prompt_tokens", "completion_tokens"):
            item[key] += values.get(key) or 0
        cost = values.get("provider_cost")
        item["calls_without_reported_cost"] += cost is None
        item["reported_cost_usd"] += cost or 0
    summary = {
        "run_status": ("completed_after_grade_recovery" if repairs and all(row['grading_status'] == 'completed' for row in current)
                       else metadata["status"]), "documents": 50,
        "original_run_status": metadata["status"],
        "grade_repairs": repairs,
        "language": "en", "strata": dict(Counter(row["stratum"] for row in selection)),
        "bundle": manifest["bundle"], "bundle_sha256": manifest["bundle_sha256"],
        "models": {"decider": "~typesafe/jev-latest", "generator": metadata["config"]["generation_model"],
                   "verifier": metadata["config"]["verifier_model"]},
        "original_outcomes": outcome_counts,
        "final_documents_with_complete_grades": len({row['target_id'] for row in current if row['grading_status'] == 'completed'}),
        "routing": dict(Counter(routes.values())),
        "prior_routing": dict(Counter(prior_routes.values())),
        "unchanged_routes": sum(prior_routes[target] == chosen for target, chosen in routes.items()),
        "current": statistics(current), "previous_revised_routed": statistics(prior),
        "per_mode": {chosen: {"current": statistics([row for row in current if mode(row) == chosen]),
                              "previous": statistics([row for row in prior if mode(row) == chosen])}
                     for chosen in ("lookup", "practitioner", "semantic")},
        "usage": dict(usage), "document_outcomes": outcomes,
        "limitations": [
            "Native before/after scores use each run's own verifiers. Practitioner quality and UN faithfulness changed; score differences do not isolate question-quality improvement.",
            "Each document was generated only in its Jev-selected mode. This run cannot measure whether the decider chose the highest-scoring alternative mode.",
            "Best follows pipeline score ranking with grounding >=3; audit acceptance is reported separately and is not an independent human evaluation.",
            "Reported costs exclude calls whose provider did not supply cost data.",
            "The raw run is preserved. Recovery logs distinguish structural recovery of recorded grades from new quality-only retry calls; questions and successful faithfulness grades were preserved.",
        ],
    }
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    current_best = {row['target_id']: row for row in best(current)}
    prior_best = {row['target_id']: row for row in best(prior)}
    document_rows = []
    for entry in selection:
        target = entry['target_id']
        item = {'target_id': target, 'document_id': entry['document_id'], 'symbol': entry['symbol'],
                'stratum': entry['stratum'], 'previous_mode': prior_routes[target],
                'current_mode': routes.get(target, 'failed')}
        for label, chosen in (('previous', prior_best.get(target, {})), ('current', current_best.get(target, {}))):
            for field in ('candidate_id', 'question', 'answer', 'faith_overall', 'qual_overall', 'total_score', 'quality_audit_status'):
                item[label + '_' + field] = chosen.get(field, '')
        document_rows.append(item)
    with (ROOT / 'document_comparison.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(document_rows[0]))
        writer.writeheader()
        writer.writerows(document_rows)
    a, b = summary["previous_revised_routed"], summary["current"]
    scores = table(["Run", "Candidates", "Best per document", "Best faithfulness /15", "Best quality /25"], [
        ["Previous revised (Jev-selected modes)", a["candidates"], a["best_candidates"], fmt(a["mean_best_faithfulness_15"]), fmt(a["mean_best_quality_25"])],
        ["Current v4 routed run", b["candidates"], b["best_candidates"], fmt(b["mean_best_faithfulness_15"]), fmt(b["mean_best_quality_25"])],
    ])
    groups = defaultdict(list)
    for row in current:
        groups[row["target_id"]].append(row)
    sections = []
    for entry in selection:
        target = entry["target_id"]
        cards = []
        for row in sorted(groups[target], key=lambda row: int(row.get("candidate_rank") or 999)):
            cards.append(f'<article><p><strong>{escape(row["question"])}</strong></p><blockquote>{escape(row["answer"])}</blockquote>'
                         f'<p>Faithfulness: {escape(row.get("faith_overall", ""))}/15 · Quality: {escape(row.get("qual_overall", ""))}/25 · '
                         f'Rank: {escape(row.get("candidate_rank", ""))} · Best: {escape(row.get("is_best", ""))} · '
                         f'Audit: {escape(row.get("quality_audit_status", ""))}</p>'
                         f'<details><summary>Verifier notes</summary><p>{escape(row.get("faith_reason", ""))}</p>'
                         f'<p>{escape(row.get("qual_reason", ""))}</p></details></article>')
        sections.append(f'<section><h2>{escape(entry["symbol"])} — {escape(entry["title"])}</h2>'
                        f'<p>{escape(target)} · {escape(entry["stratum"])} · Route: {escape(routes.get(target, "failed"))}'
                        f' (previous: {escape(prior_routes[target])})</p>' + ("".join(cards) or '<p>No candidates produced.</p>')
                        + f'<details><summary>Exact source payload</summary><pre>{escape(entry["source_payload"])}</pre></details></section>')
    html = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>UN practitioner v4: 50-document routed run</title>'
            '<style>body{font:16px/1.6 system-ui;max-width:1100px;margin:40px auto;padding:0 20px;color:#182334}'
            'table{border-collapse:collapse;width:100%}th,td{padding:10px;text-align:left;border-bottom:1px solid #ddd}'
            'section{border-top:2px solid #cad4df;margin-top:35px}article{background:#f3f6fa;padding:12px 20px;margin:15px 0}'
            'pre{white-space:pre-wrap;font-size:13px}blockquote{border-left:3px solid #6585a8;padding-left:15px}'
            'summary{cursor:pointer}</style><h1>UN practitioner v4: 50-document routed run</h1>'
            f'<p>Status: {escape(summary["run_status"])}. Bundle: {escape(manifest["bundle"])}. '
            '50 English UN documents: 25 resolutions, 20 meeting records and 5 letters. '
            'Jev chose the mode; gpt-5.6-luna generated; Claude Sonnet 5.5 verified.</p>'
            f'<p>Routing: {escape(json.dumps(summary["routing"]))}. '
            f'Unchanged routes: {summary["unchanged_routes"]}/50.</p>' + scores
            + '<p>These are native verifier scores. The rubric changed, so this table does not establish an independent quality improvement. '
            'The run evaluated only the selected mode, so it cannot measure best-mode routing accuracy.</p>'
            '<p>A small score-blind spot check of four questions from three documents found supported answers, '
            'but three questions still used descriptive document locators. This is not a run-wide estimate. '
            '<a href="manual_spot_check.json">Read the spot check</a>.</p>'
            '<p><a href="results.csv">All candidates CSV after grade recovery</a> · <a href="run/results.csv">Original raw export</a> · <a href="summary.json">Detailed summary</a> · '
            '<a href="document_comparison.csv">Before/after by document</a> · <a href="recovery_log.json">Grade recovery provenance</a> · '
            '<a href="manifest.json">Pinned prompt versions</a> · <a href="run/llm_calls.json">Recorded model calls</a></p>'
            + "".join(sections) + '</html>')
    (ROOT / "report.html").write_text(html, encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("run_status", "documents", "original_outcomes", "final_documents_with_complete_grades", "routing", "unchanged_routes", "current")}, indent=2))


if __name__ == "__main__":
    main()
