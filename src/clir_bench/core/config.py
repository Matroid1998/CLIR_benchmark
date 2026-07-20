"""
Settings and the single place defaults are resolved.

The old pipeline kept every option's default in three places (dataclass field,
argparse ``default=``, and the constructor call that rebuilt the config), so a
change had to be made three times and argparse silently won. Here there is one
precedence chain, applied once:

    CLI flag  >  environment  >  clir.toml  >  domain defaults  >  code default

Commands read what they need off ``AppContext``; there is no god-object holding
every flag of every command.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping, Optional

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]

CONFIG_FILENAME = "clir.toml"
CONFIG_ENV_VAR = "CLIR_CONFIG"


def resolve(*candidates: Any, default: Any = None) -> Any:
    """First non-None candidate, else ``default``.

    The one defaulting mechanism in the codebase. Call it as
    ``resolve(cli_value, toml_value, domain_default, default=...)``.
    """
    for value in candidates:
        if value is not None:
            return value
    return default


@dataclass(frozen=True)
class LLMSettings:
    """Model ids and transport knobs for generation and grading.

    The verifier configuration is the comparability contract across every
    dataset built by this project: changing it changes what "graded" means, so
    it lives in exactly one place.
    """

    generation_model: str = "gpt-5-mini"
    verifier_model: str = "anthropic/claude-sonnet-4.6"
    # The alias-graph/progressive family graded on 4.5; kept distinct on purpose
    # so re-running those pipelines reproduces their published scores.
    concept_verifier_model: str = "anthropic/claude-sonnet-4.5"
    generation_reasoning_effort: str = "medium"
    grading_reasoning_effort: str = "low"
    thinking_budget_tokens: int = 8000
    thinking_max_tokens: int = 12000
    retries: int = 3


@dataclass(frozen=True)
class EvalSettings:
    """Defaults for the retrieval evaluation harness."""

    corpus_repo: str = ""
    variant: str = "multilingual"
    batch_size: int = 32
    main_score: str = "recall_at_10"
    # Running embedding models is opt-in: the default flow emits a command for
    # the compute node instead of loading models on the workstation.
    allow_local_models: bool = False
    models: tuple[str, ...] = ()


@dataclass(frozen=True)
class Settings:
    """Global, domain-independent settings."""

    project_root: Path
    data_dir: Path
    reports_dir: Path
    cluster_dir: Path
    default_domain: str = ""
    llm: LLMSettings = field(default_factory=LLMSettings)
    eval: EvalSettings = field(default_factory=EvalSettings)
    # Raw [domains.<name>] tables, merged over DomainSpec.defaults at load time.
    domain_overrides: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def overrides_for(self, domain_name: str) -> Mapping[str, Any]:
        return self.domain_overrides.get(domain_name, {})


def find_config_file(start: Optional[Path] = None) -> Optional[Path]:
    """Locate clir.toml: $CLIR_CONFIG, else nearest one at or above ``start``."""
    from_env = os.environ.get(CONFIG_ENV_VAR)
    if from_env:
        path = Path(from_env).expanduser()
        return path if path.exists() else None
    current = (start or Path.cwd()).resolve()
    for directory in (current, *current.parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.exists():
            return candidate
    return None


def _read_toml(path: Optional[Path]) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_settings(
    config_path: Optional[Path] = None,
    *,
    project_root: Optional[Path] = None,
) -> Settings:
    """Build :class:`Settings` from clir.toml plus environment overrides."""
    path = config_path or find_config_file()
    raw = _read_toml(path)
    root = Path(project_root or (path.parent if path else Path.cwd())).resolve()

    paths_table = raw.get("paths", {})
    llm_table = raw.get("llm", {})
    eval_table = raw.get("eval", {})

    def _dir(key: str, fallback: str) -> Path:
        value = os.environ.get(f"CLIR_{key.upper()}_DIR") or paths_table.get(key) or fallback
        candidate = Path(str(value)).expanduser()
        return candidate if candidate.is_absolute() else (root / candidate)

    llm = LLMSettings(**{k: v for k, v in llm_table.items() if k in LLMSettings.__dataclass_fields__})
    eval_fields = {k: v for k, v in eval_table.items() if k in EvalSettings.__dataclass_fields__}
    if "models" in eval_fields:
        eval_fields["models"] = tuple(eval_fields["models"])
    evaluation = EvalSettings(**eval_fields)

    return Settings(
        project_root=root,
        data_dir=_dir("data", "data"),
        reports_dir=_dir("reports", "reports"),
        cluster_dir=_dir("cluster", "cluster"),
        default_domain=os.environ.get("CLIR_DOMAIN") or raw.get("default_domain", ""),
        llm=llm,
        eval=evaluation,
        domain_overrides=raw.get("domains", {}),
    )


def merged_domain_settings(
    settings: Settings, domain_name: str, domain_defaults: Mapping[str, Any]
) -> dict[str, Any]:
    """Domain defaults with the user's ``[domains.<name>]`` table layered on top."""
    merged = dict(domain_defaults)
    merged.update(settings.overrides_for(domain_name))
    return merged


__all__ = [
    "CONFIG_FILENAME",
    "EvalSettings",
    "LLMSettings",
    "Settings",
    "find_config_file",
    "load_settings",
    "merged_domain_settings",
    "replace",
    "resolve",
]
