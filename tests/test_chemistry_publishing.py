"""Published relevance follows accepted direct pairs, not publication closure."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from clir_bench.core import publish
from clir_bench.domains.chemistry.schema import SCHEMA


def paired_corpus():
    # EN--ZH--FR is accepted, but EN--FR was not accepted. DE shares the
    # publication while its only accepted endpoint lies outside this export.
    neighbors = {"en": ["zh"], "zh": ["en", "fr"], "fr": ["zh"], "de": ["es"]}
    return [{"id": f"EP-123-A1_{language}", "publication_number": "EP-123-A1",
             "language": language, "context": f"Abstract in {language}",
             "paired_document_ids": json.dumps([f"EP-123-A1_{other}" for other in partners])}
            for language, partners in neighbors.items()]


def query(language="en", **overrides):
    return {"corpus_id": f"EP-123-A1_{language}",
            "source_document_id": f"EP-123-A1_{language}", "question_language": language,
            "publication_number": "EP-123-A1", "question": "Question", "answer": "Answer", **overrides}


def test_qrels_follow_only_direct_accepted_edges():
    configs = publish.build_retrieval_configs(paired_corpus(), [query()], SCHEMA)
    assert {row["corpus-id"] for row in configs.qrels} == {"EP-123-A1_en", "EP-123-A1_zh"}
    assert {row["corpus-id"] for row in configs.cross_language_qrels} == {"EP-123-A1_zh"}
    assert configs.queries[0]["source_document_id"] == "EP-123-A1_en"
    assert configs.queries[0]["is_synthetic_translation"] is False
    assert configs.corpus[0]["paired_document_ids"] == ["EP-123-A1_zh"]


def test_each_source_document_uses_its_own_neighbors():
    configs = publish.build_retrieval_configs(paired_corpus(), [query("zh")], SCHEMA)
    assert {row["corpus-id"] for row in configs.cross_language_qrels} == {
        "EP-123-A1_en", "EP-123-A1_fr",
    }


def test_published_corpus_retains_upstream_provenance():
    corpus = paired_corpus()
    corpus[0].update(upstream_dataset="BASF-AI/source", upstream_revision="abc123",
                     upstream_corpus_id="publication:abstract", upstream_group_key="patent-family",
                     accepted_pair_ids='["accepted-en-zh"]')
    published = publish.corpus_rows(corpus, SCHEMA)[0]
    for field in SCHEMA.export_metadata_fields:
        if field != "paired_document_ids":
            assert published[field] == corpus[0][field]


def test_absent_partners_do_not_become_unknown_or_same_language_cross_positives():
    configs = publish.build_retrieval_configs(paired_corpus(), [query("de")], SCHEMA)
    assert {row["corpus-id"] for row in configs.qrels} == {"EP-123-A1_de"}
    assert configs.cross_language_qrels == []
    assert configs.cross_language_queries == []
    assert len(configs.queries) == 1


@pytest.mark.parametrize("value", [
    "", "not JSON", '"EP-123-A1_zh"', '{"id":"EP-123-A1_zh"}',
    [None], [True], [""], [" EP-123-A1_zh"], [["EP-123-A1_zh"]],
    ["EP-123-A1_zh", "EP-123-A1_zh"],
])
def test_malformed_explicit_links_fail_without_family_fallback(value):
    corpus = paired_corpus()
    corpus[0]["paired_document_ids"] = value
    with pytest.raises(ValueError, match="paired_document_ids"):
        publish.build_retrieval_configs(corpus, [query()], SCHEMA)


@pytest.mark.parametrize("source", ["EP-123-A1_missing", ""])
def test_unknown_query_source_does_not_inherit_family_positives(source):
    with pytest.raises(ValueError, match="no explicit pair metadata"):
        publish.build_retrieval_configs(
            paired_corpus(), [query(corpus_id=source, source_document_id=source)], SCHEMA
        )


def test_query_source_ids_must_agree():
    with pytest.raises(ValueError, match="disagrees"):
        publish.build_retrieval_configs(
            paired_corpus(), [query(source_document_id="EP-123-A1_fr")], SCHEMA
        )


def test_mixed_corpus_cannot_silently_expand_a_source_with_missing_links():
    corpus = paired_corpus()
    corpus[0].pop("paired_document_ids")
    with pytest.raises(ValueError, match="no explicit pair metadata"):
        publish.build_retrieval_configs(corpus, [query()], SCHEMA)


def test_schema_without_link_declaration_keeps_legacy_family_semantics():
    legacy_schema = replace(SCHEMA, parallel_ids_field=None)
    configs = publish.build_retrieval_configs(paired_corpus(), [query()], legacy_schema)
    assert {row["corpus-id"] for row in configs.qrels} == {
        "EP-123-A1_en", "EP-123-A1_zh", "EP-123-A1_fr", "EP-123-A1_de",
    }


def test_old_rows_without_link_column_keep_legacy_family_semantics():
    corpus = [{key: value for key, value in row.items() if key != "paired_document_ids"}
              for row in paired_corpus()]
    configs = publish.build_retrieval_configs(corpus, [query()], SCHEMA)
    assert len(configs.qrels) == 4
