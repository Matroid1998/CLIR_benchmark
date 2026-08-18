#!/usr/bin/env python3
"""Split the annotation export into two standalone files:

- annotator_notes.md      the shared_notes free-text per document, with each
                          document's slot -> model key and question texts so
                          the note's Q1..Q6 references can be read directly
- questions_by_model.csv  one row per question with model, question/answer
                          text, keep decision and score summaries
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # reports/qa_generation_model_comparison/
OUT = Path(__file__).resolve().parent

FAITH = ["faith_grounding", "faith_precision", "faith_numerical_fidelity"]
TECH = ["qual_search_bar_realism", "qual_specificity", "qual_phrasing_economy", "qual_focus"]
SEM = ["qual_search_realism", "qual_lexical_distance", "qual_conceptual_framing", "qual_retrievability"]

with open(ROOT / "all-questions-by-model-review-annotations-2026-08-18.json") as f:
    ann = json.load(f)
with open(ROOT / "model_slot_mapping.json") as f:
    mp = json.load(f)

rows = []
docs = []
for rec in ann["records"]:
    eid = rec["external_id"]
    meta = rec["metadata"]
    fields = rec["fields"]
    slots = mp["records"][eid]["slots"]
    resp = {r["question_name"]: r["value"] for r in rec["responses"]}
    note = str(resp.get("shared_notes", "")).strip()
    doc = {"doc_id": eid, "mode": meta["mode"], "lang": meta["question_language"],
           "note": note, "questions": []}
    for i, slot in enumerate(["q1", "q2", "q3", "q4", "q5", "q6"], start=1):
        qual = {c: resp[f"{slot}_{c}"] for c in TECH + SEM if f"{slot}_{c}" in resp}
        rubric = "technical" if any(c in TECH for c in qual) else "semantic"
        faith = [resp[f"{slot}_{c}"] for c in FAITH]
        q = {
            "model": slots[slot],
            "doc_id": eid,
            "slot": slot,
            "mode": meta["mode"],
            "question_language": meta["question_language"],
            "accept": resp[f"{slot}_accept"],
            "faith_mean": round(sum(faith) / 3, 4),
            "quality_mean": round(sum(qual.values()) / 4, 4),
            "rubric_used": rubric,
            "linguistic": resp[f"{slot}_qual_linguistic_quality"],
            "question": fields[f"question_{i}"],
            "answer": fields[f"answer_{i}"],
        }
        rows.append(q)
        doc["questions"].append(q)
    docs.append(doc)

# ------------------------------------------------------- questions CSV ------
rows.sort(key=lambda r: (r["model"], r["doc_id"]))
cols = ["model", "doc_id", "slot", "mode", "question_language", "accept",
        "faith_mean", "quality_mean", "rubric_used", "linguistic", "question", "answer"]
with open(OUT / "questions_by_model.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows({c: r[c] for c in cols} for r in rows)
print(f"wrote questions_by_model.csv ({len(rows)} rows)")

# --------------------------------------------------------- notes MD ---------
with_notes = [d for d in docs if d["note"]]
lines = [
    "# Annotator notes — question generation review (2026-08-18 export)",
    "",
    f"{len(with_notes)} of {len(docs)} documents carry a free-text note. Q1–Q6 in a note",
    "refer to the randomised slots the annotator saw; the key under each note",
    "resolves them to models (from `model_slot_mapping.json` — private).",
    "",
]
for d in with_notes:
    lines.append(f"## {d['doc_id']}  ·  {d['mode']} mode  ·  question language: {d['lang']}")
    lines.append("")
    for para in d["note"].splitlines():
        lines.append(f"> {para}" if para.strip() else ">")
    lines.append("")
    for q in d["questions"]:
        kept = "kept" if q["accept"] == "yes" else "DISCARDED"
        lines.append(f"- **{q['slot'].upper()} · {q['model']}** ({kept}, faith {q['faith_mean']:.2f}, "
                     f"quality {q['quality_mean']:.2f}): {q['question']}")
        lines.append(f"  — *{q['answer']}*")
    lines.append("")

no_note = [d["doc_id"] for d in docs if not d["note"]]
lines.append("---")
lines.append("")
lines.append(f"Documents without a note ({len(no_note)}): " + ", ".join(no_note))
lines.append("")

(OUT / "annotator_notes.md").write_text("\n".join(lines))
print(f"wrote annotator_notes.md ({len(with_notes)} noted docs)")
