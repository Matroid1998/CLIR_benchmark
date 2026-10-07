"""Independent Jev decisions must preserve evidence, probabilities and resumability."""

import copy
import csv
import hashlib
import json

import pytest

from clir_bench.core import llm
from clir_bench.domains.legal.qac import decider, screening_eligibility
from clir_bench.domains.legal.qac.batch_recording import RunState


@pytest.fixture(autouse=True)
def local_prompts(monkeypatch):
    monkeypatch.setenv("CLIR_PROMPT_SOURCE", "local")
    monkeypatch.delenv("CLIR_PROMPT_MANIFEST", raising=False)
    monkeypatch.setattr(screening_eligibility, "load_env", lambda: None)
    monkeypatch.setattr(decider, "eligibility_policy", lambda source: {"probability_threshold": 0.5})


def response(source, values=None):
    values = values or [0.9] * len(decider.MODES[source])
    return {"model": "recorded-jev-model", "answers": {
        mode: {"type": "noul", "noul": value}
        for mode, value in zip(decider.MODES[source], values)
    }}


def record_parent(directory, corpora):
    entries = []
    with RunState(directory / "run.sqlite") as state:
        for index, corpus in enumerate(corpora):
            text = f"### TARGET {'BLOCK' if corpus == 'un' else 'ARTICLE'}\nExact source {index}: é ≤ 70\n"
            entry = {
                "corpus": corpus, "target_id": f"document-{index}#1",
                "document_id": f"document-{index}", "symbol": f"SYMBOL/{index}",
                "source_payload": text,
                "source_payload_sha256": hashlib.sha256(text.encode()).hexdigest(),
            }
            entries.append(entry)
            task = f"decider/{corpus}/{entry['target_id']}/jev"
            record = {"request": {"model": decider.JEV_MODEL, "state": text}}
            with state.transaction() as database:
                database.execute("INSERT INTO requests VALUES (?,?,?,?)",
                                 (f"parent-request-{index}", task, "decider", json.dumps(record)))
            state.outcome(task, [{"mode": "lookup", "confidence": 0.77}])
        state.put("targets", entries)
        state.put("status", "completed")
    return directory, entries


@pytest.fixture
def parent_run(tmp_path):
    return record_parent(tmp_path / "parent", ("un", "eurlex", "un"))


@pytest.mark.parametrize("source", ["un", "eurlex"])
def test_independent_probabilities_are_not_normalized_and_half_is_inclusive(source):
    probabilities = [1, 0.9, 0.8, 0.5, 0.499, 0]
    result = decider.parse_eligibility(response(source, probabilities), source)
    assert list(result["probabilities_yes"].values()) == probabilities
    assert sum(result["probabilities_yes"].values()) > 1
    assert result["selected_modes"] == list(decider.MODES[source][:4])
    assert result["threshold"] == 0.5
    assert result["response_model"] == "recorded-jev-model"


@pytest.mark.parametrize("value", [None, True, False, "0.8", -0.01, 1.01,
                                      float("nan"), float("inf"), -float("inf")])
def test_noul_rejects_invalid_probability_without_coercion(value):
    data = response("un")
    data["answers"]["lookup"]["noul"] = value
    with pytest.raises(ValueError, match="finite and in"):
        decider.parse_eligibility(data, "un")


@pytest.mark.parametrize("change", ["missing", "extra", "choice", "scalar", "absent_value"])
def test_noul_requires_exact_complete_mode_answers(change):
    data = response("un")
    if change == "missing":
        del data["answers"]["lookup"]
    elif change == "extra":
        data["answers"]["skip"] = {"type": "noul", "noul": 0.1}
    elif change == "choice":
        data["answers"]["lookup"] = {"type": "choice", "choice": "true", "noul": 0.9}
    elif change == "scalar":
        data["answers"]["lookup"] = 0.9
    else:
        del data["answers"]["lookup"]["noul"]
    with pytest.raises(ValueError):
        decider.parse_eligibility(data, "un")


@pytest.mark.parametrize("threshold", [True, "0.5", -0.1, 1.1, float("nan")])
def test_invalid_threshold_is_rejected_before_provider_call(monkeypatch, threshold):
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Invalid settings made a call"))
    with pytest.raises(ValueError):
        decider.decide_eligibility("un", "Evidence", threshold=threshold)


@pytest.mark.parametrize("source", ["un", "eurlex"])
def test_request_has_six_independent_questions_and_exact_source(source):
    text = "### TARGET\nExact source with Unicode: é ≤ 70\n"
    request = decider.build_eligibility_request(source, text)
    assert request["state"] == text
    assert request["model"] == decider.JEV_MODEL
    assert set(request["questions"]) == set(decider.MODES[source])
    assert all(question["type"] == "noul" for question in request["questions"].values())
    assert all(set(question["criteria"]) == {"true", "false"}
               for question in request["questions"].values())


