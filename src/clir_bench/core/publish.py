"""
Publishing datasets to the Hugging Face Hub in MTEB retrieval format.

Collapses five copies of the auth / create_repo / push-each-config / upload-card
skeleton. What each dataset *contains* genuinely differs, so config builders stay
with their benchmarks; only the mechanics live here.

Two things in this module are load-bearing and were ported deliberately, not
rewritten:

* **qrels semantics.** Corpora with explicit parallel-document links use only
  the source document and its declared direct partners as positives. Legacy
  corpora retain family-based relevance and their cross-language fallback.
* **Attribution scoping.** Cards are composed from the attribution of the source
  the data actually came from. The old code attached the Google Patents CC BY 4.0
  block to EPO-derived datasets too; here a card is built per source and an
  unknown source raises.
"""

from __future__ import annotations

import json
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
        document = {
            "_id": doc_id,
            "corpus_id": doc_id,
            "title": row.get("title", ""),
            "text": schema.text_of(row),
            "corpus_language": schema.language_of(row),
            schema.family_field: schema.family_of(row),
        }
        for name in schema.export_metadata_fields:
            if name in row:
                document[name] = row[name]
        if schema.parallel_ids_field and schema.parallel_ids_field in row:
            document[schema.parallel_ids_field] = _parallel_ids(
                row[schema.parallel_ids_field], doc_id, schema.parallel_ids_field
            )
        out.append(document)
    return out


def _parallel_ids(value: Any, doc_id: str, field_name: str) -> list[str]:
    """Read explicit relevance links without accepting malformed metadata."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Document {doc_id!r} has invalid JSON in {field_name}") from exc
    if (not isinstance(value, list)
            or any(not isinstance(item, str) or not item.strip() or item != item.strip()
                   for item in value)
            or len(value) != len(set(value))):
        raise ValueError(f"Document {doc_id!r} requires unique nonempty IDs in {field_name}")
    return list(value)


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
    passthrough_fields: Sequence[str] = (
        "mode", "strategy", "strategy_name", "question_type", "source_document_id",
    ),
) -> RetrievalConfigs:
    """Turn a corpus and its QAC rows into MTEB retrieval configs.

    Explicit parallel links take precedence over family membership. They are
    direct edges, never transitive equivalence classes. The cross-language
    variant includes only queries with a known partner in another language.
    Corpora without explicit links retain the historical family-based behavior.
    """
    ids_by_family: dict[str, list[str]] = {}
    language_by_id: dict[str, str] = {}
    known_ids: set[str] = set()
    parallel_by_id: dict[str, list[str]] = {}
    for row in corpus:
        doc_id = schema.id_of(row)
        if not doc_id:
            continue
        known_ids.add(doc_id)
        language_by_id[doc_id] = schema.language_of(row)
        if schema.parallel_ids_field and schema.parallel_ids_field in row:
            if doc_id in parallel_by_id:
                raise ValueError(f"Duplicate document ID in explicit-pair corpus: {doc_id!r}")
            parallel_by_id[doc_id] = _parallel_ids(
                row[schema.parallel_ids_field], doc_id, schema.parallel_ids_field
            )
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
        if parallel_by_id:
            recorded_id = str(row.get("source_document_id", "") or "").strip()
            if recorded_id and doc_id and recorded_id != doc_id:
                raise ValueError("QAC source_document_id disagrees with its corpus document ID")
            doc_id = recorded_id or doc_id
            if doc_id not in parallel_by_id:
                raise ValueError(f"QAC source {doc_id!r} has no explicit pair metadata in the corpus")
        language = str(
            row.get("question_language") or row.get(schema.language_field) or ""
        ).strip()
        question = row.get(question_field, "")
        answer = row.get(answer_field, "")
        family = schema.family_of(row)

        query_id = _mint_query_id(schema, doc_id if doc_id in known_ids else "", language, index, seen)

        if parallel_by_id:
            relevant = list(dict.fromkeys(
                [doc_id, *(target for target in parallel_by_id[doc_id] if target in known_ids)]
            ))
            cross_relevant = [target for target in relevant
                              if language_by_id.get(target) and language_by_id[target] != language]
        else:
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
        if cross_relevant:
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
