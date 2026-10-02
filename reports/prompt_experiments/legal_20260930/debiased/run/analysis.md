# Decider screening

Run status: **completed**. Seed 20260930; 50 UN documents and 50 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider: lookup/practitioner/semantic for UN and fact_pattern/lookup for EUR-Lex. Legacy technical/descriptive modes are outside this comparison. All three modes are eligible on UN meeting records, as on other UN documents.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 13; successfully repaired: 13. Repairs reuse generation and successful verifier stages. The faithfulness retry adds only an explicit actual-batch-size instruction to avoid fabricated extra grade objects when fewer than three candidates were supplied. The grading rubric is unchanged. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. One quality response omitted positional indices; those were restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| un_all | generator | lookup | 22 | 50 | 44.00 |
| un_all | generator | practitioner | 25 | 50 | 50.00 |
| un_all | generator | semantic | 3 | 50 | 6.00 |
| un_all | generator | skip | 0 | 50 | 0.00 |
| un_all | generator | error | 0 | 50 | 0.00 |
| un_all | jev | lookup | 0 | 50 | 0.00 |
| un_all | jev | practitioner | 44 | 50 | 88.00 |
| un_all | jev | semantic | 6 | 50 | 12.00 |
| un_all | jev | skip | 0 | 50 | 0.00 |
| un_all | jev | error | 0 | 50 | 0.00 |
| un_without_meetings | generator | lookup | 15 | 30 | 50.00 |
| un_without_meetings | generator | practitioner | 15 | 30 | 50.00 |
| un_without_meetings | generator | semantic | 0 | 30 | 0.00 |
| un_without_meetings | generator | skip | 0 | 30 | 0.00 |
| un_without_meetings | generator | error | 0 | 30 | 0.00 |
| un_without_meetings | jev | lookup | 0 | 30 | 0.00 |
| un_without_meetings | jev | practitioner | 28 | 30 | 93.33 |
| un_without_meetings | jev | semantic | 2 | 30 | 6.67 |
| un_without_meetings | jev | skip | 0 | 30 | 0.00 |
| un_without_meetings | jev | error | 0 | 30 | 0.00 |
| un_meetings_only | generator | lookup | 7 | 20 | 35.00 |
| un_meetings_only | generator | practitioner | 10 | 20 | 50.00 |
| un_meetings_only | generator | semantic | 3 | 20 | 15.00 |
| un_meetings_only | generator | skip | 0 | 20 | 0.00 |
| un_meetings_only | generator | error | 0 | 20 | 0.00 |
| un_meetings_only | jev | lookup | 0 | 20 | 0.00 |
| un_meetings_only | jev | practitioner | 16 | 20 | 80.00 |
| un_meetings_only | jev | semantic | 4 | 20 | 20.00 |
| un_meetings_only | jev | skip | 0 | 20 | 0.00 |
| un_meetings_only | jev | error | 0 | 20 | 0.00 |
| eurlex_all | generator | fact_pattern | 38 | 50 | 76.00 |
| eurlex_all | generator | lookup | 1 | 50 | 2.00 |
| eurlex_all | generator | skip | 11 | 50 | 22.00 |
| eurlex_all | generator | error | 0 | 50 | 0.00 |
| eurlex_all | jev | fact_pattern | 18 | 50 | 36.00 |
| eurlex_all | jev | lookup | 22 | 50 | 44.00 |
| eurlex_all | jev | skip | 10 | 50 | 20.00 |
| eurlex_all | jev | error | 0 | 50 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | lookup | 50 | 50 | 147 | 0 | 34.66 | 14.72 | 19.94 | 28 | 0 | 50 |
| un_all | practitioner | 50 | 50 | 144 | 0 | 32.98 | 14.44 | 18.54 | 12 | 10 | 29 |
| un_all | semantic | 50 | 50 | 140 | 0 | 34.12 | 14.64 | 19.48 | 19 | 4 | 43 |
| un_without_meetings | lookup | 30 | 30 | 88 | 0 | 34.83 | 14.77 | 20.07 | 19 | 0 | 30 |
| un_without_meetings | practitioner | 30 | 30 | 86 | 0 | 33.17 | 14.40 | 18.77 | 9 | 7 | 17 |
| un_without_meetings | semantic | 30 | 30 | 82 | 0 | 34.10 | 14.67 | 19.43 | 10 | 3 | 27 |
| un_meetings_only | lookup | 20 | 20 | 59 | 0 | 34.40 | 14.65 | 19.75 | 9 | 0 | 20 |
| un_meetings_only | practitioner | 20 | 20 | 58 | 0 | 32.70 | 14.50 | 18.20 | 3 | 3 | 12 |
| un_meetings_only | semantic | 20 | 20 | 58 | 0 | 34.15 | 14.60 | 19.55 | 9 | 1 | 16 |
| eurlex_all | fact_pattern | 50 | 38 | 102 | 12 | 35.03 | 14.82 | 20.21 | 11 | 3 | 34 |
| eurlex_all | lookup | 50 | 39 | 115 | 11 | 36.85 | 14.97 | 21.87 | 32 | 1 | 38 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | generator | 50 | 50 | 0 | 24 | 50 | 0 | 0 | 34.02 | 1.54 | 34.02 | 27 | 35.56 |
| un_all | jev | 50 | 50 | 0 | 14 | 50 | 0 | 0 | 33.20 | 2.36 | 33.20 | 19.68 | 35.56 |
| un_without_meetings | generator | 30 | 30 | 0 | 18 | 30 | 0 | 0 | 34.37 | 1.30 | 34.37 | 27.97 | 35.67 |
| un_without_meetings | jev | 30 | 30 | 0 | 9 | 30 | 0 | 0 | 33.27 | 2.40 | 33.27 | 19.50 | 35.67 |
| un_meetings_only | generator | 20 | 20 | 0 | 6 | 20 | 0 | 0 | 33.50 | 1.90 | 33.50 | 25.55 | 35.40 |
| un_meetings_only | jev | 20 | 20 | 0 | 5 | 20 | 0 | 0 | 33.10 | 2.30 | 33.10 | 19.95 | 35.40 |
| eurlex_all | generator | 39 | 38 | 11 | 12 | 39 | 0 | 1 | 35.13 | 2.03 | 26.70 | 24.14 | 28.98 |
| eurlex_all | jev | 40 | 39 | 10 | 17 | 39 | 0 | 0 | 35.74 | 1.41 | 27.88 | 27.28 | 28.98 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| un_all | 50 | 23 | 19 | 4 | 27 | 0.82 | [0.12, 1.5] |
| un_without_meetings | 30 | 15 | 12 | 1 | 17 | 1.10 | [0.3, 1.9333333333333333] |
| un_meetings_only | 20 | 8 | 7 | 3 | 10 | 0.40 | [-0.7, 1.4] |
| eurlex_all | 50 | 29 | 7 | 12 | 31 | -1.18 | [-2.92, -0.1] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | practitioner_score | semantic_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A/RES/65/212 | 2011/a/res/65/212#13 | lookup | practitioner | lookup | 36 | 32 | 34 |
| A/RES/67/199 | 2013/a/res/67/199#12 | lookup | semantic | lookup | 35 | 34 | 34 |
| A/RES/65/263 | 2011/a/res/65/263#2 | lookup | practitioner | lookup, semantic | 32 | 24 | 32 |
| A/RES/68/143 | 2013/a/res/68/143#7 | lookup | practitioner | lookup, practitioner | 35 | 35 | 32 |
| A/RES/60/226 | 2005/a/res/60/226#3 | lookup | practitioner | semantic | 33 | 32 | 36 |
| S/RES/1376(2001) | 2001/s/res/1376_2001_#2 | lookup | practitioner | lookup | 35 | 32 | 34 |
| S/RES/1806(2008) | 2008/s/res/1806_2008_#8 | lookup | practitioner | practitioner | 34 | 39 | 36 |
| S/RES/1845(2008) | 2008/s/res/1845_2008_#3 | lookup | practitioner | lookup | 36 | 35 | 34 |
| A/RES/59/61 | 2004/a/res/59/61#0 | lookup | practitioner | semantic | 30 | 25 | 35 |
| A/RES/67/145 | 2013/a/res/67/145#7 | lookup | semantic | lookup | 38 | 32 | 35 |
| A/RES/58/298 | 2003/a/res/58/298#4 | lookup | practitioner | lookup | 38 | 37 | 35 |
| A/RES/57/300 | 2003/a/res/57/300#10 | lookup | practitioner | lookup | 36 | 33 | 34 |
| A/RES/57/137 | 2003/a/res/57/137#1 | lookup | practitioner | lookup | 36 | 33 | 32 |
| S/RES/2140(2014) | 2014/s/res/2140__2014_#13 | lookup | practitioner | semantic | 34 | 34 | 36 |
| CD/PV.1097 | 2008/cd/pv_1097#14 | semantic | practitioner | semantic | 32 | 30 | 35 |
| A/C.5/60/SR.64 | 2006/a/c_5/60/sr_64#14 | semantic | practitioner | lookup | 36 | 32 | 34 |
| CEDAW/C/SR.451 | 2001/cedaw/c/sr_451#4 | lookup | practitioner | lookup | 38 | 34 | 33 |
| A/AC.109/2008/SR.2 | 2008/a/ac_109/2008/sr_2#1 | lookup | practitioner | semantic | 36 | 33 | 37 |
| CEDAW/C/SR.724 | 2006/cedaw/c/sr_724#18 | lookup | practitioner | lookup | 36 | 33 | 34 |
| CD/PV.983 | 2005/cd/pv_983#13 | lookup | practitioner | semantic | 31 | 31 | 34 |
| A/CN.9/SR.917 | 2010/a/cn_9/sr_917#10 | lookup | semantic | practitioner | 32 | 34 | 31 |
| A/58/PV.1 | 2003/a/58/pv_1#15 | lookup | semantic | semantic | 32 | 32 | 35 |
| A/C.4/57/SR.18 | 2002/a/c_4/57/sr_18#15 | practitioner | semantic | semantic | 33 | 27 | 34 |
| CEDAW/C/SR.778 | 2007/cedaw/c/sr_778#5 | practitioner | semantic | semantic | 35 | 35 | 36 |
| CD/PV.841 | 2000/cd/pv_841#11 | semantic | practitioner | lookup | 36 | 33 | 33 |
| A/AC.109/2009/SR.7 | 2009/a/ac_109/2009/sr_7#4 | lookup | practitioner | lookup | 36 | 35 | 35 |
| S/2004/674 | 2004/s/2004/674#6 | lookup | practitioner | lookup | 36 | 31 | 35 |
| 32014R0910 | http://data.europa.eu/eli/reg/2014/910/art_41/oj | fact_pattern | lookup | fact_pattern | 36 | — | — |
| 32011R1077 | http://data.europa.eu/eli/reg/2011/1077/art_14/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32011R1173 | http://data.europa.eu/eli/reg/2011/1173/art_13/oj | skip | lookup |  | — | — | — |
| 32005R1651 | http://data.europa.eu/eli/reg/2005/1651/art_4/oj | fact_pattern | lookup | fact_pattern | 36 | — | — |
| 32014R0312 | http://data.europa.eu/eli/reg/2014/312/art_16/oj | fact_pattern | lookup | fact_pattern | 35 | — | — |
| 32014R0165 | http://data.europa.eu/eli/reg/2014/165/art_23/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32012R0966 | http://data.europa.eu/eli/reg/2012/966/art_56/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32008R1165 | http://data.europa.eu/eli/reg/2008/1165/art_16/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32014R0912 | http://data.europa.eu/eli/reg/2014/912/art_8/oj | fact_pattern | lookup | fact_pattern, lookup | 34 | — | — |
| 32011R1333 | http://data.europa.eu/eli/reg_impl/2011/1333/art_11/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32012R0282 | http://data.europa.eu/eli/reg_impl/2012/282/art_1/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32014R0788 | http://data.europa.eu/eli/reg/2014/788/art_20/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32011R0333 | http://data.europa.eu/eli/reg/2011/333/art_2/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32013R0811 | http://data.europa.eu/eli/reg_del/2013/811/art_1/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32005R1572 | http://data.europa.eu/eli/reg/2005/1572/art_4/oj | fact_pattern | lookup | fact_pattern | 37 | — | — |
| 32013R1290 | http://data.europa.eu/eli/reg/2013/1290/art_57/oj | fact_pattern | lookup | fact_pattern | 35 | — | — |
| 32013R1381 | http://data.europa.eu/eli/reg/2013/1381/art_5/oj | fact_pattern | lookup | lookup | 39 | — | — |
| 32009R0436 | http://data.europa.eu/eli/reg/2009/436/art_36/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32013R0231 | http://data.europa.eu/eli/reg_del/2013/231/art_43/oj | fact_pattern | lookup | fact_pattern | 33 | — | — |
| 32006R1083 | http://data.europa.eu/eli/reg/2006/1083/art_47/oj | fact_pattern | lookup | fact_pattern | 35 | — | — |
| 32012R0493 | http://data.europa.eu/eli/reg/2012/493/art_3/oj | fact_pattern | lookup | lookup | 38 | — | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 100 | 0 | 376134 | 4594 | 0.02 | 0 |
| decider | gpt-5.6-luna | 100 | 0 | 324418 | 17066 | 0 | 100 |
| generation | gpt-5.6-luna | 250 | 0 | 1445003 | 263152 | 0 | 250 |
| faithfulness | anthropic/claude-sonnet-5.5 | 229 | 0 | 1553200 | 89806 | 4.00 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 276 | 0 | 2305829 | 386422 | 8.48 | 0 |

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
