"""Return and remove only the exact Plan A task/export roots, after local proof."""

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import time
import zipfile
from pathlib import Path

PROJECT = Path("/home/chaw/curaloop-rl")
TASK = PROJECT / "goal4r2a-20261106-v1"
EXPORT = PROJECT / "goal4r2a-20261106-v1-return"
CORE_SHA = "1401547bdfd9d7ecd353a907684f293b08514706ba7481782eef2e9e1ecda667"


def core_module():
    path = Path(__file__).with_name("remote_task_archive_v1.py")
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != CORE_SHA:
        raise ValueError("Pinned preservation core differs; do not execute/delete.")
    spec = importlib.util.spec_from_file_location("curaloop_preservation_core", path)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    core.ALLOWED = {TASK}
    return core


def checked_export():
    if (
        EXPORT.parent != PROJECT
        or PROJECT.resolve(strict=True) != PROJECT
        or EXPORT.is_symlink()
        or EXPORT.resolve(strict=True) != EXPORT
        or not EXPORT.is_dir()
        or EXPORT.stat().st_uid != os.getuid()
    ):
        raise ValueError("Export root path/type/ownership differs.")
    return EXPORT


def export_files(core):
    root = checked_export()
    expected = {"task.zip", "manifest.json", "local-verification.json"}
    paths = list(root.iterdir())
    if {p.name for p in paths} != expected:
        raise ValueError("Unexpected export files; do not delete.")
    for path in paths:
        info = path.lstat()
        if (
            not stat.S_ISREG(info.st_mode)
            or path.is_symlink()
            or info.st_uid != os.getuid()
            or path.resolve(strict=True).parent != root
        ):
            raise ValueError("Unsafe export entry.")
    return {p.name: core.sha(p) for p in paths}


def snapshot(core):
    root = core.checked_root(TASK)
    if EXPORT.exists() or EXPORT.is_symlink() or EXPORT.parent.resolve(strict=True) != PROJECT:
        raise ValueError("Export must be new, outside the task and under the canonical project.")
    if core.active_processes(root):
        raise RuntimeError("Task processes remain active; no snapshot/cleanup.")
    EXPORT.mkdir(mode=0o700)
    rows = core.inventory(root)
    archive = EXPORT / "task.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as handle:
        for row in rows:
            handle.write(root / row["path"], row["path"])
    if core.inventory(root) != rows:
        raise RuntimeError("Task changed while snapshotting; keep both roots.")
    manifest = {
        "status": "SNAPSHOT_COMPLETE_NOT_LOCAL_VERIFIED",
        "root": str(root),
        "files": rows,
        "file_count": len(rows),
        "bytes": sum(r["bytes"] for r in rows),
        "tree_sha256": core.tree_sha(rows),
        "zip_sha256": core.sha(archive),
        "snapshot_cpu_seconds": time.process_time(),
        "helper_sha256": core.sha(Path(__file__)),
    }
    path = EXPORT / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: v for k, v in manifest.items() if k != "files"}
            | {"manifest_sha256": core.sha(path)}
        )
    )


def delete(core):
    root = core.checked_root(TASK)
    hashes = export_files(core)
    receipt = json.loads((EXPORT / "local-verification.json").read_text())
    if (
        receipt.get("status") != "PASS_LOCAL_ALL_FILES_VERIFIED"
        or receipt.get("remote_root") != str(root)
        or receipt.get("manifest_sha256") != hashes["manifest.json"]
        or receipt.get("zip_sha256") != hashes["task.zip"]
    ):
        raise ValueError("Exact locally verified export hashes/root required.")
    manifest = json.loads((EXPORT / "manifest.json").read_text())
    if (
        manifest["root"] != str(root)
        or manifest["file_count"] != receipt["file_count"]
        or manifest["tree_sha256"] != receipt["tree_sha256"]
        or core.tree_sha(manifest["files"]) != receipt["tree_sha256"]
    ):
        raise ValueError("Export manifest and local complete-inventory proof differ.")
    if core.active_processes(EXPORT):
        raise RuntimeError("Export processes remain active; stop cleanup.")
    # The reviewed core repeats complete source inventory, active-process and
    # immediate canonical-root checks before removing only the allowed task.
    core.delete_verified(root, EXPORT / "local-verification.json")
    if checked_export() != EXPORT or export_files(core) != hashes:
        raise RuntimeError("Export changed during cleanup; keep export.")
    shutil.rmtree(EXPORT)
    if root.exists() or root.is_symlink() or EXPORT.exists() or EXPORT.is_symlink():
        raise RuntimeError("Task/export absence verification failed.")
    print(
        json.dumps(
            {
                "status": "PASS_GOAL4R2A_TASK_AND_EXPORT_REMOVED",
                "root": str(root),
                "export": str(EXPORT),
                "remote_task_absent": True,
                "remote_export_absent": True,
                "local_inventory_verified": True,
                "tree_sha256": receipt["tree_sha256"],
                "preserved_file_count": receipt["file_count"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("snapshot", "delete"))
    args = parser.parse_args()
    core = core_module()
    snapshot(core) if args.operation == "snapshot" else delete(core)
