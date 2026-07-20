# Migration from Multi-Lingual-QAC

## Commands

The old CLI was one command with ~80 flags, where flag *order in the source* decided which
action ran. Every action is now a subcommand.

| Old | New |
|---|---|
| `qac` (no flags) | `clir ingest gp` |
| `qac --limit 500 --qa-sample 50` | `clir ingest gp --limit 500` then `clir qac generate --source gp --questions 50` |
| `qac --epo-ingest --num-batches 3` | `clir ingest epo --batches 3` |
| `qac --epo-ingest --chemistry-strict` | `clir ingest epo --strict` |
| `python -m ...preprocess.filter_multilingual` | `clir corpus filter --source gp` |
| `scripts/dedup_epo_vs_gp.py` | `clir corpus dedup --source epo --against gp` |
| `scripts/generate_epo_qac.py` | `clir qac generate --source epo --plan uniform` |
| `scripts/generate_extra_qac.py` | `clir qac generate --source gp --plan coverage --priority-langs zh es` |
| `scripts/generate_zh_extra_qac.py` | `clir qac generate --source gp --plan coverage --priority-langs zh` |
| `scripts/regrade_with_openrouter.py` | `clir qac regrade --input CSV --source gp` |
| `qac --push-corpus-hf` | `clir publish corpus` |
| `qac --push-hf --hf-repo R` | `clir publish benchmark --source gp --repo R` |
| `scripts/push_qac_chempatents_hf.py` | `clir publish benchmark --source gp` |
| `qac --evaluate-mteb all --run-id paper` | `clir eval run all --run-label paper --allow-local` (on a compute node) |
| *(no equivalent)* | `clir eval plan all --sbatch` — prepare the job without running it |
| `qac --generate-mteb-tables` | `clir eval tables --run ID` |
| `qac --analyze-questions` | `clir analyze questions --run ID` |
| `qac --analyze-confusion` | `clir analyze confusion --run ID` |
| `scripts/alias_graph_interpretations.py` | `clir analyze rescore --run alias_graph` |
| `scripts/regen_analysis_drop_gte.py` | `clir analyze rescore --drop-models Alibaba-NLP/gte-multilingual-base` |
| `qac --build-alias-graph` | `clir alias-graph build` |
| `qac --alias-generate-qa --alias-qa-limit 20` | `clir alias-graph qa --limit 20` |
| `qac --push-alias-graph-hf` | `clir alias-graph publish` |
| `scripts/patch_alias_graph_hf_source.py` | `clir alias-graph publish --only-configs queries qac source_qrels` |
| `qac --export-concept CHEBI:15365` | `clir alias-graph export-concept CHEBI:15365` |
| `qac --cache-all-chebi-wiki` | `clir alias-graph names --cache-all` |
| `qac --check-wiki-names` | `clir alias-graph names --check` |
| `qac --build-code-switched --cs-limit 50` | `clir code-switch build --limit 50` |
| `qac --cs-generate-qa` | `clir code-switch qa` |
| `qac --create-progressive-data` | `clir progressive all` |
| `qac --build-progressive-cs` | `clir progressive build` |
| `qac --progressive-cs-qa` | `clir progressive qa` |
| `qac --push-progressive-cs` | `clir progressive publish` |
| `qac --eval-progressive-cs` | `clir progressive eval --allow-local` |
| *(none)* | `clir domains`, `clir config`, `clir runs list`, `clir runs show`, `clir corpus stats` |

## Settings that used to be flags

Values that never changed per invocation now live in `clir.toml` instead of being repeated
as defaults in three places. Flags still override them.

| Old flag default | Now |
|---|---|
| `--mteb-corpus-repo MehdiAstaraki/multilingual_GP` | `[domains.chem_patents] corpus_repo` |
| `--mteb-dataset-repo ...chem-patents` | `[domains.chem_patents] benchmark_repo` |
| `--alias-hf-repo`, `--pcs-hf-repo`, `--corpus-hf-repo` | `alias_graph_repo`, `progressive_repo`, `corpus_repo` |
| `--alias-qa-model`, `--cs-model`, `--pcs-qa-model` (all `gpt-5-mini`) | `[llm] generation_model` |
| `--pcs-grader-model` | `[llm] concept_verifier_model` |
| `--chebi-variant full` | `[domains.chem_patents] chebi_variant` |
| curated 10-model list in `evaluation.py` | `[domains.chem_patents] eval_models` |

