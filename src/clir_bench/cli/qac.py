"""The ``qac`` command group: generate and re-grade question/answer/context data."""

from __future__ import annotations

import argparse
from pathlib import Path

from clir_bench import domains
from clir_bench.core import corpus as corpus_io
from clir_bench.core import qagen
from clir_bench.core.context import AppContext
from clir_bench.core.grading import GraderConfig
from clir_bench.core.llm import client_for
from clir_bench.core.parallel import run_tasks
from clir_bench.core.prompts import PromptPack


def register(subparsers: argparse._SubParsersAction, context: AppContext | None) -> None:
    parser = subparsers.add_parser("qac", help="Generate and grade question/answer data")
    sub = parser.add_subparsers(dest="qac_command", metavar="<subcommand>")

    run_workflow = bool(context and context.setting("qac_runs", False))
    workers = 6 if run_workflow else 1
    plans = (
        ", ".join(context.domain.qac_plans)
        if context and context.domain.qac_plans
        else "none declared"
    )
    generate = sub.add_parser(
        "generate",
        help="Generate graded questions from a corpus",
        description=(
            "Generate and grade questions using the same selected targets for every "
            "generator. All models and sources share one results CSV in a run folder."
        )
        if run_workflow
        else (
            "Generates candidate questions per document, grades them for "
            "faithfulness and quality, and keeps the best per document and "
            f"language. Plans available for this domain: {plans}."
        ),
    )
    generate.add_argument(
        "--source",
        required=True,
        **(
            {
                "nargs": "+",
                "choices": context.domain.source_names,
                "help": "Source corpora to include in the same run",
            }
            if run_workflow
            else {"help": "Source corpus to generate from"}
        ),
    )
    generate.add_argument(
        "--plan",
        default="balanced",
        help=(argparse.SUPPRESS if run_workflow else f"Generation plan ({plans})"),
    )
    generate.add_argument(
        "--questions",
        type=int,
        default=None if run_workflow else 100,
        help=(
            "Target/language/persona cases per model, split across sources (default: 100); "
            "each case can produce up to --keep candidates"
            if run_workflow
            else "Questions per mode"
        ),
    )
    generate.add_argument(
        "--pool",
        type=int,
        default=None,
        help=(argparse.SUPPRESS if run_workflow else "Documents to sample from"),
    )
    generate.add_argument("--langs", nargs="+", help="Restrict question languages")
    generate.add_argument(
        "--priority-langs",
        nargs="+",
        help=(
            argparse.SUPPRESS
            if run_workflow
            else "Used by the `coverage` plan: prefer documents that exist in these "
            "languages, so questions land where coverage is thin"
        ),
    )
    generate.add_argument("--modes", nargs="+", help="Question modes (default: the domain's)")
    generate.add_argument(
        "--output",
        type=Path,
        help=(
            "CSV filename within the run folder (default: results.csv)"
            if run_workflow
            else "Output CSV (default: the source's qac dir)"
        ),
    )
    generate.add_argument(
        "--append",
        action="store_true",
        help=(argparse.SUPPRESS if run_workflow else "Append to an existing dataset"),
    )
    generate.add_argument(
        "--exclude-from",
        type=Path,
        help=(argparse.SUPPRESS if run_workflow else "Skip documents already covered by this CSV"),
    )
    generate.add_argument(
        "--generation-model",
        **(
            {"action": "append", "help": "Generator model ID; repeat to compare models"}
            if run_workflow
            else {"help": "Override the generation model"}
        ),
    )
    generate.add_argument("--verifier-model", help="Override the grading model")
    generate.add_argument(
        "--workers", type=int, default=workers, help=f"Parallel documents (default: {workers})"
    )
    generate.add_argument(
        "--seed",
        type=int,
        default=None if run_workflow else 42,
        help="Selection seed (default: 42; reused on resume)",
    )
    generate.add_argument("--limit", type=int, help="Stop after N plan items (smoke tests)")
    generate.add_argument(
        "--dry-run", action="store_true", help="Show the plan without calling any model"
    )
    if run_workflow:
        _run_arguments(generate)
        generate.add_argument(
            "--targets-from",
            type=Path,
            help="Reuse the exact targets and contexts from this run folder",
        )
        generate.add_argument(
            "--generation-cache", type=Path,
            help="Replay an existing response cache for matching model IDs and inputs",
        )
        generate.add_argument(
            "--keep",
            type=int,
            default=None,
            choices=(1, 2, 3),
            help="Maximum candidates per target (default: 3)",
        )
        _context_arguments(generate)
    generate.set_defaults(handler=_domain_command if run_workflow else _generate)

    regrade = sub.add_parser(
        "regrade",
        help="Re-grade existing candidates with a different judge",
        description=(
            "Re-runs the verifiers over already-generated candidates and rewrites "
            "the scores. Generation is untouched, so this isolates judge changes."
        ),
    )
    regrade.add_argument("--input", type=Path, required=True, help="CSV of generated candidates")
    regrade.add_argument(
        "--source",
        required=not run_workflow,
        **(
            {
                "nargs": "+",
                "choices": context.domain.source_names,
                "help": "Source corpora present in the input (default: infer from its rows)",
            }
            if run_workflow
            else {"help": "Source corpus the rows came from"}
        ),
    )
    regrade.add_argument(
        "--output",
        type=Path,
        help=(
            "CSV filename within the new run folder (default: results.csv)"
            if run_workflow
            else "Output CSV (default: <input>_regraded.csv)"
        ),
    )
    regrade.add_argument("--verifier-model", help="Override the grading model")
    regrade.add_argument("--workers", type=int, default=workers)
    if run_workflow:
        _run_arguments(regrade)
        _context_arguments(regrade)
        regrade.add_argument(
            "--dry-run",
            action="store_true",
            help="Inspect the input without calling models or writing files",
        )
    regrade.set_defaults(handler=_domain_command if run_workflow else _regrade)

    best = sub.add_parser(
        "best",
        help="Select the highest-scoring question per document and language",
    )
    best.add_argument("--input", type=Path, required=True)
    best.add_argument("--output", type=Path, help="Default: <input>_best.csv")
    best.set_defaults(handler=_domain_command if run_workflow else _best)


