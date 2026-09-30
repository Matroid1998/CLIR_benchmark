# Decider screening

Run status: **completed**. Seed 20260929; 0 UN documents and 50 EUR-Lex acts, one English target per document/act. Generator/standard decider: `gpt-5.6-luna`. Verifier: `anthropic/claude-sonnet-5.5`. Jev: `~typesafe/jev-latest`.

## Design and interpretation

The sample is deterministic and stratified, not a representative corpus-frequency estimate. UN sampling uses the existing 50% resolution, 40% meeting, 10% letter mix, full-context-fit and reference-completeness filters. The complete assembled payload is identical across both deciders and every generation mode. Each mode gets one generation batch (up to three candidates), followed by the existing faithfulness and mode-specific quality verifiers. Generation does not see either decider’s answer.

“All modes” means the modes offered to the decider: lookup/practitioner/semantic for UN and fact_pattern/lookup for EUR-Lex. Legacy technical/descriptive modes are outside this comparison. Meeting records are eligible only for semantic or skip; lookup/practitioner runs on them are diagnostic restriction checks and cannot win. Semantic remains eligible on other UN documents.

Scores use the pipeline sum: faithfulness /15 plus mode-specific quality /25 = /40. For UN, the best candidate must also have grounding ≥3. “Oracle” means the best observed eligible mode in this single run, retaining ties—not human-labeled ground truth. Different quality rubrics assess different properties, so score comparisons are screening evidence. A second sensitivity analysis requires a clear/minor-issues audit; repair, review and blocking candidates are excluded there.

Coverage-adjusted utility assigns 0 to skip or a mode with no qualifying candidate; 0 is an analysis convention, not an LLM grade. Provider/parse failures and incomplete eligible-mode comparisons are excluded from policy utility. “Missed opportunity” means a decider skipped despite another mode producing a scored candidate, not proof the skip was wrong. No accuracy claim or optimal-skip threshold is possible without human labels. Bootstrap intervals resample these targets and do not capture model rerun variability.

Original failed tasks: 2; successfully repaired: 2. Repairs reuse generation and successful verifier stages. The faithfulness retry adds only an explicit actual-batch-size instruction to avoid fabricated extra grade objects when fewer than three candidates were supplied. The grading rubric is unchanged. Original calls remain in `run.sqlite`; repair calls and provenance are in [grade_repairs/trace.md](grade_repairs/trace.md). Where surrounding prose prevented parsing, an unambiguous grade array was recovered only after validating the exact count, indices, score ranges, and required fields; no extra grade objects were silently discarded. One quality response omitted positional indices; those were restored from exact, unique candidate IDs in the recorded input, followed by full schema validation. The earliest valid recorded response was used, without changing its scores. Candidate counts vary by mode, so best-of-batch scores reflect the pipeline outcome rather than an isolated causal effect of framing.

## Mode distributions

| subset | backend | mode | count | n | percent |
| --- | --- | --- | --- | --- | --- |
| eurlex_all | generator | fact_pattern | 35 | 50 | 70.00 |
| eurlex_all | generator | lookup | 10 | 50 | 20.00 |
| eurlex_all | generator | skip | 5 | 50 | 10.00 |
| eurlex_all | generator | error | 0 | 50 | 0.00 |
| eurlex_all | jev | fact_pattern | 3 | 50 | 6.00 |
| eurlex_all | jev | lookup | 42 | 50 | 84.00 |
| eurlex_all | jev | skip | 5 | 50 | 10.00 |
| eurlex_all | jev | error | 0 | 50 | 0.00 |

![Mode distribution](mode_distribution.png)

## All-mode score comparison

| subset | mode | eligible | scored | generated_candidates | no_candidates | mean_best_score | mean_best_faithfulness | mean_best_quality | oracle_wins_including_ties | best_candidate_blocking | audit_clear_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex_all | fact_pattern | 50 | 43 | 115 | 7 | 32.98 | 13.74 | 19.23 | 12 | 2 | 38 |
| eurlex_all | lookup | 50 | 44 | 127 | 6 | 35.02 | 14.57 | 20.45 | 38 | 1 | 43 |

![Mode scores](mode_scores.png)

## Decider performance against observed scores

| subset | backend | routed | scored_selected | skipped | matches_oracle | oracle_available | missed_score_opportunities | selected_mode_unproductive_despite_alternative | mean_selected_score_when_available | mean_regret_when_scored | mean_utility_zero_for_skip_or_no_candidate | mean_audit_clear_utility | mean_oracle_utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex_all | generator | 45 | 43 | 5 | 17 | 45 | 1 | 1 | 33.47 | 1.84 | 28.78 | 26.26 | 31.66 |
| eurlex_all | jev | 45 | 43 | 5 | 39 | 45 | 1 | 1 | 35.05 | 0.26 | 30.14 | 29.42 | 31.66 |

## Paired Jev versus standard-decider comparison

