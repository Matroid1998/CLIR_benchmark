#!/usr/bin/env python3
"""Create and validate a self-contained evaluator packet without optimizer history."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "reports/prompt_experiments/chemistry_loop_20261014"
MODEL = "gpt-6-astra"
REASONING_EFFORT = "xhigh"
MODES = frozenset(("lookup", "process_retrieval", "conceptual", "constraint_search",
                   "comparison", "assertion_verification", "source_finding"))
INPUT_MAPPING = {
    "evaluation_contract.md": "evaluation_contract.md",
    "sources_only.csv": "sources.csv",
    "blinded_candidates.csv": "blinded_candidates.csv",
    "review_with_source.csv": "review_with_source.csv",
    "sources_and_decisions.json": "routing_audit.json",
}
SOURCE_FIELDS = frozenset((
    "source_index", "source_document_id", "publication_number", "source_document_language",
    "source_document_title", "source_document_abstract", "source_document_first_claim",
    "source_document_text",
))
BLINDED_FIELDS = frozenset((
    "candidate_id", "source_index", "source_document_id", "publication_number", "question_language",
    "mode", "question", "answer", "question_type", "framing", "anchor", "evidence",
    "evidence_language", "answer_is_translation", "process_kind", "process_start", "process_goal",
    "relationship_type", "solution_kind", "objective", "constraints", "comparison_entities",
    "comparison_aspect", "assertion", "assertion_status", "source_identifier",
    "source_document_language", "source_document_text",
))
SUMMARY_FIELDS = (
    "prepared_sources", "screened_sources", "decider_skips", "generator_abstentions",
    "generated_sources", "canonical_candidate_count", "best_per_document_count",
    "source_language_counts", "candidate_mode_counts", "stage_error_or_pending_count",
    "provider_attempts", "provider_completed_responses", "provider_pending_outcomes",
    "provider_reported_cost", "cost_note", "all_candidates_preserved", "score_filtering", "topups",
)
OUTPUT_FILES = ("evaluation.json", "independent_candidates.csv", "independent_eligibility.json",
                "evaluation_task.txt")
CANDIDATE_REVIEW_FIELDS = frozenset((
    "candidate_id", "source_document_id", "mode", "readiness", "generator_rating_10",
    "source_support", "mode_fit", "metadata_ok", "issue_details", "suggested_repair",
))


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, content: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if not fields or len(fields) != len(set(fields)):
            raise ValueError(f"Missing or duplicate CSV headers: {path.name}")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f"Malformed CSV record: {path.name}")
        return fields, rows


def round_directory(round_number: int) -> Path:
    if type(round_number) is not int or not 1 <= round_number <= 5:
        raise ValueError("Authorized run limits exceeded")
    return BASE / f"round_{round_number:02d}"


def indexed(rows: list[dict], field: str, label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        identity = row.get(field)
        if not isinstance(identity, str) or not identity.strip() or identity in result:
            raise ValueError(f"Missing or duplicate {label} identity: {identity!r}")
        result[identity] = row
    return result


def packet_inventory(packet: Path, expected_count: int | None = None) -> tuple[dict, dict]:
    source_fields, source_rows = read_csv(packet / "sources.csv")
    if (not set(source_fields) <= SOURCE_FIELDS
            or not {"source_document_id", "source_document_text", "source_document_language"} <= set(source_fields)):
        raise ValueError("Source-only packet contains unexpected fields")
    sources = indexed(source_rows, "source_document_id", "source")
    if not 1 <= len(sources) <= 50 or (expected_count is not None and len(sources) != expected_count):
        raise ValueError("Source packet count does not match the capped manifest")
    blinded_fields, blinded_rows = read_csv(packet / "blinded_candidates.csv")
    if (not set(blinded_fields) <= BLINDED_FIELDS
            or not {"candidate_id", "source_document_id", "mode", "question", "answer",
                    "evidence", "source_document_text"} <= set(blinded_fields)):
        raise ValueError("Blinded candidate packet contains unexpected fields or model assessments")
    candidates = indexed(blinded_rows, "candidate_id", "candidate")
    if any(count > 3 for count in Counter(row["source_document_id"] for row in blinded_rows).values()):
        raise ValueError("Candidate packet exceeds three canonical candidates per source")
    for row in candidates.values():
        source = sources.get(row.get("source_document_id"))
        if source is None or row.get("mode") not in MODES:
            raise ValueError("Candidate has an unknown source or mode")
        if row.get("source_document_text") != source.get("source_document_text"):
            raise ValueError("Candidate source text differs from the source-only packet")
    _, graded_rows = read_csv(packet / "review_with_source.csv")
    graded = indexed(graded_rows, "candidate_id", "graded candidate")
    if set(graded) != set(candidates):
        raise ValueError("Blinded and scored packets do not contain the same candidates")
    for identity, row in candidates.items():
        if any(graded[identity].get(field) != value for field, value in row.items()):
            raise ValueError("Blinded candidate content differs from the scored packet")
    routing = load_json(packet / "routing_audit.json")
    if not isinstance(routing, list) or set(indexed(routing, "source_document_id", "routing source")) != set(sources):
        raise ValueError("Routing audit must cover every source exactly once")
    return sources, candidates


def verify_inputs(directory: Path, invocation: dict) -> tuple[Path, dict, dict]:
    if (invocation.get("model") != MODEL or invocation.get("reasoning_effort") != REASONING_EFFORT
            or invocation.get("fork_turns") != "none"):
        raise ValueError("Evaluator invocation must use isolated gpt-6-astra with xhigh reasoning")
    packet = Path(invocation["packet_dir"])
    expected_files = set(INPUT_MAPPING.values()) | {"run_summary.json"}
    if set(invocation["input_sha256"]) != expected_files:
        raise ValueError("Evaluator input hash inventory is incomplete or unexpected")
    for name, expected in invocation["input_sha256"].items():
        if sha256((packet / name).read_bytes()) != expected:
            raise ValueError(f"Evaluator input changed: {name}")
    if sha256((packet / "evaluation_task.txt").read_bytes()) != invocation["task_sha256"]:
        raise ValueError("Evaluator task changed")
    # Older packets pin copied inputs but not the derived summary's source files.
    # Keep them collectable, while checking every directly copied source file.
    for source, target in INPUT_MAPPING.items():
        if sha256((directory / source).read_bytes()) != invocation["input_sha256"][target]:
            raise ValueError(f"Round input changed after evaluator preparation: {source}")
    for name, expected in invocation.get("round_input_sha256", {}).items():
        if sha256((directory / name).read_bytes()) != expected:
            raise ValueError(f"Round input changed after evaluator preparation: {name}")
    manifest = load_json(directory / "manifest.json")
    if type(manifest["document_count"]) is not int or not 1 <= manifest["document_count"] <= 50:
        raise ValueError("Authorized run limits exceeded")
    sources, candidates = packet_inventory(packet, manifest["document_count"])
    summary = load_json(packet / "run_summary.json")
    if (summary["prepared_sources"] != len(sources)
            or summary["canonical_candidate_count"] != len(candidates)):
        raise ValueError("Summary coverage differs from the packet")
    return packet, sources, candidates


def prepare(round_number: int) -> tuple[Path, str]:
    directory = round_directory(round_number)
    state = load_json(directory / "run_state.json")
    if state["status"] != "complete":
        raise ValueError("Wait for the current run to finish before preparing an evaluator packet")
    manifest = load_json(directory / "manifest.json")
    count = manifest["document_count"]
    if (type(count) is not int or not 1 <= count <= 50
            or manifest.get("round", round_number) != round_number):
        raise ValueError("Authorized run limits exceeded or manifest round mismatched")
    record = directory / "evaluator_invocation.json"
    if record.exists():
        saved = load_json(record)
        packet, _, _ = verify_inputs(directory, saved)
        return packet, (packet / "evaluation_task.txt").read_text(encoding="utf-8")
    packet = Path(tempfile.mkdtemp(prefix="chemistry_evaluation_"))
    hashes, source_hashes = {}, {}
    for source, target in INPUT_MAPPING.items():
        content = (directory / source).read_bytes()
        (packet / target).write_bytes(content)
        hashes[target] = source_hashes[source] = sha256(content)
    original_summary = load_json(directory / "summary.json")
    # An allowlist keeps later optimizer notes, targets, and earlier ratings out.
    summary = {key: original_summary[key] for key in SUMMARY_FIELDS if key in original_summary}
    summary["technical_errors"] = [
        {key: value.replace(str(directory), "[round artifacts]") if isinstance(value, str) else value
         for key, value in error.items()
         if key in ("source_index", "source_document_id", "stage", "status", "attempt", "error_type", "error")}
        for error in load_json(directory / "errors.json")
    ]
    for name in ("summary.json", "errors.json", "manifest.json", "run_state.json"):
        source_hashes[name] = sha256((directory / name).read_bytes())
    refusals = []
    for path in sorted((directory / "documents").glob("*/generation/attempt_*/call_*.json")):
        source_hashes[str(path.relative_to(directory))] = sha256(path.read_bytes())
        call = load_json(path)
        for choice in (call.get("response") or {}).get("choices", []):
            if choice.get("finish_reason") == "content_filter" or choice.get("native_finish_reason") == "refusal":
                refusals.append({"source_index": int(path.parts[-4]), "stage": "generation",
                                 "finish_reason": choice.get("finish_reason"),
                                 "native_finish_reason": choice.get("native_finish_reason")})
    summary["provider_refusal_attempts"] = refusals
    write_json(packet / "run_summary.json", summary)
    hashes["run_summary.json"] = sha256((packet / "run_summary.json").read_bytes())
    template = Path(__file__).with_name("evaluator_task.txt").read_text(encoding="utf-8")
    task = template.replace("{packet_dir}", str(packet))
    (packet / "evaluation_task.txt").write_text(task, encoding="utf-8")
    invocation = {"packet_dir": str(packet), "model": MODEL, "reasoning_effort": REASONING_EFFORT,
                  "fork_turns": "none", "task_sha256": sha256(task.encode()),
                  "input_sha256": hashes, "round_input_sha256": source_hashes, "status": "prepared"}
    verify_inputs(directory, invocation)
    write_json(record, invocation)
    return packet, task


def valid_rating(value, label: str) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not 0 <= value <= 10):
        raise ValueError(f"Invalid independent rating: {label}")


def collect(round_number: int) -> dict:
    directory = round_directory(round_number)
    record = directory / "evaluator_invocation.json"
    invocation = load_json(record)
    packet, expected_sources, expected_candidates = verify_inputs(directory, invocation)
    evaluation = load_json(packet / "evaluation.json")
    ratings = evaluation["ratings"]
    for component in ("generator", "verifier", "decider"):
        valid_rating(ratings[component], component)
    eligibility = load_json(packet / "independent_eligibility.json")
    if (not isinstance(eligibility, list)
            or set(indexed(eligibility, "source_document_id", "independent source")) != set(expected_sources)):
        raise ValueError("Independent eligibility review must cover every sampled source exactly once")
    for row in eligibility:
        for field in ("eligible_modes", "uncertain_modes"):
            modes = row.get(field)
            if (not isinstance(modes, list) or any(not isinstance(mode, str) for mode in modes)
                    or len(modes) != len(set(modes)) or not set(modes) <= MODES):
                raise ValueError(f"Invalid independent eligibility mode list: {field}")
        if set(row["eligible_modes"]) & set(row["uncertain_modes"]):
            raise ValueError("A mode cannot be both eligible and uncertain")
        if not row.get("notes"):
            raise ValueError("Independent eligibility review requires evidence-based notes")
    fields, reviewed_rows = read_csv(packet / "independent_candidates.csv")
    if not CANDIDATE_REVIEW_FIELDS <= set(fields):
        raise ValueError("Independent candidate review is missing required columns")
    reviewed = indexed(reviewed_rows, "candidate_id", "independent candidate")
    if set(reviewed) != set(expected_candidates):
        raise ValueError("Independent candidate review does not cover every candidate exactly once")
    readiness = Counter()
    for identity, row in reviewed.items():
        original = expected_candidates[identity]
        if row["source_document_id"] != original["source_document_id"] or row["mode"] != original["mode"]:
            raise ValueError("Independent candidate source or mode does not match its input")
        if row["readiness"] not in ("ready", "minor_edit", "major_issue"):
            raise ValueError("Invalid independent candidate readiness")
        readiness[row["readiness"]] += 1
        try:
            value = float(row["generator_rating_10"])
        except ValueError as exc:
            raise ValueError("Invalid independent candidate rating") from exc
        valid_rating(value, identity)
        if any(not row[field].strip() for field in ("source_support", "mode_fit", "metadata_ok")):
            raise ValueError("Independent candidate review is missing a judgment")
    summary = load_json(packet / "run_summary.json")
    expected_coverage = {"sources_reviewed": len(expected_sources),
                         "candidates_reviewed": len(expected_candidates),
                         "skips_reviewed": summary["decider_skips"]}
    for field, expected in expected_coverage.items():
        value = evaluation["coverage"][field]
        if type(value) is not int or value != expected:
            raise ValueError(f"Evaluator coverage does not match the packet: {field}")
    for key in ("ready", "minor_edit", "major_issue"):
        value = evaluation["generator"]["readiness_counts"][key]
        if type(value) is not int or value != readiness[key]:
            raise ValueError("Evaluator readiness counts do not match independent row judgments")
    output = directory / "evaluation"
    output.mkdir(exist_ok=True)
    for name in OUTPUT_FILES:
        shutil.copyfile(packet / name, output / name)
    invocation.update(status="completed", ratings=ratings,
                      output_sha256={name: sha256((packet / name).read_bytes()) for name in OUTPUT_FILES})
    write_json(record, invocation)
    return evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", type=int, choices=range(1, 6), required=True)
    parser.add_argument("--collect", action="store_true")
    args = parser.parse_args()
    if args.collect:
        result = collect(args.round)
        print(json.dumps({"ratings": result["ratings"], "coverage": result["coverage"]}, indent=2))
    else:
        path, _ = prepare(args.round)
        print(path)
