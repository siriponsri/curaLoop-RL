"""Aggregate CPU/wall bootstrap for the fresh metadata-only phase."""
BOOT=r'''
import json,sys,os,time,subprocess,signal
from pathlib import Path
from datetime import datetime,timezone
p=Path(sys.argv[1]);permit=json.loads((p/'permit.json').read_text())
until=time.monotonic()+30
while not (p/'release.json').exists():
 if time.monotonic()>until:raise SystemExit(124)
 time.sleep(.05)
assert json.loads((p/'release.json').read_text())['token']==permit['token']
assert datetime.now(timezone.utc)<datetime.fromisoformat(permit['deadline_utc'])
assert os.sched_getaffinity(0)=={permit['cpu']} and os.getpriority(os.PRIO_PROCESS,0)==19
cg=Path('/sys/fs/cgroup'+next(l.split('::',1)[1] for l in Path('/proc/self/cgroup').read_text().splitlines() if l.startswith('0::')))
def usage():return int(dict(l.split() for l in (cg/'cpu.stat').read_text().splitlines())['usage_usec'])/1000000
baseline=usage();start=time.monotonic();env=os.environ.copy()
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:env[key]='1'
env['PYTHONDONTWRITEBYTECODE']='1';env.update(permit.get('environment',{}))
child=subprocess.Popen(permit['argv'],cwd=permit['root'],env=env,start_new_session=True)
limited=None
while child.poll() is None:
 if usage()-baseline>=permit['cpu_limit_seconds']-.5:limited='CPU'
 if time.monotonic()-start>=permit['runtime_seconds']-5 or datetime.now(timezone.utc)>=datetime.fromisoformat(permit['deadline_utc']):limited='WALL'
 if limited:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=2)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  break
 time.sleep(.2)
data={'token':permit['token'],'exit_code':child.returncode,'resource_limit':limited,'cpu_seconds_tree':usage()-baseline,'wall_seconds':time.monotonic()-start}
(p/'payload-exit.json').write_text(json.dumps(data));raise SystemExit(child.returncode or (124 if limited else 0))
'''
