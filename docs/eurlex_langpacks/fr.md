# Consolidated FR extraction spec — article cross-references in EUR-Lex French

**Provenance and status of the input.** The prompt announced four readers; the text supplied contains **three** surveys, and the third is **truncated mid-item** (it ends at `(d) Related pro-forms: 'therein' → 'y visée' / 'qui y`). Everything after that point — the rest of the pro-form inventory — is **missing from this consolidation**. Section 8 below is therefore complete only for the strategies attested before the cut.

All numeric claims below were **re-verified directly** against the corpus the surveys describe: `/home/mehdi/Projects/CLIR_benchmark/data/legal/eurlex/structure/langsurvey/fr.json` (45 articles, `text` = FR, `english_text` = parallel EN, 303 507 FR chars). Where a survey's count disagrees with the corpus, the corpus wins and the disagreement is recorded in §0.2. Target implementation is Python `re` (the existing EN extractor is `/home/mehdi/Projects/CLIR_benchmark/src/clir_bench/domains/legal/structure/references.py`); note Python `re` has **no variable-length lookbehind**, so every rule below is written to work left-to-right.

---

## 0. Cross-check results

### 0.1 Claims all surveys agree on and the corpus confirms

| Claim | Verified |
|---|---|
| FR `Article`/`Articles` capitalised: 0 of 589 tokens (`article` 452, `articles` 137) | yes (EN side: 132 capitalised `Articles`, 4 lowercase) |
| Zero bare `articles N` — left context is always `aux` (75), `des` (35), `les` (21) | yes, 132 total (see §0.3 for the 132nd) |
| Range connector is only `à`; 56 occurrences; zero dash/en-dash ranges; zero `jusqu'à l'article`; zero `de l'article N à l'article M`; zero `entre les articles`; zero `et suivants` | yes, all zero |
| `article N paragraphe M` without the comma: 0 occurrences | yes |
| Reversed `paragraphe N de l'article M`: 0 occurrences | yes for numbered articles (but see §0.2 row 5) |
| `alinéa` + digit: 0; `§`: 0; `sous-paragraphe`: 0; `sous-point`: 0; `art.`: 0; `article premier`: 0 | yes |
| `ce règlement` / `cette directive` / `cette décision` / `même règlement` / `même directive` / `précité` / `susvisé`: all 0 | yes |
| `n°` / `nº` / `N°`: 0; the number sign is ASCII `no` + space (74 hits) | yes |
| `au présent règlement` (dative contraction): 0 | yes |
| `présente décision` / `présent traité` / `présente annexe` / `présent titre` / `présente convention` / `présent accord`: 0 | yes |
| 21 attached `article N, paragraphes <list>` instances | yes, exactly 21 |
| `paragraphe(s) + number` = 385 occurrences | yes |
| Oxford comma inside a bare-number run (`\d , et \d`): 0 | yes |

### 0.2 Where the surveys disagree — resolved against the corpus

| # | Point | Survey 1 | Survey 2 | Survey 3 | Corpus | Ruling |
|---|---|---|---|---|---|---|
| 1 | `article 1er` count | "9 overall, 2 inside lists" | "8 occurrences" | "occurs 7 times" | **9** (`articles 1er et 2` ×2 = the 2 in lists) | Survey 1 correct |
| 2 | `l’article` (U+2019) vs `l'article` (ASCII) | 266 / 129 | (n/a) | 270 / 129 | **270 / 129** | Survey 3 correct |
| 3 | Distinct range spans | "31 distinct range spans" | (n/a) | (n/a) | **19** distinct `(from,to)` pairs across 56 occurrences | Neither: use 56 occurrences / 19 distinct |
| 4 | List connector census | `,`73 `et`67 `à`56 `ou`3 `et/ou`2 | (n/a) | (n/a) | `,`73 `et`**70** `à`56 `ou`3 `et/ou`2 | Difference is counting method (whether the `et` that re-heads a limb counts); treat `et` as ≈67–70 — **not load-bearing** |
| 5 | Is the reversed order `<sub-unit> de <article>` attested? | (n/a) | "0 occurrences of the reversed English-style order" | reports `le paragraphe 5 dudit article` ×3 | **Both true** | Reversal never occurs with a *numbered* article; it occurs **only** with the anaphor `dudit article` (3×). Merge, do not pick. |
| 6 | `du présent règlement` | (n/a) | (n/a) | 20 | **21** | Corpus |
| 7 | `de la présente directive` | (n/a) | (n/a) | 39 | **40** | Corpus |
| 8 | Article-number suffix inventory | bis ter quater octies nonies duodecies quaterdecies septdecies unvicies | (n/a) | bis ter quater quinquies octies nonies duodecies vicies unvicies | union of both, **11 forms**, is exactly what occurs: bis ter quater quinquies octies nonies duodecies quaterdecies septdecies vicies unvicies | Neither list alone is complete — use the union, and allow the full paradigm (§9) |
| 9 | `des articles` | 35 | (n/a) | (n/a) | 36 total, **35** before a digit | Both right; the 36th is `‘des articles` (quote glyph glued, §0.3) |
| 10 | `les articles` | 21 | (n/a) | (n/a) | 23 total, **21** before a digit | The other 2 are the ordinary noun (§0.3) |

