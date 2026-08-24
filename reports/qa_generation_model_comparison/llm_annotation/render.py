"""Shared prompt + schema for both LLM annotators (identical text for each pass)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUBRIC = (HERE / "rubric.md").read_text()
SLOTS = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
FAITH = ["faith_grounding", "faith_precision", "faith_numerical_fidelity"]
TECH = ["qual_search_bar_realism", "qual_specificity", "qual_phrasing_economy", "qual_focus"]
SEM = ["qual_search_realism", "qual_lexical_distance", "qual_conceptual_framing", "qual_retrievability"]


def quality_keys(mode):
    return TECH if mode == "technical" else SEM


def render_record(rec):
    parts = [f"# Record: {rec['doc_id']}", "", "## Context", rec["context"], "",
             "## Source passage", rec["passage"], "", "## Candidate questions"]
    for q in rec["questions"]:
        parts += [f"### {q['slot']}", f"Question: {q['question']}", f"Answer: {q['answer']}", ""]
    return "\n".join(parts)


def render_prompt(rec):
    """Full self-contained annotator message: rubric + record."""
    return RUBRIC + "\n---\n\n" + render_record(rec)


def schema(mode):
    score = {"type": "integer", "enum": [1, 2, 3, 4, 5]}
    keys = FAITH + quality_keys(mode) + ["linguistic_quality"]
    item_props = {"slot": {"type": "string", "enum": SLOTS}}
    item_props.update({k: score for k in keys})
    item_props["accept"] = {"type": "string", "enum": ["yes", "no"]}
    item_props["reason"] = {"type": "string", "description": "One sentence justifying the scores and the keep decision."}
    return {
        "type": "object",
        "properties": {
            "ratings": {"type": "array", "minItems": 6, "maxItems": 6,
                        "items": {"type": "object", "properties": item_props,
                                  "required": list(item_props), "additionalProperties": False}},
            "shared_notes": {"type": "string", "description": "Optional note for the whole document; empty string if none."},
        },
        "required": ["ratings", "shared_notes"],
        "additionalProperties": False,
    }


def validate(out, mode):
    """Raise if a parsed output does not match the schema contract."""
    assert set(out) == {"ratings", "shared_notes"}, set(out)
    assert [r["slot"] for r in out["ratings"]] == SLOTS, [r.get("slot") for r in out["ratings"]]
    for r in out["ratings"]:
        for k in FAITH + quality_keys(mode) + ["linguistic_quality"]:
            assert r[k] in (1, 2, 3, 4, 5), (k, r[k])
        assert r["accept"] in ("yes", "no")
    return out


if __name__ == "__main__":
    import sys
    passname = sys.argv[1]
    recs = json.load(open(HERE / f"pass_{passname}_records.json"))
    out = HERE / f"prompts_{passname}"; out.mkdir(exist_ok=True)
    for r in recs:
        (out / f"{r['doc_id']}.md").write_text(render_prompt(r))
    index = [{"doc_id": r["doc_id"], "mode": r["mode"], "path": str(out / f"{r['doc_id']}.md")} for r in recs]
    json.dump(index, open(HERE / f"prompts_{passname}_index.json", "w"), indent=1)
    json.dump({"technical": schema("technical"), "semantic": schema("semantic")}, open(HERE / "schemas.json", "w"), indent=1)
    print(f"{len(recs)} prompt files -> {out}; max chars {max(len(render_prompt(r)) for r in recs)}")
