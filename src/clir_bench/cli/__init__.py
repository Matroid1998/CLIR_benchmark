"""
Command-line entry point.

Replaces a single argparse namespace of ~80 mutually-exclusive boolean flags
dispatched through an if/return chain whose *order* silently encoded command
precedence. Here commands are real subcommands: exclusive by construction, with
their own options, discoverable through ``--help``.

The domain is resolved before the command parser is built, because a domain
contributes its own command groups (chemistry adds alias-graph and code-switch;
a legal domain would add whatever it needs).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from clir_bench import domains
from clir_bench.core.config import Settings, find_config_file, load_settings
from clir_bench.core.context import AppContext
from clir_bench.cli import analyze, corpus, evaluate, ingest, meta, publish, qac, runs

# Core command groups, in the order they appear in ``--help``.
CORE_GROUPS = (meta, ingest, corpus, qac, publish, evaluate, analyze, runs)

# Names a domain may not claim, so a domain can never shadow a core command.
RESERVED_GROUPS = frozenset(
    {"domains", "config", "ingest", "corpus", "qac", "publish", "eval", "analyze", "runs"}
)


def build_parser(context: Optional[AppContext], domain_module=None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clir",
        description="Build and evaluate multilingual CLIR benchmarks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Domains are selected with --domain (or default_domain in clir.toml).\n"
            "Run `clir domains` to see what is installed."
        ),
    )
    parser.add_argument("--domain", help="Domain to operate on (default: from clir.toml)")
    parser.add_argument("--config", type=Path, help="Path to clir.toml")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    for module in CORE_GROUPS:
        module.register(subparsers, context)

    if context is not None and domain_module is not None:
        register = getattr(domain_module, "register_cli", None)
        if callable(register):
            register(DomainRegistrar(subparsers), context)

    return parser


class DomainRegistrar:
    """Handed to a domain's ``register_cli`` so it can mount its own commands.

    A domain adds source subcommands under the core ``ingest`` group and may
    mount whole groups of its own (chemistry adds alias-graph and code-switch).
    """

    def __init__(self, subparsers: argparse._SubParsersAction) -> None:
        self._subparsers = subparsers

    def ingest_source(self, name: str, help: str = "") -> argparse.ArgumentParser:
        """Add a ``clir ingest <source>`` subcommand."""
        return ingest.source_subparsers().add_parser(name, help=help)

    def group(self, name: str, help: str = "") -> argparse._SubParsersAction:
        """Add a domain command group and return its subparser factory."""
        if name in RESERVED_GROUPS:
            raise ValueError(
                f"domain command group {name!r} collides with a core command; pick another name"
            )
        parser = self._subparsers.add_parser(name, help=help)
        return parser.add_subparsers(dest=f"{name}_command", metavar="<subcommand>")

    def command(self, name: str, help: str = "") -> argparse.ArgumentParser:
        """Add a single top-level domain command."""
        if name in RESERVED_GROUPS:
            raise ValueError(f"domain command {name!r} collides with a core command")
        return self._subparsers.add_parser(name, help=help)


def _resolve_domain(settings: Settings, requested: Optional[str]) -> Optional[str]:
    name = requested or settings.default_domain or domains.default_domain()
    return name or None


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    # Phase one: settings and domain only, so the real parser can include the
    # domain's commands. Unknown args are ignored here and parsed properly below.
    bootstrap = argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument("--domain")
    bootstrap.add_argument("--config", type=Path)
    known, _ = bootstrap.parse_known_args(args)

    config_path = known.config or find_config_file()
    settings = load_settings(config_path)
    _load_env(settings.project_root)

    domain_name = _resolve_domain(settings, known.domain)
    context: Optional[AppContext] = None
    domain_module = None
    if domain_name:
        try:
            domain_module = domains.load_module(domain_name)
            context = AppContext.build(settings, domains.load(domain_name))
        except domains.DomainNotFound as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    parser = build_parser(context, domain_module)
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    handler = getattr(parsed, "handler", None)
    if handler is None:
        # A group was named without a subcommand.
        parser.parse_args([parsed.command, "--help"])
        return 2

    if getattr(parsed, "needs_domain", True) and context is None:
        available = ", ".join(domains.available()) or "(none installed)"
        print(
            "error: no domain selected. Pass --domain NAME or set default_domain in "
            f"clir.toml. Available: {available}",
            file=sys.stderr,
        )
        return 2

    try:
        return int(handler(parsed, context) or 0)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
    except (FileNotFoundError, KeyError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        if parsed.verbose:
            raise
        return 1


def _load_env(project_root: Path) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover
        return
    load_dotenv(project_root / ".env")


__all__ = ["DomainRegistrar", "build_parser", "main"]