def _run_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--run-dir", type=Path,
        help="Run folder (default: each source's qac/<timestamp>); with multiple sources, a parent for corpus subfolders",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an existing --run-dir without repeating completed stages",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=None,
        help="Total attempts per generation or grading stage (default: 3)",
    )


def _context_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--max-references",
        type=int,
        default=None,
        help="Maximum EUR-Lex reference articles (default: 6)",
    )
    parser.add_argument(
        "--context-chars",
        type=int,
        default=None,
        help="UN context character budget (default: 30000)",
    )


def _domain_command(args: argparse.Namespace, context: AppContext) -> int:
    if getattr(args, "append", False):
        raise ValueError("--append is not supported for runs; use a new run or --resume --run-dir")
    if getattr(args, "resume", False) and not getattr(args, "run_dir", None):
        raise ValueError("--resume requires --run-dir")
    module = domains.load_module(context.domain.name)
    return module.qac_command(args.qac_command, args, context)


def _generation_config(args: argparse.Namespace, context: AppContext) -> qagen.GenerationConfig:
    llm = context.settings.llm
    return qagen.GenerationConfig(
        generation_model=getattr(args, "generation_model", None) or llm.generation_model,
        grader=GraderConfig(
            model=getattr(args, "verifier_model", None) or llm.verifier_model,
            reasoning_effort=llm.grading_reasoning_effort,
            thinking_budget_tokens=llm.thinking_budget_tokens,
            thinking_max_tokens=llm.thinking_max_tokens,
        ),
        generation_reasoning_effort=llm.generation_reasoning_effort,
        retries=llm.retries,
    )


