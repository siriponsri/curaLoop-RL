import hashlib
import json

import pytest

from tools import remote_task_archive_v1 as remote
from tools.verify_remote_return_v1 import unsafe_windows_path


def fixture_tree(tmp_path, monkeypatch):
    project = tmp_path / "owned-project"
    root = project / "owned-task"
    root.mkdir(parents=True)
    (root / "code.py").write_bytes(b"preserved code")
    monkeypatch.setattr(remote, "PROJECT", project.resolve())
    monkeypatch.setattr(remote, "ALLOWED", {root.resolve()})
    monkeypatch.setattr(remote.os, "getuid", lambda: root.stat().st_uid, raising=False)
    return root


def test_unknown_root_and_incomplete_receipt_cannot_delete(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        remote.checked_root(root.parent)
    receipt = tmp_path / "bad.json"
    receipt.write_text(json.dumps({"status": "NOT_VERIFIED", "remote_root": str(root)}))
    with pytest.raises(ValueError, match="receipt"):
        remote.delete_verified(root, receipt)
    assert (root / "code.py").is_file()


def test_changed_bytes_and_active_processes_block_cleanup(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path, monkeypatch)
    original = remote.inventory(root)
    receipt = tmp_path / "verified.json"
    receipt.write_text(
        json.dumps(
            {
                "status": "PASS_LOCAL_ALL_FILES_VERIFIED",
                "remote_root": str(root),
                "tree_sha256": remote.tree_sha(original),
                "file_count": len(original),
            }
        )
    )
    (root / "code.py").write_bytes(b"changed after retrieval")
    with pytest.raises(ValueError, match="changed"):
        remote.delete_verified(root, receipt)
    (root / "code.py").write_bytes(b"preserved code")
    monkeypatch.setattr(remote, "active_processes", lambda _: [123])
    with pytest.raises(RuntimeError, match="active"):
        remote.delete_verified(root, receipt)
    assert root.exists()


def test_inventory_hashes_exact_bytes(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path, monkeypatch)
    rows = remote.inventory(root)
    assert rows == [
        {"path": "code.py", "bytes": 14, "sha256": hashlib.sha256(b"preserved code").hexdigest()}
    ]


def test_inventory_traversal_failure_is_fatal(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path, monkeypatch)

    def unreadable(*args, **kwargs):
        kwargs["onerror"](PermissionError("simulated unreadable subtree"))
        yield None

    monkeypatch.setattr(remote.os, "walk", unreadable)
    with pytest.raises(PermissionError, match="unreadable"):
        remote.inventory(root)


def test_ancestor_task_is_not_hidden_by_shell_wrapper_filter(tmp_path):
    root = tmp_path / "task"
    args = "python " + str(root / "coordinator.py")
    assert remote.process_involves_root(root, root, args, True, "python3")
    assert remote.process_involves_root(root, tmp_path, args, True, "python3")
    assert remote.process_involves_root(root, root, "shell", True, "bash")
    assert not remote.process_involves_root(
        root, tmp_path, "cleanup --root " + str(root), True, "bash"
    )


def test_windows_aliases_are_rejected():
    for path in (
        "CON",
        "dir/NUL.txt",
        "a/COM1",
        "trailing./x",
        "space /x",
        "a:stream",
        "../outside",
    ):
        assert unsafe_windows_path(path)
    assert not unsafe_windows_path("research/__pycache__/task.cpython-312.pyc")
