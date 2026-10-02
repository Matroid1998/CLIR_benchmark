# Decider screening

Run status: **completed**. Seed 20260930; 50 UN documents and 50 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider: lookup/practitioner/semantic for UN and fact_pattern/lookup for EUR-Lex. Legacy technical/descriptive modes are outside this comparison. All three modes are eligible on UN meeting records, as on other UN documents.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 14; successfully repaired: 14. Repairs reuse generation and successful verifier stages. The faithfulness retry adds only an explicit actual-batch-size instruction to avoid fabricated extra grade objects when fewer than three candidates were supplied. The grading rubric is unchanged. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. One quality response omitted positional indices; those were restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| un_all | generator | lookup | 19 | 50 | 38.00 |
| un_all | generator | practitioner | 27 | 50 | 54.00 |
| un_all | generator | semantic | 4 | 50 | 8.00 |
| un_all | generator | skip | 0 | 50 | 0.00 |
| un_all | generator | error | 0 | 50 | 0.00 |
| un_all | jev | lookup | 15 | 50 | 30.00 |
| un_all | jev | practitioner | 0 | 50 | 0.00 |
| un_all | jev | semantic | 35 | 50 | 70.00 |
| un_all | jev | skip | 0 | 50 | 0.00 |
| un_all | jev | error | 0 | 50 | 0.00 |
| un_without_meetings | generator | lookup | 14 | 30 | 46.67 |
| un_without_meetings | generator | practitioner | 12 | 30 | 40.00 |
| un_without_meetings | generator | semantic | 4 | 30 | 13.33 |
| un_without_meetings | generator | skip | 0 | 30 | 0.00 |
| un_without_meetings | generator | error | 0 | 30 | 0.00 |
| un_without_meetings | jev | lookup | 14 | 30 | 46.67 |
| un_without_meetings | jev | practitioner | 0 | 30 | 0.00 |
| un_without_meetings | jev | semantic | 16 | 30 | 53.33 |
| un_without_meetings | jev | skip | 0 | 30 | 0.00 |
| un_without_meetings | jev | error | 0 | 30 | 0.00 |
| un_meetings_only | generator | lookup | 5 | 20 | 25.00 |
| un_meetings_only | generator | practitioner | 15 | 20 | 75.00 |
| un_meetings_only | generator | semantic | 0 | 20 | 0.00 |
| un_meetings_only | generator | skip | 0 | 20 | 0.00 |
| un_meetings_only | generator | error | 0 | 20 | 0.00 |
| un_meetings_only | jev | lookup | 1 | 20 | 5.00 |
| un_meetings_only | jev | practitioner | 0 | 20 | 0.00 |
| un_meetings_only | jev | semantic | 19 | 20 | 95.00 |
| un_meetings_only | jev | skip | 0 | 20 | 0.00 |
| un_meetings_only | jev | error | 0 | 20 | 0.00 |
| eurlex_all | generator | fact_pattern | 34 | 50 | 68.00 |
| eurlex_all | generator | lookup | 4 | 50 | 8.00 |
| eurlex_all | generator | skip | 12 | 50 | 24.00 |
| eurlex_all | generator | error | 0 | 50 | 0.00 |
| eurlex_all | jev | fact_pattern | 25 | 50 | 50.00 |
| eurlex_all | jev | lookup | 20 | 50 | 40.00 |
| eurlex_all | jev | skip | 5 | 50 | 10.00 |
| eurlex_all | jev | error | 0 | 50 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | lookup | 50 | 49 | 145 | 0 | 34.55 | 14.80 | 19.76 | 32 | 2 | 34 |
| un_all | practitioner | 50 | 48 | 141 | 0 | 34 | 14.50 | 19.50 | 19 | 7 | 36 |
| un_all | semantic | 50 | 50 | 137 | 0 | 34.16 | 14.64 | 19.52 | 20 | 0 | 37 |
| un_without_meetings | lookup | 30 | 30 | 86 | 0 | 34.80 | 14.73 | 20.07 | 21 | 1 | 21 |
| un_without_meetings | practitioner | 30 | 29 | 86 | 0 | 33.83 | 14.69 | 19.14 | 9 | 6 | 18 |
| un_without_meetings | semantic | 30 | 30 | 83 | 0 | 33.93 | 14.63 | 19.30 | 8 | 0 | 23 |
| un_meetings_only | lookup | 20 | 19 | 59 | 0 | 34.16 | 14.89 | 19.26 | 11 | 1 | 13 |
| un_meetings_only | practitioner | 20 | 19 | 55 | 0 | 34.26 | 14.21 | 20.05 | 10 | 1 | 18 |
| un_meetings_only | semantic | 20 | 20 | 54 | 0 | 34.50 | 14.65 | 19.85 | 12 | 0 | 14 |
| eurlex_all | fact_pattern | 50 | 39 | 109 | 11 | 33.95 | 14.49 | 19.46 | 8 | 2 | 32 |
| eurlex_all | lookup | 50 | 40 | 113 | 10 | 36.48 | 14.85 | 21.62 | 35 | 0 | 31 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | generator | 50 | 49 | 0 | 26 | 50 | 0 | 1 | 34.29 | 1.16 | 33.60 | 23.96 | 35.42 |
| un_all | jev | 50 | 50 | 0 | 30 | 50 | 0 | 0 | 34.50 | 0.92 | 34.50 | 23.98 | 35.42 |
| un_without_meetings | generator | 30 | 30 | 0 | 16 | 30 | 0 | 0 | 34.27 | 1.27 | 34.27 | 21.83 | 35.53 |
| un_without_meetings | jev | 30 | 30 | 0 | 17 | 30 | 0 | 0 | 34.47 | 1.07 | 34.47 | 25.47 | 35.53 |
| un_meetings_only | generator | 20 | 19 | 0 | 10 | 20 | 0 | 1 | 34.32 | 1 | 32.60 | 27.15 | 35.25 |
| un_meetings_only | jev | 20 | 20 | 0 | 13 | 20 | 0 | 0 | 34.55 | 0.70 | 34.55 | 21.75 | 35.25 |
| eurlex_all | generator | 38 | 38 | 12 | 6 | 40 | 2 | 0 | 34.05 | 2.63 | 25.88 | 20.66 | 29.32 |
| eurlex_all | jev | 45 | 39 | 5 | 16 | 40 | 1 | 0 | 34.79 | 1.92 | 27.14 | 22.82 | 29.32 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | 50 | 12 | 15 | 16 | 19 | -0.90 | [-2.56, 0.18] |
| un_without_meetings | 30 | 11 | 8 | 8 | 14 | -0.20 | [-0.9666666666666667, 0.5333333333333333] |
| un_meetings_only | 20 | 1 | 7 | 8 | 5 | -1.95 | [-5.6, 0.35] |
| eurlex_all | 50 | 30 | 2 | 11 | 37 | -1.26 | [-3.82, 1.04] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | practitioner_score | semantic_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A/RES/65/212 | 2011/a/res/65/212#13 | lookup | semantic | lookup, practitioner | 35 | 35 | 34 |
| A/RES/61/183 | 2006/a/res/61/183#3 | practitioner | semantic | lookup, semantic | 36 | 34 | 36 |
| A/RES/65/263 | 2011/a/res/65/263#2 | practitioner | lookup | lookup | 37 | 30 | 35 |
| A/RES/68/143 | 2013/a/res/68/143#7 | practitioner | semantic | lookup | 38 | 34 | 31 |
| A/RES/55/114 | 2001/a/res/55/114#5 | practitioner | semantic | lookup | 35 | 33 | 33 |
| A/RES/62/137 | 2007/a/res/62/137#12 | practitioner | lookup | lookup, semantic | 35 | 31 | 35 |
| S/RES/1376(2001) | 2001/s/res/1376_2001_#2 | lookup | semantic | lookup, semantic | 36 | 33 | 36 |
| S/RES/1806(2008) | 2008/s/res/1806_2008_#8 | lookup | semantic | lookup | 38 | 35 | 37 |
| S/RES/1466(2003) | 2003/s/res/1466_2003_#3 | practitioner | semantic | semantic | 34 | 33 | 36 |
| A/RES/56/188 | 2002/a/res/56/188#8 | practitioner | semantic | lookup, semantic | 33 | 32 | 33 |
| A/RES/60/47 | 2005/a/res/60/47#0 | semantic | lookup | semantic | 33 | 32 | 34 |
| A/RES/59/61 | 2004/a/res/59/61#0 | semantic | lookup | lookup | 33 | 32 | 31 |
| A/RES/67/222 | 2013/a/res/67/222#6 | practitioner | semantic | lookup, semantic | 36 | 34 | 36 |
| A/RES/57/137 | 2003/a/res/57/137#1 | lookup | semantic | practitioner | 33 | 35 | 33 |
| S/RES/2140(2014) | 2014/s/res/2140__2014_#13 | practitioner | lookup | lookup | 36 | 35 | 35 |
| A/C.2/58/SR.24 | 2004/a/c_2/58/sr_24#18 | practitioner | semantic | practitioner | 29 | 35 | 31 |
| CD/PV.1097 | 2008/cd/pv_1097#14 | practitioner | semantic | semantic | — | — | 34 |
| A/C.5/60/SR.64 | 2006/a/c_5/60/sr_64#14 | practitioner | semantic | semantic | 33 | 33 | 37 |
| CEDAW/C/SR.451 | 2001/cedaw/c/sr_451#4 | practitioner | semantic | lookup, practitioner, semantic | 35 | 35 | 35 |
| CCPR/C/SR.2695 | 2010/ccpr/c/sr_2695#25 | practitioner | semantic | lookup, semantic | 33 | 32 | 33 |
| GC.12/C.1/SR.1 | 2007/gc_12/c_1/sr_1#10 | practitioner | semantic | lookup, practitioner, semantic | 36 | 36 | 36 |
| CEDAW/C/SR.724 | 2006/cedaw/c/sr_724#18 | lookup | semantic | practitioner | 35 | 36 | 33 |
| CD/PV.983 | 2005/cd/pv_983#13 | practitioner | semantic | semantic | 31 | 33 | 35 |
| GC.7/C.1/SR.5 | 1998/gc_7/c_1/sr_5#16 | practitioner | semantic | lookup | 37 | 35 | 34 |
| CCW/CONF.III/SR.2 | 2006/ccw/conf_iii/sr_2#8 | lookup | semantic | semantic | 33 | 33 | 35 |
| CD/PV.880 | 2001/cd/pv_880#1 | lookup | semantic | lookup, practitioner, semantic | 35 | 35 | 35 |
| A/CN.9/SR.917 | 2010/a/cn_9/sr_917#10 | practitioner | semantic | practitioner | 34 | 36 | 35 |
| A/58/PV.1 | 2003/a/58/pv_1#15 | practitioner | semantic | lookup, semantic | 33 | 31 | 33 |
| CEDAW/C/SR(770.B) | 2007/cedaw/c/sr_770_b_#18 | practitioner | semantic | semantic | 35 | 33 | 36 |
| A/C.4/57/SR.18 | 2002/a/c_4/57/sr_18#15 | lookup | semantic | lookup | 35 | 33 | 34 |
| CEDAW/C/SR.778 | 2007/cedaw/c/sr_778#5 | practitioner | semantic | lookup, practitioner | 36 | 36 | 35 |
| CD/PV.841 | 2000/cd/pv_841#11 | practitioner | semantic | lookup, practitioner | 36 | 36 | 35 |
| CEDAW/C/SR.434 | 1999/cedaw/c/sr_434#16 | practitioner | semantic | lookup, semantic | 35 | 33 | 35 |
| A/AC.109/2009/SR.7 | 2009/a/ac_109/2009/sr_7#4 | practitioner | semantic | practitioner, semantic | 34 | 36 | 36 |
| S/2008/774 | 2008/s/2008/774#11 | practitioner | semantic | practitioner | 34 | 36 | 34 |
| S/2012/718 | 2012/s/2012/718#7 | practitioner | semantic | practitioner | 32 | 33 | 31 |
| S/1998/458 | 1998/s/1998/458#1 | practitioner | semantic | lookup, practitioner | 36 | 36 | 31 |
| S/2004/674 | 2004/s/2004/674#6 | lookup | semantic | lookup | 35 | — | 34 |
| 32010L0042 | http://data.europa.eu/eli/dir/2010/42/art_2/oj | skip | lookup |  | — | — | — |
| 32011L0081 | http://data.europa.eu/eli/dir/2011/81/art_2/oj | skip | lookup | lookup | 33 | — | — |
| 32011R1077 | http://data.europa.eu/eli/reg/2011/1077/art_14/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32006L0060 | http://data.europa.eu/eli/dir/2006/60/art_2/oj | skip | lookup |  | — | — | — |
| 32011R0492 | http://data.europa.eu/eli/reg/2011/492/art_17/oj | skip | lookup | lookup | 39 | — | — |
| 32005L0086 | http://data.europa.eu/eli/dir/2005/86/art_2/oj | skip | lookup |  | — | — | — |
| 32012R0966 | http://data.europa.eu/eli/reg/2012/966/art_56/oj | lookup | skip | fact_pattern | 33 | — | — |
| 32007L0068 | http://data.europa.eu/eli/dir/2007/68/art_2/oj | skip | lookup |  | — | — | — |
| 32004L0066 | http://data.europa.eu/eli/dir/2004/66/art_2/oj | skip | lookup |  | — | — | — |
| 32011R1333 | http://data.europa.eu/eli/reg_impl/2011/1333/art_11/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32012R0282 | http://data.europa.eu/eli/reg_impl/2012/282/art_1/oj | fact_pattern | lookup | fact_pattern, lookup | 36 | — | — |
| 32007R0520 | http://data.europa.eu/eli/reg/2007/520/art_24/oj | lookup | fact_pattern | fact_pattern | 32 | — | — |
| 32005L0009 | http://data.europa.eu/eli/dir/2005/9/art_2/oj | skip | lookup |  | — | — | — |
| 32014R0788 | http://data.europa.eu/eli/reg/2014/788/art_20/oj | fact_pattern | lookup | fact_pattern | 33 | — | — |
| 32013R1381 | http://data.europa.eu/eli/reg/2013/1381/art_5/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32009R0436 | http://data.europa.eu/eli/reg/2009/436/art_36/oj | fact_pattern | lookup | lookup | 39 | — | — |
| 32013R0231 | http://data.europa.eu/eli/reg_del/2013/231/art_43/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32006R1083 | http://data.europa.eu/eli/reg/2006/1083/art_47/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32014L0026 | http://data.europa.eu/eli/dir/2014/26/art_2/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32012R0493 | http://data.europa.eu/eli/reg/2012/493/art_3/oj | fact_pattern | lookup | lookup | 40 | — | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 100 | 0 | 320634 | 4425 | 0.01 | 0 |
| decider | gpt-5.6-luna | 100 | 0 | 257968 | 18441 | 0 | 100 |
| generation | gpt-5.6-luna | 250 | 0 | 774903 | 265794 | 0 | 250 |
| faithfulness | anthropic/claude-sonnet-5.5 | 237 | 0 | 1355798 | 100777 | 3.72 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 328 | 0 | 2347289 | 635059 | 11.05 | 0 |

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
