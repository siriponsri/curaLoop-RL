"""Non-destructive closed partial return to support local validation gating."""

import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path

TASK = Path("/home/chaw/curaloop-rl/plan-a-20261105-v2")


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024**2), b""):
            value.update(block)
    return value.hexdigest()


def main():
    assert Path.cwd().resolve() == TASK and TASK.resolve() == TASK and TASK.stat().st_uid == os.getuid()
    base = TASK / ".local/plan-a-20261105-v2"
    from research.study_v1.identity import verify_frozen, verify_selection
    protocol = verify_frozen(TASK)
    verify_selection(TASK, protocol)
    files = [p for p in (base / "runs/development").rglob("*") if p.is_file()]
    files += [base / "selection.json", base / "selection-admin-resources-v1.json",
              TASK / "docs/evidence/goal4-20261105-v1/selection-freeze-v1.json"]
    rows = []
    for path in sorted(files):
        info = path.lstat()
        assert path.resolve().is_relative_to(TASK) and stat.S_ISREG(info.st_mode) and not path.is_symlink()
        assert info.st_uid == os.getuid()
        rows.append({"path": path.relative_to(TASK).as_posix(), "bytes": info.st_size, "sha256": sha(path)})
    output = TASK / "development-return-v1"
    output.mkdir(exist_ok=False, mode=0o700)
    archive = output / "task.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as handle:
        for row in rows:
            handle.write(TASK / row["path"], row["path"])
    assert all(sha(TASK / row["path"]) == row["sha256"] for row in rows)
    manifest = {"status": "SNAPSHOT_COMPLETE_NOT_LOCAL_VERIFIED", "root": str(TASK),
                "inventory_scope": "PARTIAL_DEVELOPMENT_GATE_EXPORT_NOT_CLEANUP_AUTHORIZATION",
                "files": rows, "file_count": len(rows), "bytes": sum(r["bytes"] for r in rows),
                "zip_sha256": sha(archive), "tree_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}))


if __name__ == "__main__":
    main()
