# Source-only Jev quality routing optimized for best score above 31

The retained prompt independently predicts whether each mode can produce a best question scoring at least 32/40 under the current Gemini legal-clir-exceptional-r3 rubric. The default acceptance rule is Jev yes probability >=0.55. It runs before generation and sees the original source packet only.

Four prompt variants were tested on 30 development documents(15 per corpus). The selected variant and probability cutoff were frozen before running 20 validation documents(10 per corpus). No questions or verifier grades were regenerated. The latest prompts and routing policy were registered and activated in local MLflow as decider-score32-optimized-20261007; prompt history remains local.

## Validation comparison

| rule | tp | fp | fn | tn | rejection_rate_low | retention_rate_high | precision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| original_0.5 | 53 | 49 | 7 | 11 | 0.18 | 0.88 | 0.52 |
| original_tuned_0.87 | 26 | 18 | 34 | 42 | 0.70 | 0.43 | 0.59 |
| optimized_0.55 | 30 | 18 | 30 | 42 | 0.70 | 0.50 | 0.62 |

The optimized rule rejected 42/60 low-score-or-skip modes (70%) and retained 30/60 high-score modes (50%) on validation. It still accepted 18 low-score modes and rejected 30 high-score modes. The original tuned rule also rejected 42 low modes, but retained 26 high modes. Most of the increased rejection versus the original default comes from using a stricter decision policy; the changed prompt adds four retained high-score validation modes at matched low-score rejection.

## Full 50-document comparison

| rule | accepted | rejected | tp | fp | fn | tn | rejection_rate_low | retention_rate_high | precision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original_0.5 | 271 | 29 | 147 | 124 | 10 | 19 | 0.13 | 0.94 | 0.54 |
| original_tuned_0.87 | 130 | 170 | 75 | 55 | 82 | 88 | 0.62 | 0.48 | 0.58 |
| optimized_0.55 | 128 | 172 | 77 | 51 | 80 | 92 | 0.64 | 0.49 | 0.60 |

Across 300 document-mode pairs, the optimized rule accepted 128 and rejected 172:77 accepted modes scored above 31,51 accepted modes did not,80 high-score modes were rejected, and 92 low-score-or-skip modes were rejected. Of 143 negative references,133 have questions scoring 31 or below and 10 are generation skips. Numeric score and audit validity remain separate.

## Interpretation and reproducibility

This is a source-only prediction, not an exact guarantee about realized generator wording. The labels are maxima of the saved questions, not proof that the source could never produce a better question. Scores near 31/32 are especially sensitive to anchoring, natural persona framing and paraphrasing. Small differences appeared when the final development cases were replayed: initial selected development high-score retention was 49/97; final replay was 47/97. The probability cutoff remained frozen at 0.55. Validation results were not used to select or retune it.

The local routing_policy is removed before calling the native Jev API. Older bundles without that policy retain a 0.5 default, and an explicit --threshold overrides the pinned cutoff. The historical single-choice router remains available; these changes concern the independent six-mode Jev screen.

## Files

- [Source-only decisions, one row per document](decisions_only.csv)
- [Each mode, predicted decision, and best observed score](cutoff_comparison.csv)
- [All questions, grades, explanations and new cutoff decisions](questions_with_cutoff_decisions.csv)
- [Aggregate comparison](optimization_comparison.csv)
- [Prediction errors with original questions and reasons](cutoff_error_questions.csv)
- [Development-only variant results](development_variants.csv)
