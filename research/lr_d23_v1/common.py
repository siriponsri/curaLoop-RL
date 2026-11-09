"""Fresh LR-D23 accounting and immutable artifacts; no prior-root mutation."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / ".local/lr-d23-20261109-v1"
PUBLIC = ROOT / "docs/evidence/lr-d23-20261109-v1"
REMOTE = "/home/chaw/curaloop-tasks/lr-d23-20261109-v1"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.write("\n")


def now():
    return datetime.now(timezone.utc)


def ledger_save(value):
    assert sum(value["retained_seconds"].values()) <= 86400
    temporary = TASK / "ledger.next.json"
    with temporary.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.write("\n")
    os.replace(temporary, TASK / "ledger.json")


def authority():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert release["owner_instruction"] == "อนุมัติ goal long run"
    assert ledger["status"] == "ACTIVE" and now() < datetime.fromisoformat(release["deadline_utc"])
    assert sum(ledger["retained_seconds"].values()) <= 86400
    assert all(sha(ROOT / name) == value for name, value in release["prior_ledger_pins"].items())
    return release, ledger


def utility_start(name, cpu_seconds=120, wall_seconds=300, memory_bytes=1073741824):
    import secrets

    from research.longrun_v1.guard import ResourceGuard

    release, ledger = authority()
    assert name not in ledger["bookings"]
    permit = {"attempt": name, "token": secrets.token_hex(16), "host": "local", "cpu": 0,
              "guard_cpu_seconds": cpu_seconds, "wall_seconds": wall_seconds,
              "memory_bytes": memory_bytes, "deadline_utc": release["deadline_utc"],
              "bundle_sha256": release["proposal_sha256"], "bucket": "utilities_handoff"}
    ledger["bookings"][name] = {"status": "RESERVED", "host": "local", "bucket": "utilities_handoff",
                                "guard_cpu_seconds": cpu_seconds}
    ledger_save(ledger)
    new(TASK / "jobs" / name / "permit.json", permit)
    return ResourceGuard(TASK / "jobs" / name / "resource.json", permit)


def utility_finish(name, guard, status):
    guard.finish(status)
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][name]["status"] = status
    ledger["bookings"][name]["resource_sha256"] = sha(TASK / "jobs" / name / "resource.json")
    ledger_save(ledger)


def orchestration_start(name, cpu_seconds, wall_seconds=None):
    from tools.m2c_orchestration_guard_v2 import OrchestrationGuard

    release, ledger = authority()
    assert name not in ledger["bookings"]
    permit = {"host": "local", "bucket": "utilities_handoff", "aggregate_cpu_seconds": cpu_seconds,
              "deadline_utc": release["deadline_utc"], "wall_seconds": wall_seconds}
    new(TASK / "jobs" / name / "permit.json", permit)
    ledger["bookings"][name] = {"status": "RESERVED", **permit}
    ledger_save(ledger)
    return OrchestrationGuard(TASK / "jobs" / name / "resource.json", cpu_seconds,
                              release["deadline_utc"], wall_seconds)
