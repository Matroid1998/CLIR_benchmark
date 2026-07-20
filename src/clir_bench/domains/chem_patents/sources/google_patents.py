"""
Google Patents Public Data (BigQuery) source.

Three stages, each resumable on its own: a BigQuery extraction into NDJSON, a
per-language preprocessing pass into one CSV per language, and a merge that
applies the cross-language coverage filter and writes the corpus.

The stages are separate files on disk rather than one in-memory pipeline because
the first one costs money: a BigQuery scan of
``patents-public-data.patents.publications`` is billed per byte read, so the raw
NDJSON is treated as an expensive artefact to be reused, and every rebuild past
that point works offline from it.

Tables used:
  - ``patents-public-data.patents.publications``     (documents, localized fields)
  - ``patents-public-data.ebi_surechembl.match``     (chemical-annotation signal)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.text import clean_text_simple, word_count
from clir_bench.domains.chem_patents.schema import CONTEXT_LABELS, SCHEMA
from clir_bench.domains.chem_patents.vocabulary import (
    EXTRACTION_LANGUAGES,
    FIRST_CLAIM_MAX_CHARS,
    GP_CPC_PREFIXES,
    GP_IPC_PREFIXES,
    MIN_ABSTRACT_CHARS,
    MIN_ABSTRACT_WORDS,
    # Referenced only by the disabled localized-description filters below, which
    # are kept as commented SQL together with the reason they are off.
    MIN_DESCRIPTION_CHARS,  # noqa: F401
)

Record = dict[str, Any]

# BigQuery credentials come from the environment (gcloud ADC or a service
# account); only the billing project has to be named.
PROJECT_ENV_VAR = "GOOGLE_CLOUD_PROJECT"

# Fields BigQuery returns as repeated RECORDs, which need JSON serialization
# before they can be written to NDJSON.
RECORD_KEYS = (
    "title_localized",
    "abstract_localized",
    "description_localized",
    "description_localized_html",
    "claims_localized",
    "claims_localized_html",
    "cpc",
    "ipc",
)

# The top-N-per-language query ranks by publication date, but preprocessing
# rejects documents again on a word count the SQL can only approximate, so the
# query asks for more than the target and lets the gate take the difference.
PER_LANGUAGE_OVERFETCH_FACTOR = 1.25
PER_LANGUAGE_OVERFETCH_MIN = 10


# --------------------------------------------------------------------------- #
# SQL
# --------------------------------------------------------------------------- #

def sql_list(values: Sequence[str]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def min_abstract_chars_for_sql(min_words: int) -> int:
    """Approximate a word-count gate with a cheaper character-count gate.

    BigQuery cannot cheaply count words across a repeated record, so the SQL
    filters on characters and preprocessing applies the real word gate. Five
    characters per word is deliberately generous: over-fetching costs a little
    scan, under-fetching silently drops usable documents.
    """
    return max(MIN_ABSTRACT_CHARS, min_words * 5)


def build_query(
    *,
    languages: Optional[Sequence[str]] = None,
    cpc_prefixes: Optional[Sequence[str]] = None,
    ipc_prefixes: Optional[Sequence[str]] = None,
    use_surechembl: bool = True,
    use_classification: bool = True,
    require_multilingual: bool = False,
    min_language_count: int = 2,
    limit: Optional[int] = None,
    primary_lang: Optional[str] = None,
    min_primary_abstract_words: Optional[int] = None,
    require_primary_description: bool = False,
    require_primary_claim: bool = False,
    require_any_claim: bool = False,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    country_codes: Optional[Sequence[str]] = None,
) -> str:
    """Build BigQuery SQL for chemistry-related multilingual patents."""
    languages = languages or EXTRACTION_LANGUAGES
    cpc_prefixes = cpc_prefixes or GP_CPC_PREFIXES
    ipc_prefixes = ipc_prefixes or GP_IPC_PREFIXES

    if not use_surechembl and not use_classification:
        raise ValueError("At least one of use_surechembl or use_classification must be True.")

    lang_sql = sql_list(languages)

    date_filter = ""
    if start_date is not None:
        date_filter += f"\n  AND p.publication_date >= {start_date}"
    if end_date is not None:
        date_filter += f"\n  AND p.publication_date <= {end_date}"

    country_filter = ""
    if country_codes:
        cc_sql = sql_list(country_codes)
        country_filter = f"\n  AND p.country_code IN ({cc_sql})"

    # Chemistry is a disjunction, not a conjunction: a CPC prefix, an IPC prefix
    # or a SureChemBL chemical annotation each qualify a document on their own.
    chemistry_predicates: list[str] = []

    if use_classification:
        cpc_preds = " OR ".join(f"STARTS_WITH(c.code, {p!r})" for p in cpc_prefixes)
        ipc_preds = " OR ".join(f"STARTS_WITH(i.code, {p!r})" for p in ipc_prefixes)
        chemistry_predicates.append(
            f"""
            EXISTS (
              SELECT 1
              FROM UNNEST(IFNULL(p.cpc, [])) AS c
              WHERE {cpc_preds}
            )
            """
        )
        chemistry_predicates.append(
            f"""
            EXISTS (
              SELECT 1
              FROM UNNEST(IFNULL(p.ipc, [])) AS i
              WHERE {ipc_preds}
            )
            """
        )

    surechembl_join = ""
    if use_surechembl:
        surechembl_join = """
        LEFT JOIN (
          SELECT DISTINCT publication_number
          FROM `patents-public-data.ebi_surechembl.match`
        ) sc
        ON p.publication_number = sc.publication_number
        """
        chemistry_predicates.append("sc.publication_number IS NOT NULL")

    chemistry_where = " OR ".join(f"({p.strip()})" for p in chemistry_predicates)

    # Filter to patents that have a usable localized abstract for primary_lang
    # before limiting. This lets per-language extraction target documents that
    # are likely to survive later preprocessing.
    primary_lang_filter = ""
    if primary_lang:
        pl = primary_lang.strip().lower()
        min_chars_filter = ""
        if min_primary_abstract_words:
            min_chars_filter = f"""
              AND LENGTH(TRIM(a.text)) >= {min_abstract_chars_for_sql(int(min_primary_abstract_words))}
            """
        description_filter = ""
        if require_primary_description:
            # Disabled for now: many non-English patents in BigQuery have a
            # localized abstract but no localized description.
            # description_filter = f"""
            # AND EXISTS (
            #   SELECT 1
            #   FROM UNNEST(IFNULL(p.description_localized, [])) d
            #   WHERE LOWER(COALESCE(d.language, '')) = {pl!r}
            #     AND d.text IS NOT NULL
            #     AND LENGTH(TRIM(d.text)) >= {MIN_DESCRIPTION_CHARS}
            # )
            # """
            pass
        claim_filter = ""
        if require_primary_claim:
            claim_filter = f"""
        AND (
          EXISTS (
            SELECT 1
            FROM UNNEST(IFNULL(p.claims_localized, [])) c
            WHERE LOWER(COALESCE(c.language, '')) = {pl!r}
              AND c.text IS NOT NULL
              AND LENGTH(TRIM(c.text)) > 0
          )
          OR EXISTS (
            SELECT 1
            FROM UNNEST(IFNULL(p.claims_localized_html, [])) c
            WHERE LOWER(COALESCE(c.language, '')) = {pl!r}
              AND c.text IS NOT NULL
              AND LENGTH(TRIM(c.text)) > 0
          )
        )
            """
        primary_lang_filter = f"""
        AND EXISTS (
          SELECT 1
          FROM UNNEST(IFNULL(p.abstract_localized, [])) a
          WHERE LOWER(COALESCE(a.language, '')) = {pl!r}
            AND a.text IS NOT NULL
            AND LENGTH(TRIM(a.text)) > 0
            {min_chars_filter}
        )
        {description_filter}
        {claim_filter}
        """

    any_claim_filter = ""
    if require_any_claim and not primary_lang:
        any_claim_filter = """
        AND (
          EXISTS (
            SELECT 1
            FROM UNNEST(IFNULL(p.claims_localized, [])) c
            WHERE c.text IS NOT NULL
              AND LENGTH(TRIM(c.text)) > 0
          )
          OR EXISTS (
            SELECT 1
            FROM UNNEST(IFNULL(p.claims_localized_html, [])) c
            WHERE c.text IS NOT NULL
              AND LENGTH(TRIM(c.text)) > 0
          )
        )
        """

    multilingual_having = ""
    if require_multilingual:
        multilingual_having = f"HAVING ARRAY_LENGTH(languages_present) >= {min_language_count}"

    limit_clause = f"\nLIMIT {limit}" if limit else ""

    query = f"""
    WITH base AS (
      SELECT
        p.publication_number,
        p.family_id,
        p.country_code,
        p.publication_date,
        p.title_localized,
        p.abstract_localized,
        p.description_localized,
        p.description_localized_html,
        p.claims_localized,
        p.claims_localized_html,
        p.cpc,
        p.ipc,

        ARRAY(
          SELECT DISTINCT t.language
          FROM UNNEST(IFNULL(p.title_localized, [])) t
          WHERE t.language IN ({lang_sql}) AND t.text IS NOT NULL
          UNION DISTINCT
          SELECT DISTINCT a.language
          FROM UNNEST(IFNULL(p.abstract_localized, [])) a
          WHERE a.language IN ({lang_sql}) AND a.text IS NOT NULL
        ) AS languages_present
      FROM `patents-public-data.patents.publications` p
      {surechembl_join}
      WHERE
        ({chemistry_where})
        {primary_lang_filter}
        {any_claim_filter}
        {date_filter}
        {country_filter}
    )
    SELECT *
    FROM base
    {multilingual_having}
    ORDER BY publication_date DESC
    {limit_clause}
    """
    return query


