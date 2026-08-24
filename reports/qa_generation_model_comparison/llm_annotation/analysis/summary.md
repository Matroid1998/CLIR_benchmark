# Human vs LLM annotators — question generation model comparison (chemistry patents)

Run 2026-08-22. The 30-document × 6-generator blind review that a human annotator (amirreza) completed on
2026-08-18 was repeated with two LLM annotators under the same protocol: identical rubric text, anonymised
systems, slot order re-randomised per pass, one document (Q1–Q6 + source passage) per call.

| annotator | model | transport | docs | notes |
|---|---|---|---|---|
| Human | amirreza | Argilla | 30 | 18/180 slots scored with the other mode's quality block (scored from the block filled) |
| Claude Fable 5 | `claude-fable-5` | blind workflow subagent per document, effort=high | 30 | 1 document (MX-2025007206-A, rAAV formulations) is refused by Fable 5 (API `finish_reason=content_filter`); the harness fell back to `claude-opus-5` for it — kept and flagged, see `../claude_pass_fallback.json` |
| GPT-5.6 Sol | `gpt-5.6-sol` | OpenAI chat completions, strict JSON schema, reasoning_effort=high | 30 | reasons written in the question's language |

Regenerate: `uv run python analyze.py` (from `llm_annotation/`). All headline numbers were independently
recomputed from the raw files by a separate pass (108 values, all match to 4 decimals).

## Headline: the LLMs rank the generators almost in reverse of the human

| generator | human keep | Claude keep | GPT keep | human comp | Claude comp | GPT comp | majority keep | unanimous keep |
|---|---|---|---|---|---|---|---|---|
| GPT-5.4-mini | **87%** | 53% | 50% | 4.53 | 4.26 | 4.42 | 57% | 43% |
| GPT-5-mini | 83% | 43% | 57% | **4.60** | 4.20 | 4.42 | 60% | 27% |
| Gemini 3.5 Flash | 80% | 80% | **77%** | 4.52 | 4.41 | 4.60 | 80% | 60% |
| Qwen3.6-35B-A3B | 80% | 67% | 50% | 4.48 | 4.41 | 4.56 | 67% | 43% |
| Grok 4.3 | 77% | 77% | 70% | 4.46 | 4.35 | 4.48 | 77% | 50% |
| Sonnet 4.6 | 73% | **97%** | 73% | 4.53 | **4.50** | **4.65** | **83%** | 60% |

Overall keep rate: human 80%, Claude 69%, GPT 63%. Spearman correlation of the six per-model keep rates:
human vs Claude **−0.84**, human vs GPT **−0.60**, Claude vs GPT **+0.75** (composite: −0.43, −0.37, +0.94).
The two LLMs agree with each other about which generators are good and disagree with the human.

## Why: faithfulness drives the human, specificity drives the LLMs

- **Question-level keep agreement** (fig4): human–Claude 63% (κ = 0.03), human–GPT 71% (κ = 0.30), Claude–GPT 72%
  (κ = 0.38); three-way Fleiss κ = 0.24. 85/180 questions are kept unanimously, 10 discarded unanimously, 85 split.
