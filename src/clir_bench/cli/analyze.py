"""
The ``analyze`` command group.

Analysis is deliberately separate from evaluation: it reads saved per-query
predictions, so every breakdown can be recomputed, corrected or extended without
re-running a single model. Each command resolves the dataset it should read from
the run's own metadata, so a run stays interpretable without re-specifying flags.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from clir_bench.core.context import AppContext
from clir_bench.core.runs import read_metadata, resolve_run_dir


def register(subparsers: argparse._SubParsersAction, context: Optional[AppContext]) -> None:
    parser = subparsers.add_parser("analyze", help="Analyse a finished evaluation run")
    sub = parser.add_subparsers(dest="analyze_command", metavar="<subcommand>")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--run", help="Run id or path (default: latest)")
    common.add_argument("--dataset-repo", help="Override the dataset recorded in the run")
    common.add_argument("--output", type=Path, help="Output directory")
    common.add_argument("--no-plots", action="store_true", help="Skip PNG plots")

    questions = sub.add_parser(
        "questions",
        parents=[common],
        help="Per-question metrics by language, mode, strategy and query origin",
    )
    questions.add_argument("--k", type=int, default=10, help="Cutoff for recall/MRR (default: 10)")
    questions.add_argument("--query-metadata", type=Path, help="CSV supplying mode/strategy per question")
    questions.set_defaults(handler=_questions)

    confusion = sub.add_parser(
        "confusion",
        parents=[common],
        help="How often a labelled hard negative outranks the right document",
    )
    confusion.set_defaults(handler=_confusion)

    rescore = sub.add_parser(
        "rescore",
        parents=[common],
        help="Re-score saved predictions under a different relevance definition",
    )
    rescore.add_argument("--lens", nargs="+", help="Relevance lenses to apply (domain-defined)")
    rescore.add_argument("--drop-models", nargs="+", help="Exclude these models from the rescore")
    rescore.set_defaults(handler=_rescore)


def _resolve(args: argparse.Namespace, context: AppContext) -> tuple[Path, str, str]:
    run_dir = resolve_run_dir(context.workspace.runs_dir, args.run)
    metadata = read_metadata(run_dir)
    dataset_repo = args.dataset_repo or metadata.get("dataset_repo") or context.hf_repo("benchmark_repo")
    variant = metadata.get("dataset_variant") or context.settings.eval.variant
    if not dataset_repo:
        raise ValueError(f"{run_dir} records no dataset; pass --dataset-repo")
    print(f"run {run_dir.name}  dataset {dataset_repo} ({variant})")
    return run_dir, dataset_repo, variant


def _questions(args: argparse.Namespace, context: AppContext) -> int:
    from clir_bench.analysis.questions import analyze_questions

    run_dir, dataset_repo, variant = _resolve(args, context)
    output = args.output or (run_dir / "question_analysis")
    report = analyze_questions(
        predictions_dir=run_dir / "predictions",
        output_dir=output,
        dataset_repo=dataset_repo,
        variant=variant,
        schema=context.schema,
        vocab=context.domain.analysis,
        k=args.k,
        make_plots=not args.no_plots,
        query_metadata_csv=args.query_metadata,
    )
    print(f"report -> {report}")
    return 0


def _confusion(args: argparse.Namespace, context: AppContext) -> int:
    from clir_bench.analysis.confusion import analyze_confusion

    run_dir, dataset_repo, variant = _resolve(args, context)
    output = args.output or (run_dir / "confusion")
    report = analyze_confusion(
        predictions_dir=run_dir / "predictions",
        output_dir=output,
        dataset_repo=dataset_repo,
        variant=variant,
        schema=context.schema,
        make_plots=not args.no_plots,
        negative_name_columns=context.setting("negative_name_columns", ("neighbor_name",)),
    )
    print(f"report -> {report}")
    return 0


def _rescore(args: argparse.Namespace, context: AppContext) -> int:
    from clir_bench.analysis.rescore import rescore_run

    run_dir, dataset_repo, variant = _resolve(args, context)
    output = args.output or (run_dir / "interpretations")
    report = rescore_run(
        predictions_dir=run_dir / "predictions",
        output_dir=output,
        dataset_repo=dataset_repo,
        variant=variant,
        schema=context.schema,
        lenses=args.lens,
        drop_models=args.drop_models,
    )
    print(f"report -> {report}")
    return 0
