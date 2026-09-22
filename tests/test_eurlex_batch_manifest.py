"""Fixed target manifests preserve source identity across generator models."""

import json
from dataclasses import asdict, replace
from types import SimpleNamespace

import pytest

from clir_bench.core import llm
from clir_bench.domains.legal.qac import eurlex_batch as batch
from clir_bench.domains.legal.qac import eurlex_context as context


def target(**changes):
    return replace(batch.Target(
        eli_id="http://data.europa.eu/eli/reg/2019/904/art_4/oj",
        celex_id="32019R0904", article_number="4", n_refs=0,
        stratum="no_refs", mode="lookup", language="en"), **changes)


def test_manifest_roundtrip_preserves_order_and_all_target_fields(tmp_path):
    targets = [target(language="fr", n_external=2, n_annex=1, cites_annex=True),
               target(mode="fact_pattern", complete=False)]
    path = tmp_path / "nested" / "targets.json"
    batch.write_targets(path, targets)
    first = path.read_bytes()
    assert batch.load_targets(path) == targets
    batch.write_targets(path, batch.load_targets(path))
    assert path.read_bytes() == first
    assert json.loads(first) == [asdict(item) for item in targets]


@pytest.mark.parametrize(("rows", "message"), [
    ({"targets": []}, "nonempty JSON list"),
    ([], "nonempty JSON list"),
    (["article"], "must be an object"),
    ([{}], "invalid target manifest entry"),
    ([asdict(target(mode="technical"))], "unsupported EUR-Lex mode"),
    ([asdict(target(language="zh"))], "unsupported EUR-Lex language"),
    ([asdict(target(eli_id=""))], "nonempty article identifiers"),
    ([asdict(target()), asdict(target())], "duplicate target"),
])
def test_invalid_manifest_rejected(tmp_path, rows, message):
    path = tmp_path / "targets.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises((TypeError, ValueError), match=message):
        batch.load_targets(path)


def prepare_cli(monkeypatch, targets, args):
    units = {item.eli_id: context.ArticleUnit(
        item.eli_id, item.celex_id, item.article_number,
        texts={item.language: "Original article text"}) for item in targets}
    index = SimpleNamespace(by_eli=units)
    monkeypatch.setattr(batch.ctx, "ArticleIndex", lambda: index)
    monkeypatch.setattr(batch, "load_env", lambda: None)
    monkeypatch.setattr(llm, "client_for", lambda *_: pytest.fail("dry run initialized an API client"))
    monkeypatch.setattr("sys.argv", ["eurlex_batch", *args])
    return index


def test_cli_manifest_bypasses_selection_and_ignores_n(tmp_path, monkeypatch):
    source = tmp_path / "in.json"
    destination = tmp_path / "out.json"
    targets = [target(language="fr")]
    batch.write_targets(source, targets)
    prepare_cli(monkeypatch, targets, ["--targets-in", str(source), "--targets-out",
                                      str(destination), "--n", "999", "--dry-run"])
    monkeypatch.setattr(batch, "select", lambda *a, **kw: pytest.fail("manifest was resampled"))
    batch.main()
    assert batch.load_targets(destination) == targets


def test_cli_saves_selected_targets_during_dry_run(tmp_path, monkeypatch):
    destination = tmp_path / "selected.json"
    targets = [target()]
    prepare_cli(monkeypatch, targets, ["--targets-out", str(destination), "--dry-run"])
    monkeypatch.setattr(batch, "select", lambda *a, **kw: targets)
    batch.main()
    assert batch.load_targets(destination) == targets


@pytest.mark.parametrize("problem", ["unknown_article", "wrong_identity", "missing_language"])
def test_cli_invalid_source_manifest_fails_before_any_api_call(tmp_path, monkeypatch, problem):
    source = tmp_path / "targets.json"
    targets = [target()]
    batch.write_targets(source, targets)
    index = prepare_cli(monkeypatch, targets, ["--targets-in", str(source), "--dry-run"])
    if problem == "unknown_article":
        index.by_eli.clear()
    elif problem == "wrong_identity":
        index.by_eli[targets[0].eli_id].celex_id = "32000R0001"
    else:
        index.by_eli[targets[0].eli_id].texts.clear()
    with pytest.raises(SystemExit) as error:
        batch.main()
    assert error.value.code == 2


def test_cli_rejects_retired_modes_without_manifest(monkeypatch):
    monkeypatch.setattr("sys.argv", ["eurlex_batch", "--modes", "technical", "--dry-run"])
    monkeypatch.setattr(batch, "load_env", lambda: None)
    monkeypatch.setattr(batch.ctx, "ArticleIndex", lambda: pytest.fail("invalid mode loaded corpus"))
    with pytest.raises(SystemExit) as error:
        batch.main()
    assert error.value.code == 2
