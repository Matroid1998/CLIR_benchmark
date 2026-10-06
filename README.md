# CLIR benchmark

Builds and evaluates multilingual cross-language information retrieval benchmarks from
document collections that exist in several languages as human translations of one another.

The domains are chemistry patents (Google Patents Public Data and EPO bulk full-text data)
and legal documents (EUR-Lex articles and United Nations document blocks). Domains declare
their sources and connect their workflows to the same `clir` commands.

## Why parallel documents

Cross-language retrieval is usually evaluated on machine-translated queries or documents,
which measures the translation as much as the retriever. Patent families give something
better: the same document, written by people in several languages. A query about a document
should retrieve any of its language versions, so cross-lingual retrieval becomes directly
measurable. That relation — which documents are versions of one another — is the axis the
whole design turns on.

## Install

```bash
uv sync                      # pipeline only
uv sync --extra chem         # + BigQuery, EPO streaming, ontology graph
uv sync --extra eval         # + the embedding-model stack (compute nodes)
cp .env.example .env         # then fill in the keys you need
```

## Formatting

```bash
uv run ruff format                       # Python
uv run ruff check
uv run python scripts/format_prompts.py  # the prompt templates
```

`scripts/format_prompts.py` hard-wraps the prompt files under
`src/clir_bench/domains` to 100 display columns. It only ever *splits* an
over-long line -- it never joins lines, and it refuses to write unless the
whitespace-stripped text is unchanged and a second pass is a no-op, so the only
thing that can move is where the newlines fall. Blocks shaped like the model's
runtime input (`### ` headers, `[EN] ...` unit headers, `Act:`/`Cite as:`
metadata, quoted source bodies) and the JSON output examples are left verbatim.
Chinese breaks after its own punctuation, never inside a word. `tests/` checks
the templates stay formatted; use `--check` to see what would change.

## Use

```bash
clir domains                 # what is installed
clir config                  # resolved settings and paths

clir ingest gp --limit 500   # extract from BigQuery
clir ingest epo --batches 3  # stream EPO bulk data, resumably
clir corpus filter --source gp --min-langs 2
clir corpus stats

clir qac generate --source gp --plan balanced --questions 100
clir qac generate --source gp --plan balanced --questions 4 --dry-run   # inspect the plan first

clir publish corpus
clir publish benchmark --source gp --dry-run

clir eval plan all --sbatch  # prepare the job; run it on a GPU node
clir analyze questions --run latest
clir runs list
```

Chemistry-specific benchmarks:

```bash
clir alias-graph build       # concepts with look-alike hard negatives
clir code-switch build       # swap a term, see whether retrieval survives
clir progressive all         # swap one more term per rung, measure decay
```

Legal generation and model comparisons use the existing EUR-Lex and UN batch pipelines:

```bash
clir --domain legal qac generate --source eurlex --questions 30
# data/legal/eurlex/qac/<timestamp>/results.csv

clir --domain legal qac generate --source un --questions 30
# data/legal/un_parallel/qac/<timestamp>/results.csv

# One invocation creates matching run folders under both corpus QAC roots:
clir --domain legal qac generate --source eurlex un --questions 30 \
  --generation-model provider/model-a --generation-model provider/model-b \
  --verifier-model anthropic/claude-sonnet-5.5 --output results.csv

clir --domain legal qac generate --source eurlex un \
  --targets-from data/legal/eurlex/qac/comparison_2026-09-21 \
  --generation-model provider/model-c

clir --domain legal qac regrade \
  --input data/legal/un_parallel/qac/comparison_2026-09-21/results.csv

clir --domain legal qac best \
  --input data/legal/un_parallel/qac/comparison_2026-09-21_regrade_v2/results.csv
```

Each corpus run contains one `results.csv` combining its models and one `run.sqlite` state file. The CSV
includes all generated candidates for that corpus, their source text, model and persona, verifier scores,
and `is_best`; the state file records inputs, attempts, and completed stages. `--output`
sets the CSV filename inside the run folder. Omitting `--run-dir` creates a timestamped
folder under `data/legal/eurlex/qac/` for EUR-Lex or `data/legal/un_parallel/qac/` for UN.
When both corpora are selected, they receive the same run ID under their respective QAC roots.
An explicit `--run-dir` for multiple sources is a custom parent containing `eurlex/` and
`un_parallel/` run folders. Regrading infers the sources from the input CSV, creates a
separate run in each corresponding location, and preserves the original.
Best-only CSVs are written only by the explicit `best` command.

Legal runs share validated verifier grades across generators when the exact QA,
source context, verifier prompt/model/settings, and relevant candidate metadata match.
Candidate IDs and generator identities do not prevent reuse. Unseen candidates are
still graded in batches; each generator retains its own rows and candidate IDs.
The cache and reuse provenance live in `run.sqlite` and survive resume. Changed
answers, metadata, or verifier inputs require new grades; failed responses are not cached.
When reuse changes a quality batch, `quality_batch_diversity` is `not_evaluated`:
candidate scores are shared, but a judgment about a different batch is not copied.

