"""Reuse all passed checks; repair metadata staging in a fresh serial process."""
# ruff: noqa: E402

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import (
    PUBLIC,
    REMOTE,
    TASK,
    authority,
    finish,
    new,
    read,
    sha,
    start,
)
from tools import cf1_matrix_v2 as matrix
from tools import m2c_remote_v2 as transport
from tools.cf1_stage_v1 import stage


def main():
    _, ledger = authority()
    assert not ledger["confirmation_values_analyzed"] and not (TASK / "evaluation-release-v1.json").exists()
    gate = read(TASK / "primary-score-validation-v1.json")
    assert gate["status"] == "PASS_ALL_SIX_PRIMARY_SCORE_AND_OPERATOR_CHECKS"
    assert len(gate["campaigns"]) == 6 and not gate["confirmation_values_analyzed"]
    failed = read(TASK / "jobs/primary-score-validation-v1/controller-result.json")
    assert failed["exit_code"] == 1 and failed["unit_state"]["ActiveState"] == "failed"
    assert "manifest['biological_inputs_included'] is True" in failed["stderr"]
    code = """import json,os,resource,signal,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(10,10));signal.alarm(30)
root=Path(__ROOT__);env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
r=subprocess.run(['systemctl','--user','show','curaloop-cf1-20261109-v1-primary-score-validation-v1'],capture_output=True,text=True,env=env,timeout=10)
s=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
assert s.get('MainPID')=='0' and s.get('ActiveState')=='failed'
target=root/'inputs/primary-score-validation-v1.json';assert not target.exists()
print(json.dumps({'status':'PASS_FAILED_STAGE_TERMINAL_AND_TARGET_ABSENT','MainPID':s['MainPID'],'ActiveState':s['ActiveState'],'metadata_target_absent':True}))
""".replace("__ROOT__", repr(REMOTE))
    response = transport.remote(code, timeout=45)
    assert response.returncode == 0
    terminal = json.loads(response.stdout)
    new(TASK / "metadata-stage-terminal-v2.json", terminal)
    new(PUBLIC / "metadata-stage-repair-v2.json", {**terminal,
        "cause": "Concurrent rendered() calls temporarily mutate the shared bootstrap factory; a stale True marker leaked into later staging in the same process. Worker dispatch does not use that bootstrap body.",
        "repair": "Fresh serial metadata staging reuses exact passed checks and immutable scientific code; no refit or new cell",
        "original_failure_retained": True, "confirmation_values_analyzed": False})
    assert "manifest['biological_inputs_included'] is False" in transport.BOOTSTRAP
    stage("primary-score-validation-retry-v2", [(TASK / "primary-score-validation-v1.json", "inputs/primary-score-validation-v1.json")], bucket="technical_retry_reserve")
    new(TASK / "evaluator-wrapper-gate-v2.json", {"status": "PASS_ALL_REQUIRED_PRE_VALUE_GATES",
        "primary_score_gate_sha256": sha(TASK / "primary-score-validation-v1.json"),
        "metadata_retry": "primary-score-validation-retry-v2", "confirmation_values_analyzed": False})
    matrix.freeze_evaluator()


if __name__ == "__main__":
    guard = start("all-campaign-evaluator-release-repair-v2", 600, 1800,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("all-campaign-evaluator-release-repair-v2", guard, "PASS_SERIAL_FROZEN_EVALUATOR_RELEASE")
    except BaseException:
        finish("all-campaign-evaluator-release-repair-v2", guard, "FAIL")
        raise
