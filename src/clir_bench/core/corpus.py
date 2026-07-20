"""
Corpus reading, writing and grouping.

Every stage reads corpus rows through this module and a :class:`CorpusSchema`,
so no core code names a domain column. Replaces ad-hoc ``csv.DictReader`` loops
that were re-implemented in a dozen scripts, each with its own field-size and
grouping logic.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Optional, Sequence

from clir_bench.core.domain import CorpusSchema

# Full-text fields routinely exceed the default field-size limit.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

Row = dict[str, str]


def read_rows(path: Path) -> list[Row]:
    """Read a corpus CSV into a list of dicts."""
    with Path(path).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def iter_rows(path: Path) -> Iterator[Row]:
    """Stream a corpus CSV row by row (for files too large to hold in memory)."""
    with Path(path).open(encoding="utf-8", newline="") as fh:
        yield from csv.DictReader(fh)


def write_rows(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fieldnames: Sequence[str],
    *,
    append: bool = False,
) -> int:
    """Write rows with a fixed header; returns the number written.

    Replaces the DictWriter block that was copy-pasted into every builder and
    generator. ``extrasaction="ignore"`` matches the legacy behaviour of
    tolerating extra keys on a row.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    mode = "a" if (append and exists) else "w"
    written = 0
    with path.open(mode, encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fieldnames), extrasaction="ignore")
        if mode == "w":
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
            written += 1
    return written


def ensure_header(path: Path, fieldnames: Sequence[str]) -> None:
    """Create the file with a header if missing; verify it matches if present.

    Guards the append-in-place flows: appending rows under a different schema
    silently corrupts a dataset.
    """
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=list(fieldnames)).writeheader()
        return
    with path.open(encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh), [])
    if list(header) != list(fieldnames):
        raise ValueError(
            f"{path} has an unexpected header; refusing to append.\n"
            f"  expected: {list(fieldnames)}\n  found:    {list(header)}"
        )


def group_by_family(rows: Iterable[Mapping[str, str]], schema: CorpusSchema) -> dict[str, list[Row]]:
    """Group rows by their cross-language family key (e.g. one patent, N languages)."""
    grouped: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        key = schema.family_of(row)
        if key:
            grouped[key].append(dict(row))
    return dict(grouped)


def load_grouped(path: Path, schema: CorpusSchema) -> dict[str, list[Row]]:
    return group_by_family(read_rows(path), schema)


def languages_of(rows: Sequence[Mapping[str, str]], schema: CorpusSchema) -> set[str]:
    return {schema.language_of(row) for row in rows if schema.language_of(row)}


def has_content(rows: Sequence[Mapping[str, str]], schema: CorpusSchema) -> bool:
    """True when at least one row carries usable text."""
    return any(schema.text_of(row) for row in rows)


def pick_context_row(
    rows: Sequence[Mapping[str, str]],
    schema: CorpusSchema,
    target_language: str,
    *,
    fallback_language: str = "en",
) -> Optional[Mapping[str, str]]:
    """Best row to read context from: target language, else fallback, else any."""
    by_lang = {schema.language_of(r): r for r in rows}
    for candidate in (target_language, fallback_language):
        row = by_lang.get(candidate)
        if row is not None and schema.text_of(row):
            return row
    for row in rows:
        if schema.text_of(row):
            return row
    return None


def build_passages_text(
    rows: Sequence[Mapping[str, str]],
    schema: CorpusSchema,
    *,
    order: Sequence[str] = (),
) -> str:
    """Concatenate every language version as ``[LANG] Passage: ...`` blocks.

    Generators and graders both receive all language versions of a document;
    that cross-lingual grounding is a deliberate design property of the
    pipeline, not an implementation detail.
    """
    ranked = sorted(
        rows,
        key=lambda r: (
            order.index(schema.language_of(r)) if schema.language_of(r) in order else len(order),
            schema.language_of(r),
        ),
    )
    blocks = []
    for row in ranked:
        text = schema.text_of(row)
        if text:
            blocks.append(f"[{schema.language_of(row).upper()}] Passage:\n{text}")
    return "\n\n".join(blocks)


def serialize_languages(
    rows: Sequence[Mapping[str, str]], schema: CorpusSchema, *, order: Sequence[str] = ()
) -> str:
    """Available languages as one CSV cell, preferred order first."""
    present = languages_of(rows, schema)
    ordered = [lang for lang in order if lang in present]
    ordered += sorted(present - set(ordered))
    return ",".join(ordered)


def build_context(fields: Mapping[str, str], labels: Sequence[tuple[str, str]]) -> str:
    """Assemble the ``context`` column from labelled parts.

    ``labels`` is a sequence of (field name, label) pairs, e.g.
    ``[("title", "Title"), ("abstract", "Abstract")]``. Empty parts are skipped.
    """
    parts = []
    for name, label in labels:
        value = str(fields.get(name, "") or "").strip()
        if value:
            parts.append(f"{label}: {value}")
    return "\n\n".join(parts)


def filter_multilingual(
    rows: Iterable[Mapping[str, str]],
    schema: CorpusSchema,
    *,
    languages: Sequence[str],
    min_languages: int = 2,
) -> tuple[list[Row], dict[str, object]]:
    """Keep every row of any family present in at least ``min_languages`` of ``languages``.

    The generic form of the cross-language coverage filter that produced the
    canonical multilingual corpus. Returns the kept rows and a summary.
    """
    wanted = set(languages)
    materialized = [dict(r) for r in rows]
    per_family: dict[str, set[str]] = defaultdict(set)
    for row in materialized:
        lang = schema.language_of(row)
        if lang in wanted:
            per_family[schema.family_of(row)].add(lang)

    keep = {fam for fam, langs in per_family.items() if len(langs) >= min_languages}
    kept = [r for r in materialized if schema.family_of(r) in keep]

    coverage: dict[int, int] = defaultdict(int)
    for fam in keep:
        coverage[len(per_family[fam])] += 1
    per_language: dict[str, int] = defaultdict(int)
    for row in kept:
        per_language[schema.language_of(row)] += 1

    return kept, {
        "families_total": len(per_family),
        "families_kept": len(keep),
        "rows_kept": len(kept),
        "per_language": dict(sorted(per_language.items())),
        "coverage_distribution": dict(sorted(coverage.items())),
    }


def count_rows(path: Path) -> int:
    """Data rows in a CSV (header excluded); 0 when the file is missing.

    Parses rather than counting lines: document text routinely contains
    newlines inside quoted fields, so a line count overstates the row count --
    for this project's corpora, by roughly a factor of three.
    """
    path = Path(path)
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        next(reader, None)  # header
        return sum(1 for _ in reader)


__all__ = [
    "Row",
    "build_context",
    "build_passages_text",
    "count_rows",
    "ensure_header",
    "filter_multilingual",
    "group_by_family",
    "has_content",
    "iter_rows",
    "languages_of",
    "load_grouped",
    "pick_context_row",
    "read_rows",
    "serialize_languages",
    "write_rows",
]
