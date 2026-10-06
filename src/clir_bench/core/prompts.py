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
from functools import cache
from importlib import resources

from . import prompt_registry


def load_prompt(package: str, *parts: str) -> str:
    """Read a pinned legal prompt or a local package resource."""
    key = prompt_registry.logical_key(package, parts)
    manifest = prompt_registry.selection() if key else None
    if manifest:
        return prompt_registry.resolve_prompt(key, manifest)
    return _load_local_prompt(package, *prompt_registry.local_parts(package, parts))


@cache
def _load_local_prompt(package: str, *parts: str) -> str:
    resource = resources.files(package)
    for part in parts:
        resource = resource.joinpath(part)
    try:
        text = resource.read_text(encoding="utf-8")
        return text if parts and parts[0] == "decider" else text.strip()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"prompt not found: {package}/{'/'.join(parts)}"
        ) from exc


def _clear_prompt_cache():
    _load_local_prompt.cache_clear()
    prompt_registry.read_manifest.cache_clear()


load_prompt.cache_clear = _clear_prompt_cache


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
        key = prompt_registry.logical_key(self.package, parts)
        manifest = prompt_registry.selection() if key else None
        if manifest:
            # An existence probe may return False without loading a local substitute.
            # Validate first: a corrupt bundle must not masquerade as a missing file.
            return prompt_registry.manifest_key(key, prompt_registry.read_manifest(manifest)["prompts"]) is not None
        try:
            load_prompt(self.package, *parts)
        except (FileNotFoundError, ModuleNotFoundError):
            return False
        return True

    def available_languages(self, mode: str) -> tuple[str, ...]:
        """Languages with a generation prompt for ``mode``."""
        key = prompt_registry.logical_key(self.package, (self.generation_dir, mode, "en.txt"))
        manifest = prompt_registry.selection() if key else None
        if manifest:
            entries = prompt_registry.read_manifest(manifest)["prompts"]
            languages = {parts[3] if len(parts) == 4 else "en"
                         for entry in entries
                         if len(parts := entry.split("/")) in (3, 4)
                         and parts[1] == "generation"}
            return tuple(sorted(language for language in languages
                                if prompt_registry.manifest_key(
                                    prompt_registry.logical_key(
                                        self.package, (self.generation_dir, mode, f"{language}.txt")),
                                    entries) is not None))
        try:
            parts = prompt_registry.local_parts(self.package, (self.generation_dir, mode))
            directory = resources.files(self.package).joinpath(*parts)
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