For legal generation, `--questions 30` selects 30 target/language/persona cases per model,
split evenly across the selected sources. Each case can yield up to three candidates;
skipped targets or provider failures can reduce the number of successful cases. Every model
receives the same selected targets and contexts. `--targets-from` reuses a previous run's
selections, including its original source counts. Default modes and languages remain those
enabled by each source's batch pipeline; use `--modes` and `--langs` to restrict them.
`--dry-run` inspects the work without model calls or output files. To continue an interrupted
source run, select that source and supply its `--run-dir` with `--resume`; completed compatible
stages are reused. A multi-source run with a custom parent can also repeat its command with `--resume`. `--retries`
is the total attempts per stage (default: three). Context-capacity errors are retained in
the run state, with unknown capacity left unknown.

To request a saved question count per mode, use `--questions-per-mode` instead of
`--questions`. With `--targets-from`, this consumes only the previous run's target
pool, optionally filtered by `--langs` and `--modes`, until each mode reaches the
requested count. Historical run folders and results CSVs are supported. Short or
skipped batches advance to the next existing target; an exhausted pool is reported.
Every generator processes the same document rounds until all generators meet the
quota or the pool is exhausted. Surplus candidates remain in the run state, while
the CSV contains up to the requested count. `--trace` also writes `llm_calls.json` and `trace.md`
with every prompt, response, retry, and parsed grade in the same run folder.

For legal sources, add `--decider-model generator` to let each generator choose its
generation prompt before writing questions, or `--decider-model jev` to use Jev:

```bash
clir --domain legal qac generate --source eurlex un --questions 30 \
  --decider-model generator --generation-model gpt-5.6-luna --trace

clir --domain legal qac generate --source un --questions 30 \
  --decider-model jev --generation-model gpt-5.6-luna --trace
```

The decider sees the complete assembled generation payload. EUR-Lex choices are
`fact_pattern`, `lookup`, `conceptual`, and `skip`; UN choices are `lookup`, `practitioner`,
`conceptual`, and `skip` (`practitioner` maps to the existing `practitioners` prompts).
A skip makes no generation or verifier calls. Otherwise the chosen mode's existing
generator, verifiers, and best-candidate ranking run as usual. `--questions` counts
targets, so skips can reduce output. Do not combine the decider with `--modes` or
`--questions-per-mode`. Omit the flag to retain explicit mode selection. Reusing a
fixed-mode target plan with a decider deduplicates repeated target/language pairs.

Decisions are checkpointed in `run.sqlite`, including skips, and reused on resume.
CSV rows include the selected mode, decider model, reason (chat models), and
confidence/probabilities when returned by Jev. `--trace` includes the decider's raw
request and response. Invalid decisions are retried and then recorded as failures;
they never silently select a fallback mode. Regrading preserves decisions and only
reruns the verifiers. The original batch module CLIs also accept `--decider-model`.

