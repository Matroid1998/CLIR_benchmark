# Human annotation review — question generation model comparison (chemistry patents)

Export: `all-questions-by-model-review-annotations-2026-08-18.json` · de-anonymised with `model_slot_mapping.json`
Single annotator (amirreza), 30 patent documents × 6 models = 180 questions, all records completed.
Per question: 3 faithfulness criteria, 4 mode-specific quality criteria (technical or semantic block), linguistic quality (all 1–5), and a binary keep decision. Slot order randomised per document.

Regenerate everything: `python3 make_plots.py` (reads the two JSONs in the parent folder, `reports/qa_generation_model_comparison/`).

## Headline numbers

| model | keep | keep (tech) | keep (sem) | faith | quality | linguistic | composite (median) |
|---|---|---|---|---|---|---|---|
| GPT-5.4-mini | **86.7%** | 87.5% | **85.7%** | 4.73 | 4.29 | 4.57 | 4.67 |
| GPT-5-mini | 83.3% | 87.5% | 78.6% | **4.74** | 4.47 | 4.60 | **4.82** |
| Gemini 3.5 Flash | 80.0% | 93.8% | 64.3% | 4.37 | 4.49 | **4.70** | 4.67 |
| Qwen3.6-35B-A3B | 80.0% | **100%** | 57.1% | 4.41 | 4.42 | 4.60 | 4.69 |
| Grok 4.3 | 76.7% | 93.8% | 57.1% | 4.52 | 4.42 | 4.43 | 4.54 |
| Sonnet 4.6 | 73.3% | 87.5% | 57.1% | 4.40 | **4.64** | 4.53 | 4.62 |

Overall keep rate 144/180 = 80%. Numbers independently recomputed from the raw export by a second pass; all match.

## Main findings

1. **Semantic mode is the differentiator** (fig2). Technical-mode questions are kept 88–100% of the time for every model; semantic-mode keep rates spread from 57% (Qwen, Grok, Sonnet) to 86% (GPT-5.4-mini). 28 of the 36 discards are semantic-mode questions.
2. **Keep decisions track faithfulness, not fluency** — kept questions average 4.79 faithfulness vs 3.50 for discarded; linguistic quality is indistinguishable (4.55 vs 4.67). No question with faith ≥ 4.5 and quality ≥ 4.5 was discarded.
3. **GPT models win on faithfulness, Sonnet on quality** (fig3). GPT-5.4/5-mini lead grounding (4.83/4.80); Sonnet leads every technical-quality criterion (up to 5.00 focus) but pays a faithfulness price in semantic mode (annotator notes flag invented framing terms).
4. **GPT-5.4-mini paradox**: highest keep rate with the lowest mean quality (4.29) — weak search-bar realism (3.67) and specificity (3.56) cost quality points but rarely sink a question when faithfulness is near-perfect.
5. **Failure severity differs** (fig4): GPT-5.4-mini has only 2% negative (≤2) faithfulness ratings; Qwen 10% and Gemini 9%. Discards concentrate where those tails are.
6. **Annotator notes** (17/30 docs, fig8 scoreboard; tags in `notes_feedback_tags.csv`; where a note treats two questions as equivalent, both carry the same verdict): **Sonnet is the notes' favourite** (10 praise mentions, 7 "strongest") with looseness criticisms; **GPT-5-mini has the cleanest criticism row** (only "less context", 4×); Qwen mixes 6 superlatives with the widest criticism spread; Gemini is praised 8× but owns the two costliest content alterations (dropped "above −80 °C"); GPT-5.4-mini lands mid-field on praise (7) with the most vague/answer-mismatch remarks; Grok is least praised (6) and gets the only "should not be kept" (invented mechanism). The notes favour Sonnet while keep rates favour the GPT minis: admired-but-drifting loses to plain-but-grounded.

## Data quirk to know about

On 18/180 questions the annotator filled the **opposite mode's quality block** (all 6 questions of technical doc WO-2025210445-A1; scattered questions in 6 semantic docs — plausibly deliberate for keyword-style questions in semantic docs). Quality here is scored from whichever block was filled (`rubric_used` column in `annotation_scores_long.csv`); mode-restricted pooling changes per-model quality means by < 0.1 and no ordering.

## Overall average score (fig7)

Composite means sit in a 0.14 band — GPT-5-mini 4.60 > GPT-5.4-mini ≈ Sonnet 4.53 > Gemini 4.52 > Qwen 4.48 > Grok 4.46 — and all 95% CIs overlap (n=30/model). Pooling all 240 raw ratings instead reorders to GPT-5-mini 4.59 > Sonnet 4.54 > GPT-5.4-mini 4.49 > Gemini 4.47 > Grok 4.46 > Qwen 4.44 (quality then carries 4/8 of the weight instead of 1/3). Average score is a near tie however defined; the keep decision is the discriminating metric.

## Files

- `fig1_keep_rate` … `fig8_notes_scoreboard` (.png + .pdf)
- `notes_feedback_tags.csv` — hand-tagged note mentions (doc, model, category)
- `annotator_notes.md` / `questions_by_model.csv` — notes with resolved slots; all questions grouped by model
- `annotation_scores_long.csv` — one row per (document, model) with all criteria
- `per_model_summary.csv` / `.json` — aggregates incl. within-document mean rank
- `make_plots.py` — regenerates everything

## Decision ranking (with generation cost)

Equal-weight mean of per-criterion ranks over keep rate, faithfulness, quality, notes (praise − criticism), and generation cost ($/1000 from the cost sheet; Qwen taken as lowest). Ties in the final order break by keep rate. Full computation: `decision_ranking.csv`.

| # | model | keep | faith | quality | notes ± | gen $ | mean rank |
|---|---|---|---|---|---|---|---|
| 1 | gpt-5-mini | 83.3% | **4.74** | 4.47 | +4 | $2.66 | **2.1** |
| 2 | gpt-5.4-mini | **86.7%** | 4.73 | 4.29 | +1 | $8.35 | 3.6 |
| 3 | qwen3.6-35b-a3b | 80.0% | 4.41 | 4.42 | +2 | **lowest** | 3.6 |
| 4 | sonnet-4.6 | 73.3% | 4.40 | **4.64** | **+5** | $18.05 | 3.6 |
| 5 | gemini-3.5-flash | 80.0% | 4.37 | 4.49 | +4 | $30.19 | 4.0 |
| 6 | grok-4.3 | 76.7% | 4.52 | 4.42 | +3 | $9.77 | 4.1 |

**Pick: gpt-5-mini** — never worse than rank 3 on any criterion; grok-4.3 is strictly dominated by it on all five. Niches: gpt-5.4-mini = max keep rate at 3× cost; qwen = budget pick for technical-heavy corpora (16/16 technical keep) but worst in semantic mode; sonnet = best quality/notes, worst keep, 7× cost — a diversity second generator.
