"""
Guards on the architecture's invariants.

These are the properties that make a second domain additive. They are cheap to
check and expensive to notice by reading, so they are tests rather than prose.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "clir_bench"

# Packages that must stay domain-independent.
DOMAIN_FREE_PACKAGES = ("core", "evaluation", "analysis")


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def _python_files(package: str) -> list[Path]:
    return sorted((SRC / package).rglob("*.py"))


@pytest.mark.parametrize("package", DOMAIN_FREE_PACKAGES)
def test_domain_independent_packages_never_import_a_domain(package: str) -> None:
    """The core cannot name a domain, so chemistry cannot leak into it."""
    offenders = [
        f"{path.relative_to(SRC)} imports {module}"
        for path in _python_files(package)
        for module in _imported_modules(path)
        if module.startswith("clir_bench.domains")
    ]
    assert not offenders, "domain-independent code imported a domain:\n  " + "\n  ".join(offenders)


def _docstrings(tree: ast.Module) -> set[int]:
    """Node ids of every docstring, which may discuss the domain freely."""
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    ids.add(id(body[0].value))
    return ids


@pytest.mark.parametrize("package", DOMAIN_FREE_PACKAGES)
def test_domain_independent_packages_avoid_domain_vocabulary(package: str) -> None:
    """Catch domain words that slip in as values rather than imports.

    A column name like ``publication_number`` hardcoded in core would compile
    fine and quietly assume patents forever -- exactly the failure this layout
    exists to prevent. Docstrings and comments are exempt: explaining the domain
    is useful, depending on it is not.
    """
    forbidden = ("publication_number", "chebi", "ipc_codes", "surechembl")
    offenders = []
    for path in _python_files(package):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        exempt = _docstrings(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in exempt:
                lowered = node.value.lower()
                for word in forbidden:
                    if word in lowered:
                        offenders.append(
                            f"{path.relative_to(SRC)}:{node.lineno} has {word!r} in a string literal"
                        )
            elif isinstance(node, ast.Name) and any(w in node.id.lower() for w in forbidden):
                offenders.append(f"{path.relative_to(SRC)}:{node.lineno} names {node.id!r}")
    assert not offenders, "domain vocabulary in domain-independent code:\n  " + "\n  ".join(offenders)


def test_no_local_package_shadows_the_mteb_library() -> None:
    """A local package named ``mteb`` would shadow the library it wraps."""
    assert not (SRC / "mteb").exists(), "a local 'mteb' package would break `import mteb`"


def test_importing_the_package_is_cheap() -> None:
    """Importing clir_bench must not drag in the model or cloud stacks."""
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, clir_bench;"
            "heavy = {'torch', 'mteb', 'sentence_transformers', 'networkx', 'google.cloud'};"
            "loaded = heavy & set(sys.modules);"
            "print(','.join(sorted(loaded)))",
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(SRC.parent), "PATH": "/usr/bin:/bin"},
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not result.stdout.strip(), f"importing clir_bench loaded: {result.stdout.strip()}"
