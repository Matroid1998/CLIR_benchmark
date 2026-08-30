# EUR-Lex prompts

A variant of the `legal` prompt pack for acts whose **cross-references have been
resolved**. It exists as a separate pack rather than an edit to `legal/` because
the two disagree on a central rule, and that disagreement is the whole point.

Used by `clir_bench.domains.legal.qac.eurlex_generate`, which sends a four-block
payload (target, same-act articles, other-act articles, annexes) instead of a
single passage. Nothing in `core/` knows about any of this.

    generation/lookup/{en,fr,de,es,zh}.txt
    generation/fact_pattern/{en,fr,de,es,zh}.txt
    verifiers/{faithfulness,lookup,fact_pattern}_batch.txt

The production question languages are en, fr, de, es (the batch driver's
default): the corpus has no zh act versions, so Chinese is not generated. The
zh prompt files exist as complete translations should a cross-language run
(question in a language the corpus lacks) ever be wanted, but no default run
uses them.

## The two modes

EUR-Lex generation is **`lookup` and `fact_pattern`, and nothing else**. The
earlier `technical` / `semantic` / `descriptive` trio was retired: all three
asked the model to write *about* an article, which produced grounded, precise
questions that no practitioner would ever type. `descriptive` survives in the UN
pack only (`prompts_un`), which still runs the older four.

Both new modes are framed from the **information need** rather than from the
text, and both are fact-extraction modes, so both reuse the *technical* quality
columns and `core.grading` needs no per-mode branch.

| | `lookup` | `fact_pattern` |
|---|---|---|
| the asker | knows the regime, wants one point of law | has a situation, not a citation |
| what pins the question to the act | a **regime anchor** — the regulated actor, product, activity, or a term of art unique to the regime | the **particulars** of the situation, at least two of them |
| identifiers | forbidden in `question`, required in `question_cited` | forbidden everywhere in the question |
| typical form | "How often must a UCITS management company's compliance officer report to senior management?" | "A water utility is holding a design contest, and the jury wants to rank entries partly on criteria that were not in the contest notice. Is that allowed?" |
| extra output fields | `question_cited`, `instrument_short_name`, `anchor` | `particulars` |

Both prompts carry the same three defences against the failure modes a
production run actually produced:

- **the sibling test** — EU legislation repeats the same provision across sister
  acts (the transposition clause in every directive; near-identical
  qualifying-holding rules across UCITS/AIFMD/MiFID/CRD/Solvency II; the same
  "all other companies" residual duty in every anti-dumping regulation). A
  question that would be an equally sensible question about a *different* act
  has no anchor and is discarded.
- **the boilerplate list** — transposition, application, entry-into-force,
  addressee, "binding in its entirety", bare repeal, committee-procedure and
  definitive-collection clauses are never asked about. An article made only of
  these returns a skip.
