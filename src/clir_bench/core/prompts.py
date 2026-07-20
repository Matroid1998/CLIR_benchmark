"""
Prompt loading.

All domain knowledge that shapes questions lives in prompt files, so prompts are
the main thing a new domain writes. They are package data loaded through
``importlib.resources`` -- no ``Path(__file__)`` walking, so the package works
installed or from a wheel.

A domain declares ``prompts_package``; a :class:`PromptPack` addresses files
inside it by role. Three copies of a cached file-loader in the old repo collapse
into the cache here.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Optional


@lru_cache(maxsize=None)
def load_prompt(package: str, *parts: str) -> str:
    """Read a prompt file from a package, cached by (package, path)."""
    resource = resources.files(package)
    for part in parts:
        resource = resource.joinpath(part)
    try:
        return resource.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"prompt not found: {package}/{'/'.join(parts)}"
        ) from exc


@dataclass(frozen=True)
class PromptPack:
    """Addresses a domain's prompt files by role.

    Layout under ``package``::

        <generation_dir>/<mode>/<lang>.txt      question generation, per language
        <verifier_dir>/faithfulness_<arity>.txt grounding rubric
        <verifier_dir>/<mode>_<arity>.txt       quality rubric

    ``arity`` is ``batch`` (three candidates, JSON list) or ``single`` (one pair,
    JSON object). The two are separate files with different output contracts and
    must stay separate.
    """

    package: str
    generation_dir: str = "generation"
    verifier_dir: str = "verifiers"

    def generation(self, mode: str, language: str) -> str:
        return load_prompt(self.package, self.generation_dir, mode, f"{language}.txt")

    def faithfulness(self, arity: str = "batch") -> str:
        return load_prompt(self.package, self.verifier_dir, f"faithfulness_{arity}.txt")

    def quality(self, mode: str, arity: str = "batch") -> str:
        return load_prompt(self.package, self.verifier_dir, f"{mode}_{arity}.txt")

    def custom(self, *parts: str) -> str:
        """Any other prompt in the pack (concept queries, code-switch, ...)."""
        return load_prompt(self.package, *parts)

    def has(self, *parts: str) -> bool:
        try:
            load_prompt(self.package, *parts)
        except (FileNotFoundError, ModuleNotFoundError):
            return False
        return True

    def available_languages(self, mode: str) -> tuple[str, ...]:
        """Languages with a generation prompt for ``mode``."""
        try:
            directory = resources.files(self.package).joinpath(self.generation_dir, mode)
            return tuple(
                sorted(
                    entry.name[:-4]
                    for entry in directory.iterdir()
                    if entry.name.endswith(".txt")
                )
            )
        except (FileNotFoundError, ModuleNotFoundError, NotADirectoryError):
            return ()


__all__ = ["PromptPack", "load_prompt"]
