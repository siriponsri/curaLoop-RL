"""Freeze a single source-bounded preparation recipe and reserve its remote work."""
import base64
import json
import subprocess
from collections import defaultdict
from datetime import datetime
from tools.sar30_control_v1 import ROOT, ACCOUNT, PUBLIC, authority, digest, write_new, save_ledger

PACKAGES={
 'psa-lab/predicting-activity-by-machine-learning':['numpy==1.26.4'],
 'kexinhuang12345/deeppurpose':['DeepPurpose','torch<=2.3.0'],
 'swansonk14/admet_ai':['chemprop==1.6.1','torch<=2.3.0'],
 'felixjwong/antibioticsai':['numpy==1.26.4'],
 'anikaliu/camda-dili':['numpy==1.26.4'],
 'geopandas/geopandas':['geopandas'],
 'olivierbeq/papyrus-scripts':['papyrus-scripts'],
 'chemosim-lab/prolif':['prolif','MDAnalysis'],
 'neuropsychology/neurokit':['neurokit2'],
 'mad-lab-fau/biopsykit':['biopsykit','mne'],
 'rasterio/rasterio':['rasterio'],
 'nriesterer/syllogistic-nvc':['ccobra'],
 'brand-d/cogsci-jnmf':['ccobra'],
 'zitonglu1996/eeg2eeg':['torch<=2.3.0','tqdm'],
 'scitools/iris':['scitools-iris'],
 'ppdebreuck/modnet':['modnet','tensorflow<=2.17.0','tf_keras<=2.17.0','pymatgen<=2024.5.1']}

def main():
    r,l=authority(); assert l['status']=='ACTIVE_STATIC'
    audit=json.loads((PUBLIC/'static-input-and-dependency-audit-v1.json').read_text())['rows']
    groups=defaultdict(list)
    for row in audit:groups[row['repository_lineage']].append(row)
    base=['numpy==1.26.4','pandas==1.5.3','scipy==1.13.1','scikit-learn==1.5.2','matplotlib==3.7.5','rdkit==2023.9.5','openpyxl==3.1.5']
    plan=dict(status='FROZEN_BEFORE_ENVIRONMENT_AND_REFERENCE_OUTCOMES',
       role_freeze_sha256=digest(PUBLIC/'role-and-check-freeze-v1.json'),
       source_commit='c26e151ed601ba109dc4d35e057ff8e73fec469d',
       source_recipe='run_eval.py public bounds and task-repository dependencies, isolated lineage overlays; Python 3.10 base',
       chemprop_compatibility_basis='ADMET-AI source v1 API uses chemprop 1.x; 1.6.1 selected before any new reference outcome',
       constraints='\n'.join(base)+'\ntorch<=2.3.0\ntensorflow<=2.17.0\ntf_keras<=2.17.0\npymatgen<=2024.5.1\n',
       groups=[dict(name='base',ids=[],cases=[],packages=base)],
       locked_ids=[x['instance_id'] for x in audit if x['role']=='locked_candidate'],
       installation_attempts_per_group_max=1,reference_execution_authorized_in_this_worker=False,
       shared_cache_modified=False,scientific_model_downloads=False,early_stop_upper_bound=24)
    for n,(repo,rows) in enumerate(sorted(groups.items(),key=lambda x:min(r['instance_id'] for r in x[1])),1):
        cases=[dict(instance_id=x['instance_id'],imports=sorted(set(x['reference_imports']+x['evaluator_imports'])-{'benchmark'})) for x in rows]
        plan['groups'].append(dict(name=f'lineage-{n:02d}',repository_lineage=repo,ids=[x['instance_id'] for x in rows],cases=cases,packages=PACKAGES[repo]))
    write_new(PUBLIC/'environment-plan-v1.json',plan)
    worker=ROOT/'tools/sar30_environment_worker_v1.py'
    assert sum(b['cpu_seconds'] for b in l['reservations'])+9000<=r['cpu_cap_seconds']
    assert sum(b['cpu_seconds'] for b in l['reservations'] if b['stage']=='environment')+9000<=r['stage_caps_seconds']['environment']
    l['reservations'].append(dict(id='remote-environment-v1',stage='environment',cpu_seconds=9000,gpu_allocated_seconds=0,
        status='RESERVED_REMOTE',worker_sha256=digest(worker),plan_sha256=digest(PUBLIC/'environment-plan-v1.json'),
        scope='Two actual CPU/wall guard probes then one bounded setup/import batch; no reference/agent execution'))
    l['active_jobs'].append('remote-environment-v1');l['status']='ACTIVE_ENVIRONMENT';save_ledger(l)
    payload=dict(release=r,plan=plan,deadline_epoch=datetime.fromisoformat(r['deadline_utc']).timestamp(),
                 worker_b64=base64.b64encode(worker.read_bytes()).decode(),worker_sha256=digest(worker))
    command='python3 -c "import base64;exec(base64.b64decode(\''+payload['worker_b64']+'\'))"'
    p=subprocess.run(['rtk','proxy','ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15',
                      '100.77.149.83',command],input=json.dumps(payload),text=True,capture_output=True,timeout=180)
    value=dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
    write_new(ACCOUNT/'environment-start-transport-v1.json',value)
    print(json.dumps(value))
    assert p.returncode==0,'Do not replay remote dispatch; inspect owned state'

if __name__=='__main__':main()
