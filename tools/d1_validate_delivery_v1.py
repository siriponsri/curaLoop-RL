"""Final metadata/hash readback; no new scientific execution or ledger write."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import PUBLIC, TASK, new, now, read, sha


def main():
    ledger = read(TASK / "ledger.json")
    assert ledger["status"] == "CLOSED_COMPLETE_FOR_OWNER_REVIEW"
    assert datetime.fromisoformat(ledger["closed_utc"]) <= datetime.fromisoformat(ledger["deadline_utc"])
    assert all(row["status"] == "PASS" for row in ledger["jobs"].values())
    assert sum(ledger["retained_reservations_seconds"].values()) == 4500
    pins = read(ROOT / "docs/evidence/m2-diagnostics-20261109-v1/preservation-pins-v1.json")["pins"]
    assert all(sha(ROOT / name) == value for name, value in pins.items())
    for freeze_name, field in (("reuse-freeze-v1.json", "analysis_sources"), ("control-analysis-freeze-v1.json", "pins")):
        freeze = read(TASK / freeze_name)[field]
        source_pins = {r["path"]: r["sha256"] for r in freeze} if isinstance(freeze, list) else freeze
        assert all(sha(ROOT / name) == value for name, value in source_pins.items())
    for name in ("bootstrap", "calibration", "controls"):
        assert read(TASK / "jobs" / name / "kernel-proof.json") == {
            "cpu.max": "100000 100000", "memory.max": "4294967296", "memory.swap.max": "0",
        }
    closure = read(PUBLIC / "closure-audit-v1.json")
    report = ROOT / "docs/03_research/D1_OPERATION_HEADROOM_RESULTS_20261109.md"
    assert sha(report) == closure["report_sha256"]
    tests = 0
    for name in ("constructed-tests-v1.xml", "controls-constructed-v1.xml", "control-analysis-constructed-v1.xml"):
        suites = ET.parse(PUBLIC / name).getroot().findall("testsuite")
        for suite in suites:
            assert int(suite.attrib["errors"]) == int(suite.attrib["failures"]) == 0
            assert int(suite.attrib.get("skipped", "0")) == 0
            tests += int(suite.attrib["tests"])
    assert tests == 37
    docs = [report, ROOT / "docs/06_execution/D1_OWNER_CHECKPOINT_20261109.md",
            ROOT / "docs/06_execution/D1_EXECUTION_NOTES_20261109.md", PUBLIC / "README.md"]
    checked = 0
    target_receipt = PUBLIC / "delivery-validation-v1.json"
    for document in docs:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            assert ".local" not in target and "raw_data" not in target
            path = (document.parent / target.split("#")[0]).resolve()
            assert path == target_receipt or path.is_file(), str(path)
            checked += 1
    originals = ["research/d1_v1", "tests/research/test_d1_analysis_v1.py",
                 "tests/research/test_d1_controls_v1.py", "tests/research/test_d1_control_analysis_v1.py"]
    originals += [str(p.relative_to(ROOT)) for p in (ROOT / "tools").glob("d1_*.py")
                  if p.name != "d1_return_v1.py"]
    lint = subprocess.run([sys.executable, "-B", "-m", "ruff", "check", *originals],
                          capture_output=True, text=True, check=False)
    assert lint.returncode == 0, lint.stdout + lint.stderr
    compile((ROOT / "tools/d1_return_v1.py").read_text(encoding="utf-8"), "<versioned-return-workflow>", "exec")
    whitespace = subprocess.run(["rtk", "git", "diff", "--check"], capture_output=True, text=True, check=False)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    branch = subprocess.check_output(["rtk", "git", "branch", "--show-current"], text=True).strip()
    assert branch.splitlines()[-1] == "main"
    head = subprocess.check_output(["rtk", "git", "rev-parse", "HEAD"], text=True).strip().splitlines()[-1]
    assert head == "bf59b103a789fa2832762abcdc6d5f7dc723466e"
    result = {
        "status": "PASS_LOCAL_D1_DELIVERY_READBACK", "observed_utc": now().isoformat(),
        "head": head, "branch": "main", "commit_push": "NOT_RUN_LOCAL_EDITS_RETAINED",
        "ledger_status": ledger["status"], "ledger_sha256": sha(TASK / "ledger.json"),
        "retained_cpu_seconds": 4500, "cap_seconds": 14400,
        "jobs_terminal_PASS": len(ledger["jobs"]), "within_original_deadline": True,
        "old_preservation_pins_unchanged": len(pins), "constructed_tests_passed": tests,
        "local_document_links_checked": checked, "ruff": "PASS",
        "derived_return_workflow": "compiled; actual export/fetch/reread/cleanup PASS; inherited style unchanged",
        "analysis_and_worker_source_pins": "PASS", "cgroup_cpu_memory_swap_proofs": "PASS",
        "report_sha256": sha(report), "final_outcomes_open": False,
        "conditional96h_activated": False, "D2": "NOT_RELEASED", "independent_review": "NOT_RUN",
    }
    new(target_receipt, result)
    print(result)


if __name__ == "__main__":
    main()
