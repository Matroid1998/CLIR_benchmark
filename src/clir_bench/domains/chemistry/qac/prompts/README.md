# chemistry prompts

This directory is where the domain knowledge lives. The Python code in
`clir_bench` is domain-agnostic plumbing — it batches passages, calls a model,
parses JSON, ranks candidates and writes CSV. What makes the output *chemistry
patent* questions rather than generic questions is entirely the text in these
files: the seven retrieval personas, scientific fidelity and evidence rules,
multilingual worked examples, and grading rubrics.

Changing a rubric here changes the benchmark. Treat these files as data, not
as prose to tidy up — they were tuned against real generator output and the
wording carries weight (the scale calibration paragraph, for instance, exists
to stop graders handing out 4s and 5s by default).

Files are package data, addressed through `importlib.resources` via
`clir_bench.core.prompts.PromptPack`. Every directory carries an `__init__.py`
so the package resolves the same way installed, zipped, or from source.

The generation files are the exact standalone blocks from the repository-root
`chemistry_prompts_{de,en,es,fr,zh}.md` files, with only the surrounding Markdown
fences and blank lines removed. Preserve the prompt wording and the verbatim
source/evidence examples when editing or formatting these resources.

## Layout

    generation/lookup/{en,de,fr,es,zh}.txt                 missing technical specification
    generation/process_retrieval/{en,de,fr,es,zh}.txt      connected route or workflow
    generation/conceptual/{en,de,fr,es,zh}.txt             explicit functional relationship
    generation/constraint_search/{en,de,fr,es,zh}.txt      solution meeting requirements
    generation/comparison/{en,de,fr,es,zh}.txt             two sides on a common dimension
    generation/assertion_verification/{en,de,fr,es,zh}.txt scoped assertion check
    generation/source_finding/{en,de,fr,es,zh}.txt         publication identity from a technical clue
    verifiers/faithfulness_{batch,single}.txt   is the answer grounded in the passage?
    verifiers/<persona>_batch.txt              quality and contract checks for each new persona
    verifiers/technical_{batch,single}.txt     legacy grading and single concept queries
    verifiers/semantic_batch.txt               legacy semantic grading
    concept_query/{en,de,fr,es,zh}.txt          alias-graph: question whose answer IS the concept
    concept_query_with_term/{en,de,fr,es,zh}.txt alias-graph: same, but must use a given surface form verbatim
    code_switch/nonchem_swap.txt                picks a non-chemistry word to swap (robustness control)

`PromptPack.generation(mode, lang)` reads `generation/<mode>/<lang>.txt`;
`.faithfulness(arity)` and `.quality(mode, arity)` read from `verifiers/`;
everything else is reached with `.custom(...)`.

## Generation contract

All seven personas are enabled by default for every chemistry generation plan.
Use `--modes` to select a subset; `technical` and `semantic` are no longer
generation modes. Each call returns one to three candidates, or one
`skip_reason` object when the source cannot support that persona. An abstention
produces no candidate rows and does not call the graders. Malformed output
raises an error and is retried under the configured generation retry policy.

The parser in `../candidates.py` checks exact field sets, types, enums and
question-substring annotations. It preserves evidence verbatim. Scientific
support, evidence provenance and translation fidelity are checked by the
verifiers. Questions, evidence, evidence language, translation flags and all
persona annotations survive CSV export and regrading; arrays and booleans use
JSON cell encoding. Publication identifiers accompany the source passages for
source-finding. Best-candidate selection retains one result per publication,
question language and persona.

The seven batch quality rubrics use the same five score columns (search-bar
realism, specificity, phrasing economy, focus and linguistic quality) while
applying each persona's own contract. The batch faithfulness rubric supports
translations, connected spans and identifier answers with separate evidence.
These rubrics accompany the new generation contract and need empirical
calibration before comparing their scores with historical runs.

## The batch / single split is deliberate — do not merge these

The `_batch` and `_single` verifier prompts look nearly identical when you diff
them, which makes merging them tempting. They must stay separate because they
have **different output contracts**, and the parsers downstream depend on it:

| | input | output |
|---|---|---|
| current `*_batch.txt` | multilingual passages + **one to three** candidates | a JSON **list** matching the input count, each carrying an `"index"` |
| `*_single.txt` | one passage + **one** QA pair | a single JSON **object**, no `"index"` |

The batch form exists because the main QAC pipeline generates up to three candidates
per document and ranks them, so it grades all three in one call — one request
instead of three, and the grader sees the candidates in a fixed order. The
single form exists for the alias-graph path, which produces exactly one query
per concept and has nothing to rank.

The instruction text differs accordingly and not only in arity. The batch
prompts carry independence guardrails because grading candidates side by side
invites contrast effects. The single prompts instead judge the pair on its own
merits. Legacy technical and semantic batch rubrics retain their historical
three-candidate wording for old datasets.

There is no `semantic_single.txt`: the alias-graph path only ever grades
technical-style concept queries.