### 0.3 Facts no survey reported (found during cross-check — all are extractor traps)

1. **`article(s)` as an ordinary common noun** ("item/goods"), 4 occurrences: `les articles usagés`, `articles textiles`, `un article complet`, `tous les articles entrant dans leur composition`. None is followed by a digit → the mandatory-digit rule (§1.4) already excludes them, but do **not** relax that rule.
2. **Roman-numeral article numbers**, 4 occurrences: `l’article XXIV de l’accord général sur les tarifs douaniers` ×2, `l’article VII` ×2. These are non-EU instruments (GATT). Decide explicitly whether to emit them; a `\d`-anchored pattern drops them silently.
3. **Amendment formula with no number**: `L’article suivant est inséré` — `article` followed by `suivant`, not a number.
4. **Quote glyphs glue to the determiner** inside amendment insertions (the whole replacement text is wrapped in `‘ … ’`): the corpus contains `‘des articles`. Do not use `\s` or `\b`-after-space as the only left boundary; use `(?<![\w\-])` style or allow `[‘’"]` to precede the determiner.
5. **`audit` is safe here**: all 7 occurrences are the `à+ledit` contraction (`audit pays`, `audit alinéa`, `audit cumul`, `audit point`); the loanword *audit* does not occur. The homograph guard is still required for other corpora.
6. **`et/ou` is 31× in the text but only 2× inside an article citation**; **`ainsi que/qu'` is 36× but only 1× inside a citation** (`ainsi qu’à l’article 24`). Neither word is a citation cue on its own.

---

## 1. Article head word — all forms

### 1.1 Inflections of the head noun
Exactly two surface forms, **always lowercase** in FR (0/589 capitalised):

| Form | Count | Meaning |
|---|---|---|
| `article` | 452 | singular |
| `articles` | 137 | plural |

There is **no** `art.`, no `Art.`, no `§`, no `article premier`. Elision affects the *determiner*, never the noun: `l’article` / `l'article` (never `l’articles`, 0 occurrences).

### 1.2 Left-frames attested (this is the real anchor)
The noun is never bare. Verified frames, with counts:

**Plural (multi-article citation):** `aux articles` 75 · `des articles` 35 · `les articles` 21 · `desdits articles` 1 · `auxdits articles` 1 (the last two are anaphoric, §6).

**Singular:** `à l’article` 154 · `à l'article` 91 · `de l’article` / `de l'article` · `du présent article` 32 · `au présent article` 8 · `dans le présent article` · `son article` 2 · `dudit article` 3 · `l’article` 270 / `l'article` 129 total (all elided-determiner forms).

Also attested as the citation determiner: `par les articles`, `sans préjudice des articles`, `au titre de l’article`, `en vertu de l’article`, `conformément à l’article`, `au sens de l’article`, `aux fins de l’article`, `visé(e)(s) à l’article`, `prévu(e) à l’article`, `énoncé(e) à l’article`, `fixé(e) à l’article`, `établi à l’article`, `défini à l’article`, `dans les conditions prévues aux articles`.

### 1.3 Ready fragments

```python
AP        = r"[’'‘`´]"                       # apostrophe class — U+2019 and ASCII both occur, MIXED inside one document
ART_WORD  = r"articles?"                     # lowercase in FR; still compile with re.I for robustness
DET_SG    = rf"(?:l{AP}|d[eu]\s+l{AP}|à\s+l{AP}|son|ledit|dudit|audit)"
DET_PL    = r"(?:aux|des|les|auxdits|desdits|lesdits)"
ART_HEAD  = rf"(?:{DET_SG}|{DET_PL}\s+)?\b{ART_WORD}\b"
```

### 1.4 Hard requirement
A match is a citation **only if** the head noun is immediately followed by whitespace and an article number (§9) — a digit, or a Roman numeral if you choose to support §0.3.2. `articles` + non-number = ordinary noun or the amendment formula.

---

## 2. Connectors

### 2.1 Range connector — one form only
**`à`**, bare preposition, between two numbers. 56 occurrences, 19 distinct spans, **100 % aligned to English "to"**.

```
articles 66 à 97 · articles 10 à 14 · articles 380 à 390 · articles 4 duodecies à 4 unvicies
```

`à` is **massively overloaded** — it is also the dative preposition introducing a single article (`conformément à l'article 5`, `aux articles` = à+les). The discriminator is purely positional: **`à` is a range operator only when it sits between two NUMBER tokens inside an already-open enumeration.** It never introduces the enumeration.

`à` is also the range operator one level down: `paragraphes 1 à 4` (4×), `points a) à f)`, `points b) à g)` (