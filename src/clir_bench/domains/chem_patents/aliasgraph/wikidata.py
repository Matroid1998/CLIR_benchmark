"""
Wikipedia multilingual-name bridge for ChEBI concepts.

A concept's stable identity is its ChEBI id. Wikidata records that id on the
matching item via property ``P683`` (ChEBI ID), and every Wikidata item carries
Wikipedia sitelinks per language. So ChEBI id -> Wikidata item (via P683) ->
Wikipedia article titles gives us, for the *same* concept, the name people
actually use in each target language -- without any string matching that could
break the shared-identity guarantee.

Names are fetched in batches from the Wikidata Query Service (SPARQL) and cached
to disk keyed by ChEBI id, so only never-seen ids ever hit the network. Ids that
resolve to no Wikipedia title are cached as ``{}`` so they are not re-queried.

``cache_all_names`` is the bulk driver: the cache is normally filled lazily, for
the ~3k of ~205k ChEBI terms that turn up in the corpus, but pre-filling it for
every term lets downstream matching draw on the whole ontology. It is a thin
wrapper over the incremental fetcher, so it inherits the batching, backoff,
atomic incremental writes and negative caching, and is resumable: only ids
absent from the cache are queried, so re-running continues where a previous run
stopped.
"""

from __future__ import annotations

import json
import time
from math import ceil
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence

import requests

from clir_bench.core.context import AppContext
from clir_bench.core.llm import call_with_retries
from clir_bench.domains.chem_patents.aliasgraph import chebi as chebi_mod

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
# WQS policy requires a descriptive User-Agent with contact info.
USER_AGENT = "clir-bench/0.1 (research; +https://github.com/) chebi-wikipedia-bridge"
DEFAULT_LANGS: Sequence[str] = ("zh", "en", "de", "fr", "es")

CACHE_FILENAME = "wiki_names_cache.json"

BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 1.0
MAX_RETRIES = 4
RETRY_STATUS = {429, 500, 502, 503, 504}


def cache_path(context: AppContext) -> Path:
    """The shared ChEBI-id -> Wikipedia-titles cache."""
    return chebi_mod.cache_dir(context) / CACHE_FILENAME


def _numeric_id(chebi_id: str) -> str:
    """`CHEBI:15365` -> `15365` (P683 stores the bare number)."""
    return chebi_id.split(":", 1)[-1]


def _build_query(numeric_ids: Sequence[str], langs: Sequence[str]) -> str:
    values = " ".join(f'"{n}"' for n in numeric_ids)
    lang_filter = ", ".join(f'"{lang}"' for lang in langs)
    return f"""
SELECT ?chebi ?lang ?name WHERE {{
  VALUES ?chebi {{ {values} }}
  ?item wdt:P683 ?chebi .
  ?article schema:about ?item ;
           schema:inLanguage ?lang ;
           schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] ;
           schema:name ?name .
  FILTER(?lang in ({lang_filter}))
}}
"""


