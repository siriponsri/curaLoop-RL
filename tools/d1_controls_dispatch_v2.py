"""First dispatch of the already booked controls command via authenticated file.

The original failed at Windows CreateProcess/WinError206 before SSH started.
No permit, context, scientific source or molecular attempt is regenerated here.
"""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import TASK, authority, new, now, read, save_ledger, sha
from tools.d1_remote_v1 import REMOTE, configure, transport


def main():
    _, ledger = authority()
    assert ledger["jobs"]["controls"]["status"] == "RESERVED"
    folder = TASK / "jobs/controls"
    permit = read(folder / "permit.json")
    command = folder / "remote-command.py"
    assert not (folder / "ssh-raw.json").exists() and not (folder / "result.json").exists()
    configure()
    stage_code = '''import hashlib,json,os,resource,signal,subprocess,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(20,20));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(30)
os.sched_setaffinity(0,{69})
root=Path(__ROOT__);assert root.resolve()==root and root.is_dir() and not root.is_symlink()
assert not (root/'jobs/controls').exists()
env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
r=subprocess.run(['systemctl','--user','show','curaloop-d1-20261109-v1-controls'],capture_output=True,text=True,env=env,timeout=10)
assert 'LoadState=not-found' in r.stdout
data=sys.stdin.buffer.read(__SIZE__+1);assert len(data)==__SIZE__ and hashlib.sha256(data).hexdigest()==__SHA__
compile(data,'<authenticated-original-controls-command>','exec')
path=root/'prepared-controls-command-v1.py'
with path.open('xb') as f:f.write(data)
path.chmod(0o600)
print(json.dumps({'status':'PASS_AUTHENTICATED_FIRST_DISPATCH_STAGE','command_sha256':hashlib.sha256(data).hexdigest(),'job_and_unit_absent_before_stage':True}))
'''.replace("__ROOT__", repr(REMOTE)).replace("__SIZE__", str(command.stat().st_size)).replace("__SHA__", repr(sha(command)))
    with command.open("rb") as stream:
        staged = transport.remote(stage_code, stdin=stream, timeout=40)
    new(folder / "file-stage-v2.json", {"exit_code": staged.returncode,
                                        "stdout": staged.stdout.decode(), "stderr": staged.stderr.decode()})
    assert staged.returncode == 0, "STAGE_FAILED_INSPECT_BEFORE_RETRY"
    proof = json.loads(staged.stdout)
    assert proof["command_sha256"] == sha(command) and proof["job_and_unit_absent_before_stage"]
    new(folder / "transport-recovery-v2.json", {
        "status": "PASS_KNOWN_NOT_DISPATCHED_WINDOWS_LENGTH_RECOVERY", "utc": now().isoformat(),
        "original_error": "WinError206 in subprocess.CreateProcess before SSH process creation",
        "original_command_sha256": sha(command), "permit_sha256": sha(folder / "permit.json"),
        "same_original_booking": True, "new_scientific_attempts_added": 0,
    })
    short = "import runpy;runpy.run_path(" + repr(REMOTE + "/prepared-controls-command-v1.py") + ",run_name='__main__')"
    response = transport.remote(short, timeout=permit["wall_seconds"] + 60)
    new(folder / "ssh-raw-v2.json", {"exit_code": response.returncode,
                                    "stdout": response.stdout.decode(), "stderr": response.stderr.decode()})
    assert response.returncode == 0, "UNCERTAIN_REMOTE_OUTCOME_INSPECT_BEFORE_RETRY"
    data = json.loads(response.stdout)
    new(folder / "controller-result-v2.json", data)
    for field in ("result", "resource", "kernel-proof", "failure"):
        if field in data:
            new(folder / (field + ".json"), data[field])
    ledger = read(TASK / "ledger.json")
    ledger["jobs"]["controls"]["status"] = "PASS" if data["exit_code"] == 0 and data.get("result", {}).get("status") == "PASS" else "FAIL"
    save_ledger(ledger)
    print({"job": "controls", "status": ledger["jobs"]["controls"]["status"], "exit_code": data["exit_code"]})
    assert ledger["jobs"]["controls"]["status"] == "PASS"


if __name__ == "__main__":
    main()
