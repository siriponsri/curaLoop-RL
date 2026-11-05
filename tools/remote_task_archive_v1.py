"""Linux-only task snapshot/cleanup helper. No scientific data deserialization."""

import argparse
import hashlib
import json
import os
import shutil
import stat
import time
import zipfile
from pathlib import Path

PROJECT = Path("/home/chaw/curaloop-rl")
ALLOWED = {PROJECT / "goal2-20261104-v1"}  # v1: completed Goal2 task only


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024**2), b""):
            value.update(block)
    return value.hexdigest()


def checked_root(path):
    path = Path(path)
    if path not in ALLOWED or not path.is_absolute() or path.parent != PROJECT:
        raise ValueError("Root is not an explicitly authorized task directory.")
    if (
        path.is_symlink()
        or path.resolve(strict=True) != path
        or PROJECT.resolve(strict=True) != PROJECT
    ):
        raise ValueError("Task/project root is aliased or a symlink.")
    if not path.is_dir() or path.stat().st_uid != os.getuid():
        raise ValueError("Task root ownership/type differs.")
    return path


def inventory(root):
    root = checked_root(root)
    rows = []

    def traversal_error(error):
        raise error

    for folder, dirs, files in os.walk(root, followlinks=False, onerror=traversal_error):
        for name in sorted(dirs + files):
            path = Path(folder) / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or info.st_uid != os.getuid():
                raise ValueError("Unexpected symlink/owner: " + str(path))
            if path.resolve(strict=True).is_relative_to(root) is False:
                raise ValueError("Inventory path leaves task root.")
            if stat.S_ISREG(info.st_mode):
                rows.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "bytes": info.st_size,
                        "sha256": sha(path),
                    }
                )
            elif not stat.S_ISDIR(info.st_mode):
                raise ValueError("Unsupported filesystem entry.")
    return sorted(rows, key=lambda r: r["path"])


def tree_sha(rows):
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def process_involves_root(root, cwd, args, is_ancestor, command):
    if cwd == root or cwd.is_relative_to(root):
        return True
    if str(root) not in args:
        return False
    shell_wrappers = {"sh", "bash", "dash", "sshd", "timeout", "flock", "taskset", "nice"}
    return not (is_ancestor and command.strip() in shell_wrappers)


def active_processes(root):
    own_chain = {os.getpid()}
    parent = os.getppid()
    while parent > 1 and parent not in own_chain:
        own_chain.add(parent)
        try:
            status = (Path("/proc") / str(parent) / "status").read_text()
            parent = int(
                next(line.split()[1] for line in status.splitlines() if line.startswith("PPid:"))
            )
        except (FileNotFoundError, PermissionError, StopIteration, ValueError):
            break
    found = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            cwd = Path(os.readlink(proc / "cwd"))
            args = (proc / "cmdline").read_bytes().replace(b"\x00", b" ").decode(errors="replace")
            command = (proc / "comm").read_text()
            if process_involves_root(root, cwd, args, int(proc.name) in own_chain, command):
                found.append(int(proc.name))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return found


def snapshot(root, output):
    root = checked_root(root)
    output = Path(output)
    if output.exists() or output.resolve().is_relative_to(root):
        raise ValueError("Snapshot must be new and outside the target root.")
    expected_parent = PROJECT / "plan-a-20261105-v1"
    if (
        output.parent != expected_parent
        or expected_parent.is_symlink()
        or expected_parent.resolve(strict=True) != expected_parent
        or not expected_parent.is_dir()
        or expected_parent.stat().st_uid != os.getuid()
    ):
        raise ValueError("Snapshot output must be inside the owned PlanA task root.")
    output.mkdir()
    rows = inventory(root)
    archive = output / "task.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as handle:
        for row in rows:
            handle.write(root / row["path"], row["path"])
    if inventory(root) != rows:
        raise RuntimeError("Task changed while snapshotting; do not delete.")
    manifest = {
        "status": "SNAPSHOT_COMPLETE_NOT_LOCAL_VERIFIED",
        "root": str(root),
        "files": rows,
        "file_count": len(rows),
        "bytes": sum(r["bytes"] for r in rows),
        "tree_sha256": tree_sha(rows),
        "zip_sha256": sha(archive),
        "snapshot_cpu_seconds": time.process_time(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}))


def delete_verified(root, receipt):
    root = checked_root(root)
    receipt = json.loads(Path(receipt).read_text())
    if receipt.get("status") != "PASS_LOCAL_ALL_FILES_VERIFIED" or receipt.get(
        "remote_root"
    ) != str(root):
        raise ValueError("Successful exact-root local preservation receipt is required.")
    rows = inventory(root)
    if tree_sha(rows) != receipt["tree_sha256"] or len(rows) != receipt["file_count"]:
        raise ValueError("Remote files changed or local verification is incomplete.")
    active = active_processes(root)
    if active:
        raise RuntimeError("Task processes remain active; stop cleanup: " + str(active))
    # Final resolved path/type/ownership check immediately before recursive removal.
    if checked_root(root) != root or tree_sha(inventory(root)) != receipt["tree_sha256"]:
        raise RuntimeError("Root changed during cleanup verification.")
    shutil.rmtree(root)
    if root.exists() or root.is_symlink():
        raise RuntimeError("Cleanup absence check failed.")
    print(
        json.dumps(
            {
                "status": "PASS_VERIFIED_REMOTE_TASK_REMOVED",
                "root": str(root),
                "preserved_file_count": len(rows),
                "tree_sha256": receipt["tree_sha256"],
                "remote_absent": True,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("snapshot", "delete"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.operation == "snapshot":
        snapshot(args.root, args.output)
    else:
        delete_verified(args.root, args.receipt)
