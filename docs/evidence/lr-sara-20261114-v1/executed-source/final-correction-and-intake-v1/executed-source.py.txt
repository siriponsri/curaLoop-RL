"""Freeze one correction recipe; run its setup alongside authorized asset upload."""
import base64,json,subprocess
from concurrent.futures import ThreadPoolExecutor
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,save,write_new
from tools.sara_transport_v1 import source_call
from tools.sar30_start_environment_v1 import PACKAGES

def upload(r):
 folder=ACCOUNT/'native-assets-v1';results=[]
 for local,name in [(folder/'native-assets.tar.gz','native-assets.tar.gz'),(folder/'private-member-manifest.json','native-member-manifest.json'),(folder/'private-cases.json','native-cases.json')]:
  p=subprocess.run(['rtk','proxy','scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',str(local),
                    '100.77.149.83:'+r['remote_root']+'/incoming/'+name],capture_output=True,text=True,timeout=2000)
  receipt=dict(exit_code=p.returncode,bytes=local.stat().st_size,sha256=digest(local),stderr=p.stderr)
  write_new(ACCOUNT/(name+'.upload-v1.json'),receipt);results.append(receipt)
  assert p.returncode==0,'Transfer recovery must inspect existing bytes, not replay any scientific attempt'
 return {'status':'PASS_COHORT_ASSETS_UPLOADED_NOT_EXECUTED','files':len(results)}

def main():
 r,l=authority('technical');assert l['attempts']['correction_batch'] is None
 diagnosis=json.loads((PUBLIC/'dependency-diagnosis-v1.json').read_text())
 errors={x['instance_id']:x['result'].get('error_message','') for x in diagnosis['diagnosis']['cases']}
 assert "Read-only file system: '/root/.data'" in errors[22] and 'libXrender.so.1' in errors[26]
 old=json.loads((ROOT/'docs/evidence/lr-sar30-qual-20261114-v1/static-input-and-dependency-audit-v1.json').read_text())['rows']
 by_repo={}
 for row in old:by_repo.setdefault(row['repository_lineage'],[]).append(row)
 base_repos={'psa-lab/predicting-activity-by-machine-learning','felixjwong/antibioticsai','anikaliu/camda-dili'}
 def cases(rows):return [dict(instance_id=x['instance_id'],imports=sorted(set(x['reference_imports']+x['evaluator_imports'])-{'benchmark'})) for x in rows]
 groups=[dict(name='base',reuse='base',packages=[],cases=cases([x for x in old if x['repository_lineage'] in base_repos]))]
 for repo,reuse,name in [('olivierbeq/papyrus-scripts','lineage-07','papyrus'),('chemosim-lab/prolif','lineage-08','prolif')]:
  groups.append(dict(name=name,reuse=reuse,repository_lineage=repo,packages=[],cases=cases(by_repo[repo])))
 ccobra=[]
 for repo,rows in sorted(by_repo.items(),key=lambda pair:min(x['instance_id'] for x in pair[1])):
  if repo in base_repos or repo in {'olivierbeq/papyrus-scripts','chemosim-lab/prolif'}:continue
  if repo in {'nriesterer/syllogistic-nvc','brand-d/cogsci-jnmf'}:ccobra+=rows;continue
  groups.append(dict(name='profile-'+str(min(x['instance_id'] for x in rows)),repository_lineage=repo,packages=PACKAGES[repo],cases=cases(rows)))
 groups.append(dict(name='ccobra',repository_lineage='shared-nvc-cogsci-inputs',packages=['ccobra'],cases=cases(ccobra)))
 constraints='numpy==1.26.4\npandas==1.5.3\nscipy==1.13.1\nscikit-learn==1.5.2\nmatplotlib==3.7.5\nrdkit==2023.9.5\nopenpyxl==3.1.5\ntorch<=2.3.0\ntensorflow<=2.17.0\ntf_keras<=2.17.0\npymatgen<=2024.5.1\n'
 worker=ROOT/'tools/sara_correction_worker_v1.py'
 plan=dict(status='FROZEN_BEFORE_SINGLE_CORRECTION_BATCH',correction_batch_number=1,
     source_environment_commit='c26e151ed601ba109dc4d35e057ff8e73fec469d',worker_sha256=digest(worker),
     diagnostic_receipt_sha256=digest(PUBLIC/'dependency-diagnosis-v1.json'),
     role_freeze_sha256=digest(ROOT/r['role_freeze_source']),
     changes=[{'cause':'Papyrus pystow writes /root/.data','fix':'Explicit owned writable HOME/PYSTOW/XDG/MPL caches; read-only root retained'},
              {'cause':'ProLIF RDKit Draw missing libXrender.so.1','fix':'Download/extract Debian libxrender1 and its declared dependency closure into owned library overlay; no host install'},
              {'cause':'Prior ENOSPC with 4 GiB temporary mount','fix':'Owned disk-backed TMPDIR and root-owned private pip cache with measured free space and bounded writable workspace'},
              {'cause':'Docker CLI failed before any guard start under 1 GiB address ceiling','fix':'8 GiB host address ceiling, within 32 GiB aggregate; cause provisional; actual guard probes now passed'}],
     system_packages=['libxrender1','libgomp1'],system_package_basis='Upstream libxrender1 and GCC runtime closure; no base libc overlay or compiler/version search',
     constraints=constraints,groups=groups,max_install_attempts_per_operation=1,further_batches=False,
     downloads='Ordinary signed apt/PyPI distributions only, <=20 GiB container receive; no scientific inputs/actor weights',
     writable_workspace_cap_bytes=64*1024**3,other_owned_artifact_reserve_bytes=16*1024**3,
     native_references_executed=0,agent_calls=0)
 write_new(PUBLIC/'final-correction-plan-v1.json',plan)
 l['attempts']['correction_batch']={'id':'final-correction-v1','number':1,'status':'FROZEN','plan_sha256':digest(PUBLIC/'final-correction-plan-v1.json')}
 l['status']='ACTIVE_FINAL_CORRECTION';save(l)
 reserve('remote-final-correction-v1','technical',7800,remote=True,scope='One fixed apt/PyPI correction batch and offline import regression; host 1200 + setup 5400 + imports 600 CPU seconds, no GPU')
 with ThreadPoolExecutor(max_workers=2) as pool:
  setup=pool.submit(source_call,worker,dict(plan=plan),ACCOUNT/'correction-transport-v1.json',timeout=8500)
  transfer=pool.submit(upload,r)
  results={};failures={}
  for name,future in [('setup',setup),('transfer',transfer)]:
   try:results[name]=future.result()
   except BaseException as e:failures[name]={'type':type(e).__name__,'message':str(e)}
 write_new(ACCOUNT/'correction-and-intake-outcomes-v1.json',{'results':results,'failures':failures})
 if 'setup' in results:
  result=results['setup'];write_new(PUBLIC/'final-correction-result-v1.json',result)
  l=json.loads((ACCOUNT/'ledger.json').read_text());l['attempts']['correction_batch']['status']=result['status'];save(l)
  settle('remote-final-correction-v1',result['status'],measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds'])
 print(json.dumps({'failures':failures,'transfer':results.get('transfer'),'correction_status':results.get('setup',{}).get('status')}))
 assert not failures,'Inspect exact retained attempt; no correction replay'

if __name__=='__main__':main()
