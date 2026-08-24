# Blind LLM re-annotation of the question-generation model comparison

Replicates the human annotation protocol (30 chemistry patent documents × 6 anonymised
generators, slot order randomised per document, same Argilla rubric) with two LLM
annotators, then compares all three annotators. Run on 2026-08-22.

| annotator | transport | model id | reasoning | blind protocol |
|---|---|---|---|---|
| Claude Fable 5 | Claude Code workflow subagents, one per document | `claude-fable-5` (29 docs); `claude-opus-5` harness fallback on 1 doc, see `claude_pass_fallback.json` | effort=high | agent reads only its own anonymised prompt file (`prompts_claude/<doc>.md`); tool use audited in `claude_pass_audit.json` (30/30 clean) |
| GPT-5.6 Sol | OpenAI chat completions, strict JSON schema | `gpt-5.6-sol` | reasoning_effort=high | system = `rubric.md`, user = anonymised record |

Neither annotator was told which systems generated the questions; prompts contain only
anonymised Q1–Q6 slots. Each pass has its **own** random slot order (`build_passes.py`,
seeds 20260822 / 20260823), so position effects are independent across annotators.
`pass_<name>_slot_mapping.json` is the private de-anonymisation key of each pass.

## Files

- `rubric.md` — the annotation guidelines + criterion definitions (verbatim from the Argilla dataset) given to both LLMs
- `build_passes.py` → `pass_<name>_records.json` (anonymised records) + private slot mappings
- `render.py` → `prompts_<name>/<doc>.md`, `schemas.json` (technical / semantic output schema)
- `run_gpt.py` → `results_gpt/<doc>.json` (prompt, raw usage, validated output)
- `extract_claude.py` → `results_claude/<doc>.json` from the workflow transcripts + `claude_pass_audit.json`
- `run_openrouter_claude.py` — fallback transport used only to diagnose the Fable content filter
- `analyze.py` → `analysis/` (tables, figures, notes, disagreements; see `analysis/summary.md`)

Regenerate the analysis: `uv run python reports/qa_generation_model_comparison/llm_annotation/analyze.py`
