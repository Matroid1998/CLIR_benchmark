# UN Parallel Corpus prompts

Prompt pack for the UN Parallel Corpus source (`data/legal/un_parallel/`), where
the retrievable unit is a **block** — a contiguous run of lines of one UN
document, packed to a size window at English paragraph boundaries. Junk lines
(mastheads, TOC rows, vote rosters, adoption formulas) act as block boundaries
and fall into the gaps between blocks; section headings open the block that
follows them, so a block carries its section title. It exists as
a separate pack rather than an edit to `prompts_eurlex/` because the central
rule of that pack is **inverted back** here, and because the corpus mixes
genres (resolutions, reports, letters, meeting records) that EU legislation
does not have.

Loaded with `PromptPack("clir_bench.domains.legal.qac.prompts_un")`. Nothing in
`core/` knows about any of this.

    generation/technical/{en}.txt
    generation/semantic/{en}.txt
    verifiers/{faithfulness,technical,semantic}_batch.txt

English question-language only for now. Adding a language is a full-file
translation with the same convention as `prompts_eurlex`: the literal markers,
JSON keys, and enum values stay in English verbatim; only the explanatory text
is translated.

## The payload contract

The prompts describe — and therefore pin — the user message the future
`un_context` renderer must emit (the analog of `eurlex_context.render_payload`):

    ### TARGET BLOCK — write the questions about THIS text
    [EN] Document: S/2001/535
      Title: Letter dated 1 June 2001 from the Permanent Representatives ...
    <block text>

    ### REFERENCED DOCUMENTS — other documents CITED by the target block, supplied so an answer can be complete
    Reference: S/RES/1559(2004) — Resolution 1559 (2004) (cited paragraph 3)
    <the cited document's FULL text on whole-fit runs (reference_chars=None);
     otherwise the cited paragraph's block or the opening block, capped at 1500 chars>

    ### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only
    <document opening + neighbouring blocks, or the whole document when it fits the budget>

Both `###` markers are literal strings. Metadata lines are `Document:` (the UN
document symbol) and `Title:` (the document's first content line, masthead
stripped); they get the same "context, not content" treatment as EUR-Lex's
`Act:`/`Location:` lines. Non-English payload variants add the question-language version of each
block alongside English, as in the EUR-Lex flow.

## What changed vs. `prompts_eurlex`, and why

### 1. Two kinds of supporting material, two different rules

The payload carries both EUR-Lex-style **resolved references** and a section
EUR-Lex never had — the **surrounding document** — and they obey different
rules:

- **REFERENCED DOCUMENTS** (instruments the target block cites, resolved by
  `un_references.py` regex extraction against the corpus's own symbol index)
  follow the EUR-Lex semantics: a supplied excerpt may **complete** an answer
  whose operative fact lives in the target block; the ONE-DOCUMENT TEST
  discards questions answerable from a reference alone; candidates declare
  what they used in **`documents_involved`** (symbols, validated in
  `un_generate.normalise_involved` against what was actually supplied).
- **DOCUMENT CONTEXT** stays disambiguation-only: it resolves "the Mission",
  "the present report", "the reporting period" — and is never a source of
  answer substance (the BLOCK TEST; faithfulness caps GROUNDING at 2 on
  violations).

Output is `{question, answer, question_type|framing, documents_involved}`.

### 2. Naming for retrievability is promoted to the top rule

The corpus is institutionally repetitive: thousands of resolutions authorize
troop levels and extend mandates in identical language. Both generation prompts
carry a dedicated NAMING FOR RETRIEVABILITY section ("the most important rule
of this task"): every question must name the situation, country, mission, body,
or instrument; never "this resolution" / "the present report" / a bare
paragraph number. Technical mode may use identifiers from the metadata
(`resolution 918 (1994)`); semantic mode must anchor with proper nouns and
subject matter instead (identifiers are an identifier-leak there). The quality
verifiers back this with an ANCHOR CHECK (`no-anchor`, specificity ≤ 2) and the
semantic BOILERPLATE CHECK.

### 3. Two genre rules EU legislation never needed

- **Preambular vs. operative** — resolution preambles ("Reaffirming...") are
  framing, not answer material; questions target operative or substantive
  content.
- **Attribution** — summary records, letters, and reports state what a speaker
  or body *said*. Questions and answers must preserve attribution ("According
  to the Secretary-General's May 1994 report...") and never present an
  attributed claim as established fact. Enforced in the faithfulness verifier
  (ATTRIBUTION RULE, grounding cap 2) and the quality verifiers
  (`missing-attribution`).

### 4. Categories and framings

Technical mode targets eight UN categories (`question_type` slugs):
situation_scope_or_coverage, operative_action,
sanction_condition_or_consequence, date_deadline_or_mandate,
quantity_force_or_finance, reporting_monitoring_or_verification,
finding_event_or_assessment, actor_body_or_procedure. Relative to EUR-Lex,
"Conditions" and "Enforcement" merge into the sanctions category (in UN
practice one machine), freeing a slot for **Findings, Events & Assessments** —
the category reports live on.

Semantic mode uses three framings (`framing` values): **situation**,
**response**, **stakeholder** — the UN reading of EUR-Lex's
problem/solution/application.

### 5. Verifiers

Adapted from the EUR-Lex versions; the JSON keys the graders emit are unchanged
(`grounding`, `precision`, `numerical_fidelity`; the five quality keys), so
`core.grading` needs no modification. The `articles_involved` provenance caps
are replaced by the context-leak cap; new failure_types: `off-target-context`,
`no-anchor`, `missing-attribution`. The unresolved-citation check survives
unchanged in spirit: UN texts cite other resolutions constantly and nothing
resolves them.
