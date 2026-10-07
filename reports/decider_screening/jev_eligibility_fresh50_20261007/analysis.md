# Independent Jev eligibility compared with existing verifier grades

50 unchanged documents, 300 document-mode decisions, and 440 previously generated questions. Jev selected 271 modes and rejected 29. 1 documents have no selected mode. The exports preserve all 10 generation skips. This comparison performs no generation or regrading.

## Decision and reference definitions

Each mode is selected independently when its yes probability is at least the recorded threshold (0.5). The 0.5 threshold is exploratory; these probabilities have not been calibrated. Several or no modes may be selected for a document. The original baseline selects exactly its previous winning mode, or none for a skip.

A document-mode is **observed viable** for a verifier if at least one generated candidate has a completed numeric grade, audit status `clear` or `minor_issues`, and, for UN, grounding at least 3/5. A high numeric score alone does not override a failed audit. Generation skips have no observed passing candidate. This is the same grounded audit-pass rule used by the original screening analysis.

Verifier judgments are weak reference labels, not human ground truth. No observed passing question does not prove that a mode is impossible: generation attempted only a limited set of questions. An ungraded candidate also cannot establish a pass. A Jev yes prediction on an observed negative is counted as an FP below only for this comparison, not as a proven routing mistake.

TP = yes with an observed passing candidate; FP = yes without one; FN = no with one; TN = no without one. Precision is TP / all yes decisions. Recall is TP / all observed viable modes. Baseline metrics use the same document-mode population and the original single winner. The new policy can select more modes and therefore use a larger generation budget; its recall gain is not a comparison at equal generation cost. Undefined ratios are blank in CSV and shown as — here.

Score averages are document-mode macro averages of the best completed total /40 in each group, including candidates that fail audit or grounding. Groups without a numeric score are excluded from score averages; scored denominators are included in the statistics CSV. Within-mode mean candidate scores and passing counts are in `mode_comparison.csv`.

## Yes decisions by corpus and mode

| corpus | mode | documents | yes_count | mean_probability_yes | previous_pick_count |
| --- | --- | --- | --- | --- | --- |
| eurlex | fact_pattern | 25 | 23 | 0.81 | 0 |
| eurlex | lookup | 25 | 23 | 0.84 | 22 |
| eurlex | conceptual | 25 | 24 | 0.77 | 0 |
| eurlex | comparison | 25 | 14 | 0.52 | 1 |
| eurlex | claim_verification | 25 | 24 | 0.87 | 0 |
| eurlex | source_finding | 25 | 23 | 0.77 | 0 |
| un | lookup | 25 | 25 | 0.84 | 6 |
| un | practitioner | 25 | 25 | 0.84 | 1 |
| un | conceptual | 25 | 25 | 0.89 | 18 |
| un | comparison | 25 | 15 | 0.54 | 0 |
| un | claim_verification | 25 | 25 | 0.91 | 0 |
| un | source_finding | 25 | 25 | 0.81 | 0 |

## Overall comparison with each blinded verifier

| verifier | yes_count | observed_viable_mode_count | tp | fp | fn | tn | precision | recall | baseline_selected_count | baseline_precision | baseline_recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| verifier 1 | 271 | 239 | 228 | 43 | 11 | 18 | 0.84 | 0.95 | 48 | 0.85 | 0.17 |
| verifier 2 | 271 | 224 | 207 | 64 | 17 | 12 | 0.76 | 0.92 | 48 | 0.44 | 0.09 |
| verifier 3 | 271 | 227 | 215 | 56 | 12 | 17 | 0.79 | 0.95 | 48 | 0.56 | 0.12 |
| verifier 4 | 271 | 243 | 230 | 41 | 13 | 16 | 0.85 | 0.95 | 48 | 0.90 | 0.18 |
| verifier 5 | 271 | 274 | 255 | 16 | 19 | 10 | 0.94 | 0.93 | 48 | 0.94 | 0.16 |

## Verifier 4 comparison by corpus

| corpus | document_mode_count | yes_count | observed_viable_mode_count | tp | fp | fn | tn | precision | recall | baseline_precision | baseline_recall | mean_best_total_40_selected | mean_best_total_40_rejected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 300 | 271 | 243 | 230 | 41 | 13 | 16 | 0.85 | 0.95 | 0.90 | 0.18 | 38.71 | 37.23 |
| eurlex | 150 | 131 | 118 | 111 | 20 | 7 | 12 | 0.85 | 0.94 | 0.96 | 0.19 | 38.57 | 37.75 |
| un | 150 | 140 | 125 | 119 | 21 | 6 | 4 | 0.85 | 0.95 | 0.84 | 0.17 | 38.84 | 36.60 |

Selecting all 300 modes without Jev would have 81.0% precision against verifier 4 and retain every observed viable mode. The independent policy keeps 90.3% of all modes (5.42 per document on average). Compared with generating all modes, it would avoid 29 generation batches, while missing 13 batches with an existing verifier-4 passing question. Of these missed batches, 12 are comparison mode. Review those disagreements before choosing a production threshold; the current run measures eligibility coverage rather than a balanced persona allocation.

## Selected versus rejected scores

| verifier | selected_scored_mode_count | mean_best_total_40_selected | rejected_scored_mode_count | mean_best_total_40_rejected | ungraded_candidate_count |
| --- | --- | --- | --- | --- | --- |
| verifier 1 | 268 | 36.97 | 22 | 33.41 | 0 |
| verifier 2 | 268 | 39.55 | 22 | 39.18 | 0 |
| verifier 3 | 268 | 37.96 | 22 | 36.14 | 0 |
| verifier 4 | 268 | 38.71 | 22 | 37.23 | 0 |
| verifier 5 | 268 | 39.68 | 22 | 39.27 | 0 |

## Files

- [Every original question, grade and explanation with its new Jev decision](questions_with_jev_and_grades.csv)
- [One row per document and mode](mode_comparison.csv)
- [All five verifier comparisons, overall and by corpus/mode](comparison_statistics.csv)
- [Raw independent decisions](decisions.csv)
