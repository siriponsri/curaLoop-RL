"""Restore existing material and execute engineering build cycle one."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,save,write_new
from tools.envstable_transport_v1 import call
def main():
 r,l=authority('build');assert l['diagnosis_mechanism_supported'] and not l['attempts']['engineering_cycles']
 old=ROOT/'.local/lr-sar30-qual-20261114-v1/remote-return-v1';proof=json.loads((ROOT/'docs/evidence/lr-sar30-qual-20261114-v1/owned-return-verification-v1.json').read_text())
 bundle=old/'owned-return.tar.gz';assert digest(bundle)=='4351f5c2675fc5580f163d9a5c19fb4e1dd49ae0f512aedb511ef919c00e8ca3'
 for source,name in [(bundle,'prior-return.tar.gz'),(old/'owned-manifest.json','prior-manifest.json')]:
  p=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',str(source),'100.77.149.83:'+r['remote_root']+'/incoming/'+name],capture_output=True,text=True,timeout=1800)
  write_new(ACCOUNT/(name+'.upload-v1.json'),dict(exit_code=p.returncode,bytes=source.stat().st_size,sha256=digest(source),stderr=p.stderr));assert p.returncode==0,'Inspect existing bytes before transport recovery'
 plan=json.loads((ROOT/'docs/evidence/lr-sara-20261114-v1/final-correction-plan-v1.json').read_text())
 plan={k:plan[k] for k in ('groups','constraints')};
 for group in plan['groups']:
  if group['name']=='profile-21':group['reuse']='lineage-06'
 write_new(PUBLIC/'engineering-build-plan-v1.json',dict(plan,cycle=1,source_plan_sha256=digest(ROOT/'docs/evidence/lr-sara-20261114-v1/final-correction-plan-v1.json')))
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering_cycles'].append(dict(cycle=1,status='DISPATCHED'));save(l)
 reserve('remote-profile-build-cycle1','build',18000,remote=True,scope='Restore complete env artifacts, prep system libraries, missing profile installation and fresh import workers; CPU-bounded cycle one')
 result=call(ROOT/'tools/envstable_build_worker_v1.py',dict(plan=plan,prior_bundle_sha256=digest(bundle)),ACCOUNT/'build-cycle1-transport.json',timeout=24000)
 write_new(PUBLIC/'profile-build-cycle1.json',result);settle('remote-profile-build-cycle1',result['status'],measured_host_process_cpu_seconds=result['host_process_cpu_seconds'],dependency_receive_bytes=result['dependency_receive_bytes'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['engineering_cycles'][0]['status']=result['status'];save(l)
 print(json.dumps(dict(status=result['status'],profiles=[dict(name=x['name'],install=(x['install'] or {}).get('result',{}).get('status') if x.get('install') else 'REUSED',imports=((x.get('imports') or {}).get('result') or {}).get('status')) for x in result['rows']])))
if __name__=='__main__':main()
