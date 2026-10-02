"""Reproducible paired decider screening on fixed legal targets.

Each target is routed by both deciders and generated independently under every
current decider mode, including all modes on meeting records.
All provider calls use normal pipeline prompts,
recorders, retry budgets, and candidate grading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, replace
from pathlib import Path

from clir_bench.domains.legal.qac import _write_csv, decider, eurlex_batch, un_batch
from clir_bench.domains.legal.qac.batch_recording import RunState, export_traces
from clir_bench.domains.legal.qac.env import load_env

BATCHES = {"un": un_batch, "eurlex": eurlex_batch}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def meeting(symbol):
    return bool(re.search(r"(?:^|/)\s*(?:PV|SR)(?:[./(\d]|$)", symbol.upper()))


def task_id(kind, record, mode):
    return f"{kind}/{record['corpus']}/{record['target_id']}/{mode}"


def prepare(args):
    if getattr(args, "selection", None):
        return replay_selection(args.selection)
    entries, payloads = [], {}
    exclusion_file = getattr(args, 'exclude_documents', None)
    exclusions = json.loads(exclusion_file.read_text()) if exclusion_file else []
    for source in ("un", "eurlex"):
        count = getattr(args, source)
        if not count:
            continue
        batch = BATCHES[source]
        index = batch.ctx.BlockIndex() if source == "un" else batch.ctx.ArticleIndex()
        options = {"max_per_doc": 1} if source == "un" else {"max_per_act": 1}
        targets = batch.select(index, n=count, seed=args.seed, languages=["en"],
                               modes=["lookup"], excluded_documents=frozenset(
                                   r['document_id'] for r in exclusions if r['corpus'] == source), **options)
        if len(targets) != count:
            raise ValueError(f"Requested {count} {source} documents but selected {len(targets)}")
        for target in targets:
            payload = batch.prepare_payload(target, index)
            unit = payload.target
            identifier = target.block_id if source == "un" else target.eli_id
            doc_id = target.doc_id if source == "un" else target.celex_id
            text = unit.texts["en"]
            record = {"corpus": source, "target_id": identifier, "document_id": doc_id,
                      "symbol": getattr(unit, "symbol", doc_id),
                      "title": (unit.title if source == "un" else unit.act_titles.get("en", "")),
                      "is_meeting": meeting(unit.symbol) if source == "un" else False,
                      "stratum": target.stratum, "target": asdict(target),
                      "document_text": text, "source_payload": payload.text,
                      "source_payload_sha256": hashlib.sha256(payload.text.encode()).hexdigest()}
            entries.append(record)
            payloads[(source, identifier)] = payload
    return entries, payloads


def replay_selection(path):
    """Rebuild saved targets, refusing corpus or context drift before any calls."""
    entries = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Selection must be a nonempty list of saved screening targets")
    indexes, payloads = {}, {}
    for record in entries:
        source = record["corpus"]
        batch = BATCHES[source]
        key = (source, record["target_id"])
        if key in payloads:
            raise ValueError(f"Duplicate saved target: {key}")
        if source not in indexes:
            indexes[source] = batch.ctx.BlockIndex() if source == "un" else batch.ctx.ArticleIndex()
        target = batch.Target(**record["target"])
        if target.language != "en":
            raise ValueError("Screening comparisons currently require English targets")
        payload = batch.prepare_payload(target, indexes[source])
        expected = record["source_payload_sha256"]
        saved = record["source_payload"]
        if (payload is None or payload.text != saved
                or hashlib.sha256(saved.encode()).hexdigest() != expected):
            raise ValueError(f"Saved source payload changed for {key}; refusing unpaired comparison")
        actual_id = payload.target.block_id if source == "un" else payload.target.eli_id
        if actual_id != record["target_id"]:
            raise ValueError(f"Saved target identity mismatch: {key}")
        payloads[key] = payload
    return entries, payloads


def export(state, directory, entries):
    outcomes = {o["task"]: o for o in state.outcomes()}
    decisions, candidates, runs = [], [], []
    for record in entries:
        meta = {k: v for k, v in record.items() if k != "target"}
        for backend in ("generator", "jev"):
            result = outcomes.get(task_id("decider", record, backend))
            if result:
                decisions.append(meta | {"backend": backend, "status": result["status"],
                    "error": result["error"] or ""} | (result["rows"][0] if result["rows"] else {}))
        for mode in decider.MODES[record["corpus"]]:
            result = outcomes.get(task_id("mode", record, mode))
            if result:
                candidates.extend(result["rows"])
                runs.append({"corpus": record["corpus"], "target_id": record["target_id"],
                    "mode": mode, "is_meeting": record["is_meeting"],
                    "eligible": True,
                    "status": result["status"], "error": result["error"] or "",
                    "candidate_count": len(result["rows"])})
    _write_csv(directory / "decisions.csv", decisions)
    _write_csv(directory / "all_mode_candidates.csv", candidates)
    _write_csv(directory / "mode_runs.csv", runs)
    return decisions, candidates, runs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--un", type=int, default=50)
    parser.add_argument("--eurlex", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--generator", default="gpt-5.6-luna")
    parser.add_argument("--verifier", default="anthropic/claude-sonnet-5.5")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--selection", type=Path,
                        help="Replay an existing selection.json and verify identical source payloads")
    parser.add_argument("--prompt-manifest", type=Path,
                        help="Pin an immutable registered prompt bundle for this run")
    parser.add_argument("--exclude-documents", type=Path,
                        help="JSON list of corpus/document_id pairs excluded before sampling")
    args = parser.parse_args()
    if args.un < 0 or args.eurlex < 0 or args.un + args.eurlex < 1:
        parser.error("choose a positive number of documents")
    load_env()
    if args.prompt_manifest:
        os.environ["CLIR_PROMPT_MANIFEST"] = str(args.prompt_manifest.resolve())
    from clir_bench.core import prompt_registry
    manifest_path = prompt_registry.selection()
    entries, payloads = prepare(args)
    prompts = {}
    for source in {entry["corpus"] for entry in entries}:
        pack = BATCHES[source].gen.PROMPTS
        for backend in ("generator", "jev"):
            prompts[f"{source}/decider/{backend}"] = decider.prompt_text(source, backend)
        prompts[f"{source}/faithfulness"] = pack.faithfulness("batch")
        for mode in decider.MODES[source]:
            for role in ("generation", "quality"):
                prompts[f"{source}/{role}/{mode}"] = (pack.generation(decider.generation_mode(mode), "en")
                    if role == "generation" else pack.quality(decider.generation_mode(mode), "batch"))
    counts_by_source = Counter(entry["corpus"] for entry in entries)
    config = {"un": counts_by_source["un"], "eurlex": counts_by_source["eurlex"], "seed": args.seed,
              "generator": args.generator, "verifier": args.verifier, "retries": args.retries,
              "language": "en", "max_per_document": 1, "keep": 3,
              "meeting_modes": "all",
              "jev_model": decider.JEV_MODEL, "prompts_sha256": digest(prompts),
              "targets_sha256": digest(entries)}
    if args.selection:
        config["selection_source"] = str(args.selection.resolve())
    if manifest_path:
        config["prompt_registry"] = prompt_registry.manifest_metadata()
    if args.exclude_documents:
        config['excluded_documents_sha256'] = digest(json.loads(args.exclude_documents.read_text()))
    fingerprint = digest(config)
    args.output.mkdir(parents=True, exist_ok=True)
    with RunState(args.output / "run.sqlite") as state:
        if state.get("fingerprint") not in (None, fingerprint):
            raise ValueError("Screening settings, prompts, or source inputs changed")
        state.put("fingerprint", fingerprint)
        state.put("config", config)
        state.put("prompts", prompts)
        if manifest_path:
            manifest = prompt_registry.read_manifest(manifest_path)
            state.put("prompt_manifest", manifest)
            (args.output / "prompt_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        state.put("targets", entries)
        state.put("output", "all_mode_candidates.csv")
        state.put("status", "prepared" if args.prepare_only else "running")
        (args.output / "selection.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2))
        (args.output / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2))
        _write_csv(args.output / "documents.csv", [{k: v for k, v in e.items() if k != "target"} for e in entries])
        print(f"Selected {len(entries)} unique documents: "
              f"{dict(Counter((e['corpus'], e['stratum']) for e in entries))}", flush=True)
        if args.prepare_only:
            return
        completed = {o["task"] for o in state.outcomes() if o["status"] != "failed"}

        def work(kind, record, mode):
            task = task_id(kind, record, mode)
            if task in completed:
                return task, "replayed"
            source = record["corpus"]
            payload = payloads[source, record["target_id"]]
            checkpoint = state.checkpoint(task, retries=args.retries)
            rows = []
            try:
                if kind == "decider":
                    decision = decider.decide(source, payload, backend=mode, model=args.generator,
                                              checkpoint=checkpoint)
                    rows = [decision]
                else:
                    batch = BATCHES[source]
                    target = replace(batch.Target(**record["target"]), mode=decider.generation_mode(mode))
                    limits = {"context_chars": 30000} if source == "un" else {"max_references": 6}
                    rows = batch.run_one(target, None, payload=payload, gen_model=args.generator,
                        grade_model=args.verifier, keep=3, checkpoint=checkpoint,
                        retries=args.retries, **limits)
                    for row in rows:
                        row.update(corpus=source, target_id=record["target_id"],
                                   document_id=record["document_id"], symbol=record["symbol"],
                                   screening_mode=mode, is_meeting=record["is_meeting"],
                                   mode_eligible=True)
                error = "; ".join(sorted({row.get("grading_error", "") for row in rows
                                         if row.get("grading_status") == "failed"}))
                state.outcome(task, rows, error)
                return task, "failed" if error else ("completed" if rows else "no_candidates")
            except Exception as error:  # noqa: BLE001 - preserve failed provider/parser tasks
                state.outcome(task, rows, f"{type(error).__name__}: {error}")
                return task, "failed"

        # Verify both routing endpoints and a real generation/grading batch before fan-out.
        first = next(e for e in entries if not e["is_meeting"])
        smoke = [("decider", first, "generator"), ("decider", first, "jev"),
                 ("mode", first, "lookup")]
        with ThreadPoolExecutor(max_workers=3) as executor:
            smoke_results = list(executor.map(lambda job: work(*job), smoke))
        for result in smoke_results:
            print("PREFLIGHT", *result, flush=True)
        export(state, args.output, entries)
        if any(status == "failed" for _, status in smoke_results):
            state.put("status", "preflight_failed")
            export_traces(args.output)
            raise RuntimeError("Endpoint preflight failed; inspect run.sqlite/trace.md before scaling")
        completed.update(task for task, _ in smoke_results)
        jobs = [("decider", entry, backend) for entry in entries for backend in ("generator", "jev")]
        jobs += [("mode", entry, mode) for entry in entries for mode in decider.MODES[entry["corpus"]]]
        jobs = [job for job in jobs if task_id(*job) not in completed]
        counts = Counter()
        executor = ThreadPoolExecutor(max_workers=args.workers)
        try:
            futures = [executor.submit(work, *job) for job in jobs]
            for number, future in enumerate(as_completed(futures), 1):
                task, status = future.result()
                counts[status] += 1
                print(f"{number}/{len(jobs)} {status} {task}", flush=True)
                if number % 10 == 0:
                    export(state, args.output, entries)
        except BaseException:
            state.cancelled.set()
            executor.shutdown(wait=True, cancel_futures=True)
            state.put("status", "interrupted")
            export(state, args.output, entries)
            raise
        else:
            executor.shutdown(wait=True)
        export(state, args.output, entries)
        failures = sum(o["status"] == "failed" for o in state.outcomes())
        state.put("status", "completed_with_errors" if failures else "completed")
        state.put("summary", dict(counts))
        export_traces(args.output)
        print(f"DONE {len(entries)} documents, {failures} failed tasks -> {args.output}", flush=True)


if __name__ == "__main__":
    main()
