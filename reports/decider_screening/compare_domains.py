"""Compare completed domain screenings using their recorded pipeline scores."""
import csv
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
RUNS = {"eurlex": ROOT / "eurlex50_20260930", "un": ROOT / "un50_20260929"}


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def average(values):
    return mean(values) if values else None


def main():
    output = ROOT / "eurlex_vs_un_20260930"
    output.mkdir(exist_ok=True)
    summaries, details, baselines = [], [], []
    for domain, directory in RUNS.items():
        records = read(directory / "document_comparison.csv")
        modes = ("lookup", "fact_pattern") if domain == "eurlex" else ("lookup", "practitioner", "semantic")
        subsets = {domain: records} if domain == "eurlex" else {
            "un_without_meetings": [r for r in records if r["is_meeting"] == "False"],
            "un_all": records,
            "un_meetings_only": [r for r in records if r["is_meeting"] == "True"],
        }
        for subset, rows in subsets.items():
            assert all(r["all_eligible_modes_completed"] == "True" for r in rows)
            available = [r for r in rows if r["oracle_best_score"]]
            for backend in ("jev", "generator"):
                assert all(r[f"{backend}_decision_status"] == "completed" for r in rows)
                scored = [r for r in rows if r[f"{backend}_selected_score"]]
                matches = sum(r[f"{backend}_matches_best"] == "True" for r in available)
                adjusted = [float(r[f"{backend}_utility"]) for r in rows]
                oracle = [float(r["oracle_best_score"] or 0) for r in rows]
                summaries.append({
                    "subset": subset, "decider": backend, "documents": len(rows),
                    "selected_mode_scored": len(scored),
                    "any_mode_scored": len(available), "matched_best_including_ties": matches,
                    "matched_best_percent": 100 * matches / len(available) if available else None,
                    "mean_selected_score_when_scored": average([float(r[f"{backend}_selected_score"]) for r in scored]),
                    "mean_points_lost_when_scored": average([float(r[f"{backend}_score_regret"]) for r in scored]),
                    "mean_score_zero_for_skip_or_no_candidate": average(adjusted),
                    "mean_best_available_score_zero_for_no_candidate": average(oracle),
                    "mean_points_lost_including_skip_or_no_candidate": average([a-b for a,b in zip(oracle, adjusted)]),
                    "mean_audit_clear_score_zero_for_unavailable": average([float(r[f"{backend}_audit_clear_utility"]) for r in rows]),
                    "skipped": sum(r[f"{backend}_mode"] == "skip" for r in rows),
                    "skipped_despite_scored_alternative": sum(r[f"{backend}_missed_opportunity"] == "True" for r in rows),
                    "unproductive_choice_despite_scored_alternative": sum(r[f"{backend}_selected_mode_unproductive"] == "True" for r in rows),
                })
            for mode in modes:
                eligible = [r for r in rows if r["is_meeting"] == "False" or mode == "semantic"]
                if not eligible:
                    continue
                baselines.append({"subset": subset, "fixed_mode": mode, "eligible_documents": len(eligible),
                    "scored": sum(bool(r[f"{mode}_score"]) for r in eligible),
                    "mean_score_zero_for_no_candidate": average([float(r[f"{mode}_score"] or 0) for r in eligible])})
        details.extend(records)
    write(output / "decider_score_comparison.csv", summaries)
    write(output / "document_comparison.csv", details)
    write(output / "fixed_mode_baselines.csv", baselines)
    for r in summaries:
        if r["subset"] in ("eurlex", "un_without_meetings"):
            print(r)
    print("Saved:", output)


if __name__ == "__main__":
    main()