def test_load_targets_replays_exact_saved_jev_inputs(parent_run):
    parent, entries = parent_run
    targets = screening_eligibility.load_targets(parent)
    assert targets == [dict(entry, previous_pick="lookup", previous_confidence=0.77)
                       for entry in entries]


@pytest.mark.parametrize("change", ["payload", "hash", "request", "missing_request",
                                    "changed_retry", "unfinished", "missing_decision", "duplicate"])
def test_parent_drift_is_rejected_before_provider_calls(parent_run, tmp_path, monkeypatch, change):
    parent, original = parent_run
    entries = copy.deepcopy(original)
    with RunState(parent / "run.sqlite") as state:
        if change == "payload":
            entries[0]["source_payload"] += "New content"
            entries[0]["source_payload_sha256"] = hashlib.sha256(
                entries[0]["source_payload"].encode()).hexdigest()
            state.put("targets", entries)
        elif change == "hash":
            entries[0]["source_payload_sha256"] = "0" * 64
            state.put("targets", entries)
        elif change == "duplicate":
            state.put("targets", [*entries, entries[0]])
        elif change == "unfinished":
            state.put("status", "running")
        else:
            with state.transaction() as database:
                task = f"decider/un/{entries[0]['target_id']}/jev"
                if change == "missing_decision":
                    database.execute("DELETE FROM outcomes WHERE task=?", (task,))
                elif change == "missing_request":
                    database.execute("DELETE FROM requests WHERE task=?", (task,))
                elif change == "request":
                    database.execute("UPDATE requests SET record=? WHERE task=?",
                                     (json.dumps({"request": {"state": "Different text"}}), task))
                else:
                    database.execute("INSERT INTO requests VALUES (?,?,?,?)",
                                     ("changed-retry", task, "decider",
                                      json.dumps({"request": {"state": "Different retry text"}})))
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Drift made a provider call"))
    with pytest.raises(ValueError):
        screening_eligibility.run(parent, tmp_path / "output", retries=1)
    assert not (tmp_path / "output").exists()


def fake_decisions(calls):
    def answer(request):
        calls.append(copy.deepcopy(request))
        source = "un" if "practitioner" in request["questions"] else "eurlex"
        return response(source, [0.5, 0.9, 0.8, 0.1, 0.2, 0.3])
    return answer


