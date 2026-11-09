"""Read-only interpreter/dependency inventory before a task-owned CPU environment."""
# ruff: noqa: E402

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, start
from tools import m2c_remote_v2 as transport


def main():
    assert read(TASK / "owner-source-a-v1.json")["choice"] == "A"
    transport.TASK = TASK
    code = '''import importlib.metadata,json,os,pwd,resource,shutil,signal,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(25)
os.sched_setaffinity(0,{69})
names=['python3.8','python3.9','python3.10','python3.11','python3.12','python3','uv','micromamba','conda']
executables={n:shutil.which(n) for n in names};versions={}
for name,path in executables.items():
 if path and name.startswith('python'):
  r=subprocess.run([path,'--version'],capture_output=True,text=True,timeout=3);versions[name]=r.stdout.strip() or r.stderr.strip()
roots=[Path.home()/'curaloop-tasks'/n for n in ('lr-cf1-20261109-v1','lr-cf1-20261109-v1-export-v1')]
active=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   if p.stat().st_uid==os.getuid() and int(p.name)!=os.getpid() and b'curaloop-tasks/' in (p/'cmdline').read_bytes():active.append(int(p.name))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'host':os.uname().nodename,'executables':executables,'versions':versions,'roots_absent':all(not p.exists() and not p.is_symlink() for p in roots),'active_owned_pid_count':len(active),'disk_free':shutil.disk_usage(Path.home()).free,'memory_available':next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')),'task_created':False}))
'''
    result = transport.remote(code, timeout=40)
    new(TASK / "runtime-probe-response-v1.json", {"exit_code": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0
    value = json.loads(result.stdout)
    assert value["user"] == "chaw" and value["host"] == "dr-train" and value["roots_absent"]
    assert value["active_owned_pid_count"] == 0 and value["memory_available"] > 16 * 1024**3
    assert value["disk_free"] > 10 * 1024**3
    new(TASK / "runtime-probe-v1.json", value)
    new(PUBLIC / "runtime-probe-v1.json", {"status": "PASS_READ_ONLY_RUNTIME_INVENTORY", **value})
    print(value)


if __name__ == "__main__":
    guard = start("read-only-runtime-probe", 120, 180, orchestration=True)
    try:
        main()
        finish("read-only-runtime-probe", guard, "PASS_RUNTIME_INVENTORY")
    except BaseException:
        finish("read-only-runtime-probe", guard, "FAIL")
        raise
