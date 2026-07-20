# CLIR benchmark

Builds and evaluates multilingual cross-language information retrieval benchmarks from
document collections that exist in several languages as human translations of one another.

The current domain is chemistry patents, built from Google Patents Public Data and EPO bulk
full-text data. The code is domain-pluggable: a new body of documents is a new folder under
`src/clir_bench/domains/`, not a change to the pipeline.

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
    chem_patents/   schema, vocabulary, attribution, sources, prompts, benchmarks
data/           corpora and artifacts (gitignored)
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
