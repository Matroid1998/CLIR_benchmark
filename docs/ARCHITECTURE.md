# Architecture

## The problem this layout solves

The predecessor repo worked but had grown one shape: a single CLI with ~80 mutually
exclusive boolean flags dispatched through an if/return chain whose *order* silently
encoded which command won; a ~90-field config object shared by every command; and
chemistry-specific knowledge spread through modules that had no business knowing about
chemistry. Adding a second domain would have meant editing almost every file.

The organizing rule here is one sentence:

> A domain is data the core reads; the core never names a domain.

Everything else follows from that.

## Layers

```
cli/          argument parsing and dispatch only
   |
core/         domain-independent machinery (the pipeline stages)
   |
domains/      what a body of documents is, and what its words mean
```

Import direction is one-way and enforced by a test:

| From | To | Allowed |
|---|---|---|
| `domains/*` | `core/` | yes |
| `core/` | `domains/*` | **never** |
| `cli/` | `domains/` | only through `domains.load()` |
| `evaluation/`, `analysis/` | `domains/*` | **never** (they take domain facts as parameters) |

Because `core/` has no way to name a domain, chemistry cannot leak into it by accident;
it would not compile.

## The domain contract

A domain package exposes two symbols:

```python
SPEC: DomainSpec              # required -- pure data
def register_cli(registrar, context) -> None   # optional -- extra commands
```

`DomainSpec` (see `core/domain.py`) declares:

| Field | What it decides |
|---|---|
| `schema` | what a document row is; **`family_field`** groups cross-language versions |
| `languages` | inventory, working set, and the orderings that are load-bearing |
| `sources` | where documents come from, and whose licence applies |
| `prompts_package` | where the domain's prompt files live |
| `attributions` | per-source licensing text for dataset cards |
| `analysis` | the labels analyses report by (modes, strategies, diagnostic languages) |
| `data_layout` | logical path names to relative paths on disk |
| `defaults` | HF repo ids, model choices, knobs (overridable in `clir.toml`) |
| `qac_plans` | which documents get asked about, in which languages |

### Why `family_field` is the important one

The benchmark's central claim is that a query about a document should retrieve *any*
language version of it, because those versions are human translations of one another.
That relation is the whole benchmark. In the old code it was spelled `publication_number`
in a dozen places, which silently assumed patents forever.

Here every core stage — qrels construction, coverage filtering, cross-lingual metrics,
haystack removal — goes through `schema.family_of(row)`. A legal domain sets
`family_field = "celex_id"` and the same logic applies with no core change.

## Adding a domain

Create `src/clir_bench/domains/<name>/` with `domain.py` (the `SPEC`), `schema.py`,
`vocabulary.py`, `attribution.py`, `sources/`, `qac/prompts/`, and optionally `cli.py`.
Add a `[domains.<name>]` section to `clir.toml`.

Nothing else changes. Discovery is a `pkgutil` scan, so there is no registry file to edit,
and `available()` lists domains *without importing them* — so a domain with heavy
dependencies costs nothing until it is selected.

## Stages

```
ingest  ->  corpus  ->  qac  ->  publish  ->  eval  ->  analyze
```

Each is a CLI group and a core module. The contract between stages is a file on disk (a
corpus CSV, a QAC CSV, a published dataset, a run directory), which is what makes a stage
re-runnable in isolation and a half-finished pipeline resumable.

**Evaluation and analysis are deliberately separate.** Evaluation saves per-query
predictions; every analysis reads those. A new metric or a corrected breakdown never
requires re-encoding a corpus — which matters because encoding is the only expensive step.

## Where the duplication went

The old repo had these repeated across files; each now has one home:

| Was duplicated | Now |
|---|---|
| 6 LLM-judge grading shells | `core/grading.py`, parameterized by transport and arity |
| 5 OpenAI/OpenRouter client constructions | `core/llm.py` |
| 3 Claude thinking-transport copies | `core/llm.chat_with_thinking` |
| 3 markdown-fence JSON parsers | `core/llm.parse_json_response` |
| 4 copies of the 12-column schema | `domains/chem_patents/schema.py` |
| 7+ restatements of the 5-language set | `domains/chem_patents/vocabulary.py` |
| 5 HF publish skeletons | `core/publish.py` |
| CSV writer blocks in every builder | `core/corpus.write_rows` |
| thread-pool-with-progress in every generator | `core/parallel.run_tasks` |
| defaults in 3 places per flag | `core/config.resolve`, one precedence chain |

Two things were **not** merged, on purpose:

- **`clean_text` variants.** Google Patents text and EPO XML are cleaned differently, and
  both corpora are already published. `clean_text_simple` and `clean_text_nfkc` sit side by
  side and a source picks one explicitly.
- **Batch vs single verifier prompts.** One returns a JSON list of three gradings, the
  other a single object. Same rubric, different output contracts. Merging them would
  silently change grading.

## Deliberate guards

- **Publishing requires an attribution.** Cards are composed from the attribution of the
  source the data came from, and an unknown source raises. The old exporter attached the
  Google Patents CC BY 4.0 block to EPO-derived datasets too, crediting the wrong provider.
- **Loading embedding models is opt-in.** `clir eval run` refuses without `--allow-local`;
  `clir eval plan` writes the commands and an sbatch script to run on a compute node.
- **Appending to a dataset checks the header first.** Appending rows under a changed
  schema silently corrupts a CSV.
- **The manifest is written atomically.** Losing ingest state means duplicate rows.

## Cost of the abstraction

Two indirections a reader pays for: a corpus column is reached through `schema.family_of`
rather than `row["publication_number"]`, and prompts are addressed through a `PromptPack`
rather than a path. Both buy the second domain. Nothing else is abstracted — sources are
plain modules, plans are plain functions, and the benchmark builders are ordinary code
under the domain that owns them.
