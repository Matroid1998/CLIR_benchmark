# EUR-Lex prompts

A variant of the `legal` prompt pack for acts whose **cross-references have been
resolved**. It exists as a separate pack rather than an edit to `legal/` because
the two disagree on a central rule, and that disagreement is the whole point.

Used by `clir_bench.domains.legal.qac.eurlex_generate`, which sends a three-block
payload (target, same-act references, other-act references) instead of a single
passage. Nothing in `core/` knows about any of this.

    generation/technical/{en,fr,de,es}.txt
    generation/semantic/{en,fr,de,es}.txt
    verifiers/{faithfulness,technical,semantic}_batch.txt

## What changed, and why

### 1. The input is three labelled blocks, not one passage

The user message now looks like:

    ### TARGET ARTICLE — write the questions about THIS article
    [EN] Article 4 — Placing on the market
    ...
    ### REFERENCED ARTICLES — supporting context only, cited by the target article.
    [EN] Article 3 — Covered products
    ...
    ### REFERENCED ARTICLES FROM OTHER ACTS — supporting context only, cited by the target article.
    [EN] Article 5 — Checks
      Act: Council Regulation (EC) No 21/2004 ...
      Cite as: 32004R0021:5
    ...

All three markers are literal strings emitted by `eurlex_context.render_payload`;
an empty block is rendered as an explicit "— none." line rather than omitted.
The third block holds articles of *other* acts that the target cites by name,
present only when `structure.resolve_external` could pin the cited act down to
one in the corpus (see that module: the year/number order is fixed by the
identifier's shape and never guessed). Each such article carries a `Cite as:`
key, `CELEX:number`, which is how the model refers to it. Translations keep the
markers and keys in English verbatim; only the explanatory text is translated.

Why separate rather than concatenate: given one undifferentiated blob the model
asks about whichever article reads most interestingly, which is usually not the
one we meant. The prompt therefore says the question is *about* the target, and
adds THE ONE-ARTICLE TEST — "could a reader answer this completely by reading
ONLY the referenced article, never having seen the target? If yes, discard it".

### 2. The cross-reference rule is **inverted**

This is the substantive change. The `legal` pack says:

> **Self-Contained (No Unresolved Cross-References):** … If the substance of the
> answer lies in a provision, annex, or instrument that the passage merely cites
> but does not state, discard the question.

and its worked example discards *"Which single-use plastic products are banned?"*
precisely because Annex B was not supplied.

The EUR-Lex pack says instead:

> **Resolved Cross-References Are Allowed and Wanted:** … When that cited article
> is supplied — in the REFERENCED ARTICLES block or in the REFERENCED ARTICLES
> FROM OTHER ACTS block — you MAY follow the citation and use its content to
> complete the answer. … If the answer's substance lies behind a citation that
> was NOT supplied, discard the question.

So the discard rule survives, but its trigger moves from *"is it behind a
citation"* to *"was the cited article actually supplied"*. Questions the old pack
threw away are now the interesting ones — they are the multi-article questions
the reference graph was built to enable.

### 3. New output field: `articles_involved`

Every candidate declares which articles a reader genuinely needs:

    {"question": "...", "answer": "...", "question_type": "...", "articles_involved": ["3", "4"]}

- answer wholly inside the target → `["4"]`
- answer completed by a followed reference → `["3", "4"]`
- answer completed by an article of another act → `["4", "32004R0021:5"]` — the
  `Cite as` key, never a bare number, so that a bare number can only ever mean
  the target's own act and nothing collides
- the target article is always present
- an article merely *cited* by the target, whose content was not used, must **not**
  be listed

Identifiers of *other* acts are forbidden in the question in **both** modes:
a query anchored on another act's identifier, CELEX number or `Cite as` key
retrieves that act, not the target. Technical mode may still name the target's
own instrument.

The field is a JSON key and stays untranslated in every language variant. In
semantic mode the prompt states explicitly that the no-identifiers rule applies
to the *question* only — `articles_involved` is metadata, not part of the query —
because otherwise the two rules appear to contradict each other.

### 4. Worked examples, including both mis-declaration failures and the cross-act case

Each generation prompt carries an example of the field being right in the
single-article case, right in the multi-article case, and wrong in **both**
directions:

- **under-declared** — the answer used Article 3 but listed only `["4"]`. Called
  out as a scoring error *even though the answer is correct*, because that is the
  failure a model will otherwise make constantly.
- **over-declared** — listed `["3", "4"]` for a date that is entirely in Article
  4, on the reasoning that Article 3 is cited nearby. This is the opposite
  failure and needs its own example; a single example teaches "list everything".
- **cross-act** (Example 5) — the target's payment condition is completed by an
  article of another act; the good answer declares `["2", "32004R0021:5"]`, the
  off-target question is answerable from the other act alone, and the
  "wrong anchor" question is built around the other act's identifier — the one
  identifier that is forbidden even in technical mode.

Plus a **wrong subject** example (a question that is really about the referenced
article) and an **unsupplied reference** example (the discard rule that survives).

### 5. Verifiers

`faithfulness_batch.txt` had to change or it would have failed every
multi-article answer:

- the input description now describes all three blocks and the `Cite as` keys,
  and the candidates it grades carry their declared `articles_involved`;
- the `CROSS-REFERENCE RULE` splits into case (a) *cited article was supplied* —
  following it is legitimate support, not inference — and case (b) *not supplied*
  — score at most 2, as before;
- `GROUNDING` now also checks provenance: **cap at 2** if `articles_involved` is
  wrong in either direction, **cap at 1** if the substance came from an article
  never supplied.

The JSON keys the grader emits are unchanged (`grounding`, `precision`,
`numerical_fidelity`), so `core.grading` needs no modification.

`technical_batch.txt` and `semantic_batch.txt` gain one rule: a question whose
subject matter lives entirely in a referenced article scores at most 2 for
retrieval quality, because it would retrieve the wrong article.

## Division of labour on `articles_involved`

The LLM grader judges whether the declaration is *semantically* right. Code in
`eurlex_context.normalise_involved` checks that it is *structurally* valid —
articles the model was never sent are rejected outright, the target is inserted
if omitted, and surface variants (`"Article 3"`, `"3"`, `"3 and 4"`) are
normalised. Rubrics grade that kind of thing badly; a validator does not.
