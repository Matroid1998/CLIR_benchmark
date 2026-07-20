"""
Question-generation plans.

A plan decides *which* documents get asked about, in which languages and modes.
That is the part that changed every time a dataset was extended, so it is
separated from the engine that does the asking.

Three plans cover every build this project has done:

``balanced``   the initial dataset: a sampled pool, split evenly across modes
               and language-selection strategies.
``uniform``    a second source with fewer languages (the EPO build): uniform
               sampling over uncovered documents, strategies split evenly.
``coverage``   filling a specific gap: prioritizes documents that exist in
               named languages, which is how Chinese and Spanish coverage was
               raised without regenerating the whole set.

Every plan is reproducible from its seed, and every plan can exclude documents
already covered by an existing dataset so a build can be resumed or extended
rather than restarted.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.domain import SourceSpec
from clir_bench.core.qagen import (
    STRATEGY_ALL,
    STRATEGY_NAMES,
    STRATEGY_RANDOM_ANY,
    STRATEGY_RANDOM_EXISTING,
    STRATEGY_RANDOM_MISSING,
    PlanItem,
    allocate_quotas,
    pick_target_languages,
)
from clir_bench.domains.chem_patents import vocabulary as vocab

STRATEGIES = (
    STRATEGY_RANDOM_ANY,
    STRATEGY_RANDOM_MISSING,
    STRATEGY_RANDOM_EXISTING,
    STRATEGY_ALL,
)


def _excluded_families(path: Optional[Path], family_field: str) -> set[str]:
    """Families already covered by an existing dataset."""
    if not path:
        return set()
    path = Path(path)
    if not path.exists():
        return set()
    return {
        str(row.get(family_field, "")).strip()
        for row in corpus_io.read_rows(path)
        if str(row.get(family_field, "")).strip()
    }


def _eligible(
    grouped: Mapping[str, Sequence[Mapping[str, str]]],
    context: AppContext,
    excluded: set[str],
) -> list[str]:
    """Families with usable text that are not already covered, in a stable order."""
    schema = context.schema
    return sorted(
        family
        for family, rows in grouped.items()
        if family and family not in excluded and corpus_io.has_content(rows, schema)
    )


def _languages(args: argparse.Namespace, context: AppContext, source: SourceSpec) -> list[str]:
    """Question languages: explicit flag, else the source's, else the domain's."""
    requested = getattr(args, "langs", None)
    if requested:
        return list(requested)
    return list(source.languages or context.languages.working)


def _modes(args: argparse.Namespace) -> list[str]:
    requested = getattr(args, "modes", None)
    return list(requested) if requested else list(vocab.MODES)


def _items_for_family(
    family: str,
    rows: Sequence[Mapping[str, str]],
    *,
    context: AppContext,
    strategy: int,
    mode: str,
    languages: Sequence[str],
    rng: random.Random,
) -> list[PlanItem]:
    """Expand one document into plan items.

    ``STRATEGY_ALL`` produces one question per language; the others produce one.
    """
    available = sorted(corpus_io.languages_of(rows, context.schema))
    targets = pick_target_languages(strategy, available, languages, rng=rng)
    return [
        PlanItem(
            family=family,
            language=language,
            mode=mode,
            strategy=strategy,
            metadata={"strategy_name": STRATEGY_NAMES.get(strategy, "")},
        )
        for language in targets
    ]


def balanced_plan(
    *,
    context: AppContext,
    source: SourceSpec,
    grouped: Mapping[str, Sequence[Mapping[str, str]]],
    args: argparse.Namespace,
) -> list[PlanItem]:
    """Even coverage across modes and strategies over a sampled pool."""
    rng = random.Random(args.seed)
    languages = _languages(args, context, source)
    modes = _modes(args)
    excluded = _excluded_families(getattr(args, "exclude_from", None), context.schema.family_field)
    eligible = _eligible(grouped, context, excluded)
    if not eligible:
        return []

    pool_size = getattr(args, "pool", None) or min(len(eligible), max(args.questions * len(modes), 1))
    pool = rng.sample(eligible, min(pool_size, len(eligible)))

    items: list[PlanItem] = []
    cursor = 0
    for mode in modes:
        quotas = allocate_quotas(args.questions, STRATEGIES)
        for strategy, quota in quotas.items():
            # STRATEGY_ALL asks in every language, so it needs fewer documents.
            documents = max(1, quota // len(languages)) if strategy == STRATEGY_ALL else quota
            for _ in range(documents):
                if not pool:
                    break
                family = pool[cursor % len(pool)]
                cursor += 1
                items.extend(
                    _items_for_family(
                        family,
                        grouped[family],
                        context=context,
                        strategy=strategy,
                        mode=mode,
                        languages=languages,
                        rng=rng,
                    )
                )
    return items


def uniform_plan(
    *,
    context: AppContext,
    source: SourceSpec,
    grouped: Mapping[str, Sequence[Mapping[str, str]]],
    args: argparse.Namespace,
) -> list[PlanItem]:
    """Uniform sampling over uncovered documents, strategies split evenly.

    Used for a source whose language set differs from the main one; the quota
    split accounts for the language count rather than assuming five.
    """
    rng = random.Random(args.seed)
    languages = _languages(args, context, source)
    modes = _modes(args)
    excluded = _excluded_families(getattr(args, "exclude_from", None), context.schema.family_field)
    eligible = _eligible(grouped, context, excluded)
    if not eligible:
        return []

    rng.shuffle(eligible)
    items: list[PlanItem] = []
    cursor = 0
    for mode in modes:
        for strategy, quota in allocate_quotas(args.questions, STRATEGIES).items():
            documents = max(1, quota // len(languages)) if strategy == STRATEGY_ALL else quota
            for _ in range(documents):
                if cursor >= len(eligible):
                    cursor = 0
                family = eligible[cursor]
                cursor += 1
                items.extend(
                    _items_for_family(
                        family,
                        grouped[family],
                        context=context,
                        strategy=strategy,
                        mode=mode,
                        languages=languages,
                        rng=rng,
                    )
                )
    return items


def coverage_plan(
    *,
    context: AppContext,
    source: SourceSpec,
    grouped: Mapping[str, Sequence[Mapping[str, str]]],
    args: argparse.Namespace,
) -> list[PlanItem]:
    """Fill a language gap by preferring documents that exist in named languages.

    ``--priority-langs zh es`` draws documents that have those versions first,
    so questions land where coverage is thin instead of being spread uniformly.
    """
    rng = random.Random(args.seed)
    languages = _languages(args, context, source)
    modes = _modes(args)
    schema = context.schema
    excluded = _excluded_families(getattr(args, "exclude_from", None), schema.family_field)
    eligible = _eligible(grouped, context, excluded)
    if not eligible:
        return []

    priority = list(getattr(args, "priority_langs", None) or ())
    buckets: list[list[str]] = []
    claimed: set[str] = set()
    for language in priority:
        bucket = [
            family
            for family in eligible
            if family not in claimed and language in corpus_io.languages_of(grouped[family], schema)
        ]
        rng.shuffle(bucket)
        claimed.update(bucket)
        buckets.append(bucket)
    rest = [family for family in eligible if family not in claimed]
    rng.shuffle(rest)
    buckets.append(rest)

    ordered = [family for bucket in buckets for family in bucket]
    items: list[PlanItem] = []
    cursor = 0
    for mode in modes:
        for strategy, quota in allocate_quotas(args.questions, STRATEGIES).items():
            documents = max(1, quota // len(languages)) if strategy == STRATEGY_ALL else quota
            for _ in range(documents):
                if cursor >= len(ordered):
                    cursor = 0
                family = ordered[cursor]
                cursor += 1
                items.extend(
                    _items_for_family(
                        family,
                        grouped[family],
                        context=context,
                        strategy=strategy,
                        mode=mode,
                        languages=languages,
                        rng=rng,
                    )
                )
    return items


PLANS: Mapping[str, Callable[..., list[PlanItem]]] = {
    "balanced": balanced_plan,
    "uniform": uniform_plan,
    "coverage": coverage_plan,
}


__all__ = ["PLANS", "STRATEGIES", "balanced_plan", "coverage_plan", "uniform_plan"]