def _generate(args: argparse.Namespace, context: AppContext) -> int:
    domain = context.domain
    source = domain.source(args.source)
    corpus_path = context.workspace.corpus_csv(source)
    if not corpus_path.exists():
        raise FileNotFoundError(f"no corpus for source {source.name!r} at {corpus_path}")

    plan_builder = domain.qac_plans.get(args.plan)
    if plan_builder is None:
        available = ", ".join(domain.qac_plans) or "none"
        raise KeyError(
            f"unknown plan {args.plan!r} for domain {domain.name!r}; available: {available}"
        )

    schema = context.schema
    grouped = corpus_io.load_grouped(corpus_path, schema)
    plan = plan_builder(context=context, source=source, grouped=grouped, args=args)
    if args.limit:
        plan = plan[: args.limit]

    output = args.output or (context.workspace.qac_dir(source) / f"qac_{source.name}.csv")
    fieldnames = qagen.output_fieldnames(schema)

    print(f"plan: {len(plan)} question(s) from {len(grouped)} documents in {corpus_path.name}")
    if args.dry_run:
        for item in plan[:20]:
            print(f"  {item.family:<24} {item.language}  {item.mode:<10} {item.strategy_name}")
        if len(plan) > 20:
            print(f"  ... and {len(plan) - 20} more")
        print(f"would write -> {output}")
        return 0
    if not plan:
        print("nothing to generate")
        return 0

    config = _generation_config(args, context)
    prompts = PromptPack(package=domain.prompts_package)
    generation_client = client_for(config.generation_model)
    grading_client = client_for(config.grader.model)
    order = domain.languages.priority or domain.languages.working

    def work(item: qagen.PlanItem):
        return qagen.generate_for_document(
            item,
            grouped.get(item.family, []),
            schema=schema,
            prompts=prompts,
            config=config,
            generation_client=generation_client,
            grading_client=grading_client,
            language_order=order,
        )

    if args.append:
        corpus_io.ensure_header(output, fieldnames)
    generated: list[dict] = []
    for rows in run_tasks(plan, work, workers=args.workers, description="generate"):
        generated.extend(rows)

    rows = [qagen.normalize_row(row, fieldnames) for row in generated]
    corpus_io.write_rows(output, rows, fieldnames, append=args.append)
    best_rows = qagen.select_best(rows, schema)
    best_path = _suffixed(output, "_best")
    corpus_io.write_rows(
        best_path, [qagen.normalize_row(r, fieldnames) for r in best_rows], fieldnames
    )

    print(f"wrote {len(rows)} candidate row(s) -> {output}")
    print(f"wrote {len(best_rows)} best row(s)      -> {best_path}")
    return 0


def _regrade(args: argparse.Namespace, context: AppContext) -> int:
    from clir_bench.core.grading import grade_columns, grade_one

    domain = context.domain
    schema = context.schema
    source = domain.source(args.source)
    grouped = corpus_io.load_grouped(context.workspace.corpus_csv(source), schema)
    rows = corpus_io.read_rows(args.input)
    if not rows:
        print(f"{args.input} is empty")
        return 0

    config = _generation_config(args, context)
    prompts = PromptPack(package=domain.prompts_package)
    client = client_for(config.grader.model)
    order = domain.languages.priority or domain.languages.working

    def work(row: dict) -> dict:
        family = str(row.get(schema.family_field, ""))
        passages = corpus_io.build_passages_text(grouped.get(family, []), schema, order=order)
        mode = str(row.get("mode") or "technical")
        faith, quality = grade_one(
            client,
            config.grader,
            prompts.faithfulness("batch"),
            prompts.quality(mode, "batch"),
            passages,
            {"question": row.get("question", ""), "answer": row.get("answer", "")},
            mode,
        )
        return {**row, **grade_columns(faith, quality, mode)}

    regraded = list(run_tasks(rows, work, workers=args.workers, description="regrade"))
    output = args.output or _suffixed(args.input, "_regraded")
    fieldnames = qagen.output_fieldnames(schema)
    corpus_io.write_rows(output, [qagen.normalize_row(r, fieldnames) for r in regraded], fieldnames)

    best_rows = qagen.select_best(regraded, schema)
    best_path = _suffixed(output, "_best")
    corpus_io.write_rows(
        best_path, [qagen.normalize_row(r, fieldnames) for r in best_rows], fieldnames
    )
    print(f"regraded {len(regraded)} row(s) -> {output}")
    print(f"best {len(best_rows)} row(s)     -> {best_path}")
    return 0


def _best(args: argparse.Namespace, context: AppContext) -> int:
    schema = context.schema
    rows = corpus_io.read_rows(args.input)
    best_rows = qagen.select_best(rows, schema)
    output = args.output or _suffixed(args.input, "_best")
    fieldnames = qagen.output_fieldnames(schema)
    corpus_io.write_rows(
        output, [qagen.normalize_row(r, fieldnames) for r in best_rows], fieldnames
    )
    print(f"selected {len(best_rows)} of {len(rows)} row(s) -> {output}")
    return 0


def _suffixed(path: Path, suffix: str) -> Path:
    path = Path(path)
    return path.with_name(f"{path.stem}{suffix}{path.suffix}")
