"""
The patent corpus schema.

Column names and order match the CSVs the project already has on disk, so
existing data files are readable without conversion.

``publication_number`` is the family key: the versions of one patent in
different languages share it, which is what makes a query about a patent
relevant to all of its translations. A legal domain would set ``family_field``
to whatever plays that role there (a CELEX id, a case number) and the same core
logic applies unchanged.
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
)


__all__ = ["CONTEXT_LABELS", "CORPUS_FIELDS", "SCHEMA", "dedup_key"]
