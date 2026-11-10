"""Reconcile an exited local controller without altering results or allowances.

The owner explicitly requested goal resume. The exact cause of the local
controller exit is unknown; a stale tool-host generation is an observation,
not proof that a resource ceiling or a model failure caused it.
"""

import base64
import json
import subprocess
import sys
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, reserve, save, sha, write
from agent_rd_remote_v1 import call


def settle():
    release, ledger = authority()
    command = ["powershell", "-NoProfile", "-Command",
               '$items = @(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like "*python.exe" -and $_.CommandLine -match "agent_rd_(admin|evaluate|supervisor_recovery|postrun_documents)_v1[.]py" }); $items | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress']
    observed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
    assert not observed.stdout.strip(), "A local scientific/controller process is still present; do not orphan-settle or double-launch"
    name = "locked-supervisor-recovery-v1"
    assert ledger["bookings"][name]["status"] == "RESERVED"
    assert not (TASK / "supervisor-recovery-v1/completion.json").exists()
    resource_path = TASK / "jobs" / name / "resource.json"
    resource = read(resource_path)
    assert resource["status"] == "RUNNING" and resource["aggregate_cpu_seconds"] < resource["cpu_limit_seconds"]
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    assert all(sha(ROOT / p) == h for p, h in release["frozen_scientific_pins"].items())
    plan = read(ROOT / "research/agent_rd_eval_v1/frozen/schedule.json")
    receipts = [p for p in (PUBLIC / "locked-results-v1").glob("*.json") if not p.name.endswith("-trace.json")]
    completed = set()
    for path in receipts:
        value = read(path)
        assert sha(TASK / "locked-evaluation-v1/missions" / (value["mission_id"] + ".json")) == value["mission_file_sha256"]
        completed.add(value["unit"]["unit_id"])
    next_unit = next(u for u in plan if u["unit_id"] not in completed)
    identity_file = TASK / "locked-evaluation-v1" / (next_unit["unit_id"] + "-identity.json")
    pending = None
    if identity_file.exists():
        identity = read(identity_file)["mission_id"]
        row = read(TASK / "locked-evaluation-v1/missions" / (identity + ".json"))["payload"]
        pending = {"mission_id": identity, "state": row["state"],
                   "calls": [{"call_id": c["call_id"], "status": c["status"]} for c in row["calls"]]}
    retained = dict(ledger["retained_seconds"])
    ledger["bookings"][name].update(status="FAIL_ABRUPT_CONTROLLER_EXIT_RESOURCE_RECORD_STALE",
        resource_sha256=sha(resource_path), measured_cpu_lower_bound_seconds=resource["aggregate_cpu_seconds"],
        final_actual_cpu_unknown=True, full_cpu_reservation_retained=True)
    save(ledger)
    assert read(TASK / "ledger.json")["retained_seconds"] == retained
    write(PUBLIC / "owner-resume-controller-audit-v1.json", {"status": "PASS_ORPHAN_ACCOUNTING_AND_RESULT_PRESERVATION",
          "utc": datetime.now(timezone.utc).isoformat(), "completed_units_preserved": len(receipts), "planned": len(plan),
          "next_unit": next_unit, "pending_exact_call_reconciliation": pending,
          "last_resource_heartbeat": resource["heartbeat_utc"], "resource_file_preserved_sha256": sha(resource_path),
          "observed_cpu_lower_bound_seconds": resource["aggregate_cpu_seconds"],
          "retained_cpu_cap_seconds": ledger["bookings"][name]["cpu_cap"], "refund_or_budget_reset": False,
          "exit_cause": "UNKNOWN; stale resource record and absence of local controller processes observed",
          "owner_resume": True, "frozen_pins_preserved": len(freeze["pins"]), "new_model_calls": 0,
          "old_completion_or_resource_record_rewritten": False}, True)
    print(json.dumps({"status": "SETTLED_ORPHAN_WITH_FULL_RESERVATION", "completed": len(receipts), "next_unit": next_unit, "pending": pending}))


def probe():
    authority()
    original = read(sorted((TASK / "locked-evaluation-v1").glob("invocation-*.json"))[0])["phase"]
    status = call("status", timeout=45)
    assert status["phase"] == original["phase"] and status["admission"]["container_id"] == original["admission"]["container_id"]
    remaining = status["phase"]["cpu_base"] + status["phase"]["cpu_cap"] - status["container_cpu_seconds"]
    write(TASK / "owner-resume-runtime-v1.json", {"status": "PASS_ORIGINAL_REMOTE_PHASE_NO_INFERENCE", "runtime": status,
          "remaining_evaluation_cpu_seconds": remaining, "phase_or_deadline_reset": False}, True)
    print(json.dumps({"status": "PASS_ORIGINAL_REMOTE_PHASE_NO_INFERENCE", "remaining_evaluation_cpu_seconds": remaining}))


def inspect_call():
    authority()
    pending = read(PUBLIC / "owner-resume-controller-audit-v1.json")["pending_exact_call_reconciliation"]
    assert pending and len(pending["calls"]) == 1 and pending["calls"][0]["status"] == "RUNNING"
    call_id = pending["calls"][0]["call_id"]
    assert all(c.isalnum() or c == "-" for c in call_id)
    program = '''import hashlib,json,os,resource,sys
from pathlib import Path
os.sched_setaffinity(0,{71})
resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
resource.setrlimit(resource.RLIMIT_CPU,(2,3))
payload=json.load(sys.stdin)
root=Path('/home/chaw/curaloop-tasks/agent-rd-20261110-v1')
assert root.is_dir() and not root.is_symlink() and root.resolve()==root
identity=payload['call_id']
assert identity and all(c.isalnum() or c=='-' for c in identity)
path=root/'calls'/(identity+'.json')
value={'call_id':identity,'exists':path.exists()}
if path.exists():
 assert path.is_file() and not path.is_symlink()
 record=json.loads(path.read_text())
 value.update(status=record['status'],file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
  request_sha256=record['request_sha256'],finished_utc=record.get('finished_utc'),
  container_cpu_seconds=record.get('container_cpu_seconds'))
value['measured_host_cpu_seconds']=sum(resource.getrusage(resource.RUSAGE_SELF)[:2])
print(json.dumps(value))
'''
    write(TASK / "owner-call-metadata-source-v1.json", {"program": program}, True)
    encoded = base64.b64encode(program.encode()).decode()
    remote_command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
    name = "owner-resume-call-metadata-v1"
    reserve(name, "technical_retry", 3, "remote-metadata", ["read_one_owned_call_metadata", call_id])
    try:
        result = subprocess.run(["rtk", "proxy", "ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                                 "-o", "ConnectTimeout=15", "100.77.149.83", remote_command],
                                input=json.dumps({"call_id": call_id}), capture_output=True, text=True, encoding="utf-8", timeout=45)
        assert result.returncode == 0, result.stderr[-1200:]
        value = json.loads(result.stdout)
        write(TASK / "owner-call-metadata-v1.json", value, True)
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][name].update(status="PASS", measured_cpu_seconds=value["measured_host_cpu_seconds"])
        save(ledger)
        print(json.dumps(value))
    except BaseException:
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][name].update(status="FAIL", measured_cpu_seconds=None)
        save(ledger)
        raise


if __name__ == "__main__":
    assert sys.argv[1] in ("settle", "probe", "inspect-call")
    {"settle": settle, "probe": probe, "inspect-call": inspect_call}[sys.argv[1]]()
