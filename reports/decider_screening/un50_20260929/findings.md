# UN decider screening: 50 documents

Completed on 29 September 2026: **100 decider decisions, 150 mode trials, and 184 generated and graded candidates**. The sample contains one English target block from each of 50 distinct UN documents: 25 resolutions, 20 meeting records, and 5 letters. No EUR-Lex documents were included in this screening.

Generation and the standard decider used **GPT-5.6 Luna**. Jev used **`~typesafe/jev-latest`**. Both faithfulness and quality grading used **Claude Sonnet 5.5**. Every decision and mode trial received the same source payload for its target. Selection seed: **20260929**.

## 1. Mode distribution

Counts below include skip decisions.

| Sample | Decider | Lookup | Practitioner | Semantic | Skip |
|---|---|---:|---:|---:|---:|
| All 50 | GPT | 14 (28%) | 2 (4%) | 31 (62%) | 3 (6%) |
| All 50 | Jev | 12 (24%) | 3 (6%) | 30 (60%) | 5 (10%) |
| Without meetings, n=30 | GPT | 14 (46.7%) | 2 (6.7%) | 14 (46.7%) | 0 |
| Without meetings, n=30 | Jev | 12 (40%) | 3 (10%) | 15 (50%) | 0 |
| Meetings only, n=20 | GPT | 0 | 0 | 17 (85%) | 3 (15%) |
| Meetings only, n=20 | Jev | 0 | 0 | 15 (75%) | 5 (25%) |

Meeting records explain part of the overall semantic preference: excluding them reduces semantic from 62% to 46.7% for GPT and from 60% to 50% for Jev. Both deciders respected the meeting-record restriction on every case. All skips occurred on meeting records. These are frequencies in this deliberately stratified sample, not estimates of the full UN corpus distribution.

![Mode distributions](mode_distribution.png)

## 2. Which generation mode produced better grades?

The main comparison uses the **30 non-meeting targets**, where all three modes are eligible. Scores are faithfulness /15 plus quality /25, totaling /40. Each target-mode score is its highest-scoring candidate with UN grounding at least 3. Mean scores below exclude cases where that mode produced no qualifying candidate; the coverage column makes that denominator explicit.

| Mode | Targets with a scored candidate | Mean best score /40 | Targets where mode tied or won the highest score | Targets with an audit-clear candidate |
|---|---:|---:|---:|---:|
| Lookup | 20/30 | 29.90 | 7 | 10/30 |
| Practitioner | 18/30 | 29.22 | 4 | 7/30 |
| Semantic | **27/30** | **30.81** | **22** | **19/30** |

Two targets produced no scored candidate in any mode. The winning-mode counts retain ties, so they sum to more than 28. Semantic had both the highest yield and the highest mean best score in this sample; it tied or won on 22 of the 28 targets with any scored candidate.

Raw grades alone are insufficient: **11/20** lookup winners and **10/18** practitioner winners had a blocking quality audit, versus **2/27** semantic winners. A lower-scoring candidate in the same batch can still pass its audit. Requiring a clear/minor-issues audit and assigning zero to targets without one gives mean target-level utilities of **10.43** for lookup, **7.37** for practitioner, and **19.80** for semantic. This stricter view also favors semantic.

On the 20 meeting records, both lookup and practitioner skipped all 20 diagnostic trials. Semantic produced scored candidates on **18/20** targets, with a mean best score of **30.44/40**; **11/20** had an audit-clear candidate. Ineligible modes were never allowed to win.

![Mode scores](mode_scores.png)

## 3. Jev versus the generator-based decider

The deciders agreed on **37/50 (74%)** targets. Agreement was **19/30 (63.3%)** without meetings and **18/20 (90%)** for meetings alone.

The non-meeting comparison is more informative because all three modes can compete:

| Metric, non-meeting targets | GPT decider | Jev |
|---|---:|---:|
| Selected mode produced a scored candidate | 23/30 | **27/30** |
| Selected a tied/highest-scoring mode | 13/28 | **17/28** |
| Mean selected score, when available | 30.39 | 30.44 |
| Selected an unproductive mode although another mode worked | 5 | **1** |
| Mean score with zero for no candidate | 23.30 | **27.40** |
| Mean score with zero unless a candidate also passes the audit | 13.60 | **15.63** |

