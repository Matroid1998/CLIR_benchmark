"""A saved UN comparison plan must not resample or lose its target identity."""

import json
import sys
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from clir_bench.domains.legal.qac import un_batch as batch


def target(**changes):
    fields = dict(doc_id="2002/a/res/56/205", block_id="2002/a/res/56/205#1",
                  block_index=1, n_blocks=4, stratum="resolution",
                  mode="technical", language="en")
    return batch.Target(**(fields | changes))


def test_manifest_roundtrip_preserves_order_and_languages(tmp_path):
    targets = [target(language="fr"), target(language="en", mode="semantic")]
    path = tmp_path / "targets.json"
    batch.write_targets(path, targets)
    assert batch.load_targets(path) == targets


@pytest.mark.parametrize("changes", [
    {"language": "de"}, {"mode": "unknown"}, {"block_index": -1},
    {"block_index": True}, {"n_blocks": 1}, {"block_id": "another#1"},
])
def test_manifest_rejects_invalid_source_identity(tmp_path, changes):
    path = tmp_path / "targets.json"
    path.write_text(json.dumps([asdict(target(**changes))]))
    with pytest.raises(ValueError):
        batch.load_targets(path)


def test_manifest_rejects_duplicate_input(tmp_path):
    path = tmp_path / "targets.json"
    path.write_text(json.dumps([asdict(target()), asdict(target())]))
    with pytest.raises(ValueError, match="duplicate"):
        batch.load_targets(path)


def test_cli_replays_exact_targets_without_sampling(tmp_path, monkeypatch):
    path, output = tmp_path / "targets.json", tmp_path / "saved.json"
    batch.write_targets(path, [target(language="fr")])
    index = SimpleNamespace(docs={target().doc_id: {"n_blocks": 4}}, incomplete=None)
    monkeypatch.setattr(batch.ctx, "BlockIndex", lambda **kw: index)
    monkeypatch.setattr(batch, "load_env", lambda: None)
    monkeypatch.setattr(batch, "select", lambda *a, **kw: pytest.fail("manifest resampled"))
    monkeypatch.setattr(sys, "argv", ["un_batch", "--targets-in", str(path),
                                     "--targets-out", str(output), "--n", "999", "--dry-run"])
    batch.main()
    assert batch.load_targets(output) == [target(language="fr")]
