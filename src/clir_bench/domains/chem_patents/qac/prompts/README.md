# chem_patents prompts

This directory is where the domain knowledge lives. The Python code in
`clir_bench` is domain-agnostic plumbing — it batches passages, calls a model,
parses JSON, ranks candidates and writes CSV. What makes the output *chemistry
patent* questions rather than generic questions is entirely the text in these
files: the five question categories, the numerical-fidelity rules, the
"no document phrases" constraint, the worked Turkish/French examples, the
grading rubrics and their 1–5 calibration.

Changing a rubric here changes the benchmark. Treat these files as data, not
as prose to tidy up — they were tuned against real generator output and the
wording carries weight (the scale calibration paragraph, for instance, exists
to stop graders handing out 4s and 5s by default).

Files are package data, addressed through `importlib.resources` via
`clir_bench.core.prompts.PromptPack`. Every directory carries an `__init__.py`
so the package resolves the same way installed, zipped, or from source. Copied
byte-for-byte from the Multi-Lingual-QAC repo.

## Layout

    generation/technical/{en,de,fr,es,zh}.txt   fact-extraction question generation
    generation/semantic/{en,de,fr,es,zh}.txt    concept/problem/application question generation
    verifiers/faithfulness_{batch,single}.txt   is the answer grounded in the passage?
    verifiers/technical_{batch,single}.txt      is the question a good extractive query?
    verifiers/semantic_batch.txt                is the question a good semantic query?
    concept_query/{en,de,fr,es,zh}.txt          alias-graph: question whose answer IS the concept
    concept_query_with_term/{en,de,fr,es,zh}.txt alias-graph: same, but must use a given surface form verbatim
    code_switch/nonchem_swap.txt                picks a non-chemistry word to swap (robustness control)

`PromptPack.generation(mode, lang)` reads `generation/<mode>/<lang>.txt`;
`.faithfulness(arity)` and `.quality(mode, arity)` read from `verifiers/`;
everything else is reached with `.custom(...)`.

## The batch / single split is deliberate — do not merge these

The `_batch` and `_single` verifier prompts look nearly identical when you diff
them, which makes merging them tempting. They must stay separate because they
have **different output contracts**, and the parsers downstream depend on it:

| | input | output |
|---|---|---|
| `*_batch.txt` | one passage + **three** candidates | a JSON **list** of three objects, each carrying an `"index"` (0, 1, 2) |
| `*_single.txt` | one passage + **one** QA pair | a single JSON **object**, no `"index"` |

The batch form exists because the main QAC pipeline generates three candidates
per document and ranks them, so it grades all three in one call — one request
instead of three, and the grader sees the candidates in a fixed order. The
single form exists for the alias-graph path, which produces exactly one query
per concept and has nothing to rank.

The instruction text differs accordingly and not only in arity. The batch
prompts carry independence guardrails the single prompts have no reason to
("Grade each of the three questions independently … Do not penalize a question
for being similar to another candidate"), because grading candidates side by
side invites contrast effects. The single prompts instead say "judge the pair
on its own merits, against the rubric."

There is no `semantic_single.txt`: the alias-graph path only ever grades
technical-style concept queries.
