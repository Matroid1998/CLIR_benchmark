"""Aggregate the saved, manually authored agent reviews; makes no model calls."""

import csv
import html
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
VERSIONS = ("original", "revised", "simple")
SHARDS = ("eurlex", "un_a", "un_b")


def read(name):
    return json.loads((ROOT / name).read_text())


def write_csv(name, rows):
    with (ROOT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    mapping = read("mapping_PRIVATE.json")
    group_versions = {}
    candidate_ids = {}
    for row in mapping:
        key = (row["target_id"], row["mode"], row["label"])
        group_versions[key] = row["version"]
        if row["id"]:
            candidate_ids[(*key, row["id"])] = row["candidate_id"]

    candidates, families, details = [], [], []
    seen_families = set()
    for shard in SHARDS:
        packet = read(f"{shard}_blinded.json")
        documents = {d["target_id"]: d for d in packet}
        expected = {(d["target_id"], f["mode"]): f for d in packet for f in d["families"]}
        reviews = read(f"{shard}_reviews.json")
        assert len(reviews) == len(expected), (shard, "family count")
        for review in reviews:
            target, mode = review["target_id"], review["mode"]
            family_key = (target, mode)
            assert family_key in expected and family_key not in seen_families, family_key
            seen_families.add(family_key)
            document = documents[target]
            expected_groups = {g["label"]: g for g in expected[family_key]["groups"]}
            assert len(review["groups"]) == 3
            assert {g["label"] for g in review["groups"]} == set(expected_groups)
            preferred = review["preferred_labels"]
            assert len(set(preferred)) == len(preferred)
            assert set(preferred) <= set(expected_groups)
            matched = all(g["candidates"] for g in expected_groups.values())
            for group in review["groups"]:
                label = group["label"]
                version = group_versions[(target, mode, label)]
                expected_candidates = {c["id"]: c for c in expected_groups[label]["candidates"]}
                assert len(group["candidates"]) == len(expected_candidates)
                assert {c["id"] for c in group["candidates"]} == set(expected_candidates)
                ratings = []
                for candidate in group["candidates"]:
                    rating = candidate["question_rating"]
                    assert type(rating) is int and 1 <= rating <= 5
                    assert candidate["answer_status"] in {"ok", "minor", "major"}
                    assert candidate["reason"].strip()
                    original = expected_candidates[candidate["id"]]
                    ratings.append(rating)
                    candidates.append({
                        "corpus": document["corpus"], "target_id": target,
                        "stratum": document["stratum"], "mode": mode, "version": version,
                        "reviewer_shard": shard, "blinded_id": candidate["id"],
                        "candidate_id": candidate_ids[(target, mode, label, candidate["id"])],
                        "question": original["question"], "answer": original["answer"],
                        "question_rating": rating, "answer_status": candidate["answer_status"],
                        "reason": candidate["reason"], "all_three_generated": matched,
                    })
                best = group.get("best_candidate_id")
                assert best in expected_candidates if expected_candidates else best is None
                assert not (label in preferred and not expected_candidates)
                families.append({
                    "corpus": document["corpus"], "target_id": target, "mode": mode,
                    "version": version, "candidate_count": len(ratings),
                    "question_mean": mean(ratings) if ratings else None,
                    "question_best": max(ratings) if ratings else None,
                    "all_three_generated": matched,
                    "preferred": label in preferred,
                    "preference_credit": 1 / len(preferred) if label in preferred else 0,
                    "group_note": group["group_note"],
                    "preference_reason": review["preference_reason"],
                })
            details.append((document, review))

    assert len(candidates) == read("design.json")["candidate_count"]
    mode_summaries = []
    for corpus, mode in sorted({(r["corpus"], r["mode"]) for r in families}):
        rows = [r for r in families if (r["corpus"], r["mode"]) == (corpus, mode)]
        result = {"corpus": corpus, "mode": mode, "matched_families": sum(r["all_three_generated"] for r in rows) // 3, "versions": {}}
        for version in VERSIONS:
            groups = [r for r in rows if r["version"] == version]
            matched_groups = [r for r in groups if r["all_three_generated"]]
            qas = [r for r in candidates if (r["corpus"], r["mode"], r["version"]) == (corpus, mode, version)]
            matched_qas = [r for r in qas if r["all_three_generated"]]
            result["versions"][version] = {
                "generated_families": sum(r["candidate_count"] > 0 for r in groups),
                "questions_reviewed": len(qas),
                "matched_family_mean": mean(r["question_mean"] for r in matched_groups) if matched_groups else None,
                "matched_best_mean": mean(r["question_best"] for r in matched_groups) if matched_groups else None,
                "matched_preference_credit": sum(r["preference_credit"] for r in matched_groups),
                "all_question_mean": mean(r["question_rating"] for r in qas) if qas else None,
                "matched_good_questions": sum(r["question_rating"] >= 4 for r in matched_qas),
                "matched_questions": len(matched_qas),
                "major_answer_issues": sum(r["answer_status"] == "major" for r in qas),
            }
        mode_summaries.append(result)

    pairs = []
    for left, right in [("revised", "original"), ("simple", "original"), ("simple", "revised")]:
        for summary in mode_summaries:
            corpus, mode = summary["corpus"], summary["mode"]
            index = {(r["target_id"], r["version"]): r for r in families if (r["corpus"], r["mode"]) == (corpus, mode)}
            deltas = []
            for target in {key[0] for key in index}:
                a, b = index[(target, left)], index[(target, right)]
                if a["question_mean"] is not None and b["question_mean"] is not None:
                    deltas.append(a["question_mean"] - b["question_mean"])
            pairs.append({"corpus": corpus, "mode": mode, "left": left, "right": right,
                          "paired_families": len(deltas), "mean_difference": mean(deltas) if deltas else None,
                          "left_wins": sum(x > 1e-8 for x in deltas), "ties": sum(abs(x) <= 1e-8 for x in deltas),
                          "right_wins": sum(x < -1e-8 for x in deltas)})
    overall = {}
    for version in VERSIONS:
        corpus_scores = {corpus: mean(r["versions"][version]["matched_family_mean"] for r in mode_summaries if r["corpus"] == corpus) for corpus in ["eurlex", "un"]}
        corpus_best = {corpus: mean(r["versions"][version]["matched_best_mean"] for r in mode_summaries if r["corpus"] == corpus) for corpus in ["eurlex", "un"]}
        overall[version] = {**corpus_scores, "equal_corpus_mean": mean(corpus_scores.values()),
                            "equal_corpus_best_mean": mean(corpus_best.values())}
    summary = {"design": read("design.json"), "rubric": {
        "5": "Strong question usable as written", "4": "Good with a minor weakness",
        "3": "Meaningful editing/context needed, or thin/artificial information need",
        "2": "Major repair needed", "1": "Invalid or unanswerable",
        "answer_status": "Supplied answer evaluated separately: ok, minor, major",
        "aggregation": "Average candidate question ratings within each document/mode/version, then average documents. Main comparison uses only document/modes where all three versions generated questions. Overall weights the two corpora equally and modes equally within corpus. Empty generations are not scored zero.",
    }, "reviewed_questions": len(candidates), "reviewed_document_modes": len(seen_families),
        "mode_summaries": mode_summaries, "paired_comparisons": pairs, "overall": overall}
    (ROOT / "summary.json").write_text(json.dumps(summary, indent=2))
    write_csv("candidate_reviews.csv", candidates)
    write_csv("family_scores.csv", families)
    write_csv("paired_comparisons.csv", pairs)

    esc = lambda x: html.escape(str(x))
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Manual question-quality review</title>',
             '<style>body{font:16px/1.55 system-ui;max-width:1150px;margin:32px auto;padding:0 20px;color:#17212b}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{border:1px solid #d4dbe1;padding:9px;text-align:left}th{background:#f1f5f9}details{margin:16px 0;border:1px solid #d4dbe1;padding:12px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap}blockquote{border-left:3px solid #94a3b8;padding-left:16px}.note{background:#fff5d6;padding:16px}.qa{margin:15px 0;padding:10px;background:#f7f9fb}</style>',
             '<h1>Manual review of generated question quality</h1>',
             f'<p>{len(candidates)} questions read individually across 40 sampled documents and {len(seen_families)} document/mode comparisons. Original, revised and simple labels and previous verifier scores were hidden during review. No new generation or verifier calls were used.</p>',
             '<p class="note">Agent judgment on a stratified sample, not human gold labels or a full review of all 1,778 questions. Reviewers know this project and may recognize previously audited examples. Main scores compare only document/modes where all three versions produced questions. Supplied-answer defects are recorded separately. Labels are revealed below for inspection.</p>',
             '<p>Question ratings: 5 strong as written; 4 good with minor weakness; 3 meaningful editing/context needed or thin/artificial; 2 major repair; 1 invalid/unanswerable. No arbitrary word-limit, fixed-anchor-count or mandatory-date penalties. Legitimate factual extraction and direct application to a hypothetical case are both permitted.</p>',
             '<table><tr><th>Source / mode</th><th>Matched documents</th><th>Original /5</th><th>Revised /5</th><th>Simple /5</th></tr>']
    for row in mode_summaries:
        parts.append('<tr><td>'+esc(row['corpus']+' / '+row['mode'])+'</td><td>'+str(row['matched_families'])+'</td>'+''.join(f'<td>{row["versions"][v]["matched_family_mean"]:.2f}</td>' for v in VERSIONS)+'</tr>')
    parts.append('</table><p>Average questions within each document/mode first, then average matched documents. The overall summary gives EUR-Lex and UN equal weight; it is not a measure of routing or output coverage.</p>')
    parts.append('<p>'+esc('Overall, equal corpus weighting: '+', '.join(f'{v} {overall[v]["equal_corpus_mean"]:.2f}/5' for v in VERSIONS))+'.</p>')
    parts.append('<p>Original and Revised are effectively tied on average question quality; Simple is weaker overall. Revised shows its clearest improvement in UN lookup. The native-verifier score increase is not reproduced as an overall question-quality increase in this review.</p>')
    parts.append('<p>'+esc('Best question available in each matched document/mode, using the manual ratings: '+', '.join(f'{v} {overall[v]["equal_corpus_best_mean"]:.2f}/5' for v in VERSIONS))+'. This describes potential with ideal selection, not the quality of the questions the current pipeline actually selects. Revised has more candidates in many UN batches, so best-of-batch comparisons also reflect more chances to produce a strong question.</p>')
    parts.append('<p><a href="candidate_reviews.csv">Every question, answer, rating and reason (CSV)</a> · <a href="summary.json">Complete statistics and methodology (JSON)</a></p>')
    for doc, review in details:
        target, mode = review['target_id'], review['mode']
        parts.append(f'<details><summary>{esc(doc["corpus"])} · {esc(target)} · {esc(mode)}</summary>')
        parts.append(f'<p>{esc(review["source_note"])}</p><details><summary>Target source text</summary><pre>{esc(doc["document_text"])}</pre></details>')
        preferred_versions = [group_versions[(target, mode, label)] for label in review['preferred_labels']]
        parts.append(f'<p>Reviewer preference: {esc(", ".join(preferred_versions) or "none")}. {esc(review["preference_reason"])}</p>')
        for group in review['groups']:
            version = group_versions[(target, mode, group['label'])]
            parts.append(f'<h3>{esc(version)}</h3><p>{esc(group["group_note"])}</p>')
            for candidate in group['candidates']:
                row = next(r for r in candidates if (r['target_id'], r['mode'], r['version'], r['blinded_id']) == (target, mode, version, candidate['id']))
                parts.append(f'<div class="qa"><p><b>Question ({row["question_rating"]}/5):</b> {esc(row["question"])}</p><p><b>Answer ({esc(row["answer_status"])}):</b> {esc(row["answer"])}</p><p>{esc(row["reason"])}</p></div>')
        parts.append('</details>')
    parts.append('</html>')
    (ROOT / 'report.html').write_text('\n'.join(parts))
    print(json.dumps({"reviewed_questions": len(candidates), "overall": overall, "mode_summaries": mode_summaries}, indent=2))


if __name__ == '__main__':
    main()
