"""
The ``eval`` command group.

Running embedding models is expensive and belongs on a compute node, so the
default path is a hand-off: ``clir eval plan`` writes the exact commands (and an
sbatch script) to run elsewhere. ``clir eval run`` refuses to load models unless
told explicitly, which keeps an accidental full-corpus encode from taking over a
workstation.
"""

from __future__ import annotations

import argparse
import os
import shlex
from pathlib import Path
from typing import Optional, Sequence

from clir_bench.core.context import AppContext
from clir_bench.core.runs import make_run_id, resolve_run_dir

ALLOW_LOCAL_ENV = "CLIR_ALLOW_LOCAL_MODELS"


def register(subparsers: argparse._SubParsersAction, context: Optional[AppContext]) -> None:
    parser = subparsers.add_parser("eval", help="Evaluate retrieval models on a benchmark")
    sub = parser.add_subparsers(dest="eval_command", metavar="<subcommand>")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("models", nargs="*", help="Model ids, or 'all' for the domain's default set")
    common.add_argument("--dataset-repo", help="Benchmark dataset repo")
    common.add_argument("--corpus-repo", help="Shared haystack repo (empty string = the dataset's own corpus)")
    common.add_argument(
        "--variant",
        choices=["multilingual", "cross_language"],
        help="Which qrels to score against (default: from clir.toml)",
    )
    common.add_argument("--batch-size", type=int, help="Encoding batch size")
    common.add_argument("--run-label", help="Label appended to the run id")

    run = sub.add_parser(
        "run",
        parents=[common],
        help="Run the evaluation here (loads models; intended for a compute node)",
    )
    run.add_argument(
        "--allow-local",
        action="store_true",
        help="Confirm that loading embedding models on this machine is intended",
    )
    run.set_defaults(handler=_run)

    plan = sub.add_parser(
        "plan",
        parents=[common],
        help="Write the commands to run this evaluation elsewhere",
    )
    plan.add_argument("--sbatch", action="store_true", help="Also write a SLURM batch script")
    plan.add_argument("--output", type=Path, help="Where to write (default: cluster/)")
    plan.set_defaults(handler=_plan)

    tables = sub.add_parser("tables", help="Build comparison tables from a finished run")
    tables.add_argument("--run", help="Run id or path (default: latest)")
    tables.add_argument("--output", type=Path, help="Output directory (default: <run>/mteb_tables)")
    tables.set_defaults(handler=_tables)


def _models(args: argparse.Namespace, context: AppContext) -> list[str]:
    """Resolve the model list, expanding 'all' to the domain's curated set."""
    configured = list(context.setting("eval_models", ()) or context.settings.eval.models)
    requested = list(args.models or [])
    if not requested or [m.lower() for m in requested] == ["all"]:
        if not configured:
            raise ValueError(
                "no models given and no eval_models configured for this domain; "
                "pass model ids explicitly"
            )
        return configured
    resolved: list[str] = []
    for model in requested:
        resolved.extend(configured if model.lower() == "all" else [model])
    return list(dict.fromkeys(resolved))


def _dataset_repo(args: argparse.Namespace, context: AppContext) -> str:
    repo = context.hf_repo("benchmark_repo", args.dataset_repo)
    if not repo:
        raise ValueError("no dataset repo: pass --dataset-repo or set benchmark_repo in clir.toml")
    return repo


def _corpus_repo(args: argparse.Namespace, context: AppContext) -> str:
    if args.corpus_repo is not None:
        return args.corpus_repo.strip()
    return context.setting("corpus_repo", context.settings.eval.corpus_repo) or ""


def _run(args: argparse.Namespace, context: AppContext) -> int:
    allowed = (
        args.allow_local
        or context.settings.eval.allow_local_models
        or os.environ.get(ALLOW_LOCAL_ENV) == "1"
    )
    if not allowed:
        print(
            "Refusing to load embedding models without confirmation.\n"
            "  Encoding a full corpus needs a GPU node and can exhaust a workstation.\n\n"
            "  On a compute node:  clir eval run ... --allow-local\n"
            f"  Or set {ALLOW_LOCAL_ENV}=1, or allow_local_models = true under [eval] in clir.toml\n"
            "  To prepare the job instead:  clir eval plan ...",
        )
        return 2

    from clir_bench.evaluation.harness import run_evaluation

    models = _models(args, context)
    run_id = make_run_id(args.run_label)
    run_dir = context.workspace.runs_dir / run_id
    summaries = run_evaluation(
        models=models,
        dataset_repo=_dataset_repo(args, context),
        corpus_repo=_corpus_repo(args, context),
        variant=args.variant or context.settings.eval.variant,
        run_dir=run_dir,
        run_id=run_id,
        batch_size=args.batch_size or context.settings.eval.batch_size,
        context=context,
    )
    print(f"\nrun {run_id} -> {run_dir}")
    for model, metrics in summaries.items():
        print(f"  {model}: {metrics.get('main_score', 'n/a')}")
    print("\nnext (no models needed):")
    print(f"  clir analyze questions --run {run_id}")
    return 0


def _plan(args: argparse.Namespace, context: AppContext) -> int:
    models = _models(args, context)
    run_label = args.run_label or "eval"
    dataset_repo = _dataset_repo(args, context)
    corpus_repo = _corpus_repo(args, context)
    variant = args.variant or context.settings.eval.variant
    batch_size = args.batch_size or context.settings.eval.batch_size

    command = [
        "clir",
        "--domain",
        context.domain.name,
        "eval",
        "run",
        *models,
        "--dataset-repo",
        dataset_repo,
        "--variant",
        variant,
        "--batch-size",
        str(batch_size),
        "--run-label",
        run_label,
        "--allow-local",
    ]
    if corpus_repo:
        command += ["--corpus-repo", corpus_repo]
    rendered = " ".join(shlex.quote(part) for part in command)

    target = Path(args.output) if args.output else context.settings.cluster_dir
    target.mkdir(parents=True, exist_ok=True)
    script = target / f"eval_{run_label}.sh"
    script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        f"# {len(models)} model(s) against {dataset_repo} ({variant})\n"
        f"{rendered}\n",
        encoding="utf-8",
    )
    script.chmod(0o755)

    print(f"models ({len(models)}):")
    for model in models:
        print(f"  {model}")
    print(f"\ncommand:\n  {rendered}")
    print(f"\nwrote {script}")

    if args.sbatch:
        sbatch = target / f"eval_{run_label}.sbatch"
        sbatch.write_text(_sbatch_script(run_label, rendered), encoding="utf-8")
        print(f"wrote {sbatch}\n  submit with: sbatch {sbatch}")
    return 0


def _sbatch_script(run_label: str, command: str) -> str:
    return (
        "#!/usr/bin/env bash\n"
        f"#SBATCH --job-name=clir-{run_label}\n"
        "#SBATCH --gres=gpu:1\n"
        "#SBATCH --cpus-per-task=8\n"
        "#SBATCH --mem=64G\n"
        "#SBATCH --time=12:00:00\n"
        f"#SBATCH --output=cluster/out/{run_label}-%j.log\n\n"
        "set -euo pipefail\n"
        "export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-0}\n\n"
        f"{command}\n"
    )


def _tables(args: argparse.Namespace, context: AppContext) -> int:
    from clir_bench.analysis.tables import build_comparison_tables

    run_dir = resolve_run_dir(context.workspace.runs_dir, args.run)
    output = args.output or (run_dir / "mteb_tables")
    path = build_comparison_tables(run_dir, output)
    print(f"tables -> {path}")
    return 0
