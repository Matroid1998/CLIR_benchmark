"""
The progressive ladder: a dose-response version of code-switching.

Where ``builder.py`` perturbs one term per document, this builds a cumulative
ladder from a single base document::

    clean (0 swaps) -> 1 swap -> 2 -> 3 -> ... -> N swaps

Each rung swaps one MORE distinct chemistry term, using a mode drawn at random
from {B, C, D, F}. Variant E is excluded: it needs a model, and the point of
this build is that it is fully deterministic given the seed.

A single query (generated later, about the term swapped at rung 1) is reused at
every depth, so the eval sees a constant query against a document that degrades
one term at a time. Two properties make that reading valid and are enforced
here: the chosen terms have non-overlapping surfaces, so a later swap cannot
eat an earlier one; and a base whose term vanishes mid-ladder is dropped
entirely rather than producing a short ladder.

Swap primitives come from ``builder`` so both benchmarks perturb text
identically.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from typing import Any, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.domain import CorpusSchema
from clir_bench.domains.chem_patents.codeswitch import builder

# Modes the ladder can draw from; E is deliberately absent (see module docstring).
LADDER_MODES: tuple[str, ...] = ("B", "C", "D", "F")

TRACKING_FIELDS: tuple[str, ...] = (
    "base_id",
    "n_replacements",
    "anchor_language",
    "source_publication_number",
    "question_concept_chebi_id",
    "question_concept_name",
    "question_original_term",
    "replacements_json",
)

CORPUS_FILENAME = "progressive_corpus.csv"
QAC_FILENAME = "progressive_qac.csv"

# Ladder rungs are identified by suffixing the base document id.
RUNG_ID_PREFIX = f"{builder.VARIANT_ID_SEPARATOR}r"


def output_fieldnames(schema: CorpusSchema) -> tuple[str, ...]:
    return tuple(schema.fields) + TRACKING_FIELDS


def _mode_replacements(
    name_set: Mapping[str, Any],
    original: str,
    present_languages: set[str],
    anchor_language: str,
    modes: Sequence[str],
    working_languages: Sequence[str],
    rng: random.Random,
) -> dict[str, tuple[str, str]]:
    """``mode -> (replacement, target_language)`` for every mode that applies."""
    out: dict[str, tuple[str, str]] = {}
    for mode in modes:
        if mode == "B":
            swap = builder.clean_lang_swap(
                name_set, original, [l for l in present_languages if l != anchor_language], rng
            )
            if swap:
                out["B"] = (swap[1], swap[0])
        elif mode == "C":
            swap = builder.clean_lang_swap(
                name_set, original, [l for l in working_languages if l not in present_languages], rng
            )
            if swap:
                out["C"] = (swap[1], swap[0])
        elif mode == "D":
            replacement = builder.perturb(original, rng)
            if replacement:
                out["D"] = (replacement, anchor_language)
        elif mode == "F":
            replacement = builder.pick_ontology_variant(name_set.get("chebi", []), original, rng)
            if replacement:
                out["F"] = (replacement, "chebi")
    return out


def _swappable_terms(
    row: Mapping[str, str],
    language: str,
    present_languages: set[str],
    concept_ids: Sequence[str],
    concepts: Mapping[str, Mapping[str, Any]],
    modes: Sequence[str],
    working_languages: Sequence[str],
    rng: random.Random,
) -> list[dict[str, Any]]:
    """Concepts locatable in this language version that have an applicable swap.

    Replacements are computed here, once per concept, and carried along: the
    ladder later picks a mode per term and must not recompute (a second draw
    from ``rng`` would change the result).
    """
    out: list[dict[str, Any]] = []
    for concept_id in concept_ids:
        concept = concepts.get(concept_id)
        if concept is None:
            continue
        name_set = concept["name_set"]
        anchor = builder.locate_anchor(name_set, {language: row}, rng)
        if anchor is None:
            continue
        anchor_language, original = anchor
        replacements = _mode_replacements(
            name_set, original, present_languages, anchor_language, modes, working_languages, rng
        )
        if replacements:
            out.append(
                {
                    "cid": concept_id,
                    "name": concept["name"],
                    "original": original,
                    "mode_repls": replacements,
                }
            )
    return out


def _select_terms(
    swappable: Sequence[Mapping[str, Any]], steps: int, rng: random.Random
) -> Optional[list[Mapping[str, Any]]]:
    """``steps`` terms with non-overlapping surfaces, in random order.

    None when too few survive the overlap guard: a ladder shorter than requested
    would not be comparable with the others.
    """
    order = list(swappable)
    rng.shuffle(order)
    chosen: list[Mapping[str, Any]] = []
    surfaces: list[str] = []
    for candidate in order:
        surface = candidate["original"].casefold()
        if any(surface in other or other in surface for other in surfaces):
            continue
        chosen.append(candidate)
        surfaces.append(surface)
        if len(chosen) == steps:
            return chosen
    return None


def _rung_row(
    row: Mapping[str, str],
    *,
    schema: CorpusSchema,
    base_id: str,
    depth: int,
    anchor_language: str,
    family: str,
    concept_id: str,
    concept_name: str,
    original_term: str,
    steps: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    out = {key: row.get(key, "") for key in schema.fields}
    out[schema.id_field] = f"{base_id}{RUNG_ID_PREFIX}{depth}"
    out.update(
        {
            "base_id": base_id,
            "n_replacements": str(depth),
            "anchor_language": anchor_language,
            "source_publication_number": family,
            "question_concept_chebi_id": concept_id,
            "question_concept_name": concept_name,
            "question_original_term": original_term,
            # Only the steps applied at this depth, so a row describes itself.
            "replacements_json": json.dumps(list(steps[:depth]), ensure_ascii=False),
        }
    )
    return out


def build_progressive(context: AppContext, args: argparse.Namespace) -> int:
    """Build the cumulative ladder corpus. Returns 0 on success."""
    schema = context.schema
    steps_wanted = int(args.steps)
    modes = [
        mode.strip().upper()
        for mode in str(args.modes).split(",")
        if mode.strip().upper() in LADDER_MODES
    ]
    if not modes:
        raise ValueError(f"no usable swap modes in {args.modes!r}; pick from {list(LADDER_MODES)}")

    working_languages = tuple(context.languages.working)

    concepts = builder.load_concepts(builder.alias_graph_path(context))
    by_concept = {concept["chebi_id"]: concept for concept in concepts}

    families_by_concept: dict[str, list[str]] = defaultdict(list)
    for concept in concepts:
        for family in concept.get("gold", []):
            families_by_concept[family].append(concept["chebi_id"])

    by_family: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in corpus_io.read_rows(context.workspace.corpus_csv(args.source)):
        by_family[schema.family_of(row)][schema.language_of(row)] = row

    rng = random.Random(args.seed)
    # Sort before shuffling so the order depends on the seed alone, not on dict
    # iteration order.
    candidates = sorted(
        family
        for family, ids in families_by_concept.items()
        if len(ids) >= steps_wanted and family in by_family
    )
    rng.shuffle(candidates)

    priority = list(context.languages.priority)
    out_rows: list[dict[str, str]] = []
    mode_counts: dict[str, int] = defaultdict(int)
    n_bases = 0

    from tqdm import tqdm

    for family in tqdm(candidates, desc="Progressive CS", unit="doc"):
        if args.limit is not None and n_bases >= args.limit:
            break
        family_rows = by_family[family]
        present = set(family_rows)
        concept_ids = families_by_concept[family]

        # Use the language version that yields the most swappable terms; the
        # priority order only breaks ties.
        best_language: Optional[str] = None
        best_swappable: list[dict[str, Any]] = []
        for language in sorted(
            family_rows,
            key=lambda l: (priority.index(l) if l in priority else len(priority), l),
        ):
            swappable = _swappable_terms(
                family_rows[language],
                language,
                present,
                concept_ids,
                by_concept,
                modes,
                working_languages,
                rng,
            )
            if len(swappable) > len(best_swappable):
                best_swappable, best_language = swappable, language
        if best_language is None or len(best_swappable) < steps_wanted:
            continue

        chosen = _select_terms(best_swappable, steps_wanted, rng)
        if chosen is None:
            continue

        ladder_steps: list[dict[str, Any]] = []
        for index, candidate in enumerate(chosen, start=1):
            mode = rng.choice(sorted(candidate["mode_repls"]))
            replacement, target_language = candidate["mode_repls"][mode]
            ladder_steps.append(
                {
                    "step": index,
                    "concept_id": candidate["cid"],
                    "original": candidate["original"],
                    "replacement": replacement,
                    "mode": mode,
                    "target_language": target_language,
                }
            )

        anchor_row = family_rows[best_language]
        base_id = schema.id_of(anchor_row)
        question_term = chosen[0]

        def rung(row: Mapping[str, str], depth: int) -> dict[str, str]:
            return _rung_row(
                row,
                schema=schema,
                base_id=base_id,
                depth=depth,
                anchor_language=best_language,
                family=family,
                concept_id=question_term["cid"],
                concept_name=question_term["name"],
                original_term=question_term["original"],
                steps=ladder_steps,
            )

        ladder = [rung(anchor_row, 0)]
        current: Mapping[str, str] = anchor_row
        complete = True
        for depth, step in enumerate(ladder_steps, start=1):
            following = builder.replace_all(current, step["original"], step["replacement"])
            if following is None:
                complete = False
                break
            current = following
            ladder.append(rung(current, depth))
        if not complete:
            continue

        out_rows.extend(ladder)
        for step in ladder_steps:
            mode_counts[step["mode"]] += 1
        n_bases += 1

    output_path = context.workspace.data("progressive") / CORPUS_FILENAME
    written = corpus_io.write_rows(output_path, out_rows, output_fieldnames(schema))

    print(
        f"\nWrote {written} rows ({n_bases} base docs x {steps_wanted + 1} depths) "
        f"-> {output_path}"
    )
    print(f"  per-step mode counts: {dict(sorted(mode_counts.items()))}")
    return 0


__all__ = [
    "CORPUS_FILENAME",
    "LADDER_MODES",
    "QAC_FILENAME",
    "RUNG_ID_PREFIX",
    "TRACKING_FIELDS",
    "build_progressive",
    "output_fieldnames",
]
