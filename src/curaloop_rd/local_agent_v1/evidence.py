"""Bind public validation evidence to current artifact bytes and dependencies."""

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

VALID_STATES = {"satisfied", "failed", "unknown"}


def canonical_digest(value):
    raw = json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def artifact_identity(root, relative, *, max_bytes=16 * 1024**2):
    """A missing file has no identity; unsafe paths are errors, never evidence."""
    root = Path(root).resolve(strict=True)
    raw = Path(relative)
    if raw.is_absolute() or ".." in raw.parts or not raw.parts or ":" in str(raw):
        raise ValueError("Artifact must be a relative workspace path")
    path = root.joinpath(raw)
    for part in (path, *list(path.parents)[: len(raw.parts) - 1]):
        if part.is_symlink():
            raise ValueError("Artifact symlinks are not admitted")
    if not path.resolve().is_relative_to(root):
        raise ValueError("Artifact escaped its workspace")
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > max_bytes:
        raise ValueError("Artifact is not a bounded regular file")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"sha256": digest, "bytes": path.stat().st_size}


@dataclass(frozen=True)
class Requirement:
    identity: str
    description: str
    artifacts: tuple[str, ...]
    validator_version: str

    def __post_init__(self):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", self.identity):
            raise ValueError("Invalid requirement identity")
        if not self.artifacts or not self.validator_version:
            raise ValueError("A requirement needs artifacts and a validator version")


class EvidenceLedger:
    """Host-owned evidence; model declarations cannot create a validation event."""

    def __init__(self, root, requirements, events=None):
        self.root = Path(root).resolve(strict=True)
        items = list(requirements)
        self.requirements = {r.identity: r for r in items}
        if len(items) != len(self.requirements):
            raise ValueError("Duplicate requirement identity")
        self.events = list(events or [])
        self._check_chain()

    def _check_chain(self):
        previous = None
        for event in self.events:
            body = {k: v for k, v in event.items() if k != "event_digest"}
            if (
                body["previous_digest"] != previous
                or canonical_digest(body) != event["event_digest"]
            ):
                raise ValueError("Evidence history integrity failure")
            previous = event["event_digest"]

    def snapshot(self, requirement_id):
        req = self.requirements[requirement_id]
        return {p: artifact_identity(self.root, p) for p in req.artifacts}

    def record(self, requirement_id, state, detail, *, checked_bindings):
        if state not in VALID_STATES:
            raise ValueError("Invalid evidence state")
        req = self.requirements[requirement_id]
        current = self.snapshot(requirement_id)
        if checked_bindings != current or any(v is None for v in current.values()):
            state, detail = "unknown", "Artifact missing or changed during validation"
        event = {
            "requirement_id": requirement_id,
            "requirement_digest": canonical_digest(asdict(req)),
            "validator_version": req.validator_version,
            "state": state,
            "detail": str(detail)[:4000],
            "bindings": checked_bindings,
            "utc": datetime.now(timezone.utc).isoformat(),
            "previous_digest": self.events[-1]["event_digest"] if self.events else None,
        }
        event["event_digest"] = canonical_digest(event)
        self.events.append(event)
        return self.states()[requirement_id]

    def states(self):
        self._check_chain()
        latest = {e["requirement_id"]: e for e in self.events}
        result = {}
        for identity, req in self.requirements.items():
            event = latest.get(identity)
            reason = "No validation evidence"
            state = "unknown"
            if event:
                current = self.snapshot(identity)
                if event["requirement_digest"] != canonical_digest(asdict(req)):
                    reason = "Requirement or validator version changed"
                elif any(v is None for v in current.values()):
                    reason = "Required artifact missing"
                elif event["bindings"] != current:
                    reason = "Artifact or dependency changed since validation"
                else:
                    state, reason = event["state"], event["detail"]
            result[identity] = {
                "state": state,
                "detail": reason,
                "evidence_digest": event["event_digest"] if event else None,
            }
        return result

    def completion(self):
        states = self.states()
        return {
            "ready": bool(states) and all(s["state"] == "satisfied" for s in states.values()),
            "requirements": states,
            "scope": "Public validators only; not native scientific truth or clinical validation",
        }

    def export(self):
        return {
            "schema": "curaloop.local-agent.evidence.v1",
            "requirements": [asdict(r) for r in self.requirements.values()],
            "events": self.events,
            "current": self.completion(),
        }

    @classmethod
    def restore(cls, root, value):
        if value["schema"] != "curaloop.local-agent.evidence.v1":
            raise ValueError("Unsupported evidence schema")
        requirements = [
            Requirement(**{**r, "artifacts": tuple(r["artifacts"])}) for r in value["requirements"]
        ]
        return cls(root, requirements, value["events"])
