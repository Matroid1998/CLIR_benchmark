"""Legal QAC commands, using the existing article and block batch pipelines."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from .batch_recording import RunState, read_run_metadata


def _digest(value) -> str:
    data = value if isinstance(value, bytes) else json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def _batches():
    from . import eurlex_batch, un_batch
    return {"eurlex": eurlex_batch, "un": un_batch}


def _read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or [])


_IDENTITY_FIELDS = ("corpus", "document_id", "target_id", "document_text_scope",
                    "question_language", "mode", "generator_model_name", "generator_model_id",
                    "candidate_id", "candidate_rank", "is_best", "question", "answer",
                    "faithfulness_verifier_model", "quality_verifier_model", "grading_status",
                    "grading_error", "total_score", "document_text")


def _write_csv(path, rows, fieldnames=()):
    fields = list(dict.fromkeys((*_IDENTITY_FIELDS, *fieldnames,
                                *(key for row in rows for key in row))))
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _group_key(row):
    return (row["corpus"], row["target_id"], row["question_language"], row["mode"],
            row["generator_model_id"], row.get("faithfulness_verifier_model", ""),
            row.get("quality_verifier_model", ""))


def _rank(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[_group_key(row)].append(row)
    for key, group in groups.items():
        def score(row):
            value = row.get("total_score")
            return float(value) if value not in (None, "") else float("-inf")
        ranked = sorted(group, key=score, reverse=True)
        chosen = False
        for position, row in enumerate(ranked, 1):
            valid = row.get("grading_status", row.get("regrade_status", "completed")) == "completed"
            valid = valid and row.get("total_score") not in (None, "")
            row["candidate_rank"] = position if valid else ""
            eligible = valid and (key[0] != "un" or float(row.get("faith_grounding") or 0) >= 3)
            row["is_best"] = bool(eligible and not chosen)
            chosen = chosen or eligible
            row["best_selection_rule"] = "highest_total_grounding_at_least_3" if key[0] == "un" else "highest_total"
            row["best_selection_semantics"] = "Score ranking; check quality_audit_status separately for validity."


def _locations(args, context, sources=None):
    from clir_bench.core.runs import make_run_id
    sources = list(dict.fromkeys(sources if sources is not None else (getattr(args, "source", None) or [])))
    if len(sources) != 1:
        raise ValueError("a run folder belongs to exactly one source")
    root = context.workspace.qac_dir(sources[0])
    directory = getattr(args, "run_dir", None)
    directory = Path(directory) if directory else root / make_run_id()
    filename = Path(getattr(args, "output", None) or "results.csv")
    if filename.name != str(filename) or filename.suffix.lower() != ".csv":
        raise ValueError("--output must be a CSV filename within --run-dir")
    output = directory / filename
    resume = getattr(args, "resume", False)
    if resume and not (directory / "run.sqlite").is_file():
        raise ValueError("--resume requires an existing run.sqlite")
    if not resume and directory.exists() and any(directory.iterdir()):
        raise ValueError(f"run directory is not empty; choose another or use --resume: {directory}")
    saved = read_run_metadata(directory) if resume else {}
    if saved.get("imported") and resume:
        raise ValueError("historical imports have no resumable stage checkpoints; use --targets-from or regrade")
    if saved.get("output") and filename.name != saved["output"]:
        if getattr(args, "output", None):
            raise ValueError("--resume cannot change the output filename")
        output = directory / saved["output"]
    return directory, output, saved


def _run_locations(args, context, sources):
    """A shared experiment ID, with a separate resumable run for each corpus."""
    if len(sources) == 1:
        return {sources[0]: _locations(args, context, sources)}
    from clir_bench.core.runs import make_run_id
    run_id = make_run_id()
    parent = getattr(args, "run_dir", None)
    folders = {source: (Path(parent) / ("un_parallel" if source == "un" else source)
                        if parent else context.workspace.qac_dir(source) / run_id) for source in sources}
    return {source: _locations(SimpleNamespace(**(vars(args) | {"run_dir": directory})), context, [source])
            for source, directory in folders.items()}


def _joined_metadata(records):
    present = [record for record in records if record]
    if not present:
        return {}
    targets, seen = [], set()
    for record in present:
        for entry in record.get("targets", []):
            key = _digest([entry["corpus"], entry["target"]])
            if key not in seen:
                targets.append(entry)
                seen.add(key)
    return dict(present[0], targets=targets)


def _target_metadata(path, sources):
    path = Path(path)
    if path.is_file() or (path / "run.sqlite").is_file():
        record = read_run_metadata(path)
        records = [record]
        available = {entry["corpus"] for entry in record.get("targets", [])}
        related = record.get("related_runs", {})
        related = related if isinstance(related, dict) else {}
        for source in sources:
            sibling = related.get(source)
            if source not in available and sibling:
                records.append(read_run_metadata(Path(sibling)))
        return _joined_metadata(records)
    return _joined_metadata(read_run_metadata(path / ("un_parallel" if source == "un" else source))
                            for source in sources)


def _options(args, context, saved=None):
    old = (saved or {}).get("config", {})
    defaults = {"questions": 100, "seed": 42, "keep": 3, "retries": 3,
                "max_references": 6, "context_chars": 30000,
                "reference_chars": None,
                "generation_model": [context.setting("generation_model", "gpt-5.6-luna")],
                "verifier_model": context.setting("verifier_model", "anthropic/claude-sonnet-5"),
                "langs": None, "modes": None}
    options = {key: getattr(args, key, None) if getattr(args, key, None) is not None
               else old.get(key, default) for key, default in defaults.items()}
    for key in ("questions", "keep", "retries"):
        if options[key] < 1:
            raise ValueError(f"--{key} must be positive")
    if options["max_references"] < 0 or options["context_chars"] < 0:
        raise ValueError("context limits must be nonnegative")
    if not options["verifier_model"] or not options["generation_model"] or any(
            not isinstance(model, str) or not model.strip() for model in options["generation_model"]):
        raise ValueError("generator and verifier model IDs must be nonempty")
    return options


def _indexes(sources, supplied=None, *, context=None):
    batches = _batches()
    indexes = {}
    for source in sources:
        if (supplied or {}).get(source) is not None:
            indexes[source] = supplied[source]
        elif source == "eurlex":
            directory = context.workspace.data("eurlex_structure")
            indexes[source] = batches[source].ctx.ArticleIndex(
                articles_path=directory / "articles.jsonl", edges_path=directory / "internal_edges.jsonl",
                external_edges_path=directory / "external_edges.jsonl", status_path=directory / "reference_status.jsonl",
                quarantine_path=directory / "quarantine.jsonl")
        else:
            directory = context.workspace.data("un_blocks")
            indexes[source] = batches[source].ctx.BlockIndex(
                blocks_path=directory / "blocks_en.jsonl", docs_path=directory / "docs_en.jsonl",
                status_path=directory / "reference_status_en.jsonl", sixway_dir=context.workspace.data("un_parallel"))
    return indexes


def _select(sources, indexes, options):
    batches, selections = _batches(), []
    for position, source in enumerate(sources):
        batch = batches[source]
        languages = options["langs"] or (["en", "fr", "de", "es"] if source == "eurlex" else ["en", "fr", "es", "zh"])
        modes = options["modes"] or (batch.gen.MODES if source == "eurlex" else batch.DEFAULT_MODES)
        supported_langs = batch.ACT_LANGUAGES if source == "eurlex" else batch.UN_LANGUAGES
        supported_modes = batch.gen.MODES if source == "eurlex" else batch.SUPPORTED_MODES
        # Mixed-source selections may name the union of their supported personas/languages.
        active_languages = [language for language in languages if language in supported_langs]
        active_modes = [mode for mode in modes if mode in supported_modes]
        if not active_languages or not active_modes:
            raise ValueError(f"no selected languages/personas are supported by {source}")
        count = options["questions"] // len(sources) + (position < options["questions"] % len(sources))
        if count:
            targets = batch.select(indexes[source], n=count, seed=options["seed"],
                                   languages=active_languages, modes=active_modes)
            selections.extend({"corpus": source, "target": asdict(target)} for target in targets)
    all_modes = set().union(*(set(batches[s].gen.MODES if s == "eurlex" else batches[s].SUPPORTED_MODES) for s in sources))
    all_langs = set().union(*(set(batches[s].ACT_LANGUAGES if s == "eurlex" else batches[s].UN_LANGUAGES) for s in sources))
    if set(options["modes"] or []) - all_modes or set(options["langs"] or []) - all_langs:
        raise ValueError("unsupported language or persona in the selected sources")
    return selections


def _prepare(selections, indexes, options, operation):
    batches = _batches()
    targets = [(entry, batches[entry["corpus"]].Target(**entry["target"])) for entry in selections]
    if "un" in indexes:
        wanted = defaultdict(set)
        for entry, target in targets:
            if entry["corpus"] == "un" and target.language != "en":
                wanted[target.language].add(target.doc_id)
                wanted[target.language].update(batches["un"]._cited_doc_ids(indexes["un"], target))
        for language, docs in sorted(wanted.items()):
            indexes["un"].preload_translations([language], docs)
    prepared, prompts = [], {}
    for entry, target in targets:
        source, batch = entry["corpus"], batches[entry["corpus"]]
        supported_modes = batch.gen.MODES if source == "eurlex" else batch.SUPPORTED_MODES
        supported_languages = batch.ACT_LANGUAGES if source == "eurlex" else batch.UN_LANGUAGES
        if target.mode not in supported_modes or target.language not in supported_languages:
            raise ValueError(f"unsupported saved target persona/language for {source}")
        limits = {"max_references": options["max_references"]} if source == "eurlex" else {
            "context_chars": options["context_chars"], "reference_chars": options["reference_chars"]}
        payload = batch.prepare_payload(target, indexes[source], **limits)
        if payload is None:
            raise ValueError(f"target cannot be reconstructed: {entry['target']}")
        if hasattr(payload, "target") and not payload.target.texts.get(target.language):
            raise ValueError(f"target has no source text in {target.language}: {entry['target']}")
        digest = _digest(payload.text.encode())
        if entry.get("payload_sha256") and digest != entry["payload_sha256"]:
            raise ValueError(f"source payload changed: {entry['target']}")
        entry["payload_sha256"] = digest
        pack = batch.gen.PROMPTS
        prompts[f"{source}/faithfulness"] = pack.faithfulness("batch")
        prompts[f"{source}/quality/{target.mode}"] = pack.quality(target.mode, "batch")
        if operation == "generate":
            prompts[f"{source}/generation/{target.mode}/{target.language}"] = pack.generation(target.mode, target.language)
        prepared.append((entry, target, payload))
    return prepared, prompts


def generate(args, context, *, selections=None, supplied_indexes=None):
    from clir_bench.core.prompts import load_prompt
    load_prompt.cache_clear()
    if getattr(args, "append", False):
        raise ValueError("legal runs use a new folder or --resume instead of --append")
    if (getattr(args, "exclude_from", None) or getattr(args, "pool", None)
            or getattr(args, "priority_langs", None) or getattr(args, "plan", "balanced") != "balanced"):
        raise ValueError("legal selection uses its batch samplers or --targets-from")
    sources = list(dict.fromkeys(args.source))
    if not sources or set(sources) - {"eurlex", "un"}:
        raise ValueError("legal sources are eurlex and un")
    locations = _run_locations(args, context, sources)
    saved = _joined_metadata(location[2] for location in locations.values())
    origin = _target_metadata(args.targets_from, sources) if getattr(args, "targets_from", None) else saved
    inherited = {key: value for key, value in origin.get("config", {}).items()
                 if key in ("max_references", "context_chars", "reference_chars", "seed")}
    options = _options(args, context, saved or {"config": inherited})
    if selections is None:
        selections = [entry for entry in origin.get("targets", []) if entry["corpus"] in sources] or None
        if origin and selections is None:
            raise ValueError("input run has no matching saved targets")
        if origin and set(sources) - {entry["corpus"] for entry in selections or []}:
            raise ValueError("saved target plan does not cover every requested source")
        if selections is not None and not saved:
            for key, field in (("modes", "mode"), ("langs", "language")):
                requested = getattr(args, key, None)
                expected = origin.get("config", {}).get(key) or {entry["target"][field] for entry in selections}
                if requested and set(requested) != set(expected):
                    raise ValueError(f"--{key} cannot change the selections in a saved target plan")
            requested_count = getattr(args, "questions", None)
            if requested_count is not None and requested_count != len(selections):
                raise ValueError("--questions differs from the saved target count")
    indexes = _indexes(sources, supplied_indexes, context=context)
    selections = selections if selections is not None else _select(sources, indexes, options)
    if getattr(args, "limit", None):
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        selections = selections[:args.limit]
    if not selections:
        raise ValueError("selection produced no targets")
    prepared, prompts = _prepare(selections, indexes, options, "generate")
    models = list(dict.fromkeys(options["generation_model"]))
    options["generation_model"] = models
    cases = [(entry, target, payload, model, None)
             for entry, target, payload in prepared for model in models]
    return _execute_sources(args, context, "generate", locations, options, selections,
                            prompts, indexes, cases)


def regrade(args, context):
    from clir_bench.core.prompts import load_prompt
    load_prompt.cache_clear()
    rows, fields = _read_csv(args.input)
    if not rows:
        raise ValueError("input CSV has no generated candidates")
    source_hint = getattr(args, "source", None) or []
    input_sources = list(dict.fromkeys(row.get("corpus") or (source_hint[0] if len(source_hint) == 1 else "")
                                      for row in rows))
    if set(input_sources) - {"eurlex", "un"}:
        raise ValueError("input needs corpus=eurlex/un, or a single --source")
    locations = _run_locations(args, context, input_sources)
    saved = _joined_metadata(location[2] for location in locations.values())
    input_hash = _digest(Path(args.input).read_bytes())
    parent = read_run_metadata(Path(args.input).parent) if (Path(args.input).parent / "run.sqlite").exists() else {}
    options = _options(args, context, saved or parent)
    batches, groups = _batches(), defaultdict(list)
    selected_sources = getattr(args, "source", None)
    for position, row in enumerate(rows, 1):
        row["corpus"] = row.get("corpus") or (selected_sources[0] if selected_sources and len(selected_sources) == 1 else "")
        source = row["corpus"]
        if source not in batches:
            raise ValueError("input needs corpus=eurlex/un, or a single --source")
        if selected_sources and source not in selected_sources:
            raise ValueError("--source must cover every input row; regrading never silently removes rows")
        row["target_id"] = row.get("target_id") or row.get("target_article_id") or row.get("block_id")
        if not row.get("generator_model_id") or not row.get("question") or not row.get("answer") or not row["target_id"]:
            raise ValueError(f"input row {position} lacks generator identity, target, question, or answer")
        row["candidate_id"] = row.get("candidate_id") or "q_" + _digest([input_hash, position])[:24]
        row["generator_model_name"] = row.get("generator_model_name") or row["generator_model_id"].rsplit("/", 1)[-1]
        groups[_group_key(row)[:5]].append(row)
    ids = [row["candidate_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("candidate_id must be unique in the input CSV")
    sources = list(dict.fromkeys(row["corpus"] for row in rows))
    selections, seen = [], set()
    inherited = {(e["corpus"], e["target"].get("eli_id") or e["target"].get("block_id"),
                  e["target"]["language"], e["target"]["mode"]): e for e in parent.get("targets", [])}
    for key, group in groups.items():
        identity = key[:4]
        hashes = {row["source_payload_sha256"] for row in group if row.get("source_payload_sha256")}
        if len(hashes) > 1:
            raise ValueError("input rows disagree on source payload")
        if identity not in seen:
            entry = dict(inherited.get(identity) or {"corpus": key[0], "target": asdict(batches[key[0]].target_from_rows(group))})
            if hashes:
                if entry.get("payload_sha256") and entry["payload_sha256"] not in hashes:
                    raise ValueError("input source payload differs from its parent run")
                entry["payload_sha256"] = next(iter(hashes))
            selections.append(entry)
            seen.add(identity)
        elif hashes:
            previous = next(e for e in selections if (e["corpus"],
                e["target"].get("eli_id") or e["target"].get("block_id"),
                e["target"]["language"], e["target"]["mode"]) == identity)
            if previous.get("payload_sha256") and previous["payload_sha256"] not in hashes:
                raise ValueError("different generators received different source payloads")
            previous["payload_sha256"] = next(iter(hashes))
    indexes = _indexes(sources, context=context)
    prepared, prompts = _prepare(selections, indexes, options, "regrade")
    contexts = {(e["corpus"], t.eli_id if e["corpus"] == "eurlex" else t.block_id, t.language, t.mode): (e,t,p)
                for e,t,p in prepared}
    cases = [(*contexts[key[:4]], key[4], group) for key, group in groups.items()]
    options["input_sha256"] = input_hash
    return _execute_sources(args, context, "regrade", locations, options, selections,
                            prompts, indexes, cases, original_rows=rows, original_fields=fields)


def _execute_sources(args, context, operation, locations, options, selections,
                     prompts, indexes, cases, *, original_rows=None, original_fields=()):
    jobs = []
    for source, (directory, output, saved) in locations.items():
        selected = [entry for entry in selections if entry["corpus"] == source]
        if not selected:
            continue
        parameters = (args, context, operation, directory, output, saved, options, selected,
                      {key: value for key, value in prompts.items() if key.startswith(source + "/")},
                      {source: indexes[source]}, [case for case in cases if case[0]["corpus"] == source])
        keywords = {"original_rows": ([row for row in original_rows if row["corpus"] == source]
                                      if original_rows is not None else None),
                    "original_fields": original_fields,
                    "related_runs": {key: str(value[0].resolve()) for key, value in locations.items()
                                     if any(entry["corpus"] == key for entry in selections)}}
        # Check every corpus before any billable work or output is started.
        _execute(*parameters, **keywords, validate_only=True)
        jobs.append((parameters, keywords))
    status = 0
    for parameters, keywords in jobs:
        status = max(status, _execute(*parameters, **keywords))
    return status


def _execute(args, context, operation, directory, output, saved, options, selections,
             prompts, indexes, cases, *, original_rows=None, original_fields=(),
             related_runs=None, validate_only=False):
    config = dict(options, operation=operation, targets=selections,
                  prompts_sha256={key: _digest(text.encode()) for key, text in prompts.items()})
    cache_path = getattr(args, "generation_cache", None) or saved.get("config", {}).get("generation_cache")
    if cache_path:
        config["generation_cache"] = str(Path(cache_path).resolve())
        config["generation_cache_sha256"] = _digest(Path(cache_path).read_bytes())
    fingerprint = _digest(config)
    if saved and saved.get("fingerprint") != fingerprint:
        raise ValueError("resume settings, prompts, or source inputs changed; start a new run")
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    if validate_only:
        return 0
    print(f"{operation}: {len(selections)} shared targets, {len(cases)} model/target cases -> {output}")
    if getattr(args, "dry_run", False):
        print(f"no model calls; at most {len(cases) * (3 if operation == 'generate' else 2)} initial stage calls")
        return 0
    batches = _batches()
    originals = {row["candidate_id"]: row for row in original_rows or []}
    with RunState(directory / "run.sqlite") as state:
        # A second process may have completed after the preflight path check.
        if saved:
            if state.get("fingerprint") != fingerprint:
                raise ValueError("run state changed since preflight; start a new run")
        elif state.get("schema_version") is not None or state.outcomes():
            raise ValueError("run directory acquired an existing run; choose another directory")
        if cache_path:
            state.load_replay(Path(cache_path), options["generation_model"])
        for key, value in {"schema_version": 1, "config": config, "fingerprint": fingerprint,
                           "targets": selections, "prompts": prompts, "output": output.name,
                           "status": "running"}.items():
            state.put(key, value)
        if original_rows is not None:
            state.put("input", {"path": str(Path(args.input).resolve()), "sha256": options["input_sha256"]})
        if related_runs:
            state.put("related_runs", (state.get("related_runs") or {}) | related_runs)
        completed = {record["task"] for record in state.outcomes()
                     if record["status"] in ("completed", "no_candidates")}
        def work(case):
            entry, target, payload, model, candidates = case
            source = entry["corpus"]
            task = _digest([source, asdict(target), model, [c["candidate_id"] for c in candidates or []]])
            if task in completed:
                return task
            limits = {"max_references": options["max_references"]} if source == "eurlex" else {
                "context_chars": options["context_chars"], "reference_chars": options["reference_chars"]}
            try:
                result = batches[source].run_one(target, indexes[source], gen_model=model,
                    grade_model=options["verifier_model"], keep=options["keep"] if candidates is None else len(candidates),
                    existing_candidates=candidates, checkpoint=state.checkpoint(task, retries=options["retries"]),
                    retries=options["retries"], payload=payload, **limits)
                for row in result:
                    row.setdefault("generator_model_name", model.rsplit("/", 1)[-1])
                    row["source_payload_sha256"] = entry["payload_sha256"]
                    for phase, prompt_key in (("faithfulness", f"{source}/faithfulness"),
                                              ("quality", f"{source}/quality/{target.mode}")):
                        row[f"{phase}_verifier_prompt_sha256"] = config["prompts_sha256"][prompt_key]
                    if originals:
                        original = originals[row["candidate_id"]]
                        old = {k: v for k,v in original.items() if not (k.startswith(("faith_", "qual_", "quality_", "faithfulness_", "regrade_", "grading_"))
                               or k in ("total_score", "candidate_rank", "is_best"))}
                        old.update(row)
                        # Metadata supplied by the caller remains authoritative.
                        for key in ("question", "answer", "generator_model_name", "generator_model_id", "candidate_id"):
                            old[key] = original[key]
                        row.clear()
                        row.update(old)
                        row["regrade_status"] = row.get("grading_status", "completed")
                        row["regrade_error"] = row.get("grading_error", "")
                        row["regraded_at_utc"] = datetime.now(timezone.utc).isoformat()
                        row["previous_comparison_sha256"] = options["input_sha256"]
                from .batch_recording import _redact
                for row in result:
                    for diagnostic in ("grading_error", "regrade_error"):
                        if diagnostic in row:
                            row[diagnostic] = _redact(row[diagnostic], state._secrets)
                error = "; ".join(sorted({r.get("grading_error", "") for r in result if r.get("grading_status") == "failed"}))
                state.outcome(task, result, error)
            except Exception as exc:  # noqa: BLE001 - provider and parser failures must preserve candidates
                # Regrading must retain every original question even when context/transport fails.
                from .batch_recording import _redact
                diagnostic = _redact(str(exc), state._secrets)
                result = []
                for original in candidates or []:
                    row = {k: v for k,v in original.items() if not k.startswith(("faith_", "qual_", "quality_", "faithfulness_"))}
                    row.update(grading_status="failed", grading_error=diagnostic, regrade_status="failed",
                               regrade_error=diagnostic, total_score="", candidate_rank="", is_best=False)
                    result.append(row)
                state.outcome(task, result, str(exc))
            return task

        def export():
            outcomes = state.outcomes()
            result = [row for record in outcomes for row in record["rows"]]
            if originals:
                positions = {key: i for i,key in enumerate(originals)}
                result.sort(key=lambda row: positions[row["candidate_id"]])
            _rank(result)
            _write_csv(output, result, original_fields)
            return outcomes, result

        executor = ThreadPoolExecutor(max_workers=args.workers)
        try:
            futures = [executor.submit(work, case) for case in cases]
            for number, future in enumerate(as_completed(futures), 1):
                future.result()
                if number % 10 == 0 or number == len(futures):
                    print(f"completed {number}/{len(futures)} cases", flush=True)
        except BaseException:
            state.cancelled.set()
            executor.shutdown(wait=True, cancel_futures=True)
            export()
            state.put("status", "interrupted")
            raise
        else:
            executor.shutdown(wait=True)
        outcomes, rows = export()
        counts = dict(Counter(record["status"] for record in outcomes))
        state.put("summary", dict(counts, candidates=len(rows), best=sum(bool(r["is_best"]) for r in rows)))
        state.put("status", "completed_with_errors" if counts.get("failed") else "completed")
        state.put("results_sha256", _digest(output.read_bytes()))
        print(f"wrote {len(rows)} candidates; outcomes {counts}; state -> {state.path}")
        return 1 if counts.get("failed") else 0


def best(args, context):
    rows, fields = _read_csv(args.input)
    _rank(rows)
    selected = [row for row in rows if row["is_best"]]
    output = Path(args.output) if args.output else Path(args.input).with_stem(Path(args.input).stem + "_best")
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    _write_csv(output, selected, fields)
    print(f"wrote {len(selected)} best candidates -> {output}")
    return 0


def legacy_main(args, *, index, corpus, targets):
    """Adapt the original batch arguments after their corpus-specific selection."""
    from clir_bench.core.config import load_settings
    from clir_bench.core.context import AppContext
    from clir_bench.domains.legal import SPEC
    context = AppContext.build(load_settings(), SPEC)
    output = Path(args.out) if args.out else None
    options = SimpleNamespace(
        source=[corpus], questions=args.n, generation_model=[args.gen_model],
        verifier_model=args.grade_model, workers=args.workers, seed=args.seed,
        keep=args.keep, retries=3, dry_run=args.dry_run,
        langs=None, modes=None, targets_from=None, resume=False,
        run_dir=output.parent if output and str(output.parent) != "." else None,
        output=Path(output.name) if output else None,
        max_references=getattr(args, "max_references", 6),
        context_chars=getattr(args, "context_chars", 30000),
        reference_chars=(_batches()["un"].refs.DEFAULT_REFERENCE_CHARS
                         if corpus == "un" and getattr(args, "no_fit", False) else None),
        generation_cache=getattr(args, "generation_cache", None),
    )
    if getattr(args, "generation_records", None):
        print("generation recording is included in run.sqlite; separate recording files are no longer needed")
    return generate(options, context,
                    selections=[{"corpus": corpus, "target": asdict(target)} for target in targets],
                    supplied_indexes={corpus: index})
