"""Commands that describe the installation itself."""

from __future__ import annotations

import argparse
import json
from typing import Optional

from clir_bench import domains
from clir_bench.core.context import AppContext


def register(subparsers: argparse._SubParsersAction, context: Optional[AppContext]) -> None:
    listing = subparsers.add_parser("domains", help="List installed domains")
    listing.set_defaults(handler=_domains, needs_domain=False)

    config = subparsers.add_parser("config", help="Show resolved configuration")
    config.add_argument("--json", action="store_true", help="Machine-readable output")
    config.set_defaults(handler=_config, needs_domain=False)


def _domains(args: argparse.Namespace, context: Optional[AppContext]) -> int:
    names = domains.available()
    if not names:
        print("No domains installed.")
        return 0
    active = context.domain.name if context else ""
    for name in names:
        try:
            spec = domains.load(name)
            marker = "*" if name == active else " "
            sources = ", ".join(spec.source_names) or "none"
            print(f" {marker} {name:<16} {spec.title}")
            print(f"   {' ' * 16} sources: {sources}; languages: {', '.join(spec.languages.working)}")
        except Exception as exc:  # noqa: BLE001 - a broken domain must not hide the others
            print(f"   {name:<16} (failed to load: {exc})")
    if active:
        print("\n* = active domain")
    return 0


def _config(args: argparse.Namespace, context: Optional[AppContext]) -> int:
    if context is None:
        print("No domain selected; showing global settings only.")
        return 0
    settings = context.settings
    payload = {
        "domain": context.domain.name,
        "project_root": str(settings.project_root),
        "data_dir": str(settings.data_dir),
        "reports_dir": str(settings.reports_dir),
        "llm": {
            "generation_model": settings.llm.generation_model,
            "verifier_model": settings.llm.verifier_model,
            "concept_verifier_model": settings.llm.concept_verifier_model,
        },
        "eval": {
            "corpus_repo": settings.eval.corpus_repo,
            "variant": settings.eval.variant,
            "allow_local_models": settings.eval.allow_local_models,
        },
        "domain_settings": dict(context.domain_settings),
        "sources": {
            source.name: {
                "languages": list(source.languages),
                "corpus": str(context.workspace.corpus_csv(source)),
                "attribution": source.attribution_key,
            }
            for source in context.domain.sources
        },
    }
    if args.json:
        print(json.dumps(payload, indent=2, default=str))
        return 0

    print(f"domain      {payload['domain']}  ({context.domain.title})")
    print(f"data        {payload['data_dir']}")
    print(f"reports     {payload['reports_dir']}")
    print(f"languages   {', '.join(context.languages.working)}")
    print("\nsources")
    for name, info in payload["sources"].items():
        print(f"  {name:<6} {', '.join(info['languages'])}")
        print(f"         {info['corpus']}")
    print("\nmodels")
    print(f"  generation {payload['llm']['generation_model']}")
    print(f"  verifier   {payload['llm']['verifier_model']}")
    if payload["domain_settings"]:
        print("\ndomain settings")
        for key, value in sorted(payload["domain_settings"].items()):
            if key != "paths":
                print(f"  {key:<22} {value}")
    return 0
