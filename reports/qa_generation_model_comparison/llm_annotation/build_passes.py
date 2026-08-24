#!/usr/bin/env python3
"""Build anonymised, freshly slot-randomised annotation passes for LLM annotators.

Source of truth: the human Argilla export (fields = what the human saw) and its
private slot mapping. Each LLM pass gets its own random slot order (own seed) so
position effects are independent across annotators. Private mappings are written
to --private-dir (kept out of the repo until both passes are finished).
"""
import argparse, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLOTS = ["q1", "q2", "q3", "q4", "q5", "q6"]

ap = argparse.ArgumentParser()
ap.add_argument("--private-dir", required=True)
args = ap.parse_args()
priv = Path(args.private_dir); priv.mkdir(parents=True, exist_ok=True)
here = Path(__file__).resolve().parent

ann = json.load(open(ROOT / "all-questions-by-model-review-annotations-2026-08-18.json"))
mp = json.load(open(ROOT / "model_slot_mapping.json"))
models = mp["models"]

# de-anonymise the human view into model -> (q, a)
docs = []
for rec in ann["records"]:
    eid = rec["external_id"]
    f = rec["fields"]; m = rec["metadata"]
    slots = mp["records"][eid]["slots"]
    assert m["mode"] == mp["records"][eid]["mode"]
    by_model = {}
    for i, s in enumerate(SLOTS, 1):
        by_model[slots[s]] = {"question": f[f"question_{i}"], "answer": f[f"answer_{i}"]}
    assert set(by_model) == set(models), eid
    docs.append({"doc_id": eid, "mode": m["mode"], "question_language": m["question_language"],
                 "context_language": m["context_language"], "strategy": m["strategy_name"],
                 "passage": f["passage"], "context": f["context"], "by_model": by_model})
docs.sort(key=lambda d: d["doc_id"])
print(f"{len(docs)} documents, {len(models)} models, max passage chars = {max(len(d['passage']) for d in docs)}")

PASSES = {"claude": 20260822, "gpt": 20260823}
for name, seed in PASSES.items():
    rng = random.Random(seed)
    records, mapping = [], {"pass": name, "seed": seed, "models": models,
                            "note": "Private de-anonymisation key for this LLM pass. slots maps q1..q6 -> model.",
                            "records": {}}
    for d in docs:
        order = list(models); rng.shuffle(order)
        mapping["records"][d["doc_id"]] = {"mode": d["mode"], "question_language": d["question_language"],
                                           "slots": dict(zip(SLOTS, order))}
        records.append({k: d[k] for k in ("doc_id", "mode", "question_language", "context_language", "strategy", "context", "passage")}
                       | {"questions": [{"slot": s.upper(), "question": d["by_model"][mo]["question"],
                                         "answer": d["by_model"][mo]["answer"]} for s, mo in zip(SLOTS, order)]})
    json.dump(records, open(here / f"pass_{name}_records.json", "w"), ensure_ascii=False, indent=1)
    json.dump(mapping, open(priv / f"pass_{name}_slot_mapping.json", "w"), indent=2)
    # sanity: the new order differs from the human's for most docs
    same = sum(mapping["records"][d["doc_id"]]["slots"] == mp["records"][d["doc_id"]]["slots"] for d in docs)
    print(f"pass {name}: {len(records)} records written; identical-to-human order on {same} docs")
