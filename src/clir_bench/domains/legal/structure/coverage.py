"""
Formex coverage probe -- how ragged is the 2004 boundary?

Two acts from 2004 in the pilot returned 404 for Formex in every language, so
"Formex era starts in 2004" is an approximation rather than a rule. This samples
acts per year and records whether CELLAR actually serves Formex for them, so the
corpus cutoff can be set from measurement instead of folklore.

Availability only: it issues one request per act and reads the status, never the
body. Results are cached, so a re-run costs nothing for acts already probed.

Usage:
    python -m clir_bench.domains.legal.structure.coverage --per-year 12
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict

from clir_bench.domains.legal.structure import cellar, paths, select

PROBE_JSON = paths.STRUCTURE_DIR / "formex_coverage.json"


def probe(celex: str) -> bool:
    """True when CELLAR serves Formex for this act in English."""
    zip_path = paths.CACHE_DIR / f"{celex}.en.zip"
    miss_path = paths.CACHE_DIR / f"{celex}.en.miss"
    if zip_path.exists():
        return True
    if miss_path.exists():
        return False
    files = cellar.fetch_act(celex, "en")
    return files.act_xml is not None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-year", type=int, default=12)
    parser.add_argument("--from-year", type=int, default=2000)
    parser.add_argument("--to-year", type=int, default=2016)
    args = parser.parse_args()

    paths.ensure_dirs()

    # Candidates only cover the Formex era, so read the raw corpus metadata to
    # reach back before it.
    import pyarrow.parquet as pq
    rows = []
    for split in ("train", "validation", "test"):
        table = pq.read_table(paths.DOCUMENTS_DIR / f"{split}.parquet",
                              columns=["celex_id", "doc_type", "year"]).to_pandas()
        rows.append(table)
    import pandas as pd
    meta = pd.concat(rows, ignore_index=True)

    by_year: dict[int, list[str]] = defaultdict(list)
    for year in range(args.from_year, args.to_year + 1):
        pool = sorted(meta[meta.year == year].celex_id)
        if not pool:
            continue
        pool.sort(key=lambda c: hashlib.sha256(c.encode()).hexdigest())
        by_year[year] = pool[: args.per_year]

    results: dict[str, dict] = {}
    if PROBE_JSON.exists():
        results = json.loads(PROBE_JSON.read_text())

    for year in sorted(by_year):
        hits = 0
        for celex in by_year[year]:
            if celex in results:
                hits += results[celex]["formex"]
                continue
            ok = probe(celex)
            results[celex] = {"year": year, "formex": bool(ok)}
            hits += ok
        total = len(by_year[year])
        print(f"{year}  formex {hits:>3}/{total:<3} {'#' * round(20 * hits / total)}",
              flush=True)
        PROBE_JSON.write_text(json.dumps(results, indent=2))

    print(f"\nwrote {PROBE_JSON}")


if __name__ == "__main__":
    main()
