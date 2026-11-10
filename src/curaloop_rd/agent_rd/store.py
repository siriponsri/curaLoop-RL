"""Separate additive mission store; atomic snapshots and hash-chained events."""

import hashlib
import json
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .contracts import canonical, digest


def stamp():
    return datetime.now(timezone.utc).isoformat()


class MissionConflict(ValueError):
    pass


class MissionStore:
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.lock = threading.RLock()
        self.safe()
        self.root.mkdir(parents=True, exist_ok=True)

    def safe(self):
        if any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise ValueError("Mission store must not follow symlinks")

    def path(self, identity):
        if str(uuid.UUID(identity)) != identity:
            raise ValueError("Canonical mission UUID required")
        self.safe()
        path = self.root / (identity + ".json")
        if path.is_symlink():
            raise ValueError("Mission file must not be a symlink")
        return path

    def _write(self, row):
        path = self.path(row["mission_id"])
        envelope = {"payload": row, "sha256": digest(row)}
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", prefix=".mission-", dir=self.root, delete=False) as output:
                temporary = Path(output.name)
                output.write(canonical(envelope))
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, path)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()

    def create(self, spec, *, system="P", seed=17011):
        with self.lock:
            identity = str(uuid.uuid4())
            row = {"schema": "curaloop.agent-rd.mission.v1", "mission_id": identity,
                   "spec": spec.model_dump(), "spec_sha256": digest(spec.model_dump()), "system": system, "seed": seed,
                   "implementation_id": digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))}),
                   "revision": 0, "state": "DRAFT", "created_utc": stamp(), "events": [], "calls": [],
                   "tool_receipts": [], "candidate": None, "released": None, "verification": None,
                   "fallback": None, "error": None, "evidence": None, "derived": None,
                   "limits": {"model_calls": 3, "tool_calls": 2, "repair_calls_within_total": 2, "max_output_tokens_per_call": 256},
                   "cost": {"paid_cost_usd": 0, "model_calls": 0, "tool_calls": 0, "model_tokens": 0,
                            "model_cpu_seconds": 0, "model_wall_seconds": 0, "failed_calls": 0}}
            self._write(row)
            return row

    def read(self, identity):
        with self.lock:
            envelope = json.loads(self.path(identity).read_text(encoding="utf-8"))
            row = envelope["payload"]
            if digest(row) != envelope["sha256"] or row["spec_sha256"] != digest(row["spec"]):
                raise ValueError("Mission integrity check failed; preserve original file")
            previous = None
            for event in row["events"]:
                actual = {k: v for k, v in event.items() if k != "sha256"}
                if event["previous"] != previous or digest(actual) != event["sha256"]:
                    raise ValueError("Mission event integrity check failed")
                previous = event["sha256"]
            return row

    def update(self, identity, expected_revision, state, detail, **changes):
        with self.lock:
            row = self.read(identity)
            if row["revision"] != expected_revision:
                raise MissionConflict("Refresh the mission before retrying a stale action")
            event = {"revision": expected_revision + 1, "state": state, "detail": detail, "utc": stamp(),
                     "previous": row["events"][-1]["sha256"] if row["events"] else None}
            event["sha256"] = digest(event)
            row.update(changes, state=state, revision=expected_revision + 1)
            row["events"].append(event)
            self._write(row)
            return row

    def list(self):
        self.safe()
        rows, errors = [], []
        for path in sorted(self.root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:100]:
            try:
                row = self.read(path.stem)
                rows.append({k: row[k] for k in ("mission_id", "revision", "state", "created_utc", "spec", "cost")})
            except (ValueError, OSError, KeyError) as exc:
                errors.append({"mission_id": path.stem, "error": str(exc)})
        return {"items": rows, "integrity_issues": errors}
