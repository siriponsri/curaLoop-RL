"""Supervise the unchanged evaluator without a waiting-document deadlock.

Only pre-unit SSH-status transport exits may resume operationally. Completed
units are skipped by the frozen evaluator, never regenerated. Three transport
invocations maximum; original model phase, source pins and deadline unchanged.
"""

import json
import subprocess
import sys
import time

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write


def main():
    authority()
    assert read(TASK / "read-only-reconnect-v1.json")["status"] == "PASS_SAME_RUNTIME_RECONNECTED_NO_INFERENCE"
    work = TASK / "supervisor-recovery-v1"
    work.mkdir(exist_ok=False)
    assert not (PUBLIC / "locked-progress-v1.json").exists()
    frozen_path = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
    freeze = read(frozen_path)
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    for attempt in range(1, 4):
        folder = work / ("transport-invocation-" + str(attempt))
        folder.mkdir()
        out, err = (folder / "stdout.txt").open("xb"), (folder / "stderr.txt").open("xb")
        evaluator = subprocess.Popen([sys.executable, "tools/agent_rd_evaluate_v1.py"], cwd=ROOT, stdout=out, stderr=err)
        heartbeat = 0
        progress = {}
        while evaluator.poll() is None:
            if time.monotonic() >= heartbeat:
                try:
                    progress = read(TASK / "locked-evaluation-v1/progress.json")
                except (OSError, ValueError):
                    pass
                print(json.dumps({"status": "RUNNING_UNCHANGED_FROZEN_EVALUATOR", "transport_invocation": attempt,
                                  "completed": progress.get("completed"), "planned": 408}), flush=True)
                heartbeat = time.monotonic() + 60
            time.sleep(1)
        out.close()
        err.close()
        write(folder / "exit.json", {"exit_code": evaluator.returncode, "stderr_sha256": sha(folder / "stderr.txt"),
                                     "freeze_sha256": sha(frozen_path)}, True)
        if evaluator.returncode == 0:
            disposition = read(PUBLIC / "locked-progress-v1.json")
            assert disposition["status"] in ("COMPLETE", "INCOMPLETE") and disposition["stop_reason"] != "OPERATIONAL_BATCH_BOUNDARY"
            write(TASK / "evaluation-completion-v1.json", {"evaluation_exit_code": 0, "supervisor": "supervisor-recovery-v1",
                  "transport_invocation": attempt, "disposition_sha256": sha(PUBLIC / "locked-progress-v1.json"),
                  "freeze_sha256": sha(frozen_path), "frozen_evaluator_changed": False, "model_phase_reset": False}, True)
            print("Frozen evaluator exited; only now starting actual-data reports", flush=True)
            documents = subprocess.run([sys.executable, "tools/agent_rd_postrun_documents_v1.py", "recovery-v1"], cwd=ROOT)
            write(work / "completion.json", {"evaluation_exit_code": 0, "documents_exit_code": documents.returncode,
                  "visual_review": "PENDING", "remote_return": "PENDING", "ledger_closed": False}, True)
            raise SystemExit(documents.returncode)
        error = (folder / "stderr.txt").read_text(encoding="utf-8", errors="replace")
        status_location = 'status = call("status")' in error or 'phase = call("status")' in error
        network_error = any(message in error for message in ("Connection timed out during banner exchange", "port 22 timed out", "Connection reset by peer"))
        write(folder / "interruption.json", {"status": "PRE_UNIT_TRANSPORT_INTERRUPTION" if status_location and network_error else "STOP_UNCLASSIFIED_EXECUTION_ERROR",
              "no_trial_replacement": True, "scientific_protocol_changed": False, "phase_or_deadline_reset": False}, True)
        if not (status_location and network_error) or attempt == 3:
            write(work / "completion.json", {"evaluation_exit_code": evaluator.returncode,
                  "documents": "NOT_RUN_NO_FINAL_DISPOSITION", "ledger_closed": False}, True)
            raise SystemExit(evaluator.returncode)
        print("Recorded pre-unit network interruption; one bounded operational resume after60s, no model retry", flush=True)
        time.sleep(60)


if __name__ == "__main__":
    main()
