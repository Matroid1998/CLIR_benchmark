"""
Retrieval-decay evaluation for the progressive ladder.

For each base document the builder produced a ladder (``base__r0 .. base__rN``)
and one fixed query. This measures where each rung ranks IN THE FULL SHARED
CORPUS as the swap depth grows -- the dose-response curve behind "how fast does
retrieval fall apart?".

Three choices make the numbers mean what they claim:

* The haystack is the shared corpus with every language version of the base
  publications removed. Left in, the untouched original would be a near-duplicate
  twin of the depth-0 variant and would absorb the query at every depth.
* The haystack is encoded once per model and cached on disk, keyed on the exact
  id list, because it is by far the dominant cost and it does not change between
  depths.
* Rank is computed against the whole haystack rather than a candidate pool, so a
  document that falls out of the top-k is actually measured falling, not clipped.

This command loads embedding models, so it honours the same ``--allow-local``
confirmation as ``clir eval run``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional, Sequence

from clir_bench.core.context import AppContext
from clir_bench.core.runs import slugify_model

# Must match ``clir eval run``'s guard; duplicated rather than imported because
# domain packages do not import from the CLI layer.
ALLOW_LOCAL_ENV = "CLIR_ALLOW_LOCAL_MODELS"

RUN_LABEL = "progressive_cs"
RECALL_CUTOFFS: tuple[int, ...] = (1, 10, 100)

_QUERY_SUFFIX_RE = re.compile(r"__q_[a-z]{2,3}$")


def _strip_query_suffix(query_id: str) -> str:
    """Recover a base id from a query id when the queries config lacks one."""
    return _QUERY_SUFFIX_RE.sub("", str(query_id))


def _doc_text(title: Any, text: Any) -> str:
    """Compose document text exactly as the shared corpus and MTEB runs do."""
    return (str(title or "") + " " + str(text or "")).strip()


def _load_config(repo: str, config: str, revision: str):
    """Load one config from a HF dataset repo or a local dry-run export dir.

    The local layouts are the two ``publish_bundle`` can produce
    (``<dir>/<config>/<config>.parquet`` and ``<dir>/data/<config>/*.parquet``),
    so a dry-run export can be evaluated offline.
    """
    from datasets import load_dataset

    path = Path(repo)
    if path.is_dir():
        parquet = path / config / f"{config}.parquet"
        if not parquet.exists():
            hits = sorted((path / "data" / config).glob("*.parquet"))
            if not hits:
                raise FileNotFoundError(f"no {config} parquet under {path}")
            parquet = hits[0]
        return load_dataset("parquet", data_files=str(parquet), split="train")
    return load_dataset(repo, config, split="train", revision=revision)


def _task_metadata():
    """Minimal MTEB metadata, needed only so wrappers can read a prompt.

    ``prompt`` is set for the same reason the main harness sets it: instruction
    models call ``get_instruction()``, which otherwise looks this task up in
    MTEB's static registry and raises, since it is not there.
    """
    from mteb.abstasks.task_metadata import TaskMetadata

    from clir_bench.evaluation.harness import DEFAULT_RETRIEVAL_PROMPT

    return TaskMetadata(
        name="ProgressiveCS",
        description="Progressive code-switching retrieval decay",
        reference=None,
        type="Retrieval",
        category="t2t",
        modalities=["text"],
        eval_splits=["train"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        prompt=DEFAULT_RETRIEVAL_PROMPT,
        date=None,
        domains=None,
        task_subtypes=None,
        license=None,
        annotations_creators=None,
        dialect=None,
        sample_creation=None,
        bibtex_citation=None,
        dataset={"path": "local/progressive-cs", "revision": "1.0"},
    )


def _encode(model: Any, texts: Sequence[str], prompt_type: str, meta: Any, batch_size: int):
    """Encode and L2-normalize, using each model's correct prompt path.

    Registered models go through the MTEB wrapper's dataloader interface so
    query and document prompts are applied; a plain SentenceTransformer (the
    fallback for models MTEB has no entry for) is called directly.
    """
    import numpy as np
    from sentence_transformers import SentenceTransformer

    if isinstance(model, SentenceTransformer):
        raw = model.encode(
            list(texts), batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True
        )
    else:
        from mteb._create_dataloaders import _create_dataloader_from_texts
        from mteb.types import PromptType

        raw = model.encode(
            _create_dataloader_from_texts(list(texts), batch_size=batch_size),
            task_metadata=meta,
            hf_split="train",
            hf_subset="default",
            prompt_type=PromptType.query if prompt_type == "query" else PromptType.document,
            batch_size=batch_size,
            show_progress_bar=True,
        )
    embeddings = np.asarray(raw, dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return embeddings / norms


def _haystack_embeddings(
    model: Any,
    slug: str,
    ids: Sequence[str],
    texts: Sequence[str],
    meta: Any,
    batch_size: int,
    cache_dir: Optional[Path],
):
    """Encode the haystack once, cached and keyed on the exact id list.

    Keying on the ids rather than a timestamp means a changed haystack
    re-encodes automatically -- reusing a stale cache would silently compare
    ranks against a different corpus.
    """
    import numpy as np

    cache_npy = ids_json = None
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_npy = cache_dir / f"{slug}__haystack.npy"
        ids_json = cache_dir / f"{slug}__haystack_ids.json"
        if cache_npy.exists() and ids_json.exists():
            cached = json.loads(ids_json.read_text(encoding="utf-8"))
            if cached == list(ids):
                print(f"  [cache] reusing haystack embeddings ({len(ids)} docs) for {slug}")
                return np.load(cache_npy)
    print(f"  encoding haystack: {len(ids)} docs")
    embeddings = _encode(model, texts, "document", meta, batch_size)
    if cache_npy is not None:
        np.save(cache_npy, embeddings)
        ids_json.write_text(json.dumps(list(ids)), encoding="utf-8")
    return embeddings


def _models(args: argparse.Namespace, context: AppContext) -> list[str]:
    configured = list(context.setting("eval_models", ()) or context.settings.eval.models)
    requested = [m for m in (args.models or []) if m]
    if not requested or [m.lower() for m in requested] == ["all"]:
        if not configured:
            raise ValueError("no models given and no eval_models configured for this domain")
        return configured
    resolved: list[str] = []
    for model in requested:
        resolved.extend(configured if model.lower() == "all" else [model])
    return list(dict.fromkeys(resolved))


def evaluate_progressive(context: AppContext, args: argparse.Namespace) -> int:
    """Measure retrieval decay by ladder depth. Returns 0 on success."""
    allowed = (
        args.allow_local
        or context.settings.eval.allow_local_models
        or os.environ.get(ALLOW_LOCAL_ENV) == "1"
    )
    if not allowed:
        print(
            "Refusing to load embedding models without confirmation.\n"
            "  Encoding a full corpus needs a GPU node and can exhaust a workstation.\n\n"
            "  On a compute node:  clir progressive eval ... --allow-local\n"
            f"  Or set {ALLOW_LOCAL_ENV}=1, or allow_local_models = true under [eval] in clir.toml",
        )
        return 2

    import numpy as np

    schema = context.schema
    dataset_repo = context.hf_repo("progressive_repo", args.repo)
    if not dataset_repo:
        raise ValueError("no dataset repo: pass --repo or set progressive_repo in clir.toml")
    corpus_repo = (
        args.corpus_repo
        if args.corpus_repo is not None
        else context.setting("corpus_repo", context.settings.eval.corpus_repo)
    )
    if not corpus_repo:
        raise ValueError("no haystack: pass --corpus-repo or set corpus_repo in clir.toml")

    models = _models(args, context)
    batch_size = args.batch_size or context.settings.eval.batch_size
    revision = "main"

    rung_id: dict[str, dict[int, str]] = defaultdict(dict)
    rung_text: dict[str, str] = {}
    mode_at_depth: dict[str, dict[int, str]] = defaultdict(dict)
    base_families: set[str] = set()
    for row in _load_config(dataset_repo, "corpus", revision):
        variant_id, base, depth = str(row["_id"]), str(row["base_id"]), int(row["depth"])
        rung_id[base][depth] = variant_id
        rung_text[variant_id] = _doc_text(row.get("title"), row.get("text"))
        mode_at_depth[base][depth] = str(row.get("mode_added") or "")
        family = str(row.get("source_publication_number") or "").strip()
        if family:
            base_families.add(family)

    queries = [
        {
            "query_id": str(row["_id"]),
            "text": str(row["text"]),
            "base_id": str(row.get("base_id") or _strip_query_suffix(str(row["_id"]))),
            "query_language": str(row.get("query_language") or "").strip(),
        }
        for row in _load_config(dataset_repo, "queries", revision)
    ]
    queries = [q for q in queries if q["base_id"] in rung_id]

    # ``--limit`` selects base documents, not queries, so a bounded run still
    # evaluates complete ladders.
    selected = list(dict.fromkeys(q["base_id"] for q in queries))
    if args.limit is not None:
        selected = selected[: args.limit]
    keep = set(selected)
    queries = [q for q in queries if q["base_id"] in keep]
    if not queries:
        raise ValueError(f"no queries to evaluate (check the dataset at {dataset_repo})")

    print(
        f"Progressive eval: {len(queries)} queries over {len(selected)} base docs, "
        f"{len(models)} model(s), dataset={dataset_repo}, haystack={corpus_repo}"
    )

    from clir_bench.evaluation.harness import load_corpus_dataset

    haystack_ids: list[str] = []
    haystack_texts: list[str] = []
    for row in load_corpus_dataset(corpus_repo, revision):
        doc_id = str(row.get("id") or row.get("_id") or "")
        if schema.family_from_doc_id(doc_id) in base_families:
            continue
        haystack_ids.append(doc_id)
        haystack_texts.append(_doc_text(row.get("title"), row.get("text")))
    print(
        f"  haystack: {len(haystack_ids)} docs "
        f"(dropped {len(base_families)} base publications)"
    )

    # Model loading, HF caching and the position_ids repair are the evaluation
    # layer's business, so this command goes through exactly the same door as
    # ``clir eval run``.
    from clir_bench.evaluation import models as model_loading

    model_cache = model_loading.configure_hf_cache(context.project_root)
    cache_dir = context.workspace.data("progressive") / "emb"
    meta = _task_metadata()
    records: list[dict[str, Any]] = []

    for name in models:
        slug = slugify_model(name)
        print(f"\nModel: {name}")
        try:
            model, _model_meta = model_loading.load_model(name, cache_dir=model_cache)
        except Exception as exc:  # noqa: BLE001 - gated weights, missing extras
            print(f"  [skip] could not load `{name}`: {exc}")
            continue
        try:
            haystack = _haystack_embeddings(
                model, slug, haystack_ids, haystack_texts, meta, batch_size, cache_dir
            )
            rung_ids = [rung_id[b][k] for b in selected for k in sorted(rung_id[b])]
            rungs = _encode(model, [rung_text[v] for v in rung_ids], "document", meta, batch_size)
            rung_vectors = {vid: rungs[i] for i, vid in enumerate(rung_ids)}
            query_vectors = _encode(
                model, [q["text"] for q in queries], "query", meta, batch_size
            )
        except Exception as exc:  # noqa: BLE001 - one bad model must not lose the rest
            print(f"  [skip] encoding failed for `{name}`: {exc}")
            continue

        for index, query in enumerate(queries):
            vector = query_vectors[index]
            base = query["base_id"]
            haystack_scores = haystack @ vector
            previous = None
            for depth in sorted(rung_id[base]):
                score = float(rung_vectors[rung_id[base][depth]] @ vector)
                # Rungs are never in the haystack, so no sibling exclusion is
                # needed: everything scoring above this rung is a true competitor.
                rank = int(1 + np.count_nonzero(haystack_scores > score))
                record = {
                    "model": name,
                    "model_slug": slug,
                    "query_id": query["query_id"],
                    "query_language": query["query_language"],
                    "base_id": base,
                    "depth": depth,
                    "mode_added": mode_at_depth[base].get(depth, ""),
                    "score": score,
                    "rank": rank,
                    "rr": 1.0 / rank,
                    "cos_drop_from_prev": (previous - score) if previous is not None else np.nan,
                }
                for cutoff in RECALL_CUTOFFS:
                    record[f"r{cutoff}"] = int(rank <= cutoff)
                records.append(record)
                previous = score

    if not records:
        raise RuntimeError("no records produced -- every model failed to load or encode")

    output_dir = context.workspace.runs_dir / RUN_LABEL
    summary_path = _write_outputs(records, output_dir, len(haystack_ids))
    print(f"\nWrote summary -> {summary_path}")
    return 0


def _write_outputs(records: list[dict[str, Any]], output_dir: Path, n_haystack: int) -> Path:
    import pandas as pd

    frame = pd.DataFrame(records)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "experimental_plots").mkdir(exist_ok=True)
    (output_dir / "key_findings").mkdir(exist_ok=True)
    frame.to_parquet(output_dir / "curve_records.parquet", index=False)

    aggregates = {
        "n": ("query_id", "nunique"),
        "mean_cos": ("score", "mean"),
        "mrr": ("rr", "mean"),
        **{f"recall_at_{c}": (f"r{c}", "mean") for c in RECALL_CUTOFFS},
        "median_rank": ("rank", "median"),
    }
    summary = frame.groupby(["model", "depth"]).agg(**aggregates).reset_index()
    summary_path = output_dir / "curve_summary.csv"
    summary.to_csv(summary_path, index=False)

    # Same curves split by query language: with strategy=all queries this
    # separates monolingual decay (query language == anchor) from cross-lingual.
    by_language = (
        frame.groupby(["model", "query_language", "depth"])
        .agg(
            n=("query_id", "nunique"),
            mean_cos=("score", "mean"),
            mrr=("rr", "mean"),
            recall_at_10=("r10", "mean"),
            recall_at_100=("r100", "mean"),
        )
        .reset_index()
    )
    by_language.to_csv(output_dir / "curve_summary_by_language.csv", index=False)

    mode_breakdown = (
        frame[frame["depth"] >= 1]
        .groupby(["model", "mode_added"])
        .agg(n=("query_id", "size"), mean_cos_drop=("cos_drop_from_prev", "mean"))
        .reset_index()
    )
    mode_breakdown.to_csv(output_dir / "mode_breakdown.csv", index=False)

    _plot_curves(summary, output_dir / "experimental_plots" / "decay_curve.png")
    _write_findings(
        frame, summary, mode_breakdown, n_haystack, output_dir / "key_findings" / "summary.md"
    )
    print(summary.to_string(index=False))
    return summary_path


def _plot_curves(summary, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    panels = [
        ("recall_at_10", "Recall@10"),
        ("mrr", "MRR"),
        ("mean_cos", "Mean cosine(query, doc)"),
    ]
    figure, axes = plt.subplots(1, len(panels), figsize=(15, 4.2))
    for axis, (column, title) in zip(axes, panels):
        for model, group in summary.groupby("model"):
            group = group.sort_values("depth")
            axis.plot(group["depth"], group[column], marker="o", label=model.split("/")[-1])
        axis.set_xlabel("# replacements (code-switch depth)")
        axis.set_ylabel(title)
        axis.set_title(f"{title} vs depth")
        axis.grid(True, alpha=0.3)
    axes[0].legend(fontsize=7, loc="best")
    figure.suptitle("Progressive code-switching: retrieval decay vs dose", fontweight="bold")
    figure.tight_layout()
    figure.savefig(path, dpi=130)
    plt.close(figure)
    print(f"Wrote plot -> {path}")


def _write_findings(frame, summary, mode_breakdown, n_haystack: int, path: Path) -> None:
    max_depth = int(frame["depth"].max())
    lines = [
        "# Progressive code-switching -- retrieval decay\n",
        f"- **{frame['base_id'].nunique()}** base documents, ladder depth 0..{max_depth}, "
        f"haystack = **{n_haystack}** docs (base publications removed).\n",
    ]
    for model, group in summary.groupby("model"):
        group = group.sort_values("depth")
        clean = group[group.depth == 0]
        worst = group[group.depth == max_depth]
        r10_0, r10_n = clean["recall_at_10"].iloc[0], worst["recall_at_10"].iloc[0]
        cos_0, cos_n = clean["mean_cos"].iloc[0], worst["mean_cos"].iloc[0]
        lines.append(
            f"- `{model}`: recall@10 {r10_0:.2f} -> {r10_n:.2f} "
            f"(delta={r10_0 - r10_n:+.2f}); mean cosine {cos_0:.3f} -> {cos_n:.3f}.\n"
        )
    lines.append("\n## Per-step cosine drop by swap mode\n")
    for model, group in mode_breakdown.groupby("model"):
        parts = ", ".join(f"{r.mode_added}={r.mean_cos_drop:.4f}" for r in group.itertuples())
        lines.append(f"- `{model}`: {parts}\n")
    path.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote findings -> {path}")


__all__ = ["ALLOW_LOCAL_ENV", "RECALL_CUTOFFS", "RUN_LABEL", "evaluate_progressive"]