| subset | valid_pairs | agree | generator_better_utility | jev_better_utility | utility_ties | mean_paired_utility_difference_generator_minus_jev | bootstrap_95_interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex_all | 50 | 18 | 4 | 26 | 20 | -1.36 | [-2, -0.72] |

## Disagreements for manual review

| symbol | target_id | generator_mode | jev_mode | oracle_modes | lookup_score | practitioner_score | semantic_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32009R0663 | http://data.europa.eu/eli/reg/2009/663/art_11/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32012R1219 | http://data.europa.eu/eli/reg/2012/1219/art_13/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32009R0470 | http://data.europa.eu/eli/reg/2009/470/art_5/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32013R0153 | http://data.europa.eu/eli/reg_del/2013/153/art_18/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32013R1303 | http://data.europa.eu/eli/reg/2013/1303/art_123/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32012R1151 | http://data.europa.eu/eli/reg/2012/1151/art_9/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32013L0059 | http://data.europa.eu/eli/dir/2013/59/art_56/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32013R1315 | http://data.europa.eu/eli/reg/2013/1315/art_46/oj | fact_pattern | lookup | fact_pattern, lookup | 34 | — | — |
| 32013R0952 | http://data.europa.eu/eli/reg/2013/952/art_6/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32010L0013 | http://data.europa.eu/eli/dir/2010/13/art_13/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32010R0113 | http://data.europa.eu/eli/reg/2010/113/art_6/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32011R1034 | http://data.europa.eu/eli/reg_impl/2011/1034/art_8/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32014L0104 | http://data.europa.eu/eli/dir/2014/104/art_1/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32009L0071 | http://data.europa.eu/eli/dir/2009/71/art_4/oj | fact_pattern | lookup | lookup | 33 | — | — |
| 32011L0093 | http://data.europa.eu/eli/dir/2011/93/art_25/oj | fact_pattern | lookup | fact_pattern | 33 | — | — |
| 32009R0260 | http://data.europa.eu/eli/reg/2009/260/art_15/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32008L0052 | http://data.europa.eu/eli/dir/2008/52/art_7/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32010R0583 | http://data.europa.eu/eli/reg/2010/583/art_21/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32007R0951 | http://data.europa.eu/eli/reg/2007/951/art_34/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32011L0016 | http://data.europa.eu/eli/dir/2011/16/art_13/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32013R0229 | http://data.europa.eu/eli/reg/2013/229/art_9/oj | fact_pattern | lookup | lookup | 38 | — | — |
| 32010L0065 | http://data.europa.eu/eli/dir/2010/65/art_4/oj | fact_pattern | lookup | lookup | 35 | — | — |
| 32008R0994 | http://data.europa.eu/eli/reg/2008/994/art_68/oj | fact_pattern | lookup | lookup | 31 | — | — |
| 32009R1121 | http://data.europa.eu/eli/reg/2009/1121/art_69/oj | fact_pattern | lookup | lookup | 37 | — | — |
| 32014R0508 | http://data.europa.eu/eli/reg/2014/508/art_42/oj | fact_pattern | lookup | fact_pattern, lookup | 36 | — | — |
| 32008R0215 | http://data.europa.eu/eli/reg/2008/215/art_27/oj | fact_pattern | lookup | fact_pattern | 34 | — | — |
| 32014L0053 | http://data.europa.eu/eli/dir/2014/53/art_3/oj | fact_pattern | lookup | fact_pattern | 30 | — | — |
| 32013R0131 | http://data.europa.eu/eli/reg_impl/2013/131/art_4/oj | fact_pattern | lookup | lookup | 36 | — | — |
| 32008L0056 | http://data.europa.eu/eli/dir/2008/56/art_4/oj | fact_pattern | lookup | lookup | 34 | — | — |
| 32008L0098 | http://data.europa.eu/eli/dir/2008/98/art_5/oj | fact_pattern | lookup | lookup | 33 | — | — |
| 32011R0543 | http://data.europa.eu/eli/reg_impl/2011/543/art_17/oj | fact_pattern | lookup | fact_pattern | 35 | — | — |
| 32014R0809 | http://data.europa.eu/eli/reg_impl/2014/809/art_12/oj | fact_pattern | lookup | lookup | 35 | — | — |

## Recorded usage

| stage | model | calls | provider_errors | prompt_tokens | completion_tokens | reported_cost | calls_missing_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| decider | ~typesafe/jev-latest | 50 | 0 | 83922 | 1953 | 0.00 | 0 |
| decider | gpt-5.6-luna | 50 | 0 | 60360 | 4761 | 0 | 50 |
| generation | gpt-5.6-luna | 100 | 0 | 683520 | 114472 | 0 | 100 |
| faithfulness | anthropic/claude-sonnet-5.5 | 93 | 0 | 411558 | 36630 | 1.19 | 0 |
| quality | anthropic/claude-sonnet-5.5 | 97 | 0 | 470648 | 141612 | 2.36 | 0 |
| faithfulness_repair | anthropic/claude-sonnet-5.5 | 1 | 0 | 3869 | 217 | 0.01 | 0 |

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
