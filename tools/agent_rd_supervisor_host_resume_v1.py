"""Resume a controller-host interruption with exact persisted call identities.

No automatic network retry, model retry, new phase or new scientific settings.
The bounded parent admin process may run hidden, independently of a tool poll.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write


def main():
    authority()
    assert read(TASK / "owner-resume-runtime-v1.json")["status"] == "PASS_ORIGINAL_REMOTE_PHASE_NO_INFERENCE"
    cached = read(TASK / "owner-call-metadata-v1.json")
    assert cached["status"] == "PASS_PROVIDER_RESPONSE", "Do not replace an unresolved interrupted generation"
    interruption = read(PUBLIC / "owner-resume-controller-audit-v1.json")
    assert interruption["completed_units_preserved"] == 197
    work = TASK / "supervisor-host-resume-v1"
    work.mkdir(exist_ok=False)
    frozen_path = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
    freeze = read(frozen_path)
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    assert not (PUBLIC / "locked-progress-v1.json").exists()
    before = {p.name: sha(p) for p in (PUBLIC / "locked-results-v1").glob("*.json")}
    write(work / "preserved-results-before-resume.json", before, True)
    out, err = (work / "evaluation.stdout.txt").open("xb"), (work / "evaluation.stderr.txt").open("xb")
    evaluator = subprocess.Popen([sys.executable, "tools/agent_rd_evaluate_v1.py"], cwd=ROOT, stdout=out, stderr=err)
    heartbeat = 0
    while evaluator.poll() is None:
        if time.monotonic() >= heartbeat:
            try:
                progress = read(TASK / "locked-evaluation-v1/progress.json")
            except (OSError, ValueError):
                progress = {}
            value = {"status": "RUNNING_UNCHANGED_EVALUATOR_AFTER_OWNER_RESUME", "pid": os.getpid(),
                     "evaluator_pid": evaluator.pid, "completed": progress.get("completed"), "planned": 408,
                     "utc": datetime.now(timezone.utc).isoformat(), "automatic_network_retry": False}
            write(work / "heartbeat.json", value)
            print(json.dumps(value), flush=True)
            heartbeat = time.monotonic() + 30
        time.sleep(1)
    out.close()
    err.close()
    assert all(sha(PUBLIC / "locked-results-v1" / name) == digest for name, digest in before.items())
    write(work / "evaluation-exit.json", {"exit_code": evaluator.returncode,
          "preserved_previous_result_files": len(before), "new_generation_of_completed_units": False,
          "source_freeze_sha256": sha(frozen_path), "stderr_sha256": sha(work / "evaluation.stderr.txt")}, True)
    if evaluator.returncode:
        write(work / "completion.json", {"evaluation_exit_code": evaluator.returncode,
              "documents": "NOT_RUN_WITHOUT_FINAL_DISPOSITION", "ledger_closed": False}, True)
        raise SystemExit(evaluator.returncode)
    disposition = read(PUBLIC / "locked-progress-v1.json")
    assert disposition["status"] in ("COMPLETE", "INCOMPLETE") and disposition["stop_reason"] != "OPERATIONAL_BATCH_BOUNDARY"
    write(TASK / "evaluation-completion-v1.json", {"evaluation_exit_code": 0, "supervisor": "supervisor-host-resume-v1",
          "disposition_sha256": sha(PUBLIC / "locked-progress-v1.json"), "freeze_sha256": sha(frozen_path),
          "frozen_evaluator_changed": False, "model_phase_reset": False,
          "owner_resumed_controller_host_exit": True, "original_network_retry_allowance_not_reset": True}, True)
    documents = subprocess.run([sys.executable, "tools/agent_rd_postrun_documents_v1.py", "host-resume-v1"], cwd=ROOT)
    write(work / "completion.json", {"evaluation_exit_code": 0, "documents_exit_code": documents.returncode,
          "visual_review": "PENDING", "remote_return": "PENDING", "ledger_closed": False}, True)
    raise SystemExit(documents.returncode)


if __name__ == "__main__":
    main()
