# 5-verifier comparison

440 unchanged questions from 50 documents. Each verifier assessed both faithfulness and mode-specific quality. Generation and decider choices are fixed. The original 10 generation skips are represented explicitly in the exports, with blank grade cells.

Statistics average all candidates, paired by candidate ID; they are not best-per-document averages. A numeric total /40 is faithfulness /15 plus quality /25. Audit pass means clear or minor issues. A high score does not override a failed audit check.

| verifier | scored | mean_faithfulness_15 | mean_quality_25 | mean_total_40 | perfect_40 | audit_pass | audit_pass_percent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| verifier 1 | 440 | 14.54 | 21.57 | 36.11 | 63 | 317 | 72.05 |
| verifier 2 | 440 | 14.82 | 24.59 | 39.41 | 334 | 312 | 70.91 |
| verifier 3 | 440 | 14.53 | 22.84 | 37.37 | 111 | 305 | 69.32 |
| verifier 4 | 440 | 14.77 | 23.11 | 37.88 | 240 | 332 | 75.45 |
| verifier 5 | 440 | 14.91 | 24.62 | 39.54 | 346 | 408 | 92.73 |

## Audit outcomes

| verifier | clear | minor_issues | repair | blocking | review |
| --- | --- | --- | --- | --- | --- |
| verifier 1 | 278 | 39 | 48 | 75 | 0 |
| verifier 2 | 309 | 3 | 63 | 64 | 1 |
| verifier 3 | 241 | 64 | 77 | 45 | 13 |
| verifier 4 | 327 | 5 | 46 | 62 | 0 |
| verifier 5 | 395 | 13 | 14 | 17 | 1 |

## Changes relative to verifier 1

| verifier | paired_candidates | mean_delta_vs_verifier_1 | higher | lower | equal |
| --- | --- | --- | --- | --- | --- |
| verifier 1 | 440 | 0.00 | 0 | 0 | 440 |
| verifier 2 | 440 | 3.30 | 359 | 15 | 66 |
| verifier 3 | 440 | 1.26 | 263 | 101 | 76 |
| verifier 4 | 440 | 1.76 | 290 | 57 | 93 |
| verifier 5 | 440 | 3.42 | 368 | 8 | 64 |

## Per-mode candidate averages

