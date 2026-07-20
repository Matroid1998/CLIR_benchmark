"""
Chemistry patents domain.

Exposes the two symbols the loader looks for: ``SPEC`` (what the domain is) and
``register_cli`` (the commands it adds).
"""

from clir_bench.domains.chem_patents.domain import SPEC


def register_cli(registrar, context) -> None:
    """Mount this domain's commands. Imported lazily to keep startup cheap."""
    from clir_bench.domains.chem_patents.cli import register_cli as _register

    _register(registrar, context)


__all__ = ["SPEC", "register_cli"]
