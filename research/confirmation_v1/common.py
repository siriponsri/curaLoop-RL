"""Fresh LR-CF1 authority and conservative accounting; old ledgers read only."""

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / ".local/lr-cf1-20261109-v1"
PUBLIC = ROOT / "docs/evidence/lr-cf1-20261109-v1"
REMOTE = "/home/chaw/curaloop-tasks/lr-cf1-20261109-v1"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1048576), b""):
            value.update(block)
    return value.hexdigest()


def new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.write("\n")


def now():
    return datetime.now(timezone.utc)


def save(ledger):
    assert sum(ledger["retained_seconds"].values()) <= 172800
    path = TASK / "ledger.next.json"
    new(path, ledger)
    os.replace(path, TASK / "ledger.json")


def authority():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert release["owner_instruction"] == "อนุมัติ contribution และ LR-CF1 ตามแผน (แนะนำ)"
    assert ledger["status"] == "ACTIVE" and now() < datetime.fromisoformat(release["deadline_utc"])
    assert all(sha(ROOT / name) == digest for name, digest in release["prior_ledger_pins"].items())
    return release, ledger


def start(name, cpu=120, wall=300, bucket="admission_and_calibration", orchestration=False):
    release, ledger = authority()
    assert name not in ledger["bookings"]
    if bucket != "utilities_return_handoff_delivery":
        ledger["retained_seconds"][bucket] = ledger["retained_seconds"].get(bucket, 0) + cpu
        assert ledger["retained_seconds"][bucket] <= ledger["stage_caps_seconds"][bucket]
    else:
        assert sum(b["cpu_cap"] for b in ledger["bookings"].values() if b["bucket"] == bucket) + cpu <= 43200
    permit = {"attempt": name, "token": secrets.token_hex(16), "host": "local", "cpu": 0,
              "guard_cpu_seconds": cpu, "wall_seconds": wall, "memory_bytes": 1073741824,
              "deadline_utc": release["deadline_utc"], "bundle_sha256": release["plan_sha256"]}
    ledger["bookings"][name] = {"status": "RESERVED", "bucket": bucket, "cpu_cap": cpu, "host": "local"}
    save(ledger)
    new(TASK / "jobs" / name / "permit.json", permit)
    if orchestration:
        from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
        return OrchestrationGuard(TASK / "jobs" / name / "resource.json", cpu, release["deadline_utc"], wall)
    from research.longrun_v1.guard import ResourceGuard
    return ResourceGuard(TASK / "jobs" / name / "resource.json", permit)


def finish(name, guard, status):
    guard.finish(status)
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][name].update(status=status, resource_sha256=sha(TASK / "jobs" / name / "resource.json"))
    save(ledger)
