"""Reserve once and guard a local qualification worker, including descendants."""
import argparse
import json
import os
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.sar30_control_v1 import ACCOUNT, ROOT, authority, digest, save_ledger
from tools.dc2_local_guard_v1 import LocalGuard

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',required=True); p.add_argument('--stage',required=True)
    p.add_argument('--cpu',type=int,required=True); p.add_argument('--wall',type=int,required=True)
    p.add_argument('script',type=Path); p.add_argument('args',nargs=argparse.REMAINDER)
    a=p.parse_args(); r,l=authority()
    assert all(x.startswith('remote-') for x in l['active_jobs']) and a.id.replace('-','').isalnum()
    assert all(b['id']!=a.id for b in l['reservations']), 'No repeated attempt'
    assert a.cpu>0 and a.wall>0
    assert sum(b['cpu_seconds'] for b in l['reservations'])+a.cpu<=r['cpu_cap_seconds']
    assert sum(b['cpu_seconds'] for b in l['reservations'] if b['stage']==a.stage)+a.cpu<=r['stage_caps_seconds'][a.stage]
    script=a.script.resolve(); assert script.parent==ROOT/'tools' and script.name.startswith('sar30_')
    if l['status'].startswith('ACTIVE_CLOSEOUT'):
        assert a.stage=='report_delivery' and script.name in ('sar30_report_v1.py','sar30_closeout_v1.py','sar30_delivery_v1.py')
    folder=ACCOUNT/'jobs'/a.id; folder.mkdir(parents=True,exist_ok=False)
    (folder/'executed-source.py.txt').write_bytes(script.read_bytes())
    b=dict(id=a.id,stage=a.stage,cpu_seconds=a.cpu,gpu_allocated_seconds=0,status='RESERVED',pid=os.getpid(),
           script=script.relative_to(ROOT).as_posix(),script_sha256=digest(script),args=a.args,
           started_utc=datetime.now(timezone.utc).isoformat())
    l['reservations'].append(b); l['active_jobs'].append(a.id); save_ledger(l)
    guard=None; code=1
    try:
        guard=LocalGuard(folder/'resources.json',a.cpu,r['deadline_utc'],a.wall)
        sys.argv=[str(script)]+a.args
        runpy.run_path(str(script),run_name='__main__'); code=0
    except SystemExit as e:
        code=e.code if isinstance(e.code,int) else 1
    finally:
        if guard: guard.finish('PASS' if code==0 else 'FAIL')
        l=json.loads((ACCOUNT/'ledger.json').read_text())
        b=next(b for b in l['reservations'] if b['id']==a.id)
        b.update(status='PASS' if code==0 else 'FAIL',exit_code=code,finished_utc=datetime.now(timezone.utc).isoformat())
        if (folder/'resources.json').exists():
            b.update(receipt_sha256=digest(folder/'resources.json'),measured_cpu_seconds=json.loads((folder/'resources.json').read_text())['aggregate_cpu_seconds'])
        l['active_jobs'].remove(a.id); save_ledger(l)
    return code

if __name__=='__main__': raise SystemExit(main())