def test_run_resume_reuses_outcomes_and_completed_stages(parent_run, tmp_path, monkeypatch):
    parent, entries = parent_run
    output, calls = tmp_path / "output", []
    monkeypatch.setattr(llm, "decisions", fake_decisions(calls))
    screening_eligibility.run(parent, output, workers=2, retries=1)
    assert len(calls) == len(entries)
    assert {call["state"] for call in calls} == {entry["source_payload"] for entry in entries}
    with (output / "decisions.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(entries) * 6
    assert sum(row["selected"] == "True" for row in rows) == len(entries) * 3
    assert all(row["selected"] == "True" for row in rows if row["probability_yes"] == "0.5")
    with RunState(output / "run.sqlite") as state:
        assert state.get("status") == "completed"
        assert state.get("summary")["failures"] == 0
        with state.transaction() as database:
            # Recreate interruption after a successful API stage but before its outcome was committed.
            database.execute("DELETE FROM outcomes WHERE task=?",
                             (f"eligibility/un/{entries[0]['target_id']}",))
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Resume made a provider call"))
    screening_eligibility.run(parent, output, workers=1, retries=1)
    with RunState(output / "run.sqlite") as state:
        assert len(state.outcomes()) == len(entries)
        assert all(outcome["status"] == "completed" for outcome in state.outcomes())
        with state.transaction() as database:
            assert database.execute("SELECT COUNT(*) FROM requests").fetchone()[0] == len(entries)


@pytest.mark.parametrize("change", ["threshold", "retries", "prompt"])
def test_resume_rejects_changed_settings_before_another_call(parent_run, tmp_path, monkeypatch, change):
    parent, _ = parent_run
    output = tmp_path / "output"
    monkeypatch.setattr(llm, "decisions", fake_decisions([]))
    screening_eligibility.run(parent, output, workers=1, retries=1)
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Changed settings made a call"))
    kwargs = {"workers": 1, "retries": 1}
    if change == "threshold":
        kwargs["threshold"] = 0.6
    elif change == "retries":
        kwargs["retries"] = 2
    else:
        original = decider.eligibility_prompt_text
        monkeypatch.setattr(decider, "eligibility_prompt_text", lambda source: original(source) + "\n")
    with pytest.raises(ValueError, match="changed on resume"):
        screening_eligibility.run(parent, output, **kwargs)
    with RunState(output / "run.sqlite") as state:
        assert state.get("status") == "completed"


@pytest.mark.parametrize("selection", [
    [], {}, [None], [{"corpus": "un"}],
    [{"corpus": None, "document_id": "document-0"}],
    [{"corpus": "un", "document_id": " "}],
    [{"corpus": "un", "document_id": 0}],
    [{"corpus": "unknown", "document_id": "document-0"}],
    [{"corpus": "un", "document_id": "missing"}],
    [{"corpus": "un", "document_id": "document-0"}] * 2,
])
def test_invalid_document_selection_makes_no_provider_call(
    parent_run, tmp_path, monkeypatch, selection,
):
    parent, _ = parent_run
    path = tmp_path / "selection.json"
    path.write_text(json.dumps(selection), encoding="utf-8")
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Invalid selection made a call"))
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        screening_eligibility.run(parent, output, document_selection=path)
    assert not output.exists()


def test_document_selection_replays_30_original_targets_and_resumes_after_file_move(
    tmp_path, monkeypatch,
):
    parent, entries = record_parent(tmp_path / "parent", ("un", "eurlex") * 25)
    selected = entries[10:40]
    path = tmp_path / "selection.json"
    # Selection order and unrelated split metadata cannot alter source replay order.
    path.write_text(json.dumps([
        {"corpus": entry["corpus"], "document_id": entry["document_id"], "split": "development"}
        for entry in reversed(selected)
    ]), encoding="utf-8")
    output, calls = tmp_path / "output", []
    monkeypatch.setattr(llm, "decisions", fake_decisions(calls))
    screening_eligibility.run(parent, output, workers=2, retries=1, document_selection=path)
    assert len(calls) == 30
    assert {call["state"] for call in calls} == {entry["source_payload"] for entry in selected}
    with RunState(output / "run.sqlite") as state:
        recorded = state.get("targets")
        assert [entry["document_id"] for entry in recorded] == [
            entry["document_id"] for entry in selected
        ]
        config = state.get("config")
        assert config["documents_by_corpus"] == {"un": 15, "eurlex": 15}
        assert config["targets_sha256"] == screening_eligibility.digest(recorded)
        assert config["document_selection_sha256"] == screening_eligibility.digest([
            {"corpus": entry["corpus"], "document_id": entry["document_id"]}
            for entry in selected
        ])
        assert state.get("summary")["decisions"] == 180
    moved = tmp_path / "moved.json"
    path.rename(moved)
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Resume made a provider call"))
    screening_eligibility.run(parent, output, workers=1, retries=1, document_selection=moved)
    # A different selection is a different replay even if it has the same size.
    moved.write_text(json.dumps([
        {"corpus": entry["corpus"], "document_id": entry["document_id"]}
        for entry in entries[11:41]
    ]), encoding="utf-8")
    with pytest.raises(ValueError, match="changed on resume"):
        screening_eligibility.run(parent, output, retries=1, document_selection=moved)


@pytest.mark.parametrize("explicit, expected", [(None, 0.63), (0.5, 0.5)])
def test_run_uses_prompt_policy_unless_threshold_is_explicit(
    parent_run, tmp_path, monkeypatch, explicit, expected,
):
    parent, entries = parent_run
    monkeypatch.setattr(decider, "eligibility_policy", lambda source: {"probability_threshold": 0.63})
    monkeypatch.setattr(llm, "decisions", fake_decisions([]))
    output = tmp_path / "output"
    screening_eligibility.run(parent, output, threshold=explicit, retries=1)
    with RunState(output / "run.sqlite") as state:
        assert state.get("config")["threshold"] == expected
        rows = [row for outcome in state.outcomes() for row in outcome["rows"]]
        assert all(row["threshold"] == expected for row in rows)
        expected_yes = len(entries) * (2 if expected == 0.63 else 3)
        assert sum(row["selected"] for row in rows) == expected_yes


def test_different_corpus_policies_require_explicit_threshold(
    parent_run, tmp_path, monkeypatch,
):
    parent, _ = parent_run
    monkeypatch.setattr(decider, "eligibility_policy", lambda source: {
        "probability_threshold": 0.6 if source == "un" else 0.7,
    })
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Policy disagreement made a call"))
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="supply an explicit threshold"):
        screening_eligibility.run(parent, output)
    assert not output.exists()
    monkeypatch.setattr(llm, "decisions", fake_decisions([]))
    screening_eligibility.run(parent, output, threshold=0.63, retries=1)
    with RunState(output / "run.sqlite") as state:
        assert state.get("config")["threshold"] == 0.63


@pytest.mark.parametrize("threshold", [True, "0.5", -0.1, 1.1, float("nan")])
def test_run_rejects_invalid_explicit_threshold_before_provider_call(
    parent_run, tmp_path, monkeypatch, threshold,
):
    parent, _ = parent_run
    monkeypatch.setattr(llm, "decisions", lambda _: pytest.fail("Invalid threshold made a call"))
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        screening_eligibility.run(parent, output, threshold=threshold)
    assert not output.exists()
