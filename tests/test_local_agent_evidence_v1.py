"""Constructed mechanism checks, never experimental agent or native success."""

import copy
import os

import pytest

from curaloop_rd.local_agent_v1.evidence import EvidenceLedger, Requirement, artifact_identity


def test_byte_edit_with_same_timestamp_invalidates_and_revalidation_restores(tmp_path):
    artifact = tmp_path / "result.csv"
    artifact.write_text("id,value\na,1\n")
    old_time = artifact.stat().st_mtime_ns
    req = Requirement("table", "Readable current table", ("result.csv",), "csv-v1")
    ledger = EvidenceLedger(tmp_path, [req])
    ledger.record(
        "table", "satisfied", "Public CSV check", checked_bindings=ledger.snapshot("table")
    )
    assert ledger.completion()["ready"]
    artifact.write_text("id,value\na,9\n")
    os.utime(artifact, ns=(old_time, old_time))
    assert not ledger.completion()["ready"]
    assert ledger.states()["table"]["state"] == "unknown"
    ledger.record(
        "table", "failed", "Value violates a public rule", checked_bindings=ledger.snapshot("table")
    )
    assert ledger.states()["table"]["state"] == "failed"
    assert not ledger.completion()["ready"]


def test_program_dependency_and_validator_version_both_invalidate(tmp_path):
    (tmp_path / "result.csv").write_text("id\na\n")
    (tmp_path / "program.py").write_text("print('first')\n")
    req = Requirement(
        "dependency", "Output came from current code", ("result.csv", "program.py"), "v1"
    )
    ledger = EvidenceLedger(tmp_path, [req])
    ledger.record(
        "dependency", "satisfied", "Validated", checked_bindings=ledger.snapshot("dependency")
    )
    exported = ledger.export()
    (tmp_path / "program.py").write_text("print('second')\n")
    restored = EvidenceLedger.restore(tmp_path, exported)
    assert not restored.completion()["ready"]
    changed = Requirement("dependency", req.description, req.artifacts, "v2")
    assert not EvidenceLedger(tmp_path, [changed], ledger.events).completion()["ready"]


def test_changed_during_check_missing_artifact_and_history_tamper(tmp_path):
    path = tmp_path / "table.csv"
    path.write_text("id\na\n")
    req = Requirement("rows", "Expected public shape", ("table.csv",), "v1")
    ledger = EvidenceLedger(tmp_path, [req])
    checked = ledger.snapshot("rows")
    path.write_text("id\nb\n")
    ledger.record("rows", "satisfied", "Stale validator observation", checked_bindings=checked)
    assert not ledger.completion()["ready"]
    value = copy.deepcopy(ledger.export())
    value["events"][0]["state"] = "satisfied"
    with pytest.raises(ValueError, match="integrity"):
        EvidenceLedger.restore(tmp_path, value)
    path.unlink()
    assert ledger.states()["rows"]["state"] == "unknown"
    assert not EvidenceLedger(tmp_path, []).completion()["ready"]


@pytest.mark.parametrize("path", ["../hidden.txt", "C:/private.txt", "/private.txt"])
def test_workspace_escape_cannot_be_evidence(tmp_path, path):
    with pytest.raises(ValueError):
        artifact_identity(tmp_path, path)
