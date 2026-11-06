"""Close only a terminal, absent UI unit as FAILED_RECONCILED; never infer PASS."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import PRIVATE,PUBLIC,DATABASE,Coordinator,ssh,write,sha

def reconcile(attempt):
    assert attempt.startswith('ui-') and attempt.replace('-','').isalnum()
    path=PRIVATE/'runs'/attempt/'tree-proof.json';proof=json.loads(path.read_text());permit=proof['permit']
    assert permit['attempt']==attempt and proof['owned_invocation']
    assert (proof['after_stop'].get('LoadState')=='not-found' or (proof['after_stop'].get('ActiveState')=='failed' and proof['after_stop'].get('MainPID')=='0' and proof['after_stop'].get('InvocationID')==proof['invocation_id'])) and proof['populated_after_stop']=='CGROUP_ABSENT'
    fresh=ssh('''
import json,subprocess
from pathlib import Path
unit=__UNIT__;cg=Path(__CG__)
r=subprocess.run(['systemctl','--user','show',unit],capture_output=True,text=True,timeout=10)
state=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
assert not cg.exists()
if state.get('LoadState')!='not-found':
 assert state.get('InvocationID')==__INV__ and state.get('MainPID')=='0' and state.get('ActiveState')=='failed'
 subprocess.run(['systemctl','--user','reset-failed',unit],check=True,capture_output=True,timeout=10)
r=subprocess.run(['systemctl','--user','show',unit,'--property=LoadState','--value'],capture_output=True,text=True,timeout=10)
print(json.dumps({'load_state':r.stdout.strip(),'cgroup_absent':not cg.exists()}))
'''.replace('__UNIT__',repr(permit['unit'])).replace('__CG__',repr('/sys/fs/cgroup'+proof['launch_properties']['ControlGroup'])).replace('__INV__',repr(proof['invocation_id'])))
    assert fresh=={'load_state':'not-found','cgroup_absent':True}
    receipt={'schema':'curaloop.ui.reconciliation.v1','attempt':attempt,'token':permit['token'],
      'status':'FAILED_RECONCILED','reason':'Original collector could not corroborate CPU counters after systemd removed the empty cgroup. No original acceptance promoted to PASS.',
      'aggregate_cpu_seconds':int(proof['terminal_properties']['CPUUsageNSec'])/1e9,'retained_cpu_seconds':900,
      'fresh_absence':fresh,'original_proof_sha256':sha(path.read_bytes())}
    db=Coordinator(DATABASE)
    with db.transaction() as con:
        row=con.execute('SELECT * FROM jobs WHERE attempt=?',(attempt,)).fetchone()
        assert row['state']=='UNKNOWN' and json.loads(row['permit'])==permit
        con.execute('UPDATE jobs SET state=?,receipt_sha256=?,completion=? WHERE attempt=?',('FAILED_RECONCILED',sha(json.dumps(receipt,sort_keys=True).encode()),json.dumps(receipt,sort_keys=True),attempt))
    write(PUBLIC/(attempt+'-reconciliation.json'),receipt)
    print(json.dumps({'attempt':attempt,'status':receipt['status'],'fresh_absence':fresh}))

if __name__=='__main__':reconcile(sys.argv[1])
