"""Export a completed rerun and compare it with the same saved targets."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args()
    old, new = args.previous, args.current
    previous = {r["target_id"]: r for r in read(old / "document_comparison.csv")}
    current = read(new / "document_comparison.csv")
    assert set(previous) == {r["target_id"] for r in current}
    assert all(r["all_eligible_modes_completed"] == "True" for r in current)
    assert all(r[f"{b}_decision_status"] == "completed" for r in current for b in ("jev", "generator"))
    assert json.loads((old / "selection.json").read_text()) == json.loads((new / "selection.json").read_text())
    policies = []
    for version, directory in (("previous", old), ("updated", new)):
        policies.extend(dict(version=version, **r) for r in read(directory / "decider_performance.csv"))
    write(new / "previous_vs_updated_metrics.csv", policies)
    details = []
    for row in current:
        before = previous[row["target_id"]]
        out = {k: row[k] for k in ("corpus", "target_id", "symbol", "is_meeting")}
        for backend in ("jev", "generator"):
            old_mode, new_mode = before[f"{backend}_mode"], row[f"{backend}_mode"]
            old_choice_on_new_scores = float(row.get(f"{old_mode}_score") or 0)
            if row["is_meeting"] == "True" and old_mode not in ("semantic", "skip"):
                raise ValueError("Review meeting-mode eligibility before comparing changed policies")
            out.update({
                f"{backend}_previous_mode": old_mode,
                f"{backend}_updated_mode": new_mode,
                f"{backend}_choice_changed": old_mode != new_mode,
                f"{backend}_previous_confidence": before[f"{backend}_confidence"],
                f"{backend}_updated_confidence": row[f"{backend}_confidence"],
                f"{backend}_previous_selected_score": before[f"{backend}_selected_score"],
                f"{backend}_updated_selected_score": row[f"{backend}_selected_score"],
                f"{backend}_previous_choice_on_updated_scores_zero_if_unavailable": old_choice_on_new_scores,
                f"{backend}_updated_choice_gain_on_updated_scores": float(row[f"{backend}_utility"]) - old_choice_on_new_scores,
            })
        details.append(out)
    write(new / "previous_vs_updated_documents.csv", details)
    candidates = read(new / "all_mode_candidates.csv")
    grouped = defaultdict(list)
    for row in candidates:
        assert row["grading_status"] == "completed"
        grouped[row.get("target_id") or row["target_article_id"], row["screening_mode"]].append(row)
    modes = {r["target_id"]: [] for r in current}
    for row in read(new / "mode_scores.csv"):
        modes[row["target_id"]].append(row)
    documents = {r["target_id"]: r for r in read(new / "documents.csv")}
    decisions = read(new / "decisions.csv")
    jev = {r["target_id"]: r for r in decisions if r["backend"] == "jev"}
    exports = []
    exported = 0
    for row in current:
        target = row["target_id"]
        out = {k: row[k] for k in ("corpus", "document_id", "target_id", "symbol", "title", "is_meeting")}
        out.update(document=row["document_text"], jev_selected_mode=row["jev_mode"],
                   jev_confidence=row["jev_confidence"], jev_probabilities_json=jev[target]["probabilities_json"],
                   other_llm_model="gpt-5.6-luna", other_llm_selected_mode=row["generator_mode"],
                   other_llm_reason=row["generator_reason"])
        for scores in modes[target]:
            mode = scores["mode"]
            batch = sorted(grouped[target, mode], key=lambda r: int(r["candidate_rank"]))
            assert len(batch) == int(scores["candidate_count"])
            questions, grades = [], []
            for i, candidate in enumerate(batch, 1):
                question = f'{i}. {candidate["question"]}'
                if candidate.get("question_cited"):
                    question += f'\nWith identifier: {candidate["question_cited"]}'
                questions.append(question)
                grades.append(f'{i}. Total: {candidate["total_score"]}/40; '
                              f'faithfulness: {candidate["faith_overall"]}/15; '
                              f'quality: {candidate["qual_overall"]}/25; '
                              f'audit: {candidate["quality_audit_status"]}')
            out.update({f"{mode}_best_grade_out_of_40": scores["best_score"],
                        f"{mode}_questions": "\n\n".join(questions),
                        f"{mode}_question_grades": "\n".join(grades),
                        f"{mode}_candidate_count": len(batch),
                        f"{mode}_eligible": scores["eligible"],
                        f"{mode}_skip_reason": scores["generation_skip_reason"]})
            exported += len(batch)
        out["complete_decider_input"] = documents[target]["source_payload"]
        exports.append(out)
    assert exported == len(candidates)
    write(new / "documents_decisions_questions_grades.csv", exports)
    write(new / "jev_selections.csv", list(jev.values()))
    calls = json.loads((new / "llm_calls.json").read_text())["calls"]
    responses = [{"task_id": c["task_id"], "response": c["record"]["response"]}
                 for c in calls if c["record"].get("model") == "~typesafe/jev-latest"]
    (new / "jev_responses.json").write_text(json.dumps(responses, ensure_ascii=False, indent=2) + "\n")
    print(f"Validated and exported {len(exports)} documents and {exported} candidate grades.")
    for backend in ("jev", "generator"):
        print(backend, "changed choices", sum(r[f"{backend}_choice_changed"] for r in details),
              "mean routing gain on updated scores", mean(r[f"{backend}_updated_choice_gain_on_updated_scores"] for r in details))
    for row in policies:
        print({k: row[k] for k in ("version", "subset", "backend", "scored_selected", "matches_oracle",
              "oracle_available", "mean_selected_score_when_available", "mean_regret_when_scored",
              "mean_utility_zero_for_skip_or_no_candidate")})


if __name__ == "__main__":
    main()
