# legal prompts

QAC prompt pack for the **legal** domain (legislation, regulations, resolutions).
Extracted verbatim from `legal_qac_prompts_v1.md` at the repo root. As in
`chem_patents`, the Python code is domain-agnostic plumbing; what makes the output
*legal* questions is entirely the text in these files. Treat them as data, not
prose to tidy — the rubrics and their 1–5 calibration were tuned against real
generator output.

Files are package data, addressed through `importlib.resources` via
`clir_bench.core.prompts.PromptPack`. Every directory carries an empty
`__init__.py` so the package resolves the same way installed, zipped, or from
source.

## Layout (present today)

    generation/technical/{en,de,es,fr,zh}.txt  fact-extraction question generation
    generation/semantic/{en,de,es,fr,zh}.txt   concept/problem/application generation
    verifiers/technical_batch.txt   is the question a good extractive query? (3 candidates)
    verifiers/semantic_batch.txt    is the question a good semantic query?   (3 candidates)
    verifiers/faithfulness_batch.txt is the answer grounded in the passage?  (3 pairs)

The generation prompts exist in the same five languages as `chem_patents`:
English, German, Spanish, French and Chinese. Each language variant fully
translates the instructions and declares its own output language ("MUST be
written in French", etc.); the JSON output template, the enum values
(`question_type` / `framing`), the example source passages, and the `✗ Bad (…)`
failure tags stay in English. Following the chem_patents convention exactly, the
German, Spanish and French variants keep the worked example questions in English,
while the Chinese variant translates them (matching
`chem_patents/generation/*/{de,es,fr,zh}.txt`).

`PromptPack.generation(mode, lang)` reads `generation/<mode>/<lang>.txt`;
`.quality(mode, arity)` and `.faithfulness(arity)` read from `verifiers/`.

## Differences from the chem_patents pack (per the v1 source note)

Pipeline-compatible by design — same three-candidate structure, same JSON
schemas. The only schema-visible changes:

- **`question_type`** values (technical mode): `scope_or_applicability`,
  `obligation_or_prohibition`, `condition_or_prerequisite`, `deadline_or_duration`,
  `amount_or_threshold`, `monitoring_or_reporting`, `enforcement_or_consequence`,
  `definition_actor_or_procedure`.
- Added **`failure_type`** values: `unresolved-cross-reference` (both verifiers);
  `identifier-leak`, `boilerplate-generic` (semantic verifier).
- `numerical_fidelity` is **extended** (not renamed) to cover official identifiers
  — instrument, article, paragraph, and annex numbers — alongside numbers/dates.

## Not present yet (add when building the domain)

- **More language variants.** Generation prompts cover en/de/es/fr/zh. The working-
  language set for legal is not yet fixed (EU official languages for EUR-Lex, the
  six UN languages for the UN corpus), so add `generation/<mode>/<lang>.txt` for
  any further working language before generating in it.
- **Single-arity verifiers.** No `*_single.txt` — the source provides only the
  batch (three-candidate) verifiers used by the main QAC loop. A concept-query /
  alias-graph path (if ported) would need the single-object variants.
- **Domain wiring.** `domains/legal/` has no `__init__.py`/`SPEC` yet, so the
  domain is intentionally not discoverable. Building it (schema with
  `family_field`, languages, sources, `qac_plans`, `attributions`, and
  `prompts_package = "clir_bench.domains.legal.qac.prompts"`) is the next step.
