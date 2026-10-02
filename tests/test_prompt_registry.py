"""Actual local MLflow versions, immutable run snapshots, and strict runtime selection."""

import json

import pytest

from clir_bench.core import prompt_registry as registry
from clir_bench.core.prompts import PromptPack, load_prompt
from clir_bench.domains.legal.qac import decider


@pytest.fixture(autouse=True)
def clean_prompt_selection(monkeypatch, tmp_path):
    for key in ("CLIR_PROMPT_MANIFEST", "CLIR_PROMPT_SOURCE", "CLIR_PROMPT_REGISTRY_URI"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("MLFLOW_DISABLE_AGENT_HINT", "1")
    monkeypatch.chdir(tmp_path)
    load_prompt.cache_clear()
    yield
    load_prompt.cache_clear()


@pytest.fixture
def client(tmp_path):
    pytest.importorskip("mlflow")
    pytest.importorskip("alembic")
    return registry.MLflowRegistry(registry_uri="sqlite:///" + str(tmp_path / "registry.db"))


def test_actual_sqlite_versions_and_idempotent_immutable_experiment_alias(client):
    prompts = {"un/generation/practitioner": "Exact text\n", "evaluation/common": "Judge."}
    original = client.publish(prompts, bundle="baseline", label="experiment-baseline")
    assert original["provider"] == "mlflow"
    assert client.publish(prompts, bundle="baseline", label="experiment-baseline") == original
    assert original["prompts"]["un/generation/practitioner"]["version"] == 1
    with pytest.raises(ValueError, match="mismatch"):
        client.publish(prompts | {"un/generation/practitioner": "Changed"},
                       bundle="baseline", label="experiment-baseline")
    changed = client.publish(prompts | {"un/generation/practitioner": "Changed"},
                             bundle="debiased", label="experiment-debiased")
    assert changed["prompts"]["un/generation/practitioner"]["version"] == 2
    old = original["prompts"]["un/generation/practitioner"]
    assert client.get(old["name"], version=old["version"]).template == "Exact text\n"
    assert client.get(old["name"], label="experiment-baseline").version == 1
    assert "/" not in old["name"]


def test_manifest_pins_loaders_and_jev_without_registry_reads(client, tmp_path, monkeypatch):
    jev = '{"questions": {"mode": {"type": "choice"}}}\n'
    prompts = {"un/decider/jev": jev, "un/generation/practitioner": "Pinned generation"}
    manifest = client.publish(prompts, bundle="baseline", label="baseline")
    path = tmp_path / "manifest.json"
    registry.write_manifest(path, manifest)
    monkeypatch.setenv("CLIR_PROMPT_MANIFEST", str(path))
    monkeypatch.setattr(registry.MLflowRegistry, "get", lambda *a, **k: pytest.fail("registry read"))
    pack = PromptPack(registry.PREFIX + "un")
    assert pack.generation("practitioners", "en") == "Pinned generation"
    assert decider.prompt_text("un", "jev") == jev
    assert decider.build_request("un", "jev", "complete source", "ignored")["state"] == "complete source"
    with pytest.raises(ValueError, match="missing un/quality/practitioner"):
        pack.quality("practitioners")
    assert "text" not in registry.manifest_metadata()["prompts"]["un/decider/jev"]


def test_manifest_tamper_and_snapshot_overwrite_are_rejected(client, tmp_path):
    original = client.publish({"un/quality/lookup": "Original"}, bundle="a", label="a")
    path = tmp_path / "manifest.json"
    registry.write_manifest(path, original)
    registry.write_manifest(path, original)
    changed = client.publish({"un/quality/lookup": "Changed"}, bundle="b", label="b")
    with pytest.raises(ValueError, match="refusing to replace"):
        registry.write_manifest(path, changed)
    broken = json.loads(path.read_text())
    broken["prompts"]["un/quality/lookup"]["text"] = "Tampered"
    path.write_text(json.dumps(broken))
    with pytest.raises(ValueError, match="validation failed"):
        registry.read_manifest(str(path))


def test_activation_switches_default_without_changing_pinned_experiment(client, monkeypatch):
    pack = PromptPack(registry.PREFIX + "un")
    first = client.publish({"un/quality/lookup": "First"}, bundle="first", label="first")
    second = client.publish({"un/quality/lookup": "Second"}, bundle="second", label="second")
    client.activate(first, label="production")
    assert pack.quality("lookup") == "First"
    client.activate(second, label="production")
    assert pack.quality("lookup") == "Second"
    assert client.get(registry.prompt_name("un/quality/lookup"), label="first").template == "First"
    monkeypatch.setenv("CLIR_PROMPT_SOURCE", "local")
    assert "Second" != pack.quality("lookup")
    monkeypatch.setenv("CLIR_PROMPT_MANIFEST", str(registry.active_manifest_path()))
    with pytest.raises(ValueError, match="conflicts"):
        pack.quality("lookup")


def test_manifest_path_switch_is_not_hidden_by_prompt_cache(client, tmp_path, monkeypatch):
    pack = PromptPack(registry.PREFIX + "un")
    for label in ("first", "second"):
        path = tmp_path / (label + ".json")
        registry.write_manifest(path, client.publish({"un/quality/lookup": label},
                                                     bundle=label, label=label))
        monkeypatch.setenv("CLIR_PROMPT_MANIFEST", str(path))
        assert pack.quality("lookup") == label


def test_sync_inventory_covers_all_languages_and_legacy_modes():
    prompts = registry.local_legal_prompts()
    assert len(prompts) == 48
    for source in registry.MODES:
        assert prompts[f"{source}/decider/jev"] == decider.prompt_text(source, "jev")
    for language in ("de", "es", "fr", "zh"):
        assert f"eurlex/generation/fact_pattern/{language}" in prompts
        assert f"un/generation/practitioner/{language}" in prompts
    assert "un/generation/technical" in prompts
    assert "un/quality/descriptive" in prompts
    assert len({registry.prompt_name(key) for key in prompts}) == len(prompts)


def test_partial_or_corrupt_active_manifest_never_falls_back(tmp_path):
    active = registry.active_manifest_path()
    active.parent.mkdir()
    active.write_text('{"provider":"mlflow"}')
    with pytest.raises(ValueError, match="unsupported prompt manifest"):
        PromptPack(registry.PREFIX + "un").quality("lookup")


def test_registry_requires_persistent_sqlite_and_nonreserved_aliases(client):
    with pytest.raises(ValueError, match="persistent sqlite"):
        registry.MLflowRegistry(registry_uri="sqlite:///:memory:")
    with pytest.raises(ValueError, match="non-reserved alias"):
        client.publish({"evaluation/common": "test"}, bundle="a", label="latest")


def test_has_probe_reports_absence_but_does_not_mask_corrupt_manifest(client, tmp_path,
                                                                    monkeypatch):
    manifest = client.publish({"un/quality/lookup": "Pinned"}, bundle="a", label="a")
    path = tmp_path / "manifest.json"
    registry.write_manifest(path, manifest)
    monkeypatch.setenv("CLIR_PROMPT_MANIFEST", str(path))
    pack = PromptPack(registry.PREFIX + "un")
    assert pack.has("verifiers", "lookup_batch.txt")
    assert not pack.has("verifiers", "practitioners_batch.txt")
    with pytest.raises(ValueError, match="missing un/quality/practitioner"):
        pack.quality("practitioners")
    broken = tmp_path / "broken.json"
    broken.write_text('{"provider":"mlflow"}')
    monkeypatch.setenv("CLIR_PROMPT_MANIFEST", str(broken))
    with pytest.raises(ValueError, match="unsupported prompt manifest"):
        pack.has("verifiers", "lookup_batch.txt")
