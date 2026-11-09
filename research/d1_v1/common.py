"""Fresh D1 authority, immutable artifacts and budget checks."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / ".local/d1-operation-headroom-20261109-v1"
OLD = ROOT / ".local/m2-costed-20261108-v2"
PUBLIC = ROOT / "docs/evidence/d1-operation-headroom-20261109-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.write("\n")


def now():
    return datetime.now(timezone.utc)


def authority():
    release = read(TASK / "release.json")
    assert release["owner_approval"] == "อนุมัติ D1 ครับ"
    assert release["final_outcomes_open"] is False
    assert now() < datetime.fromisoformat(release["deadline_utc"])
    ledger = read(TASK / "ledger.json")
    assert ledger["status"] == "ACTIVE"
    assert sum(ledger["retained_reservations_seconds"].values()) <= 14400
    assert sha(OLD / "ledger.json") == release["old_m2_ledger_sha256"]
    return release, ledger


def save_ledger(ledger):
    assert sum(ledger["retained_reservations_seconds"].values()) <= 14400
    temporary = TASK / "ledger.next.json"
    with temporary.open("x", encoding="utf-8") as file:
        json.dump(ledger, file, indent=2, allow_nan=False)
        file.write("\n")
    os.replace(temporary, TASK / "ledger.json")


def start_job(name):
    from research.longrun_v1.guard import ResourceGuard

    _, ledger = authority()
    assert name not in ledger["jobs"], "NO_AUTOMATIC_JOB_REPLAY"
    permit = read(TASK / "permits" / (name + ".json"))
    ledger["jobs"][name] = {"status": "RESERVED", "permit_sha256": sha(TASK / "permits" / (name + ".json"))}
    save_ledger(ledger)
    guard = ResourceGuard(TASK / "jobs" / name / "resource.json", permit)
    return guard


def finish_job(name, guard, status):
    guard.finish(status)
    ledger = read(TASK / "ledger.json")
    ledger["jobs"][name]["status"] = status
    ledger["jobs"][name]["resource_sha256"] = sha(TASK / "jobs" / name / "resource.json")
    save_ledger(ledger)
