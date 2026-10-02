import hashlib
import json
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from clir_bench.domains.legal.qac import screening


@dataclass
class SavedTarget:
    language: str = "en"


def fixture(tmp_path, monkeypatch, text="original source"):
    record = {"corpus": "un", "target_id": "doc#1", "target": {"language": "en"},
              "source_payload": text, "source_payload_sha256": hashlib.sha256(text.encode()).hexdigest()}
    payload = SimpleNamespace(text=text, target=SimpleNamespace(block_id="doc#1"))
    batch = SimpleNamespace(Target=SavedTarget, ctx=SimpleNamespace(BlockIndex=lambda: None),
                            prepare_payload=lambda *args: payload)
    monkeypatch.setitem(screening.BATCHES, "un", batch)
    path = tmp_path / "selection.json"
    path.write_text(json.dumps([record]))
    return path, record, payload


def test_replay_preserves_entire_selection_and_payload(tmp_path, monkeypatch):
    path, record, payload = fixture(tmp_path, monkeypatch)
    entries, payloads = screening.replay_selection(path)
    assert entries == [record]
    assert payloads == {("un", "doc#1"): payload}


@pytest.mark.parametrize("change", ["text", "hash", "identity", "duplicate"])
def test_replay_rejects_drift_before_provider_calls(tmp_path, monkeypatch, change):
    path, record, payload = fixture(tmp_path, monkeypatch)
    if change == "text":
        payload.text = "new corpus content"
    elif change == "identity":
        payload.target.block_id = "doc#2"
    elif change == "hash":
        record["source_payload_sha256"] = "0" * 64
        path.write_text(json.dumps([record]))
    else:
        path.write_text(json.dumps([record, record]))
    with pytest.raises(ValueError):
        screening.replay_selection(path)