def build_query_per_language_top_n(
    *,
    languages: Optional[Sequence[str]] = None,
    limit_per_lang: int,
    cpc_prefixes: Optional[Sequence[str]] = None,
    ipc_prefixes: Optional[Sequence[str]] = None,
    use_surechembl: bool = True,
    use_classification: bool = True,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    country_codes: Optional[Sequence[str]] = None,
    min_abstract_words: int = MIN_ABSTRACT_WORDS,
    require_description: bool = False,
    require_claim: bool = False,
) -> str:
    """Build one top-N-per-language query for cheaper extraction.

    One windowed scan covers every language at once. The naive alternative --
    one query per language -- rescans the same large public tables sixteen times
    and is the dominant BigQuery cost in this pipeline.
    """
    languages = languages or EXTRACTION_LANGUAGES
    cpc_prefixes = cpc_prefixes or GP_CPC_PREFIXES
    ipc_prefixes = ipc_prefixes or GP_IPC_PREFIXES

    if not use_surechembl and not use_classification:
        raise ValueError("At least one of use_surechembl or use_classification must be True.")

    lang_array_sql = ", ".join(f"'{lang}'" for lang in languages)

    date_filter = ""
    if start_date is not None:
        date_filter += f"\n      AND p.publication_date >= {start_date}"
    if end_date is not None:
        date_filter += f"\n      AND p.publication_date <= {end_date}"

    country_filter = ""
    if country_codes:
        cc_sql = sql_list(country_codes)
        country_filter = f"\n      AND p.country_code IN ({cc_sql})"

    chemistry_predicates: list[str] = []
    if use_classification:
        cpc_preds = " OR ".join(f"STARTS_WITH(c.code, {p!r})" for p in cpc_prefixes)
        ipc_preds = " OR ".join(f"STARTS_WITH(i.code, {p!r})" for p in ipc_prefixes)
        chemistry_predicates.append(
            f"""
            EXISTS (
              SELECT 1
              FROM UNNEST(IFNULL(p.cpc, [])) AS c
              WHERE {cpc_preds}
            )
            """
        )
        chemistry_predicates.append(
            f"""
            EXISTS (
              SELECT 1
              FROM UNNEST(IFNULL(p.ipc, [])) AS i
              WHERE {ipc_preds}
            )
            """
        )

    surechembl_join = ""
    if use_surechembl:
        surechembl_join = """
        LEFT JOIN (
          SELECT DISTINCT publication_number
          FROM `patents-public-data.ebi_surechembl.match`
        ) sc
        ON p.publication_number = sc.publication_number
        """
        chemistry_predicates.append("sc.publication_number IS NOT NULL")

    chemistry_where = " OR ".join(f"({p.strip()})" for p in chemistry_predicates)
    min_abstract_chars = min_abstract_chars_for_sql(min_abstract_words)
    description_clause = ""
    if require_description:
        # Disabled for now: requiring localized descriptions collapses
        # multilingual coverage in the public BigQuery table.
        # description_clause = f"""
        # AND EXISTS (
        #   SELECT 1
        #   FROM UNNEST(IFNULL(b.description_localized, [])) d
        #   WHERE LOWER(COALESCE(d.language, '')) = lang
        #     AND d.text IS NOT NULL
        #     AND LENGTH(TRIM(d.text)) >= {MIN_DESCRIPTION_CHARS}
        # )
        # """
        pass

    claim_clause = ""
    if require_claim:
        claim_clause = """
      AND (
        EXISTS (
          SELECT 1
          FROM UNNEST(IFNULL(b.claims_localized, [])) c
          WHERE LOWER(COALESCE(c.language, '')) = lang
            AND c.text IS NOT NULL
            AND LENGTH(TRIM(c.text)) > 0
        )
        OR EXISTS (
          SELECT 1
          FROM UNNEST(IFNULL(b.claims_localized_html, [])) c
          WHERE LOWER(COALESCE(c.language, '')) = lang
            AND c.text IS NOT NULL
            AND LENGTH(TRIM(c.text)) > 0
        )
      )
        """

    return f"""
    WITH base AS (
      SELECT
        p.publication_number,
        p.family_id,
        p.country_code,
        p.publication_date,
        p.title_localized,
        p.abstract_localized,
        p.description_localized,
        p.description_localized_html,
        p.claims_localized,
        p.claims_localized_html,
        p.cpc,
        p.ipc
      FROM `patents-public-data.patents.publications` p
      {surechembl_join}
      WHERE
        ({chemistry_where})
        {date_filter}
        {country_filter}
    ),
    ranked AS (
      SELECT
        b.publication_number,
        lang,
        ROW_NUMBER() OVER (
          PARTITION BY lang
          ORDER BY b.publication_date DESC, b.publication_number DESC
        ) AS rn
      FROM base b
      CROSS JOIN UNNEST([{lang_array_sql}]) AS lang
      WHERE EXISTS (
        SELECT 1
        FROM UNNEST(IFNULL(b.abstract_localized, [])) a
        WHERE LOWER(COALESCE(a.language, '')) = lang
          AND a.text IS NOT NULL
          AND LENGTH(TRIM(a.text)) >= {min_abstract_chars}
      )
      {description_clause}
      {claim_clause}
    ),
    selected AS (
      SELECT DISTINCT publication_number
      FROM ranked
      WHERE rn <= {limit_per_lang}
    )
    SELECT
      b.publication_number,
      b.family_id,
      b.country_code,
      b.publication_date,
      b.title_localized,
      b.abstract_localized,
      b.description_localized,
      b.description_localized_html,
      b.claims_localized,
      b.claims_localized_html,
      b.cpc,
      b.ipc
    FROM base b
    INNER JOIN selected s
      USING (publication_number)
    ORDER BY b.publication_date DESC, b.publication_number DESC
    """


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #

