"""
EPO bulk full-text ingest (BDDS product 32).

The EPO publishes its weekly full-text deliveries as multi-gigabyte archives on
an anonymous endpoint. Downloading one, unpacking it and filtering afterwards
would need tens of gigabytes of free disk per week, which this project does not
have, so an item is streamed over HTTP and filtered as it arrives: nested
archives are recursed into a member at a time and the bytes are discarded once
the row is built. Peak working set is one nested archive, not one delivery.

The consequence is that the archives cannot be re-read cheaply, so what survives
a run has to be decided during it. Three filters run in order, cheapest first:

  1. auxiliary XML is skipped by filename before it is ever parsed;
  2. a document must be chemistry (classification codes, or title keywords when
     ``--strict`` is off);
  3. a document must exist in at least two of the EPO's three official
     languages, judged on substantive text rather than on titles.

Resume state lives in a manifest of processed BDDS item ids and the publication
numbers already written, so an interrupted run continues without re-downloading
and without duplicating rows.

Discovery (anonymous):
  GET {API_BASE}/api/public/products/32
Download (anonymous):
  {API_BASE}/api/public/products/32/delivery/{deliveryId}/item/{itemId}/download
"""

from __future__ import annotations

import argparse
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

import requests
from tqdm import tqdm

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.domain import CorpusSchema
from clir_bench.core.ingest import (
    Manifest,
    MultilingualAccumulator,
    http_stream,
    stream_archive_members,
)
from clir_bench.domains.chem_patents.sources.epo_xml import (
    AUXILIARY_XML_RE,
    build_row_for_language,
    chemistry_rank,
    language_has_substantive_text,
    parse_epo_patent_bytes,
)
from clir_bench.domains.chem_patents.vocabulary import CHEMISTRY_LABELS

API_BASE = "https://publication-bdds.apps.epo.org/bdds/bdds-bff-service/prod"
PRODUCT_ID = 32
USER_AGENT = "clir-bench/0.1 (+research)"

# Languages a document must be present in before it is worth keeping. Two is the
# floor for a cross-language pair; requiring all three would cost most of the
# corpus, since the EPO translates claims into all three but abstracts rarely.
MIN_LANGUAGES = 2

