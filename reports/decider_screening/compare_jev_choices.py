"""Compare changed Jev choices on fixed grades, excluding abstentions/missing scores."""
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
RUNS = {"un": "un50_20260930_all_modes", "eurlex": "eurlex50_20260930_v2"}


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(name, rows):
    with (ROOT / name).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = []
    for corpus, run in RUNS.items():
        directory = ROOT / run
        current = {r["target_id"]: r for r in read(directory / "document_comparison.csv")}
        for change in read(directory / "previous_vs_updated_documents.csv"):
            if change["jev_choice_changed"] != "True":
                continue
            before, after = change["jev_previous_mode"], change["jev_updated_mode"]
            scores = current[change["target_id"]]
            old_score, new_score = scores.get(f"{before}_score", ""), scores.get(f"{after}_score", "")
            if "skip" in (before, after):
                status = "abstention"
            elif old_score == "" or new_score == "":
                status = "no_qualifying_candidate"
            else:
                status = "paired_scores"
            delta = float(new_score) - float(old_score) if status == "paired_scores" else None
            rows.append({
                "corpus": corpus, "document": change["symbol"], "target_id": change["target_id"],
                "is_meeting": change["is_meeting"], "previous_choice": before, "updated_choice": after,
                "previous_choice_score_using_updated_grades": old_score,
                "updated_choice_score_using_updated_grades": new_score,
                "comparison_status": status, "score_change": delta,
                "outcome": ("worse" if delta < 0 else "better" if delta > 0 else "tied") if delta is not None else "not_compared",
                "previous_confidence": change["jev_previous_confidence"],
                "updated_confidence": change["jev_updated_confidence"],
            })
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["corpus"], row["previous_choice"], row["updated_choice"]].append(row)
    summaries = []
    for (corpus, before, after), group in grouped.items():
        paired = [r for r in group if r["comparison_status"] == "paired_scores"]
        summaries.append({
            "corpus": corpus, "previous_choice": before, "updated_choice": after,
            "changed_documents": len(group), "paired_scored_documents": len(paired),
            "abstention_documents": sum(r["comparison_status"] == "abstention" for r in group),
            "no_qualifying_candidate_documents": sum(r["comparison_status"] == "no_qualifying_candidate" for r in group),
            "worse": sum(r["outcome"] == "worse" for r in paired),
            "better": sum(r["outcome"] == "better" for r in paired),
            "tied": sum(r["outcome"] == "tied" for r in paired),
            "mean_previous_score": mean(float(r["previous_choice_score_using_updated_grades"]) for r in paired) if paired else None,
            "mean_updated_score": mean(float(r["updated_choice_score_using_updated_grades"]) for r in paired) if paired else None,
            "mean_score_change": mean(r["score_change"] for r in paired) if paired else None,
            "net_score_change": sum(r["score_change"] for r in paired) if paired else None,
        })
    assert len(rows) == 28
    assert all(r["score_change"] is None for r in rows if r["comparison_status"] != "paired_scores")
    assert all(r["changed_documents"] == r["paired_scored_documents"] + r["abstention_documents"]
               + r["no_qualifying_candidate_documents"] for r in summaries)
    write("jev_changed_choices_20260930.csv", rows)
    write("jev_mode_transition_summary_20260930.csv", summaries)
    write("jev_abstentions_and_missing_candidates_20260930.csv",
          [r for r in rows if r["comparison_status"] != "paired_scores"])
    for row in summaries:
        print(row)


if __name__ == "__main__":
    main()
