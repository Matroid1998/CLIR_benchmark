# German (de) article‑cross‑reference extraction spec — consolidated

**Provenance.** Built from 3 survey objects (the prompt says "four independent readers"; **the fourth survey is absent — the JSON array ends mid‑token inside survey 3's `ACT-TYPE NOUNS` note, at `` `Rechtsakt ``. Anything a 4th reader found is not in this spec.**). Every count below was re‑verified by me against the corpus `/home/mehdi/Projects/CLIR_benchmark/data/legal/eurlex/structure/langsurvey/de.json` (45 articles, keys `celex_id`, `article_number`, `text`, `english_text`). Claims I could not verify are marked **[unverified]**. Claims that are mine and appear in no survey are marked **[NEW]**.

Corpus caveat: 45 articles, ~299 k chars, drawn from a handful of CELEX docs (32010R1063, VAT Directive 2006/112, AIFMD 2011/61, …). Frequencies are indicative, not distributional truth.

---

## 0. Survey cross‑check: agreements, disagreements, corrections

**Verified identical across surveys and corpus**
- Head‑word counts `Artikel` 421 / `Artikels` 82 / `Artikeln` 52 — exact.
- In‑chain connector counts `und` 71, `sowie` 19, `oder` 13, `und/oder` 2 — exact (my chain regex reproduces 133 chains with precisely these totals).
- Range: 40 collapsed `Artikel N bis M` vs exactly 1 repeated `bis Artikel` — exact.
- Zero Oxford comma inside an article chain — 0 hits, confirmed.
- Zero `Artikel N (M)` parentheses, zero preposed `Absatz x des Artikels N` — confirmed 0.
- Survey 3's internal‑marker counts (`dieser Verordnung` 15, `dieser Richtlinie` 63, `vorliegenden Verordnung` 7, `vorliegenden Richtlinie` 2, `jener Richtlinie` 3, `jener Verordnung` 1, `jenem Artikel` 1, `jener Vorschrift` 2, `genannten Richtlinie` 3, `genannten Artikels` 3, `dessen Artikel` 3, `Diese Verordnung` 1) — all exact.
- Survey 3's negative findings (`dieses Beschlusses`, `dieser Entscheidung`, `dieses Vertrags`, … = 0) — confirmed 0.

**Disagreements / errors to resolve**

| # | Issue | Resolution |
|---|---|---|
| D‑1 | Survey 1 quotes `"Artikel 27 Absätze 1 bis 4 der Verordnung"`; survey 2 quotes the same span as `der Richtlinie 77/388/EWG`. | **Survey 2 is right.** Corpus: `gemäß Artikel 27 Absätze 1 bis 4 der Richtlinie 77/388/EWG genehmigt wurden`. Survey 1 paraphrased the trailing act. Treat survey 1's *truncated* example strings as illustrative, not verbatim. |
| D‑2 | Survey 2 says `Artikels` is "82×, **47** followed directly by a number". | 82 total is right; the follow‑count is **49** if Roman numerals count (`des Artikels VII` ×2), **47** if digits only. Not a real conflict — different denominators. Use `[0-9IVXLC]`. |
| D‑3 | Survey 2 mandates a `(?<!Unter)Absatz` guard because "`Unterabsatz` CONTAINS `Absatz`". | **Half‑right; the stated reason is wrong.** German is `Unterabsatz` with **lowercase** `a`. A **case‑sensitive** `\bAbsatz\b` yields **0** false hits inside `Unterabsatz` (measured). The guard is only needed if you compile with `re.I` or without `\b`. Keep the guard anyway (free, and protects against `re.I`), but do not rely on it as the primary defence — use `\b` + case‑sensitivity. |
| D‑4 | Survey 1 lists `Artikel 28 Absatz 1, 2 und 3` (singular); survey 2 lists `Artikel 28 Absätze 1, 2 und 3` (plural). | **Both exist, in different documents, for the same underlying reference.** Corpus has `(4) Artikel 28 Absätze 1, 2 und 3 und Artikel 30 gelten…` *and* `für die Zwecke des Artikels 28 Absatz 1, 2 und 3 und des Artikels 30…`. Not a contradiction — it is the proof that **number agreement on `Absatz` is not a list signal**. |
| D‑5 | Survey 1 says "`bis` is the ONLY range word"; survey 2 is silent. | **Confirmed.** 0 hits for `Artikel N–M`, `Artikel N-M`, `ff.`, `bis einschließlich`. |

**[NEW] — found by me, in none of the three surveys**
1. `dieser Artikel` = genitive **PLURAL** ("these Articles"), 2×: `Für die Zwecke dieser Artikel gelten die Absätze 1 und 2 des vorliegenden Artikels entsprechend.` / `Als zuständige Behörden und als AIF-Anleger im Sinne dieser Artikel gelten…`. Distinct from `dieses Artikels` (gen. sg.). A rule "`dieser` + act‑noun ⇒ internal act reference" must not fire here.
2. `diesem Artikel` (dat. sg.) 13× — `gemäß diesem Artikel`, `in diesem Artikel festgelegten Bedingungen`.
3. Internal markers for **non‑article** units: `dieses Abschnitts` 21×, `dieses Absatzes` 6×, `dieses Buchstabens` 2×, `dieses Kapitels` 1×.
4. **Spaced letter suffix**: `des Anhangs 13 a`, `in Anhang 13 d`, `Auslegungsvorschrift 2 a` — the letter suffix is separated by a space in some source text, alongside `Anhang 13a` (7×), `13b`, `13c`, `13d`. Not attested for `Artikel` here, but it is the same typesetting artefact.
5. `Nummer 2.5` — **dotted** point numbers (`Anhang I Teil A Nummer 2.5`).
6. `Ziffer`/`Ziffern` take their own lists and ranges: `Buchstabe a Ziffern ii und iii`, `Ziffern i bis iv dieses Buchstabens`, `Buchstabe a Ziffer vii`.
7. `bzw.` (32×) = "or / respectively". It joins **noun phrases**, never bare numbers inside a chain (1 near‑miss: `gemäß Absatz 1 bzw. der Ergebnisse … gemäß Absatz 2` — two separate references). **Do not add `bzw.` to the in‑chain connector set.** `beziehungsweise` spelled out: 5×, same behaviour.
8. Zero abbreviations of any unit: `Art.` 0, `Abs.` 0, `UAbs.` 0, `Buchst.` 0. `Nr.` occurs 56× but **only inside act numbers** (`Verordnung (EG) Nr. 45/2001`), never as a unit marker.
9. Clause‑boundary comma trap: `gemäß Artikel 301 Absatz 1, ist er berechtigt…` — the comma is syntax, not enumeration. The "comma continues the chain" rule must require a **digit/letter/roman token** after the comma.
10. Higher structural units present and numbered: `Anhang` 66 / `Anhangs` 4 / `Anhänge` 2, `Teil` 13, `Titel` 3, `Kapitel` 17 / `Kapitels` 3, `Abschnitt` 22 / `Abschnitts` 23, `Unterabschnitt` 17 (incl. `Unterabschnitte 1, 2, 3, 5, 6 und 7`), `Anlage` 5, `Feld/Felder` 19 (form fields, not law).

---

## 1. Article head‑word forms (all inflections)

Exactly three surface forms; **no others exist in the corpus**, and the word is **never abbreviated and never lowercase**.

| Form | Case/number | Count | Followed by a number |
|---|---|---|---|
| `Artikel` | nom./acc./dat. sg., nom./acc. pl. | 421 | 404 |
| `Artikels` | **gen. sg.** | 82 | 49 (47 digits + 2 Roman) |
| `Artikeln` | **dat. pl.** | 52 | 52 |

```
ART_HEAD = r'\bArtikel(?:s|n)?\b'
```
- `Artikeln` is a **strong positive signal that a multi‑article list or range follows** (52/52 followed by a number).
- Never anchor on `Artikel\s` (whitespace): that misses `Artikeln 10 bis 14` and `Artikels 378`.
- Never anchor on bare substring `Artikel` without `\b`: it prefix‑matches `Artikels`/`Artikeln` and then mis‑tokenises the number.
- `Art.` + digit: **0**. lowercase `artikel` + digit: **0**. `Artikel(` : **0**.
- Source noise, 1 instance, do not model: `des in Artikels 67 Absatz 6 genannten delegierten Rechtsakts` (wrong case).

**Determiners that may precede the head** (optional, and they *change mid‑chain*), measured immediately before `Artikel*`:
`den` 52, `des` 48, `der` 44, `dieses` 24, `diesem` 13, `dem` 7, `vorliegenden` 6, `die` 5, `genannten` 3, `dieser` 2, `jenem` 1.

```
DET = r'(?:der|die|das|den|dem|des|dieser|diese|dieses|diesem|diesen|jener|jenem|jenes|genannten|vorliegenden)'
```

---

## 2. Connector words

### 2a. List connectors (in‑chain, verified counts over 133 chains)

| Token | In‑chain count | Notes |
|---|---|---|
| `und` | 71 | dominant |
| `sowie` | 19 | **= "and". The #1 miss for a dictionary‑written regex.** Joins the last group of a chain, esp. after internal `und`s or ranges. |
| `oder` | 13 | minority |
| `und/oder` | 2 | written **solid with a slash, no spaces**. Tokenisers that split on `/` break this. |
| `,` | — | plain comma; **no Oxford comma ever** (0 hits for `…, und/oder/sowie <digit>`) |

```
CONJ = r'(?:und/oder|und|oder|sowie)'
SEP  = r'(?:\s*,\s*|\s+' + CONJ + r'\s+)'
```
- **Not** connectors: `bzw.` (32×), `beziehungsweise` (5×), `jeweils` (6×), `respektive` (0). [NEW]
- Long German lists frequently **end an enumeration with a plain comma and continue into the next member** — do not assume the last item is preceded by a conjunction.
- **Do not derive conjunctive/disjunctive semantics from the German connector.** Verified DE↔EN mismatches: `Artikeln 151, 152 und 153` ← EN "Articles 151, 152 **or** 153"; `Artikeln 194 bis 197 und 199` ← EN "… **or** Article 199"; `Artikeln 110, 111` ← EN "Articles 110 **and** 111"; `Artikeln 132, 135, 136, 371, 375, 376, 377` ← EN "…, 376 **and** 377". The same document uses `und` and `sowie` interchangeably for the same English string (`den Artikeln 194 bis 197 und 199` 3× vs `… sowie 199` 2×).

### 2b. Range connector

**`bis` is the only range word.** Verified 0 for `Artikel N[–-]M`, `Artikel N ff.`, `bis einschließlich`.

Two shapes:
- **Collapsed (40×, dominant)** — head word written once: `Artikel 66 bis 97`, `den Artikeln 282 bis 292`, `der Artikel 312 bis 325`.
- **Repeated (exactly 1×)** — `Artikel 4k bis Ar