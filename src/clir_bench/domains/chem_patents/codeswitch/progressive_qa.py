"""
Queries for the progressive ladder.

Each base document gets ONE query per target language, about the concept whose
term is swapped at rung 1. The same query is emitted against every depth of that
base's ladder: the eval measures decay of a CONSTANT query against a degrading
document, so regenerating per depth would destroy the measurement.

Generation is deliberately identical to the alias-graph concept-query pipeline
-- same prompts, same describe-but-never-name contract, same answer selection,
same rubrics -- so the two benchmarks' scores can be read side by side. The
document is passed in all of its available languages at once; only the query
language varies. Generation runs on the OpenAI model, grading on the concept
verifier (Claude), which is the split the published progressive dataset used.
"""

from __future__ import annotations

import argparse
import random
from typing import Any, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.grading import (
    FAITHFULNESS_FIELDS,
    MODE_TECHNICAL,
    TECHNICAL_QUALITY_FIELDS,
    GraderConfig,
    grade_columns,
    grade_one,
)
from clir_bench.core.llm import client_for
from clir_bench.core.parallel import run_tasks
from clir_bench.core.prompts import PromptPack
from clir_bench.core.qagen import STRATEGY_NAMES, pick_target_languages
from clir_bench.domains.chem_patents.codeswitch import builder, progressive

# Same retry budget as the alias-graph concept-query pipeline.
MAX_GENERATION_RETRIES = 3

# Query ids suffix the base document id, matching the ladder's own separator
# (``<base>__r3`` / ``<base>__q_de``). Published, therefore fixed -- note it is
# NOT the core ``make_query_id`` convention, which uses a single underscore.
QUERY_ID_INFIX = f"{builder.VARIANT_ID_SEPARATOR}q_"

OUTPUT_FIELDS: tuple[str, ...] = (
    "base_id",
    "query_id",
    "n_replacements",
    "concept_chebi_id",
    "concept_name",
    "query_language",
    "strategy",
    "term_used",
    "question",
    "answer",
    "question_type",
    *FAITHFULNESS_FIELDS,
    *TECHNICAL_QUALITY_FIELDS,
    "qual_failure_type",
    "total_score",
    "gold_id",
    "source_id",
)


def _concept_helpers():
    """The alias-graph generator, alias list and answer picker.

    Imported rather than reimplemented: this benchmark's whole claim is that its
    queries are alias-graph concept queries asked against a degrading document,
    so a second copy of the generation contract here would silently make the two
    incomparable. They are module-private over there; a shared surface for them
    is the obvious follow-up if a third benchmark needs them too.
    """
    from clir_bench.domains.chem_patents.aliasgraph.concept_qa import (
        CONCEPT_PROMPT_DIR,
        all_aliases,
        generate_concept_query,
        pick_answer,
    )

    return CONCEPT_PROMPT_DIR, all_aliases, generate_concept_query, pick_answer


