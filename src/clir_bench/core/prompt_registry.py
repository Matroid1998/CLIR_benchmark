"""Publish local MLflow prompt versions and load immutable, self-contained run bundles.

Runtime reads pinned text from CLIR_PROMPT_MANIFEST or the local active manifest, never a moving alias.
The CLI is the explicit synchronization boundary between editable files and runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from functools import cache
from importlib import resources
from pathlib import Path

PREFIX = "clir_bench.domains.legal.qac.prompts_"
MODES = {
    "eurlex": ("fact_pattern", "lookup", "conceptual",
               "comparison", "claim_verification", "source_finding"),
    "un": ("lookup", "practitioner", "conceptual",
           "comparison", "claim_verification", "source_finding"),
}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def bundle_digest(prompts: dict[str, str]) -> str:
    return sha256(json.dumps(prompts, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def logical_key(package: str, parts: tuple[str, ...]) -> str | None:
    """Map package resources to the logical keys used by screening snapshots."""
    if not package.startswith(PREFIX) or package[len(PREFIX):] not in MODES:
        return None
    source = package[len(PREFIX):]
    path = "/".join(parts)
    if path in ("decider/generator.txt", "decider/jev.json", "decider/jev_eligibility.json"):
        return f"{source}/decider/{Path(path).stem}"
    if len(parts) == 3 and parts[0] == "generation" and parts[2].endswith(".txt"):
        mode = "practitioner" if parts[1] == "practitioners" else parts[1]
        lang = parts[2][:-4]
        return f"{source}/generation/{mode}" + (f"/{lang}" if lang != "en" else "")
    if len(parts) == 2 and parts[0] == "verifiers" and parts[1].endswith("_batch.txt"):
        mode = parts[1][:-10]
        if mode == "faithfulness":
            return f"{source}/faithfulness"
        return f"{source}/quality/{'practitioner' if mode == 'practitioners' else mode}"
    # An explicit bundle must not quietly load an unregistered legal template.
    return f"{source}/resource/{path}"


def local_parts(package: str, parts: tuple[str, ...]) -> tuple[str, ...]:
    """The old UN resource name remains readable; chemistry keeps semantic."""
    if package == PREFIX + "un":
        return tuple({"semantic": "conceptual", "semantic_batch.txt":
                      "conceptual_batch.txt"}.get(part, part) for part in parts)
    return parts


def manifest_key(key: str, entries: dict) -> str | None:
    """Prefer exact historical keys; alias only the renamed UN mode."""
    if key in entries:
        return key
    parts = key.split("/")
    if len(parts) >= 3 and parts[0] == "un" and parts[1] in ("generation", "quality"):
        aliases = {"semantic": "conceptual", "conceptual": "semantic"}
        if parts[2] in aliases:
            parts[2] = aliases[parts[2]]
            alias = "/".join(parts)
            if alias in entries:
                return alias
    return None


def prompt_name(key: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", key):
        raise ValueError(f"invalid prompt logical key: {key!r}")
    parts = key.split("/")
    if len(parts) == 2 and parts[1] == "faithfulness":
        key += "/batch"
    # English snapshot keys omit the language; supplemental generation keys can include it.
    has_language = len(parts) == 4 and parts[1] == "generation"
    return "clir-legal-" + key.replace("/", "-") + ("" if has_language else "-en")


def local_legal_prompts() -> dict[str, str]:
    """Snapshot every legal template so activation also supports other languages/modes."""
    result = {}

    def visit(package, node, parts=()):
        for entry in sorted(node.iterdir(), key=lambda value: value.name):
            child_parts = (*parts, entry.name)
            if entry.is_dir():
                visit(package, entry, child_parts)
            elif entry.name.endswith((".txt", ".json")):
                text = entry.read_text(encoding="utf-8")
                result[logical_key(package, child_parts)] = (
                    text if child_parts[0] == "decider" else text.strip())

    for source in MODES:
        package = PREFIX + source
        visit(package, resources.files(package))
    return result


def registry_workspace_root() -> Path:
    current = Path.cwd().resolve()
    for parent in (current, *current.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".clir").is_dir():
            return parent
    return current


def active_manifest_path() -> Path:
    return registry_workspace_root() / ".clir" / "active_prompt_manifest.json"


def selection() -> str | None:
    """Use a pinned snapshot; explicit local mode bypasses automatic activation."""
    manifest = os.environ.get("CLIR_PROMPT_MANIFEST", "").strip()
    source = os.environ.get("CLIR_PROMPT_SOURCE", "").strip()
    if source not in ("", "local"):
        raise ValueError("CLIR_PROMPT_SOURCE must be unset or 'local'")
    if source == "local" and manifest:
        raise ValueError("CLIR_PROMPT_SOURCE=local conflicts with CLIR_PROMPT_MANIFEST")
    if source == "local":
        return None
    if manifest:
        return str(Path(manifest).expanduser().resolve())
    active = active_manifest_path()
    return str(active.resolve()) if active.exists() else None


def validate_manifest(data: dict) -> dict:
    if (not isinstance(data, dict) or data.get("schema_version") != 1
            or data.get("provider") != "mlflow"):
        raise ValueError("unsupported prompt manifest")
    if not all(isinstance(data.get(k), str) and data[k]
               for k in ("bundle", "label", "registry_uri", "bundle_sha256")):
        raise ValueError("prompt manifest is missing bundle metadata")
    entries = data.get("prompts")
    if not isinstance(entries, dict) or not entries:
        raise ValueError("prompt manifest must contain prompts")
    texts = {}
    for key, entry in entries.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("text"), str):
            raise ValueError(f"invalid prompt entry: {key}")  # noqa: TRY004 - malformed JSON data
        if (entry.get("name") != prompt_name(key)
                or type(entry.get("version")) is not int or entry["version"] < 1
                or entry.get("sha256") != sha256(entry["text"])):
            raise ValueError(f"prompt version/name/hash validation failed: {key}")
        texts[key] = entry["text"]
    if data.get("bundle_sha256") != bundle_digest(texts):
        raise ValueError("prompt bundle hash validation failed")
    return data


@cache
def read_manifest(path: str) -> dict:
    """Pin one validated snapshot per path for the duration of a run."""
    return validate_manifest(json.loads(Path(path).read_text(encoding="utf-8")))


def resolve_prompt(key: str, path: str) -> str:
    entries = read_manifest(path)["prompts"]
    resolved = manifest_key(key, entries)
    if resolved is None:
        raise ValueError(f"selected prompt bundle is missing {key}; local fallback is disabled")
    return entries[resolved]["text"]


def manifest_metadata() -> dict | None:
    path = selection()
    if not path:
        return None
    manifest = read_manifest(path)
    return {key: manifest[key] for key in (
        "schema_version", "provider", "bundle", "label", "registry_uri", "bundle_sha256")} | {
        "prompts": {key: {k: entry[k] for k in ("name", "version", "sha256")}
                    for key, entry in manifest["prompts"].items()}}


class MLflowRegistry:
    """Account-free MLflow Prompt Registry backed by a local SQLite database."""

    def __init__(self, *, registry_uri=None):
        uri = registry_uri or os.environ.get("CLIR_PROMPT_REGISTRY_URI")
        if not uri:
            uri = "sqlite:///" + str((registry_workspace_root() / ".clir" / "prompts.db").resolve())
        if not uri.startswith("sqlite:///") or uri == "sqlite:///:memory:":
            raise ValueError("Prompt registry requires a persistent sqlite:/// database URI")
        database = Path(uri[len("sqlite:///"):]).expanduser().resolve()
        database.parent.mkdir(parents=True, exist_ok=True)
        self.registry_uri = "sqlite:///" + str(database)
        try:
            from mlflow import MlflowClient
        except ImportError:
            raise RuntimeError("Install prompt registry dependencies with uv sync --extra prompts") from None
        self._client = MlflowClient(tracking_uri=self.registry_uri, registry_uri=self.registry_uri)

    def get(self, name, *, label=None, version=None):
        if version is not None:
            return self._client.load_prompt(name, version=version, allow_missing=True,
                                            cache_ttl_seconds=0)
        if not label:
            raise ValueError("An explicit version or alias is required")
        return self._client.load_prompt(f"prompts:/{name}@{label}", allow_missing=True,
                                        cache_ttl_seconds=0)

    @staticmethod
    def _verify(remote, name, text, *, version=None):
        if (remote is None or remote.name != name or remote.template != text
                or not isinstance(remote.version, int) or remote.version < 1
                or (version is not None and remote.version != version)):
            raise ValueError(f"MLflow prompt content/version mismatch: {name}")
        return remote

    @staticmethod
    def _check_label(label):
        if (not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", label)
                or label.lower() == "latest" or re.fullmatch(r"v[0-9]+", label)):
            raise ValueError("Use an explicit non-reserved alias of letters, digits, '_' or '-'")

    def publish(self, prompts: dict[str, str], *, bundle: str, label: str) -> dict:
        self._check_label(label)
        if not bundle:
            raise ValueError("bundle is required")
        if (not isinstance(prompts, dict) or not prompts
                or not all(isinstance(v, str) and v.strip() for v in prompts.values())):
            raise ValueError("prompts must be a nonempty mapping of keys to text")
        if len({prompt_name(key) for key in prompts}) != len(prompts):
            raise ValueError("multiple logical keys map to the same MLflow prompt name")
        digest = bundle_digest(prompts)
        existing = {}
        # Check every experiment alias before writing any versions; never silently move one.
        for key, text in sorted(prompts.items()):
            name = prompt_name(key)
            remote = self.get(name, label=label)
            if remote is not None:
                self._verify(remote, name, text)
            existing[key] = remote
        entries = {}
        for key, text in sorted(prompts.items()):
            name = prompt_name(key)
            remote = existing[key]
            if remote is None:
                remote = self._client.register_prompt(
                    name=name, template=text,
                    commit_message=f"CLIR {bundle}: {sha256(text)}",
                    tags={"clir.logical_key": key, "clir.bundle": bundle,
                          "clir.sha256": sha256(text), "clir.bundle_sha256": digest})
                self._client.set_prompt_alias(name, label, remote.version)
            self._verify(remote, name, text)
            version = remote.version
            self._verify(self.get(name, version=version), name, text, version=version)
            entries[key] = {"name": name, "version": version,
                            "sha256": sha256(text), "text": text}
        return validate_manifest({"schema_version": 1, "provider": "mlflow",
                                  "bundle": bundle, "label": label,
                                  "registry_uri": self.registry_uri,
                                  "bundle_sha256": digest, "prompts": entries})

    def activate(self, manifest: dict, *, label: str, output: Path | None = None):
        validate_manifest(manifest)
        self._check_label(label)
        if manifest["registry_uri"] != self.registry_uri:
            raise ValueError("manifest registry differs from the configured prompt registry")
        for entry in manifest["prompts"].values():
            self._verify(self.get(entry["name"], version=entry["version"]), entry["name"],
                         entry["text"], version=entry["version"])
        for entry in manifest["prompts"].values():
            self._client.set_prompt_alias(entry["name"], label, entry["version"])
            self._verify(self.get(entry["name"], label=label), entry["name"], entry["text"],
                         version=entry["version"])
        path = output or active_manifest_path()
        _atomic_manifest(path, manifest)
        read_manifest.cache_clear()
        return path


def write_manifest(path: Path, manifest: dict):
    """Never overwrite an existing run snapshot with a different bundle."""
    validate_manifest(manifest)
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != manifest:
            raise ValueError(f"refusing to replace a different prompt manifest: {path}")
        return
    _atomic_manifest(path, manifest)


def _atomic_manifest(path: Path, manifest: dict):
    content = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    from dotenv import load_dotenv
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("publish", "sync"):
        command = commands.add_parser(name, help="Publish saved text" if name == "publish"
                                      else "Publish all current EUR-Lex and UN prompt templates")
        if name == "publish":
            command.add_argument("--prompts", type=Path, required=True)
        command.add_argument("--registry-uri", help="Local sqlite:/// registry, default .clir/prompts.db")
        command.add_argument("--bundle", required=True)
        command.add_argument("--label", required=True)
        command.add_argument("--output", type=Path, required=True)
    activate = commands.add_parser("activate", help="Move an explicit deployment label")
    activate.add_argument("--manifest", type=Path, required=True)
    activate.add_argument("--label", required=True)
    activate.add_argument("--registry-uri")
    activate.add_argument("--output", type=Path, help="Default .clir/active_prompt_manifest.json")
    args = parser.parse_args(argv)
    if args.command == "activate":
        manifest = read_manifest(str(args.manifest.resolve()))
        registry = MLflowRegistry(registry_uri=args.registry_uri or manifest["registry_uri"])
        path = registry.activate(manifest, label=args.label, output=args.output)
        print(f"Activated {len(manifest['prompts'])} pinned versions as {args.label}: {path}")
    else:
        registry = MLflowRegistry(registry_uri=args.registry_uri)
        prompts = (json.loads(args.prompts.read_text(encoding="utf-8"))
                   if args.command == "publish" else local_legal_prompts())
        manifest = registry.publish(prompts, bundle=args.bundle, label=args.label)
        write_manifest(args.output, manifest)
        print(f"Pinned {len(prompts)} MLflow prompts in {args.output.resolve()}")


if __name__ == "__main__":
    main()
