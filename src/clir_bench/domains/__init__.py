"""
Domain discovery.

The only bridge between the core and the domains. ``available()`` lists domain
packages *without importing them*, so `clir domains` never pulls in networkx or
BigQuery; ``load()`` imports just the one selected.

Adding a domain is creating a subpackage here that exposes ``SPEC``. No file in
this module changes.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Optional

from clir_bench.core.domain import DomainSpec

__all__ = ["available", "load", "load_module", "DomainNotFound"]


class DomainNotFound(LookupError):
    """Raised when a requested domain package does not exist."""


def available() -> tuple[str, ...]:
    """Names of installed domains, discovered by scanning subpackages."""
    return tuple(
        sorted(
            module.name
            for module in pkgutil.iter_modules(__path__)
            if module.ispkg and not module.name.startswith("_")
        )
    )


def load_module(name: str) -> ModuleType:
    if name not in available():
        raise DomainNotFound(
            f"unknown domain {name!r}; available: {', '.join(available()) or '(none)'}"
        )
    return importlib.import_module(f"{__name__}.{name}")


def load(name: str) -> DomainSpec:
    """Import a domain package and return its ``SPEC``."""
    module = load_module(name)
    spec = getattr(module, "SPEC", None)
    if not isinstance(spec, DomainSpec):
        raise DomainNotFound(
            f"domain {name!r} does not expose a DomainSpec as module attribute 'SPEC'"
        )
    return spec


def default_domain(preferred: Optional[str] = None) -> str:
    """The configured domain, or the only installed one when unambiguous."""
    if preferred:
        return preferred
    names = available()
    if len(names) == 1:
        return names[0]
    return ""
