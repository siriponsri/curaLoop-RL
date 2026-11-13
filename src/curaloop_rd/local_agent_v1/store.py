"""Separate durable local-workflow jobs; no legacy database migration."""

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "INTERRUPTED", "ABSTAINED"}


class JobConflict(ValueError):
    pass


class JobStore:
    def __init__(self, root):
        root = Path(root)
        if root.is_symlink():
            raise ValueError("Workflow storage cannot be a symlink")
        root.mkdir(parents=True, exist_ok=True)
        self.root = root.resolve()
        self.database = self.root / "jobs.sqlite3"
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError("Unsupported local workflow database version")
            db.execute(
                "CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, revision INTEGER NOT NULL, payload TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS events (id TEXT NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(id,revision))"
            )
            db.execute("PRAGMA user_version=1")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def folder(self, identity):
        if not re.fullmatch(r"[0-9a-f]{32}", identity):
            raise ValueError("Invalid workflow job ID")
        path = self.root / identity
        if path.is_symlink():
            raise ValueError("Job folder cannot be a symlink")
        return path

    def create(self, spec):
        identity = uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "job_id": identity,
            "revision": 0,
            "state": "QUEUED",
            "spec": spec,
            "created_utc": now,
            "updated_utc": now,
            "attempt": 0,
            "provider_calls": [],
            "parameters": spec["parameters"] if spec["mode"] == "deterministic" else None,
            "result": None,
            "error": None,
            "process": None,
        }
        self.folder(identity).mkdir(exist_ok=False)
        with self.connect() as db:
            if db.execute("SELECT count(*) FROM jobs").fetchone()[0] >= 32:
                raise JobConflict("Local workflow storage reached its 32-job limit")
            payload = json.dumps(row, ensure_ascii=False, allow_nan=False)
            db.execute("INSERT INTO jobs VALUES (?,?,?)", (identity, 0, payload))
            db.execute(
                "INSERT INTO events VALUES (?,?,?)",
                (identity, 0, json.dumps({"state": "QUEUED", "utc": now})),
            )
        return row

    def read(self, identity):
        self.folder(identity)
        with self.connect() as db:
            value = db.execute("SELECT payload FROM jobs WHERE id=?", (identity,)).fetchone()
        if value is None:
            raise FileNotFoundError(identity)
        return json.loads(value[0])

    def list(self):
        with self.connect() as db:
            rows = [
                json.loads(r[0]) for r in db.execute("SELECT payload FROM jobs ORDER BY rowid DESC")
            ]
        return [
            {
                k: r[k]
                for k in (
                    "job_id",
                    "revision",
                    "state",
                    "created_utc",
                    "updated_utc",
                    "attempt",
                    "error",
                )
            }
            | {"mode": r["spec"]["mode"], "counts": r["result"]["counts"] if r["result"] else None}
            for r in rows
        ]

    def update(self, identity, expected_revision, *, detail, **patch):
        permitted = {
            "state",
            "attempt",
            "provider_calls",
            "parameters",
            "result",
            "error",
            "process",
        }
        if not set(patch).issubset(permitted):
            raise ValueError("Unknown workflow state field")
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            value = db.execute(
                "SELECT payload,revision FROM jobs WHERE id=?", (identity,)
            ).fetchone()
            if value is None:
                raise FileNotFoundError(identity)
            if value[1] != expected_revision:
                raise JobConflict("Workflow revision changed; refresh before acting")
            row = json.loads(value[0])
            row.update(patch, revision=expected_revision + 1, updated_utc=now)
            db.execute(
                "UPDATE jobs SET revision=?,payload=? WHERE id=?",
                (row["revision"], json.dumps(row, ensure_ascii=False, allow_nan=False), identity),
            )
            event = {"utc": now, "detail": detail, "changes": patch}
            db.execute(
                "INSERT INTO events VALUES (?,?,?)",
                (identity, row["revision"], json.dumps(event, ensure_ascii=False, allow_nan=False)),
            )
        return row

    def history(self, identity):
        self.read(identity)
        with self.connect() as db:
            return [
                {"revision": n, **json.loads(p)}
                for n, p in db.execute(
                    "SELECT revision,payload FROM events WHERE id=? ORDER BY revision", (identity,)
                )
            ]

    def recover_interrupted(self):
        for item in self.list():
            if item["state"] not in TERMINAL:
                self.update(
                    item["job_id"],
                    item["revision"],
                    state="INTERRUPTED",
                    detail="Previous server stopped. Recorded PIDs are historical; no process was killed and no model or computation was repeated.",
                    process=None,
                    error="REVIEW_AND_EXPLICIT_RESUME_REQUIRED",
                )
