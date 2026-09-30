# Fresh 100-document screening with decider examples

50 EUR-Lex articles and 50 UN passages; prior screening documents and identified example acts are excluded. Each decider receives the same five examples for its corpus. Generator and standard decider: gpt-5.6-luna; grader: anthropic/claude-sonnet-5.5; Jev: ~typesafe/jev-latest.

Scores are the best qualifying candidate in the selected mode, out of 40. Skips and missing qualifying candidates are excluded from averages and score losses, never assigned zero. Best-mode match rates use scored selections only and retain ties. All modes are eligible on UN meeting records. This new sample cannot isolate the effect of prompt changes.

## Selected-mode scores

| subset | decider | scored_selected | mean_selected_score_out_of_40 | mean_gap_to_best_mode_when_scored | best_mode_match_percent_among_scored | abstentions | no_qualifying_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex | jev | 39 | 35.44 | 0.05 | 94.87 | 10 | 1 |
| eurlex | generator | 38 | 33.05 | 2.39 | 21.05 | 11 | 1 |
| un_all | jev | 38 | 30.45 | 1.00 | 68.42 | 9 | 3 |
| un_all | generator | 45 | 29.84 | 1.44 | 60.00 | 0 | 5 |
| un_without_meetings | jev | 23 | 30.17 | 1.30 | 56.52 | 5 | 2 |
| un_without_meetings | generator | 26 | 30.69 | 0.81 | 73.08 | 0 | 4 |
| un_meetings_only | jev | 15 | 30.87 | 0.53 | 86.67 | 4 | 1 |
| un_meetings_only | generator | 19 | 28.68 | 2.32 | 42.11 | 0 | 1 |

## Comparison on the same scored documents

| subset | paired_scored_documents | jev_mean | gpt_mean | jev_minus_gpt | jev_higher | gpt_higher | tied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eurlex | 38 | 35.39 | 33.05 | 2.34 | 30 | 2 | 6 |
| un_all | 38 | 30.45 | 30.11 | 0.34 | 8 | 3 | 27 |
| un_without_meetings | 23 | 30.17 | 30.57 | -0.39 | 1 | 3 | 19 |
| un_meetings_only | 15 | 30.87 | 29.40 | 1.47 | 7 | 0 | 8 |

## Mode distributions

| subset | decider | mode | count | percent |
| --- | --- | --- | --- | --- |
| eurlex | jev | fact_pattern | 0 | 0.00 |
| eurlex | jev | lookup | 40 | 80.00 |
| eurlex | jev | skip | 10 | 20.00 |
| eurlex | generator | fact_pattern | 37 | 74.00 |
| eurlex | generator | lookup | 2 | 4.00 |
| eurlex | generator | skip | 11 | 22.00 |
| un_all | jev | lookup | 18 | 36.00 |
| un_all | jev | practitioner | 6 | 12.00 |
| un_all | jev | semantic | 17 | 34.00 |
| un_all | jev | skip | 9 | 18.00 |
| un_all | generator | lookup | 21 | 42.00 |
| un_all | generator | practitioner | 5 | 10.00 |
| un_all | generator | semantic | 24 | 48.00 |
| un_all | generator | skip | 0 | 0.00 |
| un_without_meetings | jev | lookup | 13 | 43.33 |
| un_without_meetings | jev | practitioner | 5 | 16.67 |
| un_without_meetings | jev | semantic | 7 | 23.33 |
| un_without_meetings | jev | skip | 5 | 16.67 |
| un_without_meetings | generator | lookup | 8 | 26.67 |
| un_without_meetings | generator | practitioner | 5 | 16.67 |
| un_without_meetings | generator | semantic | 17 | 56.67 |
| un_without_meetings | generator | skip | 0 | 0.00 |
| un_meetings_only | jev | lookup | 5 | 25.00 |
| un_meetings_only | jev | practitioner | 1 | 5.00 |
| un_meetings_only | jev | semantic | 10 | 50.00 |
| un_meetings_only | jev | skip | 4 | 20.00 |
| un_meetings_only | generator | lookup | 13 | 65.00 |
| un_meetings_only | generator | practitioner | 0 | 0.00 |
| un_meetings_only | generator | semantic | 7 | 35.00 |
| un_meetings_only | generator | skip | 0 | 0.00 |

## Scores by generation mode

These conditional means can cover different documents; they are not paired comparisons.

| subset | mode | scored_documents | mean_best_score_out_of_40 |
| --- | --- | --- | --- |
| eurlex | fact_pattern | 37 | 32.95 |
| eurlex | lookup | 39 | 35.44 |
| un_all | lookup | 39 | 29.36 |
| un_all | practitioner | 35 | 29.09 |
| un_all | semantic | 44 | 30.77 |
| un_without_meetings | lookup | 20 | 30.40 |
| un_without_meetings | practitioner | 20 | 29.55 |
| un_without_meetings | semantic | 25 | 31.08 |
| un_meetings_only | lookup | 19 | 28.26 |
| un_meetings_only | practitioner | 15 | 28.47 |
| un_meetings_only | semantic | 19 | 30.37 |

## Files

[Full document/question/grade CSV](documents_decisions_questions_grades.csv), [score summary](score_only_summary.csv), [paired scores](paired_decider_scores.csv), [abstentions and missing scores](abstentions_and_missing_scores.csv), [Jev responses](jev_responses.json), [validation](validation.json).
