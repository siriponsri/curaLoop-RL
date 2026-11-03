"""Versioned local SQLite storage for public snapshots, never private campaign objects."""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from curaloop.domain import canonical_json

SCHEMA_VERSION = 1
RECOVERY_HELP = (
    "Saved state was retained. Stop the server, copy the database and journal files for investigation, "
    "then set CURALOOP_STORAGE_PATH to a new file and import a validated single-run JSON. "
    "Do not delete or overwrite the original database."
)


class StorageError(RuntimeError):
    """A durable write or integrity check failed; no successful mutation is implied."""


class StaleRevision(StorageError):
    """The durable revision changed before this request committed."""


class CapacityError(StorageError):
    """A local retention or CPU concurrency limit was reached."""


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def encode(value: dict) -> tuple[str, str]:
    payload = canonical_json(value)
    return payload, hashlib.sha256(payload.encode("utf-8")).hexdigest()


def decode(payload: str, checksum: str) -> dict:
    if not isinstance(payload, str) or not isinstance(checksum, str):
        raise StorageError("Saved public snapshot has invalid storage types. " + RECOVERY_HELP)
    if hashlib.sha256(payload.encode("utf-8")).hexdigest() != checksum:
        raise StorageError("Saved public snapshot checksum differs. " + RECOVERY_HELP)
    try:
        value = json.loads(payload)
    except (ValueError, TypeError) as exc:
        raise StorageError("Saved public snapshot is invalid JSON. " + RECOVERY_HELP) from exc
    if not isinstance(value, dict):
        raise StorageError("Saved public snapshot must be an object. " + RECOVERY_HELP)
    return value


class SnapshotStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.connection() as connection:
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version not in (0, SCHEMA_VERSION):
                    raise StorageError(
                        f"Unsupported local storage schema {version}; expected {SCHEMA_VERSION}. "
                        + RECOVERY_HELP
                    )
                check = connection.execute("PRAGMA quick_check").fetchone()[0]
                if check != "ok":
                    raise StorageError("Local storage integrity check failed. " + RECOVERY_HELP)
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                if version == 0 and tables:
                    raise StorageError("Unrecognized local storage schema. " + RECOVERY_HELP)
                if version == 0:
                    connection.executescript(
                        """
                        BEGIN IMMEDIATE;
                        CREATE TABLE runs (
                            session_id TEXT PRIMARY KEY,
                            revision INTEGER NOT NULL CHECK(revision >= 0),
                            snapshot TEXT NOT NULL,
                            checksum TEXT NOT NULL,
                            creation_identity TEXT NOT NULL,
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        );
                        CREATE TABLE run_revisions (
                            session_id TEXT NOT NULL REFERENCES runs(session_id) ON DELETE CASCADE,
                            revision INTEGER NOT NULL,
                            snapshot TEXT NOT NULL,
                            checksum TEXT NOT NULL,
                            saved_at TEXT NOT NULL,
                            PRIMARY KEY(session_id, revision)
                        );
                        CREATE TABLE comparisons (
                            job_id TEXT PRIMARY KEY,
                            status TEXT NOT NULL,
                            snapshot TEXT NOT NULL,
                            checksum TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        );
                        PRAGMA user_version=1;
                        COMMIT;
                        """
                    )
                else:
                    required = {"runs", "run_revisions", "comparisons"}
                    if not required.issubset(tables):
                        raise StorageError("Local storage schema is incomplete. " + RECOVERY_HELP)
        except OSError as exc:
            raise StorageError("Cannot open local storage. " + RECOVERY_HELP) from exc

    @contextmanager
    def connection(self):
        connection = None
        try:
            connection = sqlite3.connect(str(self.path), timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA synchronous=FULL")
            yield connection
            connection.commit()
        except sqlite3.Error as exc:
            if connection is not None:
                connection.rollback()
            raise StorageError("Local storage operation failed. " + RECOVERY_HELP) from exc
        finally:
            if connection is not None:
                connection.close()

    def create_run(self, session_id: str, report: dict, creation_identity: dict) -> None:
        payload, checksum = encode(report)
        now = timestamp()
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] >= 40:
                raise CapacityError(
                    "40 saved campaigns reached. Export and remove an old campaign."
                )
            connection.execute(
                "INSERT INTO runs VALUES (?, 0, ?, ?, ?, ?, ?)",
                (session_id, payload, checksum, canonical_json(creation_identity), now, now),
            )
            connection.execute(
                "INSERT INTO run_revisions VALUES (?, 0, ?, ?, ?)",
                (session_id, payload, checksum, now),
            )

    def update_run(self, session_id: str, expected_revision: int, report: dict) -> None:
        payload, checksum = encode(report)
        now = timestamp()
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            changed = connection.execute(
                "UPDATE runs SET revision=?, snapshot=?, checksum=?, updated_at=? "
                "WHERE session_id=? AND revision=?",
                (expected_revision + 1, payload, checksum, now, session_id, expected_revision),
            ).rowcount
            if changed != 1:
                raise StaleRevision("Stale action rejected; the durable run was not charged twice.")
            connection.execute(
                "INSERT INTO run_revisions VALUES (?, ?, ?, ?, ?)",
                (session_id, expected_revision + 1, payload, checksum, now),
            )

    def run_record(self, session_id: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM runs WHERE session_id=?", (session_id,)
            ).fetchone()
            return dict(row) if row else None

    def run_records(self) -> list[dict]:
        with self.connection() as connection:
            return [
                dict(row)
                for row in connection.execute("SELECT * FROM runs ORDER BY updated_at DESC")
            ]

    def revisions(self, session_id: str) -> list[dict]:
        with self.connection() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT revision, saved_at FROM run_revisions WHERE session_id=? "
                    "ORDER BY revision DESC",
                    (session_id,),
                )
            ]

    def revision_report(self, session_id: str, revision: int) -> dict | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT snapshot, checksum FROM run_revisions WHERE session_id=? AND revision=?",
                (session_id, revision),
            ).fetchone()
            return decode(row["snapshot"], row["checksum"]) if row else None

    def delete_run(self, session_id: str) -> None:
        with self.connection() as connection:
            connection.execute("DELETE FROM runs WHERE session_id=?", (session_id,))

    def create_job(self, job: dict) -> None:
        payload, checksum = encode(job)
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute("SELECT COUNT(*) FROM comparisons").fetchone()[0] >= 20:
                raise CapacityError(
                    "20 saved comparisons reached. Export and remove an old comparison."
                )
            if (
                connection.execute(
                    "SELECT COUNT(*) FROM comparisons WHERE status IN ('queued', 'running')"
                ).fetchone()[0]
                >= 2
            ):
                raise CapacityError("Two CPU comparison jobs are already running.")
            connection.execute(
                "INSERT INTO comparisons VALUES (?, ?, ?, ?, ?)",
                (job["job_id"], job["status"], payload, checksum, timestamp()),
            )

    def update_job(self, job: dict, expected_status: str) -> None:
        payload, checksum = encode(job)
        with self.connection() as connection:
            changed = connection.execute(
                "UPDATE comparisons SET status=?, snapshot=?, checksum=?, updated_at=? "
                "WHERE job_id=? AND status=?",
                (job["status"], payload, checksum, timestamp(), job["job_id"], expected_status),
            ).rowcount
            if changed != 1:
                raise StaleRevision("Comparison state changed; its result was not overwritten.")

    def job(self, job_id: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT snapshot, checksum FROM comparisons WHERE job_id=?", (job_id,)
            ).fetchone()
            return decode(row["snapshot"], row["checksum"]) if row else None

    def job_records(self) -> list[dict]:
        with self.connection() as connection:
            return [
                dict(row)
                for row in connection.execute("SELECT * FROM comparisons ORDER BY updated_at DESC")
            ]

    def delete_job(self, job_id: str) -> bool:
        with self.connection() as connection:
            return bool(
                connection.execute(
                    "DELETE FROM comparisons WHERE job_id=? AND status NOT IN ('queued','running')",
                    (job_id,),
                ).rowcount
            )
