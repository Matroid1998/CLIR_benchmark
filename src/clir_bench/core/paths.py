"""
Workspace: logical names to concrete paths.

The old ``PipelinePaths`` hardcoded chemistry directory names (``google_patents``,
``EPO``, ``chebi``, ``alias_graph``) as dataclass fields, so the path registry
could not describe a second domain. Here a domain declares ``data_layout`` --
logical key to relative path -- and the workspace resolves keys against the data
root, letting the user override any single key in clir.toml.

Layout keys deliberately reproduce the legacy on-disk names, so an existing
``data/`` tree works unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from clir_bench.core.domain import DomainSpec, SourceSpec


@dataclass(frozen=True)
class Workspace:
    """Resolves a domain's logical paths under the data and reports roots."""

    data_dir: Path
    reports_dir: Path
    domain: DomainSpec
    overrides: Mapping[str, str]

    @classmethod
    def build(
        cls,
        *,
        data_dir: Path,
        reports_dir: Path,
        domain: DomainSpec,
        overrides: Optional[Mapping[str, Any]] = None,
    ) -> "Workspace":
        raw = (overrides or {}).get("paths", {}) or {}
        return cls(
            data_dir=Path(data_dir),
            reports_dir=Path(reports_dir),
            domain=domain,
            overrides={str(k): str(v) for k, v in raw.items()},
        )

    # -- data paths --------------------------------------------------------- #

    def data(self, key: str) -> Path:
        """Absolute path for a ``data_layout`` key (or a user override)."""
        relative = self.overrides.get(key) or self.domain.data_layout.get(key)
        if relative is None:
            known = ", ".join(sorted(self.domain.data_layout)) or "(none declared)"
            raise KeyError(
                f"domain {self.domain.name!r} declares no data_layout key {key!r}; known keys: {known}"
            )
        path = Path(relative).expanduser()
        return path if path.is_absolute() else (self.data_dir / path)

    def corpus_csv(self, source: str | SourceSpec) -> Path:
        spec = source if isinstance(source, SourceSpec) else self.domain.source(source)
        return self.data_dir / spec.corpus_relpath

    def qac_dir(self, source: str | SourceSpec) -> Path:
        spec = source if isinstance(source, SourceSpec) else self.domain.source(source)
        return self.data_dir / spec.qac_dir_relpath

    # -- report paths ------------------------------------------------------- #

    @property
    def runs_dir(self) -> Path:
        return self.reports_dir / "runs"

    def report(self, *parts: str) -> Path:
        return self.reports_dir.joinpath(*parts)

    def ensure(self, path: Path) -> Path:
        """Create ``path``'s parent directory and return the path unchanged."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_dir(self, path: Path) -> Path:
        Path(path).mkdir(parents=True, exist_ok=True)
        return path


__all__ = ["Workspace"]
