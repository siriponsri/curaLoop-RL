"""Read live CF1 resources and artifact sizes without opening molecular values."""
# ruff: noqa: E402

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import REMOTE, TASK, finish, new, read, start
from tools.m2c_remote_v2 import remote


def main(name):
    guard = start("live-readback-" + name, 60, 90, bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        ledger = read(TASK / "ledger.json")
        names = [k for k, r in ledger["bookings"].items() if r["status"] == "RESERVED" and r["host"] == "dr-train"]
        code = """import json,os,resource,signal,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(10,10));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(40)
os.sched_setaffinity(0,{69})
root=Path(__ROOT__);names=__NAMES__;out={'jobs':{},'model_directories':{}}
assert root.resolve()==root and root.is_dir() and not root.is_symlink()
for name in names:
 folder=root/'jobs'/name
 out['jobs'][name]={}
 for field in ('resource','kernel-proof','failure'):
  p=folder/(field+'.json')
  if p.exists():out['jobs'][name][field]=json.loads(p.read_text())
 env=os.environ.copy();env['XDG_RUNTIME_DIR']='/run/user/'+str(os.getuid());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
 r=subprocess.run(['systemctl','--user','show','curaloop-cf1-20261109-v1-'+name],capture_output=True,text=True,timeout=10,env=env)
 state=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
 out['jobs'][name]['unit']={k:state.get(k) for k in ('MainPID','ActiveState','SubState','CPUUsageNSec','MemoryCurrent','MemoryPeak','Result')}
total=0
for parent,dirs,files in os.walk(root,followlinks=False):
 for name in dirs+files:assert not (Path(parent)/name).is_symlink()
 for name in files:total+=(Path(parent)/name).stat().st_size
out['regular_file_bytes']=total
if (root/'models').exists():
 for folder in (root/'models').iterdir():
  if folder.is_dir():out['model_directories'][folder.name]=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
assert total<8*1024**3
print(json.dumps(out))
""".replace("__ROOT__", repr(REMOTE)).replace("__NAMES__", repr(names))
        result = remote(code, timeout=60)
        assert result.returncode == 0, result.stderr.decode(errors="replace")[-500:]
        value = json.loads(result.stdout)
        new(TASK / ("live-readback-" + name + ".json"), value)
        print(json.dumps(value, indent=2))
        finish("live-readback-" + name, guard, "PASS_READ_ONLY_LIVE_METADATA")
    except BaseException:
        finish("live-readback-" + name, guard, "FAIL")
        raise


if __name__ == "__main__":
    main(sys.argv[1])
