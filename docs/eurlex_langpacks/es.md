# Spanish (es) article-reference extraction — consolidated regex specification

**Sources consolidated:** three language surveys supplied in the prompt (S1 = lists/ranges/chains; S2 = paragraph/point attachment; S3 = internal vs. external act references). The prompt announced four readers but only three survey blocks were supplied, and S3 is truncated mid-note in section (d, other) — items 7 and 8 below are therefore reconstructed from S3's partial text plus my own corpus verification, and any *fourth* survey's content is absent.

**Verification:** every count and claim below was re-checked directly against the corpus the surveys read, `/home/mehdi/Projects/CLIR_benchmark/data/legal/eurlex/structure/langsurvey/es.json` (45 articles, `text` + `english_text`). Counts marked ✓ reproduce the survey; counts marked **[CORRECTED]** do not. Target implementation is the ES sibling of `/home/mehdi/Projects/CLIR_benchmark/src/clir_bench/domains/legal/structure/references.py`.

---

## 0. Cross-check: where the surveys disagree or are wrong

Stated explicitly rather than silently resolved.

| # | Issue | S1 / S2 / S3 claim | Corpus says | Resolution for the spec |
|---|---|---|---|---|
| 0.1 | Suffix/whitespace-loss artifacts | S1: "Three occurrences", all in 32010R1063 (`97 octiesy`, `4 duodeciesa`, `97 viciesy`) | **[CORRECTED]** Four at article level — S1 missed `en el artículo 97 **noniesen** caso de que:`. Plus at other levels: `anexo 13 **bispara**`, `anexo 13 **bisexija**`, `anexo 13 **bisno**`, `anexo **13ter**`, `sección **1bis**` (×3), `mutatis**mutandisa**` | Generalise: whitespace is lost on **either side** of a Latin suffix, and the following word is *not* necessarily a connector. §9.3 |
| 0.2 | Serial comma before final `y` | S1: "no serial comma before `y`", exactly 3 exceptions, all caused by `apartado` | **[CORRECTED]** True inside *article* chains, but the corpus contains one same-level serial comma at another level: `las subsecciones 1, 2, 3, 5, 6, y 7 en Ceuta y Melilla` | The `, y` → level-exit rule (§4) is safe for `artículo`/`apartado` chains only. Do **not** generalise it to `sección`/`subsección`/`anexo` lists. |
| 0.3 | Internal vs. external discriminator for bare `de la Directiva` | S3: "The discriminator is presence/absence of a following number token" | Incomplete. `de dicha Directiva`, `de la mencionada Directiva` also carry **no number** and are **external** | Discriminator = *no number* **and** *no anaphoric determiner* (`dicho/a`, `mencionad-`, `ese/esa`). §5.4 |
| 0.4 | `presente` as internal trigger | S3 treats `presente` + noun as the trigger token | `presente` is also the present-subjunctive of *presentar*: `el declarante no **presente una** comunicación`, `cuando el producto **presente un** riesgo` (×3), `**presente por** lo demás una exposición`. Also a source typo `en la **presenta** sección` | Require determiner **before** and an act/subdivision noun **after**. Never fire on `presente` alone. §5.6 |
| 0.5 | `apartado` comma-form frequency | S2: "~121 occurrences" | **[CORRECTED]** 114 for `art[íi]culo <digits>, apartado`; the balance are suffixed (`97 duodecies, apartado 4`) or ordinal (`apartado primero`) forms | Cosmetic; no rule change. |
| 0.6 | `y/o` frequency | S1: 30 in corpus, 2 in article chains | **[CORRECTED]** 31 in corpus ✓2 in article chains | Cosmetic. |
| 0.7 | `número` count | S2: 26, never structural | **[CORRECTED]** 27, never structural ✓ | Cosmetic. |
| 0.8 | Range connector coverage | S1: `a` is the only range connector, 42 hits, article level | ✓42. S2 independently shows the *same* `a` ranging paragraphs (`apartados 1 a 4`, 4×), letters (`letras a) a d)`, 5×), incisos (3×), points (1×), sections (`apartados 5 a 8`) | Not a disagreement — `a` is the range connector at **every** level. §2.2 |
| 0.9 | Letter suffixes | S1/S2: `letra d) bis` (suffix outside the paren) | Corpus has **both** placements: `letra d) bis`, `letra m) bis` **and** `letra a sexies)` (suffix *inside* the paren). Neither survey reported the inside form | §9.4 |
| 0.10 | Head plurality vs. reference count | S1 says ES plural ↔ EN repeated singular *and* ES repeated singular ↔ EN plural | Both directions confirmed | Never derive a count from the head's number, in either language. §1.4 |

---

## 1. Article head word — all forms

