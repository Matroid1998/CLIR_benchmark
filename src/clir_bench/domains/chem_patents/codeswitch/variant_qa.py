"""
Queries for the code-switched variants.

Two different question shapes, because the variants test two different things.

B/C/D/F ask about the ORIGINAL term: one query is generated per
(source document, concept, original term) with that term reproduced verbatim,
graded ONCE, and then fanned out across every variant in the group with the
variant document as gold. The gold document no longer contains the term the
query names -- that gap is the measurement, and generating a separate query per
variant would confound it with query-to-query variance.

E is a control, so it gets an ordinary document QA: three candidates on the E
document, graded and ranked, best one kept.
"""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Any, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.grading import (
    FAITHFULNESS_FIELDS,
    MODE_TECHNICAL,
    TECHNICAL_QUALITY_FIELDS,
    GraderConfig,
    grade_columns,
    grade_faithfulness,
    grade_one,
    grade_quality,
    rank_candidates,
)
from clir_bench.core.llm import chat, client_for, parse_json_object
from clir_bench.core.parallel import run_tasks
from clir_bench.core.prompts import PromptPack
from clir_bench.core.qagen import GenerationConfig, generate_candidates
from clir_bench.domains.chem_patents.codeswitch import builder

# The verbatim-term prompt is strict, but models still paraphrase the term. Two
# attempts (the second one scolding) was enough in practice; more just burns
# tokens on a concept whose term the model will not reproduce.
MAX_GENERATION_ATTEMPTS = 2

TERM_PROMPT_DIR = "concept_query_with_term"

