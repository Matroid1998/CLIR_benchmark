"""
Article-level structure and cross-reference metadata for EUR-Lex acts.

This subtree turns whole-act EUR-Lex texts into three flat JSONL artifacts:

    article records      one row per (act, article, language)
    internal edges       article -> article, intra-act only
    external references  flagged, never resolved

It is deliberately self-contained. The legal domain has no ``DomainSpec`` yet,
so nothing here is wired into the ``clir`` CLI and ``domains.available()`` still
reports only the domains that expose a ``SPEC``. Each stage is a module with a
``main()``, run as ``python -m clir_bench.domains.legal.structure.<stage>``.

Design decisions that are load-bearing, recorded here because they are not
obvious from the code:

* **Formex, 2004 onward.** CELLAR serves Formex XML only for acts published from
  roughly 2004. Older acts 404 for both Formex and XHTML and survive only as
  flat legacy HTML, so the corpus is scoped to the Formex era rather than mixing
  two very different segmentation qualities in one artifact.

* **English-only extraction, structural projection.** Article numbering is
  identical across language versions by drafting rule, so references are
  extracted once from English and projected onto the other languages by joining
  on article number. Measured per-language extraction varies by 30-50% on the
  same act, so the projection is not merely cheaper, it is more consistent.

* **ELI URIs are looked up, not derived.** ``32014R0680`` is *not*
  ``eli/reg/2014/680`` -- it is ``eli/reg_impl/2014/680``. Implementing and
  delegated acts carry distinct ELI subtypes, so the act's ELI comes from
  CELLAR's ``identifiers`` notice and only the ``art_N`` subdivision is appended.
"""

from __future__ import annotations

__all__ = ["ACT_LANGUAGES"]

# The four languages this benchmark uses for EUR-Lex. Chinese comes from the UN
# corpus and is deliberately absent here.
ACT_LANGUAGES = ("en", "fr", "de", "es")
