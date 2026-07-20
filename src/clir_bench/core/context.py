"""
AppContext: the object every command receives.

Three small frozen pieces -- settings, the active domain, the workspace -- in
place of the old ~90-field ``PipelineConfig`` that every command had to share.
Per-command options stay in that command's own argparse namespace.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from clir_bench.core.config import Settings, merged_domain_settings
from clir_bench.core.domain import DomainSpec
from clir_bench.core.paths import Workspace


@dataclass(frozen=True)
class AppContext:
    settings: Settings
    domain: DomainSpec
    workspace: Workspace
    # DomainSpec.defaults with the user's [domains.<name>] table layered on top.
    domain_settings: Mapping[str, Any]

    @classmethod
    def build(cls, settings: Settings, domain: DomainSpec) -> "AppContext":
        overrides = settings.overrides_for(domain.name)
        return cls(
            settings=settings,
            domain=domain,
            workspace=Workspace.build(
                data_dir=settings.data_dir,
                reports_dir=settings.reports_dir,
                domain=domain,
                overrides=overrides,
            ),
            domain_settings=merged_domain_settings(settings, domain.name, domain.defaults),
        )

    def setting(self, key: str, default: Any = None) -> Any:
        """A domain-level default/override (HF repo ids, model choices, knobs)."""
        return self.domain_settings.get(key, default)

    @property
    def schema(self):
        return self.domain.schema

    @property
    def languages(self):
        return self.domain.languages

    @property
    def project_root(self) -> Path:
        return self.settings.project_root

    def hf_repo(self, key: str, override: Optional[str] = None) -> str:
        """Resolve an HF repo id: explicit flag wins, else the domain setting."""
        value = override or self.setting(key, "")
        return _normalize_hf_repo(str(value or ""))


def _normalize_hf_repo(value: str) -> str:
    """Accept a full hub URL or a bare ``owner/name``."""
    raw = value.strip()
    marker = "huggingface.co/datasets/"
    if marker in raw:
        raw = raw.split(marker, 1)[1]
    return raw.strip().strip("/")


__all__ = ["AppContext"]