- **the informativeness test** — an answer that restates the question's own
  words or the pointer it was built from ("in relation to matters to which it
  applies") means the question is empty.

### Skipping

Both prompts answer a boilerplate-only article with

    [{"skip_reason": "transposition clause only"}]

rather than padding out three questions. `eurlex_generate.is_skip` /
`skip_reason` distinguish that from a malformed response; `parse_candidates`
returns no candidates either way, so the target simply contributes no rows.

## What changed relative to the `legal` pack, and why

### 1. The input is four labelled blocks, not one passage

The user message looks like:

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
    ### REFERENCED ANNEXES — annexes cited by the target article, of this act or of another act ...
    [EN] ANNEX I
      Act: Directive (EU) 2019/904 ...
      Cite as: 32019L0904:anx_1
    ...

All four markers are literal strings emitted by `eurlex_context.render_payload`;
an empty block is rendered as an explicit "— none." line rather than omitted.
The third block holds articles of *other* acts that the target cites by name,
present only when `structure.resolve_external` could pin the cited act down to
one in the corpus (see that module: the year/number order is fixed by the
identifier's shape and never guessed). Each such article carries a `Cite as:`
key, `CELEX:number`, which is how the model refers to it. The fourth block holds
annexes the target cites — of this act or of another act in the corpus — each
with a `Cite as:` key of the form `CELEX:anx_<id>`, declared the same way.

Why separate rather than concatenate: given one undifferentiated blob the model
asks about whichever article reads most interestingly, which is usually not the
one we meant. Both prompts therefore say the question is *about* the target, and
add THE ONE-ARTICLE TEST — "could a reader answer this completely by reading
ONLY the referenced article, never having seen the target? If yes, discard it".
In a production run, *every* multi-article question generated failed that test,
so both prompts carry the real failures as worked examples.

### 2. The cross-reference rule is **inverted**

This is the substantive change. The `legal` pack says:

> **Self-Contained (No Unresolved Cross-References):** … If the substance of the
> answer lies in a provision, annex, or instrument that the passage merely cites
> but does not state, discard the question.

The EUR-Lex pack says instead:

> **Resolved Cross-References Are Allowed and Wanted:** … When that cited article
> is supplied — in the REFERENCED ARTICLES block, the REFERENCED ARTICLES FROM
> OTHER ACTS block, or the REFERENCED ANNEXES block — you MAY follow the
> citation and use its content to complete the answer. … If the answer's
> substance lies behind a citation that was NOT supplied, discard the question.

So the discard rule survives, but its trigger moves from *"is it behind a
citation"* to *"was the cited article actually supplied"*. Questions the old pack
threw away are now the interesting ones — they are the multi-article questions
the reference graph was built to enable.

### 3. `articles_involved`

Every candidate declares which articles a reader genuinely needs:

- answer wholly inside the target → `["4"]`
- answer completed by a followed reference → `["3", "4"]`
- answer completed by an article of another act → `["4", "32004R0021:5"]` — the
  `Cite as` key, never a bare number, so that a bare number can only ever mean
  the target's own act and nothing collides
- answer completed by an annex (of any act) → `["4", "32019L0904:anx_1"]` — annexes
  are always declared by their `Cite as` key
- the target article is always present
- an article merely *cited* by the target, whose content was not used, must **not**
  be listed

Each prompt carries the field being right in the single-article case, right in
the multi-article case, and wrong in **both** directions — under-declared (called
out as a scoring error *even though the answer is correct*) and over-declared
(listing a cited article that contributed nothing). A single example teaches
"list everything".

Identifiers of *other* acts are forbidden in the question in **both** modes: a
query anchored on another act's identifier, CELEX number or `Cite as` key
retrieves that act, not the target. Only `lookup` may name the target's own
instrument, and only in `question_cited`.

The field is a JSON key and stays untranslated in every language variant.

### 4. Output schema

    lookup       {"question", "question_cited", "instrument_short_name",
                  "answer", "question_type", "anchor", "articles_involved"}
    fact_pattern {"question", "answer", "question_type",
                  "particulars", "articles_involved"}

`parse_candidates` reads the extra fields **per mode**, so a field belonging to
the other mode cannot leak into a row — the two prompts are near-identical
siblings and a model that has seen both will occasionally emit the wrong one.
`instrument_short_name` is `null` unless a conventional short name is in
established use; a model told to write null sometimes writes the *string*, so
`_short_name` maps `None`, `"null"` and `"none"` alike to `""`.

Both modes write one CSV with one schema; the columns the other mode does not
emit stay empty. `particulars` join on `|`, not `,`, because a particular
routinely contains a comma ("40 tonnes placed on the Spanish market last year").

### 5. Verifiers

`faithfulness_batch.txt` is shared by both modes and is unchanged by the mode
swap:

- the input description covers all four blocks (including REFERENCED ANNEXES)
  and the `Cite as` keys, and the candidates it grades carry their declared
  `articles_involved`;
- the `CROSS-REFERENCE RULE` splits into case (a) *cited article was supplied* —
  following it is legitimate support, not inference — and case (b) *not supplied*
  — score at most 2;
- `GROUNDING` also checks provenance: **cap at 2** if `articles_involved` is
  wrong in either direction, **cap at 1** if the substance came from an article
  never supplied.

`lookup_batch.txt` and `fact_pattern_batch.txt` share the technical five
sub-criteria and emit the same JSON keys, so `core.grading` needs no change.
Each adds the checks its mode turns on:

| check | `lookup` | `fact_pattern` |
|---|---|---|
| IDENTIFIER-LEAK | ✓ | ✓ |
| ANCHOR CHECK — no regime anchor, only generic actors | ✓ | |
| FACT-PATTERN CHECK — no situation, a bare slot | | ✓ |
| SIBLING TEST — would fit a different act equally well | ✓ | ✓ |
| TERM-SUBSTITUTION — a term of art swapped for a near-synonym | | ✓ |
| BOILERPLATE — the answer is a transposition/entry-into-force/addressee clause | ✓ | ✓ |

The graders see only `question`, `answer` and `articles_involved`, so every
check above is judged from the question text itself rather than from the
generator's own `anchor` / `particulars` self-report.

Both also keep the EUR-LEX TARGET SCOPE rule: a question whose subject matter
lives entirely in a referenced article or annex — of the same act or of another
— scores at most 2 for retrieval quality, because it would retrieve the wrong
document.

## Translations

Each mode ships five full-file translations. The convention, shared with
`prompts_un`:

- **translated**: all prose, headings, rules, self-check items, output field
  descriptions, and the closing trailer — including anything that models the
  wording of the question the model must *output* (question shapes, anchor and
  particular specimens, the forbidden deictic phrases);
- **verbatim English**: the `###` block markers, the `Act:` / `Location:` /
  `Cite as:` keys, every JSON key and `question_type` value, all instrument
  identifiers and CELEX keys, the indented metadata specimen, and **the whole
  worked-examples block**, which is a sample of English input and output;
- the third paragraph declares the output language, and the trailer states that
  the article is supplied in that language *and* in English.

One line = one line across all five files (251 for `lookup`, 209 for
`fact_pattern`), which makes the examples block diffable byte-for-byte against
`en.txt` as a regression check.

## Division of labour on `articles_involved`

The LLM grader judges whether the declaration is *semantically* right. Code in
`eurlex_context.normalise_involved` checks that it is *structurally* valid —
articles the model was never sent are rejected outright, the target is inserted
if omitted, and surface variants (`"Article 3"`, `"3"`, `"3 and 4"`) are
normalised. Rubrics grade that kind of thing badly; a validator does not.
