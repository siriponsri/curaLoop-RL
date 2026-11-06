"""Local state transitions, content-checked bundles and idempotent previews."""

import hashlib
import json
import os
import re
import sqlite3
import uuid
from pathlib import Path

from .contracts import WorkflowError, canonical, identity, validate_plan


def report_markdown(plan):
    lines = ["# Offline R&D study proposal", "", plan["question"], "",
             "**OFFLINE FIXTURE/METADATA WORKFLOW; NO SCIENTIFIC RESULTS.**", "",
             f"Plan SHA256: `{plan['plan_sha256']}`", "",
             f"Target: {plan['target']}; endpoint: {plan['endpoint']}; unit: {plan['unit']}.",
             f"Illustrative planned cost: {plan['planned_cost']} / {plan['budget']}.", "",
             "## Source ledger", ""]
    for record in plan["evidence"]:
        lines.extend([f"- {record['source_id']}: {record['citation']}, version {record['version']}, "
                      f"location {record['locator']}. Status: {record['measurement_status']}. "
                      f"Synthetic fixture: {record['synthetic']}.",
                      f"  Source statement: {record['statement']}"])
    lines.extend(["", "## Limits", "",
                  "Measurement statuses remain distinct; missing, censored, default-filled and "
                  "predicted values are not automatically measured positive or negative outcomes.",
                  "No measurements were ordered, no confirmed hits counted, and no report delivered externally.",
                  "The workflow validates declared evidence; it does not establish that every source statement is true.",
                  "", "Flagged statuses: " + (", ".join(plan["limitations"]) or "none"), ""])
    return "\n".join(lines)


