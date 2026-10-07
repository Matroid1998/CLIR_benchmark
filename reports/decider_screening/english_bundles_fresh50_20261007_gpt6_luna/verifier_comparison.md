# GPT-6 Luna verifier comparison

All 440 candidates from the same 25 UN and 25 EUR-Lex documents were regraded. No questions or decider choices were regenerated. The exact original system/user verifier messages were reused. All 290 faithfulness and 290 quality calls completed successfully; the 10 original generation skips remain unchanged.

Previous verifier: `anthropic/claude-sonnet-5.5`, with the original thinking settings. New verifier: `gpt-6-luna`, with medium reasoning effort. This compares verifier judgments on fixed candidates; it does not establish which judge is correct.

## Candidate-level scores

These means include every generated candidate, paired by candidate ID. They differ from the best-candidate-per-document means in the screening report. Total = faithfulness /15 + quality /25.

| Metric | Claude Sonnet 5.5 | GPT-6 Luna |
| --- | ---: | ---: |
| Faithfulness /15 | 14.54 | 14.82 |
| Quality /25 | 21.57 | 24.59 |
| Total /40 | 36.11 | 39.41 |

| Corpus | Mode | Candidates | Claude /40 | GPT-6 Luna /40 | Difference |
| --- | --- | ---: | ---: | ---: | ---: |
| eurlex | claim_verification | 28 | 36.39 | 39.39 | +3.00 |
| eurlex | comparison | 24 | 36.21 | 39.29 | +3.08 |
| eurlex | conceptual | 29 | 35.62 | 39.34 | +3.72 |
| eurlex | fact_pattern | 43 | 34.12 | 39.23 | +5.12 |
| eurlex | lookup | 50 | 37.92 | 39.50 | +1.58 |
| eurlex | source_finding | 24 | 37.96 | 39.75 | +1.79 |
| un | claim_verification | 37 | 36.22 | 39.49 | +3.27 |
| un | comparison | 24 | 33.58 | 39.42 | +5.83 |
| un | conceptual | 41 | 36.98 | 39.44 | +2.46 |
| un | lookup | 58 | 36.55 | 39.48 | +2.93 |
| un | practitioner | 55 | 34.38 | 39.11 | +4.73 |
| un | source_finding | 27 | 37.81 | 39.70 | +1.89 |

GPT-6 Luna scored 359 candidates higher, 15 lower, and 66 the same. It awarded 40/40 to 334 candidates (75.9%).

## Audit outcomes

Numeric scores and audit checks are separate. A high numeric grade does not override a failed mode/support/metadata check.

| Audit | Claude | GPT-6 Luna |
| --- | ---: | ---: |
| clear | 278 | 309 |
| minor_issues | 39 | 3 |
| repair | 48 | 63 |
| blocking | 75 | 64 |
| review | 0 | 1 |

Clear/minor-issues candidates: Claude 317/440 (72.0%); GPT-6 Luna 312/440 (70.9%). In EUR-Lex lookup, GPT-6 Luna marked 43/50 candidates for metadata repair, 5 blocking, and 2 clear. Recorded problems frequently identify empty-string instrument_short_name values where null or a supported name is required; some also identify anchors absent from the questions. These are findings on the unchanged recorded inputs, not changes introduced by this regrade.

## Files

- [All modes and grades, one row per document](all_modes_per_document_with_jev_and_grades.csv)
- [Question-by-question verifier comparison](verifier_candidate_comparison.csv)
- [Per-mode candidate averages](verifier_mode_comparison.csv)
- [Full screening statistics with the new grades](analysis.md)
- [Export and request verification](export_validation.json)
