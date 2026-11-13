"""Run trusted LR-SC1 local intake/analysis inside existing Windows Job limits."""
from __future__ import annotations
import argparse
import json
import os
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.sc1_control_v1 import ACCOUNT, RELEASE, ROOT, digest
from tools.dc2_local_guard_v1 import LocalGuard


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--cpu", required=True, type=int)
    parser.add_argument("--wall", required=True, type=int)
    parser.add_argument("script", type=Path)
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Safe unique attempt id required")
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    path = ACCOUNT / "ledger.json"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    if not ledger["status"].startswith("ACTIVE") or ledger["active_jobs"]:
        raise RuntimeError("Only one fresh active local attempt at a time")
    if ledger["status"] == "ACTIVE_CLOSEOUT_FAILED_GATE1":
        allowed = {"sc1_return_v1.py", "sc1_report_v1.py", "sc1_delivery_audit_v1.py", "sc1_git_delivery_v1.py"}
        if args.script.name not in allowed or args.stage != "analysis_delivery":
            raise RuntimeError("Failed gate permits return/report/audit/delivery only, no further research")
    if datetime.now(timezone.utc) >= datetime.fromisoformat(release["deadline_utc"]):
        raise RuntimeError("Deadline passed")
    if args.stage != "gate0":
        gate = json.loads((ROOT / "docs/evidence/lr-sc1-20261113-v1/gate0-v1.json").read_text())
        if gate["status"] != "PASS_BOUNDED_EMPIRICAL_DISTINCTION":
            raise RuntimeError("Gate 0 not passed")
    if any(item["id"] == args.id for item in ledger["reservations"]):
        raise RuntimeError("Attempt id already retained")
    reserved = sum(item["cpu_seconds"] for item in ledger["reservations"] if item["stage"] == args.stage)
    cap = release["stage_caps_seconds"][args.stage]["cpu"]
    if args.cpu <= 0 or args.wall <= 0 or reserved + args.cpu > cap:
        raise RuntimeError("Stage CPU allowance unavailable")
    script = args.script.resolve()
    if not script.is_relative_to(ROOT / "tools") or not script.name.startswith("sc1_"):
        raise ValueError("Only reviewed task-owned trusted workers allowed")
    receipt = ACCOUNT / "jobs" / args.id / "resources.json"
    receipt.parent.mkdir(parents=True, exist_ok=False)
    booking = {"id": args.id, "stage": args.stage, "cpu_seconds": args.cpu,
               "gpu_allocated_seconds": 0, "status": "RESERVED", "pid": os.getpid(),
               "script": str(script.relative_to(ROOT)), "script_sha256": digest(script),
               "args": args.args, "started_utc": datetime.now(timezone.utc).isoformat(),
               "resource_receipt": str(receipt.relative_to(ROOT))}
    ledger["reservations"].append(booking)
    ledger["active_jobs"].append(args.id)
    save(path, ledger)
    guard = None
    code = 1
    try:
        guard = LocalGuard(receipt, args.cpu, release["deadline_utc"], args.wall)
        sys.argv = [str(script)] + args.args
        runpy.run_path(str(script), run_name="__main__")
        code = 0
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    finally:
        status = "PASS" if code == 0 else "FAIL"
        if guard:
            guard.finish(status)
        ledger = json.loads(path.read_text(encoding="utf-8"))
        for item in ledger["reservations"]:
            if item["id"] == args.id:
                item["status"] = status
                item["exit_code"] = code
                item["finished_utc"] = datetime.now(timezone.utc).isoformat()
                if receipt.exists():
                    item["receipt_sha256"] = digest(receipt)
                    item["measured_aggregate_cpu_seconds"] = json.loads(receipt.read_text())["aggregate_cpu_seconds"]
        ledger["active_jobs"].remove(args.id)
        save(path, ledger)
    return code


if __name__ == "__main__":
    sys.exit(main())