OUTPUT_FIELDS: tuple[str, ...] = (
    "variant",
    "concept_chebi_id",
    "concept_name",
    "query_language",
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


def pick_answer(
    name_set: Mapping[str, Any], language: str, passages: str, answer_order: Sequence[str]
) -> str:
    """The concept's surface form in the query language (alias-graph rules).

    Imported from the alias-graph pipeline rather than reimplemented: the answer
    surface has to be chosen identically in both benchmarks or their scores are
    not comparable. This shim drops the language/grounded parts of its return,
    which the variant benchmark does not record.
    """
    from clir_bench.domains.chem_patents.aliasgraph.concept_qa import pick_answer as pick

    answer, _language, _grounded = pick(name_set, language, passages, answer_order)
    return answer


def generate_term_query(
    client: Any,
    prompts: PromptPack,
    passages: str,
    concept_name: str,
    term: str,
    language: str,
    *,
    model: str,
    reasoning_effort: str,
) -> Optional[dict[str, str]]:
    """One query in ``language`` that contains ``term`` character for character.

    Returns None when the model never reproduces the term exactly, which is a
    hard requirement: a query that paraphrased the swapped-out term would test
    paraphrase robustness rather than code-switching.
    """
    prompt = prompts.custom(TERM_PROMPT_DIR, f"{language}.txt")
    base = (
        f"CONCEPT: {concept_name}\n"
        f"TERM (use exactly, verbatim): {term}\n\n"
        f"PASSAGES:\n{passages}"
    )
    for attempt in range(MAX_GENERATION_ATTEMPTS):
        user = base
        if attempt:
            user += (
                "\n\nThe previous attempt did not contain the TERM exactly. "
                f"You MUST include this exact string in the question, unchanged: {term}"
            )
        raw = chat(
            client,
            model,
            [{"role": "system", "content": prompt}, {"role": "user", "content": user}],
            reasoning_effort=reasoning_effort,
        )
        data = parse_json_object(raw)
        question = str(data.get("question", "")).strip()
        if question and term in question:
            return {
                "question": question,
                "question_type": str(data.get("question_type", "other")).strip(),
            }
    return None


def _score_columns(faith: Mapping[str, Any], quality: Mapping[str, Any]) -> dict[str, Any]:
    return grade_columns(faith, quality, MODE_TECHNICAL)


class _Generator:
    """Everything a worker thread needs, resolved once."""

    def __init__(self, context: AppContext, args: argparse.Namespace) -> None:
        settings = context.settings.llm
        self.context = context
        self.schema = context.schema
        self.prompts = PromptPack(context.domain.prompts_package)
        self.model = args.model or settings.generation_model
        self.client = client_for(self.model)
        self.generation_effort = settings.generation_reasoning_effort
        # Variant QA grades on the generation model, as the published dataset
        # did; the Claude verifier is reserved for the progressive ladder.
        self.grader = GraderConfig(
            model=self.model, reasoning_effort=settings.grading_reasoning_effort
        )
        self.generation = GenerationConfig(
            generation_model=self.model,
            grader=self.grader,
            generation_reasoning_effort=settings.generation_reasoning_effort,
            retries=settings.retries,
        )
        self.language_order = context.languages.priority
        self.answer_order = context.languages.answer_order

    def passages(self, rows: Sequence[Mapping[str, str]]) -> str:
        return corpus_io.build_passages_text(rows, self.schema, order=self.language_order)

    def term_group(
        self,
        group: Mapping[str, Any],
        source_rows: Mapping[str, Mapping[str, str]],
        name_sets: Mapping[str, Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        source = source_rows.get(group["source_id"])
        if source is None:
            return []
        passages = self.passages([source])
        if not passages.strip():
            return []

        language = group["anchor_language"]
        term = group["original_term"]
        concept_name = group["concept_name"]
        generated = generate_term_query(
            self.client,
            self.prompts,
            passages,
            concept_name,
            term,
            language,
            model=self.model,
            reasoning_effort=self.generation_effort,
        )
        if generated is None:
            return []

        answer = pick_answer(
            name_sets.get(group["concept_chebi_id"], {}), language, passages, self.answer_order
        )
        qa = {"question": generated["question"], "answer": answer}
        faith, quality = grade_one(
            self.client,
            self.grader,
            self.prompts.faithfulness("single"),
            self.prompts.quality(MODE_TECHNICAL, "single"),
            passages,
            qa,
            MODE_TECHNICAL,
        )
        scores = _score_columns(faith, quality)

        return [
            {
                "variant": variant,
                "concept_chebi_id": group["concept_chebi_id"],
                "concept_name": concept_name,
                "query_language": language,
                "term_used": term,
                "question": generated["question"],
                "answer": answer,
                "question_type": generated["question_type"],
                **scores,
                "gold_id": gold_id,
                "source_id": group["source_id"],
            }
            for variant, gold_id in group["variants"]
        ]

    def control_document(self, row: Mapping[str, str]) -> list[dict[str, Any]]:
        passages = self.passages([row])
        if not passages.strip():
            return []
        language = row.get("anchor_language") or self.schema.language_of(row) or "en"

        qa_pairs = generate_candidates(
            self.client,
            self.generation,
            self.prompts.generation(MODE_TECHNICAL, language),
            passages,
            MODE_TECHNICAL,
        )
        qa_pairs = [qa for qa in qa_pairs if qa.get("question") and qa.get("answer")]
        if not qa_pairs:
            return []
        faith = grade_faithfulness(
            self.client, self.grader, self.prompts.faithfulness("batch"), passages, qa_pairs
        )
        quality = grade_quality(
            self.client,
            self.grader,
            self.prompts.quality(MODE_TECHNICAL, "batch"),
            passages,
            qa_pairs,
            MODE_TECHNICAL,
        )
        ranked = rank_candidates(qa_pairs, faith, quality, MODE_TECHNICAL)
        if not ranked:
            return []
        best = ranked[0]
        return [
            {
                "variant": "E",
                "concept_chebi_id": row.get("concept_chebi_id", ""),
                "concept_name": row.get("concept_name", ""),
                "query_language": language,
                "term_used": "",
                "question": best.qa.get("question", ""),
                "answer": best.qa.get("answer", ""),
                "question_type": best.qa.get("question_type", ""),
                **_score_columns(best.faith, best.quality),
                "gold_id": self.schema.id_of(row),
                "source_id": row.get("source_id", ""),
            }
        ]


def generate_variant_qa(context: AppContext, args: argparse.Namespace) -> int:
    """Generate queries for the A-F variant corpus. Returns 0 on success."""
    schema = context.schema
    workdir = context.workspace.data("code_switched")
    variant_rows = corpus_io.read_rows(workdir / builder.CORPUS_FILENAME)
    source_rows = {
        schema.id_of(row): row
        for row in corpus_io.read_rows(context.workspace.corpus_csv(getattr(args, "source", "gp")))
    }
    name_sets = {
        concept["chebi_id"]: concept.get("name_set", {})
        for concept in builder.load_concepts(builder.alias_graph_path(context))
    }

    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    control_rows: list[Mapping[str, str]] = []
    for row in variant_rows:
        variant = row.get("variant", "")
        if variant == "E":
            control_rows.append(row)
            continue
        if variant == "A":
            # The baseline document is its own gold for every group's query; it
            # needs no question of its own.
            continue
        key = (row["source_id"], row["concept_chebi_id"], row["original_term"])
        group = groups.setdefault(
            key,
            {
                "source_id": row["source_id"],
                "concept_chebi_id": row["concept_chebi_id"],
                "concept_name": row["concept_name"],
                "anchor_language": row["anchor_language"],
                "original_term": row["original_term"],
                "variants": [],
            },
        )
        group["variants"].append((variant, schema.id_of(row)))

    group_list = list(groups.values())
    if args.limit is not None:
        group_list = group_list[: args.limit]
        control_rows = control_rows[: args.limit]

    generator = _Generator(context, args)
    print(
        f"Variant QA: {len(group_list)} B/C/D/F groups + {len(control_rows)} E docs, "
        f"model={generator.model}, workers={args.workers}"
    )

    jobs: list[tuple[str, Any]] = [("group", g) for g in group_list]
    jobs += [("control", r) for r in control_rows]

    def run_job(job: tuple[str, Any]) -> list[dict[str, Any]]:
        kind, payload = job
        if kind == "group":
            return generator.term_group(payload, source_rows, name_sets)
        return generator.control_document(payload)

    out_rows: list[dict[str, Any]] = []
    for result in run_tasks(jobs, run_job, workers=args.workers, description="Variant QA"):
        out_rows.extend(result)

    output_path = workdir / builder.QAC_FILENAME
    written = corpus_io.write_rows(output_path, out_rows, OUTPUT_FIELDS)
    per_variant = Counter(row["variant"] for row in out_rows)
    print(f"\nWrote {written} variant-QA rows -> {output_path}")
    print(f"  per variant: {dict(sorted(per_variant.items()))}")
    return 0


__all__ = [
    "MAX_GENERATION_ATTEMPTS",
    "OUTPUT_FIELDS",
    "TERM_PROMPT_DIR",
    "generate_term_query",
    "generate_variant_qa",
]