_NOT_CHEMISTRY, _, _CHEMISTRY_CORE = CHEMISTRY_LABELS


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ItemRef:
    """One downloadable archive within one BDDS delivery."""

    item_id: int
    item_name: str
    delivery_id: int
    delivery_name: str
    file_size: str
    checksum_sha1: str
    published_at: str
    download_url: str

    @property
    def archive_kind(self) -> str:
        """Archive kind as ``core.ingest`` names it.

        Gzipped tars collapse to "tar": the streamer opens with mode ``r|*``,
        which sniffs compression, so the distinction the filename makes does not
        need to reach it.
        """
        name = self.item_name.lower()
        if name.endswith(".zip"):
            return "zip"
        if name.endswith((".tar", ".tar.gz", ".tgz")):
            return "tar"
        raise ValueError(f"unrecognised archive for item {self.item_id}: {self.item_name}")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json, application/octet-stream;q=0.9, */*;q=0.5",
    })
    return session


def list_items(
    product_id: int = PRODUCT_ID,
    *,
    session: Optional[requests.Session] = None,
) -> list[ItemRef]:
    """Every item of every delivery of a public BDDS product, newest first."""
    owned = session is None
    session = session or build_session()
    try:
        response = session.get(f"{API_BASE}/api/public/products/{product_id}", timeout=30)
        response.raise_for_status()
        payload = response.json()
    finally:
        if owned:
            session.close()

    items: list[ItemRef] = []
    for delivery in payload.get("deliveries", []):
        delivery_id = delivery["deliveryId"]
        for entry in delivery.get("items", []):
            items.append(ItemRef(
                item_id=entry["itemId"],
                item_name=entry["itemName"],
                delivery_id=delivery_id,
                delivery_name=delivery.get("deliveryName", ""),
                file_size=entry.get("fileSize", ""),
                checksum_sha1=entry.get("fileChecksum", ""),
                published_at=entry.get("itemPublicationDatetime", ""),
                download_url=(
                    f"{API_BASE}/api/public/products/{product_id}"
                    f"/delivery/{delivery_id}/item/{entry['itemId']}/download"
                ),
            ))

    items.sort(key=lambda item: item.published_at, reverse=True)
    return items


def select_next_items(
    items: Iterable[ItemRef],
    processed_ids: Iterable[str],
    n: int,
) -> list[ItemRef]:
    """The ``n`` newest items not already in the manifest."""
    seen = {str(value) for value in processed_ids}
    selected: list[ItemRef] = []
    for item in items:
        if str(item.item_id) in seen:
            continue
        selected.append(item)
        if len(selected) >= n:
            break
    return selected


# --------------------------------------------------------------------------- #
# Ingest of one item
# --------------------------------------------------------------------------- #

def _is_patent_xml(name: str) -> bool:
    return name.lower().endswith(".xml") and not AUXILIARY_XML_RE.search(name)


def _row_rank(row: Mapping[str, Any]) -> tuple:
    """Rank two versions of the same (publication, language).

    A publication appears several times in one delivery under different kind
    codes -- A1 application, A2 search report, B1 grant -- and the later one
    supersedes the earlier, so the kind code decides first. Kind codes sort
    correctly as plain strings (B1 > A2 > A1). Text volume breaks ties within a
    kind, where the difference is which XML happened to carry the fuller text.
    """
    return (str(row.get("_kind", "")), _text_volume(row))


def _text_volume(row: Mapping[str, Any]) -> int:
    """Abstract and claim weigh full; description is discounted as it is truncated."""
    return (
        len(row.get("abstract") or "")
        + len(row.get("first_claim") or "")
        + len(row.get("description") or "") // 4
    )


def ingest_item(
    item: ItemRef,
    *,
    manifest: Manifest,
    corpus_path: Path,
    schema: CorpusSchema,
    languages: Sequence[str],
    session: requests.Session,
    source_value: str = "epo",
    strict: bool = False,
    min_languages: int = MIN_LANGUAGES,
) -> dict[str, Any]:
    """Stream one BDDS item end to end: parse, filter, append, commit."""
    print(
        f"[epo] item {item.item_id} {item.item_name} "
        f"({item.file_size or 'unknown size'}, published {item.published_at or 'unknown'})"
    )

    accumulator = MultilingualAccumulator(rank=_row_rank)
    # Chemistry is a property of the publication, not of one XML of it, and the
    # strongest signal across versions wins -- an A1 with no classification
    # codes yet must not veto the B1 that has them. Tracked outside the
    # accumulator so versions that yield no usable row still count.
    labels: dict[str, str] = {}
    stats = {"xml_seen": 0, "xml_parse_errors": 0, "xml_not_patent": 0}

    stream = http_stream(item.download_url, session=session, description=f"  download {item.item_name}")
    progress = tqdm(desc=f"  parse {item.item_name}", unit="xml", leave=False)
    try:
        for payload, name in stream_archive_members(stream, kind=item.archive_kind, keep=_is_patent_xml):
            stats["xml_seen"] += 1
            progress.update(1)
            try:
                record = parse_epo_patent_bytes(payload, xml_name=name)
            except ET.ParseError:
                stats["xml_parse_errors"] += 1
                continue
            except ValueError:
                # Not an <ep-patent-document>, or missing identifiers/title.
                stats["xml_not_patent"] += 1
                continue

            family = record["publication_number"]
            label = record["chemistry"]["label"]
            if chemistry_rank(label) > chemistry_rank(labels.get(family, _NOT_CHEMISTRY)):
                labels[family] = label

            for language in languages:
                # Gate before building: a language slot with only a title must
                # not count toward coverage, and a row that cannot count is a
                # row the corpus has no use for.
                if not language_has_substantive_text(record, language):
                    continue
                row = build_row_for_language(record, language, source=source_value)
                if row is None:
                    continue
                row["_kind"] = record.get("kind", "")
                accumulator.add(family, language, row)
    finally:
        progress.close()

    def accept(group: Sequence[Mapping[str, Any]]) -> bool:
        label = labels.get(schema.family_of(group[0]), _NOT_CHEMISTRY)
        if label == _NOT_CHEMISTRY:
            return False
        return not strict or label == _CHEMISTRY_CORE

    rows = accumulator.materialize(
        min_languages=min_languages,
        languages=list(languages),
        accept=accept,
    )

    # Cross-item dedup only. Rows sharing a publication within this item are all
    # written -- several languages of one document is the point of the corpus.
    already_written = manifest.processed_families
    fresh = [row for row in rows if schema.family_of(row) not in already_written]
    families = {schema.family_of(row) for row in fresh}

    corpus_io.ensure_header(corpus_path, schema.fields)
    appended = corpus_io.write_rows(corpus_path, fresh, schema.fields, append=True)

    summary = {
        **stats,
        "publications_seen": len(labels),
        "chemistry_publications": sum(1 for label in labels.values() if label != _NOT_CHEMISTRY),
        "publications_written": len(families),
        "rows_appended": appended,
    }

    manifest.mark_processed(str(item.item_id), families)
    manifest.extra.setdefault("items", {})[str(item.item_id)] = {
        "item_name": item.item_name,
        "delivery_id": item.delivery_id,
        "delivery_name": item.delivery_name,
        "file_size": item.file_size,
        "checksum_sha1": item.checksum_sha1,
        "published_at": item.published_at,
        "processed_at": _now(),
        **summary,
    }
    manifest.extra["last_ingest_at"] = _now()
    manifest.save()

    print(
        f"  parsed {stats['xml_seen']} XML files, {summary['chemistry_publications']} chemistry "
        f"publications, appended {appended} rows ({len(families)} new publications) to {corpus_path}"
    )
    return summary


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #

def ingest(context: AppContext, args: argparse.Namespace) -> int:
    """Handler for ``clir ingest epo``."""
    spec = context.domain.source("epo")
    schema = context.schema
    languages = tuple(spec.languages)

    output_dir = getattr(args, "output_dir", None)
    if output_dir:
        # Pilot mode: an isolated manifest and corpus, so validating the
        # pipeline against a small archive cannot contaminate the real corpus
        # or burn the item's id in the real manifest.
        root = context.workspace.ensure_dir(Path(output_dir).expanduser())
        manifest_path = root / "manifest.json"
        corpus_path = root / "multilingual_corpus.csv"
    else:
        manifest_path = context.workspace.data("epo_manifest")
        corpus_path = context.workspace.corpus_csv(spec)
    context.workspace.ensure(corpus_path)

    batches = int(getattr(args, "batches", 1) or 1)
    if batches < 1:
        print("[epo] --batches must be at least 1", file=sys.stderr)
        return 2

    manifest = Manifest.load(manifest_path)
    session = build_session()
    try:
        items = list_items(session=session)
        wanted = getattr(args, "item", None)
        if wanted:
            queued = [item for item in items if str(item.item_id) == str(wanted)]
            if not queued:
                print(f"[epo] no item {wanted!r} in BDDS product {PRODUCT_ID}", file=sys.stderr)
                return 1
        else:
            queued = select_next_items(items, manifest.processed_items, batches)

        if not queued:
            print(
                f"[epo] nothing new to process; {len(manifest.processed_items)} "
                f"item(s) already in {manifest_path}"
            )
            return 0

        print(f"[epo] {len(queued)} item(s) queued:")
        for item in queued:
            print(f"  {item.item_id:>6}  {item.item_name:<40} {item.file_size:>10}  {item.published_at}")

        for position, item in enumerate(queued, 1):
            if manifest.is_processed(str(item.item_id)):
                print(
                    f"[epo] item {item.item_id} is already in the manifest; "
                    "pass --output-dir to re-run it in isolation"
                )
                continue
            print(f"\n[epo] batch {position}/{len(queued)}")
            try:
                ingest_item(
                    item,
                    manifest=manifest,
                    corpus_path=corpus_path,
                    schema=schema,
                    languages=languages,
                    session=session,
                    source_value=spec.source_value,
                    strict=bool(getattr(args, "strict", False)),
                )
            except Exception as exc:
                # Stop rather than continue: a half-streamed item leaves rows on
                # disk whose publications are not yet in the manifest, and the
                # next item would append on top of that inconsistency.
                print(f"[epo] failed on item {item.item_id}: {exc}", file=sys.stderr)
                return 1
    finally:
        session.close()

    return 0


__all__ = [
    "API_BASE",
    "ItemRef",
    "MIN_LANGUAGES",
    "PRODUCT_ID",
    "build_session",
    "ingest",
    "ingest_item",
    "list_items",
    "select_next_items",
]
