# EUR-Lex article segmentation and cross-reference extraction — pilot

Pilot of 20 acts, drawn stratified by size from the Formex-era EUR-Lex corpus.
**Not to be scaled up until this audit is reviewed.**

Code: `src/clir_bench/domains/legal/structure/`.
Artifacts: `data/legal/eurlex/structure/` (gitignored, like every other corpus).

```
select    candidates + stratified pilot            candidates.csv, pilot.csv
cellar    fetch Formex and ELI, cache everything   cache/, fetch_manifest.json
segment   parse-fmx -> article records             articles.jsonl
references English-only extraction                 internal_edges.jsonl,
                                                   external_references.jsonl,
                                                   dropped_references.jsonl
project   cross-language join, annotate            quarantine.jsonl
resolve_external  cross-act references -> edges    external_edges.jsonl,
          when the cited act is in the corpus      unresolved_external.jsonl,
                                                   reference_status.jsonl
audit     sample, recall probe, cross-check        reports/eurlex_structure/
```

## What came out

| | |
|---|---|
| acts fetched in all four languages | **18 of 20** |
| article records (4 languages) | **5,488** — 3,260 article, 1,968 recital, 260 annex |
| internal edges (article → article, intra-act) | **1,884** |
| external references (flagged; resolved by `resolve_external` when the cited act is in the corpus) | **228** |
| dropped and logged | **165** |
| acts quarantined by the cross-language join | **0** |

Every internal edge is valid in all four languages. 420 of 815 English articles
emit at least one edge; median article is 93 tokens.

## Validation

**Precision — 100/100.** A stratified sample of 100 edges (across 12 acts and all
three expansion rules) was read in context by hand. All 100 are correct. The
sample and its context windows are in `audit_sample.csv`.

This is the *second* audit. The first found 5 false positives in 100 and a
32% edge inflation; all four defects are fixed and pinned by tests in
`tests/test_eurlex_references.py` (20 tests, all passing):

| defect | effect | fix |
|---|---|---|
| a citation chain repeating "Article" was re-parsed from each repetition | 738 duplicate rows (32%) | heads inside a consumed enumeration are skipped |
| `of that Regulation` read as internal | false internal edges | anaphoric determiners route to external |
| `of the Seventh Council Directive`, `of the OECD Model Tax Convention` | false internal edges | capitalised proper-noun modifiers allowed before the designator, matched case-sensitively via `(?-i:…)` |
| list stopped at a parenthesised sub-reference: `Articles 2(2) and (3), 4 and 5(2)` | lost articles 4 and 5 | connector may resume across `(n)` groups |

**Recall — no misses of the `Article N` pattern.** All 1,380 heads in 945,737
characters are accounted for: 1,281 start an enumeration, 99 are absorbed into a
longer chain, **0 unaccounted**. What remains invisible by construction is small:

| | count | |
|---|---|---|
| `this Article` | 94 | anaphoric self-reference, dropped per spec |
| `that`/`the said`/`the same Article` | 7 | genuine ceiling |
| `preceding`/`following Article` | 2 | genuine ceiling |
| `Art. 5` | 0 | not used in EN acts |
| `Annex N` | 200 | not an article reference — now extracted separately as annex citations (see Known limitations) |

So the article-to-article recall ceiling is ~9 phrases in the whole pilot.

### Paragraph and point references resolve to the destination article

A reference to a *paragraph or point of an article* is a reference to that
article, and is recorded as one. Both word orders work:

- `Article 5(1)`, `Article 22(2)(a)` → edge to article 5 / 22, with the
  paragraph kept verbatim in `target_paragraph_surface` so paragraph
  granularity can be added later without re-extracting. **365 of 1,884 edges
  (19%)** are of this shape.
- `point (2) of Article 312`, `paragraphs 2 and 3 of Article 21` → edge to
  article 312 / 21. Of 85 such constructions, 71 produce an internal edge, 12
  are governed by another act and go to the external file, and 2 are correct
  non-edges (one external via *Delegated Regulation (EU) No 1268/2012*, one a
  parent-act article dropped by the inventory filter inside an amending act).
  **None are missed.**

The 554 bare `paragraph N` mentions are a different thing and are *not* misses:
535 point at a paragraph of the article being read, and the rest say
`paragraph N of this Article`. Both are intra-article, so no article edge exists
to find. Reaching *inside* an article, to make the paragraph itself a resolvable
target, is a granularity change and a separate decision.

### 300-article gold standard: precision 100%, recall 100%

