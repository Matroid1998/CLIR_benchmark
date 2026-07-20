"""
Publishing datasets to the Hugging Face Hub in MTEB retrieval format.

Collapses five copies of the auth / create_repo / push-each-config / upload-card
skeleton. What each dataset *contains* genuinely differs, so config builders stay
with their benchmarks; only the mechanics live here.

Two things in this module are load-bearing and were ported deliberately, not
rewritten:

* **qrels semantics.** Every document sharing a family key is a positive for a
  query about that family, and the cross-language variant keeps only positives
  in a different language than the query (falling back to all positives when
  that would empty the set). Changing this changes what published scores mean.
* **Attribution scoping.** Cards are composed from the attribution of the source
  the data actually came from. The old code attached the Google Patents CC BY 4.0
  block to EPO-derived datasets too; here a card is built per source and an
  unknown source raises.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from clir_bench.core.domain import CorpusSchema, DomainSpec

HF_TOKEN_VARS = ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN")


def hf_token(explicit: Optional[str] = None) -> str:
    token = explicit or next((os.environ.get(var) for var in HF_TOKEN_VARS if os.environ.get(var)), None)
    if not token:
        raise RuntimeError(
            f"No Hugging Face token: set one of {', '.join(HF_TOKEN_VARS)} in .env"
        )
    return token


@dataclass
class DatasetBundle:
    """A set of named configs ready to publish, plus its dataset card."""

    configs: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    card_body: str = ""

    def add(self, name: str, rows: Sequence[Mapping[str, Any]]) -> None:
        self.configs[name] = [dict(r) for r in rows]

    @property
    def names(self) -> list[str]:
        return list(self.configs)

    def summary(self) -> str:
        return ", ".join(f"{name}={len(rows)}" for name, rows in self.configs.items())


def card_yaml(config_names: Sequence[str]) -> str:
    """The ``configs:`` YAML header that tells the Hub how to load each config."""
    body = "".join(
        f"- config_name: {name}\n  data_files:\n  - split: train\n    path: data/{name}/*.parquet\n"
        for name in config_names
    )
    return f"---\nconfigs:\n{body}---\n"


def build_card(
    *,
    title: str,
    description: str,
    attribution: str,
    bundle: DatasetBundle,
    extra: str = "",
) -> str:
    """Compose a dataset card. ``attribution`` is required and never defaulted."""
    if not attribution.strip():
        raise ValueError("refusing to build a dataset card without an attribution block")
    sizes = "\n".join(f"- `{name}`: {len(rows)} rows" for name, rows in bundle.configs.items())
    sections = [
        card_yaml(bundle.names),
        f"# {title}\n",
        description.strip(),
        "\n## Configs\n",
        sizes,
        "\n## Source and licensing\n",
        attribution.strip(),
    ]
    if extra.strip():
        sections.extend(["\n", extra.strip()])
    if bundle.card_body.strip():
        sections.extend(["\n", bundle.card_body.strip()])
    return "\n".join(sections) + "\n"


def publish_bundle(
    bundle: DatasetBundle,
    repo_id: str,
    *,
    card: str,
    token: Optional[str] = None,
    private: bool = False,
    dry_run: bool = False,
    dry_run_dir: Optional[Path] = None,
    only_configs: Optional[Sequence[str]] = None,
) -> str:
    """Push every config to ``repo_id``; on ``dry_run`` write parquet locally.

    ``only_configs`` re-pushes a subset, leaving the others untouched -- needed
    when adding a column to a published dataset without rebuilding it.
    """
    from datasets import Dataset

    names = list(only_configs) if only_configs else bundle.names
    unknown = [n for n in names if n not in bundle.configs]
    if unknown:
        raise KeyError(f"cannot publish unknown config(s): {unknown}")

    if dry_run:
        target = Path(dry_run_dir or Path.cwd() / "hf_export")
        target.mkdir(parents=True, exist_ok=True)
        for name in names:
            config_dir = target / name
            config_dir.mkdir(parents=True, exist_ok=True)
            Dataset.from_list(bundle.configs[name]).to_parquet(str(config_dir / f"{name}.parquet"))
        (target / "README.md").write_text(card, encoding="utf-8")
        print(f"[dry run] wrote {len(names)} config(s) -> {target}")
        return str(target)

    from huggingface_hub import HfApi

    token = hf_token(token)
    api = HfApi(token=token)
    api.create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)

    for name in names:
        Dataset.from_list(bundle.configs[name]).push_to_hub(
            repo_id, config_name=name, data_dir=f"data/{name}", token=token
        )
        print(f"  pushed config {name} ({len(bundle.configs[name])} rows)")

    api.upload_file(
        path_or_fileobj=card.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
    )
    url = f"https://huggingface.co/datasets/{repo_id}"
    print(f"Published {repo_id}: {bundle.summary()}\n  {url}")
    return url


def upload_directory(
    local_dir: Path,
    repo_id: str,
    *,
    path_in_repo: str,
    token: Optional[str] = None,
) -> str:
    """Upload a folder of results/tables into a dataset repo."""
    from huggingface_hub import HfApi

    token = hf_token(token)
    api = HfApi(token=token)
    api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    api.upload_folder(
        folder_path=str(local_dir),
        path_in_repo=path_in_repo,
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
    )
    return f"https://huggingface.co/datasets/{repo_id}/tree/main/{path_in_repo}"


# --------------------------------------------------------------------------- #
# MTEB retrieval configs
# --------------------------------------------------------------------------- #

def corpus_rows(
    rows: Iterable[Mapping[str, str]], schema: CorpusSchema
) -> list[dict[str, Any]]:
    """Corpus documents in MTEB shape, carrying language and family metadata."""
    out = []
    for row in rows:
        doc_id = schema.id_of(row)
        if not doc_id:
            continue
        out.append(
            {
                "_id": doc_id,
                "corpus_id": doc_id,
                "title": row.get("title", ""),
                "text": schema.text_of(row),
                "corpus_language": schema.language_of(row),
                schema.family_field: schema.family_of(row),
            }
        )
    return out


@dataclass
class RetrievalConfigs:
    """The corpus/queries/qrels triple plus the cross-language variant."""

    corpus: list[dict[str, Any]]
    queries: list[dict[str, Any]]
    qrels: list[dict[str, Any]]
    cross_language_queries: list[dict[str, Any]]
    cross_language_qrels: list[dict[str, Any]]
    qac: list[dict[str, Any]]


def build_retrieval_configs(
    corpus: Sequence[Mapping[str, str]],
    qac: Sequence[Mapping[str, str]],
    schema: CorpusSchema,
    *,
    question_field: str = "question",
    answer_field: str = "answer",
    doc_id_field: str = "corpus_id",
    passthrough_fields: Sequence[str] = ("mode", "strategy", "strategy_name", "question_type"),
) -> RetrievalConfigs:
    """Turn a corpus and its QAC rows into MTEB retrieval configs.

    Relevance: a query generated from a document is relevant to *every* language
    version of that document -- they are translations of one another, so a
    retriever that returns the German version of the right document has
    succeeded. The cross-language variant drops the same-language versions to
    isolate genuinely cross-lingual retrieval.
    """
    ids_by_family: dict[str, list[str]] = {}
    language_by_id: dict[str, str] = {}
    known_ids: set[str] = set()
    for row in corpus:
        doc_id = schema.id_of(row)
        if not doc_id:
            continue
        known_ids.add(doc_id)
        language_by_id[doc_id] = schema.language_of(row)
        family = schema.family_of(row)
        if family:
            ids_by_family.setdefault(family, []).append(doc_id)

    queries: list[dict[str, Any]] = []
    qrels: list[dict[str, Any]] = []
    cross_queries: list[dict[str, Any]] = []
    cross_qrels: list[dict[str, Any]] = []
    triplets: list[dict[str, Any]] = []
    seen: set[str] = set()

    for index, row in enumerate(qac):
        doc_id = str(row.get(doc_id_field, "") or "").strip()
        language = str(
            row.get("question_language") or row.get(schema.language_field) or ""
        ).strip()
        question = row.get(question_field, "")
        answer = row.get(answer_field, "")
        family = schema.family_of(row)

        query_id = _mint_query_id(schema, doc_id if doc_id in known_ids else "", language, index, seen)

        relevant = list(ids_by_family.get(family, []))
        if not relevant and doc_id:
            relevant = [doc_id]
        cross_relevant = [d for d in relevant if language_by_id.get(d, "") != language] or list(relevant)

        source_language = language_by_id.get(doc_id, "")
        query_row: dict[str, Any] = {
            "_id": query_id,
            "query_id": query_id,
            "text": question,
            "query_language": language,
            "source_language": source_language,
            # True when the question language differs from its source document's
            # language, i.e. the question is a translation rather than native.
            "is_synthetic_translation": bool(language and source_language and language != source_language),
            schema.family_field: family,
        }
        for name in passthrough_fields:
            if name in row:
                query_row[name] = str(row.get(name, "") or "").strip()

        queries.append(query_row)
        cross_queries.append(dict(query_row))
        for target in relevant:
            qrels.append({"query-id": query_id, "corpus-id": target, "score": 1})
        for target in cross_relevant:
            cross_qrels.append({"query-id": query_id, "corpus-id": target, "score": 1})

        triplets.append({**query_row, "question": question, "answer": answer, "corpus_id": doc_id})

    return RetrievalConfigs(
        corpus=corpus_rows(corpus, schema),
        queries=queries,
        qrels=qrels,
        cross_language_queries=cross_queries,
        cross_language_qrels=cross_qrels,
        qac=triplets,
    )


def _mint_query_id(
    schema: CorpusSchema, doc_id: str, language: str, index: int, seen: set[str]
) -> str:
    """Deterministic query id, with an index suffix only on collision."""
    query_id = schema.make_query_id(doc_id, language) if doc_id else f"q_{index}_{language}"
    if query_id in seen:
        query_id = f"{query_id}_{index}"
    seen.add(query_id)
    return query_id


def bundle_from_configs(configs: RetrievalConfigs) -> DatasetBundle:
    """Standard config naming used by every benchmark this project publishes."""
    bundle = DatasetBundle()
    bundle.add("corpus", configs.corpus)
    bundle.add("queries", configs.queries)
    bundle.add("qrels", configs.qrels)
    bundle.add("qac", configs.qac)
    bundle.add("cross_language-corpus", configs.corpus)
    bundle.add("cross_language-queries", configs.cross_language_queries)
    bundle.add("cross_language-qrels", configs.cross_language_qrels)
    return bundle


__all__ = [
    "DatasetBundle",
    "RetrievalConfigs",
    "build_card",
    "build_retrieval_configs",
    "bundle_from_configs",
    "card_yaml",
    "corpus_rows",
    "hf_token",
    "publish_bundle",
    "upload_directory",
]
