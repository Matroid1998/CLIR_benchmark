"""Run independent Jev suitability on exact source inputs from a saved screening run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from clir_bench.core import prompt_registry
from clir_bench.domains.legal.qac import decider
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.env import load_env
from clir_bench.domains.legal.qac.screening import digest
from clir_bench.domains.legal.qac.screening_analysis import write_csv


def load_targets(parent: Path) -> list[dict]:
    """Require saved targets to match the actual previous native Jev requests."""
    with sqlite3.connect((parent / "run.sqlite").resolve().as_uri() + "?mode=ro", uri=True) as db:
        metadata = {k: json.loads(v) for k, v in db.execute("SELECT key,value FROM metadata")}
        if metadata.get("status") != "completed":
            raise ValueError("Eligibility replay requires a completed parent screening run")
        records = {}
        for task, raw in db.execute("SELECT task,record FROM requests WHERE stage='decider'"):
            record = json.loads(raw)
            request = record.get("request")
            if not request or not task.endswith("/jev"):
                continue
            value = request.get("state")
            if task in records and records[task] != value:
                raise ValueError(f"Parent Jev inputs changed between attempts: {task}")
            records[task] = value
        outcomes = {task: (status, json.loads(rows)) for task, status, rows in
                    db.execute("SELECT task,status,rows FROM outcomes")}
    targets, seen, documents = [], set(), set()
    for entry in metadata["targets"]:
        corpus, target_id = entry["corpus"], entry["target_id"]
        key = corpus, target_id
        document = corpus, entry["document_id"]
        if corpus not in decider.MODES or key in seen or document in documents:
            raise ValueError(f"Unsupported or duplicated parent target: {key}")
        seen.add(key)
        documents.add(document)
        task = f"decider/{corpus}/{target_id}/jev"
        text = records.get(task)
        if (not isinstance(text, str) or text != entry["source_payload"]
                or hashlib.sha256(text.encode()).hexdigest() != entry["source_payload_sha256"]):
            raise ValueError(f"Parent source payload differs from recorded Jev input: {key}")
        status, rows = outcomes.get(task, (None, []))
        if status != "completed" or len(rows) != 1:
            raise ValueError(f"Missing successful parent Jev decision: {key}")
        if rows[0]["mode"] not in (*decider.MODES[corpus], "skip"):
            raise ValueError(f"Parent uses a different mode vocabulary: {key}")
        targets.append(dict(entry, previous_pick=rows[0]["mode"],
                            previous_confidence=rows[0].get("confidence")))
    if not targets:
        raise ValueError("Parent contains no targets")
    return targets


def run(parent: Path, output: Path, *, threshold=0.5, workers=8, retries=3):
    if parent.resolve() == output.resolve():
        raise ValueError("Eligibility output must be separate from its parent")
    decider._probability(threshold)
    if workers < 1 or retries < 1:
        raise ValueError("workers and retries must be positive")
    load_env()
    targets = load_targets(parent)
    sources = sorted({entry["corpus"] for entry in targets})
    prompts = {source: decider.eligibility_prompt_text(source) for source in sources}
    # Validate every request before making any provider call.
    for source in sources:
        decider.build_eligibility_request(source, "validation")
    config = {"operation": "jev_eligibility_only", "parent_run": str(parent.resolve()),
              "model": decider.JEV_MODEL, "threshold": threshold, "retries": retries,
              "documents_by_corpus": dict(Counter(e["corpus"] for e in targets)),
              "source_inputs": "Exact recorded parent Jev state; no questions or grades",
              "targets_sha256": digest(targets), "prompts_sha256": digest(prompts),
              "prompt_registry": prompt_registry.manifest_metadata()}
    fingerprint = digest(config)
    output.mkdir(parents=True, exist_ok=True)
    with RunState(output / "run.sqlite") as state:
        if state.get("fingerprint") not in (None, fingerprint):
            raise ValueError("Eligibility inputs, prompts, or settings changed on resume")
        for key, value in {"fingerprint": fingerprint, "config": config, "targets": targets,
                           "prompts": prompts, "output": "decisions.csv", "status": "running"}.items():
            state.put(key, value)
        manifest_path = prompt_registry.selection()
        if manifest_path:
            manifest = prompt_registry.read_manifest(manifest_path)
            state.put("prompt_manifest", manifest)
            prompt_registry.write_manifest(output / "prompt_manifest.json", manifest)
        (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
        completed = {r["task"] for r in state.outcomes() if r["status"] == "completed"}

        def work(entry):
            source, target_id = entry["corpus"], entry["target_id"]
            task = f"eligibility/{source}/{target_id}"
            if task in completed:
                return task, "replayed"
            try:
                result = decider.decide_eligibility(source, entry["source_payload"],
                    threshold=threshold, checkpoint=state.checkpoint(task, retries=retries))
                rows = []
                for mode, probability in result["probabilities_yes"].items():
                    row = {key: entry.get(key, "") for key in (
                        "corpus", "document_id", "target_id", "symbol", "source_payload_sha256",
                        "previous_pick", "previous_confidence")}
                    row.update(mode=mode, probability_yes=probability,
                               selected=mode in result["selected_modes"], threshold=threshold,
                               response_model=result["response_model"])
                    rows.append(row)
                state.outcome(task, rows)
                return task, "completed"
            except Exception as error:  # noqa: BLE001 - checkpoint failures remain resumable
                state.outcome(task, [], f"{type(error).__name__}: {error}")
                return task, "failed"

        # Confirm the native noul contract for each corpus before the remaining calls.
        smoke = [next(e for e in targets if e["corpus"] == source) for source in sources]
        with ThreadPoolExecutor(max_workers=min(workers, len(smoke))) as executor:
            first = list(executor.map(work, smoke))
        for result in first:
            print("PREFLIGHT", *result, flush=True)
        preflight_failed = any(status == "failed" for _, status in first)
        if not preflight_failed:
            rest = [entry for entry in targets if entry not in smoke]
            with ThreadPoolExecutor(max_workers=workers) as executor:
                for i, future in enumerate(as_completed([executor.submit(work, e) for e in rest]), 1):
                    print(f"{i}/{len(rest)}", *future.result(), flush=True)
        outcomes = state.outcomes()
        failures = [r for r in outcomes if r["status"] != "completed"]
        rows = [row for outcome in outcomes if outcome["status"] == "completed"
                for row in outcome["rows"]]
        state.put("status", "completed_with_errors" if failures else "completed")
        state.put("summary", {"documents": len(targets), "decisions": len(rows),
                              "yes": sum(row["selected"] for row in rows), "failures": len(failures)})
        if rows:
            write_csv(output / "decisions.csv", rows)
            wide = []
            for entry in targets:
                selected = [r for r in rows if (r["corpus"], r["target_id"])
                            == (entry["corpus"], entry["target_id"])]
                if not selected:
                    continue
                document = {key: entry[key] for key in ("corpus", "document_id", "target_id", "symbol")}
                document["threshold"] = threshold
                document["selected_modes"] = "|".join(r["mode"] for r in selected if r["selected"])
                for row in selected:
                    document[f"{row['mode']}__yes"] = row["selected"]
                    document[f"{row['mode']}__probability_yes"] = row["probability_yes"]
                wide.append(document)
            write_csv(output / "decisions_only.csv", wide)
    export_traces(output)
    if failures:
        raise RuntimeError(f"{len(failures)} eligibility tasks failed; inspect recorded calls")
    print(f"DONE {len(targets)} documents, {len(rows)} independent decisions", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grades-csv", type=Path, help="Existing blinded five-verifier grades to compare")
    parser.add_argument("--prompt-manifest", type=Path)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()
    if args.prompt_manifest:
        os.environ["CLIR_PROMPT_MANIFEST"] = str(args.prompt_manifest.resolve())
    if args.grades_csv and not args.grades_csv.is_file():
        parser.error("--grades-csv must exist")
    run(args.parent, args.output, threshold=args.threshold, workers=args.workers, retries=args.retries)
    if args.grades_csv:
        from clir_bench.domains.legal.qac.screening_eligibility_analysis import analyze
        analyze(args.output, args.grades_csv)


if __name__ == "__main__":
    main()