- **What predicts "keep"** (point-biserial r with the annotator's own scores): human — faithfulness 0.76, quality 0.61,
  specificity 0.34. Claude — faithfulness 0.08, specificity **0.71**, search-bar realism 0.58. GPT — faithfulness 0.34,
  specificity **0.68**, search-bar realism 0.64. The LLMs rate nearly every answer as faithful (91% / 89% of faithfulness
  ratings are 5, vs 75% for the human) and then discard on retrieval usefulness.
- **The 26 questions the human kept and both LLMs discarded** are 21 technical-mode keyword questions, 18 of them from the
  two GPT-mini generators: faithful but unanchored ("¿Qué valores puede tomar b?", "What is the weight percent range of Cu
  in the alloy?", "Welche Festigkeit weisen die … Aluminiumlegierungsprodukte auf? — hohe Festigkeit"). The LLMs' own
  specificity score on these is 1.9 (Claude) / 2.4 (GPT) vs 3.4 / 4.1 on the human-kept questions they also kept.
- **The 9 questions the human discarded and both LLMs kept** are mostly Grok and Sonnet semantic-mode questions where the
  human had flagged drifting/invented framing; the LLMs scored their grounding 4–5.
- **Mode** (fig2): the human keeps technical questions at 92% and semantic at 67%; Claude inverts this (62% / 79%),
  GPT is flat (69% / 56%). Claude keeps 100% of Grok's and Sonnet's semantic questions; GPT keeps only 21% of Qwen's.
- **Scale use** (fig5): the human gives 5s to 65% of quality ratings, GPT 36%, Claude 19%. Claude is the harshest on
  the technical quality block (mean 3.0 search-bar realism, 2.8 specificity) — it reads most keyword questions as
  "conversational, not search-like".
- **Criterion-level agreement** (agreement.json): specificity is the criterion the three agree on most (ρ ≈ 0.58–0.84);
  phrasing economy, conceptual framing and retrievability correlate near zero between human and LLMs — the rubric words
  mean different things to them. Claude–GPT correlate 0.5–0.8 on every quality criterion.
- **Position** (fig6): no annotator shows a monotone slot-position effect; GPT's Q4 dip (43%) is the largest single-slot
  deviation (n = 30 per bar, so ±17 pp is within noise).
- **Notes**: Claude wrote a document note for 30/30 docs, GPT 29/30, the human 17/30. Both LLMs' dominant
  document-level complaint is the same as the human's: near-duplicate questions across generators for the same fact.
  Both also flag mixed-language answers (English answer span under a Spanish/German question) — a defect the human
  never penalised (8 Claude discards and 4 GPT discards cite it).

## Sensitivity

Dropping the Opus-5-substituted document from the Claude pass moves every per-model keep rate by ≤ 3 pp and the
overall keep rate from 69.4% to 69.5%; no ordering changes. On that document the three annotators cast identical
keep votes on 3 of 6 questions.

## Cost

GPT-5.6 Sol: 63.9k prompt + 62.6k completion tokens (≈ 31k of them reasoning) for 30 calls, ~25 s per document.
Claude Fable 5 workflow: 45k output tokens, 1.4M cache-read/creation input tokens across 31 agents, ~60 s wall clock.

## Files

- `per_model_by_annotator.csv`, `annotator_summary.csv`, `criteria_by_model_annotator.csv` — aggregates
- `agreement.json` / `agreement_pairs.csv` — pairwise and three-way agreement, per-model consensus
- `per_question_all_annotators.csv` — one row per (doc, generator) with all three verdicts, scores and LLM reasons
- `scores_long_all_annotators.csv` — long format, one row per (annotator, doc, slot)
- `disagreements.md` — every human/LLM keep disagreement with the LLM reasons; `notes_<annotator>.md` — notes + reasons per document
- `discard_reason_tags_<annotator>.csv` — categorised LLM discard reasons (see below)
- `keep_by_slot_position.csv`, `llm_usage.json`
- `fig1`–`fig7` (.png + .pdf)

## Why the LLMs discard (hand-categorised one-sentence reasons, `discard_reason_tags_<annotator>.csv`)

| primary category | Claude (55 discards) | GPT (67 discards) |
|---|---|---|
| unanchored / generic question (no document-specific anchor) | **33** | **23** |
| faithfulness (unsupported, altered, dropped qualifier) | 6 | 22 |
| answer form (padded, list-like, framing mismatch) | 1 | 9 |
| answer/question language mismatch | 6 | 3 |
| trivial / tautological | 4 | 3 |
| not search-like / fluency | 3 | 4 |
| lifted wording, multi-fact, other | 2 | 3 |

Of the Claude discards the human kept (43), 29 are unanchored-generic; of GPT's (42), 19 are unanchored-generic
and 8 faithfulness. Per generator: the GPT-minis are discarded for being generic (Claude 22/31, GPT 15/26);
Qwen and Gemini are the only generators whose discards are led by faithfulness (GPT: Qwen 7, Gemini 6; Claude: Qwen 4);
Sonnet loses one question under Claude (English answer under a German question) and four under GPT (faithfulness).
Near-duplication is never a primary reason but the most common secondary one.

## Caveats

- Single pass per LLM annotator at one temperature setting; no repeat to measure self-consistency.
- 1/30 Claude documents was rated by Opus 5 (content-filter fallback), labelled "Claude Fable 5" in figures.
- The human's 18 rubric-switched slots mean quality/composite agreement compares non-identical criteria on 10% of pairs
  (per-criterion correlations intersect on common criteria and are unaffected).
- n = 30 per generator: 95% bootstrap CIs on keep rates are ±15 pp wide; generator orderings within an annotator are
  suggestive, the cross-annotator inversion is the robust finding.
