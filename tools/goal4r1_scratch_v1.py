"""Return then remove only positively identified synthetic D0 test fixtures."""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

TASK = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")
EXPORT = Path(str(TASK) + "-return")
TEMP = Path("/tmp/pytest-of-chaw")
RELATIVE = Path(".local/goal4r1-20261105-v1")
ALLOWED_FILES = {".admin.lock", "run/reservations.json", "launch-constructed-v1-0.log"}
START = datetime(2026, 11, 5, 14, 43, 55, tzinfo=timezone.utc).timestamp()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_leaf(path):
    if (not re.fullmatch(r"pytest-[0-9]+", path.parent.name) or
        not re.fullmatch(r"test_launch_failure_keeps_full_[0-9]+", path.name) or path.parent.parent != TEMP):
        raise ValueError("Not an exact task fixture path.")
    for p in (TEMP, path.parent, path):
        if p.is_symlink() or p.resolve(strict=True) != p or p.stat().st_uid != os.getuid() or not p.is_dir():
            raise ValueError("Fixture path/owner differs.")
    rows = []
    for folder, dirs, files in os.walk(path, followlinks=False):
        for name in dirs + files:
            p = Path(folder) / name
            info = p.lstat()
            if p.is_symlink() or info.st_uid != os.getuid() or not p.resolve(strict=True).is_relative_to(path):
                raise ValueError("Unexpected fixture entry.")
            if stat.S_ISREG(info.st_mode):
                rows.append({"path": p.relative_to(path).as_posix(), "bytes": info.st_size, "sha256": sha(p)})
            elif not stat.S_ISDIR(info.st_mode):
                raise ValueError("Unsupported fixture entry.")
    if {r["path"] for r in rows} != ALLOWED_FILES or sum(r["bytes"] for r in rows) > 1024**2:
        raise ValueError("Not the fixed synthetic reservation fixture.")
    reservation = json.loads((path / "run/reservations.json").read_text())
    jobs = reservation["jobs"]
    if len(jobs) != 4 or {j["shard"] for j in jobs} != set(range(4)) or any(
        j["phase"] != "constructed" or j["stage"] != "D0" or j["cpu_limit"] != 5 or j["pid"] is not None
        or j["attempt"] != "v1" or str(j["resource_relative"]) !=
        f".local/goal4r1-20261105-v1/runs/constructed-v1/shard-{j['shard']}/resources.json" for j in jobs
    ):
        raise ValueError("Fixture does not identify this task.")
    if not START <= (path / "run/reservations.json").stat().st_mtime <= START + 3600:
        raise ValueError("Fixture time is outside this task's D0 window.")
    return sorted(rows, key=lambda r: r["path"])


def collect():
    manifest = TASK / RELATIVE / "external-scratch-manifest.json"
    if manifest.exists():
        raise FileExistsError("Preserve fixture collection attempts.")
    sources, skipped = [], 0
    if TEMP.is_dir() and not TEMP.is_symlink():
        for parent in sorted(TEMP.iterdir()):
            if not re.fullmatch(r"pytest-[0-9]+", parent.name) or parent.is_symlink() or not parent.is_dir():
                continue
            for leaf in sorted(parent.glob("test_launch_failure_keeps_full_[0-9]*")):
                try:
                    rows = check_leaf(leaf)
                except (ValueError, OSError, KeyError):
                    skipped += 1
                    continue
                prefix = RELATIVE / "external-scratch" / parent.name / leaf.name
                for row in rows:
                    target = TASK / prefix / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as dest, (leaf / row["path"]).open("rb") as source:
                        shutil.copyfileobj(source, dest)
                    if sha(target) != row["sha256"]:
                        raise ValueError("Fixture copy differs.")
                sources.append({"source": str(leaf), "staged_relative": prefix.as_posix(), "files": rows})
    report = {"status": "PASS_IDENTIFIED_SYNTHETIC_FIXTURES_STAGED_NOT_DELETED", "sources": sources,
              "skipped_nonmatching_directories_not_touched": skipped, "nonempty_fixture_count": len(sources),
              "source_sha256": sha(Path(__file__))}
    with manifest.open("x") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k != "sources"}))


def cleanup():
    if EXPORT.is_symlink() or EXPORT.resolve(strict=True) != EXPORT or EXPORT.stat().st_uid != os.getuid():
        raise ValueError("Wrong verified export root.")
    proof = json.loads((EXPORT / "local-verification.json").read_text())
    manifest = json.loads((EXPORT / "manifest.json").read_text())
    if (proof["status"] != "PASS_LOCAL_ALL_FILES_VERIFIED" or proof["remote_root"] != str(TASK)
        or manifest["root"] != str(TASK) or manifest["file_count"] != proof["file_count"]
        or proof["manifest_sha256"] != sha(EXPORT / "manifest.json")
        or proof["zip_sha256"] != sha(EXPORT / "task.zip") or manifest["tree_sha256"] != proof["tree_sha256"]):
        raise ValueError("Complete local return proof required before fixture deletion.")
    staged = TASK / RELATIVE / "external-scratch-manifest.json"
    records = {r["path"]: r for r in manifest["files"]}
    if records[staged.relative_to(TASK).as_posix()]["sha256"] != sha(staged):
        raise ValueError("Staged fixture manifest was not returned unchanged.")
    sources = json.loads(staged.read_text())["sources"]
    for item in sources:
        path = Path(item["source"])
        if check_leaf(path) != item["files"]:
            raise ValueError("Original synthetic fixture changed.")
        for row in item["files"]:
            key = item["staged_relative"] + "/" + row["path"]
            if records[key]["sha256"] != row["sha256"] or records[key]["bytes"] != row["bytes"]:
                raise ValueError("Fixture bytes absent from complete verified return.")
    for item in sources:
        path = Path(item["source"])
        if check_leaf(path) != item["files"]:
            raise ValueError("Fixture changed immediately before deletion.")
        for row in item["files"]:
            (path / row["path"]).unlink()
        (path / "run").rmdir()
        path.rmdir()  # Never remove pytest parent or unrelated test directories.
    print(json.dumps({"status": "PASS_VERIFIED_SYNTHETIC_FIXTURES_REMOVED", "fixtures": len(sources),
                      "pytest_parent_removed": False, "task_inventory_modified": False}))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["collect", "cleanup"])
    args = p.parse_args()
    if TASK.resolve(strict=True) != TASK or TASK.stat().st_uid != os.getuid():
        raise ValueError("Wrong task root.")
    collect() if args.action == "collect" else cleanup()
