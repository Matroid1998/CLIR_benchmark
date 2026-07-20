"""
Concept-query generation for the alias-graph benchmark.

For each selected document we generate ONE technical search query whose *answer
is the concept itself*: concept = Aspirin -> a query that describes aspirin from
a gold patent without ever naming it; answer = "Aspirin". Every alias the
concept has, in every language, is handed to the generator as a forbidden list,
because a query that leaks any surface form of the answer would be solvable by
string matching rather than by understanding the chemistry.

The query language is chosen with the same four strategies as the main QAC
pipeline, and the same two verifiers grade the pair -- but with the single-arity
prompts, since there is one candidate rather than three.
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from tqdm import tqdm

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
from clir_bench.core.llm import call_with_retries, chat, client_for, parse_json_object
from clir_bench.core.parallel import run_tasks
from clir_bench.core.prompts import PromptPack
from clir_bench.core.qagen import STRATEGY_NAMES, pick_target_languages
from clir_bench.domains.chem_patents.aliasgraph.builder import (
    DEFAULT_SOURCE,
    alias_json_path,
    load_concepts,
    qac_csv_path,
)
from clir_bench.domains.chem_patents.aliasgraph.matching import contains_name

# Directory inside the domain's prompt package holding one concept-query
# generation prompt per language (``<prompts_package>/concept_query/<lang>.txt``).
CONCEPT_PROMPT_DIR = "concept_query"

# Retry generation on an empty/errored response for the same document.
MAX_GEN_RETRIES = 3


def generate_concept_qa(context: AppContext, args: argparse.Namespace) -> int:
    """Handler for ``clir alias-graph qa``."""
    schema = context.schema
    languages = list(context.languages.working)
    entries = load_concepts(alias_json_path(context))
    corpus_csv = context.workspace.corpus_csv(DEFAULT_SOURCE)
    groups = corpus_io.load_grouped(corpus_csv, schema)
    output_path = qac_csv_path(context)

    generation_model = getattr(args, "model", None) or context.settings.llm.generation_model
    grader = GraderConfig(
        model=context.settings.llm.concept_verifier_model,
        reasoning_effort=context.settings.llm.grading_reasoning_effort,
        thinking_budget_tokens=context.settings.llm.thinking_budget_tokens,
        thinking_max_tokens=context.settings.llm.thinking_max_tokens,
    )
    strategy = int(args.strategy)
    limit = getattr(args, "limit", None)
    workers = max(1, int(getattr(args, "workers", 1) or 1))
    rng = random.Random(args.seed)

    per_lang = max(1, limit // len(languages)) if limit is not None else None
    plan = _build_document_plan(
        entries,
        groups,
        context=context,
        per_lang=per_lang,
        strategy=strategy,
        languages=languages,
        rng=rng,
    )
    n_docs = len({family for _, family, _ in plan})
    target = f"~{per_lang}/language" if per_lang is not None else "all eligible"
    print(
        f"Concept-query QA: {n_docs} documents ({target}) -> {len(plan)} queries, "
        f"strategy={STRATEGY_NAMES.get(strategy, strategy)}, model={generation_model}, "
        f"grader={grader.model}, workers={workers}"
    )

    fields = _output_fieldnames(schema)
    corpus_io.write_rows(output_path, (), fields)  # fresh file with just the header

    prompts = PromptPack(context.domain.prompts_package)
    generation_client = client_for(generation_model)
    grading_client = client_for(grader.model)
    language_order = list(context.languages.priority)

    def work(item: Tuple[dict, str, str]) -> Optional[dict]:
        entry, family, target_lang = item
        name_set = entry.get("name_set", {})
        return _process_item(
            entry,
            groups[family],
            family,
            target_lang,
            name_set,
            all_aliases(name_set),
            context=context,
            prompts=prompts,
            generation_client=generation_client,
            grading_client=grading_client,
            generation_model=generation_model,
            grader=grader,
            strategy=strategy,
            language_order=language_order,
        )

    written = 0
    for row in run_tasks(plan, work, workers=workers, description="Concept Q&A"):
        if row is None:
            continue
        corpus_io.write_rows(output_path, [row], fields, append=True)
        written += 1

    print(f"\nWrote {written} concept-query rows -> {output_path}")
    return 0


# --------------------------------------------------------------------------- #
# Names and answers
# --------------------------------------------------------------------------- #

def _names_for_lang(name_set: Mapping[str, Any], lang: str) -> List[str]:
    value = name_set.get(lang)
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return []


def all_aliases(name_set: Mapping[str, Any]) -> List[str]:
    seen: Dict[str, None] = {}
    for value in name_set.values():
        names = value if isinstance(value, list) else [value]
        for n in names:
            if n:
                seen.setdefault(n, None)
    return list(seen)


def pick_answer(
    name_set: Mapping[str, Any],
    target_lang: str,
    passages: str,
    answer_order: Sequence[str],
) -> Tuple[str, str, bool]:
    """
    Choose the answer (the concept's name). Decision: answer = the concept's name
    in the query language. We use the query-language Wikipedia title when the
    concept has one (preferring a grounded variant), otherwise the **canonical
    ChEBI primary name** (English). We never scan the full ChEBI synonym list,
    because it contains brand names and formulas that are common words (e.g.
    "Action", "CO2") and would be wrongly picked up as grounded.
    Returns (answer, lang, grounded).
    """
    if target_lang != "chebi":
        target_names = _names_for_lang(name_set, target_lang)
        for nm in target_names:
            if contains_name(passages, nm):
                return nm, target_lang, True
        if target_names:
            return target_names[0], target_lang, False

    # No Wikipedia title in the query language: use the ChEBI primary name (the
    # first entry of the chebi bucket is the canonical name, not a synonym).
    chebi_names = _names_for_lang(name_set, "chebi")
    if chebi_names:
        primary = chebi_names[0]
        return primary, "chebi", contains_name(passages, primary)

    # Last resort: any Wikipedia title we have.
    for lang in answer_order:
        names = _names_for_lang(name_set, lang)
        if names:
            return names[0], lang, contains_name(passages, names[0])
    return "", "", False


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #

def generate_concept_query(
    client: Any,
    prompt: str,
    passages: str,
    concept_name: str,
    aliases: Sequence[str],
    *,
    model: str,
    reasoning_effort: str,
) -> Dict[str, str]:
    """Generate ONE concept-centric technical query."""
    alias_block = ", ".join(aliases)
    user = (
        f"CONCEPT (the answer): {concept_name}\n"
        f"ALIASES — never use any of these in the question (any language/spelling): {alias_block}\n\n"
        f"PASSAGES:\n{passages}"
    )
    raw = chat(
        client,
        model,
        [{"role": "system", "content": prompt}, {"role": "user", "content": user}],
        reasoning_effort=reasoning_effort,
    )
    data = parse_json_object(raw)
    return {
        "question": str(data.get("question", "")).strip(),
        "question_type": str(data.get("question_type", "other")).strip(),
    }


def _process_item(
    entry: Mapping[str, Any],
    doc_rows: Sequence[dict],
    family: str,
    target_lang: str,
    name_set: Mapping[str, Any],
    aliases: Sequence[str],
    *,
    context: AppContext,
    prompts: PromptPack,
    generation_client: Any,
    grading_client: Any,
    generation_model: str,
    grader: GraderConfig,
    strategy: int,
    language_order: Sequence[str],
) -> Optional[dict]:
    """Generate + grade ONE (concept, gold publication, target language) item.

    All language variants of ``doc_rows`` (the same patent in en/de/fr/es/zh) are
    passed to the generator together; the question is written in ``target_lang``.
    Returns the output row, or None if no valid question/answer could be formed.
    """
    schema = context.schema
    passages = corpus_io.build_passages_text(doc_rows, schema, order=language_order)
    if not passages.strip():
        return None
    context_row = corpus_io.pick_context_row(doc_rows, schema, target_lang) or doc_rows[0]
    context_languages = corpus_io.serialize_languages(doc_rows, schema, order=language_order)

    answer, answer_lang, _grounded = pick_answer(
        name_set, target_lang, passages, context.languages.answer_order
    )
    if not answer:
        return None

    prompt = prompts.custom(CONCEPT_PROMPT_DIR, f"{target_lang}.txt")

    def _generate() -> Dict[str, str]:
        candidate = generate_concept_query(
            generation_client,
            prompt,
            passages,
            entry["name"],
            aliases,
            model=generation_model,
            reasoning_effort=context.settings.llm.generation_reasoning_effort,
        )
        # An empty question is a non-response, not a valid result: retry it the
        # same way a transport error is retried.
        if not candidate["question"]:
            raise ValueError("empty question")
        return candidate

    try:
        gen = call_with_retries(
            _generate,
            retries=MAX_GEN_RETRIES,
            label=f"concept query {entry['chebi_id']} [{target_lang}]",
        )
    except RuntimeError as exc:
        tqdm.write(f"  {entry['chebi_id']} [{target_lang}]: {exc}; skipped")
        return None

    qa_pair = {"question": gen["question"], "answer": answer}
    try:
        faith, qual = grade_one(
            grading_client,
            grader,
            prompts.faithfulness("single"),
            prompts.quality(MODE_TECHNICAL, "single"),
            passages,
            qa_pair,
            MODE_TECHNICAL,
        )
    except Exception as exc:  # noqa: BLE001 - a grader hiccup must not fail the run
        tqdm.write(f"  {entry['chebi_id']} [{target_lang}]: grading error: {exc}")
        return None

    row: Dict[str, Any] = {
        "chebi_id": entry["chebi_id"],
        "concept_name": entry["name"],
        "mode": MODE_TECHNICAL,
        "strategy": strategy,
        "strategy_name": STRATEGY_NAMES.get(strategy, str(strategy)),
        "corpus_id": schema.id_of(context_row),
        schema.family_field: family,
        "question_language": target_lang,
        # Quirk kept from the published dataset: this column is named
        # ``context_language`` but holds the comma-joined list of every language
        # the document exists in, not a single language.
        "context_language": context_languages,
        "question": gen["question"],
        "answer": answer,
        "answer_language": answer_lang,
        "question_type": gen["question_type"],
        "gold_publication_count": entry.get("n_gold", len(entry.get("gold", []))),
    }
    row.update(grade_columns(faith, qual, MODE_TECHNICAL))
    tqdm.write(
        f"  {entry['chebi_id']} ({entry['name']}) [{target_lang}]: "
        f"ok (total={row['total_score']})"
    )
    return row


def _output_fieldnames(schema) -> tuple[str, ...]:
    return (
        "chebi_id", "concept_name", "mode", "strategy", "strategy_name",
        "corpus_id", schema.family_field, "question_language", "context_language",
        "question", "answer", "answer_language", "question_type",
        *FAITHFULNESS_FIELDS, *TECHNICAL_QUALITY_FIELDS,
        "qual_failure_type", "total_score", "gold_publication_count",
    )


# --------------------------------------------------------------------------- #
# Document selection
# --------------------------------------------------------------------------- #

def _groundable_concepts(
    family_concepts: Sequence[Mapping[str, Any]], passages: str
) -> List[Mapping[str, Any]]:
    """Concepts (gold for this document) whose name actually appears in the passages."""
    out: List[Mapping[str, Any]] = []
    for entry in family_concepts:
        names = all_aliases(entry.get("name_set", {}))
        if names and any(contains_name(passages, nm) for nm in names):
            out.append(entry)
    return out


def _build_document_plan(
    entries: Sequence[Mapping[str, Any]],
    groups: Mapping[str, Sequence[dict]],
    *,
    context: AppContext,
    per_lang: Optional[int],
    strategy: int,
    languages: Sequence[str],
    rng: random.Random,
) -> List[Tuple[Mapping[str, Any], str, str]]:
    """Select unique documents and build a (concept, family, query language) work list.

    Each selected document is paired with a single answer-concept (a concept it
    is gold for whose name appears in the passages) and one query per language
    returned by ``strategy``: a single language for strategies 1-3, all five for
    strategy 4 ("all"). Selection is balanced by *source* language: each language
    should be present in at least ``per_lang`` selected documents (a multilingual
    document counts toward every language it contains), so the total number of
    documents may be below ``len(languages) * per_lang``. A language with too few
    eligible documents is capped and warned. When ``per_lang`` is None, every
    eligible document is selected (no cap).
    """
    schema = context.schema
    langs = list(languages)
    order = list(context.languages.priority)

    # Invert concept -> gold into family -> [concept entries this document is gold for].
    family_concepts: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for entry in entries:
        for family in entry.get("gold", []):
            if family in groups:
                family_concepts[family].append(entry)

    # Per candidate document: present languages + the concepts groundable in its text.
    present_by_family: Dict[str, Set[str]] = {}
    groundable_by_family: Dict[str, List[Mapping[str, Any]]] = {}
    candidates: List[str] = []
    for family, concepts in family_concepts.items():
        rows = groups[family]
        present = corpus_io.languages_of(rows, schema) & set(langs)
        if not present:
            continue
        passages = corpus_io.build_passages_text(rows, schema, order=order)
        if not passages.strip():
            continue
        grounded = _groundable_concepts(concepts, passages)
        if not grounded:
            continue
        present_by_family[family] = present
        groundable_by_family[family] = grounded
        candidates.append(family)

    rng.shuffle(candidates)

    if per_lang is None:
        selected = list(candidates)
    else:
        # Assign up to ``per_lang`` DISTINCT documents to each language (each
        # document counts toward exactly one language), so the total is ~``limit``
        # rather than collapsing when documents are multilingual. Process scarcer
        # languages first so they claim their few documents before abundant ones
        # (en/fr) can take them; ``candidates`` is already shuffled, so the
        # per-language pick is uniform-random.
        selected_set: Set[str] = set()
        langs_by_scarcity = sorted(
            langs, key=lambda L: sum(1 for f in candidates if L in present_by_family[f])
        )
        for language in langs_by_scarcity:
            picked = 0
            for family in candidates:
                if picked >= per_lang:
                    break
                if family in selected_set or language not in present_by_family[family]:
                    continue
                selected_set.add(family)
                picked += 1
        selected = [f for f in candidates if f in selected_set]
        # Warn on each language's true coverage in the final set (a document
        # assigned to one language may also exist in others).
        for language in langs:
            have = sum(1 for f in selected if language in present_by_family[f])
            if have < per_lang:
                print(
                    f"  [balance] {language}: only {have}/{per_lang} eligible documents "
                    "(selected all available)"
                )

    plan: List[Tuple[Mapping[str, Any], str, str]] = []
    for family in selected:
        grounded = list(groundable_by_family[family])
        rng.shuffle(grounded)
        entry = grounded[0]
        # One query per language returned by the strategy: a single language for
        # strategies 1-3, all of them for strategy 4 ("all"). Document selection
        # (which/how many documents) is independent of this.
        for target_lang in pick_target_languages(
            strategy, sorted(present_by_family[family]), langs, rng=rng
        ):
            plan.append((entry, family, target_lang))
    return plan


# Re-exported for the code-switch benchmarks: their queries must be *the same
# kind of query* as the alias-graph ones, so they call these rather than keeping
# a second copy that could silently drift.
__all__ = [
    "CONCEPT_PROMPT_DIR",
    "all_aliases",
    "generate_concept_qa",
    "generate_concept_query",
    "pick_answer",
]
