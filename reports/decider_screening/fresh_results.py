"""Score-only screening results; abstentions and missing grades never become zero."""
import argparse
import csv
import json
from collections import defaultdict
from statistics import mean
from pathlib import Path


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def avg(values):
    return mean(values) if values else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    p = args.directory
    rows = read(p / "document_comparison.csv")
    assert all(r["all_eligible_modes_completed"] == "True" for r in rows)
    assert all(r[f"{b}_decision_status"] == "completed" for r in rows for b in ("jev", "generator"))
    subsets = {"eurlex": [r for r in rows if r["corpus"] == "eurlex"],
               "un_all": [r for r in rows if r["corpus"] == "un"],
               "un_without_meetings": [r for r in rows if r["corpus"] == "un" and r["is_meeting"] == "False"],
               "un_meetings_only": [r for r in rows if r["corpus"] == "un" and r["is_meeting"] == "True"]}
    metrics, paired, mode_metrics, distributions, missing = [], [], [], [], []
    for subset, records in subsets.items():
        if not records:
            continue
        modes = ("fact_pattern", "lookup") if subset == "eurlex" else ("lookup", "practitioner", "semantic")
        for backend in ("jev", "generator"):
            scored = [r for r in records if r[f"{backend}_selected_score"] != ""]
            abstentions = [r for r in records if r[f"{backend}_mode"] == "skip"]
            unscored = [r for r in records if r[f"{backend}_mode"] != "skip" and r[f"{backend}_selected_score"] == ""]
            assert len(records) == len(scored) + len(abstentions) + len(unscored)
            metrics.append({"subset": subset, "decider": backend, "documents": len(records),
                "scored_selected": len(scored), "abstentions": len(abstentions),
                "no_qualifying_candidate": len(unscored),
                "mean_selected_score_out_of_40": avg([float(r[f"{backend}_selected_score"]) for r in scored]),
                "mean_gap_to_best_mode_when_scored": avg([float(r[f"{backend}_score_regret"]) for r in scored]),
                "best_mode_matches_including_ties": sum(r[f"{backend}_matches_best"] == "True" for r in scored),
                "best_mode_match_percent_among_scored": 100 * sum(r[f"{backend}_matches_best"] == "True" for r in scored) / len(scored) if scored else None})
            for mode in (*modes, "skip"):
                count = sum(r[f"{backend}_mode"] == mode for r in records)
                distributions.append({"subset": subset, "decider": backend, "mode": mode,
                                      "count": count, "percent": 100 * count / len(records)})
            for r in abstentions + unscored:
                missing.append({"subset": subset, "target_id": r["target_id"], "symbol": r["symbol"],
                                "decider": backend, "mode": r[f"{backend}_mode"],
                                "status": "abstention" if r[f"{backend}_mode"] == "skip" else "no_qualifying_candidate"})
        pairs = [r for r in records if r["jev_selected_score"] != "" and r["generator_selected_score"] != ""]
        differences = [float(r["jev_selected_score"]) - float(r["generator_selected_score"]) for r in pairs]
        paired.append({"subset": subset, "paired_scored_documents": len(pairs),
            "jev_mean": avg([float(r["jev_selected_score"]) for r in pairs]),
            "gpt_mean": avg([float(r["generator_selected_score"]) for r in pairs]),
            "jev_minus_gpt": avg(differences), "jev_higher": sum(d > 0 for d in differences),
            "gpt_higher": sum(d < 0 for d in differences), "tied": sum(d == 0 for d in differences),
            "deciders_agree_count": sum(r["jev_mode"] == r["generator_mode"] for r in records)})
        for mode in modes:
            values = [float(r[f"{mode}_score"]) for r in records if r[f"{mode}_score"] != ""]
            mode_metrics.append({"subset": subset, "mode": mode, "scored_documents": len(values),
                                 "mean_best_score_out_of_40": avg(values)})
    for filename, data in (("score_only_summary.csv", metrics), ("paired_decider_scores.csv", paired),
                           ("mode_score_summary.csv", mode_metrics), ("decider_mode_distribution.csv", distributions),
                           ("abstentions_and_missing_scores.csv", missing)):
        write(p / filename, data)
    candidates = read(p / "all_mode_candidates.csv")
    assert all(r["grading_status"] == "completed" for r in candidates)
    assert len({r["candidate_id"] for r in candidates}) == len(candidates)
    grouped = defaultdict(list)
    for r in candidates:
        grouped[r.get("target_id") or r["target_article_id"], r["screening_mode"]].append(r)
    documents = {r["target_id"]: r for r in read(p / "documents.csv")}
    decisions = read(p / "decisions.csv")
    jev = {r["target_id"]: r for r in decisions if r["backend"] == "jev"}
    mode_rows = defaultdict(list)
    for r in read(p / "mode_scores.csv"):
        mode_rows[r["target_id"]].append(r)
    exported = []
    total = 0
    for r in rows:
        target = r["target_id"]
        out = {k: r[k] for k in ("corpus", "document_id", "target_id", "symbol", "title", "is_meeting")}
        out.update(document=r["document_text"], jev_selected_mode=r["jev_mode"],
                   jev_confidence=r["jev_confidence"], jev_probabilities_json=jev[target]["probabilities_json"],
                   gpt_selected_mode=r["generator_mode"], gpt_reason=r["generator_reason"])
        for mode_row in mode_rows[target]:
            mode = mode_row["mode"]
            batch = sorted(grouped[target, mode], key=lambda c: int(c["candidate_rank"]))
            assert len(batch) == int(mode_row["candidate_count"])
            questions, grades = [], []
            for i, c in enumerate(batch, 1):
                text = f'{i}. {c["question"]}'
                if c.get("question_cited"):
                    text += f'\nWith identifier: {c["question_cited"]}'
                questions.append(text)
                grades.append(f'{i}. Total: {c["total_score"]}/40; faithfulness: {c["faith_overall"]}/15; '
                              f'quality: {c["qual_overall"]}/25; audit: {c["quality_audit_status"]}')
            out.update({f"{mode}_best_score": mode_row["best_score"], f"{mode}_questions": "\n\n".join(questions),
                        f"{mode}_question_grades": "\n".join(grades), f"{mode}_candidate_count": len(batch),
                        f"{mode}_skip_reason": mode_row["generation_skip_reason"]})
            total += len(batch)
        out["complete_decider_input"] = documents[target]["source_payload"]
        exported.append(out)
    assert total == len(candidates)
    write(p / "documents_decisions_questions_grades.csv", exported)
    write(p / "jev_selections.csv", list(jev.values()))
    calls = json.loads((p / "llm_calls.json").read_text())["calls"]
    responses = [{"task_id": c["task_id"], "request_id": c["request_id"], "response": c["record"].get("response")}
                 for c in calls if c["record"].get("model") == "~typesafe/jev-latest"]
    (p / "jev_responses.json").write_text(json.dumps(responses, ensure_ascii=False, indent=2) + "\n")
    from clir_bench.domains.legal.qac.screening_analysis import table
    report = ["# Fresh 100-document screening with decider examples",
              "50 EUR-Lex articles and 50 UN passages; prior screening documents and identified example acts "
              "are excluded. Each decider receives the same five examples for its corpus. Generator and "
              "standard decider: gpt-5.6-luna; grader: anthropic/claude-sonnet-5.5; Jev: ~typesafe/jev-latest.",
              "Scores are the best qualifying candidate in the selected mode, out of 40. Skips and missing "
              "qualifying candidates are excluded from averages and score losses, never assigned zero. "
              "Best-mode match rates use scored selections only and retain ties. All modes are eligible "
              "on UN meeting records. This new sample cannot isolate the effect of prompt changes.",
              "## Selected-mode scores",
              table(metrics, ['subset', 'decider', 'scored_selected', 'mean_selected_score_out_of_40',
                              'mean_gap_to_best_mode_when_scored', 'best_mode_match_percent_among_scored',
                              'abstentions', 'no_qualifying_candidate']),
              "## Comparison on the same scored documents",
              table(paired, ['subset', 'paired_scored_documents', 'jev_mean', 'gpt_mean',
                             'jev_minus_gpt', 'jev_higher', 'gpt_higher', 'tied']),
              "## Mode distributions",
              table(distributions, ['subset', 'decider', 'mode', 'count', 'percent']),
              "## Scores by generation mode",
              "These conditional means can cover different documents; they are not paired comparisons.",
              table(mode_metrics, ['subset', 'mode', 'scored_documents', 'mean_best_score_out_of_40']),
              "## Files",
              "[Full document/question/grade CSV](documents_decisions_questions_grades.csv), "
              "[score summary](score_only_summary.csv), [paired scores](paired_decider_scores.csv), "
              "[abstentions and missing scores](abstentions_and_missing_scores.csv), "
              "[Jev responses](jev_responses.json), [validation](validation.json)."]
    (p / "analysis.md").write_text("\n\n".join(report) + "\n")
    print(json.dumps({"documents": len(rows), "graded_candidates": len(candidates),
                      "metrics": metrics, "paired_comparison": paired}, indent=2))


if __name__ == "__main__":
    main()