| verifier | corpus | mode | candidates | mean_total_40 | audit_pass | audit_pass_percent |
| --- | --- | --- | --- | --- | --- | --- |
| verifier 1 | un | lookup | 58 | 36.55 | 41 | 70.69 |
| verifier 1 | un | practitioner | 55 | 34.38 | 29 | 52.73 |
| verifier 1 | un | conceptual | 41 | 36.98 | 25 | 60.98 |
| verifier 1 | un | comparison | 24 | 33.58 | 16 | 66.67 |
| verifier 1 | un | claim_verification | 37 | 36.22 | 27 | 72.97 |
| verifier 1 | un | source_finding | 27 | 37.81 | 23 | 85.19 |
| verifier 1 | eurlex | lookup | 50 | 37.92 | 42 | 84.00 |
| verifier 1 | eurlex | fact_pattern | 43 | 34.12 | 24 | 55.81 |
| verifier 1 | eurlex | conceptual | 29 | 35.62 | 22 | 75.86 |
| verifier 1 | eurlex | comparison | 24 | 36.21 | 18 | 75.00 |
| verifier 1 | eurlex | claim_verification | 28 | 36.39 | 26 | 92.86 |
| verifier 1 | eurlex | source_finding | 24 | 37.96 | 24 | 100.00 |
| verifier 2 | un | lookup | 58 | 39.48 | 46 | 79.31 |
| verifier 2 | un | practitioner | 55 | 39.11 | 38 | 69.09 |
| verifier 2 | un | conceptual | 41 | 39.44 | 28 | 68.29 |
| verifier 2 | un | comparison | 24 | 39.42 | 22 | 91.67 |
| verifier 2 | un | claim_verification | 37 | 39.49 | 32 | 86.49 |
| verifier 2 | un | source_finding | 27 | 39.70 | 24 | 88.89 |
| verifier 2 | eurlex | lookup | 50 | 39.50 | 2 | 4.00 |
| verifier 2 | eurlex | fact_pattern | 43 | 39.23 | 32 | 74.42 |
| verifier 2 | eurlex | conceptual | 29 | 39.34 | 23 | 79.31 |
| verifier 2 | eurlex | comparison | 24 | 39.29 | 18 | 75.00 |
| verifier 2 | eurlex | claim_verification | 28 | 39.39 | 25 | 89.29 |
| verifier 2 | eurlex | source_finding | 24 | 39.75 | 22 | 91.67 |
| verifier 3 | un | lookup | 58 | 37.91 | 43 | 74.14 |
| verifier 3 | un | practitioner | 55 | 35.80 | 37 | 67.27 |
| verifier 3 | un | conceptual | 41 | 37.29 | 26 | 63.41 |
| verifier 3 | un | comparison | 24 | 36.12 | 18 | 75.00 |
| verifier 3 | un | claim_verification | 37 | 37.76 | 27 | 72.97 |
| verifier 3 | un | source_finding | 27 | 38.56 | 23 | 85.19 |
| verifier 3 | eurlex | lookup | 50 | 38.50 | 15 | 30.00 |
| verifier 3 | eurlex | fact_pattern | 43 | 36.53 | 32 | 74.42 |
| verifier 3 | eurlex | conceptual | 29 | 37.38 | 21 | 72.41 |
| verifier 3 | eurlex | comparison | 24 | 36.67 | 15 | 62.50 |
| verifier 3 | eurlex | claim_verification | 28 | 37.54 | 25 | 89.29 |
| verifier 3 | eurlex | source_finding | 24 | 38.75 | 23 | 95.83 |
| verifier 4 | un | lookup | 58 | 37.64 | 44 | 75.86 |
| verifier 4 | un | practitioner | 55 | 36.82 | 37 | 67.27 |
| verifier 4 | un | conceptual | 41 | 37.76 | 27 | 65.85 |
| verifier 4 | un | comparison | 24 | 38.38 | 19 | 79.17 |
| verifier 4 | un | claim_verification | 37 | 38.84 | 28 | 75.68 |
| verifier 4 | un | source_finding | 27 | 39.48 | 24 | 88.89 |
| verifier 4 | eurlex | lookup | 50 | 37.96 | 41 | 82.00 |
| verifier 4 | eurlex | fact_pattern | 43 | 35.26 | 24 | 55.81 |
| verifier 4 | eurlex | conceptual | 29 | 38.03 | 20 | 68.97 |
| verifier 4 | eurlex | comparison | 24 | 38.83 | 18 | 75.00 |
| verifier 4 | eurlex | claim_verification | 28 | 38.50 | 26 | 92.86 |
| verifier 4 | eurlex | source_finding | 24 | 39.92 | 24 | 100.00 |
| verifier 5 | un | lookup | 58 | 39.59 | 54 | 93.10 |
| verifier 5 | un | practitioner | 55 | 39.02 | 47 | 85.45 |
| verifier 5 | un | conceptual | 41 | 39.49 | 38 | 92.68 |
| verifier 5 | un | comparison | 24 | 39.58 | 23 | 95.83 |
| verifier 5 | un | claim_verification | 37 | 39.70 | 35 | 94.59 |
| verifier 5 | un | source_finding | 27 | 39.81 | 26 | 96.30 |
| verifier 5 | eurlex | lookup | 50 | 39.80 | 46 | 92.00 |
| verifier 5 | eurlex | fact_pattern | 43 | 39.19 | 38 | 88.37 |
| verifier 5 | eurlex | conceptual | 29 | 39.62 | 27 | 93.10 |
| verifier 5 | eurlex | comparison | 24 | 39.42 | 22 | 91.67 |
| verifier 5 | eurlex | claim_verification | 28 | 39.71 | 28 | 100.00 |
| verifier 5 | eurlex | source_finding | 24 | 39.96 | 24 | 100.00 |

## Files

- [All five grades per question](all_verifier_grades.csv)
- [All modes side by side per document](all_modes_per_document.csv)
- [Overall statistics](overall_statistics.csv)
- [Per-mode statistics](mode_statistics.csv)
