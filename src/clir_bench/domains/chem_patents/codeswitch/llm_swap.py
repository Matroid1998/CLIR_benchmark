"""
Variant E: the non-chemistry control swap.

The only code-switch variant that needs a model. It asks for one ordinary,
non-chemistry noun that appears in the passage and its translation into a target
language; the builder then swaps every occurrence. Variant E exists to separate
"retrieval broke because a term changed language" from "retrieval broke because
a CHEMISTRY term changed language" -- so the model's pick must not be a
chemistry term, and a pick that lands on the avoid list is discarded rather than
retried, because a model that ignored the instruction once will usually ignore
it again.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

from clir_bench.core.context import AppContext
from clir_bench.core.llm import chat, client_for, parse_json_object
from clir_bench.core.prompts import PromptPack

PROMPT_PARTS: tuple[str, ...] = ("code_switch", "nonchem_swap.txt")

NonChemSwapper = Callable[[str, Sequence[str], str], Optional[tuple[str, str]]]


def nonchem_swapper(context: AppContext, *, model: Optional[str] = None) -> NonChemSwapper:
    """Build ``swap(doc_text, avoid_terms, target_language) -> (original, replacement)``.

    A closure so the client and prompt are resolved once per build rather than
    once per document.
    """
    settings = context.settings.llm
    model = model or settings.generation_model
    prompts = PromptPack(context.domain.prompts_package)
    prompt = prompts.custom(*PROMPT_PARTS)
    client = client_for(model)
    # The legacy pipeline ran this selection at the shared low effort, not the
    # higher generation effort: it is a lookup, not a writing task.
    effort = settings.grading_reasoning_effort

    def swap(
        text: str, avoid_terms: Sequence[str], target_language: str
    ) -> Optional[tuple[str, str]]:
        language_name = context.languages.name_of(target_language)
        user = (
            f"TARGET LANGUAGE: {language_name}\n"
            f"CHEMISTRY TERMS TO AVOID (never pick any of these): {', '.join(avoid_terms)}\n\n"
            f"PASSAGE:\n{text}"
        )
        raw = chat(
            client,
            model,
            [{"role": "system", "content": prompt}, {"role": "user", "content": user}],
            reasoning_effort=effort,
        )
        data = parse_json_object(raw)
        original = str(data.get("original_term", "")).strip()
        replacement = str(data.get("replacement_term", "")).strip()
        if not original or not replacement:
            return None
        if original.casefold() in {term.casefold() for term in avoid_terms}:
            return None
        return original, replacement

    return swap


__all__ = ["NonChemSwapper", "PROMPT_PARTS", "nonchem_swapper"]
