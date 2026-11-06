"""Frozen 12 engineering cases plus meaningful boundary/integrity regressions."""

import dataclasses
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from curaloop_rd.contracts import WorkflowError, draft_plan, identity, inspect_source, validate_plan
from curaloop_rd.demo import brief, catalogue
from curaloop_rd.workflow import Workflow


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rd-case-")
        self.root = Path(self.temp.name)
        self.flow = Workflow(self.root)
        self.plan = draft_plan(brief(), catalogue())

    def tearDown(self):
        self.flow.close()
        self.temp.cleanup()

    def report(self, plan=None):
        self.flow.start("example", plan or self.plan)
        return self.flow.build_report("example", 0)

    def error(self, code, fn):
        with self.assertRaises(WorkflowError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)


class Cases(Fixture):
    def test_N01_single_source_report(self):
        report = self.report()
        payload = json.loads((Path(report["folder"]) / "bundle.json").read_text())
        self.assertEqual(payload["plan"]["evidence"][0]["source_id"], "fixture_measured")
        self.assertIsNone(payload["scientific_results"])
        self.assertFalse(payload["external_delivery"])
        self.assertEqual(self.flow.state("example")["phase"], "REPORT_READY")

    def test_N02_provenance_retention(self):
        plan = draft_plan(brief(("fixture_measured", "fixture_paper")), catalogue())
        report = self.report(plan)
        text = (Path(report["folder"]) / "report.md").read_text()
        for record in plan["evidence"]:
            for value in (record["source_id"], record["citation"], record["version"], record["locator"]):
                self.assertIn(value, text)

    def test_N03_measurement_status_preservation(self):
        plan = draft_plan(brief(tuple(catalogue())), catalogue())
        report = self.report(plan)
        payload = json.loads((Path(report["folder"]) / "bundle.json").read_text())
        self.assertEqual({r["measurement_status"] for r in payload["plan"]["evidence"]},
                         {"measured_exact", "metadata_only", "tested_censored", "default_filled",
                          "missing", "untested", "predicted"})
        self.assertIsNone(payload["plan"]["confirmed_hits"])
        self.assertTrue(payload["plan"]["synthetic_fixture_present"])

    def test_N04_exact_budget(self):
        plan = draft_plan(brief(request_count=3, unit_cost=.1, budget=.3), catalogue())
        self.assertEqual(plan["planned_cost"], .3)
        self.report(plan)

    def test_N05_completed_replay(self):
        first = self.report()
        state = self.flow.start("example", self.plan)
        second = self.flow.build_report("example", state["revision"])
        self.assertEqual(first, second)
        self.assertEqual(len(list((self.root / "bundles").iterdir())), 1)

    def test_N06_preview_is_local(self):
        report = self.report()
        receipt = self.flow.preview_delivery("example", report["revision"])
        self.assertFalse(receipt["delivered"])
        self.assertEqual(receipt["destination"], "LOCAL_PREVIEW_ONLY")

    def test_F01_unavailable_source(self):
        records = catalogue()
        records["fixture_measured"] = dataclasses.replace(records["fixture_measured"], available=False)
        self.error("SOURCE_UNAVAILABLE", lambda: draft_plan(brief(), records))
        self.assertEqual(self.flow.connection.execute("SELECT count(*) FROM runs").fetchone()[0], 0)

    def test_F02_conflicting_endpoint(self):
        records = catalogue()
        records["fixture_paper"] = dataclasses.replace(records["fixture_paper"], endpoint="OTHER_PHENOTYPE")
        self.error("ENDPOINT_CONFLICT", lambda: draft_plan(brief(tuple(records)), records))

    def test_F03_reserved_payload_not_inspected(self):
        class NeverRead:
            def __deepcopy__(self, memo):
                raise AssertionError("Reserved payload was inspected")
        source = dataclasses.replace(catalogue()["fixture_measured"], source_id="fixture_reserved",
                                     role="final_reserved", statement=NeverRead())
        self.error("RESERVED_EVIDENCE", lambda: inspect_source({source.source_id: source}, source.source_id))
        forged = dataclasses.replace(source, source_id="alias_fixture_reserved", role="development_fixture")
        self.error("RESERVED_EVIDENCE", lambda: inspect_source({forged.source_id: forged}, forged.source_id))

    def test_F04_stale_revision(self):
        self.report()
        before = self.flow.state("example")
        self.error("STALE_REVISION", lambda: self.flow.build_report("example", 0))
        self.assertEqual(self.flow.state("example"), before)

    def test_F05_interrupted_report_recovers(self):
        self.flow.start("example", self.plan)
        def interrupt(path, data):
            path.write_bytes(data[:10])
            raise RuntimeError("Synthetic interruption during staged file write")
        with patch.object(self.flow, "_write_staged", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "Synthetic interruption"):
                self.flow.build_report("example", 0)
        self.assertEqual(self.flow.state("example")["phase"], "VALIDATED")
        self.assertEqual(self.flow.connection.execute("SELECT count(*) FROM previews").fetchone()[0], 0)
        self.flow.close()
        self.flow = Workflow(self.root)
        report = self.flow.build_report("example", 0)
        self.assertEqual(self.flow.state("example")["phase"], "REPORT_READY")
        self.assertTrue((Path(report["folder"]) / "manifest.json").is_file())
        self.assertEqual(len(list(Path(report["folder"]).glob(".*.partial-*"))), 1)

    def test_F06_duplicate_preview(self):
        report = self.report()
        first = self.flow.preview_delivery("example", report["revision"])
        second = self.flow.preview_delivery("example", report["revision"])
        self.assertEqual(first, second)
        self.assertEqual(first, self.flow.preview_delivery("example", first["revision"]))
        self.assertEqual(self.flow.connection.execute("SELECT count(*) FROM previews").fetchone()[0], 1)
        self.assertEqual(self.flow.state("example")["revision"], first["revision"])


