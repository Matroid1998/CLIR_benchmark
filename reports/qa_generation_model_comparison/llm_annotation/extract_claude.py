#!/usr/bin/env python3
"""Extract the Claude workflow pass into results_claude/<doc>.json and audit agent tool use.

Reads the workflow transcript dir (journal.jsonl has each agent's structured return value;
agent-*.jsonl has the full transcript with model id, usage and every tool call).
"""
import glob, json, re, sys
from pathlib import Path
from render import HERE, validate, RUBRIC, render_record

wf_dirs = [Path(a) for a in sys.argv[1:]]  # later dirs override earlier ones per doc
recs = {r["doc_id"]: r for r in json.load(open(HERE / "pass_claude_records.json"))}
out_dir = HERE / "results_claude"; out_dir.mkdir(exist_ok=True)

results = {}
for wf_dir in wf_dirs:
    for line in open(wf_dir / "journal.jsonl"):
        o = json.loads(line)
        if o["type"] == "result":
            results[o["agentId"]] = o["result"]

audit = []
for f in [p for wf_dir in wf_dirs for p in sorted(glob.glob(str(wf_dir / "agent-*.jsonl")))]:
    agent_id = Path(f).stem.split("-", 1)[1]
    lines = [json.loads(l) for l in open(f)]
    first = lines[0]["message"]["content"]
    text = first if isinstance(first, str) else json.dumps(first)
    doc_id = re.search(r"prompts_claude/([^ \n]+)\.md", text).group(1)
    tools, model, usage = [], None, {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    for o in lines:
        if o.get("type") == "assistant":
            model = o["message"].get("model", model)
            u = o["message"].get("usage") or {}
            for k in usage: usage[k] += u.get(k, 0) or 0
            for blk in o["message"]["content"]:
                if blk.get("type") == "tool_use":
                    tools.append({"name": blk["name"], "input": blk["input"] if blk["name"] != "StructuredOutput" else "<ratings>"})
    own_prompt = str(HERE / "prompts_claude" / f"{doc_id}.md")
    reads = [t for t in tools if t["name"] == "Read"]
    other = [t for t in tools if t["name"] not in ("Read", "StructuredOutput")]
    clean = (len(reads) >= 1 and all(t["input"].get("file_path") == own_prompt for t in reads) and not other)
    models_in_run = sorted({o["message"].get("model") for o in lines if o.get("type") == "assistant"})
    audit.append({"doc_id": doc_id, "agent_id": agent_id, "model": model, "models_in_run": models_in_run, "n_tool_uses": len(tools),
                  "superseded": False,
                  "reads": [t["input"].get("file_path") for t in reads], "other_tools": other,
                  "blind_protocol_ok": clean, "usage": usage})
    out = results.get(agent_id)
    if out is None:
        print("NO RESULT for", doc_id, agent_id); continue
    rec = recs[doc_id]
    validate(out, rec["mode"])
    json.dump({"doc_id": doc_id, "mode": rec["mode"], "model": model, "requested_model": "session model (claude-fable-5)",
               "reasoning_effort": "high", "usage": usage, "agent_id": agent_id,
               "system_prompt": "(workflow agent; prompt file = rubric + record)", "user_prompt": RUBRIC + "\n---\n\n" + render_record(rec),
               "output": out}, open(out_dir / f"{doc_id}.json", "w"), ensure_ascii=False, indent=1)

# a later run for the same doc supersedes the earlier one (used to replace a run whose ratings came from a fallback model)
last = {a["doc_id"]: a["agent_id"] for a in audit}
for a in audit: a["superseded"] = last[a["doc_id"]] != a["agent_id"]
json.dump(audit, open(HERE / "claude_pass_audit.json", "w"), indent=1)
audit = [a for a in audit if not a["superseded"]]
n_ok = sum(a["blind_protocol_ok"] for a in audit)
print(f"{len(results)} results, {len(audit)} agents, blind protocol ok on {n_ok}/{len(audit)}; models={set(a['model'] for a in audit)}")
for a in audit:
    if not a["blind_protocol_ok"]:
        print("  VIOLATION", a["doc_id"], a["reads"], a["other_tools"])
tok = {k: sum(a["usage"][k] for a in audit) for k in audit[0]["usage"]}
print("token totals", tok)
print("written", len(list(out_dir.glob("*.json"))))
