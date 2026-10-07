# Decider screening

Run status: **completed**. Seed 20261007; 25 UN documents and 25 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `google/gemini-3.8-flash`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

This is a verifier-only rerun. Questions, answers, candidate metadata, source packets, and both decider outputs were reused from the parent run. Only faithfulness and quality verification were called, using the exact saved system/user messages and `google/gemini-3.8-flash` with medium reasoning effort. Usage below counts only this rerun. The generation design described next belongs to the parent run.

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider in this run: eurlex: lookup, fact_pattern, conceptual, comparison, claim_verification, source_finding; un: lookup, practitioner, conceptual, comparison, claim_verification, source_finding. Legacy technical/descriptive modes are outside this comparison. All declared modes are eligible on UN meeting records, as on other UN documents.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 0; successfully repaired: 0. Repairs reuse generation and successful verifier stages. Recorded structural recoveries retain provider scores; missing grades are retried under the saved repair policy. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. Omitted positional indices can be restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| un_all | generator | lookup | 10 | 25 | 40.00 |
| un_all | generator | practitioner | 2 | 25 | 8.00 |
| un_all | generator | conceptual | 10 | 25 | 40.00 |
| un_all | generator | comparison | 3 | 25 | 12.00 |
| un_all | generator | claim_verification | 0 | 25 | 0.00 |
| un_all | generator | source_finding | 0 | 25 | 0.00 |
| un_all | generator | skip | 0 | 25 | 0.00 |
| un_all | generator | error | 0 | 25 | 0.00 |
| un_all | jev | lookup | 6 | 25 | 24.00 |
| un_all | jev | practitioner | 1 | 25 | 4.00 |
| un_all | jev | conceptual | 18 | 25 | 72.00 |
| un_all | jev | comparison | 0 | 25 | 0.00 |
| un_all | jev | claim_verification | 0 | 25 | 0.00 |
| un_all | jev | source_finding | 0 | 25 | 0.00 |
| un_all | jev | skip | 0 | 25 | 0.00 |
| un_all | jev | error | 0 | 25 | 0.00 |
| un_without_meetings | generator | lookup | 4 | 15 | 26.67 |
| un_without_meetings | generator | practitioner | 2 | 15 | 13.33 |
| un_without_meetings | generator | conceptual | 7 | 15 | 46.67 |
| un_without_meetings | generator | comparison | 2 | 15 | 13.33 |
| un_without_meetings | generator | claim_verification | 0 | 15 | 0.00 |
| un_without_meetings | generator | source_finding | 0 | 15 | 0.00 |
| un_without_meetings | generator | skip | 0 | 15 | 0.00 |
| un_without_meetings | generator | error | 0 | 15 | 0.00 |
| un_without_meetings | jev | lookup | 4 | 15 | 26.67 |
| un_without_meetings | jev | practitioner | 1 | 15 | 6.67 |
| un_without_meetings | jev | conceptual | 10 | 15 | 66.67 |
| un_without_meetings | jev | comparison | 0 | 15 | 0.00 |
| un_without_meetings | jev | claim_verification | 0 | 15 | 0.00 |
| un_without_meetings | jev | source_finding | 0 | 15 | 0.00 |
| un_without_meetings | jev | skip | 0 | 15 | 0.00 |
| un_without_meetings | jev | error | 0 | 15 | 0.00 |
| un_meetings_only | generator | lookup | 6 | 10 | 60.00 |
| un_meetings_only | generator | practitioner | 0 | 10 | 0.00 |
| un_meetings_only | generator | conceptual | 3 | 10 | 30.00 |
| un_meetings_only | generator | comparison | 1 | 10 | 10.00 |
| un_meetings_only | generator | claim_verification | 0 | 10 | 0.00 |
| un_meetings_only | generator | source_finding | 0 | 10 | 0.00 |
| un_meetings_only | generator | skip | 0 | 10 | 0.00 |
| un_meetings_only | generator | error | 0 | 10 | 0.00 |
| un_meetings_only | jev | lookup | 2 | 10 | 20.00 |
| un_meetings_only | jev | practitioner | 0 | 10 | 0.00 |
| un_meetings_only | jev | conceptual | 8 | 10 | 80.00 |
| un_meetings_only | jev | comparison | 0 | 10 | 0.00 |
| un_meetings_only | jev | claim_verification | 0 | 10 | 0.00 |
| un_meetings_only | jev | source_finding | 0 | 10 | 0.00 |
| un_meetings_only | jev | skip | 0 | 10 | 0.00 |
| un_meetings_only | jev | error | 0 | 10 | 0.00 |
| eurlex_all | generator | lookup | 16 | 25 | 64.00 |
| eurlex_all | generator | fact_pattern | 3 | 25 | 12.00 |
| eurlex_all | generator | conceptual | 3 | 25 | 12.00 |
| eurlex_all | generator | comparison | 2 | 25 | 8.00 |
| eurlex_all | generator | claim_verification | 0 | 25 | 0.00 |
| eurlex_all | generator | source_finding | 0 | 25 | 0.00 |
| eurlex_all | generator | skip | 1 | 25 | 4.00 |
| eurlex_all | generator | error | 0 | 25 | 0.00 |
| eurlex_all | jev | lookup | 22 | 25 | 88.00 |
| eurlex_all | jev | fact_pattern | 0 | 25 | 0.00 |
| eurlex_all | jev | conceptual | 0 | 25 | 0.00 |
| eurlex_all | jev | comparison | 1 | 25 | 4.00 |
| eurlex_all | jev | claim_verification | 0 | 25 | 0.00 |
| eurlex_all | jev | source_finding | 0 | 25 | 0.00 |
| eurlex_all | jev | skip | 2 | 25 | 8.00 |
| eurlex_all | jev | error | 0 | 25 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | lookup | 25 | 24 | 58 | 0 | 31.50 | 12.08 | 19.42 | 17 | 1 | 23 |
| un_all | practitioner | 25 | 25 | 55 | 0 | 30.16 | 12 | 18.16 | 12 | 8 | 17 |
| un_all | conceptual | 25 | 23 | 41 | 0 | 31.13 | 11.96 | 19.17 | 16 | 3 | 19 |
| un_all | comparison | 25 | 23 | 24 | 1 | 29.78 | 11.96 | 17.83 | 8 | 9 | 12 |
| un_all | claim_verification | 25 | 25 | 37 | 0 | 31.08 | 12 | 19.08 | 12 | 3 | 17 |
| un_all | source_finding | 25 | 24 | 27 | 0 | 31.46 | 11.83 | 19.62 | 16 | 0 | 23 |
| un_without_meetings | lookup | 15 | 15 | 32 | 0 | 31.87 | 12.13 | 19.73 | 11 | 0 | 15 |
| un_without_meetings | practitioner | 15 | 15 | 31 | 0 | 30.13 | 12 | 18.13 | 5 | 5 | 10 |
| un_without_meetings | conceptual | 15 | 14 | 24 | 0 | 31 | 11.93 | 19.07 | 9 | 2 | 11 |
| un_without_meetings | comparison | 15 | 14 | 14 | 1 | 29 | 11.93 | 17.07 | 3 | 8 | 6 |
| un_without_meetings | claim_verification | 15 | 15 | 20 | 0 | 30.80 | 12 | 18.80 | 6 | 3 | 10 |
| un_without_meetings | source_finding | 15 | 14 | 16 | 0 | 31.50 | 12 | 19.50 | 9 | 0 | 13 |
| un_meetings_only | lookup | 10 | 9 | 26 | 0 | 30.89 | 12 | 18.89 | 6 | 1 | 8 |
| un_meetings_only | practitioner | 10 | 10 | 24 | 0 | 30.20 | 12 | 18.20 | 7 | 3 | 7 |
| un_meetings_only | conceptual | 10 | 9 | 17 | 0 | 31.33 | 12 | 19.33 | 7 | 1 | 8 |
| un_meetings_only | comparison | 10 | 9 | 10 | 0 | 31 | 12 | 19 | 5 | 1 | 6 |
| un_meetings_only | claim_verification | 10 | 10 | 17 | 0 | 31.50 | 12 | 19.50 | 6 | 0 | 7 |
| un_meetings_only | source_finding | 10 | 10 | 11 | 0 | 31.40 | 11.60 | 19.80 | 7 | 0 | 10 |
| eurlex_all | lookup | 25 | 23 | 50 | 2 | 31.70 | 12.13 | 19.57 | 18 | 0 | 22 |
| eurlex_all | fact_pattern | 25 | 24 | 43 | 1 | 29.29 | 12.08 | 17.21 | 5 | 12 | 11 |
| eurlex_all | conceptual | 25 | 22 | 29 | 3 | 31.14 | 11.95 | 19.18 | 11 | 2 | 20 |
| eurlex_all | comparison | 25 | 24 | 24 | 1 | 31.54 | 12.12 | 19.42 | 17 | 3 | 17 |
| eurlex_all | claim_verification | 25 | 24 | 28 | 1 | 30 | 11.92 | 18.08 | 7 | 8 | 16 |
| eurlex_all | source_finding | 25 | 24 | 24 | 1 | 31.38 | 11.96 | 19.42 | 13 | 0 | 24 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | generator | 25 | 25 | 0 | 16 | 25 | 0 | 0 | 30.76 | 1.32 | 30.76 | 22.96 | 32.08 |
| un_all | jev | 25 | 23 | 0 | 15 | 25 | 0 | 2 | 31.35 | 0.74 | 28.84 | 24.24 | 32.08 |
| un_without_meetings | generator | 15 | 15 | 0 | 9 | 15 | 0 | 0 | 30.87 | 1.27 | 30.87 | 21.27 | 32.13 |
| un_without_meetings | jev | 15 | 14 | 0 | 9 | 15 | 0 | 1 | 31.43 | 0.71 | 29.33 | 23.47 | 32.13 |
| un_meetings_only | generator | 10 | 10 | 0 | 7 | 10 | 0 | 0 | 30.60 | 1.40 | 30.60 | 25.50 | 32 |
| un_meetings_only | jev | 10 | 9 | 0 | 6 | 10 | 0 | 1 | 31.22 | 0.78 | 28.10 | 25.40 | 32 |
| eurlex_all | generator | 24 | 24 | 1 | 16 | 24 | 0 | 0 | 31.17 | 1.08 | 29.92 | 25.16 | 30.96 |
| eurlex_all | jev | 23 | 23 | 2 | 18 | 24 | 1 | 0 | 31.70 | 0.57 | 29.16 | 27.88 | 30.96 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | 25 | 16 | 4 | 2 | 19 | 1.92 | [-0.64, 5.44] |
| un_without_meetings | 15 | 11 | 2 | 2 | 11 | 1.53 | [-1.4666666666666666, 6.333333333333333] |
| un_meetings_only | 10 | 5 | 2 | 0 | 8 | 2.50 | [0, 7.3] |
| eurlex_all | 25 | 17 | 2 | 5 | 18 | 0.76 | [-1.04, 3.64] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | fact_pattern_score | conceptual_score | comparison_score | claim_verification_score | source_finding_score | practitioner_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S/RES/1900(2009) | 2009/s/res/1900_2009_#2 | comparison | lookup | lookup | 34 | — | 25 | 27 | 30 | — | 32 |
| A/RES/61/163 | 2006/a/res/61/163#4 | practitioner | conceptual | lookup, conceptual, comparison | 32 | — | 32 | 32 | 31 | 29 | 29 |
| A/RES/63/114 | 2008/a/res/63/114#2 | lookup | conceptual | lookup, practitioner, claim_verification | 32 | — | 31 | 25 | 32 | 31 | 32 |
| A/C.4/61/SR.10 | 2006/a/c_4/61/sr_10#17 | lookup | conceptual | lookup, comparison, source_finding | 32 | — | 31 | 32 | 30 | 32 | 24 |
| CEDAW/C/SR(858.B) | 2009/cedaw/c/sr_858_b_#22 | lookup | conceptual | lookup, practitioner, conceptual, comparison, claim_verification, source_finding | 32 | — | 32 | 32 | 32 | 32 | 32 |
| A/CN.9/SR.943 | 2013/a/cn_9/sr_943#2 | lookup | conceptual | lookup, practitioner, conceptual, source_finding | 32 | — | 32 | 26 | 31 | 32 | 32 |
| PBC/3/GNB/SR.1 | 2008/pbc/3/gnb/sr_1#15 | comparison | conceptual | lookup, practitioner, conceptual, comparison, claim_verification | 32 | — | 32 | 32 | 32 | 28 | 32 |
| A/C.3/55/SR.30 | 2000/a/c_3/55/sr_30#11 | lookup | conceptual | comparison, claim_verification, source_finding | 24 | — | — | 32 | 32 | 32 | 27 |
| S/1998/927 | 1998/s/1998/927#3 | comparison | conceptual | lookup, practitioner, comparison, claim_verification, source_finding | 32 | — | — | 32 | 32 | 32 | 32 |
| 32007R0041 | http://data.europa.eu/eli/reg/2007/41/art_79/oj | fact_pattern | lookup | lookup, comparison | 32 | 25 | 31 | 32 | 27 | 31 | — |
| 32009R0194 | http://data.europa.eu/eli/reg/2009/194/art_1/oj | fact_pattern | lookup | fact_pattern, conceptual, claim_verification | 31 | 32 | 32 | 29 | 32 | 31 | — |
| 32008R0683 | http://data.europa.eu/eli/reg/2008/683/art_22/oj | conceptual | skip | conceptual, comparison, source_finding | — | 28 | 32 | 32 | 31 | 32 | — |
| 32011R0349 | http://data.europa.eu/eli/reg/2011/349/art_1/oj | comparison | lookup | lookup, comparison, claim_verification, source_finding | 32 | 29 | 29 | 32 | 32 | 32 | — |
| 32005R0356 | http://data.europa.eu/eli/reg/2005/356/art_14/oj | fact_pattern | comparison | lookup, conceptual, comparison, source_finding | 32 | 31 | 32 | 32 | 31 | 32 | — |
| 32013L0034 | http://data.europa.eu/eli/dir/2013/34/art_33/oj | conceptual | lookup | comparison, claim_verification, source_finding | 31 | 26 | 28 | 32 | 32 | 32 | — |
| 32014R0909 | http://data.europa.eu/eli/reg/2014/909/art_43/oj | conceptual | lookup | lookup, fact_pattern, claim_verification, source_finding | 32 | 32 | 31 | 31 | 32 | 32 | — |
| 32009R1107 | http://data.europa.eu/eli/reg/2009/1107/art_31/oj | comparison | lookup | lookup | 32 | 30 | 29 | 30 | 31 | 31 | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| faithfulness | google/gemini-3.8-flash | 290 | 0 | 1690598 | 257639 | 2.23 | 0 |
| quality | google/gemini-3.8-flash | 290 | 0 | 2391262 | 644576 | 4.21 | 0 |

Reported cost is in USD where provided. Missing provider costs are unknown, not zero.

## Artifacts

- [Documents and full source payloads](documents.csv)
- [All modes side by side, one row per document](all_modes_per_document_with_jev_and_grades.csv)
- [Documents and decisions, including reasons/probabilities](decisions.csv)
- [Per-document comparison and regrets](document_comparison.csv)
- [All generated questions and verifier grades](all_mode_candidates.csv)
- [Per-target mode scores, questions, answers and statuses](mode_scores.csv)
- [Mode distributions](mode_distribution.csv)
- [Decider metrics](decider_performance.csv)
- [Pairwise confusion counts](confusion.csv)
- [Provider call trace](trace.md) and [raw trace](llm_calls.json)
- [Reproducible configuration](config.json), [selection](selection.json), and `run.sqlite`
