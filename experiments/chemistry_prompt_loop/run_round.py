#!/usr/bin/env python3
"""Run capped, reproducible prompt experiments without selecting away failures.

Prepare only after the current prompt edits are ready. Preparation freezes the
sources, prompts, model settings, and independent evaluator contract. Running
uses those frozen artifacts and checkpoints each model stage separately.
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import random
import shutil
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from clir_bench.core import corpus, llm
from clir_bench.core.grading import (
    GraderConfig,
    grade_columns,
    grade_faithfulness,
    grade_quality,
)
from clir_bench.core.qagen import (
    CANDIDATE_METADATA_FIELDS,
    GenerationConfig,
    generate_candidates,
    normalize_row,
    select_best,
)
from clir_bench.domains.chemistry.qac import decider
from clir_bench.domains.chemistry.qac.candidates import parse_candidates
from clir_bench.domains.chemistry.schema import SCHEMA
from clir_bench.domains.chemistry.vocabulary import MODES

LANGUAGES = ("en", "fr", "es", "zh", "de")
QAC = ROOT / "data/chemistry/ai4chem_abstract_pairs/qac"
CORPUS = ROOT / "data/chemistry/ai4chem_abstract_pairs/multilingual_corpus.csv"
PROMPTS = ROOT / "src/clir_bench/domains/chemistry/qac/prompts"
BASELINE = QAC / "generation_100_jev_haiku_5_5_gemini_3_8_flash_20261014_batch2_review_with_source.csv"
DEFAULT_OUTPUT = ROOT / "reports/prompt_experiments/chemistry_loop_20261014"
MODEL_CONFIG = {
    "decider_model": decider.JEV_MODEL,
    "generation_model": "anthropic/claude-haiku-5.5",
    "verifier_model": "google/gemini-3.8-flash",
    "generation_reasoning_effort": "medium",
    "verifier_reasoning_effort": "low",
    "candidates_per_document": 3,
    "stage_attempt_limit": 3,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(normalize_row(row, fields) for row in rows)
    temporary.replace(path)


def source_packet(source: dict) -> str:
    return corpus.build_passages_text([source], SCHEMA, include_identifiers=True)


def sample_sources(rows: list[dict], *, excluded_ids: set[str], excluded_families: set[str],
                   count: int, seed: int) -> list[dict]:
    """Fix the entire screening budget before any model sees a document."""
    if not 1 <= count <= 50:
        raise ValueError("A round must have between 1 and 50 distinct source documents")
    pool = {language: [] for language in LANGUAGES}
    identities = set()
    for row in rows:
        identity, family, language = (SCHEMA.id_of(row), SCHEMA.family_of(row),
                                      SCHEMA.language_of(row))
        if identity in identities:
            raise ValueError(f"Duplicate corpus ID: {identity}")
        identities.add(identity)
        if (identity and family and language in pool and SCHEMA.text_of(row)
                and identity not in excluded_ids and family not in excluded_families):
            pool[language].append(row)
    rng = random.Random(seed)
    for values in pool.values():
        values.sort(key=SCHEMA.id_of)
        rng.shuffle(values)
    selected, selected_families = [], set(excluded_families)
    for index in range(count):
        language = LANGUAGES[index % len(LANGUAGES)]
        while pool[language] and SCHEMA.family_of(pool[language][-1]) in selected_families:
            pool[language].pop()
        if not pool[language]:
            raise ValueError(f"Insufficient disjoint source documents in {language}")
        source = pool[language].pop()
        selected.append(dict(source, source_index=index + 1))
        selected_families.add(SCHEMA.family_of(source))
    return selected


def prepare(args: argparse.Namespace) -> Path:
    if not 1 <= args.round <= 5:
        raise ValueError("The user authorized at most five rounds")
    directory = args.output / f"round_{args.round:02d}"
    if (directory / "manifest.json").exists():
        verify_snapshot(directory)
        print(f"Already prepared; immutable snapshot retained: {directory}", flush=True)
        return directory
    if directory.exists() and any(directory.iterdir()):
        raise ValueError(f"Incomplete preparation exists; inspect before repairing: {directory}")
    if args.round > 1:
        previous = args.output / f"round_{args.round - 1:02d}"
        if not (previous / "manifest.json").exists():
            raise ValueError("Prepare rounds sequentially; the preceding round is missing")
        if (not (previous / "run_state.json").exists()
                or read_json(previous / "run_state.json")["status"] != "complete"):
            raise ValueError("Execute the preceding round before preparing another round")
    contract = args.contract.read_bytes()
    fixed_contract = args.output / "evaluation_contract.md"
    if fixed_contract.exists() and fixed_contract.read_bytes() != contract:
        raise ValueError("Independent evaluation contract must stay fixed across rounds")
    excluded_ids, excluded_families = set(), set()
    exclusions = []
    for path in sorted(QAC.glob("*review_with_source.csv")):
        for row in read_csv(path):
            excluded_ids.add(row.get("source_document_id") or row["corpus_id"])
            excluded_families.add(row["publication_number"])
        exclusions.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())})
    for path in sorted(args.output.glob("round_*/sources.json")):
        for row in read_json(path):
            excluded_ids.add(SCHEMA.id_of(row))
            excluded_families.add(SCHEMA.family_of(row))
    sources = sample_sources(read_csv(args.corpus), excluded_ids=excluded_ids,
                             excluded_families=excluded_families,
                             count=args.documents, seed=args.seed + args.round - 1)
    directory.mkdir(parents=True)
    fixed_contract.parent.mkdir(parents=True, exist_ok=True)
    if not fixed_contract.exists():
        fixed_contract.write_bytes(contract)
    (directory / "evaluation_contract.md").write_bytes(contract)
    prompt_files = ["decider/jev_eligibility.json", "verifiers/faithfulness_batch.txt"]
    prompt_files += [f"verifiers/{mode}_batch.txt" for mode in MODES]
    prompt_files += [f"generation/{mode}/{language}.txt" for mode in MODES for language in LANGUAGES]
    hashes = {}
    for name in prompt_files:
        target = directory / "prompts" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROMPTS / name, target)
        hashes[name] = digest(target.read_bytes())
    write_json(directory / "sources.json", sources)
    with BASELINE.open(encoding="utf-8", newline="") as handle:
        review_fields = next(csv.reader(handle))
    write_json(directory / "review_fields.json", review_fields)
    write_json(directory / "manifest.json", {
        "schema_version": 1, "created_at": now(), "round": args.round,
        "document_cap": 50, "round_cap": 5, "document_count": len(sources),
        "seed": args.seed + args.round - 1, "models": MODEL_CONFIG,
        "source_selection": "fixed language-balanced random sample; no topups or score filtering",
        "language_counts": dict(Counter(SCHEMA.language_of(row) for row in sources)),
        "excluded_prior_document_count": len(excluded_ids),
        "excluded_prior_family_count": len(excluded_families), "baseline_exclusions": exclusions,
        "sources_sha256": digest((directory / "sources.json").read_bytes()),
        "corpus": str(args.corpus), "corpus_sha256": digest(args.corpus.read_bytes()),
        "prompt_sha256": hashes, "contract_sha256": digest(contract),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "ranking": "all canonical candidates retained; best-per-document is supplementary only",
    })
    export(directory)
    print(f"Prepared {len(sources)} fixed sources and {len(hashes)} prompt files: {directory}", flush=True)
    return directory


def verify_snapshot(directory: Path) -> dict:
    manifest = read_json(directory / "manifest.json")
    if not 1 <= manifest["round"] <= 5 or not 1 <= manifest["document_count"] <= 50:
        raise ValueError("Manifest violates authorized document/round limits")
    if manifest["models"] != MODEL_CONFIG:
        raise ValueError("Frozen model settings differ from this runner's model settings")
    sources_path = directory / "sources.json"
    if digest(sources_path.read_bytes()) != manifest["sources_sha256"]:
        raise ValueError("Frozen source sample changed")
    sources = read_json(sources_path)
    if len(sources) != manifest["document_count"] or len({SCHEMA.id_of(s) for s in sources}) != len(sources):
        raise ValueError("Source count or uniqueness mismatch")
    for name, expected in manifest["prompt_sha256"].items():
        if digest((directory / "prompts" / name).read_bytes()) != expected:
            raise ValueError(f"Frozen prompt changed: {name}")
    if digest((directory / "evaluation_contract.md").read_bytes()) != manifest["contract_sha256"]:
        raise ValueError("Frozen evaluation contract changed")
    return manifest


def stage_directory(directory: Path, source: dict, stage: str) -> Path:
    return directory / "documents" / f"{source['source_index']:03d}" / stage


def stage_result(directory: Path, source: dict, stage: str) -> Any | None:
    path = stage_directory(directory, source, stage) / "state.json"
    if path.exists():
        state = read_json(path)
        if state["status"] == "complete":
            return state["result"]
    return None


class PendingCallError(RuntimeError):
    """A process ended while the provider could have accepted its request."""


class OfflineReplayError(RuntimeError):
    """A replay is missing a completed response or its original inputs differ."""


class CallRecorder:
    """Record every provider attempt, replaying a saved response after interruption."""

    def __init__(self, path: Path, client: Any, *, retry_uncertain: bool = False):
        self.path, self.client, self.index = path, client, 0
        self.retry_uncertain = retry_uncertain
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def call(self, request: dict, invoke) -> dict:
        path = self.path / f"call_{self.index:02d}.json"
        self.index += 1
        request_hash = digest(json.dumps(request, sort_keys=True, ensure_ascii=False).encode())
        if path.exists():
            saved = read_json(path)
            if saved["request_sha256"] != request_hash:
                raise ValueError("Cannot resume a saved model call with changed inputs")
            if saved["status"] == "complete":
                return saved["response"]
            if saved["status"] == "started" and not self.retry_uncertain:
                raise PendingCallError(f"Uncertain provider outcome in {path}; inspect before --retry-uncertain")
            # Keep incomplete attempts in the ledger even when explicitly retried.
            path = path.with_name(f"{path.stem}_retry_{time.time_ns()}.json")
        record = {"status": "started", "started_at": now(), "request_sha256": request_hash,
                  "request": request}
        write_json(path, record)
        try:
            response = invoke()
        except Exception as exc:
            write_json(path, dict(record, status="error", finished_at=now(),
                                  error_type=type(exc).__name__, error=str(exc)))
            raise
        write_json(path, dict(record, status="complete", finished_at=now(), response=response))
        return response

    def create(self, **request):
        response = self.call(request, lambda: self.client.chat.completions.create(**request).model_dump())
        # The upstream SDK already accepted this response. Revalidating its full
        # OpenRouter envelope against OpenAI-only enums rejects provider metadata
        # such as service_tier="provisioned". Our pipeline consumes only content;
        # expose it verbatim while retaining the entire raw envelope on disk.
        return SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(content=choice["message"].get("content")))
            for choice in response["choices"]
        ], model_dump=lambda: response)

    def decisions(self, request):
        return self.call(request, lambda: llm.decisions(request))


class OfflineRecorder(CallRecorder):
    """Read saved successful responses; never invoke a client or write call logs."""

    def call(self, request: dict, invoke) -> dict:
        path = self.path / f"call_{self.index:02d}.json"
        self.index += 1
        if not path.exists():
            raise OfflineReplayError(f"No recorded call at {path}")
        saved = read_json(path)
        expected = digest(json.dumps(request, sort_keys=True, ensure_ascii=False).encode())
        if saved["request_sha256"] != expected:
            raise OfflineReplayError("Recorded request does not match the frozen prompt and canonical candidates")
        if saved["status"] != "complete":
            raise OfflineReplayError(f"Recorded provider call is {saved['status']}, not complete")
        return saved["response"]


def replay_result(directory: Path, source: dict, stage: str, attempt: Path) -> Any:
    """Apply the ordinary content parsers to a saved, identical model request."""
    recorder = OfflineRecorder(attempt, None)
    decision = stage_result(directory, source, "routing")
    mode, language, packet = decision["mode"], SCHEMA.language_of(source), source_packet(source)
    grader = GraderConfig(model=MODEL_CONFIG["verifier_model"],
                          reasoning_effort=MODEL_CONFIG["verifier_reasoning_effort"], use_thinking=False)
    if stage == "generation":
        config = GenerationConfig(generation_model=MODEL_CONFIG["generation_model"], grader=grader,
                                  generation_reasoning_effort=MODEL_CONFIG["generation_reasoning_effort"],
                                  candidates=MODEL_CONFIG["candidates_per_document"], retries=1,
                                  candidate_parser=parse_candidates)
        prompt = (directory / "prompts/generation" / mode / f"{language}.txt").read_text().strip()
        return generate_candidates(recorder, config, prompt, packet, mode)
    candidates = stage_result(directory, source, "generation")
    if not candidates:
        raise OfflineReplayError("No canonical candidates exist for this verifier request")
    candidates = [dict(row, mode=mode, question_language=language,
                       candidate_id=f"s{source['source_index']:03d}c{index + 1}")
                  for index, row in enumerate(candidates)]
    if stage == "faithfulness":
        prompt = (directory / "prompts/verifiers/faithfulness_batch.txt").read_text().strip()
        return grade_faithfulness(recorder, grader, prompt, packet, candidates, strict=True)
    if stage == "quality":
        prompt = (directory / "prompts/verifiers" / f"{mode}_batch.txt").read_text().strip()
        return grade_quality(recorder, grader, prompt, packet, candidates, mode, strict=True)
    raise ValueError(f"Stage cannot have the ChatCompletion envelope bug: {stage}")


def is_transport_validation_failure(validation: dict) -> bool:
    """Scope recovery to the observed adapter defect, never content refusals."""
    error = validation.get("error", "")
    return (validation.get("error_type") == "ValidationError"
            and "validation error for ChatCompletion" in error
            and "service_tier" in error and "input_value='provisioned'" in error)


def recover_transport(directory: Path) -> dict:
    """Recover adapter failures from the earliest valid saved response, offline."""
    verify_snapshot(directory)
    if (not (directory / "run_state.json").exists()
            or read_json(directory / "run_state.json")["status"] != "complete"):
        raise ValueError("Offline recovery requires a terminal original run")
    recovery_version = "content_view_v1"
    records = []
    for source in read_json(directory / "sources.json"):
        generation_changed = False
        for stage in ("generation", "faithfulness", "quality"):
            path = stage_directory(directory, source, stage)
            state_path = path / "state.json"
            if not state_path.exists():
                continue
            prior = read_json(state_path)
            if prior.get("transport_recovery_version") == recovery_version:
                continue
            affected = any(is_transport_validation_failure(read_json(p))
                           for p in path.glob("attempt_*/validation.json"))
            if not affected and not generation_changed:
                continue
            recovery_path = path / "recovery" / recovery_version
            recovery_path.mkdir(parents=True, exist_ok=True)
            write_json(recovery_path / "prior_state.json", prior)
            attempts = []
            result, chosen_attempt = None, None
            for attempt in sorted(path.glob("attempt_*"), key=lambda p: int(p.name.split("_")[1])):
                try:
                    result = replay_result(directory, source, stage, attempt)
                except Exception as exc:  # noqa: BLE001 -- preserve content/parser errors without retrying the model
                    attempts.append({"attempt": attempt.name, "status": "error",
                                     "error_type": type(exc).__name__, "error": str(exc)})
                else:
                    chosen_attempt = int(attempt.name.split("_")[1])
                    attempts.append({"attempt": attempt.name, "status": "complete"})
                    break
            write_json(recovery_path / "replay_attempts.json", attempts)
            record = {"source_index": source["source_index"], "stage": stage,
                      "prior_attempt": prior.get("attempt"), "chosen_attempt": chosen_attempt,
                      "reason": "provider_envelope_validation" if affected else "generation_inputs_changed",
                      "paid_calls": 0, "replay_attempts": attempts}
            if chosen_attempt is not None:
                state = {"status": "complete", "attempt": chosen_attempt, "result": result,
                         "finished_at": now(), "transport_recovery_version": recovery_version,
                         "recovery_prior_state": str((recovery_path / "prior_state.json").relative_to(directory))}
                write_json(state_path, state)
                record["status"] = "recovered"
                if stage == "generation":
                    generation_changed = result != prior.get("result")
            else:
                # Original parse/refusal errors remain visible, with no fabricated grade.
                write_json(state_path, {"status": "error", "attempt": prior.get("attempt", 0),
                           "finished_at": now(), "error_type": "OfflineReplayError",
                           "error": "No saved response passed unchanged parsers for canonical inputs",
                           "transport_recovery_version": recovery_version,
                           "recovery_prior_state": str((recovery_path / "prior_state.json").relative_to(directory))})
                record["status"] = "unresolved"
            records.append(record)
    report_path = directory / "transport_recovery.json"
    if records or not report_path.exists():
        write_json(report_path, {"recovery_version": recovery_version, "completed_at": now(),
                   "runner_sha256": digest(Path(__file__).read_bytes()), "paid_calls": 0,
                   "policy": "Earliest saved response passing unchanged content parsers; no score selection",
                   "records": records})
    export(directory)
    report = read_json(report_path)
    print(json.dumps({"recovered_stages": sum(r["status"] == "recovered" for r in report["records"]),
                      "unresolved_stages": sum(r["status"] == "unresolved" for r in report["records"]),
                      "paid_calls": 0}, indent=2), flush=True)
    return report


def execute_stage(directory: Path, source: dict, stage: str, callback, client: Any,
                  *, retry_errors: bool, retry_uncertain: bool) -> Any | None:
    path = stage_directory(directory, source, stage)
    state_path = path / "state.json"
    state = read_json(state_path) if state_path.exists() else {}
    if state.get("status") == "complete":
        return state["result"]
    if state.get("status") == "error" and not retry_errors:
        return None
    previous_attempt = state.get("attempt", 0)
    first_attempt = previous_attempt if state.get("status") == "running" else previous_attempt + 1
    for attempt in range(first_attempt, first_attempt + MODEL_CONFIG["stage_attempt_limit"]):
        write_json(state_path, {"status": "running", "attempt": attempt, "started_at": now()})
        recorder = CallRecorder(path / f"attempt_{attempt:02d}", client,
                                retry_uncertain=retry_uncertain)
        try:
            result = callback(recorder)
        except PendingCallError as exc:
            # Keep running state so a later intentional resume can replay its response.
            print(f"Source {source['source_index']:02d} {stage}: {exc}", flush=True)
            return None
        except Exception as exc:  # noqa: BLE001 -- provider/parser failures are stage audit records
            failure = {"status": "error", "attempt": attempt, "finished_at": now(),
                       "error_type": type(exc).__name__, "error": str(exc)}
            write_json(state_path, failure)
            write_json(path / f"attempt_{attempt:02d}" / "validation.json", failure)
            print(f"Source {source['source_index']:02d} {stage} attempt {attempt}: {type(exc).__name__}",
                  flush=True)
            if attempt + 1 < first_attempt + MODEL_CONFIG["stage_attempt_limit"]:
                time.sleep(min(2 ** (attempt - first_attempt), 4))
        else:
            success = {"status": "complete", "attempt": attempt,
                       "finished_at": now(), "result": result}
            write_json(state_path, success)
            write_json(path / f"attempt_{attempt:02d}" / "validation.json", success)
            return result
    return None


def run(directory: Path, args: argparse.Namespace) -> None:
    manifest = verify_snapshot(directory)
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(ROOT / ".env")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    # Disable invisible SDK retries: every provider attempt belongs in the ledger.
    client = OpenAI(api_key=key, base_url=llm.OPENROUTER_BASE_URL, max_retries=0, timeout=180)
    write_json(directory / "run_state.json", {"status": "running", "started_at": now()})
    sources = read_json(directory / "sources.json")
    eligibility_template = read_json(directory / "prompts/decider/jev_eligibility.json")
    policy = eligibility_template.pop("routing_policy", {"probability_threshold": 0.5})
    threshold = policy["probability_threshold"]
    stage_options = {"retry_errors": args.retry_errors, "retry_uncertain": args.retry_uncertain}

    def screen(source):
        request = dict(eligibility_template, model=decider.JEV_MODEL, state=source_packet(source))
        result = execute_stage(directory, source, "decider",
                               lambda recorder: decider.parse_eligibility(
                                   recorder.decisions(request), threshold=threshold),
                               client, **stage_options)
        print(f"Screened {source['source_index']:02d}/{len(sources)}: "
              f"{'ok' if result is not None else 'error'}", flush=True)

    parallel(sources, screen, args.workers)
    # Routing is deterministic in source order and independent of provider timing.
    counts, assignments = Counter(), []
    for source in sources:
        eligibility = stage_result(directory, source, "decider")
        if eligibility is None:
            continue
        identity = json.dumps(["gp", SCHEMA.family_of(source), SCHEMA.language_of(source),
                               SCHEMA.id_of(source)], ensure_ascii=False)
        decision = decider.choose(eligibility, counts, decider.resolve_weights(),
                                  seed=manifest["seed"], identity=identity)
        decision.update(source_index=source["source_index"], document_id=SCHEMA.id_of(source))
        saved_path = stage_directory(directory, source, "routing") / "state.json"
        if saved_path.exists():
            # An earlier decider failure can recover without reassigning other documents.
            decision = read_json(saved_path)["result"]
        else:
            write_json(saved_path, {"status": "complete", "result": decision})
        if decision["mode"] != "skip":
            counts[decision["mode"]] += 1
        assignments.append(decision)
    write_json(directory / "eligibility.json", {"prompt": eligibility_template,
               "policy": policy, "assignments": assignments})
    export(directory)

    grader = GraderConfig(model=MODEL_CONFIG["verifier_model"],
                          reasoning_effort=MODEL_CONFIG["verifier_reasoning_effort"], use_thinking=False)
    generation = GenerationConfig(
        generation_model=MODEL_CONFIG["generation_model"], grader=grader,
        generation_reasoning_effort=MODEL_CONFIG["generation_reasoning_effort"],
        candidates=MODEL_CONFIG["candidates_per_document"], retries=1,
        candidate_parser=parse_candidates,
    )

    def generate_and_grade(source):
        decision = stage_result(directory, source, "routing")
        if decision is None or decision["mode"] == "skip":
            return
        mode, language, packet = decision["mode"], SCHEMA.language_of(source), source_packet(source)
        prompt = (directory / "prompts/generation" / mode / f"{language}.txt").read_text().strip()
        candidates = execute_stage(
            directory, source, "generation",
            lambda recorder: generate_candidates(recorder, generation, prompt, packet, mode),
            client, **stage_options,
        )
        if candidates:
            candidates = [dict(row, mode=mode, question_language=language,
                               candidate_id=f"s{source['source_index']:03d}c{index + 1}")
                          for index, row in enumerate(candidates)]
            faith_prompt = (directory / "prompts/verifiers/faithfulness_batch.txt").read_text().strip()
            quality_prompt = (directory / "prompts/verifiers" / f"{mode}_batch.txt").read_text().strip()
            execute_stage(directory, source, "faithfulness",
                          lambda recorder: grade_faithfulness(recorder, grader, faith_prompt,
                                                               packet, candidates, strict=True),
                          client, **stage_options)
            execute_stage(directory, source, "quality",
                          lambda recorder: grade_quality(recorder, grader, quality_prompt,
                                                         packet, candidates, mode, strict=True),
                          client, **stage_options)
        print(f"Generated/graded {source['source_index']:02d}/{len(sources)}: "
              f"{len(candidates) if candidates is not None else 'error'} candidates", flush=True)

    parallel(sources, generate_and_grade, args.workers)
    export(directory)
    write_json(directory / "run_state.json", {"status": "complete", "finished_at": now(),
               "meaning": "Every fixed source has been attempted; errors and skips are retained."})
    summary = read_json(directory / "summary.json")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


def parallel(items, callback, workers: int) -> None:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(callback, item) for item in items]
        for future in as_completed(futures):
            future.result()


def source_columns(source: dict) -> dict:
    return {"source_index": source["source_index"], "source_document_id": SCHEMA.id_of(source),
            "publication_number": SCHEMA.family_of(source),
            "source_document_language": SCHEMA.language_of(source),
            "source_document_title": source.get("title", ""),
            "source_document_abstract": source.get("abstract", ""),
            "source_document_first_claim": source.get("first_claim", ""),
            "source_document_text": SCHEMA.text_of(source)}


def export(directory: Path) -> None:
    """Export partial runs too: failures and abstentions remain visible."""
    manifest = verify_snapshot(directory)
    sources = read_json(directory / "sources.json")
    rows, audit, attempts, errors, calls = [], [], [], [], []
    for source in sources:
        language, source_id = SCHEMA.language_of(source), SCHEMA.id_of(source)
        decision = stage_result(directory, source, "routing")
        eligibility = stage_result(directory, source, "decider")
        candidates = stage_result(directory, source, "generation")
        faith = stage_result(directory, source, "faithfulness")
        quality = stage_result(directory, source, "quality")
        stages = {}
        for stage in ("decider", "generation", "faithfulness", "quality"):
            path = stage_directory(directory, source, stage) / "state.json"
            stages[stage] = read_json(path)["status"] if path.exists() else "not_started"
            if path.exists() and stages[stage] != "complete":
                errors.append(dict(source_index=source["source_index"], source_document_id=source_id,
                                   stage=stage, **read_json(path)))
        audit.append({**source_columns(source), "pipeline_stage_statuses": stages,
                      "decider_probabilities_yes": eligibility["probabilities_yes"] if eligibility else {},
                      "decider_threshold": eligibility["threshold"] if eligibility else "",
                      "decider_eligible_modes": eligibility["selected_modes"] if eligibility else [],
                      "decider_rejected_modes": [m for m in MODES if eligibility and m not in eligibility["selected_modes"]],
                      "decider_selected_mode": decision["mode"] if decision else "",
                      "generation_candidate_count": len(candidates) if candidates is not None else "",
                      "generator_abstained": candidates == []})
        if candidates is not None and decision is not None:
            source_rows = []
            for index, candidate in enumerate(candidates):
                row = {**source_columns(source), **candidate,
                       "corpus_id": source_id, "question_language": language,
                       "context_language": language, "context_languages": language,
                       "mode": decision["mode"], "question_mode": decision["mode"],
                       "strategy": 3, "strategy_name": "random_existing",
                       "candidate_id": f"s{source['source_index']:03d}c{index + 1}",
                       "candidate_original_index": index,
                       "generation_model": MODEL_CONFIG["generation_model"],
                       "verifier_model": MODEL_CONFIG["verifier_model"],
                       "decider_eligible_modes": decision["eligible_modes"],
                       "pipeline_stage_statuses": stages,
                       **decider.row_metadata(decision, manifest["prompt_sha256"]["decider/jev_eligibility.json"])}
                # Missing verifier output is not replaced with fabricated numerical grades.
                if faith is not None or quality is not None:
                    f = faith[index] if faith is not None else {"overall": None}
                    q = quality[index] if quality is not None else {"overall": None}
                    row.update(grade_columns(f, q, decision["mode"]))
                source_rows.append(row)
            ranked = sorted(source_rows, key=lambda r: (r.get("total_score") is not None,
                                                        r.get("total_score") or 0), reverse=True)
            for rank, row in enumerate(ranked, 1):
                row["candidate_rank"] = rank if row.get("total_score") is not None else ""
            # Primary export keeps generation order, avoiding score-order presentation bias.
            rows.extend(source_rows)
        for path in sorted((directory / "documents" / f"{source['source_index']:03d}").glob("*/attempt_*/call_*.json")):
            call = read_json(path)
            response = call.get("response") or {}
            calls.append({"source_index": source["source_index"], "stage": path.parts[-3],
                          "artifact": str(path.relative_to(directory)), "status": call["status"],
                          "started_at": call["started_at"], "finished_at": call.get("finished_at"),
                          "response_id": response.get("id"), "model": response.get("model"),
                          "usage": response.get("usage"), "error_type": call.get("error_type")})
            if path.parts[-3] == "generation":
                raw = ((response.get("choices") or [{}])[0].get("message") or {}).get("content")
                attempts.append({"source_index": source["source_index"], "source_document_id": source_id,
                                 "mode": decision["mode"] if decision else "", "artifact": str(path.relative_to(directory)),
                                 "status": call["status"], "raw_generator_output": raw})
    fields = read_json(directory / "review_fields.json")
    fields += ["source_index", "candidate_original_index", "pipeline_stage_statuses"]
    write_csv(directory / "review_with_source.csv", rows, fields)
    write_csv(directory / "best_per_document_with_source.csv", select_best(rows, SCHEMA), fields)
    blinded_fields = ["candidate_id", "source_index", "source_document_id", "publication_number",
                      "question_language", "mode", "question", "answer", *CANDIDATE_METADATA_FIELDS,
                      "source_document_language", "source_document_text"]
    blinded_fields = list(dict.fromkeys(blinded_fields))
    write_csv(directory / "blinded_candidates.csv", rows, blinded_fields)
    source_rows = [source_columns(source) for source in sources]
    write_csv(directory / "sources_only.csv", source_rows, list(source_rows[0]))
    audit_fields = list(audit[0]) if audit else []
    write_csv(directory / "sources_and_decisions.csv", audit, audit_fields)
    write_json(directory / "sources_and_decisions.json", audit)
    write_json(directory / "generation_attempts.json", attempts)
    validation_failures = []
    for path in sorted((directory / "documents").glob("*/*/attempt_*/validation.json")):
        validation = read_json(path)
        if validation["status"] == "error":
            validation_failures.append({"artifact": str(path.relative_to(directory)), **validation})
    write_json(directory / "validation_failures.json", validation_failures)
    write_json(directory / "errors.json", errors)
    write_json(directory / "call_ledger.json", calls)
    write_json(directory / "summary.json", {
        "round": manifest["round"], "prepared_sources": len(sources),
        "screened_sources": sum(stage_result(directory, s, "decider") is not None for s in sources),
        "decider_skips": sum(row["decider_selected_mode"] == "skip" for row in audit),
        "generator_abstentions": sum(row["generator_abstained"] for row in audit),
        "generated_sources": len({row["source_document_id"] for row in rows}),
        "canonical_candidate_count": len(rows), "best_per_document_count": len(select_best(rows, SCHEMA)),
        "source_language_counts": dict(Counter(SCHEMA.language_of(s) for s in sources)),
        "candidate_mode_counts": dict(Counter(row["mode"] for row in rows)),
        "stage_error_or_pending_count": len(errors), "provider_attempts": len(calls),
        "provider_completed_responses": sum(c["status"] == "complete" for c in calls),
        "provider_pending_outcomes": sum(c["status"] == "started" for c in calls),
        "provider_reported_cost": sum((c.get("usage") or {}).get("cost") or 0 for c in calls),
        "cost_note": "Sum of supplied provider costs only; missing costs and errors can still be billable.",
        "all_candidates_preserved": True, "score_filtering": False, "topups": False,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", type=int, required=True, choices=range(1, 6))
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--recover-transport", action="store_true",
                        help="Offline recovery of saved responses rejected by the provider-envelope adapter")
    parser.add_argument("--documents", type=int, default=50)
    parser.add_argument("--seed", type=int, default=2026101401)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--contract", type=Path, default=Path(__file__).with_name("evaluation_contract.md"))
    parser.add_argument("--retry-errors", action="store_true",
                        help="Retry failed stages; already completed stages remain cached")
    parser.add_argument("--retry-uncertain", action="store_true",
                        help="Explicitly allow a retry when a previous provider outcome is unknown")
    args = parser.parse_args()
    if not any((args.prepare, args.run, args.export, args.recover_transport)):
        parser.error("Specify --prepare, --run, --export, or --recover-transport")
    if args.recover_transport and (args.prepare or args.run):
        parser.error("--recover-transport is offline only; do not combine it with --prepare or --run")
    if not 1 <= args.workers <= 20:
        parser.error("workers must be between 1 and 20")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    # One process owns preparation/routing/export; source calls within it may run concurrently.
    with (args.output / ".runner.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Another round runner is active; resume its process rather than duplicating it") from exc
        directory = args.output / f"round_{args.round:02d}"
        if args.prepare:
            prepare(args)
        if args.recover_transport:
            recover_transport(directory)
        if args.run:
            run(directory, args)
        elif args.export:
            export(directory)


if __name__ == "__main__":
    main()
