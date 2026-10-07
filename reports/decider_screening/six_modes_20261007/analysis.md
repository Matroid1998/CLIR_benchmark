# Decider screening

Run status: **completed**. Seed 20260930; 50 UN documents and 50 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider in this run: eurlex: fact_pattern, lookup, conceptual, comparison, claim_verification, source_finding; un: lookup, practitioner, conceptual, comparison, claim_verification, source_finding. Legacy technical/descriptive modes are outside this comparison. All declared modes are eligible on UN meeting records, as on other UN documents.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 19; successfully repaired: 19. Repairs reuse generation and successful verifier stages. Recorded structural recoveries retain provider scores; missing grades are retried under the saved repair policy. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. Omitted positional indices can be restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| un_all | generator | lookup | 10 | 50 | 20.00 |
| un_all | generator | practitioner | 36 | 50 | 72.00 |
| un_all | generator | conceptual | 4 | 50 | 8.00 |
| un_all | generator | comparison | 0 | 50 | 0.00 |
| un_all | generator | claim_verification | 0 | 50 | 0.00 |
| un_all | generator | source_finding | 0 | 50 | 0.00 |
| un_all | generator | skip | 0 | 50 | 0.00 |
| un_all | generator | error | 0 | 50 | 0.00 |
| un_all | jev | lookup | 47 | 50 | 94.00 |
| un_all | jev | practitioner | 0 | 50 | 0.00 |
| un_all | jev | conceptual | 1 | 50 | 2.00 |
| un_all | jev | comparison | 1 | 50 | 2.00 |
| un_all | jev | claim_verification | 0 | 50 | 0.00 |
| un_all | jev | source_finding | 0 | 50 | 0.00 |
| un_all | jev | skip | 1 | 50 | 2.00 |
| un_all | jev | error | 0 | 50 | 0.00 |
| un_without_meetings | generator | lookup | 9 | 30 | 30.00 |
| un_without_meetings | generator | practitioner | 19 | 30 | 63.33 |
| un_without_meetings | generator | conceptual | 2 | 30 | 6.67 |
| un_without_meetings | generator | comparison | 0 | 30 | 0.00 |
| un_without_meetings | generator | claim_verification | 0 | 30 | 0.00 |
| un_without_meetings | generator | source_finding | 0 | 30 | 0.00 |
| un_without_meetings | generator | skip | 0 | 30 | 0.00 |
| un_without_meetings | generator | error | 0 | 30 | 0.00 |
| un_without_meetings | jev | lookup | 30 | 30 | 100.00 |
| un_without_meetings | jev | practitioner | 0 | 30 | 0.00 |
| un_without_meetings | jev | conceptual | 0 | 30 | 0.00 |
| un_without_meetings | jev | comparison | 0 | 30 | 0.00 |
| un_without_meetings | jev | claim_verification | 0 | 30 | 0.00 |
| un_without_meetings | jev | source_finding | 0 | 30 | 0.00 |
| un_without_meetings | jev | skip | 0 | 30 | 0.00 |
| un_without_meetings | jev | error | 0 | 30 | 0.00 |
| un_meetings_only | generator | lookup | 1 | 20 | 5.00 |
| un_meetings_only | generator | practitioner | 17 | 20 | 85.00 |
| un_meetings_only | generator | conceptual | 2 | 20 | 10.00 |
| un_meetings_only | generator | comparison | 0 | 20 | 0.00 |
| un_meetings_only | generator | claim_verification | 0 | 20 | 0.00 |
| un_meetings_only | generator | source_finding | 0 | 20 | 0.00 |
| un_meetings_only | generator | skip | 0 | 20 | 0.00 |
| un_meetings_only | generator | error | 0 | 20 | 0.00 |
| un_meetings_only | jev | lookup | 17 | 20 | 85.00 |
| un_meetings_only | jev | practitioner | 0 | 20 | 0.00 |
| un_meetings_only | jev | conceptual | 1 | 20 | 5.00 |
| un_meetings_only | jev | comparison | 1 | 20 | 5.00 |
| un_meetings_only | jev | claim_verification | 0 | 20 | 0.00 |
| un_meetings_only | jev | source_finding | 0 | 20 | 0.00 |
| un_meetings_only | jev | skip | 1 | 20 | 5.00 |
| un_meetings_only | jev | error | 0 | 20 | 0.00 |
| eurlex_all | generator | fact_pattern | 1 | 50 | 2.00 |
| eurlex_all | generator | lookup | 36 | 50 | 72.00 |
| eurlex_all | generator | conceptual | 2 | 50 | 4.00 |
| eurlex_all | generator | comparison | 0 | 50 | 0.00 |
| eurlex_all | generator | claim_verification | 0 | 50 | 0.00 |
| eurlex_all | generator | source_finding | 0 | 50 | 0.00 |
| eurlex_all | generator | skip | 11 | 50 | 22.00 |
| eurlex_all | generator | error | 0 | 50 | 0.00 |
| eurlex_all | jev | fact_pattern | 0 | 50 | 0.00 |
| eurlex_all | jev | lookup | 37 | 50 | 74.00 |
| eurlex_all | jev | conceptual | 1 | 50 | 2.00 |
| eurlex_all | jev | comparison | 0 | 50 | 0.00 |
| eurlex_all | jev | claim_verification | 0 | 50 | 0.00 |
| eurlex_all | jev | source_finding | 0 | 50 | 0.00 |
| eurlex_all | jev | skip | 12 | 50 | 24.00 |
| eurlex_all | jev | error | 0 | 50 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | lookup | 50 | 50 | 146 | 0 | 35.08 | 14.78 | 20.30 | 28 | 0 | 48 |
| un_all | practitioner | 50 | 50 | 114 | 0 | 33.06 | 14.74 | 18.32 | 10 | 7 | 44 |
| un_all | conceptual | 50 | 50 | 139 | 0 | 33.70 | 14.52 | 19.18 | 13 | 5 | 44 |
| un_all | comparison | 50 | 47 | 50 | 0 | 25.64 | 13.19 | 12.45 | 0 | 41 | 3 |
| un_all | claim_verification | 50 | 50 | 144 | 0 | 31.40 | 14.54 | 16.86 | 5 | 9 | 39 |
| un_all | source_finding | 50 | 50 | 50 | 0 | 33.08 | 14.22 | 18.86 | 8 | 1 | 43 |
| un_without_meetings | lookup | 30 | 30 | 88 | 0 | 35.47 | 14.80 | 20.67 | 19 | 0 | 30 |
| un_without_meetings | practitioner | 30 | 30 | 72 | 0 | 33.47 | 14.83 | 18.63 | 9 | 4 | 27 |
| un_without_meetings | conceptual | 30 | 30 | 84 | 0 | 33.80 | 14.67 | 19.13 | 6 | 4 | 26 |
| un_without_meetings | comparison | 30 | 28 | 30 | 0 | 25.25 | 12.93 | 12.32 | 0 | 24 | 2 |
| un_without_meetings | claim_verification | 30 | 30 | 84 | 0 | 31.73 | 14.50 | 17.23 | 2 | 5 | 24 |
| un_without_meetings | source_finding | 30 | 30 | 30 | 0 | 33.37 | 14.40 | 18.97 | 5 | 0 | 26 |
| un_meetings_only | lookup | 20 | 20 | 58 | 0 | 34.50 | 14.75 | 19.75 | 9 | 0 | 18 |
| un_meetings_only | practitioner | 20 | 20 | 42 | 0 | 32.45 | 14.60 | 17.85 | 1 | 3 | 17 |
| un_meetings_only | conceptual | 20 | 20 | 55 | 0 | 33.55 | 14.30 | 19.25 | 7 | 1 | 18 |
| un_meetings_only | comparison | 20 | 19 | 20 | 0 | 26.21 | 13.58 | 12.63 | 0 | 17 | 1 |
| un_meetings_only | claim_verification | 20 | 20 | 60 | 0 | 30.90 | 14.60 | 16.30 | 3 | 4 | 15 |
| un_meetings_only | source_finding | 20 | 20 | 20 | 0 | 32.65 | 13.95 | 18.70 | 3 | 1 | 17 |
| eurlex_all | fact_pattern | 50 | 38 | 104 | 12 | 35.71 | 14.84 | 20.87 | 16 | 3 | 33 |
| eurlex_all | lookup | 50 | 39 | 114 | 11 | 36.67 | 14.92 | 21.74 | 22 | 2 | 37 |
| eurlex_all | conceptual | 50 | 40 | 92 | 10 | 34.45 | 14.70 | 19.75 | 7 | 2 | 38 |
| eurlex_all | comparison | 50 | 50 | 53 | 0 | 29.26 | 13.64 | 15.62 | 1 | 18 | 25 |
| eurlex_all | claim_verification | 50 | 50 | 144 | 0 | 33.28 | 14.76 | 18.52 | 11 | 5 | 46 |
| eurlex_all | source_finding | 50 | 49 | 51 | 1 | 34.29 | 14.69 | 19.59 | 7 | 3 | 41 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | generator | 50 | 50 | 0 | 15 | 50 | 0 | 0 | 33.70 | 2.26 | 33.70 | 31.10 | 35.96 |
| un_all | jev | 49 | 49 | 1 | 26 | 50 | 1 | 0 | 35 | 1 | 34.30 | 32.28 | 35.96 |
| un_without_meetings | generator | 30 | 30 | 0 | 13 | 30 | 0 | 0 | 34.43 | 1.90 | 34.43 | 34.37 | 36.33 |
| un_without_meetings | jev | 30 | 30 | 0 | 19 | 30 | 0 | 0 | 35.47 | 0.87 | 35.47 | 35.47 | 36.33 |
| un_meetings_only | generator | 20 | 20 | 0 | 2 | 20 | 0 | 0 | 32.60 | 2.80 | 32.60 | 26.20 | 35.40 |
| un_meetings_only | jev | 19 | 19 | 1 | 7 | 20 | 1 | 0 | 34.26 | 1.21 | 32.55 | 27.50 | 35.40 |
| eurlex_all | generator | 39 | 39 | 11 | 23 | 50 | 11 | 0 | 36.72 | 0.62 | 28.64 | 27.30 | 36.62 |
| eurlex_all | jev | 38 | 38 | 12 | 21 | 50 | 12 | 0 | 36.61 | 0.71 | 27.82 | 26.48 | 36.62 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | 50 | 9 | 8 | 26 | 16 | -0.60 | [-1.7, 1.06] |
| un_without_meetings | 30 | 9 | 5 | 13 | 12 | -1.03 | [-1.8666666666666667, -0.2] |
| un_meetings_only | 20 | 0 | 3 | 13 | 4 | 0.05 | [-2.25, 3.7] |
| eurlex_all | 50 | 46 | 4 | 0 | 46 | 0.82 | [0.02, 2.32] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | fact_pattern_score | lookup_score | conceptual_score | comparison_score | claim_verification_score | source_finding_score | practitioner_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/RES/61/183 | 2006/a/res/61/183#3 | practitioner | lookup | lookup | — | 35 | 33 | 30 | 34 | 31 | 33 |
| A/RES/67/199 | 2013/a/res/67/199#12 | conceptual | lookup | conceptual | — | 32 | 36 | 28 | 33 | 29 | 30 |
| A/RES/68/254 | 2014/a/res/68/254#2 | practitioner | lookup | lookup | — | 37 | 33 | 26 | 26 | 34 | 33 |
| A/RES/55/114 | 2001/a/res/55/114#5 | practitioner | lookup | lookup | — | 37 | 34 | 22 | 30 | 32 | 32 |
| A/RES/62/137 | 2007/a/res/62/137#12 | practitioner | lookup | practitioner | — | 35 | 31 | 26 | 34 | 34 | 36 |
| A/RES/60/226 | 2005/a/res/60/226#3 | practitioner | lookup | conceptual | — | 33 | 35 | 26 | 33 | 34 | 33 |
| A/RES/68/18 | 2013/a/res/68/18#1 | practitioner | lookup | practitioner | — | 35 | 32 | 31 | 29 | 35 | 36 |
| S/RES/1806(2008) | 2008/s/res/1806_2008_#8 | practitioner | lookup | practitioner | — | 37 | 37 | 23 | 31 | 35 | 39 |
| S/RES/1466(2003) | 2003/s/res/1466_2003_#3 | practitioner | lookup | lookup, practitioner, conceptual, claim_verification, source_finding | — | 35 | 35 | 21 | 35 | 35 | 35 |
| S/RES/1565(2004) | 2004/s/res/1565_2004_#11 | practitioner | lookup | lookup | — | 39 | 36 | 24 | 31 | 32 | 34 |
| A/RES/60/47 | 2005/a/res/60/47#0 | practitioner | lookup | lookup, conceptual | — | 34 | 34 | 33 | 31 | 33 | 32 |
| S/RES/1988(2011) | 2011/s/res/1988_2011_#19 | practitioner | lookup | conceptual | — | 36 | 37 | 23 | 34 | 29 | 32 |
| A/RES/67/145 | 2013/a/res/67/145#7 | conceptual | lookup | lookup | — | 37 | 36 | 17 | 32 | 35 | 31 |
| A/RES/58/298 | 2003/a/res/58/298#4 | practitioner | lookup | lookup, practitioner, source_finding | — | 37 | 33 | 27 | 35 | 37 | 37 |
| A/RES/57/300 | 2003/a/res/57/300#10 | practitioner | lookup | lookup | — | 39 | 35 | 29 | 35 | 34 | 34 |
| A/RES/67/222 | 2013/a/res/67/222#6 | practitioner | lookup | lookup, source_finding | — | 35 | 33 | 26 | 30 | 35 | 32 |
| S/RES/2140(2014) | 2014/s/res/2140__2014_#13 | practitioner | lookup | lookup | — | 36 | 34 | 20 | 32 | 32 | 35 |
| A/C.2/58/SR.24 | 2004/a/c_2/58/sr_24#18 | practitioner | lookup | lookup | — | 36 | 33 | 24 | 28 | 32 | 33 |
| CD/PV.1097 | 2008/cd/pv_1097#14 | practitioner | lookup | conceptual | — | 34 | 35 | 25 | 29 | 34 | 31 |
| A/C.5/60/SR.64 | 2006/a/c_5/60/sr_64#14 | conceptual | lookup | source_finding | — | 34 | 33 | 25 | 33 | 38 | 33 |
| CEDAW/C/SR.451 | 2001/cedaw/c/sr_451#4 | practitioner | lookup | claim_verification | — | 35 | 32 | 20 | 36 | 33 | 30 |
| A/AC.109/2008/SR.2 | 2008/a/ac_109/2008/sr_2#1 | practitioner | lookup | source_finding | — | 35 | 35 | 30 | 34 | 36 | 35 |
| CCPR/C/SR.2695 | 2010/ccpr/c/sr_2695#25 | practitioner | lookup | claim_verification | — | 32 | 32 | 26 | 33 | 28 | 32 |
| GC.12/C.1/SR.1 | 2007/gc_12/c_1/sr_1#10 | practitioner | lookup | conceptual | — | 34 | 36 | 27 | 27 | 33 | 34 |
| CEDAW/C/SR.724 | 2006/cedaw/c/sr_724#18 | practitioner | lookup | lookup | — | 36 | 31 | 22 | 30 | 34 | 33 |
| CD/PV.983 | 2005/cd/pv_983#13 | lookup | skip | claim_verification | — | 32 | 32 | — | 34 | 32 | 31 |
| GC.7/C.1/SR.5 | 1998/gc_7/c_1/sr_5#16 | practitioner | lookup | lookup | — | 36 | 33 | 21 | 31 | 32 | 34 |
| CCW/CONF.III/SR.2 | 2006/ccw/conf_iii/sr_2#8 | practitioner | lookup | conceptual | — | 34 | 36 | 28 | 28 | 31 | 33 |
| CD/PV.880 | 2001/cd/pv_880#1 | practitioner | lookup | lookup | — | 35 | 32 | 26 | 30 | 33 | 31 |
| A/CN.9/SR.917 | 2010/a/cn_9/sr_917#10 | practitioner | comparison | lookup | — | 35 | 33 | 32 | 34 | 33 | 30 |
| A/58/PV.1 | 2003/a/58/pv_1#15 | practitioner | conceptual | lookup | — | 35 | 31 | 26 | 31 | 26 | 33 |
| CEDAW/C/SR(770.B) | 2007/cedaw/c/sr_770_b_#18 | practitioner | lookup | lookup | — | 36 | 33 | 34 | 27 | 33 | 35 |
| A/C.4/57/SR.18 | 2002/a/c_4/57/sr_18#15 | practitioner | lookup | conceptual | — | 31 | 33 | 29 | 27 | 31 | 29 |
| CEDAW/C/SR.778 | 2007/cedaw/c/sr_778#5 | practitioner | lookup | lookup | — | 36 | 35 | 25 | 33 | 33 | 31 |
| CD/PV.841 | 2000/cd/pv_841#11 | conceptual | lookup | conceptual | — | 35 | 36 | 24 | 32 | 35 | 34 |
| CEDAW/C/SR.434 | 1999/cedaw/c/sr_434#16 | practitioner | lookup | conceptual, source_finding | — | 34 | 35 | 25 | 29 | 35 | 32 |
| A/AC.109/2009/SR.7 | 2009/a/ac_109/2009/sr_7#4 | practitioner | lookup | lookup, practitioner, conceptual | — | 35 | 35 | 29 | 32 | 31 | 35 |
| S/2008/774 | 2008/s/2008/774#11 | practitioner | lookup | lookup | — | 37 | 35 | 25 | 30 | 35 | 33 |
| S/2012/718 | 2012/s/2012/718#7 | practitioner | lookup | practitioner | — | 32 | 31 | 24 | 33 | 34 | 35 |
| S/1998/458 | 1998/s/1998/458#1 | practitioner | lookup | claim_verification | — | 36 | 35 | 22 | 37 | 31 | 33 |
| S/2004/505 | 2004/s/2004/505#15 | practitioner | lookup | lookup | — | 37 | 31 | — | 36 | 32 | 34 |
| 32011R0492 | http://data.europa.eu/eli/reg/2011/492/art_17/oj | lookup | conceptual | source_finding | 31 | 34 | 33 | 29 | 34 | 35 | — |
| 32012R0966 | http://data.europa.eu/eli/reg/2012/966/art_56/oj | conceptual | skip | lookup | — | 38 | 35 | 25 | 35 | 33 | — |
| 32011R1008 | http://data.europa.eu/eli/reg_impl/2011/1008/art_1/oj | fact_pattern | lookup | fact_pattern | 39 | 37 | 35 | 28 | 34 | 36 | — |
| 32006R1083 | http://data.europa.eu/eli/reg/2006/1083/art_47/oj | conceptual | lookup | conceptual | 36 | 35 | 38 | 35 | 33 | 37 | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 100 | 0 | 468884 | 7654 | 0.02 | 0 |
| decider | gpt-5.6-luna | 100 | 0 | 331118 | 18617 | 0 | 100 |
| generation | gpt-5.6-luna | 600 | 0 | 2828408 | 507817 | 0 | 600 |
| faithfulness | anthropic/claude-sonnet-5.5 | 568 | 0 | 4104775 | 186206 | 10.07 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 648 | 1 | 5965067 | 874901 | 20.68 | 1 |
| quality_repair | anthropic/claude-sonnet-5.5 | 7 | 0 | 71055 | 7651 | 0.22 | 0 |

Reported cost is in USD where provided. Missing provider costs are unknown, not zero.

## Artifacts

- [Documents and full source payloads](documents.csv)
- [Documents and decisions, including reasons/probabilities](decisions.csv)
- [Per-document comparison and regrets](document_comparison.csv)
- [All generated questions and verifier grades](all_mode_candidates.csv)
- [Per-target mode scores, questions, answers and statuses](mode_scores.csv)
- [Mode distributions](mode_distribution.csv)
- [Decider metrics](decider_performance.csv)
- [Pairwise confusion counts](confusion.csv)
- [Provider call trace](trace.md) and [raw trace](llm_calls.json)
- [Reproducible configuration](config.json), [selection](selection.json), and `run.sqlite`
