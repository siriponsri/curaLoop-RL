"""One bounded local worker; scripts are confined to the new LR1 namespace."""
import argparse,json,os,runpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,authority,digest,reserve,settle
from tools.dc2_local_guard_v1 import LocalGuard
def main():
 p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--stage',required=True);p.add_argument('--cpu',type=int,required=True);p.add_argument('--wall',type=int,required=True);p.add_argument('script',type=Path);p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args()
 r,l=authority(a.stage);assert all(x.startswith('remote-') for x in l['active_jobs']);script=a.script.resolve()
 assert script.parent==ROOT/'tools' and script.name.startswith('saralr1_');folder=ACCOUNT/'jobs'/a.id;folder.mkdir(parents=True,exist_ok=False)
 reserve(a.id,a.stage,a.cpu,scope=script.name);(folder/'executed-source.py.txt').write_bytes(script.read_bytes());guard=None;code=1
 try:
  guard=LocalGuard(folder/'resources.json',a.cpu,r['deadlines_utc'][a.stage],a.wall);sys.argv=[str(script)]+a.args;runpy.run_path(str(script),run_name='__main__');code=0
 except SystemExit as e:code=e.code if isinstance(e.code,int) else 1
 finally:
  if guard:guard.finish('PASS' if code==0 else 'FAIL')
  fields=dict(script=script.relative_to(ROOT).as_posix(),source_sha256=digest(folder/'executed-source.py.txt'),args=a.args,exit_code=code)
  if (folder/'resources.json').exists():fields.update(measured_cpu_seconds=json.loads((folder/'resources.json').read_text())['aggregate_cpu_seconds'],receipt_sha256=digest(folder/'resources.json'))
  settle(a.id,'PASS' if code==0 else 'FAIL',**fields)
 return code
if __name__=='__main__':raise SystemExit(main())
