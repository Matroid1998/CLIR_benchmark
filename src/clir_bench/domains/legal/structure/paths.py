"""Where this stage reads and writes.

The legal domain has no ``DomainSpec``, so ``core.paths.Workspace`` cannot
resolve these yet. These constants mirror the layout a ``data_layout`` entry
would declare, so wiring them into the domain spec later is a rename, not a
move.
"""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Repository root, found by walking up from this file."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


ROOT = repo_root()

EURLEX_DIR = ROOT / "data/legal/eurlex"
DOCUMENTS_DIR = EURLEX_DIR / "documents"

STRUCTURE_DIR = EURLEX_DIR / "structure"
CACHE_DIR = STRUCTURE_DIR / "cache"          # raw CELLAR responses, never re-fetched
PARSED_DIR = STRUCTURE_DIR / "parsed"        # parse-fmx JSON, one per (celex, lang)

CANDIDATES_CSV = STRUCTURE_DIR / "candidates.csv"
PILOT_CSV = STRUCTURE_DIR / "pilot.csv"

ARTICLES_JSONL = STRUCTURE_DIR / "articles.jsonl"
INTERNAL_EDGES_JSONL = STRUCTURE_DIR / "internal_edges.jsonl"
EXTERNAL_REFS_JSONL = STRUCTURE_DIR / "external_references.jsonl"
QUARANTINE_JSONL = STRUCTURE_DIR / "quarantine.jsonl"
DROPPED_JSONL = STRUCTURE_DIR / "dropped_references.jsonl"
FETCH_MANIFEST_JSON = STRUCTURE_DIR / "fetch_manifest.json"

# Stage 5 (resolve_external): cross-act references resolved to articles that
# are themselves in the corpus, everything that could not be resolved with its
# reason, and the per-article verdict on whether the citation graph is complete.
EXTERNAL_EDGES_JSONL = STRUCTURE_DIR / "external_edges.jsonl"
UNRESOLVED_EXTERNAL_JSONL = STRUCTURE_DIR / "unresolved_external.jsonl"
REFERENCE_STATUS_JSONL = STRUCTURE_DIR / "reference_status.jsonl"

REPORTS_DIR = ROOT / "reports/eurlex_structure"


def ensure_dirs() -> None:
    for path in (STRUCTURE_DIR, CACHE_DIR, PARSED_DIR, REPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "ROOT", "EURLEX_DIR", "DOCUMENTS_DIR", "STRUCTURE_DIR", "CACHE_DIR",
    "PARSED_DIR", "CANDIDATES_CSV", "PILOT_CSV", "ARTICLES_JSONL",
    "INTERNAL_EDGES_JSONL", "EXTERNAL_REFS_JSONL", "QUARANTINE_JSONL",
    "DROPPED_JSONL", "FETCH_MANIFEST_JSON", "EXTERNAL_EDGES_JSONL",
    "UNRESOLVED_EXTERNAL_JSONL", "REFERENCE_STATUS_JSONL", "REPORTS_DIR",
    "ensure_dirs",
]
