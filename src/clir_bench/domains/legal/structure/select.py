"""
Stage 1 -- choose which acts to segment.

Scans the MultiEURLEX parquet for acts that can actually carry the metadata this
pipeline produces, then draws a pilot stratified by size.

Why stratify by article count rather than sample at random: short amending acts
dominate the corpus and yield no intra-act edges at all -- 32008R1113 has three
articles and zero internal references. A uniform sample would spend most of the
pilot on acts with nothing to extract, and the reference audit needs acts with
dense reference webs to measure recall against.

Usage:
    python -m clir_bench.domains.legal.structure.select scan
    python -m clir_bench.domains.legal.structure.select sample --n 20
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

from clir_bench.domains.legal.structure import ACT_LANGUAGES
from clir_bench.domains.legal.structure import paths

# CELLAR serves Formex only from roughly 2004; older acts survive as flat legacy
# HTML, which segments far worse. See the package docstring.
FORMEX_ERA_FROM = 2004

# "Article 12" at the start of a line. A proxy only: in amending acts the quoted
# text of the parent act also matches, so this over-counts. Good enough to bin by
# size, and the authoritative count comes from the Formex parse in stage 3.
_ARTICLE_HEADING_RE = re.compile(r"(?m)^\s*Article\s+(\d+)\b")

# Size bins, by proxy article count. The open-ended top bin is where the dense
# reference webs live.
SIZE_BINS: tuple[tuple[str, int, int], ...] = (
    ("tiny", 1, 4),
    ("small", 5, 14),
    ("medium", 15, 39),
    ("large", 40, 10_000),
)


def bin_for(n_articles: int) -> str | None:
    for name, lo, hi in SIZE_BINS:
        if lo <= n_articles <= hi:
            return name
    return None


def proxy_article_count(text: str) -> int:
    """Distinct article numbers appearing as a heading. See `_ARTICLE_HEADING_RE`."""
    return len({m.group(1) for m in _ARTICLE_HEADING_RE.finditer(text or "")})


def scan(*, batch_size: int = 256) -> list[dict]:
    """Every act that is Formex-era and present in all four working languages."""
    columns = ["celex_id", "doc_type", "year"] + [f"text.{lg}" for lg in ACT_LANGUAGES]
    rows: list[dict] = []
    skipped = Counter()

    for split in ("train", "validation", "test"):
        path = paths.DOCUMENTS_DIR / f"{split}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"missing {path}; run data/legal/eurlex/_fetch.py first")
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=batch_size, columns=columns):
            d = batch.to_pydict()
            # `iter_batches` keeps `text` as a nested struct even when the
            # selection names its children; `read_table` would flatten it.
            for i in range(len(d["celex_id"])):
                year = int(d["year"][i])
                if year < FORMEX_ERA_FROM:
                    skipped["pre-formex-era"] += 1
                    continue
                struct = d["text"][i] or {}
                texts = {lg: (struct.get(lg) or "") for lg in ACT_LANGUAGES}
                missing = [lg for lg, t in texts.items() if not t.strip()]
                if missing:
                    skipped["missing-language"] += 1
                    continue
                n = proxy_article_count(texts["en"])
                if n == 0:
                    # No numbered article headings: "Sole Article" acts and
                    # texts whose structure did not survive MultiEURLEX's
                    # preprocessing. Rejected per spec.
                    skipped["no-numbered-articles"] += 1
                    continue
                rows.append({
                    "celex_id": d["celex_id"][i],
                    "doc_type": d["doc_type"][i],
                    "year": year,
                    "split": split,
                    "proxy_articles": n,
                    "size_bin": bin_for(n) or "",
                    "chars_en": len(texts["en"]),
                })
    print(f"[scan] kept {len(rows):,} candidate acts", file=sys.stderr)
    for reason, count in skipped.most_common():
        print(f"       skipped {count:>7,}  {reason}", file=sys.stderr)
    return rows


def write_candidates(rows: list[dict]) -> Path:
    paths.ensure_dirs()
    with paths.CANDIDATES_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return paths.CANDIDATES_CSV


def read_candidates() -> list[dict]:
    with paths.CANDIDATES_CSV.open(encoding="utf-8") as fh:
        return [
            {**r, "year": int(r["year"]),
             "proxy_articles": int(r["proxy_articles"]),
             "chars_en": int(r["chars_en"])}
            for r in csv.DictReader(fh)
        ]


def sample(rows: list[dict], *, n: int = 20, seed: int = 20260803) -> list[dict]:
    """Draw `n` acts spread across size bin, then doc type, then era.

    Deterministic: selection is by a seeded hash of the CELEX id rather than
    `random.sample`, so re-running with a larger `n` keeps the earlier picks.
    """
    import hashlib

    def rank(celex: str) -> int:
        return int(hashlib.sha256(f"{seed}:{celex}".encode()).hexdigest(), 16)

    strata: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row["size_bin"]:
            strata[(row["size_bin"], row["doc_type"])].append(row)
    for bucket in strata.values():
        bucket.sort(key=lambda r: rank(r["celex_id"]))

    # Round-robin across strata so every bin and both act types are represented
    # even when one stratum is far larger than the others.
    order = sorted(strata)
    picked: list[dict] = []
    depth = 0
    while len(picked) < n:
        progressed = False
        for key in order:
            if len(picked) >= n:
                break
            bucket = strata[key]
            if depth < len(bucket):
                picked.append(bucket[depth])
                progressed = True
        if not progressed:
            break
        depth += 1

    picked.sort(key=lambda r: (r["size_bin"], r["doc_type"], r["celex_id"]))
    return picked


def write_pilot(rows: list[dict]) -> Path:
    paths.ensure_dirs()
    with paths.PILOT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return paths.PILOT_CSV


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan", help="find all Formex-era four-language acts")
    p_sample = sub.add_parser("sample", help="draw a stratified pilot")
    p_sample.add_argument("--n", type=int, default=20)
    p_sample.add_argument("--seed", type=int, default=20260803)
    args = parser.parse_args()

    if args.command == "scan":
        rows = scan()
        path = write_candidates(rows)
        by_bin = Counter(r["size_bin"] for r in rows)
        by_type = Counter(r["doc_type"] for r in rows)
        print(f"wrote {path}")
        print("  by size bin:", dict(by_bin))
        print("  by doc type:", dict(by_type))
        return

    rows = read_candidates()
    picked = sample(rows, n=args.n, seed=args.seed)
    path = write_pilot(picked)
    print(f"wrote {path}  ({len(picked)} acts)")
    for row in picked:
        print(f"  {row['celex_id']}  {row['doc_type']:<11} {row['year']}  "
              f"{row['size_bin']:<7} ~{row['proxy_articles']:>3} articles")


if __name__ == "__main__":
    main()