class Boundaries(Fixture):
    def test_stored_plan_hash_is_verified(self):
        self.flow.start("example", self.plan)
        with self.flow.connection:
            self.flow.connection.execute("UPDATE runs SET plan_hash='wrong' WHERE run_id='example'")
        self.error("PLAN_IDENTITY_MISMATCH", lambda: self.flow.build_report("example", 0))

    def test_stored_preview_is_verified(self):
        report = self.report()
        receipt = self.flow.preview_delivery("example", report["revision"])
        forged = dict(receipt, delivered=True)
        with self.flow.connection:
            self.flow.connection.execute("UPDATE previews SET receipt_json=?", (json.dumps(forged),))
        self.error("PREVIEW_IDENTITY_MISMATCH", lambda: self.flow.preview_delivery("example", receipt["revision"]))

    def test_invalid_numerics_and_budget(self):
        for changes in ({"budget": float("nan")}, {"unit_cost": float("inf")},
                        {"request_count": True}, {"budget": -1}, {"budget": 5}):
            with self.assertRaises(WorkflowError):
                draft_plan(brief(**changes), catalogue())

    def test_changed_run_identity_is_rejected(self):
        self.report()
        changed = draft_plan(brief(question="A different question"), catalogue())
        self.error("RUN_ID_CONFLICT", lambda: self.flow.start("example", changed))

    def test_tampered_report_cannot_be_previewed(self):
        report = self.report()
        (Path(report["folder"]) / "report.md").write_text("Altered report")
        self.error("BUNDLE_CONTENT_CONFLICT", lambda: self.flow.preview_delivery("example", 1))
        self.assertEqual(self.flow.connection.execute("SELECT count(*) FROM previews").fetchone()[0], 0)

    def test_tampered_plan_and_forged_derived_fields(self):
        changed = dict(self.plan, confirmed_hits=999)
        self.error("PLAN_IDENTITY_MISMATCH", lambda: validate_plan(changed))
        changed["plan_sha256"] = identity({k: v for k, v in changed.items() if k != "plan_sha256"})
        self.error("PLAN_IDENTITY_MISMATCH", lambda: validate_plan(changed))

    def test_unknown_role_and_incompatible_unit(self):
        records = catalogue()
        records["fixture_measured"] = dataclasses.replace(records["fixture_measured"], role="unknown")
        self.error("EXPOSURE_UNCLEARED", lambda: draft_plan(brief(), records))
        self.error("ENDPOINT_CONFLICT", lambda: draft_plan(brief(unit="nM"), catalogue()))

    def test_path_and_revision_type_boundaries(self):
        self.error("UNSAFE_PATH", lambda: self.flow.start("../escape", self.plan))
        self.flow.start("example", self.plan)
        self.error("STALE_REVISION", lambda: self.flow.build_report("example", False))