class Workflow:
    def __init__(self, root):
        self.root = Path(root).absolute()
        if self.root.is_symlink() or self.root.resolve() != self.root:
            raise WorkflowError("UNSAFE_PATH", "Output root must be canonical")
        self.root.mkdir(parents=True, exist_ok=True)
        for name in ("state.sqlite3", "bundles"):
            if (self.root / name).is_symlink():
                raise WorkflowError("UNSAFE_PATH", name)
        self.connection = sqlite3.connect(self.root / "state.sqlite3")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY, plan_hash TEXT NOT NULL,
                plan_json TEXT NOT NULL, revision INTEGER NOT NULL,
                phase TEXT NOT NULL, bundle_hash TEXT);
            CREATE TABLE IF NOT EXISTS previews (
                run_id TEXT PRIMARY KEY, receipt_json TEXT NOT NULL);
        """)

    def close(self):
        self.connection.close()

    def start(self, run_id, plan):
        if type(run_id) is not str or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", run_id):
            raise WorkflowError("UNSAFE_PATH", "Invalid run ID")
        validate_plan(plan)
        with self.connection:
            self.connection.execute("INSERT OR IGNORE INTO runs VALUES (?,?,?,0,'VALIDATED',NULL)",
                                    (run_id, plan["plan_sha256"], canonical(plan)))
            row = self._row(run_id)
            if row["plan_hash"] != plan["plan_sha256"] or row["plan_json"] != canonical(plan):
                raise WorkflowError("RUN_ID_CONFLICT", run_id)
        return dict(row)

    def _row(self, run_id):
        row = self.connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise WorkflowError("UNKNOWN_RUN", run_id)
        return row

    def state(self, run_id):
        return dict(self._row(run_id))

    @staticmethod
    def _stored_plan(row):
        try:
            plan = validate_plan(json.loads(row["plan_json"]))
        except (TypeError, json.JSONDecodeError) as exc:
            raise WorkflowError("PLAN_IDENTITY_MISMATCH", "Stored plan is malformed") from exc
        expected_revisions = {"VALIDATED": 0, "REPORT_READY": 1, "PREVIEW_READY": 2}
        if (row["plan_hash"] != plan["plan_sha256"]
                or row["phase"] not in expected_revisions
                or row["revision"] != expected_revisions[row["phase"]]):
            raise WorkflowError("PLAN_IDENTITY_MISMATCH", "Stored plan/state identity differs")
        return plan

    @staticmethod
    def _revision(row, expected):
        if type(expected) is not int or row["revision"] != expected:
            raise WorkflowError("STALE_REVISION", "Expected current revision")

    @staticmethod
    def _write_staged(path, data):
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

    def _write_once(self, folder, name, data):
        if folder.is_symlink() or folder.resolve() != folder:
            raise WorkflowError("UNSAFE_PATH", "Bundle folder is aliased")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        if path.is_symlink():
            raise WorkflowError("UNSAFE_PATH", "Bundle file is aliased")
        if path.exists():
            if path.read_bytes() != data:
                raise WorkflowError("BUNDLE_CONTENT_CONFLICT", name)
            return
        partial = folder / ("." + name + ".partial-" + uuid.uuid4().hex)
        self._write_staged(partial, data)
        try:
            # Publish complete bytes atomically without replacing an existing file.
            os.link(partial, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != data:
                raise WorkflowError("BUNDLE_CONTENT_CONFLICT", name)
        partial.unlink()

    def build_report(self, run_id, expected_revision):
        db = self.connection
        db.execute("BEGIN IMMEDIATE")
        try:
            row = self._row(run_id)
            self._revision(row, expected_revision)
            plan = self._stored_plan(row)
            bundle = {"schema": "curaloop.report-bundle.v1", "plan": plan,
                      "scientific_results": None, "external_delivery": False}
            digest = identity(bundle)
            folder = self.root / "bundles" / digest
            payloads = {"bundle.json": (canonical(bundle) + "\n").encode(),
                        "report.md": report_markdown(plan).encode()}
            for name, data in payloads.items():
                self._write_once(folder, name, data)
            manifest = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
            self._write_once(folder, "manifest.json", (canonical(manifest) + "\n").encode())
            if row["phase"] == "VALIDATED":
                db.execute("UPDATE runs SET phase='REPORT_READY', revision=revision+1, bundle_hash=? WHERE run_id=?",
                           (digest, run_id))
            elif row["bundle_hash"] != digest:
                raise WorkflowError("BUNDLE_CONTENT_CONFLICT", "Stored digest differs")
            db.commit()
            return {"bundle_sha256": digest, "folder": str(folder),
                    "revision": self._row(run_id)["revision"], "external_delivery": False}
        except BaseException:
            db.rollback()
            raise

    def preview_delivery(self, run_id, expected_revision):
        db = self.connection
        db.execute("BEGIN IMMEDIATE")
        try:
            row = self._row(run_id)
            if not (row["phase"] == "PREVIEW_READY" and type(expected_revision) is int
                    and expected_revision in (row["revision"], row["revision"] - 1)):
                self._revision(row, expected_revision)
            if row["phase"] not in ("REPORT_READY", "PREVIEW_READY"):
                raise WorkflowError("REPORT_NOT_READY", run_id)
            # Revalidate stored plan and files, including retries after interruption.
            plan = self._stored_plan(row)
            bundle = {"schema": "curaloop.report-bundle.v1", "plan": plan,
                      "scientific_results": None, "external_delivery": False}
            digest = identity(bundle)
            folder = self.root / "bundles" / digest
            if row["bundle_hash"] != digest or folder.is_symlink() or folder.resolve() != folder:
                raise WorkflowError("BUNDLE_CONTENT_CONFLICT", "Bundle identity differs")
            expected = {"bundle.json": (canonical(bundle) + "\n").encode(),
                        "report.md": report_markdown(plan).encode()}
            expected["manifest.json"] = (canonical({k: hashlib.sha256(v).hexdigest()
                                                   for k, v in expected.items()}) + "\n").encode()
            for name, data in expected.items():
                path = folder / name
                if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
                    raise WorkflowError("BUNDLE_CONTENT_CONFLICT", name)
            existing = db.execute("SELECT receipt_json FROM previews WHERE run_id=?", (run_id,)).fetchone()
            if existing:
                try:
                    receipt = json.loads(existing[0])
                except json.JSONDecodeError as exc:
                    raise WorkflowError("PREVIEW_IDENTITY_MISMATCH", "Malformed receipt") from exc
                expected_receipt = {"schema": "curaloop.delivery-preview.v1", "run_id": run_id,
                                    "bundle_sha256": digest, "destination": "LOCAL_PREVIEW_ONLY",
                                    "delivered": False, "revision": row["revision"]}
                if row["phase"] != "PREVIEW_READY" or receipt != expected_receipt:
                    raise WorkflowError("PREVIEW_IDENTITY_MISMATCH", "Stored receipt differs")
                db.commit()
                return receipt
            if row["phase"] == "PREVIEW_READY":
                raise WorkflowError("PREVIEW_IDENTITY_MISMATCH", "Committed preview receipt is missing")
            receipt = {"schema": "curaloop.delivery-preview.v1", "run_id": run_id,
                       "bundle_sha256": digest, "destination": "LOCAL_PREVIEW_ONLY",
                       "delivered": False, "revision": row["revision"] + 1}
            db.execute("INSERT INTO previews VALUES (?,?)", (run_id, canonical(receipt)))
            db.execute("UPDATE runs SET phase='PREVIEW_READY', revision=revision+1 WHERE run_id=?", (run_id,))
            db.commit()
            return receipt
        except BaseException:
            db.rollback()
            raise
