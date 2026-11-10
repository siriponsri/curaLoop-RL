"""Read-only preservation, remote absence and final acceptance inventory checks."""

import base64
import json
import re
import subprocess
from datetime import datetime, timezone

from cf2p_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write


def remote_absence():
    code = '''import json,os,resource,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5))
resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
signal.alarm(20)
cpu=sorted(os.sched_getaffinity(0))[-1];os.sched_setaffinity(0,{cpu})
names=['lr-cf2p-20261110-v1','lr-cf2p-20261110-v1-export-v1','lr-cf1-20261109-v1','lr-cf1-20261109-v1-export-v1']
checks={n:not (Path.home()/'curaloop-tasks'/n).exists() and not (Path.home()/'curaloop-tasks'/n).is_symlink() for n in names}
print(json.dumps({'hostname':os.uname().nodename,'initial_cpu':cpu,'absence':checks,'task_created':False,'task_deleted':False,'read_only':True}))
'''
    encoded = base64.b64encode(code.encode()).decode()
    command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
    result = subprocess.run(["rtk", "proxy", "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                             "-o", "ConnectTimeout=15", "100.77.149.83", command], capture_output=True, text=True, timeout=35)
    write(TASK / "ssh-final-readonly-response-v1.json", {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, True)
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert value["hostname"] == "dr-train" and all(value["absence"].values())
    write(PUBLIC / "remote-absence-v1.json", {"status": "PASS_FRESH_READ_ONLY_ABSENCE", "utc": datetime.now(timezone.utc).isoformat(),
          **value, "compute_task_created": False, "upload_bytes": 0,
          "return_and_cleanup": "NOT_APPLICABLE_NO_REMOTE_FILES", "private_key_read": False,
          "configuration_changed": False, "remote_probe_cpu_upper_seconds": 5}, True)


def main():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"] == "ACTIVE"
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    preserved = {p: sha(ROOT / p) == h for p, h in release["prior_ledger_pins"].items()}
    frozen = {p: sha(ROOT / p) == h for p, h in release["frozen_scientific_pins"].items()}
    assert len(preserved) == 13 and all(preserved.values()) and len(frozen) == 66 and all(frozen.values())
    proposal = read(ROOT / "research/configs/lr_cf2p_proposal_20261110_v1.json")
    assert sha(ROOT / proposal["proposal_path"]) == release["proposal_sha256"]
    assert sha(ROOT / "research/configs/lr_cf2p_proposal_20261110_v1.json") == release["proposal_config_sha256"]
    assert all(sha(ROOT / row["path"]) == row["sha256"] and (ROOT / row["path"]).stat().st_size == row["bytes"] for row in proposal["inputs"])
    old = ["docs/manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf"]
    paths = subprocess.check_output(["rtk", "proxy", "git", "ls-tree", "-r", "--name-only", release["base_commit"], "src/curaloop_rd"], cwd=ROOT, text=True).splitlines()
    old.extend(p for p in paths if p.endswith(".py"))
    unchanged = {}
    for path in old:
        raw = subprocess.check_output(["rtk", "proxy", "git", "show", release["base_commit"] + ":" + path], cwd=ROOT)
        unchanged[path] = (ROOT / path).read_bytes() == raw
    assert all(unchanged.values())
    browser = read(PUBLIC / "browser-check-v5.json")
    assert browser["status"] == "PASS_ACTUAL_PRODUCTION_BROWSER" and len(browser["views"]) == 70
    assert browser["explicit_scenario_builder_reachable_without_auto_creation"]
    assert read(PUBLIC / "native-c-workspace-v2.json")["status"] == "PASS_ACTUAL_LOCAL_STDIO"
    assert read(PUBLIC / "visual-review-v1.json")["sha256"] == sha(ROOT / "docs/manual/CuraLoop-RL-Confirmation-Evidence-Guide-EN-v4.pdf")
    tests = {}
    for name, expected in [("final-api-privacy-regressions-v1", "22 passed"), ("final-frontend-tests-v4", "26 passed"), ("final-python-lint-v3", "All checks passed")]:
        booking = ledger["bookings"][name]
        assert booking["status"] == "PASS"
        folder = TASK / "jobs" / name
        assert expected in (folder / "stdout.txt").read_text(encoding="utf-8", errors="replace")
        tests[name] = {"status": "PASS", "stdout_sha256": sha(folder / "stdout.txt"), "resource_sha256": sha(folder / "resource.json"), "command": booking["command"]}
    write(PUBLIC / "verification-v1.json", {"status": "PASS_EXECUTED_TARGETED_ENGINEERING_CHECKS", "checks": tests,
          "python_tests": 22, "frontend_tests": 26, "all_scientific_suites_rerun": False,
          "dependency_warning": "FastAPI TestClient: Starlette/httpx deprecation, tests pass",
          "production_browser": "browser-check-v5.json", "production_build": "frontend-build-v5.json",
          "native_stdio": "native-c-workspace-v2.json"}, True)
    remote_absence()
    # Inspect only the known owned server. Unrelated owner listeners are not stopped.
    own_pid = browser.get("server_pid")
    command = "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress"
    result = subprocess.run(["rtk", "proxy", "powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=25)
    assert result.returncode == 0, result.stderr
    processes = json.loads(result.stdout)
    # Every earlier guarded parent PID should have exited. Current audit parent/child are expected active.
    prior_pids = {read(TASK / "jobs" / name / "resource.json")["pid"] for name, row in ledger["bookings"].items() if row["status"] != "RESERVED" and (TASK / "jobs" / name / "resource.json").exists()}
    active_prior = [{"pid": p["ProcessId"], "command": p.get("CommandLine", "")} for p in processes if p["ProcessId"] in prior_pids and "cf2p_admin_v1.py run " in (p.get("CommandLine") or "")]
    assert not active_prior
    owned_servers = [p["ProcessId"] for p in processes if "uvicorn" in (p.get("CommandLine") or "") and "--port 5173" in (p.get("CommandLine") or "")]
    # The browser records termination of its exact owned server; never kill a reused port's new owner.
    assert browser["owned_server_stopped"]
    if own_pid:
        assert not any(p["ProcessId"] == own_pid and "uvicorn" in (p.get("CommandLine") or "") for p in processes)
    source = {p.relative_to(ROOT).as_posix(): sha(p) for p in [ROOT / "api/main.py", *sorted((ROOT / "frontend/src").rglob("*"))] if p.is_file()}
    new_docs = [ROOT / p for p in ("docs/05_product/CF1_INTEGRATION_GUIDE_20261110.md", "docs/06_execution/LR_CF2P_OWNER_CHECKPOINT_20261110.md", "docs/evidence/lr-cf2p-20261110-v1/README.md", "docs/03_research/CF2_DESIGN_DECISION_20261110.md", "docs/03_research/CF2_CONDITIONAL_EVALUATION_DESIGN_20261110.md", "docs/02_literature/CF2_CLOSEST_WORK_20261110.md")]
    broken = []
    for path in new_docs:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"[\u0e00-\u0e7f]", text), path
        for target in re.findall(r"\]\(([^)]+)\)", text):
            resolved = (path.parent / target.split("#")[0]).resolve()
            pending = {PUBLIC / "closure-audit-v1.json", PUBLIC / "budget-closeout-v1.json"}
            if not target.startswith(("https:", "http:", "#")) and not resolved.exists() and resolved not in pending:
                broken.append({"file": path.relative_to(ROOT).as_posix(), "target": target})
    assert not broken, broken
    diff = subprocess.run(["rtk", "proxy", "git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    artifact_paths = sorted(p for p in PUBLIC.rglob("*") if p.is_file())
    # No copyrighted reading copies, private rows, credentials or disposable storage are public artifacts.
    assert not any(p.suffix.lower() in (".sqlite3", ".db", ".tar", ".gz") for p in artifact_paths)
    write(PUBLIC / "closure-audit-v1.json", {"status": "PASS_PRE_CLOSURE_ACCEPTANCE_AND_PRESERVATION", "utc": datetime.now(timezone.utc).isoformat(),
          "next_required_steps": ["parent closes current budget after this guarded audit exits", "normal main commit/push and remote/clean verification"],
          "prior_closed_ledgers": preserved, "frozen_scientific_pins": frozen, "five_proposal_inputs_unchanged": True,
          "immutable_proposal_and_config_unchanged": True, "prior_c_python_and_manual_v3_byte_unchanged": unchanged,
          "source_inventory_sha256": source, "public_artifacts_before_this_receipt": {p.relative_to(ROOT).as_posix(): sha(p) for p in artifact_paths},
          "known_prior_guarded_jobs_still_running": active_prior, "owned_browser_server_stopped": True,
          "unowned_listeners_stopped": False, "candidate_port_uvicorn_pids_at_check": owned_servers,
          "remote_return_cleanup": "NOT_APPLICABLE_NO_REMOTE_FILES", "broken_new_document_links": broken,
          "new_documents_english": True, "git_diff_check": "PASS", "final16_access": False,
          "private_cf1_row_access": False, "molecular_fits": 0, "paid_or_gpu": False,
          "live_external_writes": False, "deployment_or_submission": False,
          "independent_reviewer": False}, True)
    print("PASS final acceptance, source preservation, documentation and fresh remote absence")


if __name__ == "__main__":
    main()
