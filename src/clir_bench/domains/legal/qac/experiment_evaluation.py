"""Frozen, mode-blind evaluation across prompt versions on identical source payloads."""
from __future__ import annotations

import argparse
import csv
import hashlib  
import json
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from clir_bench.core import llm
from clir_bench.domains.legal.qac import _write_csv
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.decider import MODES
from clir_bench.domains.legal.qac.env import load_env
from clir_bench.domains.legal.qac.screening import digest

SCORES = ("grounding", "answer_resolution", "retrievability", "information_value", "clarity")


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def candidate_key(row):
    corpus = row.get("corpus") or ("eurlex" if row.get("celex_id") else "un")
    target_id = row.get("target_id") or row.get("target_article_id") or row["block_id"]
    return corpus, target_id, row.get("screening_mode") or row["mode"]


def validate_generation_completion(version, selection, config, mode_runs, candidates):
    """Require every expected generation outcome before spending on common grading.

    Empty successful generations are observed outcomes, while failed or unstarted
    generations are missing data. Native grading failures remain independently
    evaluable when their generated question/answer pairs were preserved.
    """
    if config.get("meeting_modes") != "all":
        raise ValueError(f"{version}: unsupported meeting_modes; common evaluation requires 'all'")
    targets = {(row["corpus"], row["target_id"]) for row in selection}
    if len(targets) != len(selection):
        raise ValueError(f"{version}: duplicate selection targets")
    modes = dict(MODES)
    if any(row["corpus"] == "un" and row["mode"] == "semantic" for row in mode_runs):
        modes["un"] = ("lookup", "practitioner", "semantic")
    if not any(row["corpus"] == "eurlex" and row["mode"] == "conceptual" for row in mode_runs):
        modes["eurlex"] = ("fact_pattern", "lookup")
    for corpus, declared in config.get("modes_by_source", {}).items():
        allowed = set(MODES.get(corpus, ())) | ({"semantic"} if corpus == "un" else set())
        if not declared or len(set(declared)) != len(declared) or not set(declared) <= allowed:
            raise ValueError(f"{version}: invalid declared modes for {corpus}")
        modes[corpus] = tuple(declared)
    expected = {(corpus, target_id, mode) for corpus, target_id in targets for mode in modes[corpus]}
    grouped = defaultdict(list)
    for row in candidates:
        key = candidate_key(row)
        if key not in expected:
            raise ValueError(f"{version}: unexpected candidate target/mode: {key}")
        if any(not isinstance(row.get(field), str) or not row[field].strip()
               for field in ("question", "answer")):
            raise ValueError(f"{version}: generated candidate lacks a question/answer: {key}")
        grouped[key].append(row)
    outcomes = {}
    for row in mode_runs:
        key = row["corpus"], row["target_id"], row["mode"]
        if key not in expected or key in outcomes:
            raise ValueError(f"{version}: unexpected or duplicate generation outcome: {key}")
        outcomes[key] = row
    missing = expected - outcomes.keys()
    if missing:
        raise ValueError(f"{version}: missing generation outcomes for {len(missing)} target/modes; "
                         f"first: {min(missing)}")
    for key, row in outcomes.items():
        if str(row.get("eligible", "")).lower() != "true":
            raise ValueError(f"{version}: generation outcome is not eligible in all-mode run: {key}")
        try:
            count = int(row["candidate_count"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"{version}: invalid generation candidate count: {key}") from error
        if count != len(grouped[key]):
            raise ValueError(f"{version}: generation candidate count disagrees with saved rows: {key}")
        status = row["status"]
        if status == "no_candidates" and count == 0:
            continue
        if status == "completed" and count > 0:
            continue
        if (status == "failed" and count > 0
                and all(candidate.get("grading_status") in ("completed", "failed")
                        for candidate in grouped[key])
                and any(candidate.get("grading_status") == "failed" for candidate in grouped[key])):
            continue
        raise ValueError(f"{version}: generation is unfinished, failed, or inconsistent: {key} ({status})")


def prepare(runs, selection, batch_size=6):
    """Deduplicate identical pairs and hide version/mode/old grades from the judge."""
    sources = {}
    for row in selection:
        key = row["corpus"], row["target_id"]
        if key in sources:
            raise ValueError(f"Duplicate selection target: {key}")
        payload = row.get("source_payload")
        if (not isinstance(payload, str)
                or hashlib.sha256(payload.encode()).hexdigest() != row.get("source_payload_sha256")):
            raise ValueError(f"Selection source payload hash mismatch: {key}")
        sources[key] = row
    pairs, memberships = {}, []
    reference_settings = None
    for version, directory in runs.items():
        config = json.loads((directory / "config.json").read_text())
        settings = {key: config[key] for key in
                    ("generator", "verifier", "language", "keep", "meeting_modes")}
        if reference_settings is None:
            reference_settings = settings
        elif settings != reference_settings:
            raise ValueError(f"{version}: model/language/candidate settings differ")
        saved = json.loads((directory / "selection.json").read_text())
        if saved != selection:
            raise ValueError(f"{version}: selections differ; cannot make a paired comparison")
        candidates = read_csv(directory / "all_mode_candidates.csv")
        validate_generation_completion(version, selection, config,
                                       read_csv(directory / "mode_runs.csv"), candidates)
        for row in candidates:
            corpus, target_id, mode = candidate_key(row)
            source = sources[corpus, target_id]
            if row.get("source_payload_sha256") != source["source_payload_sha256"]:
                raise ValueError(f"{version}: candidate source payload differs: {target_id}")
            identity = digest([corpus, target_id, row["question"], row["answer"]])
            blind_id = "c_" + identity[:24]
            pairs.setdefault((corpus, target_id), {})[blind_id] = {
                "candidate_id": blind_id, "question": row["question"], "answer": row["answer"]}
            memberships.append({"version": version, "corpus": corpus, "target_id": target_id,
                                "symbol": source["symbol"], "is_meeting": source["is_meeting"],
                                "mode": mode,
                                "candidate_id": row["candidate_id"], "blind_id": blind_id,
                                "question": row["question"], "answer": row["answer"]})
    jobs = []
    for key in sorted(pairs):
        candidates = [pairs[key][identity] for identity in sorted(pairs[key])]
        random.Random(digest(list(key))).shuffle(candidates)
        for start in range(0, len(candidates), batch_size):
            batch = candidates[start:start + batch_size]
            envelope = {"corpus": key[0], "passages": sources[key]["source_payload"],
                        "candidates": batch}
            jobs.append(("common/" + digest(envelope), envelope))
    # Native grading can reorder CSV rows; it must not invalidate a blinded resume.
    memberships.sort(key=lambda row: (row["version"], row["corpus"], row["target_id"],
                                      row["mode"], row["candidate_id"]))
    return jobs, memberships


def validate(data, candidates):
    if not isinstance(data, dict) or set(data) != {"candidates"}:
        raise ValueError("Common evaluator must return a candidates object")
    items = data["candidates"]
    if not isinstance(items, list) or len(items) != len(candidates):
        raise ValueError("Common evaluator candidate count mismatch")
    result = []
    for index, (item, candidate) in enumerate(zip(items, candidates)):
        if item.get("index") != index or item.get("candidate_id") != candidate["candidate_id"]:
            raise ValueError("Common evaluator candidate identity/order mismatch")
        scores, reasons = item.get("scores"), item.get("reasons")
        if not isinstance(scores, dict) or set(scores) != set(SCORES):
            raise ValueError("Common evaluator score keys mismatch")
        if any(type(v) is not int or not 1 <= v <= 5 for v in scores.values()):
            raise ValueError("Common evaluator scores must be integers in 1–5")
        if (not isinstance(reasons, dict) or set(reasons) != set(SCORES)
                or any(not isinstance(v, str) or not v.strip() for v in reasons.values())):
            raise ValueError("Common evaluator needs a reason for every score")
        # Predeclared usability gate; absent questions and failed evaluations never score zero.
        usable = (scores["grounding"] >= 4 and scores["answer_resolution"] >= 4
                  and all(scores[key] >= 3 for key in ("retrievability", "information_value", "clarity")))
        result.append({"blind_id": candidate["candidate_id"], **scores,
                       "total": sum(scores.values()), "usable": usable,
                       "reasons_json": json.dumps(reasons, ensure_ascii=False)})
    return result


def export(state, output, memberships):
    outcomes = state.outcomes()
    scores = {row["blind_id"]: row for item in outcomes if item["status"] == "completed"
              for row in item["rows"]}
    rows = [{**member, **scores.get(member["blind_id"], {}),
             "evaluation_status": "completed" if member["blind_id"] in scores else "missing"}
            for member in memberships]
    _write_csv(output / "candidate_scores.csv", rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", required=True, help="VERSION=RUN_DIRECTORY")
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="anthropic/claude-sonnet-5.5")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    load_env()
    runs = dict(value.split("=", 1) for value in args.run)
    if len(runs) != len(args.run):
        raise ValueError("Run version names must be unique")
    runs = {key: Path(value) for key, value in runs.items()}
    selection = json.loads((next(iter(runs.values())) / "selection.json").read_text())
    from clir_bench.core.prompt_registry import validate_manifest
    manifest = validate_manifest(json.loads(args.prompt_manifest.read_text()))
    entry = manifest["prompts"]["evaluation/common"]
    prompt = entry["text"]
    if hashlib.sha256(prompt.encode()).hexdigest() != entry["sha256"]:
        raise ValueError("Common evaluation prompt hash mismatch")
    jobs, memberships = prepare(runs, selection)
    config = {"model": args.model, "prompt": {k: v for k, v in entry.items() if k != "text"},
              "jobs_sha256": digest(jobs), "memberships_sha256": digest(memberships),
              "criteria": SCORES,
              "usable": "grounding>=4, answer_resolution>=4, all other criteria>=3"}
    args.output.mkdir(parents=True, exist_ok=True)
    with RunState(args.output / "run.sqlite") as state:
        if state.get("fingerprint") not in (None, digest(config)):
            raise ValueError("Common evaluator inputs changed; use a new output directory")
        state.put("fingerprint", digest(config))
        state.put("config", config)
        state.put("prompts", {"evaluation/common": prompt})
        state.put("prompt_manifest", manifest)
        state.put("targets", selection)
        state.put("memberships", memberships)
        (args.output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
        (args.output / "prompt_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        completed = {o["task"] for o in state.outcomes() if o["status"] == "completed"}
        print(f"COMMON {len(jobs)} batches; {len(memberships)} candidate memberships; {len(completed)} cached", flush=True)
        if args.prepare_only:
            return

        def work(job):
            task, envelope = job
            checkpoint = state.checkpoint(task, retries=args.retries)
            def call():
                client = checkpoint.client("common_quality", args.model, llm.client_for(args.model))
                raw = llm.chat(client, args.model, [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(envelope, ensure_ascii=False)}],
                    reasoning_effort="low", max_tokens=12000)
                return validate(llm.parse_json_response(raw), envelope["candidates"])
            try:
                rows = checkpoint.run("common_quality", call)
                state.outcome(task, rows)
                return task, "completed"
            except Exception as error:  # noqa: BLE001 - persist provider and validation failures
                state.outcome(task, [], f"{type(error).__name__}: {error}")
                return task, "failed"

        remaining = [job for job in jobs if job[0] not in completed]
        # Validate the real output contract before launching the remaining paid batches.
        if remaining:
            first = work(remaining.pop(0))
            print("PREFLIGHT", *first, flush=True)
            if first[1] == "failed":
                state.put("status", "preflight_failed")
                export_traces(args.output)
                raise RuntimeError("Common evaluator preflight failed; inspect saved trace")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(work, job) for job in remaining]
            for number, future in enumerate(as_completed(futures), 1):
                result = future.result()
                print(f"{number}/{len(remaining)}", *result, flush=True)
                if number % 20 == 0:
                    export(state, args.output, memberships)
        rows = export(state, args.output, memberships)
        missing = sum(r["evaluation_status"] != "completed" for r in rows)
        state.put("status", "completed_with_errors" if missing else "completed")
        export_traces(args.output)
        print(f"DONE common evaluation: {len(rows)} rows; {missing} missing", flush=True)
        if missing:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
