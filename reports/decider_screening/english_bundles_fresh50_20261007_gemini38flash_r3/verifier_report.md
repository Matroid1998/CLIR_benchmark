# Updated verifier rubric: same 50 documents and 440 questions

Only verifier 4 was rerun, using legal-clir-exceptional-r3. All question text, answers, source packets and decider outputs were preserved. The 10 generation skips retain blank grades. The new rubric was registered in local MLflow and activated before grading.

## Interpreting the scores

The scoring standard changed: 4 can mean fully correct, while 5 requires exceptional evidence. Numerical fidelity uses 4 as a compatibility value when inapplicable. Old and new totals share a /40 range but their difference does not measure a change in question quality. Audit pass means clear or minor issues; numeric scores do not override failed audit checks.

## Overall scores and audit outcomes

| rubric | scored | mean_faithfulness_15 | mean_quality_25 | mean_total_40 | perfect_40 | audit_pass | audit_pass_percent | clear | minor_issues | repair | blocking | review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| previous | 440 | 14.77 | 23.11 | 37.88 | 240 | 332 | 75.45 | 327 | 5 | 46 | 62 | 0 |
| legal-clir-exceptional-r3 | 440 | 11.92 | 18.48 | 30.40 | 0 | 304 | 69.09 | 303 | 1 | 43 | 92 | 1 |

## New scores by corpus and mode

| corpus | mode | candidates | mean_total_40 | audit_pass | audit_pass_percent |
| --- | --- | --- | --- | --- | --- |
| un | all | 242 | 30.34 | 165 | 68.18 |
| eurlex | all | 198 | 30.48 | 139 | 70.20 |
| eurlex | claim_verification | 28 | 29.61 | 18 | 64.29 |
| un | practitioner | 55 | 29.55 | 33 | 60.00 |
| un | lookup | 58 | 30.47 | 43 | 74.14 |
| un | source_finding | 27 | 31.33 | 25 | 92.59 |
| un | claim_verification | 37 | 30.65 | 24 | 64.86 |
| un | conceptual | 41 | 30.61 | 27 | 65.85 |
| un | comparison | 24 | 29.79 | 13 | 54.17 |
| eurlex | lookup | 50 | 31.14 | 42 | 84.00 |
| eurlex | conceptual | 29 | 30.97 | 23 | 79.31 |
| eurlex | comparison | 24 | 31.54 | 17 | 70.83 |
| eurlex | source_finding | 24 | 31.38 | 24 | 100.00 |
| eurlex | fact_pattern | 43 | 28.86 | 15 | 34.88 |

## Existing independent Jev decisions against the updated grades

Jev was not rerun. Its 0.5 cutoff still selects 271 of 300 modes. Observed passing modes have at least one audit-passing candidate, with grounding >=3 additionally required for UN. These are model judgments, not human ground truth; no passing candidate does not prove a mode impossible.

| rubric | yes | observed_passing_modes | tp | fp | fn | tn | precision | recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| previous | 271 | 243 | 230 | 41 | 13 | 16 | 0.85 | 0.95 |
| new | 271 | 221 | 210 | 61 | 11 | 18 | 0.77 | 0.95 |

Required exceptional-score rationale markers missing: 0. Grades were not silently changed.

## Files

- [New grades and reasons, document text, questions, and saved Jev decisions](verifier_grades.csv)
- [Detailed statistics](verifier_statistics.csv)
- [Per-question previous/new grade comparison](verifier_candidate_comparison.csv)
- [Jev versus old/new grades for each mode](jev_vs_new_verifier.csv)