def _serialize_record(obj: Any) -> Any:
    """Convert BigQuery row values to JSON-serializable Python types."""
    return json.loads(json.dumps(obj, default=str))


def _run_query_iter(project_id: str, query: str, *, page_size: int = 1000) -> Iterator[Record]:
    from google.cloud import bigquery

    client = bigquery.Client(project=project_id)
    job_config = bigquery.QueryJobConfig(use_legacy_sql=False)
    query_job = client.query(query, job_config=job_config)
    result = query_job.result(page_size=page_size)

    for row in result:
        record: Record = dict(row.items())
        for key in RECORD_KEYS:
            if key in record and record[key] is not None:
                record[key] = _serialize_record(record[key])
        yield record


def run_query(project_id: str, query: str, output_path: Path, *, page_size: int = 1000) -> int:
    """Run a query and stream the results to NDJSON; returns rows written."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8") as fh:
        for record in _run_query_iter(project_id, query, page_size=page_size):
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            if count % 1000 == 0:
                print(f"Wrote {count:,} rows...")
    print(f"Done. Wrote {count:,} rows to: {output_path}")
    return count


def extract(
    project_id: str,
    output_path: Path,
    *,
    languages: Optional[Sequence[str]] = None,
    cpc_prefixes: Optional[Sequence[str]] = None,
    ipc_prefixes: Optional[Sequence[str]] = None,
    use_surechembl: bool = True,
    use_classification: bool = True,
    require_multilingual: bool = False,
    min_language_count: int = 2,
    limit: Optional[int] = None,
    primary_lang: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    country_codes: Optional[Sequence[str]] = None,
) -> int:
    """Extract chemistry-related multilingual patents into NDJSON."""
    query = build_query(
        languages=languages,
        cpc_prefixes=cpc_prefixes,
        ipc_prefixes=ipc_prefixes,
        use_surechembl=use_surechembl,
        use_classification=use_classification,
        require_multilingual=require_multilingual,
        min_language_count=min_language_count,
        limit=limit,
        primary_lang=primary_lang,
        min_primary_abstract_words=MIN_ABSTRACT_WORDS if primary_lang else None,
        require_primary_description=False,
        require_primary_claim=False,
        require_any_claim=False,
        start_date=start_date,
        end_date=end_date,
        country_codes=country_codes,
    )
    return run_query(project_id=project_id, query=query, output_path=Path(output_path))


def extract_per_language(
    project_id: str,
    output_path: Path,
    *,
    languages: Optional[Sequence[str]] = None,
    limit_per_lang: int = 100,
    cpc_prefixes: Optional[Sequence[str]] = None,
    ipc_prefixes: Optional[Sequence[str]] = None,
    use_surechembl: bool = True,
    use_classification: bool = True,
) -> int:
    """Pull one shared document set covering up to ``limit_per_lang`` per language."""
    languages = languages or EXTRACTION_LANGUAGES
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fetch_limit = max(
        limit_per_lang + PER_LANGUAGE_OVERFETCH_MIN,
        int(limit_per_lang * PER_LANGUAGE_OVERFETCH_FACTOR),
    )
    query = build_query_per_language_top_n(
        languages=languages,
        limit_per_lang=fetch_limit,
        cpc_prefixes=cpc_prefixes,
        ipc_prefixes=ipc_prefixes,
        use_surechembl=use_surechembl,
        use_classification=use_classification,
        min_abstract_words=MIN_ABSTRACT_WORDS,
        require_description=False,
        require_claim=False,
    )
    print(
        f"Running one top-N-per-language query for {len(languages)} languages "
        f"(target {limit_per_lang}, fetch {fetch_limit} per language)."
    )
    return run_query(project_id=project_id, query=query, output_path=output_path)


# --------------------------------------------------------------------------- #
# Preprocessing
# --------------------------------------------------------------------------- #

def _localized_text(items: Optional[Sequence[Mapping[str, Any]]], language: str) -> Optional[str]:
    """Text for one language out of a ``*_localized`` repeated record."""
    if not items:
        return None
    for item in items:
        if isinstance(item, dict):
            if (item.get("language") or "").lower() == language.lower():
                text = item.get("text")
                if text and text.strip():
                    return text.strip()
    return None


def _truncate(text: str, *, max_chars: int) -> str:
    """Trim to ``max_chars`` on a word boundary, without an ellipsis marker.

    Deliberately not ``core.text.truncate_text``: that one appends "..." and
    only backs off to a word boundary within the last 20% of the budget. Claims
    in the published corpus were cut with these rules, so changing them would
    silently rewrite existing documents.
    """
    text = clean_text_simple(text)
    if len(text) <= max_chars:
        return text
    snippet = text[:max_chars].rsplit(" ", 1)[0].strip()
    return snippet or text[:max_chars].strip()


def _normalize_claim_text(text: str) -> str:
    """Normalize parsed claim text and drop the leading claim number."""
    text = clean_text_simple(text)
    text = re.sub(r"^\s*1\s*[\.\):\-]*\s*", "", text)
    return text.strip()


def _first_claim_from_html(claim_html: str) -> str:
    """Parse the first claim out of ``claims_localized_html``.

    ``<chemistry>`` blocks are dropped rather than flattened: they hold MOL/CDX
    payloads that would otherwise land in the retrievable text as noise.
    """
    match = re.search(r"<claim\b[^>]*>(.*?)</claim>", claim_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""

    claim_block = re.sub(
        r"<chemistry\b.*?</chemistry>", " ", match.group(1), flags=re.IGNORECASE | re.DOTALL
    )
    claim_block = re.sub(r"</?claim-text\b[^>]*>", " ", claim_block, flags=re.IGNORECASE)
    claim_block = re.sub(r"<[^>]+>", " ", claim_block)
    return _normalize_claim_text(claim_block)


def _first_claim_from_text(claim_text: str) -> str:
    """Parse the first claim out of plain ``claims_localized``."""
    cleaned = clean_text_simple(claim_text)
    if not cleaned:
        return ""

    cleaned = re.sub(r"^\s*1\s*[\.\):\-]*\s*", "", cleaned)
    next_claim = re.search(r"\s2\s*[\.\):\-]\s+", cleaned)
    if next_claim:
        cleaned = cleaned[: next_claim.start()]
    return _normalize_claim_text(cleaned)


def build_first_claim(
    claim_items: Optional[Sequence[Mapping[str, Any]]],
    claim_html_items: Optional[Sequence[Mapping[str, Any]]],
    language: str,
    *,
    max_chars: int = FIRST_CLAIM_MAX_CHARS,
) -> str:
    """First localized claim, preferring the HTML variant.

    HTML first because it carries explicit ``<claim>`` boundaries; the plain
    variant has to guess where claim 1 ends by looking for claim 2's number,
    which fails on documents that number claims unusually.
    """
    claim_html = _localized_text(claim_html_items, language)
    if claim_html:
        first_claim = _first_claim_from_html(claim_html)
        if first_claim:
            return _truncate(first_claim, max_chars=max_chars)

    claim_text = _localized_text(claim_items, language)
    if claim_text:
        first_claim = _first_claim_from_text(claim_text)
        if first_claim:
            return _truncate(first_claim, max_chars=max_chars)

    return ""


def load_records(ndjson_path: Path) -> list[Record]:
    """Read the raw NDJSON into memory (one extraction is a few hundred MB)."""
    records: list[Record] = []
    with Path(ndjson_path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_language_rows(
    records: Sequence[Record],
    language: str,
    *,
    per_lang_limit: Optional[int] = None,
    min_abstract_words: int = MIN_ABSTRACT_WORDS,
    source_value: str = "google_patents",
) -> tuple[list[corpus_io.Row], dict[str, int]]:
    """Corpus rows for one language, plus the counts of what was rejected."""
    rows: list[corpus_io.Row] = []
    seen_publications: set[str] = set()
    skipped_short = 0
    missing_claim = 0

    for record in records:
        title = _localized_text(record.get("title_localized"), language)
        abstract = _localized_text(record.get("abstract_localized"), language)
        # Left blank by design. BigQuery's localized descriptions exist for far
        # fewer languages than its abstracts, so including them would bias the
        # corpus toward the languages that happen to have them, and their length
        # would dominate the retrievable text. The column stays for schema
        # stability with the EPO corpus, which does carry descriptions.
        description = ""
        first_claim = build_first_claim(
            record.get("claims_localized"),
            record.get("claims_localized_html"),
            language,
        )

        if not abstract and not title:
            continue

        publication_number = record.get("publication_number") or ""
        if publication_number in seen_publications:
            continue
        seen_publications.add(publication_number)

        title = clean_text_simple(title or "")
        abstract = clean_text_simple(abstract or "")
        if word_count(abstract) < min_abstract_words:
            skipped_short += 1
            continue
        if not first_claim:
            missing_claim += 1

        fields = {"title": title, "abstract": abstract, "first_claim": first_claim}
        ipc_codes = "|".join(
            code
            for entry in (record.get("ipc") or [])
            if (code := (entry.get("code") or "").strip())
        )

        rows.append(
            {
                "id": SCHEMA.make_doc_id(publication_number, language),
                "language": language,
                "title": title,
                "abstract": abstract,
                "description": description,
                "first_claim": first_claim,
                "context": corpus_io.build_context(fields, CONTEXT_LABELS),
                "publication_number": publication_number,
                "country_code": record.get("country_code") or "",
                "publication_date": record.get("publication_date") or "",
                "source": source_value,
                "ipc_codes": ipc_codes,
            }
        )

        # The cap counts kept rows, not scanned records, which is why the
        # extraction over-fetches: rejects here must not eat into the target.
        if per_lang_limit and len(rows) >= per_lang_limit:
            break

    return rows, {"skipped_short": skipped_short, "missing_claim": missing_claim}


def preprocess_ndjson(
    ndjson_path: Path,
    output_dir: Path,
    *,
    languages: Optional[Sequence[str]] = None,
    per_lang_limit: Optional[int] = None,
    min_abstract_words: int = MIN_ABSTRACT_WORDS,
    source_value: str = "google_patents",
) -> dict[str, int]:
    """Write one CSV per language; returns language -> row count."""
    languages = languages or EXTRACTION_LANGUAGES
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = load_records(ndjson_path)

    counts: dict[str, int] = {}
    for language in languages:
        rows, stats = build_language_rows(
            records,
            language,
            per_lang_limit=per_lang_limit,
            min_abstract_words=min_abstract_words,
            source_value=source_value,
        )
        out_path = output_dir / f"{language}.csv"
        corpus_io.write_rows(out_path, rows, SCHEMA.fields)
        counts[language] = len(rows)
        _report_language(language, len(rows), out_path, stats)
    return counts


def _report_language(language: str, count: int, path: Path, stats: Mapping[str, int]) -> None:
    print(
        f"  {language}: {count:,} rows -> {path}"
        f" (skipped {stats['skipped_short']:,} short/title-only records,"
        f" {stats['missing_claim']:,} without claims)"
    )


# --------------------------------------------------------------------------- #
# Merge
# --------------------------------------------------------------------------- #

def merge_preprocessed(
    preprocessed_dir: Path,
    *,
    languages: Optional[Sequence[str]] = None,
    min_abstract_words: int = MIN_ABSTRACT_WORDS,
) -> list[corpus_io.Row]:
    """Concatenate the per-language CSVs, re-cleaning and re-gating each row.

    The gates run again here rather than being trusted from preprocessing: these
    files are edited and regenerated by hand during dataset work, and the merge
    is the last point where a malformed row can be caught before it reaches the
    corpus.

    ``context`` is reassembled from the cleaned parts instead of being cleaned in
    place. The old merge ran the whitespace collapse over the stored context too,
    which flattened its blank-line separators into single spaces -- but the
    published corpus was filtered straight out of these per-language CSVs and so
    kept the separators. Reassembling reproduces the published text exactly and
    is a no-op on every row of the current corpus.
    """
    preprocessed_dir = Path(preprocessed_dir)
    languages = languages or EXTRACTION_LANGUAGES

    rows: list[corpus_io.Row] = []
    for language in languages:
        path = preprocessed_dir / f"{language}.csv"
        if not path.exists():
            continue
        for row in corpus_io.iter_rows(path):
            for name in ("title", "abstract", "description", "first_claim"):
                row[name] = clean_text_simple(row.get(name, ""))
            row["ipc_codes"] = row.get("ipc_codes", "")
            if word_count(row["abstract"]) < min_abstract_words:
                continue
            row["context"] = corpus_io.build_context(row, CONTEXT_LABELS)
            rows.append(row)
    return rows


# --------------------------------------------------------------------------- #
# Ingest command
# --------------------------------------------------------------------------- #

def _ask(prompt: str, default: str = "n") -> str:
    """First letter of the answer, or ``default`` when there is nobody to ask."""
    if not sys.stdin or not sys.stdin.isatty():
        return default
    choice = input(prompt).strip().lower() or default
    return choice[0] if choice else default


def _count_lines(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open(encoding="utf-8") as fh:
        return sum(1 for _ in fh)


def ingest(context: AppContext, args: argparse.Namespace) -> int:
    """Run the extract -> preprocess -> merge stages, reusing what already exists.

    Each stage asks before overwriting its output, because the stages have very
    different costs: re-extracting means paying BigQuery again, while rebuilding
    the corpus is seconds of local work. ``--yes`` rebuilds everything.
    """
    source = context.domain.source("gp")
    workspace = context.workspace
    raw_path = workspace.data("gp_raw")
    preprocessed_dir = workspace.data("gp_preprocessed")
    corpus_path = workspace.data("gp_corpus")

    requested = tuple(getattr(args, "languages", None) or ())
    # Extraction and preprocessing cast the wide net (the full inventory) so the
    # per-language CSVs stay available for later work, but the corpus is built
    # from the source's working languages only: those are the ones with enough
    # parallel coverage, and they are exactly what the published corpus contains.
    extract_languages = requested or context.languages.inventory
    corpus_languages = requested or source.languages
    limit = getattr(args, "limit", None)
    assume_yes = bool(getattr(args, "yes", False))

    run_extract = not getattr(args, "skip_extract", False)
    if run_extract and raw_path.exists() and not assume_yes:
        run_extract = (
            _ask(
                f"Raw data already exists ({_count_lines(raw_path):,} records). "
                "Query BigQuery again and overwrite it? "
                "(y = re-extract, n = reuse existing raw data): "
            )
            == "y"
        )

    if run_extract:
        project_id = os.environ.get(PROJECT_ENV_VAR) or str(context.setting("gcp_project", "") or "")
        if not project_id:
            print(f"Error: set {PROJECT_ENV_VAR} (or 'gcp_project' in clir.toml) for extraction.")
            return 1
        print("Running extraction...")
        if limit:
            extract_per_language(
                project_id=project_id,
                output_path=raw_path,
                languages=extract_languages,
                limit_per_lang=limit,
            )
        else:
            extract(
                project_id=project_id,
                output_path=raw_path,
                languages=extract_languages,
            )
    elif raw_path.exists():
        print(f"Reusing existing raw data: {raw_path}")

    if not raw_path.exists():
        print(f"Error: raw data not found at {raw_path}. Run extraction first.")
        return 1

    if not getattr(args, "skip_preprocess", False):
        print("\nPreprocessing to CSV per language...")
        workspace.ensure_dir(preprocessed_dir)
        records = load_records(raw_path)
        skip_remaining = False
        for language in extract_languages:
            out_path = preprocessed_dir / f"{language}.csv"
            if skip_remaining:
                print(f"  Skipping {language} (user chose skip remaining).")
                continue
            if out_path.exists() and not assume_yes:
                answer = _ask(
                    f"  {language}: preprocessed CSV already exists "
                    f"({corpus_io.count_rows(out_path):,} rows). Rebuild it from raw data? "
                    "(y = rebuild, n = keep current file, s = keep this and all remaining languages): "
                )
                if answer == "s":
                    skip_remaining = True
                    print(f"  Skipping {language} and remaining.")
                    continue
                if answer != "y":
                    print(f"  {language}: skipped.")
                    continue
            rows, stats = build_language_rows(
                records,
                language,
                per_lang_limit=limit,
                source_value=source.source_value,
            )
            corpus_io.write_rows(out_path, rows, context.schema.fields)
            _report_language(language, len(rows), out_path, stats)

    if corpus_path.exists() and not assume_yes:
        rebuild = _ask(
            f"Corpus already exists ({corpus_io.count_rows(corpus_path):,} rows). "
            "Rebuild it from the preprocessed files? (y/n): "
        )
        if rebuild != "y":
            print(f"Keeping existing corpus: {corpus_path}")
            return 0

    merged = merge_preprocessed(preprocessed_dir, languages=corpus_languages)
    min_languages = int(getattr(args, "min_langs", 2) or 2)
    kept, summary = corpus_io.filter_multilingual(
        merged,
        context.schema,
        languages=corpus_languages,
        min_languages=min_languages,
    )
    # Sorted by family then language so the corpus diffs readably between
    # rebuilds; the canonical published corpus is in this order.
    kept.sort(key=lambda row: (context.schema.family_of(row), context.schema.language_of(row)))
    corpus_io.write_rows(corpus_path, kept, context.schema.fields)

    print(
        f"\nMerged {len(merged):,} rows; kept {summary['rows_kept']:,} rows from "
        f"{summary['families_kept']:,} publications present in >= {min_languages} of "
        f"{list(corpus_languages)}."
    )
    print(f"  Per language: {summary['per_language']}")
    print(f"  Coverage:     {summary['coverage_distribution']} (languages -> publications)")
    print(f"  Corpus:       {corpus_path}")
    return 0


__all__ = [
    "build_first_claim",
    "build_language_rows",
    "build_query",
    "build_query_per_language_top_n",
    "extract",
    "extract_per_language",
    "ingest",
    "load_records",
    "merge_preprocessed",
    "min_abstract_chars_for_sql",
    "preprocess_ndjson",
    "run_query",
    "sql_list",
]
