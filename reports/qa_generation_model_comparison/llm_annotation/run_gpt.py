#!/usr/bin/env python3
"""Blind annotation pass with an OpenAI model (structured output), one call per document."""
import argparse, json, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from openai import OpenAI, BadRequestError
from render import HERE, render_prompt, schema, validate, RUBRIC, render_record

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gpt-5.6-sol")
ap.add_argument("--pass-name", default="gpt")
ap.add_argument("--effort", default="high")
ap.add_argument("--workers", type=int, default=6)
ap.add_argument("--limit", type=int, default=None)
args = ap.parse_args()

client = OpenAI()
recs = json.load(open(HERE / f"pass_{args.pass_name}_records.json"))[: args.limit]
out_dir = HERE / f"results_{args.pass_name}"; out_dir.mkdir(exist_ok=True)
lock = threading.Lock()


def call(rec):
    path = out_dir / f"{rec['doc_id']}.json"
    if path.exists():
        return rec["doc_id"], "cached"
    messages = [{"role": "system", "content": RUBRIC},
                {"role": "user", "content": render_record(rec)}]
    fmt = {"type": "json_schema", "json_schema": {"name": "question_review", "strict": True, "schema": schema(rec["mode"])}}
    last = None
    for attempt in range(4):
        kwargs = dict(model=args.model, messages=messages, response_format=fmt)
        if args.effort:
            kwargs["reasoning_effort"] = args.effort
        try:
            t0 = time.time()
            resp = client.chat.completions.create(**kwargs)
            text = resp.choices[0].message.content or ""
            parsed = validate(json.loads(text), rec["mode"])
            usage = resp.usage.model_dump() if resp.usage else None
            with lock:
                json.dump({"doc_id": rec["doc_id"], "mode": rec["mode"], "model": resp.model, "requested_model": args.model,
                           "reasoning_effort": args.effort, "seconds": round(time.time() - t0, 1), "usage": usage,
                           "system_prompt": RUBRIC, "user_prompt": render_record(rec), "output": parsed},
                          open(path, "w"), ensure_ascii=False, indent=1)
            return rec["doc_id"], f"ok {round(time.time() - t0)}s"
        except BadRequestError as e:
            last = e
            msg = str(e)
            if "reasoning_effort" in msg or "reasoning" in msg:
                args.effort = None; continue
            if "strict" in msg or "schema" in msg or "minItems" in msg:
                fmt["json_schema"]["strict"] = False; continue
            raise
        except Exception as e:  # noqa: BLE001
            last = e; time.sleep(5 * (attempt + 1))
    return rec["doc_id"], f"FAILED {last!r}"


with ThreadPoolExecutor(args.workers) as ex:
    futs = [ex.submit(call, r) for r in recs]
    for f in as_completed(futs):
        d, s = f.result(); print(d, s, flush=True)
print("done", len(list(out_dir.glob("*.json"))), "/", len(recs))
