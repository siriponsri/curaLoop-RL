"""Fresh absence/preservation/report audit; close only after all booked jobs end."""
import argparse
import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.sc1_control_v1 import ACCOUNT, PUBLIC, RELEASE, ROOT, digest, write_new
from tools.sc1_job_v1 import save
from tools.sc1_report_v1 import verify as report_verify, PDF, MD


def verify():
    program = '''import http.client,json,socket,urllib.parse
from pathlib import Path
class Unix(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(15);self.sock.connect('/var/run/docker.sock')
c=Unix('localhost');q=urllib.parse.quote(json.dumps({'label':['curaloop.task=lr-sc1-20261113-v1']}))
c.request('GET','/containers/json?all=1&filters='+q);r=c.getresponse();b=r.read(1048577);c.close()
if r.status!=200 or len(b)>1048576:raise RuntimeError('Owned absence query failed')
paths=['/home/chaw/curaloop-tasks/lr-sc1-20261113-v1','/home/chaw/curaloop-tasks/lr-sc1-20261113-v1-return.tar.gz','/home/chaw/curaloop-tasks/lr-sc1-20261113-v1-return-manifest.json']
out={'paths_absent':{p:not Path(p).exists() for p in paths},'owned_container_count':len(json.loads(b))}
print(json.dumps(out))
'''
    encoded = base64.b64encode(program.encode()).decode()
    p = subprocess.run(["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "100.77.149.83",
                        "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""], capture_output=True, text=True, timeout=35)
    if p.returncode:
        raise RuntimeError("Independent fresh remote absence observation failed")
    absence = json.loads(p.stdout)
    if absence["owned_container_count"] or not all(absence["paths_absent"].values()):
        raise RuntimeError("Remote owned resources remain")
    release = json.loads(RELEASE.read_text())
    checks = {path: (ROOT / path).is_file() and digest(ROOT / path) == expected for path, expected in release["preservation_pins"].items()}
    if not all(checks.values()):
        raise RuntimeError("Historical preservation pin changed")
    reconstruction = report_verify()
    structural = json.loads((ACCOUNT / "pdf-qa-v1/structural-qa.json").read_text())
    if len(structural["pages"]) != 5 or structural["outside_page_spans"] or structural["pdf_sha256"] != digest(PDF) or structural["source_sha256"] != digest(MD):
        raise RuntimeError("Manuscript changed after rendered review")
    # Author self-review observed all five final page renders, the enlarged
    # result table/diagram, and grayscale figure in the task conversation.
    visual = {"status": "PASS_AUTHOR_VISUAL_SELF_REVIEW", "page_count": 5,
              "reviewed": ["All five final page PNGs", "Result table and execution diagram at enlarged size", "Grayscale figure"],
              "clipping_overlap_orphans": "NONE_OBSERVED", "independent_expert_review": False,
              "pdf_sha256": digest(PDF), "source_sha256": digest(MD), "reviewed_utc": datetime.now(timezone.utc).isoformat(),
              "author_design_self_score": 94, "self_score_is_research_validation": False}
    write_new(PUBLIC / "manuscript-visual-review-v1.json", visual)
    result = {"status": "PASS_READY_FOR_ACCOUNT_CLOSEOUT", "fresh_remote_absence": absence,
              "preservation_pin_count": len(checks), "all_preservation_pins_match": True,
              "offline_audit_reconstruction": reconstruction, "manuscript_visual_review": visual,
              "remote_return": json.loads((PUBLIC / "remote-return-v1.json").read_text()),
              "remote_cleanup": json.loads((PUBLIC / "remote-cleanup-v1.json").read_text()),
              "verification_utc": datetime.now(timezone.utc).isoformat()}
    write_new(ACCOUNT / "delivery-verification-v1.json", result)
    print(json.dumps({"status": result["status"], "preservation_pins": len(checks), "pages": 5, "remote_owned_containers": 0}))


def close():
    path = ACCOUNT / "ledger.json"
    ledger = json.loads(path.read_text())
    if ledger["status"] != "ACTIVE_CLOSEOUT_FAILED_GATE1" or ledger["active_jobs"] or ledger.get("active_remote_jobs"):
        raise RuntimeError("All original local/remote jobs must be terminal before closeout")
    verified = json.loads((ACCOUNT / "delivery-verification-v1.json").read_text())
    if verified["status"] != "PASS_READY_FOR_ACCOUNT_CLOSEOUT":
        raise RuntimeError("Verification missing")
    release = json.loads(RELEASE.read_text())
    if any(digest(ROOT / name) != expected for name, expected in release["preservation_pins"].items()):
        raise RuntimeError("Preservation changed before closure")
    returned = json.loads((ACCOUNT / "remote-return-v1/manifest.json").read_text())["files"]
    source_map = {"remote.py": "tools/sc1_remote_native_v1.py", "inside.py": "tools/sc1_native_inside_v1.py",
                  "remote-v2.py": "tools/sc1_remote_native_v2.py", "inside-v2.py": "tools/sc1_native_inside_v2.py",
                  "return-v1.py": "tools/sc1_return_remote_v1.py"}
    if any(digest(ROOT / local) != returned[remote]["sha256"] for remote, local in source_map.items()):
        raise RuntimeError("Returned executed remote source differs from committed candidate")
    if any(row["id"] == "final-git-administration-v1" for row in ledger["reservations"]):
        raise RuntimeError("Final administration booking already retained")
    ledger["reservations"].append({"id": "final-git-administration-v1", "stage": "analysis_delivery", "cpu_seconds": 600,
                                   "gpu_allocated_seconds": 0, "status": "RETAINED_UNMETERED_FINAL_ADMIN_ALLOWANCE",
                                   "scope": "Account closure, authorized final Git commit/push and read-only delivery verification; not a model job"})
    totals = {name: {"cpu": sum(item["cpu_seconds"] for item in ledger["reservations"] if item["stage"] == name),
                     "gpu": sum(item["gpu_allocated_seconds"] for item in ledger["reservations"] if item["stage"] == name)} for name in release["stage_caps_seconds"]}
    for stage, usage in totals.items():
        if usage["cpu"] > release["stage_caps_seconds"][stage]["cpu"] or usage["gpu"] > release["stage_caps_seconds"][stage]["gpu_allocated"]:
            raise RuntimeError("Stage resource ceiling exceeded")
    cpu = sum(row["cpu"] for row in totals.values())
    gpu = sum(row["gpu"] for row in totals.values())
    if cpu > release["cpu_cap_seconds"] or gpu > release["gpu_allocated_cap_seconds"]:
        raise RuntimeError("Global resource ceiling exceeded")
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    now = datetime.now(timezone.utc).isoformat()
    ledger.update(status="CLOSED_NO_GO_NATIVE_EVALUATOR_READINESS", closed_utc=now,
                  conservative_retained_cpu_seconds=cpu, conservative_retained_gpu_seconds=gpu,
                  budget_reuse_authorized=False)
    save(path, ledger)
    result = {"status": "PASS_FAILED_GATE_CLOSEOUT_COMPLETE", "research_outcome": "NO_GO_NATIVE_EVALUATOR_READINESS",
              "closed_utc": now, "source_commit": source_commit, "base_commit": release["base_commit"],
              "final_main_commit": "Subsequent account/documentation closeout commit; exact SHA in private delivery-git-receipt-v1.json and owner reply",
              "active_research_jobs": 0, "active_booked_local_jobs": 0, "active_booked_remote_jobs": 0,
              "agent_comparison": "NOT_RUN", "agent_calls": 0, "primary_effect": None, "primary_effect_status": "NOT_ESTIMABLE",
              "validation_native_final": "28/29 subproblems; 5/6 main problems", "further_research_in_this_account": False,
              "cpu_cap_hours": 128, "gpu_cap_hours": 96, "conservative_retained_cpu_seconds": cpu,
              "conservative_retained_cpu_hours": cpu / 3600, "allocated_gpu_seconds": gpu,
              "measured_local_job_cpu_seconds": sum(item.get("measured_aggregate_cpu_seconds", 0) for item in ledger["reservations"]),
              "measured_remote_return_process_cpu_seconds": sum(item.get("measured_process_cpu_seconds", 0) or 0 for item in ledger["reservations"]),
              "complete_measured_aggregate_cpu": "NOT_ESTABLISHED; retained reservations include unmetered administration and failed attempts",
              "stage_retained_seconds": totals, "ledger_sha256": digest(path),
              "remote_return_files": verified["remote_return"]["file_count"], "remote_return_file_bytes": verified["remote_return"]["file_bytes"],
              "full_local_return_reread": "PASS", "exact_remote_cleanup_and_fresh_absence": "PASS",
              "preservation_pins": verified["preservation_pin_count"], "preservation_status": "PASS",
              "returned_executed_remote_source_concordance": "PASS_FIVE_EXACT_SOURCE_FILES",
              "manuscript_pages": 5, "manuscript_sha256": digest(PDF), "manuscript_visual_review": "PASS_AUTHOR_SELF_REVIEW",
              "empirical_software_engineering_submission_readiness": "NO_GO_NO_AGENT_COMPARATIVE_EVIDENCE",
              "old_final16_private_cf1_hidden_outcomes": "CLOSED", "paid_api_deployment_submission": "NONE"}
    write_new(PUBLIC / "delivery-audit-v1.json", result)
    write_new(ACCOUNT / "closeout-audit-pin-v1.json", {"delivery_audit_sha256": digest(PUBLIC / "delivery-audit-v1.json"), "ledger_sha256": digest(path)})
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--close", action="store_true")
    args = parser.parse_args()
    close() if args.close else verify()
