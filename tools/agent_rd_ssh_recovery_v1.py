"""Record a pre-unit transport interruption and test the same runtime once.

No model inference, scientific edit, phase transition or allowance reset.
"""

import json
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write
from agent_rd_remote_v1 import call


def main():
    authority()
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    old_work = TASK / "supervisor-v1"
    assert read(old_work / "completion.json")["evaluation_exit_code"] == 1
    error = (old_work / "evaluation.stderr.txt").read_text(encoding="utf-8")
    assert 'status = call("status")' in error and "Connection timed out during banner exchange" in error
    progress = read(TASK / "locked-evaluation-v1/progress.json")
    receipts = [p for p in (PUBLIC / "locked-results-v1").glob("*.json") if not p.name.endswith("-trace.json")]
    assert len(receipts) == progress["completed"] == 52
    for path in receipts:
        receipt = read(path)
        assert sha(TASK / "locked-evaluation-v1/missions" / (receipt["mission_id"] + ".json")) == receipt["mission_file_sha256"]
    write(PUBLIC / "execution-interruption-v1.json", {"status": "PRE_UNIT_TRANSPORT_INTERRUPTION_NOT_MODEL_TASK_FAILURE",
          "utc_observed": datetime.now(timezone.utc).isoformat(), "completed_units_preserved": len(receipts),
          "planned_units": 408, "location": "SSH status check before the next unit identity/model request",
          "error": "Connection timed out during SSH banner exchange", "next_unit_model_call": "NOT_STARTED",
          "stderr_sha256": sha(old_work / "evaluation.stderr.txt"), "failed_supervisor_resource_sha256": sha(TASK / "jobs/locked-supervisor-v1/resource.json"),
          "document_wait": "Stopped only the identified waiting document child after evaluator exit; all failures retained",
          "frozen_pins_preserved": len(freeze["pins"]), "scientific_protocol_changed": False,
          "phase_or_deadline_reset": False, "rerun_completed_units": False}, True)
    try:
        status = call("status", timeout=45)
        original = read(sorted((TASK / "locked-evaluation-v1").glob("invocation-*.json"))[0])["phase"]
        assert status["phase"] == original["phase"]
        assert status["admission"]["container_id"] == original["admission"]["container_id"]
        remaining = status["phase"]["cpu_base"] + status["phase"]["cpu_cap"] - status["container_cpu_seconds"]
        value = {"status": "PASS_SAME_RUNTIME_RECONNECTED_NO_INFERENCE", "remaining_evaluation_cpu_seconds": remaining,
                 "phase_reset": False, "new_model_call": False, "runtime_status": status}
    except Exception as exc:
        value = {"status": "FAIL_READ_ONLY_RECONNECT", "error": type(exc).__name__ + ": " + str(exc)[-1500:],
                 "new_model_call": False, "phase_reset": False, "system_permissions_changed": False}
    write(TASK / "read-only-reconnect-v1.json", value, True)
    print(json.dumps(value))
    raise SystemExit(0 if value["status"].startswith("PASS") else 1)


if __name__ == "__main__":
    main()