Jev's observed advantage comes mainly from avoiding modes that yield no candidate, rather than from substantially higher grades when both routes produce a question. Its paired mean advantage was **4.10 points per non-meeting target**, counting no candidate as zero. A target-bootstrap 95% interval was approximately **−0.07 to +8.80**, so this small screening does not establish a decisive advantage.

Jev abstained more often on meetings: 5 skips versus GPT's 3. Semantic generation nevertheless produced scored candidates for 4 of Jev's skipped targets and 2 of GPT's. That does not prove those skips were mistaken: some candidates had blocking audit issues. Indeed, both deciders had the same audit-clear meeting utility, **17.65**, despite GPT's higher raw yield.

Across all 50 targets, Jev's selected route produced a scored candidate on **41/50**, versus GPT's **39/50**. Their coverage-adjusted means were **25.20** and **23.90**, respectively; the paired difference interval includes zero.

### Speed and recorded cost

Jev's 50 decisions averaged **0.274 seconds** each (95th percentile **0.395 s**), versus **3.358 seconds** (95th percentile **6.380 s**) for GPT's decisions: roughly **12× faster** in this run. These are observed API-call durations under this workload, not controlled serving benchmarks.

OpenRouter reported **$0.009712** for all 50 Jev decisions. Total provider-reported cost, including grading and repairs, was **$6.279808**. Direct OpenAI calls did not report monetary cost, so that total excludes GPT generation and decider charges; see [usage.csv](usage.csv) for their token counts.

## Interpretation

**Jev is a promising router on this sample, but neither decider demonstrated an improvement over simply generating semantic questions for every non-meeting target.** That baseline yielded scored candidates on 27/30 targets, a coverage-adjusted mean of **27.73**, and an audit-clear mean of **19.80**. Jev matched its yield but scored slightly lower under the raw coverage metric and more clearly lower after audits. This supports keeping semantic as an explicit baseline in the next evaluation, and reviewing the lookup/practitioner choices that trigger skips or blocking audits.

The standard decider selected an unproductive lookup mode for `A/RES/61/173` and `E/RES/2014/23`, while Jev chose semantic, which scored 29 and 31 respectively. Conversely, GPT chose semantic for `A/RES/60/129`, producing a score of 30, while Jev chose practitioner and obtained no candidate. The [per-document comparison](document_comparison.csv) records all such cases and both deciders' choices.

A next screening should add human judgments of mode suitability and skip correctness, and repeat generation to measure stability. The current results are based on one sampled block per document, one generation batch per mode, and one automated judge. Different quality rubrics and different candidate counts limit claims about intrinsic mode superiority. “Highest observed score” is an experiment result, not gold-standard decider accuracy.

## Grading repairs and reproducibility

Eight target-mode batches initially failed strict verifier parsing. They were recovered or regraded without regenerating questions or changing scoring criteria. The faithfulness prompt requests three grades even when only one or two candidates exist; repair requests explicitly specify the actual count. One response with surrounding prose was recovered only after exact grade-count/schema validation. One quality response's missing positional indices were restored from its exact, unique candidate IDs, retaining the earliest valid response and unchanged scores.

The final exports contain **no unresolved grading failures**. The original calls remain unchanged in `run.sqlite`; [grade_repairs/trace.md](grade_repairs/trace.md) and its separate SQLite file preserve all repair attempts. The [technical analysis](analysis.md) includes full metric tables and definitions.

```bash
.venv/bin/python -m clir_bench.domains.legal.qac.screening \
  --output reports/decider_screening/un50_20260929 --un 50 --workers 8

.venv/bin/python -m clir_bench.domains.legal.qac.screening_repair \
  reports/decider_screening/un50_20260929

.venv/bin/python -m clir_bench.domains.legal.qac.screening_analysis \
  reports/decider_screening/un50_20260929
```

Completed compatible stages are reused; a new sample or model configuration requires a new output directory.

## Saved files

- [Documents and both deciders' choices, one row per document](document_comparison.csv)
- [Documents, full inputs, decisions, reasons and probabilities, one row per decider](decisions.csv)
- [All 150 target-mode results, including scores and skip reasons](mode_scores.csv)
- [All 184 questions and complete verifier grades](all_mode_candidates.csv)
- [Mode distributions](mode_distribution.csv), [mode summaries](mode_summary.csv), [decider metrics](decider_performance.csv), and [agreement](agreement.csv)
- [Selection](selection.json), [configuration](config.json), [machine-readable summary](summary.json), and [complete original call trace](trace.md)
