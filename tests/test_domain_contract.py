"""
The domain contract, checked against the one domain that implements it.

These tests double as the specification a second domain must satisfy: anything
asserted here is something ``domains/legal/`` will also have to get right.
"""

from __future__ import annotations

import pytest

from clir_bench import domains
from clir_bench.core.domain import DomainSpec


@pytest.fixture(scope="module")
def spec() -> DomainSpec:
    return domains.load("chem_patents")


def test_domains_are_discoverable_without_importing_them() -> None:
    assert "chem_patents" in domains.available()


def test_unknown_domain_reports_what_is_available() -> None:
    with pytest.raises(domains.DomainNotFound) as excinfo:
        domains.load("legal")
    assert "chem_patents" in str(excinfo.value)


def test_every_source_declares_an_attribution(spec: DomainSpec) -> None:
    """Publishing data without naming its provider is a licensing failure."""
    for source in spec.sources:
        assert spec.attribution_for(source.name).strip()


def test_attributions_are_not_interchangeable(spec: DomainSpec) -> None:
    """Each source's licence text must be specific to that source.

    The predecessor attached the Google Patents CC BY 4.0 notice to EPO-derived
    datasets, crediting a provider the data did not come from.
    """
    gp = spec.attribution_for("gp")
    epo = spec.attribution_for("epo")
    assert gp != epo
    assert "CC BY 4.0" in gp and "provided by IFI CLAIMS" in gp
    assert "European Patent Office" in epo
    # The EPO block may mention the Google attribution, but only to disclaim it.
    assert "provided by IFI CLAIMS" not in epo
    assert "does **not** apply" in epo


def test_working_languages_have_names_and_prompts(spec: DomainSpec) -> None:
    from clir_bench.core.prompts import PromptPack

    pack = PromptPack(package=spec.prompts_package)
    for language in spec.languages.working:
        assert spec.languages.name_of(language) != language, f"no display name for {language}"
    for mode in spec.analysis.modes:
        available = pack.available_languages(mode)
        missing = set(spec.languages.working) - set(available)
        assert not missing, f"mode {mode} has no generation prompt for {sorted(missing)}"


def test_schema_round_trips_document_ids(spec: DomainSpec) -> None:
    schema = spec.schema
    doc_id = schema.make_doc_id("EP-3686982-A1", "de")
    assert doc_id == "EP-3686982-A1_de"
    assert schema.language_from_doc_id(doc_id) == "de"
    assert schema.family_from_doc_id(doc_id) == "EP-3686982-A1"


def test_language_inference_ignores_ids_without_a_language_suffix(spec: DomainSpec) -> None:
    """Shared-haystack documents may not encode a language; that must not crash."""
    assert spec.schema.language_from_doc_id("EP-3686982-A1") == ""
    assert spec.schema.family_from_doc_id("EP-3686982-A1") == "EP-3686982-A1"


def test_text_falls_through_an_empty_field(spec: DomainSpec) -> None:
    """A present-but-empty context must fall through to the abstract.

    The old English-first pipeline used dict-default chaining here, so an empty
    context skipped a non-empty abstract and landed on the title.
    """
    row = {"context": "", "abstract": "An abstract.", "title": "A title"}
    assert spec.schema.text_of(row) == "An abstract."


def test_dedup_key_normalizes_across_source_formats(spec: DomainSpec) -> None:
    """The two sources format publication numbers differently.

    This normalization is what keeps the corpora disjoint; without it the same
    patent appears twice under two spellings.
    """
    from_gp = {"publication_number": "EP-3686982-A1", "country_code": "EP"}
    from_epo = {"publication_number": "3686982", "country_code": "EP"}
    assert spec.schema.dedup_key(from_gp) == spec.schema.dedup_key(from_epo)


def test_data_layout_resolves_under_the_data_root(spec: DomainSpec) -> None:
    from pathlib import Path

    from clir_bench.core.paths import Workspace

    workspace = Workspace.build(
        data_dir=Path("/tmp/data"), reports_dir=Path("/tmp/reports"), domain=spec
    )
    assert workspace.data("gp_corpus") == Path("/tmp/data/google_patents/multilingual_corpus.csv")
    with pytest.raises(KeyError):
        workspace.data("no_such_key")


def test_declared_plans_are_callable(spec: DomainSpec) -> None:
    assert spec.qac_plans, "a domain with no generation plan cannot build a benchmark"
    for name, builder in spec.qac_plans.items():
        assert callable(builder), f"plan {name} is not callable"
