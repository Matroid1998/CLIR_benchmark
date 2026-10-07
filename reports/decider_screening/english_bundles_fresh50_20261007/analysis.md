# Decider screening

Run status: **completed**. Seed 20261007; 25 UN documents and 25 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

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
| un_all | lookup | 25 | 24 | 58 | 0 | 38.50 | 14.83 | 23.67 | 14 | 0 | 24 |
| un_all | practitioner | 25 | 25 | 55 | 0 | 36.12 | 14.92 | 21.20 | 3 | 8 | 18 |
| un_all | conceptual | 25 | 25 | 41 | 0 | 37.36 | 14.52 | 22.84 | 9 | 4 | 19 |
| un_all | comparison | 25 | 24 | 24 | 1 | 33.58 | 14.17 | 19.42 | 2 | 7 | 16 |
| un_all | claim_verification | 25 | 25 | 37 | 0 | 36.92 | 14.80 | 22.12 | 4 | 0 | 20 |
| un_all | source_finding | 25 | 25 | 27 | 0 | 37.80 | 14.68 | 23.12 | 8 | 1 | 21 |
| un_without_meetings | lookup | 15 | 15 | 32 | 0 | 39 | 14.87 | 24.13 | 12 | 0 | 15 |
| un_without_meetings | practitioner | 15 | 15 | 31 | 0 | 36.47 | 14.87 | 21.60 | 2 | 5 | 10 |
| un_without_meetings | conceptual | 15 | 15 | 24 | 0 | 37.33 | 14.40 | 22.93 | 5 | 3 | 10 |
| un_without_meetings | comparison | 15 | 14 | 14 | 1 | 33.43 | 14.29 | 19.14 | 0 | 4 | 10 |
| un_without_meetings | claim_verification | 15 | 15 | 20 | 0 | 36.67 | 14.73 | 21.93 | 2 | 0 | 12 |
| un_without_meetings | source_finding | 15 | 15 | 16 | 0 | 37.07 | 14.73 | 22.33 | 2 | 1 | 12 |
| un_meetings_only | lookup | 10 | 9 | 26 | 0 | 37.67 | 14.78 | 22.89 | 2 | 0 | 9 |
| un_meetings_only | practitioner | 10 | 10 | 24 | 0 | 35.60 | 15 | 20.60 | 1 | 3 | 8 |
| un_meetings_only | conceptual | 10 | 10 | 17 | 0 | 37.40 | 14.70 | 22.70 | 4 | 1 | 9 |
| un_meetings_only | comparison | 10 | 10 | 10 | 0 | 33.80 | 14 | 19.80 | 2 | 3 | 6 |
| un_meetings_only | claim_verification | 10 | 10 | 17 | 0 | 37.30 | 14.90 | 22.40 | 2 | 0 | 8 |
| un_meetings_only | source_finding | 10 | 10 | 11 | 0 | 38.90 | 14.60 | 24.30 | 6 | 0 | 9 |
| eurlex_all | lookup | 25 | 23 | 50 | 2 | 39.22 | 14.83 | 24.39 | 17 | 0 | 22 |
| eurlex_all | fact_pattern | 25 | 24 | 43 | 1 | 34.50 | 14.62 | 19.88 | 2 | 9 | 15 |
| eurlex_all | conceptual | 25 | 22 | 29 | 3 | 35.82 | 14.55 | 21.27 | 2 | 2 | 20 |
| eurlex_all | comparison | 25 | 24 | 24 | 1 | 36.21 | 14.33 | 21.88 | 5 | 3 | 18 |
| eurlex_all | claim_verification | 25 | 24 | 28 | 1 | 36.58 | 14.88 | 21.71 | 4 | 2 | 22 |
| eurlex_all | source_finding | 25 | 24 | 24 | 1 | 37.96 | 14.92 | 23.04 | 5 | 0 | 24 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | generator | 25 | 25 | 0 | 11 | 25 | 0 | 0 | 37.56 | 1.92 | 37.56 | 29.60 | 39.48 |
| un_all | jev | 25 | 25 | 0 | 11 | 25 | 0 | 0 | 37.56 | 1.92 | 37.56 | 28.88 | 39.48 |
| un_without_meetings | generator | 15 | 15 | 0 | 7 | 15 | 0 | 0 | 37.40 | 2.13 | 37.40 | 25.33 | 39.53 |
| un_without_meetings | jev | 15 | 15 | 0 | 8 | 15 | 0 | 0 | 37.73 | 1.80 | 37.73 | 25.93 | 39.53 |
| un_meetings_only | generator | 10 | 10 | 0 | 4 | 10 | 0 | 0 | 37.80 | 1.60 | 37.80 | 36 | 39.40 |
| un_meetings_only | jev | 10 | 10 | 0 | 3 | 10 | 0 | 0 | 37.30 | 2.10 | 37.30 | 33.30 | 39.40 |
| eurlex_all | generator | 24 | 24 | 1 | 13 | 24 | 0 | 0 | 38 | 1.75 | 36.48 | 33.52 | 38.16 |
| eurlex_all | jev | 23 | 23 | 2 | 16 | 24 | 1 | 0 | 39.17 | 0.57 | 36.04 | 34.48 | 38.16 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | 25 | 16 | 5 | 3 | 17 | 0 | [-1.2, 1.12] |
| un_without_meetings | 15 | 11 | 2 | 2 | 11 | -0.33 | [-2.066666666666667, 1.3333333333333333] |
| un_meetings_only | 10 | 5 | 3 | 1 | 6 | 0.50 | [-0.6, 1.8] |
| eurlex_all | 25 | 17 | 2 | 4 | 19 | 0.44 | [-1.56, 3.6] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | fact_pattern_score | conceptual_score | comparison_score | claim_verification_score | source_finding_score | practitioner_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S/RES/1900(2009) | 2009/s/res/1900_2009_#2 | comparison | lookup | lookup | 40 | — | 32 | 32 | 38 | 32 | 38 |
| A/RES/61/163 | 2006/a/res/61/163#4 | practitioner | conceptual | lookup, conceptual | 40 | — | 40 | 37 | 39 | 35 | 33 |
| A/RES/63/114 | 2008/a/res/63/114#2 | lookup | conceptual | lookup, source_finding | 39 | — | 37 | 28 | 36 | 39 | 37 |
| A/C.4/61/SR.10 | 2006/a/c_4/61/sr_10#17 | lookup | conceptual | lookup, conceptual, source_finding | 40 | — | 40 | 33 | 35 | 40 | 35 |
| CEDAW/C/SR(858.B) | 2009/cedaw/c/sr_858_b_#22 | lookup | conceptual | source_finding | 38 | — | 37 | 33 | 38 | 40 | 36 |
| A/CN.9/SR.943 | 2013/a/cn_9/sr_943#2 | lookup | conceptual | source_finding | 35 | — | 38 | 26 | 35 | 39 | 37 |
| PBC/3/GNB/SR.1 | 2008/pbc/3/gnb/sr_1#15 | comparison | conceptual | comparison, claim_verification, source_finding | 37 | — | 36 | 38 | 38 | 38 | 35 |
| A/C.3/55/SR.30 | 2000/a/c_3/55/sr_30#11 | lookup | conceptual | comparison | 36 | — | 31 | 40 | 39 | 38 | 28 |
| S/1998/927 | 1998/s/1998/927#3 | comparison | conceptual | lookup, practitioner | 40 | — | 29 | 37 | 36 | 37 | 40 |
| 32007R0041 | http://data.europa.eu/eli/reg/2007/41/art_79/oj | fact_pattern | lookup | lookup | 40 | 33 | 34 | 38 | 32 | 39 | — |
| 32009R0194 | http://data.europa.eu/eli/reg/2009/194/art_1/oj | fact_pattern | lookup | claim_verification | 39 | 39 | 39 | 37 | 40 | 36 | — |
| 32008R0683 | http://data.europa.eu/eli/reg/2008/683/art_22/oj | conceptual | skip | source_finding | — | 31 | 33 | 33 | 39 | 40 | — |
| 32011R0349 | http://data.europa.eu/eli/reg/2011/349/art_1/oj | comparison | lookup | lookup, comparison | 40 | 39 | 37 | 40 | 39 | 39 | — |
| 32005R0356 | http://data.europa.eu/eli/reg/2005/356/art_14/oj | fact_pattern | comparison | lookup, fact_pattern | 40 | 40 | 36 | 39 | 35 | 39 | — |
| 32013L0034 | http://data.europa.eu/eli/dir/2013/34/art_33/oj | conceptual | lookup | lookup, source_finding | 38 | 28 | 33 | 32 | 36 | 38 | — |
| 32014R0909 | http://data.europa.eu/eli/reg/2014/909/art_43/oj | conceptual | lookup | lookup | 40 | 37 | 34 | 36 | 37 | 39 | — |
| 32009R1107 | http://data.europa.eu/eli/reg/2009/1107/art_31/oj | comparison | lookup | lookup | 40 | 33 | 36 | 35 | 36 | 37 | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 50 | 0 | 366391 | 3865 | 0.02 | 0 |
| decider | gpt-5.6-luna | 50 | 0 | 310987 | 10261 | 0 | 50 |
| generation | gpt-5.6-luna | 300 | 0 | 1372472 | 193363 | 0 | 300 |
| faithfulness | anthropic/claude-sonnet-5.5 | 290 | 0 | 2116425 | 107771 | 5.31 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 295 | 0 | 3167583 | 476556 | 11.10 | 0 |

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
