"""
The patent corpus schema.

The historical text columns are retained, with upstream provenance and accepted
pair metadata appended. ``publication_number`` identifies one publication;
the upstream patent-family grouping is preserved separately. Retrieval relevance
uses explicit ``paired_document_ids``, since accepted language pairs do not
necessarily connect every language version of a publication to every other one.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from clir_bench.core.domain import CorpusSchema

CORPUS_FIELDS = (
    "id",
    "language",
    "title",
    "abstract",
    "description",
    "first_claim",
    "context",
    "publication_number",
    "country_code",
    "publication_date",
    "source",
    "ipc_codes",
    "upstream_dataset",
    "upstream_revision",
    "upstream_corpus_id",
    "upstream_group_key",
    "accepted_pair_ids",
    "paired_document_ids",
)

# The parts assembled into the ``context`` column, in order.
CONTEXT_LABELS = (
    ("title", "Title"),
    ("abstract", "Abstract"),
    ("first_claim", "First claim"),
)

# A run of at least five digits is the document number inside a publication id;
# the surrounding country code and kind code vary by source formatting
# ("EP-3686982-A1" from Google Patents vs "3686982" from EPO bulk data).
_DOC_NUMBER_RE = re.compile(r"(\d{5,})")


def dedup_key(row: Mapping[str, Any]) -> str:
    """Canonical patent identity: country code plus bare document number.

    The two sources format publication numbers differently, so a raw string
    comparison misses overlaps. This normalization is the contract that keeps
    the Google Patents and EPO corpora disjoint.
    """
    publication = str(row.get("publication_number", "") or "")
    country = str(row.get("country_code", "") or "").strip().upper()
    match = _DOC_NUMBER_RE.search(publication)
    if not match:
        return publication.strip()
    if not country:
        head = publication.strip().upper()
        country = head[:2] if head[:2].isalpha() else ""
    return f"{country}_{match.group(1)}"


SCHEMA = CorpusSchema(
    fields=CORPUS_FIELDS,
    family_field="publication_number",
    id_field="id",
    language_field="language",
    text_fields=("context", "abstract", "title"),
    dedup_key_fn=dedup_key,
    parallel_ids_field="paired_document_ids",
    export_metadata_fields=(
        "upstream_dataset", "upstream_revision", "upstream_corpus_id", "upstream_group_key",
        "accepted_pair_ids", "paired_document_ids",
    ),
)


__all__ = ["CONTEXT_LABELS", "CORPUS_FIELDS", "SCHEMA", "dedup_key"]