## Data

Nothing needs converting. `data_layout` in the domain spec reproduces the old directory
names exactly, so an existing `data/` tree works unmoved:

```
data/google_patents/{chemistry_patents.ndjson,preprocessed/,multilingual_corpus.csv,qac/}
data/EPO/{manifest.json,multilingual_corpus.csv,qac/}
data/{chebi,alias_graph,code_switched,progressive_cs}/
```

Two additions: `data/human_eval/` for the annotation spreadsheet that used to sit in the
repo root, and `data/baselines/` for the frozen snapshot the coverage plan resumes against.

Copy or symlink the old tree:

```bash
cp -r ../Multi-Lingual-QAC/data  ./data          # or: ln -s ../Multi-Lingual-QAC/data data
cp -r ../Multi-Lingual-QAC/reports ./reports
```

`data/EPO/manifest.json` carries ingest resume state — copy it, don't regenerate it, or the
next EPO ingest re-appends documents already in the corpus.

## What moved where

| Old | New |
|---|---|
| `dataloaders/google_patents.py` | `domains/chem_patents/sources/google_patents.py` (+ generic parts to `core/corpus.py`) |
| `dataloaders/epo_bdds.py` | `domains/chem_patents/sources/epo_bdds.py` (+ streaming/manifest/accumulator to `core/ingest.py`) |
| `dataloaders/epo_xml.py` | `domains/chem_patents/sources/epo_xml.py` |
| `preprocess/filter_multilingual.py` | `core/corpus.filter_multilingual` |
| `preprocess/corpus.py` | deleted (was a re-export shim over the loader) |
| `qac_generation/multilingual_qa.py` | split: engine to `core/qagen.py`, grading to `core/grading.py`, prompts to `domains/chem_patents/qac/prompts/` |
| `qac_generation/balanced_multilingual_qa.py` | `domains/chem_patents/qac/plans.py` (`balanced`) |
| `qac_generation/openai_qa.py` | `attic/` (superseded English-first pipeline) |
| `export/hf_upload.py` | `core/publish.py` + `domains/chem_patents/attribution.py` |
| `mteb/evaluation.py` | `evaluation/{harness,models,metrics}.py` + `analysis/tables.py` |
| `mteb/question_analysis.py` | `analysis/questions.py` (+ shared loaders to `analysis/predictions.py`) |
| `mteb/runs.py` | `core/runs.py` |
| `progressive/eval.py` | `domains/chem_patents/codeswitch/progressive_eval.py` |
| `alias_graph/{chebi,matching,builder}.py` | `domains/chem_patents/aliasgraph/` |
| `alias_graph/{wikidata_names,cache_all}.py` | `domains/chem_patents/aliasgraph/wikidata.py` |
| `alias_graph/confusion_analysis.py` | `analysis/confusion.py` |
| `alias_graph/retrieval_results.py` | `analysis/rankings.py` |
| `alias_graph/qac_generation/claude_grading.py` | deleted — `core/grading.GraderConfig` handles the transport |
| `scripts/` (25 files) | commands above, or `attic/` — see `attic/README.md` |

The local package named `mteb` is gone. It only worked because of namespacing; the
evaluation package is now `evaluation`, so `import mteb` unambiguously means the library.

## Behaviour that intentionally changed

1. **Attribution is scoped per source.** EPO-derived datasets no longer carry the Google
   Patents CC BY 4.0 block. Publishing a source with no declared attribution now fails
   instead of defaulting.
2. **`clir eval run` refuses to load models** without `--allow-local` (or
   `allow_local_models` in `clir.toml`). Use `clir eval plan` to prepare a cluster job.
3. **Text fallback uses `or` chaining consistently.** The old Option-A pipeline used
   dict-default chaining, so a row with a present-but-empty `context` skipped a non-empty
   `abstract` and fell through to the title. Every path now picks the abstract.
4. **`select_best` sorts explicitly** rather than relying on upstream ordering.
5. **`concept_id` replaces `chebi_id`** in the exported rankings table, since that analysis
   is domain-agnostic. Published dataset configs keep their original column names.

Everything else — prompts, rubrics, thresholds, SQL, regexes, id conventions, qrels
semantics, CSV schemas — is byte-for-byte or logic-for-logic identical.