class _Generator:
    """Clients, prompts and models resolved once for the whole run."""

    def __init__(self, context: AppContext, args: argparse.Namespace) -> None:
        settings = context.settings.llm
        self.schema = context.schema
        self.prompts = PromptPack(context.domain.prompts_package)
        self.language_order = context.languages.priority
        self.strategy = int(args.strategy)

        self.model = args.model or settings.generation_model
        self.generation_client = client_for(self.model)
        self.generation_effort = settings.generation_reasoning_effort
        self.answer_order = context.languages.answer_order

        grader_model = args.grader_model or settings.concept_verifier_model
        self.grader_model = grader_model
        self.grading_client = client_for(grader_model)
        self.grader = GraderConfig(
            model=grader_model,
            reasoning_effort=settings.grading_reasoning_effort,
            thinking_budget_tokens=settings.thinking_budget_tokens,
            thinking_max_tokens=settings.thinking_max_tokens,
        )

        (
            self.concept_prompt_dir,
            self.all_aliases,
            self.generate_concept_query,
            self.pick_answer,
        ) = _concept_helpers()

    def _query(
        self,
        base: Mapping[str, Any],
        passages: str,
        name_set: Mapping[str, Any],
        aliases: Sequence[str],
        language: str,
    ) -> list[dict[str, Any]]:
        from tqdm import tqdm

        concept_name = base["concept_name"]
        generated: Optional[Mapping[str, str]] = None
        for _ in range(MAX_GENERATION_RETRIES):
            try:
                candidate = self.generate_concept_query(
                    self.generation_client,
                    self.prompts.custom(self.concept_prompt_dir, f"{language}.txt"),
                    passages,
                    concept_name,
                    aliases,
                    model=self.model,
                    reasoning_effort=self.generation_effort,
                )
            except Exception as exc:  # noqa: BLE001 - transport errors vary by provider
                tqdm.write(f"  {base['concept_chebi_id']} [{language}]: generation error: {exc}")
                continue
            if candidate.get("question"):
                generated = candidate
                break
        if generated is None:
            return []

        answer, _answer_language, _grounded = self.pick_answer(
            name_set, language, passages, self.answer_order
        )
        if not answer:
            return []

        qa = {"question": generated["question"], "answer": answer}
        try:
            faith, quality = grade_one(
                self.grading_client,
                self.grader,
                self.prompts.faithfulness("single"),
                self.prompts.quality(MODE_TECHNICAL, "single"),
                passages,
                qa,
                MODE_TECHNICAL,
            )
        except Exception as exc:  # noqa: BLE001 - a grader outage must not kill the run
            tqdm.write(
                f"  {base['concept_chebi_id']} [{language}]: grading error "
                f"({self.grader_model}): {exc}"
            )
            return []
        scores = grade_columns(faith, quality, MODE_TECHNICAL)

        query_id = f"{base['base_id']}{QUERY_ID_INFIX}{language}"
        return [
            {
                "base_id": base["base_id"],
                "query_id": query_id,
                "n_replacements": depth,
                "concept_chebi_id": base["concept_chebi_id"],
                "concept_name": concept_name,
                "query_language": language,
                "strategy": self.strategy,
                "term_used": base["original_term"],
                "question": generated["question"],
                "answer": answer,
                "question_type": generated.get("question_type", ""),
                **scores,
                "gold_id": gold_id,
                "source_id": base["base_id"],
            }
            for depth, gold_id in sorted(base["variants"])
        ]

    def base(
        self,
        base: Mapping[str, Any],
        grouped: Mapping[str, Sequence[Mapping[str, str]]],
        name_sets: Mapping[str, Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        rows = grouped.get(base["family"])
        if not rows:
            return []
        passages = corpus_io.build_passages_text(rows, self.schema, order=self.language_order)
        if not passages.strip():
            return []
        name_set = name_sets.get(base["concept_chebi_id"], {})
        aliases = self.all_aliases(name_set)

        out: list[dict[str, Any]] = []
        for language in base["target_languages"]:
            out.extend(self._query(base, passages, name_set, aliases, language))
        return out


def generate_progressive_qa(context: AppContext, args: argparse.Namespace) -> int:
    """Generate one fixed query per base document (per target language)."""
    schema = context.schema
    workdir = context.workspace.data("progressive")
    ladder_rows = corpus_io.read_rows(workdir / progressive.CORPUS_FILENAME)
    source = getattr(args, "source", "gp")
    grouped = corpus_io.load_grouped(context.workspace.corpus_csv(source), schema)
    name_sets = {
        concept["chebi_id"]: concept.get("name_set", {})
        for concept in builder.load_concepts(builder.alias_graph_path(context))
    }

    bases: dict[str, dict[str, Any]] = {}
    for row in ladder_rows:
        base_id = row["base_id"]
        base = bases.setdefault(
            base_id,
            {
                "base_id": base_id,
                "family": row["source_publication_number"],
                "concept_chebi_id": row["question_concept_chebi_id"],
                "concept_name": row["question_concept_name"],
                "anchor_language": row["anchor_language"],
                "original_term": row["question_original_term"],
                "variants": [],
            },
        )
        base["variants"].append((int(row["n_replacements"]), schema.id_of(row)))

    base_list = list(bases.values())
    if args.limit is not None:
        base_list = base_list[: args.limit]

    # Language choice happens up front, single-threaded, so the run reproduces
    # from the seed regardless of how the workers interleave.
    rng = random.Random(args.seed)
    working = list(context.languages.working)
    for base in base_list:
        present = sorted(
            corpus_io.languages_of(grouped.get(base["family"], []), schema)
        )
        base["target_languages"] = pick_target_languages(
            int(args.strategy), present, working, rng=rng
        )

    generator = _Generator(context, args)
    n_queries = sum(len(base["target_languages"]) for base in base_list)
    print(
        f"Progressive QA: {len(base_list)} base docs x "
        f"strategy={STRATEGY_NAMES.get(int(args.strategy), args.strategy)} -> {n_queries} "
        f"queries; generation={generator.model}, grading={generator.grader_model}, "
        f"workers={args.workers}"
    )

    output_path = workdir / progressive.QAC_FILENAME
    # Written base by base rather than at the end: these runs take hours, and an
    # interrupted one must keep everything already generated. The empty write
    # truncates any previous run's file and lays down the header.
    corpus_io.write_rows(output_path, (), OUTPUT_FIELDS)
    written = 0
    query_ids: set[str] = set()
    for rows in run_tasks(
        base_list,
        lambda base: generator.base(base, grouped, name_sets),
        workers=args.workers,
        description="Progressive QA",
    ):
        if not rows:
            continue
        written += corpus_io.write_rows(output_path, rows, OUTPUT_FIELDS, append=True)
        query_ids.update(row["query_id"] for row in rows)

    print(f"\nWrote {written} progressive-QA rows ({len(query_ids)} queries) -> {output_path}")
    return 0


__all__ = [
    "MAX_GENERATION_RETRIES",
    "OUTPUT_FIELDS",
    "QUERY_ID_INFIX",
    "generate_progressive_qa",
]