The edge-sample audit above measures precision but is structurally incapable of
measuring recall — a reference the extractor never emitted cannot appear in a
sample of its output. So recall was measured the other way round.

300 of the 815 English articles (37%, uniform random, 16 of 18 acts) were
annotated by **30 annotators working blind**: two independent passes over each
article, given the article text and the act's article inventory and *not* the
extractor's output. Verified after the fact: no annotator read any extractor
artifact, and none applied a regex to article text — the annotations are reading
derived. Scored at edge level.

| | |
|---|---|
| articles annotated | 300 |
| of those, with zero extracted edges (pure recall probe) | 140 |
| edges in scope | 566 |
| true positives | 566 |
| false positives | **0** |
| false negatives | **0** |
| **precision / recall** | **100% / 100%** |

The two passes also agreed with *each other* on all 566 edges.

**How much to trust this.** Two qualifications:

1. **The annotators are not independent in the way two people would be.** They
   are separate contexts with different framing, but the same underlying model,
   so a systematic misreading would be shared by both passes and by this
   analysis, and would show up as agreement rather than as error. Human
   annotation is the check this does not replace.
2. **0 errors in 566 is not a zero error rate.** By the rule of three it
   supports precision and recall of **≥99.5% at 95% confidence** — consistent
   with the ~99%/~85% that published extractors report, and notably above the
   85% recall figure, which is explained by that figure counting paragraph-level
   references this pipeline scopes out.

Three independent lines now agree: the deterministic head accounting (0
unaccounted of 1,380), the external cross-check against a different tool over a
different source format (0 article-qualified misses), and this gold standard.

**Second opinion on external references.** `noworneverev/eurlex-parser` scrapes
EUR-Lex HTML — an independent pipeline over an independent source format.

| | |
|---|---|
| identifiable act citations we report (14 acts) | 130 |
| corroborated by eurlex-parser | **105 (80.8%)** |
| reported only by us | 25 |
| reported only by eurlex-parser | 89 |
| — of those, bare act mentions with no article | 89 |
| — of those, article-qualified and genuinely missed | **0** |

The raw set-overlap figure is 43.8%, and it is misleading: the two tools have
different scopes. eurlex-parser lists every act *named anywhere* in an article;
this pipeline records only acts that *govern an article citation*. Every one of
the 89 one-sided cases was checked against the source text and none is
article-qualified. The 25 we report alone were spot-checked and are real
(e.g. "Article 209 of Regulation (EU, Euratom) No 966/2012"), i.e. references
their scraper missed.

## Findings that affect scale-up

**1. The Formex era starts in 2005, not 2004.** Measured by probing 12 acts per
year (`formex_coverage.json`):

```
2000-2003   0/12 per year
2004        6/12          <- transition year, half the acts have no Formex
2005-2015  ~12/12
```

Both pilot acts that failed to fetch (`32004L0022`, `32004R0170`) are from 2004,
exactly the predicted 50%. Pre-2004 acts have no Formex *and* no XHTML — only
flat legacy HTML. Recommend cutting at **2005**; it costs ~1,750 acts of the
15,267 candidates and removes a ragged half-covered year.

**2. ELI subdivision URIs are constructed, not registered.** `eur-lex.europa.eu`
returns HTTP 200 for `…/art_999/oj` *and* `…/art_banana/oj`, so a 200 proves
nothing. CELLAR does mint real subdivision URIs, but only for articles that serve
as a legal basis elsewhere — two of the GDPR's ninety-nine. The pattern is the
official ELI shape and is language-independent, which is why it is used, but
every id here is only as correct as the Formex inventory behind it.

**3. The act-level ELI must be looked up, not derived.** `32014R0680` is
`eli/reg_impl/2014/680`, not `eli/reg/2014/680`. Implementing and delegated acts
take distinct ELI subtypes the CELEX letter does not encode; three of the 20
pilot acts (`reg_impl`, `reg_del`, `dir_del`) would have had wrong identifiers.
The lookup costs one 919-byte request per act.

**4. Stratifying by article count was necessary, not cosmetic.** 12,518 of the
15,267 candidate acts (82%) have 1–4 articles and emit essentially no internal
edges. A uniform random pilot of 20 would have spent ~16 acts on acts with
nothing to extract.

**5. Per-language extraction is not reliable — English-only was right.** The same
act through the same parser yields 362 English edges and 240 German ones. Article
*inventories*, by contrast, matched exactly across all four languages for all 18
acts, so the structural join is sound and the asymmetry is in the reference
prose, not the structure.

