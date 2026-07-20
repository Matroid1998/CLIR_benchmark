"""The ``corpus`` command group: shape a raw ingest into a usable corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext


def register(subparsers: argparse._SubParsersAction, context: Optional[AppContext]) -> None:
    parser = subparsers.add_parser("corpus", help="Filter, deduplicate and inspect corpora")
    sub = parser.add_subparsers(dest="corpus_command", metavar="<subcommand>")

    filter_parser = sub.add_parser(
        "filter",
        help="Keep documents available in at least N languages",
        description=(
            "Writes the multilingual corpus: every document present in at least "
            "--min-langs of the target languages, with all of its language versions."
        ),
    )
    filter_parser.add_argument("--source", help="Source to filter (default: every source)")
    filter_parser.add_argument("--input", type=Path, help="Input corpus CSV (default: the source's)")
    filter_parser.add_argument("--output", type=Path, help="Output CSV (default: overwrite input)")
    filter_parser.add_argument("--langs", nargs="+", help="Target languages (default: source's)")
    filter_parser.add_argument("--min-langs", type=int, default=2, help="Minimum coverage (default: 2)")
    filter_parser.set_defaults(handler=_filter)

    dedup = sub.add_parser(
        "dedup",
        help="Drop documents from one source that already exist in another",
        description=(
            "Compares canonical document keys across two sources and rewrites the "
            "first source's corpus without the overlap. Keeps a .bak copy."
        ),
    )
    dedup.add_argument("--source", required=True, help="Source to prune")
    dedup.add_argument("--against", required=True, help="Source that wins on conflict")
    dedup.add_argument("--dry-run", action="store_true", help="Report the overlap without writing")
    dedup.set_defaults(handler=_dedup)

    stats = sub.add_parser("stats", help="Language and coverage statistics for a corpus")
    stats.add_argument("--source", help="Source to describe (default: every source)")
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(handler=_stats)


def _sources(context: AppContext, name: Optional[str]):
    return [context.domain.source(name)] if name else list(context.domain.sources)


def _filter(args: argparse.Namespace, context: AppContext) -> int:
    schema = context.schema
    for source in _sources(context, args.source):
        source_path = args.input or context.workspace.corpus_csv(source)
        if not source_path.exists():
            print(f"skip {source.name}: no corpus at {source_path}")
            continue
        languages = args.langs or list(source.languages)
        rows = corpus_io.read_rows(source_path)
        kept, summary = corpus_io.filter_multilingual(
            rows, schema, languages=languages, min_languages=args.min_langs
        )
        target = args.output or source_path
        corpus_io.write_rows(target, kept, schema.fields)
        print(f"{source.name}: {summary['rows_kept']} rows from {summary['families_kept']} documents -> {target}")
        print(f"  languages: {summary['per_language']}")
        print(f"  coverage:  {summary['coverage_distribution']}")
    return 0


def _dedup(args: argparse.Namespace, context: AppContext) -> int:
    schema = context.schema
    target_source = context.domain.source(args.source)
    against_source = context.domain.source(args.against)
    target_path = context.workspace.corpus_csv(target_source)
    against_path = context.workspace.corpus_csv(against_source)

    for path in (target_path, against_path):
        if not path.exists():
            raise FileNotFoundError(f"corpus not found: {path}")

    keep_keys = {schema.dedup_key(row) for row in corpus_io.iter_rows(against_path)}
    keep_keys.discard("")

    rows = corpus_io.read_rows(target_path)
    kept = [row for row in rows if schema.dedup_key(row) not in keep_keys]
    removed = len(rows) - len(kept)
    dropped = sorted({schema.dedup_key(r) for r in rows if schema.dedup_key(r) in keep_keys})

    print(f"{args.source}: {removed} rows overlap {args.against} ({len(dropped)} documents)")
    for key in dropped[:20]:
        print(f"  {key}")
    if len(dropped) > 20:
        print(f"  ... and {len(dropped) - 20} more")

    if args.dry_run:
        print("dry run: nothing written")
        return 0
    if removed:
        backup = target_path.with_suffix(target_path.suffix + ".bak")
        backup.write_bytes(target_path.read_bytes())
        corpus_io.write_rows(target_path, kept, schema.fields)
        print(f"rewrote {target_path} ({len(kept)} rows); backup at {backup}")
    return 0


def _stats(args: argparse.Namespace, context: AppContext) -> int:
    schema = context.schema
    report = {}
    for source in _sources(context, args.source):
        path = context.workspace.corpus_csv(source)
        if not path.exists():
            continue
        rows = corpus_io.read_rows(path)
        grouped = corpus_io.group_by_family(rows, schema)
        per_language: dict[str, int] = {}
        coverage: dict[int, int] = {}
        for row in rows:
            language = schema.language_of(row)
            per_language[language] = per_language.get(language, 0) + 1
        for members in grouped.values():
            count = len(corpus_io.languages_of(members, schema))
            coverage[count] = coverage.get(count, 0) + 1
        report[source.name] = {
            "path": str(path),
            "rows": len(rows),
            "documents": len(grouped),
            "per_language": dict(sorted(per_language.items())),
            "coverage_distribution": dict(sorted(coverage.items())),
        }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    if not report:
        print("no corpora found; run `clir ingest` first")
        return 0
    for name, info in report.items():
        print(f"{name}: {info['rows']} rows, {info['documents']} documents")
        print(f"  {info['path']}")
        print(f"  per language: {info['per_language']}")
        print(f"  languages per document: {info['coverage_distribution']}")
    return 0