Jev uses `OPENROUTER_API_KEY`, model `~typesafe/jev-latest`, and
[OpenRouter's Decisions endpoint](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request)
(`POST https://openrouter.ai/api/alpha/decisions`). Its structured instructions and
criteria are sent directly; it returns a typed choice rather than a prose reason.
The four decider templates are packaged in each legal prompt pack's `decider/` directory.

### Legal prompt versions in local MLflow

The [MLflow Prompt Registry](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.register_prompt)
runs locally with SQLite and requires no account, API key, or server. Install its
optional dependencies with `uv sync --extra prompts`. The default database is
`.clir/prompts.db` at the workspace root; override it with
`CLIR_PROMPT_REGISTRY_URI=sqlite:////absolute/path/to/prompts.db` or `--registry-uri`.

After editing prompts, publish all EUR-Lex and UN templates and activate their
pinned snapshot for subsequent legal runs:

```bash
python -m clir_bench.core.prompt_registry sync \
  --bundle legal-next --label legal-next \
  --output reports/prompt_versions/legal-next.json
python -m clir_bench.core.prompt_registry activate \
  --manifest reports/prompt_versions/legal-next.json \
  --label production
clir --domain legal qac generate --source eurlex un --langs en --questions 100
```

`sync` includes all 48 current templates: every language and supported legacy mode,
not just the sixteen English prompts compared by the experiment. Other languages
therefore remain available after activation. To publish a saved snapshot, use
`publish --prompts path/to/prompts.json` with the same bundle, label and output
arguments. The JSON maps logical keys, such as `un/generation/practitioner`, to
exact prompt text; supplemental evaluation prompts may be included.

Each publication records MLflow names, immutable version numbers, text SHA-256,
and exact text in a self-contained manifest. Repeating the same experiment alias
and text is idempotent. Changed text needs a new alias and manifest path; existing
experiment aliases cannot silently move. The SDK supports moving aliases, but
runtime reads pinned manifest text, so alias changes cannot change an ongoing run.

`activate` verifies every pinned version, sets the chosen deployment alias and
atomically writes `.clir/active_prompt_manifest.json`. Later legal loads discover
this file from the workspace root or its subdirectories. Explicit
`CLIR_PROMPT_MANIFEST=/absolute/path/to/manifest.json` selects a different run pin.
Missing prompt keys or invalid hashes fail rather than falling back to edited
local files. Jev JSON remains exact text until its native request is built.

Before first activation, package prompts remain available. For intentional
unregistered development, set `CLIR_PROMPT_SOURCE=local`; it bypasses the default
active snapshot and cannot be combined with an explicit manifest. Tests can use
`CLIR_PROMPT_SOURCE=local python -m pytest`. Keep immutable experiment manifests
with their runs and preserve `.clir/prompts.db` to retain registry history.

Activation updates aliases individually before replacing the local active
snapshot; retry activation if interrupted. Existing active runs retain their
snapshot. Normal publication does not activate a bundle automatically.

For a paired prompt experiment, `python -m clir_bench.domains.legal.qac.screening`
accepts `--selection previous/run/selection.json --prompt-manifest version/manifest.json`
and an independent `--output` directory. It rebuilds and verifies the exact saved source
payloads before making calls, then runs both deciders and all eligible generation modes.
`screening_analysis` exports the native results. `screening_repair --recovery-only`
can recover schema-only failures from recorded responses without new model calls;
repairs retain pinned prompts and their own audit log.

`python -m clir_bench.domains.legal.qac.experiment_evaluation` compares completed runs
using one pinned, mode-blind rubric; identical pairs are graded once across versions.
`reports/prompt_experiments/compare_versions.py` writes a standalone HTML report and
paired CSV summaries. Its optional `--mlflow-registry-uri` logs aggregate experiment
metrics alongside the registered prompts. See each command's `--help` and the
[September 2026 experiment design](reports/prompt_experiments/legal_20260930/experiment_design.json)
for the frozen sample, models, criteria and limitations. The
[experiment findings](reports/prompt_experiments/legal_20260930/findings.html)
record the completed reruns, controlled router comparisons, and current evaluation status.

```bash
clir --domain legal qac generate --source eurlex --langs en \
  --modes lookup fact_pattern --questions-per-mode 15 \
  --targets-from data/legal/eurlex/qac/eurlex_luna30_en \
  --generation-model gpt-5.6-luna --verifier-model anthropic/claude-sonnet-5.5 \
  --run-dir data/legal/eurlex/qac/modes15_new_verifiers --trace
```

Any command's `--help` lists its options; `--dry-run` exists wherever something is written
or published.

## Running models

Encoding a corpus needs a GPU and can exhaust a workstation, so it is opt-in. The normal
path is `clir eval plan`, which writes the exact command and an sbatch script; the run
itself needs `--allow-local` on the machine that should do the work. Analysis reads saved
predictions, so every breakdown, metric and plot can be recomputed without touching a model.

## Layout

```
src/clir_bench/
  core/         domain-independent stages: corpus, qagen, grading, publish, ingest, runs
  evaluation/   retrieval harness, metrics, model loading
  analysis/     per-question, confusion, rescoring, tables (reads saved predictions)
  cli/          command groups
  domains/
    chemistry/   schema, vocabulary, attribution, sources, prompts, benchmarks
    legal/       structured legal corpora, source prompts, batch pipelines, QAC runs
data/           corpora and artifacts (gitignored)
data/legal/eurlex/qac/       EUR-Lex question-generation runs
data/legal/un_parallel/qac/  UN question-generation runs
data/legal/qac/              preserved original combined exports (historical provenance)
reports/runs/   evaluation runs, each self-describing
attic/          one-off scripts, frozen with provenance notes
docs/           ARCHITECTURE.md, MIGRATION.md, licensing and pipeline notes
```

`core/` may not import from `domains/` — a domain reaches the core only as data on its
`DomainSpec`. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the contract and
[docs/MIGRATION.md](docs/MIGRATION.md) for the mapping from the previous repo.

## Data licensing

Patent text comes from third-party sources with their own terms, and each dataset published
from here carries the attribution of the source it was actually built from — Google Patents
Public Data is CC BY 4.0 and requires attribution; EPO bulk data has its own conditions.
Publishing a source with no declared attribution is a hard error rather than a default. See
[docs/DATA_LICENSE_AND_CONFIRMATION.md](docs/DATA_LICENSE_AND_CONFIRMATION.md).
