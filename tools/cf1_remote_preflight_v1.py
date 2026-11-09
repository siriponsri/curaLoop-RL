"""One noninteractive read-only probe; no remote root or experiment creation."""
# ruff: noqa: E402

import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, start


def main():
    profile = "100.77.149.83"
    config = subprocess.run(["rtk", "proxy", "ssh", "-G", profile], capture_output=True, text=True, timeout=20)
    fields = dict(line.split(maxsplit=1) for line in config.stdout.splitlines() if len(line.split(maxsplit=1)) == 2)
    assert config.returncode == 0 and fields["user"] == "chaw" and fields["hostname"] == profile
    assert "id_ed25519_dr_train" in config.stdout
    new(TASK / "ssh-profile.json", {"selected_profile": profile, "user": "chaw",
                                   "configured_identity_verified": True, "private_key_read": False,
                                   "config_changed": False})
    code = '''import json,os,pwd,resource,shutil,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(15)
allowed=sorted(os.sched_getaffinity(0));cpus=[69,70,71];assert all(c in allowed for c in cpus);os.sched_setaffinity(0,{69})
names=['lr-cf1-20261109-v1','lr-cf1-20261109-v1-export-v1','lr-d23-20261109-v1','lr-d23-20261109-v1-export-v1']
paths=[Path.home()/'curaloop-tasks'/n for n in names];active=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   if p.stat().st_uid==os.getuid() and int(p.name)!=os.getpid() and b'curaloop-tasks/' in (p/'cmdline').read_bytes():active.append(int(p.name))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
mem=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'hostname':os.uname().nodename,'candidate_cpus':cpus,'owned_roots_absent':all(not p.exists() and not p.is_symlink() for p in paths),'active_owned_pid_count':len(active),'memory_available':mem,'disk_free':shutil.disk_usage(Path.home()).free,'task_root_created':False,'experiment_started':False,'cgroup_enforcement_proved':False}))
'''
    encoded = base64.b64encode(code.encode()).decode()
    command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
    result = subprocess.run(["rtk", "proxy", "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                             "-o", "StrictHostKeyChecking=yes", profile, command],
                            capture_output=True, text=True, timeout=35)
    new(TASK / "remote-preflight-response.json", {"returncode": result.returncode,
                                                "stdout": result.stdout, "stderr": result.stderr})
    assert result.returncode == 0, "SSH_PREFLIGHT_FAILED_NO_AUTOMATIC_RETRY"
    value = json.loads(result.stdout)
    assert value["user"] == "chaw" and value["hostname"] == "dr-train"
    assert value["owned_roots_absent"] and value["active_owned_pid_count"] == 0
    assert value["memory_available"] > 16 * 1024**3 and value["disk_free"] > 10 * 1024**3
    new(PUBLIC / "remote-preflight-v1.json", {"status": "PASS_READ_ONLY_PREFLIGHT_NOT_COMPUTE_ADMISSION", **value})
    print("PASS read-only SSH preflight; no task files or experiment created")


if __name__ == "__main__":
    guard = start("read-only-remote-preflight", 120, 180, orchestration=True)
    try:
        main()
        finish("read-only-remote-preflight", guard, "PASS_PREFLIGHT_NOT_COMPUTE_ADMISSION")
    except BaseException:
        finish("read-only-remote-preflight", guard, "FAIL")
        raise
