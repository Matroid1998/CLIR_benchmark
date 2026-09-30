# Decider screening

Run status: **completed**. Seed 20260929; 0 UN documents and 50 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider: lookup/practitioner/semantic for UN and fact_pattern/lookup for EUR-Lex. Legacy technical/descriptive modes are outside this comparison. In this historical run, meeting records permit only semantic or skip; lookup/practitioner trials are diagnostic and cannot win.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 1; successfully repaired: 1. Repairs reuse generation and successful verifier stages. The faithfulness retry adds only an explicit actual-batch-size instruction to avoid fabricated extra grade objects when fewer than three candidates were supplied. The grading rubric is unchanged. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. One quality response omitted positional indices; those were restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| eurlex_all | generator | fact_pattern | 36 | 50 | 72.00 |
| eurlex_all | generator | lookup | 10 | 50 | 20.00 |
| eurlex_all | generator | skip | 4 | 50 | 8.00 |
| eurlex_all | generator | error | 0 | 50 | 0.00 |
| eurlex_all | jev | fact_pattern | 6 | 50 | 12.00 |
| eurlex_all | jev | lookup | 39 | 50 | 78.00 |
| eurlex_all | jev | skip | 5 | 50 | 10.00 |
| eurlex_all | jev | error | 0 | 50 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex_all | fact_pattern | 50 | 44 | 118 | 6 | 33.07 | 13.75 | 19.32 | 16 | 3 | 38 |
| eurlex_all | lookup | 50 | 45 | 132 | 5 | 34.64 | 14.49 | 20.16 | 31 | 1 | 44 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex_all | generator | 46 | 45 | 4 | 22 | 45 | 0 | 0 | 33.67 | 1.58 | 30.30 | 26.84 | 31.72 |
| eurlex_all | jev | 45 | 44 | 5 | 32 | 45 | 1 | 0 | 34.68 | 0.52 | 30.52 | 29.18 | 31.72 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex_all | 50 | 19 | 10 | 20 | 20 | -0.22 | [-1.5, 1.6] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | practitioner_score | semantic_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32009R0663 | http://data.europa.eu/eli/reg/2009/663/art_11/oj | fact_pattern | lookup | fact_pattern | 35 | — | — |
| 32012R1219 | http://data.europa.eu/eli/reg/2012/1219/art_13/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32013R0153 | http://data.europa.eu/eli/reg_del/2013/153/art_18/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32013R1303 | http://data.europa.eu/eli/reg/2013/1303/art_123/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32012R1151 | http://data.europa.eu/eli/reg/2012/1151/art_9/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32013L0059 | http://data.europa.eu/eli/dir/2013/59/art_56/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32013R1315 | http://data.europa.eu/eli/reg/2013/1315/art_46/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32013R0952 | http://data.europa.eu/eli/reg/2013/952/art_6/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32010L0013 | http://data.europa.eu/eli/dir/2010/13/art_13/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32010R0113 | http://data.europa.eu/eli/reg/2010/113/art_6/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32011R1034 | http://data.europa.eu/eli/reg_impl/2011/1034/art_8/oj | fact_pattern | lookup | fact_pattern | 33 | — | — |
| 32014L0104 | http://data.europa.eu/eli/dir/2014/104/art_1/oj | fact_pattern | lookup | lookup | 33 | — | — |
| 32007R1566 | http://data.europa.eu/eli/reg/2007/1566/art_13/oj | fact_pattern | lookup | fact_pattern, lookup | 33 | — | — |
| 32006L0024 | http://data.europa.eu/eli/dir/2006/24/art_15/oj | lookup | skip | lookup | 37 | — | — |
| 32011L0093 | http://data.europa.eu/eli/dir/2011/93/art_25/oj | fact_pattern | lookup | fact_pattern | 33 | — | — |
| 32009R0260 | http://data.europa.eu/eli/reg/2009/260/art_15/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32008L0052 | http://data.europa.eu/eli/dir/2008/52/art_7/oj | fact_pattern | lookup | fact_pattern | 32 | — | — |
| 32010R0583 | http://data.europa.eu/eli/reg/2010/583/art_21/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32007R0951 | http://data.europa.eu/eli/reg/2007/951/art_34/oj | fact_pattern | lookup | fact_pattern | 32 | — | — |
| 32011L0016 | http://data.europa.eu/eli/dir/2011/16/art_13/oj | fact_pattern | lookup | fact_pattern | 34 | — | — |
| 32013R0229 | http://data.europa.eu/eli/reg/2013/229/art_9/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32008R0994 | http://data.europa.eu/eli/reg/2008/994/art_68/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32009R1121 | http://data.europa.eu/eli/reg/2009/1121/art_69/oj | fact_pattern | lookup | fact_pattern | 34 | — | — |
| 32008R0215 | http://data.europa.eu/eli/reg/2008/215/art_27/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32014L0053 | http://data.europa.eu/eli/dir/2014/53/art_3/oj | fact_pattern | lookup | fact_pattern | 31 | — | — |
| 32013R0131 | http://data.europa.eu/eli/reg_impl/2013/131/art_4/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32008L0056 | http://data.europa.eu/eli/dir/2008/56/art_4/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32008L0098 | http://data.europa.eu/eli/dir/2008/98/art_5/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32008R0303 | http://data.europa.eu/eli/reg/2008/303/art_12/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32010L0044 | http://data.europa.eu/eli/dir/2010/44/art_30/oj | fact_pattern | lookup | fact_pattern | 31 | — | — |
| 32014R0809 | http://data.europa.eu/eli/reg_impl/2014/809/art_12/oj | fact_pattern | lookup | lookup | 36 | — | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 50 | 0 | 98922 | 1956 | 0.00 | 0 |
| decider | gpt-5.6-luna | 50 | 0 | 60360 | 4977 | 0 | 50 |
| generation | gpt-5.6-luna | 100 | 0 | 683520 | 116407 | 0 | 100 |
| faithfulness | anthropic/claude-sonnet-5.5 | 95 | 0 | 414862 | 37366 | 1.20 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 98 | 0 | 473598 | 133773 | 2.28 | 0 |

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