**6. The inventory filter earns its place.** 160 of 165 drops are targets outside
the act's own article set — 148 from amending articles quoting the parent act
(`Articles 66 to 97` in a 3-article regulation), the rest suffixed articles like
`5a`/`7a` that exist only in a repealed directive. Without it these would be
plausible-looking false edges.

## Known limitations

- **Amending acts remain the residual precision risk.** The inventory filter
  catches quoted references whose numbers fall outside this act, but a quoted
  reference that *collides* with a real article number would survive. 29 of 1,884
  edges come from articles flagged `is_amending`; `source_is_amending` is on every
  edge so they can be excluded downstream.
- **`thereof` is routed to external** (6 cases). In an enacting article it nearly
  always refers to an act named earlier, and inventing an internal edge would be
  indistinguishable from a real one. Conservative for internal precision.
- **Recitals and annexes are edge sources too** (`source_unit_type` /
  `target_unit_type` on every edge), but question generation reads only
  article → article edges.
- **Annex citations are classified like article ones**: "Annex I *to
  Regulation (EC) No 376/2008*" is that regulation's annex and goes to the
  external file (annexes are governed by "to" where articles are governed by
  "of"); "the Annex", the drafting style for an act with a single annex, is
  linked to that annex (rule `annex_single`) and is ambiguous otherwise; a bare
  label not in the act's own labelled annex inventory is dropped *and logged
  per source*, because it now blocks question-generation completeness.
- **Cross-act references are resolved conservatively** by
  `resolve_external`: the act's identifier is parsed with the year/number order
  fixed by its shape (`No N/YYYY`, `YYYY/N/EC`, `(EU) YYYY/N`) and never guessed
  the other way round — `Regulation (EC) No 2004/2003` read backwards is a real
  act in this corpus, so "does the candidate exist?" is not a safe tie-breaker.
  Only regulations and directives can resolve (the corpus holds no decisions);
  anaphoric citations ("of that Regulation", "thereof", a bare "the Directive")
  and unnumbered instruments (Treaty, Financial Regulation) are recorded in
  `unresolved_external.jsonl` with a reason. On the full corpus this yields
  ~15.6k article → article edges into ~930 acts (43 % of the article-level
  citations that name an act; the rest name acts outside the corpus).
  `--audit` compares the result with the parse-fmx `crossReferences` block from
  the second-opinion tool: act-level agreement is 98.6 %, and every sampled
  disagreement was the other tool reversing the year/number order.
- **`reference_status.jsonl` says, per article, whether every citation it
  makes — article or annex, same act or another — is resolved.**
  `qac/eurlex_batch` samples question targets from complete articles only, so
  the generator never writes about a citation it could not follow. Resolved
  annexes are supplied to the generator in their own payload block, clipped
  hard because annex tables run long; an annex citation that cannot be pinned
  down (act outside the corpus, anaphoric, label not in inventory, bare "the
  Annex" in a multi-annex act) makes the article incomplete.
- **Structural flags are computed on English and copied** to the other languages,
  for the same reason references are. `is_definitions` fires on 8 articles,
  `is_final_provision` on 28, `is_amending` on 8.

## Reproducing

```bash
git clone --depth 1 https://github.com/maastrichtlawtech/eur-lex-visualiser tools/eur-lex-visualiser
cd tools/eur-lex-visualiser/backend && npm install jsdom@25 && cd -

python -m clir_bench.domains.legal.structure.select scan
python -m clir_bench.domains.legal.structure.select sample --n 20
python -m clir_bench.domains.legal.structure.cellar --pilot
python -m clir_bench.domains.legal.structure.segment --pilot
python -m clir_bench.domains.legal.structure.references
python -m clir_bench.domains.legal.structure.project
python -m clir_bench.domains.legal.structure.resolve_external
python -m clir_bench.domains.legal.structure.resolve_external --audit
python -m clir_bench.domains.legal.structure.resolve_external --sample 300
python -m clir_bench.domains.legal.structure.audit sample --n 100
python -m clir_bench.domains.legal.structure.audit recall
python -m clir_bench.domains.legal.structure.audit crosscheck --python <env-with-eurlex-parser>
```

`eur-lex-visualiser` is **GPL-3.0**. It is cloned into `tools/` (gitignored) and
driven as a subprocess; no code from it is copied into this repository. It
provides segmentation only — reference extraction is ours, so the rule that fired
is recorded per edge.
