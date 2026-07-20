"""
The ``ingest`` command group.

Core owns the group; the active domain fills it with one subcommand per source,
because sources differ genuinely in what they need (a BigQuery extraction takes
a per-language limit, a bulk-archive ingest takes a batch count). With no domain
subcommands registered, ``clir ingest`` lists what the domain declares.
"""

from __future__ import annotations

import argparse
from typing import Optional

from clir_bench.core.context import AppContext

# Set during register() so the domain registrar can add source subcommands.
_source_subparsers: Optional[argparse._SubParsersAction] = None


def register(subparsers: argparse._SubParsersAction, context: Optional[AppContext]) -> None:
    global _source_subparsers
    parser = subparsers.add_parser("ingest", help="Fetch documents from a source into the corpus")
    _source_subparsers = parser.add_subparsers(dest="source", metavar="<source>")
    parser.set_defaults(handler=_list_sources, needs_domain=True)


def source_subparsers() -> argparse._SubParsersAction:
    """The subparser factory domains add their per-source commands to."""
    if _source_subparsers is None:
        raise RuntimeError("ingest group has not been registered yet")
    return _source_subparsers


def _list_sources(args: argparse.Namespace, context: AppContext) -> int:
    print(f"Sources declared by domain {context.domain.name!r}:\n")
    for source in context.domain.sources:
        corpus = context.workspace.corpus_csv(source)
        exists = "present" if corpus.exists() else "not yet built"
        print(f"  {source.name:<8} {source.description or source.name}")
        print(f"  {'':8} languages: {', '.join(source.languages)}")
        print(f"  {'':8} corpus:    {corpus} ({exists})")
    print("\nRun `clir ingest <source> --help` for a source's options.")
    return 0
