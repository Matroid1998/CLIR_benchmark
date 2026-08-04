"""
Gold-standard audit: measure precision *and* recall on whole articles.

The first audit sampled extracted edges and checked each one, which measures
precision but is structurally incapable of measuring recall -- a reference the
extractor never emitted can never appear in a sample of its output. Recall has to
be measured the other way round: read whole articles, write down every
article-to-article reference they actually contain, and only then compare.

So this stage does two things:

``prepare``  samples articles and writes annotation batches containing the
             article text and the act's article inventory -- and deliberately
             *not* the extractor's output, so annotation is blind. Anything else
             invites rubber-stamping, which would bias recall upward.

``score``    merges the independent annotations, compares them to the extracted
             edges, and writes out every disagreement for manual adjudication.

Scoring is at edge level, (source article, target article), because that is the
unit the pipeline actually ships.

Usage:
    python -m clir_bench.domains.legal.structure.gold prepare --n 300 --batches 15
    python -m clir_bench.domains.legal.structure.gold score
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict

from clir_bench.domains.legal.structure import paths

GOLD_DIR = paths.STRUCTURE_DIR / "gold300"
BATCH_DIR = GOLD_DIR / "batches"
ANNOTATION_DIR = GOLD_DIR / "annotations"
SAMPLE_JSON = GOLD_DIR / "sample.json"


def _english_articles() -> list[dict]:
    return [json.loads(line) for line in paths.ARTICLES_JSONL.open(encoding="utf-8")
            if (row := json.loads(line))["language"] == "en"
            and row["unit_type"] == "article"]


def prepare(n: int, batches: int, seed: int) -> None:
    rows = [json.loads(line) for line in paths.ARTICLES_JSONL.open(encoding="utf-8")]
    english = [r for r in rows if r["language"] == "en" and r["unit_type"] == "article"]

    inventories: dict[str, list[str]] = defaultdict(list)
    for row in english:
        inventories[row["celex_id"]].append(row["article_number"])

    # Uniform random over articles: unbiased for a corpus-level rate, and it
    # keeps articles with no extracted edges in the sample, which is exactly
    # where false negatives hide.
    def rank(row: dict) -> str:
        return hashlib.sha256(f"{seed}:{row['eli_id']}".encode()).hexdigest()

    picked = sorted(english, key=rank)[:n]

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)

    # Balance batches by character count, not article count: one article in the
    # pilot is 90k characters and would otherwise swamp whichever batch it fell
    # into while the rest went half empty.
    buckets: list[list[dict]] = [[] for _ in range(batches)]
    sizes = [0] * batches
    for row in sorted(picked, key=lambda r: -len(r["text"])):
        target = sizes.index(min(sizes))
        buckets[target].append(row)
        sizes[target] += len(row["text"])

    for index, bucket in enumerate(buckets):
        payload = {
            "batch": index,
            "articles": [{
                "celex_id": r["celex_id"],
                "article_number": r["article_number"],
                "heading": r["heading"],
                "act_article_inventory": sorted(inventories[r["celex_id"]],
                                                key=lambda x: (len(x), x)),
                "text": r["text"],
            } for bucket_row in [bucket] for r in bucket_row],
        }
        (BATCH_DIR / f"batch_{index:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1))

    SAMPLE_JSON.write_text(json.dumps(
        [{"celex_id": r["celex_id"], "article_number": r["article_number"]} for r in picked],
        indent=1))
    print(f"sampled {len(picked)} of {len(english)} English articles "
          f"({len(picked) / len(english):.0%})")
    print(f"batches: {batches}  chars per batch: min {min(sizes):,} max {max(sizes):,}")
    print(f"acts represented: {len({r['celex_id'] for r in picked})}")
    print(f"wrote {BATCH_DIR}")


# -- scoring ---------------------------------------------------------------- #

def _load_annotations() -> dict[tuple[str, str], set[str]]:
    """(celex, article) -> union of target article numbers across annotators."""
    gold: dict[tuple[str, str], set[str]] = defaultdict(set)
    seen_files = 0
    for path in sorted(ANNOTATION_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        seen_files += 1
        for article in payload.get("articles", []):
            key = (article["celex_id"], str(article["article_number"]))
            gold.setdefault(key, set())
            for reference in article.get("internal_references", []):
                for target in reference.get("target_article_numbers", []):
                    target = str(target).strip()
                    if target and target != str(article["article_number"]):
                        gold[key].add(target)
    print(f"loaded {seen_files} annotation files")
    return gold


def score() -> None:
    sample = {(r["celex_id"], r["article_number"]) for r in json.loads(SAMPLE_JSON.read_text())}
    gold = _load_annotations()

    extracted: dict[tuple[str, str], set[str]] = defaultdict(set)
    for line in paths.INTERNAL_EDGES_JSONL.open(encoding="utf-8"):
        edge = json.loads(line)
        key = (edge["source_celex"], edge["source_article_number"])
        if key in sample:
            extracted[key].add(edge["target_article_number"])

    inventories: dict[str, set[str]] = defaultdict(set)
    for line in paths.ARTICLES_JSONL.open(encoding="utf-8"):
        row = json.loads(line)
        if row["unit_type"] == "article" and row["language"] == "en":
            inventories[row["celex_id"]].add(row["article_number"])

    tp = fp = fn = 0
    disagreements = []
    annotated = [k for k in sample if k in gold]
    for key in sorted(annotated):
        celex, article = key
        # An annotated target outside the act's own inventory is out of scope by
        # spec (step 5), so it cannot count as a miss.
        want = {t for t in gold[key] if t in inventories[celex]}
        got = extracted.get(key, set())
        tp += len(want & got)
        for target in sorted(got - want):
            fp += 1
            disagreements.append({"kind": "false_positive_candidate", "celex_id": celex,
                                  "article_number": article, "target": target})
        for target in sorted(want - got):
            fn += 1
            disagreements.append({"kind": "false_negative_candidate", "celex_id": celex,
                                  "article_number": article, "target": target})

    (GOLD_DIR / "disagreements.json").write_text(json.dumps(disagreements, indent=1))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    print(f"articles annotated      {len(annotated)}")
    print(f"true positives          {tp}")
    print(f"false-positive candidates {fp}")
    print(f"false-negative candidates {fn}")
    print(f"precision (pre-adjudication) {precision:.1%}")
    print(f"recall    (pre-adjudication) {recall:.1%}")
    print(f"\ndisagreements to adjudicate -> {GOLD_DIR / 'disagreements.json'}")
    (GOLD_DIR / "score.json").write_text(json.dumps(
        {"articles": len(annotated), "tp": tp, "fp": fp, "fn": fn,
         "precision": precision, "recall": recall}, indent=1))


def adjudicate() -> None:
    """Print every disagreement with the text around it, for manual ruling.

    Neither side is authoritative: an annotator can invent a reference just as an
    extractor can miss one. Each case is decided by reading the source text.
    """
    import re

    disagreements = json.loads((GOLD_DIR / "disagreements.json").read_text())
    texts = {}
    for line in paths.ARTICLES_JSONL.open(encoding="utf-8"):
        row = json.loads(line)
        if row["unit_type"] == "article" and row["language"] == "en":
            texts[(row["celex_id"], row["article_number"])] = row["text"]

    for index, case in enumerate(disagreements, 1):
        key = (case["celex_id"], case["article_number"])
        text = texts.get(key, "")
        target = case["target"]
        # Show every mention of the disputed number in the article.
        windows = []
        for match in re.finditer(rf"\b{re.escape(target)}\b", text):
            lo, hi = max(0, match.start() - 150), min(len(text), match.end() + 90)
            windows.append(re.sub(r"\s+", " ", text[lo:hi]))
        tag = "FP?" if case["kind"].startswith("false_positive") else "FN?"
        print(f"[{index}] {tag} {case['celex_id']} art {case['article_number']} "
              f"-> target {target}   ({len(windows)} mention(s) of '{target}')")
        for window in windows[:3]:
            print(f"      …{window}…")
        if not windows:
            print("      (the number does not appear in the article text at all)")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--batches", type=int, default=15)
    p.add_argument("--seed", type=int, default=300300)
    sub.add_parser("score")
    sub.add_parser("adjudicate")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.n, args.batches, args.seed)
    elif args.command == "score":
        score()
    else:
        adjudicate()


if __name__ == "__main__":
    main()
