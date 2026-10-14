# Chemistry prompt evaluation loop

The 2026-10-14 campaign stopped after round 4 at the user's request. All four
independent evaluations are complete. Results and the unmet strict targets are
recorded in `reports/prompt_experiments/chemistry_loop_20261014/final_summary.json`;
`round_metrics.csv` compares the batches. The active r6 prompts match round 4's
frozen snapshot. No fifth round was launched.

Run commands from the repository root with its `.venv`. Model calls use `OPENROUTER_API_KEY` from the environment or `.env`: Jev (`~typesafe/jev-latest`) decides eligibility, Haiku (`anthropic/claude-haiku-5.5`) generates, and Gemini (`google/gemini-3.8-flash`) verifies.

## Run a round

Finish prompt edits before preparing the round. Preparation freezes prompts, sources, model settings, and the fixed independent evaluation contract.

```bash
.venv/bin/python experiments/chemistry_prompt_loop/run_round.py --round 1 --prepare
.venv/bin/python experiments/chemistry_prompt_loop/run_round.py --round 1 --run --workers 5
```

Artifacts are under `reports/prompt_experiments/chemistry_loop_20261014/round_01/`. The runner allows rounds 1–5 and at most 50 distinct source documents per round, including screening failures and skips. The default sample has 10 sources per language (English, French, Spanish, Chinese, German), excludes prior reviewed publications and earlier round samples, and never tops up rejected documents. Each eligible source can produce up to three questions. All canonical candidates are retained without score or persona-quota filtering.

Resume with the same `--run` command; completed stages and received responses are reused. Add `--retry-errors` only to retry recorded failed stages. `--retry-uncertain` explicitly allows retrying a request whose provider outcome was lost; inspect its ledger first because it may already have been billed. Keep one runner process active. After independent review, use its findings to update prompts and prepare the next numbered round. Stop after five rounds even if desired ratings remain unmet.

## Independent evaluation

When execution and any recovery are complete:

```bash
.venv/bin/python experiments/chemistry_prompt_loop/prepare_evaluator.py --round 1
```

This prints a neutral temporary packet directory. Start a **fresh** `collaboration.spawn_agent` using `model="gpt-6-astra"`, `reasoning_effort="xhigh"`, and `fork_turns="none"`. Its message must be the **verbatim contents** of that packet's `evaluation_task.txt`. Do not add targets, prior ratings, optimizer feedback, or conversation history. The script prepares the packet; the collaboration tool launches the evaluator.

The evaluator takes the perspective of a human chemist, first reviewing every source and every blinded candidate independently, then examining routing and verifier judgments. It writes three review files inside the packet; collection also preserves the task text. In coverage bookkeeping, `skips_reviewed` means decider all-mode skips. Track generator abstentions and provider failures separately. Collect after the agent finishes:

```bash
.venv/bin/python experiments/chemistry_prompt_loop/prepare_evaluator.py --round 1 --collect
```

Collection checks input/task hashes, exact source and candidate coverage, source/mode identity, valid eligibility modes and ratings, and consistent readiness/skip counts. Results are copied into the round's `evaluation/` directory. Existing packets are reused only when their pinned inputs remain unchanged. The packet never includes repository prompts, optimization history, or earlier evaluations. Isolation is enforced by a fresh agent context and explicit task instructions; it is not a filesystem sandbox.

## Offline recovery

An earlier adapter rejected otherwise complete OpenRouter responses containing `service_tier="provisioned"`. Once the original process finishes, recover these saved responses without paid calls:

```bash
.venv/bin/python experiments/chemistry_prompt_loop/run_round.py --round 1 --recover-transport
```

Recovery selects the earliest saved response that passes the unchanged content parsers. It retains original requests, responses, errors, and prior stage state, and records provenance in `transport_recovery.json`. It does not repair model content or bypass provider refusals. Prepare the evaluator packet only after recovery and other artifact changes are finished.

## Reading the artifacts

| Artifact | Purpose |
| --- | --- |
| `sources_only.csv`, `blinded_candidates.csv` | Independent source and candidate review before seeing model judgments. |
| `review_with_source.csv` | Every canonical candidate, full source, annotations, and verifier output; original generation order. |
| `sources_and_decisions.json` | Every sampled source and all seven eligibility decisions, including skips/errors. |
| `best_per_document_with_source.csv` | Supplementary ranking view; never the sole evaluation population. |
| `generation_attempts.json`, `validation_failures.json`, `errors.json` | Raw generation attempts, malformed outputs, and unresolved stages. Provider refusals differ from chemistry-based abstention. |
| `documents/`, `call_ledger.json`, `summary.json` | Checkpoints, raw provider calls, usage, coverage, and supplied cost figures. Missing cost values do not mean free calls. |
| `manifest.json`, `prompts/` | Frozen source/model settings and prompt hashes/snapshots. |
| `evaluator_invocation.json`, `evaluation/` | Requested isolated model configuration, packet hashes, collected judgments, and ratings. The invocation records intent; the collaboration tool result establishes which agent was launched. |

Offline checks:

```bash
.venv/bin/python -m pytest -q experiments/chemistry_prompt_loop/test_run_round.py experiments/chemistry_prompt_loop/test_prepare_evaluator.py
```
