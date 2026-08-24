#!/usr/bin/env python3
"""Fallback transport for a single document: same rubric + record, Claude via OpenRouter, JSON output validated against the schema."""
import json, sys, time
from openai import OpenAI
from render import HERE, RUBRIC, render_record, schema, validate

doc_id, model = sys.argv[1], sys.argv[2]
rec = next(r for r in json.load(open(HERE / "pass_claude_records.json")) if r["doc_id"] == doc_id)
client = OpenAI(api_key=__import__("os").environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
sch = schema(rec["mode"])
messages = [{"role": "system", "content": RUBRIC + "\n\nReturn ONLY a JSON object (no prose, no code fence) that matches this JSON schema exactly:\n" + json.dumps(sch)},
            {"role": "user", "content": render_record(rec)}]
t0 = time.time()
resp = client.chat.completions.create(model=model, messages=messages, max_tokens=16000,
                                      extra_body={"reasoning": {"effort": "high"}, "provider": {"require_parameters": False}})
text = resp.choices[0].message.content or ""
print("RAW model:", resp.model, "finish:", resp.choices[0].finish_reason, "len:", len(text)); print("RAW text head:", text[:1500]); print("RAW msg:", {k:(str(v)[:300]) for k,v in resp.choices[0].message.model_dump().items() if k!="content" and v}); print("RAW resp extra:", {k:str(v)[:200] for k,v in resp.model_dump().items() if k not in ("choices",)})
cleaned = text.strip()
if cleaned.startswith("```"):
    cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
out = validate(json.loads(cleaned), rec["mode"])
print("model used:", resp.model, "| provider:", getattr(resp, "provider", None), "| seconds:", round(time.time() - t0), "| usage:", resp.usage.model_dump() if resp.usage else None)
json.dump({"doc_id": doc_id, "mode": rec["mode"], "model": resp.model, "requested_model": model, "transport": "openrouter", "reasoning_effort": "high",
           "seconds": round(time.time() - t0, 1), "usage": resp.usage.model_dump() if resp.usage else None,
           "system_prompt": messages[0]["content"], "user_prompt": messages[1]["content"], "output": out},
          open(HERE / f"results_claude_openrouter__{doc_id}.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:800])
