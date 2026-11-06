import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from tools.lrbc_ui_control_v1 import ssh,REMOTE,PUBLIC,write,DATABASE
from research.longrun_v1.coordinator import Coordinator
snap=Coordinator(DATABASE).snapshot()
assert all(r['state'] in ('COMPLETED','FAILED','FAILED_RECONCILED') for r in snap['jobs'])
result=ssh('''
import json,subprocess
from pathlib import Path
root=Path(__ROOT__);rows=[]
for folder in sorted((root/'runs').iterdir()):
 permit=json.loads((folder/'permit.json').read_text());unit=permit['unit']
 assert unit.startswith('curaloop-ui-') and unit.endswith('.service') and permit['remote_root']==str(root)
 r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10);state=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
 if state.get('LoadState')=='not-found':rows.append({'unit':unit,'status':'ALREADY_ABSENT'});continue
 assert state.get('MainPID')=='0' and state.get('ActiveState') in ('inactive','failed')
 assert str(folder/'bootstrap.py') in state['ExecStart']
 cg=Path('/sys/fs/cgroup'+state.get('ControlGroup',''));assert cg==Path('/sys/fs/cgroup') or not cg.exists() or 'populated 0' in (cg/'cgroup.events').read_text()
 proof=json.loads((folder/'tree-proof.json').read_text()) if (folder/'tree-proof.json').is_file() else None
 if proof and proof.get('invocation_id'):assert state['InvocationID']==proof['invocation_id']
 (folder/'unit-before-final-reset.json').write_text(json.dumps(state,indent=2))
 if state['ActiveState']=='failed':
  reset=subprocess.run(['systemctl','--user','reset-failed',unit],capture_output=True,text=True,timeout=10);assert reset.returncode==0
 after=subprocess.run(['systemctl','--user','show',unit,'--property=LoadState','--value'],capture_output=True,text=True,timeout=10)
 assert after.stdout.strip()=='not-found';rows.append({'unit':unit,'status':'PASS_OWNED_TERMINAL_UNIT_ABSENT'})
print(json.dumps({'status':'PASS_OWNED_UNIT_CLEANUP','units':rows}))
'''.replace('__ROOT__',repr(REMOTE)),timeout=60)
write(PUBLIC/'terminal-unit-cleanup-v2.json',result)
write(PUBLIC/'terminal-accounting-v3.json',{'schema':'curaloop.ui.terminal-accounting.v1','contract':snap.get('contract'),'snapshot':{k:v for k,v in snap.items() if k!='jobs'},'job_count':len(snap['jobs']),'jobs':[{'attempt':r['attempt'],'state':r['state'],'reserved_cpu_seconds':r['reserved']} for r in snap['jobs']]})
print(json.dumps({'status':result['status'],'units':len(result['units']),'snapshot_keys':list(snap),'jobs':len(snap['jobs'])}))