def load_cache(path: Path) -> Dict[str, Dict[str, str]]:
    path = Path(path)
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_cache(path: Path, cache: Dict[str, Dict[str, str]]) -> None:
    """Write through a temp file: an interrupted bulk run must not truncate it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=0)
    tmp.replace(path)


def _post_query(query: str) -> dict:
    # POST (not GET): the VALUES list makes the query long, and WQS 502s on
    # oversized URLs. 429 and 5xx are transient here, so they are raised as
    # errors for the retry wrapper rather than surfaced as a parse failure.
    headers = {"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    resp = requests.post(
        SPARQL_ENDPOINT,
        data={"query": query, "format": "json"},
        headers=headers,
        timeout=120,
    )
    if resp.status_code in RETRY_STATUS:
        raise requests.HTTPError(f"{resp.status_code} from WQS", response=resp)
    resp.raise_for_status()
    return resp.json()


def _query_batch(
    numeric_ids: Sequence[str], langs: Sequence[str]
) -> Dict[str, Dict[str, str]]:
    query = _build_query(numeric_ids, langs)
    payload = call_with_retries(
        lambda: _post_query(query), retries=MAX_RETRIES, label="wikidata sparql"
    )
    out: Dict[str, Dict[str, str]] = {}
    for row in payload["results"]["bindings"]:
        chebi_id = f"CHEBI:{row['chebi']['value']}"
        lang = row["lang"]["value"]
        out.setdefault(chebi_id, {})[lang] = row["name"]["value"]
    return out


def fetch_wikipedia_names(
    chebi_ids: Iterable[str],
    *,
    langs: Sequence[str] = DEFAULT_LANGS,
    path: Path,
) -> Dict[str, Dict[str, str]]:
    """
    Return ``{chebi_id: {lang: wikipedia_title}}`` for the requested ids.

    Only ids absent from the cache are queried (batched). A failed batch is
    skipped (not cached), so the run still produces KG-only names and the batch
    can be retried later. The cache is persisted incrementally after each batch.
    """
    path = Path(path)
    cache = load_cache(path)

    wanted = list(dict.fromkeys(chebi_ids))  # de-dup, keep order
    missing = [cid for cid in wanted if cid not in cache]
    if missing:
        print(
            f"Fetching Wikipedia names for {len(missing)} ChEBI ids "
            f"({len(wanted) - len(missing)} cached) in {tuple(langs)} ..."
        )
    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start : start + BATCH_SIZE]
        numeric = [_numeric_id(cid) for cid in batch]
        try:
            results = _query_batch(numeric, langs)
        except Exception as exc:  # network / SPARQL hiccup: skip, keep KG names
            print(f"  Wikidata batch {start // BATCH_SIZE} failed ({exc}); skipping.")
            continue
        for cid in batch:
            cache[cid] = results.get(cid, {})  # {} = queried, no Wikipedia article
        save_cache(path, cache)
        time.sleep(SLEEP_BETWEEN_BATCHES)

    return {cid: cache.get(cid, {}) for cid in wanted}


def cache_all_names(
    context: AppContext,
    *,
    variant: Optional[str] = None,
    langs: Sequence[str] = DEFAULT_LANGS,
) -> None:
    """Fetch Wikipedia names for every ChEBI term into the shared name cache."""
    directory = chebi_mod.cache_dir(context)
    resolved = chebi_mod.variant_for(context, variant)
    path = cache_path(context)

    graph = chebi_mod.load_chebi_graph(directory, resolved)
    all_ids = list(graph.nodes())

    cache = load_cache(path)
    missing = [cid for cid in all_ids if cid not in cache]
    n_batches = ceil(len(missing) / BATCH_SIZE)
    # ~1s sleep + ~1-2.5s per query round-trip => budget a 2-3.5s/batch range.
    eta_lo = n_batches * (SLEEP_BETWEEN_BATCHES + 1.0) / 3600
    eta_hi = n_batches * (SLEEP_BETWEEN_BATCHES + 2.5) / 3600

    print(
        f"ChEBI {resolved} graph: {len(all_ids)} terms; cache has {len(cache)} "
        f"({len(missing)} missing).\n"
        f"Fetching {len(missing)} ids in {n_batches} batches of {BATCH_SIZE} "
        f"for langs {tuple(langs)}; est. {eta_lo:.1f}-{eta_hi:.1f} h.\n"
        f"Resumable -- safe to interrupt and re-run."
    )
    if not missing:
        print("Nothing to do: every ChEBI term is already in the cache.")
        return

    fetch_wikipedia_names(all_ids, langs=langs, path=path)

    final = load_cache(path)
    with_any = sum(1 for v in final.values() if v)
    with_zh = sum(1 for v in final.values() if isinstance(v, dict) and v.get("zh"))
    print(
        f"Done. Cache now holds {len(final)} entries: "
        f"{with_any} with >=1 Wikipedia name, {with_zh} with a Chinese name."
    )


__all__ = [
    "DEFAULT_LANGS",
    "cache_all_names",
    "cache_path",
    "fetch_wikipedia_names",
    "load_cache",
    "save_cache",
]
