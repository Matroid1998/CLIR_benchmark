"""The ``runs`` command group: inspect the evaluation run registry."""

from __future__ import annotations

import argparse
import json
from typing import Optional

from clir_bench.core.context import AppContext
from clir_bench.core.runs import list_runs, read_metadata, read_summary, resolve_run_dir


def register(subparsers: argparse._SubParsersAction, context: Optional[AppContext]) -> None:
    parser = subparsers.add_parser("runs", help="Inspect evaluation runs")
    sub = parser.add_subparsers(dest="runs_command", metavar="<subcommand>")

    listing = sub.add_parser("list", help="List runs, newest first")
    listing.add_argument("--limit", type=int, default=20)
    listing.set_defaults(handler=_list)

    show = sub.add_parser("show", help="Show one run's provenance and scores")
    show.add_argument("--run", help="Run id or path (default: latest)")
    show.add_argument("--json", action="store_true")
    show.set_defaults(handler=_show)


def _list(args: argparse.Namespace, context: AppContext) -> int:
    runs = list_runs(context.workspace.runs_dir)
    if not runs:
        print(f"no runs under {context.workspace.runs_dir}")
        return 0
    for run in runs[: args.limit]:
        models = run["models"]
        summary = f"{len(models)} model(s)" if models else "no models recorded"
        print(f"{run['run_id']:<28} {run['created_at'][:19]:<20} {summary}")
    if len(runs) > args.limit:
        print(f"... and {len(runs) - args.limit} more")
    return 0


def _show(args: argparse.Namespace, context: AppContext) -> int:
    run_dir = resolve_run_dir(context.workspace.runs_dir, args.run)
    metadata = read_metadata(run_dir)
    summary = read_summary(run_dir)

    if args.json:
        print(json.dumps({"metadata": metadata, "summary": summary}, indent=2))
        return 0

    print(f"run       {metadata.get('run_id', run_dir.name)}")
    print(f"path      {run_dir}")
    print(f"created   {metadata.get('created_at', 'unknown')}")
    print(f"domain    {metadata.get('domain', 'unknown')}")
    print(f"dataset   {metadata.get('dataset_repo', '?')} ({metadata.get('dataset_variant', '?')})")
    if metadata.get("corpus_repo"):
        print(f"haystack  {metadata['corpus_repo']}")
    commit = metadata.get("git_commit")
    if commit:
        print(f"commit    {commit}{' (dirty)' if metadata.get('git_dirty') else ''}")
    sizes = metadata.get("sizes") or {}
    if sizes:
        print(f"sizes     {sizes}")

    models = (summary.get("models") or metadata.get("scores") or {})
    if models:
        print("\nscores")
        for model, metrics in models.items():
            main = metrics.get("main_score", "n/a") if isinstance(metrics, dict) else metrics
            print(f"  {model:<52} {main}")

    for name, label in (
        ("predictions", "predictions"),
        ("question_analysis", "question analysis"),
        ("confusion", "confusion analysis"),
        ("mteb_tables", "comparison tables"),
    ):
        if (run_dir / name).exists():
            print(f"\n{label}: {run_dir / name}")
    return 0
