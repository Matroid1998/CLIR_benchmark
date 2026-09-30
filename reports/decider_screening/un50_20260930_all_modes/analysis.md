# Decider screening

Run status: **completed**. Seed 20260929; 50 UN documents and 0 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider: lookup/practitioner/semantic for UN and fact_pattern/lookup for EUR-Lex. Legacy technical/descriptive modes are outside this comparison. All three modes are eligible on UN meeting records, as on other UN documents.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 14; successfully repaired: 14. Repairs reuse generation and successful verifier stages. The faithfulness retry adds only an explicit actual-batch-size instruction to avoid fabricated extra grade objects when fewer than three candidates were supplied. The grading rubric is unchanged. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. One quality response omitted positional indices; those were restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| un_all | generator | lookup | 15 | 50 | 30.00 |
| un_all | generator | practitioner | 5 | 50 | 10.00 |
| un_all | generator | semantic | 25 | 50 | 50.00 |
| un_all | generator | skip | 5 | 50 | 10.00 |
| un_all | generator | error | 0 | 50 | 0.00 |
| un_all | jev | lookup | 4 | 50 | 8.00 |
| un_all | jev | practitioner | 23 | 50 | 46.00 |
| un_all | jev | semantic | 14 | 50 | 28.00 |
| un_all | jev | skip | 9 | 50 | 18.00 |
| un_all | jev | error | 0 | 50 | 0.00 |
| un_without_meetings | generator | lookup | 13 | 30 | 43.33 |
| un_without_meetings | generator | practitioner | 4 | 30 | 13.33 |
| un_without_meetings | generator | semantic | 12 | 30 | 40.00 |
| un_without_meetings | generator | skip | 1 | 30 | 3.33 |
| un_without_meetings | generator | error | 0 | 30 | 0.00 |
| un_without_meetings | jev | lookup | 4 | 30 | 13.33 |
| un_without_meetings | jev | practitioner | 14 | 30 | 46.67 |
| un_without_meetings | jev | semantic | 7 | 30 | 23.33 |
| un_without_meetings | jev | skip | 5 | 30 | 16.67 |
| un_without_meetings | jev | error | 0 | 30 | 0.00 |
| un_meetings_only | generator | lookup | 2 | 20 | 10.00 |
| un_meetings_only | generator | practitioner | 1 | 20 | 5.00 |
| un_meetings_only | generator | semantic | 13 | 20 | 65.00 |
| un_meetings_only | generator | skip | 4 | 20 | 20.00 |
| un_meetings_only | generator | error | 0 | 20 | 0.00 |
| un_meetings_only | jev | lookup | 0 | 20 | 0.00 |
| un_meetings_only | jev | practitioner | 9 | 20 | 45.00 |
| un_meetings_only | jev | semantic | 7 | 20 | 35.00 |
| un_meetings_only | jev | skip | 4 | 20 | 20.00 |
| un_meetings_only | jev | error | 0 | 20 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | lookup | 50 | 40 | 84 | 10 | 29.65 | 14 | 15.65 | 17 | 15 | 20 |
| un_all | practitioner | 50 | 38 | 87 | 11 | 29.08 | 13.74 | 15.34 | 11 | 20 | 15 |
| un_all | semantic | 50 | 41 | 98 | 9 | 30.46 | 13.10 | 17.37 | 24 | 12 | 26 |
| un_without_meetings | lookup | 30 | 21 | 41 | 9 | 30.38 | 14.14 | 16.24 | 12 | 8 | 11 |
| un_without_meetings | practitioner | 30 | 23 | 50 | 7 | 29.30 | 13.83 | 15.48 | 7 | 12 | 10 |
| un_without_meetings | semantic | 30 | 25 | 60 | 5 | 30.28 | 13.08 | 17.20 | 13 | 7 | 15 |
| un_meetings_only | lookup | 20 | 19 | 43 | 1 | 28.84 | 13.84 | 15 | 5 | 7 | 9 |
| un_meetings_only | practitioner | 20 | 15 | 37 | 4 | 28.73 | 13.60 | 15.13 | 4 | 8 | 5 |
| un_meetings_only | semantic | 20 | 16 | 38 | 4 | 30.75 | 13.12 | 17.62 | 11 | 5 | 11 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | generator | 45 | 41 | 5 | 28 | 46 | 4 | 1 | 30.80 | 0.71 | 25.26 | 17.10 | 28.64 |
| un_all | jev | 41 | 36 | 9 | 15 | 46 | 7 | 3 | 30.19 | 1.56 | 21.74 | 13.10 | 28.64 |
| un_without_meetings | generator | 29 | 26 | 1 | 17 | 27 | 1 | 0 | 30.42 | 0.85 | 26.37 | 16.60 | 28 |
| un_without_meetings | jev | 25 | 23 | 5 | 10 | 27 | 4 | 0 | 30.09 | 1.30 | 23.07 | 13.37 | 28 |
| un_meetings_only | generator | 16 | 15 | 4 | 11 | 19 | 3 | 1 | 31.47 | 0.47 | 23.60 | 17.85 | 29.60 |
| un_meetings_only | jev | 16 | 13 | 4 | 5 | 19 | 3 | 3 | 30.38 | 2 | 19.75 | 12.70 | 29.60 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | 50 | 22 | 17 | 4 | 29 | 3.52 | [1.3, 6.12] |
| un_without_meetings | 30 | 12 | 10 | 3 | 17 | 3.30 | [0.5666666666666667, 6.766666666666667] |
| un_meetings_only | 20 | 10 | 7 | 1 | 12 | 3.85 | [0.65, 8.15] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | practitioner_score | semantic_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A/RES/60/163 | 2005/a/res/60/163#4 | semantic | skip |  | — | — | — |
| S/RES/1353(2001) | 2001/s/res/1353_2001_#8 | lookup | practitioner | lookup | 32 | 31 | 28 |
| A/RES/56/160 | 2002/a/res/56/160#6 | lookup | practitioner | lookup | 34 | 31 | 32 |
| A/RES/52/56 | 1997/a/res/52/56#10 | practitioner | lookup | practitioner | 27 | 28 | — |
| A/RES/55/201 | 2001/a/res/55/201#6 | semantic | practitioner |  | — | — | — |
| A/RES/68/188 | 2014/a/res/68/188#7 | semantic | skip | semantic | — | — | 30 |
| A/RES/57/326 | 2002/a/res/57/326#1 | lookup | practitioner | practitioner | 32 | 33 | 32 |
| A/RES/57/97 | 2003/a/res/57/97#3 | lookup | practitioner | lookup | 33 | 29 | 32 |
| A/RES/60/140 | 2005/a/res/60/140#5 | semantic | lookup |  | — | — | — |
| A/RES/65/141 | 2011/a/res/65/141#10 | semantic | practitioner | practitioner | 30 | 32 | 28 |
| A/RES/61/173 | 2006/a/res/61/173#1 | lookup | skip | semantic | 25 | 28 | 29 |
| A/RES/57/124 | 2003/a/res/57/124#2 | lookup | practitioner | lookup, practitioner | 31 | 31 | 30 |
| A/RES/57/183 | 2003/a/res/57/183#9 | lookup | practitioner | lookup, practitioner, semantic | 31 | 31 | 31 |
| A/HRC/RES/25/6 | 2014/a/hrc/res/25/6#7 | lookup | practitioner | semantic | 27 | 28 | 29 |
| A/RES/67/276 | 2013/a/res/67/276#2 | practitioner | skip | practitioner | — | 32 | 28 |
| CD/PV.1154 | 2009/cd/pv_1154#3 | semantic | practitioner | semantic | 31 | 29 | 35 |
| CEDAW/C/SR.438 | 1999/cedaw/c/sr_438#8 | semantic | practitioner | semantic | 33 | 31 | 35 |
| A/C.5/58/SR.45 | 2004/a/c_5/58/sr_45#2 | semantic | practitioner | semantic | 32 | 32 | 34 |
| A/C.3/66/SR.22 | 2012/a/c_3/66/sr_22#7 | semantic | practitioner | practitioner | 30 | 32 | 30 |
| A/CN.9/SR.845 | 2007/a/cn_9/sr_845#7 | lookup | practitioner | lookup | 32 | — | 30 |
| CEDAW/C/SR.560 | 2002/cedaw/c/sr_560#20 | semantic | practitioner | semantic | 30 | 31 | 33 |
| A/CN.9/SR.841 | 2007/a/cn_9/sr_841#21 | lookup | semantic | lookup | 31 | — | 24 |
| CD/PV.1063 | 2007/cd/pv_1063#7 | semantic | practitioner | semantic | 24 | — | 26 |
| GC.15/SR.9 | 2014/gc_15/sr_9#10 | semantic | skip | practitioner | 29 | 32 | — |
| A/CN.9/SR.902 | 2010/a/cn_9/sr_902#16 | skip | practitioner | lookup | 28 | — | — |
| S/2009/658 | 2009/s/2009/658#0 | lookup | practitioner | lookup | 34 | 27 | 32 |
| A/C.5/56/46 | 2002/a/c_5/56/46#12 | lookup | practitioner | lookup | 32 | 31 | 31 |
| S/2006/724 | 2006/s/2006/724#6 | lookup | practitioner | lookup, semantic | 28 | 27 | 28 |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 50 | 0 | 246346 | 2542 | 0.01 | 0 |
| generation | gpt-5.6-luna | 150 | 0 | 1226677 | 204555 | 0 | 150 |
| decider | gpt-5.6-luna | 50 | 0 | 196859 | 14617 | 0 | 50 |
| faithfulness | anthropic/claude-sonnet-5.5 | 170 | 0 | 1383653 | 94783 | 3.72 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 129 | 0 | 1203411 | 206644 | 4.47 | 0 |
| faithfulness_repair | anthropic/claude-sonnet-5.5 | 16 | 0 | 135345 | 5014 | 0.32 | 0 |

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