### 1.1 Lexical forms (exhaustive)
```
artículo     articulo     artículos     articulos
```
- **Always lowercase.** Verified: `artículo` 422, `artículos` 138, `Artículo` **0**, `Artículos` **0** — including in headings, where English writes `Article`. Case carries **zero** signal in Spanish (EN has 132 capitalised `Articles`). Match case-insensitively but never *rely* on case.
- The unaccented `articulo/articulos` does not occur in this corpus but costs nothing to allow (`art[íi]culos?`).
- Abbreviation `art.` / `arts.`: **0 hits.** Do not implement.
- `y siguientes`, `ss.`: **0 hits.** Do not implement.

### 1.2 Determiners and prepositions that precede the head (verified inventory)
Counts of the token immediately preceding `artículo(s)`:

| token | n | note |
|---|---|---|
| `el` | 264 | incl. amendment fronting `En el artículo` |
| `los` | 130 | |
| `del` | 80 | `de`+`el` contraction, obligatory |
| `presente` | 39 | `del presente artículo` etc. |
| `al` | 29 | `a`+`el` contraction — **not a range marker** |
| `su` | 5 | "thereof", §8 |
| `de`, `con` | 2 each | |
| `este` | 2 | §5.5 |
| `dicho` | 2 | §6 |
| `y`, `un`, `esos` | 1 each | `un artículo` is the common noun |

Full preposition+determiner shapes attested before a head: `el`, `la`(n/a), `los`, `del`, `al`, `en el`, `en los`, `de los`, `a los`, `con el`, `con los`, `su`, `este`, `esos`, `dicho`, `el presente`, `del presente`.

**Do not anchor on `los artículos`.** Three counter-cases:
1. Source agreement errors, singular determiner + plural noun, introducing a genuine multi-article chain (3 occurrences): `el artículos 167, 168 y 169`, `en el artículos 194 a 197 y 199`, `en virtud del artículos 110 y 111`.
2. The one determiner-less occurrence, inside quotation marks: `la frase ‘artículos 69 y 100’ se sustituye por ‘artículo 100’`.
3. `su artículo 8`, `este artículo`, `dicho artículo`.

→ Match on `art[íi]culos?` regardless of what precedes it; use the preceding determiner only as a *feature*, never as a *gate*.

### 1.3 Head regex (ES equivalent of `_HEAD_RE`)
```python
_HEAD_RE = re.compile(r"\bart[íi]culos?\b(?=[\s,]*\d)", re.I | re.U)
```
The lookahead (a digit must follow, possibly across a comma) is the cheap false-positive filter — see §1.5. Because `í` is non-ASCII, keep `re.U` (default for `str`) and never use `[a-z]` classes for Spanish words.

### 1.4 Plurality is *not* a count
- ES one plural head ↔ EN three singular heads: `los artículos 16, 17 o 18` = "Article 16, Article 17 or Article 18".
- ES repeated singular heads ↔ EN one plural head: `del artículo 86, apartados 7 y 8, y del artículo 97 duodecies` = "Articles 86(7) and (8) and 97k".
- Chains repeat the **whole prepositional phrase**, which English never does: `en los artículos 220 a 236 y **en los artículos** 238, 239 y 240` = "Articles 220 to 236 and Articles 238, 239 and 240". Verified repeated-head shapes after a connector: `en el artículo` 57, `al artículo` 26, `en los artículos` 24, `del artículo` 19, `el artículo` 14, `a los artículos` 5, `de los artículos` 3, `con el artículo` 2, `los artículos` 2, `con los artículos` 1, `en el artículos` 1.
- Chains may switch number mid-way: `... los artículos 158 a 161 y **el artículo** 164`.

**Consequence for the chain walker:** a repeated head inside an already-consumed enumeration must be *absorbed*, not treated as a new enumeration (same `consumed_to` guard as the English implementation) — otherwise ES emits far more duplicate edges than EN, because ES repeats the head much more often.

### 1.5 False positives — `artículo` as the common noun "item / article of goods"
All in 32010R1063 Art. 1, all in lettered lists sitting next to real citations, so proximity heuristics misfire:
```
j) los artículos usados recogidos en él, aptos únicamente para la recuperación de materias primas;
d) el planchado de textiles y artículos textiles;
j) ... la preparación de surtidos (incluida la formación de juegos de artículos);
o) el montaje simple de partes de artículos para formar un artículo completo ...
```
Filter: require a digit (optionally after a comma/whitespace) immediately after the head. This is sufficient in this corpus.

---

## 2. Connectors

### 2.1 List connectors
| surface | role | evidence |
|---|---|---|
| `,` | list separator (also the *only* separator in `los artículos 35, 37 a 41`) | dominant |
| `y` | "and" — final element | 80 tokens inside article chains |
| `o` | "or" | 3 chains only |
| `u` | **allomorph of `o` before a word beginning o-/ho-** | 2, both `los artículos 84, 85 **u** 86` (ochenta y seis) |
| `y/o` | "and/or", written with a slash, **no spaces** | 2 inside article chains (`los artículos