"""Task/export deletion requires complete verified local preservation."""

import json
import shutil
import sys
from pathlib import Path

import pytest

from tools import remote_goal4_return_v1 as helper
from tools import verify_remote_return_v1 as base
from tools import verify_remote_return_v2 as verifier


def test_only_explicit_goal4_task_root_is_allowed():
    assert helper.TASK == Path("/home/chaw/curaloop-rl/plan-a-20261105-v2")
    assert helper.EXPORT == Path("/home/chaw/curaloop-rl/plan-a-20261105-v2-return")
    core = helper.core_module()
    assert core.ALLOWED == {helper.TASK}
    with pytest.raises(ValueError, match="explicitly authorized"):
        core.checked_root(Path("/home/chaw/curaloop-rl"))
    with pytest.raises(ValueError, match="explicitly authorized"):
        core.checked_root(Path("/home/chaw/curaloop-rl/plan-a-20261105-v1"))


def fixture(tmp_path, monkeypatch):
    project = tmp_path / "remote-project"
    project.mkdir()
    task = project / "plan-a-20261105-v1"
    task.mkdir()
    (task / "artifact.bin").write_bytes(b"constructed-preservation-fixture\x00")
    (task / ".cleanup.lock").write_bytes(b"")
    (project / "unrelated-project").mkdir()
    (project / "unrelated-project/sentinel").write_text("untouched")
    monkeypatch.setattr(helper, "PROJECT", project)
    monkeypatch.setattr(helper, "TASK", task)
    monkeypatch.setattr(helper, "EXPORT", project / "plan-a-20261105-v1-return")
    fixture_uid = task.stat().st_uid
    monkeypatch.setattr(helper.os, "getuid", lambda: fixture_uid, raising=False)
    core = helper.core_module()
    monkeypatch.setattr(core, "PROJECT", project)
    monkeypatch.setattr(core, "active_processes", lambda root: [])
    return project, task, core


def preserve_local(tmp_path, monkeypatch, core):
    local = tmp_path / "local-project"
    local.mkdir()
    folder = local / ".local/plan-a-20261105-v1/remote-return/current"
    folder.mkdir(parents=True)
    for name in ("task.zip", "manifest.json"):
        shutil.copyfile(helper.EXPORT / name, folder / name)
    monkeypatch.setattr(base, "ROOT", local)
    monkeypatch.setattr(sys, "argv", ["verify_remote_return_v2", "--folder", str(folder)])
    verifier.main()
    proof = folder / "local-verification-with-manifest.json"
    shutil.copyfile(proof, helper.EXPORT / "local-verification.json")
    return folder


def test_both_roots_removed_only_after_unchanged_manifest_and_complete_file_verification(
    tmp_path, monkeypatch
):
    project, task, core = fixture(tmp_path, monkeypatch)
    helper.snapshot(core)
    folder = preserve_local(tmp_path, monkeypatch, core)
    receipt = json.loads((folder / "local-verification-with-manifest.json").read_text())
    assert receipt["manifest_unchanged_during_verification"]
    assert (folder / "files/artifact.bin").read_bytes() == b"constructed-preservation-fixture\x00"
    helper.delete(core)
    assert not task.exists() and not helper.EXPORT.exists()
    assert (project / "unrelated-project/sentinel").read_text() == "untouched"


@pytest.mark.parametrize("change", ["source", "zip", "receipt"])
def test_change_after_snapshot_or_local_proof_keeps_remote_files(tmp_path, monkeypatch, change):
    _, task, core = fixture(tmp_path, monkeypatch)
    helper.snapshot(core)
    preserve_local(tmp_path, monkeypatch, core)
    if change == "source":
        (task / "new-data.bin").write_bytes(b"not-in-local-snapshot")
    elif change == "zip":
        with (helper.EXPORT / "task.zip").open("ab") as handle:
            handle.write(b"changed")
    else:
        path = helper.EXPORT / "local-verification.json"
        receipt = json.loads(path.read_text())
        receipt["manifest_sha256"] = "0" * 64
        path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        helper.delete(core)
    assert task.exists() and helper.EXPORT.exists()


def test_active_process_stops_before_snapshot_creation(tmp_path, monkeypatch):
    _, task, core = fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(core, "active_processes", lambda root: [12345])
    with pytest.raises(RuntimeError, match="processes remain"):
        helper.snapshot(core)
    assert task.exists() and not helper.EXPORT.exists()


def test_manifest_changed_during_verification_cannot_get_enhanced_pass(tmp_path, monkeypatch):
    _, _, core = fixture(tmp_path, monkeypatch)
    helper.snapshot(core)
    real = base.main

    def changed_after_base_check():
        real()
        folder = Path(sys.argv[2])
        with (folder / "manifest.json").open("ab") as handle:
            handle.write(b" ")

    monkeypatch.setattr(base, "main", changed_after_base_check)
    with pytest.raises(ValueError, match="changed during"):
        preserve_local(tmp_path, monkeypatch, core)
    local = tmp_path / "local-project/.local/plan-a-20261105-v1/remote-return/current"
    assert not (local / "local-verification-with-manifest.json").exists()
    assert helper.TASK.exists() and helper.EXPORT.exists()
