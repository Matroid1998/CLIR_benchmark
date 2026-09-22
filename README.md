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
  --verifier-model anthropic/claude-sonnet-5 --output results.csv

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
