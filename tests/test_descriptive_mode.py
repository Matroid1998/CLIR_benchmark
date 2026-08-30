"""The `descriptive` mode: a technical-family fact-extraction mode whose QUESTION
describes an instrument instead of citing it. Shares the technical quality
columns. Only the UN pack still exposes it -- EUR-Lex generation was cut down to
`lookup` and `fact_pattern` (see test_eurlex_modes.py), so the pack loop below
is deliberately UN-only rather than both legal packs."""

from __future__ import annotations

from clir_bench.core.grading import (
    MODE_DESCRIPTIVE, SEMANTIC_QUALITY_FIELDS, SEMANTIC_QUALITY_KEYS,
    TECHNICAL_QUALITY_FIELDS, TECHNICAL_QUALITY_KEYS, quality_fields, quality_keys,
)
from clir_bench.core.prompts import PromptPack

UN = PromptPack("clir_bench.domains.legal.qac.prompts_un")


def test_descriptive_uses_technical_quality_columns():
    assert quality_keys(MODE_DESCRIPTIVE) == TECHNICAL_QUALITY_KEYS
    assert quality_fields(MODE_DESCRIPTIVE) == TECHNICAL_QUALITY_FIELDS
    # unchanged for the other two
    assert quality_keys("technical") == TECHNICAL_QUALITY_KEYS
    assert quality_keys("semantic") == SEMANTIC_QUALITY_KEYS
    assert quality_fields("semantic") == SEMANTIC_QUALITY_FIELDS


def test_both_packs_expose_descriptive_prompts():
    for pack in (UN,):
        assert pack.generation("descriptive", "en")
        assert pack.quality("descriptive", "batch")
        assert "en" in pack.available_languages("descriptive")


def test_descriptive_generation_forbids_identifiers_in_the_question():
    for pack in (UN,):
        g = pack.generation("descriptive", "en").lower()
        assert "describe" in g and "identifier" in g
        # the JSON schema stays the technical one: question_type, no framing
        assert "question_type" in g and '"framing"' not in g


def test_descriptive_verifier_has_identifier_leak_check():
    for pack in (UN,):
        v = pack.quality("descriptive", "batch")
        assert "identifier-leak" in v
        # shares the technical five sub-criteria (specificity, not retrievability)
        assert "specificity" in v.lower() and "retrievability" not in v.lower()


def test_generate_routes_descriptive_to_question_type():
    from clir_bench.domains.legal.qac import un_generate as un
    payload_json = [{"question": "q", "answer": "a", "question_type": "operative_action"}]
    (c,) = un.parse_candidates(payload_json, "descriptive")
    assert c.classification == "operative_action"
    # semantic still reads framing, so a descriptive payload's question_type is used
    (c2,) = un.parse_candidates(payload_json, "semantic")
    assert c2.classification == "other"           # no framing key present
    assert un.MODE_DESCRIPTIVE == "descriptive"
