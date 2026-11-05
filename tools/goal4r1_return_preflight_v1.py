"""Record/remove only pytest convenience aliases; retain every target byte."""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

TASK = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")
EXPORT = Path(str(TASK) + "-return")
SCRATCH = TASK / ".local/goal4r1-20261105-v1/reporting-test-temp-v1"


def main():
    if TASK.resolve(strict=True) != TASK or TASK.stat().st_uid != os.getuid():
        raise ValueError("Wrong task root.")
    started, cpu = time.perf_counter(), time.process_time()
    rows = []
    for folder, dirs, files in os.walk(TASK, followlinks=False):
        for name in dirs + files:
            p = Path(folder) / name
            if not p.is_symlink():
                continue
            target = p.resolve(strict=True)
            if (p.parent != SCRATCH or not p.name.startswith("test_") or not p.name.endswith("current") or
                p.lstat().st_uid != os.getuid() or target.parent != SCRATCH or not target.is_dir() or
                not target.name.startswith(p.name[:-len("current")]) or target.is_symlink()):
                raise ValueError("Unexpected link; do not remove aliases or snapshot.")
            rows.append({"path": p.relative_to(TASK).as_posix(), "link_text": os.readlink(p),
                         "target_relative": target.relative_to(TASK).as_posix()})
    record = TASK / "docs/evidence/goal4r1-20261105-v1/return-preflight-v1.json"
    if record.exists():
        raise FileExistsError("Preserve preflight attempts.")
    # First preserve all link identities; unlink aliases only, never target trees.
    report = {"status": "PASS_ONLY_PYTEST_CONVENIENCE_ALIASES_IDENTIFIED", "utc": datetime.now(timezone.utc).isoformat(),
              "aliases": rows, "regular_target_bytes_deleted": 0,
              "initial_snapshot_attempt": "Stopped before archive creation because aliases were present",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with record.open("x") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    for row in rows:
        p = TASK / row["path"]
        if not p.is_symlink() or os.readlink(p) != row["link_text"] or p.resolve() != TASK / row["target_relative"]:
            raise ValueError("Alias changed before unlink.")
        p.unlink()
    removed_empty = False
    if EXPORT.exists():
        if EXPORT.is_symlink() or EXPORT.resolve(strict=True) != EXPORT or EXPORT.stat().st_uid != os.getuid() or any(EXPORT.iterdir()):
            raise ValueError("Keep nonempty or unexpected prior export.")
        EXPORT.rmdir()  # Empty failed-attempt directory only; contains no file bytes.
        removed_empty = True
    print(json.dumps({"status": "PASS_RECORDED_ALIAS_METADATA_TARGET_BYTES_RETAINED", "aliases_removed": len(rows),
                      "regular_files_removed": 0, "empty_failed_export_removed": removed_empty,
                      "cpu_seconds": time.process_time() - cpu, "wall_seconds": time.perf_counter() - started}))


if __name__ == "__main__":
    main()
