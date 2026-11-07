"""Bounded opaque byte checks using existing manifests; never decode dataset rows."""
import collections,hashlib,json,time
from datetime import datetime,timezone
from pathlib import Path
import psutil

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.local/data-inventory-20261107-v1'
PUBLIC=ROOT/'docs/evidence/local-data-inventory-20261107-v1'
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def main():
    start=time.process_time();proc=psutil.Process();proc.cpu_affinity([max(proc.cpu_affinity())])
    pins=[];hashed=0
    def check(rel,expected,kind):
        nonlocal hashed
        path=ROOT/rel;size=path.stat().st_size;assert size<=16*1024**2 and hashed+size<=64*1024**2
        digest=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(1024**2),b''):digest.update(block)
        hashed+=size;actual=digest.hexdigest();assert actual==expected,rel
        pins.append({'path':rel,'bytes':size,'sha256':actual,'status':'PASS_CURRENT_BYTE_HASH_MATCH','kind':kind})
    hiv=json.loads((ROOT/'src/curaloop/resources/hiv_manifest.json').read_text())
    check('src/curaloop/resources/hiv_replay_v1.json.gz',hiv['resource_sha256'],'EXPOSED_REPLAY_SUBSET')
    registry=json.loads((ROOT/'research/manifests/ncats_development_tasks_v1.json').read_text())
    for r in registry['records']:check(registry['local_resource_files'][r['task_id']],r['dataset_sha256'],'EXPOSED_DEVELOPMENT_COHORT')
    fs=json.loads((ROOT/'docs/evidence/plan-a-20261105-v1/feature-cohort-v2-result.json').read_text())
    roles=collections.Counter();counts=collections.Counter()
    for task in fs['selected_task_manifest']:
        check('research/raw_data/external-benchmarks/fs-mol-0.1/feature-cohort-v2/'+task['assay_id']+'.features.json',task['feature_sha256'],'LABEL_FREE_FEATURES_'+task['role'].upper())
        roles[task['role']]+=1;counts[task['role']]+=task['retained_structures']
    assert dict(roles)==fs['selected_assay_counts']
    release_paths=['.local/r0-chembl-20261107-v1/ledger.json','.local/r0r-chembl-20261107-v1/ledger.json',
        '.local/r0a1-chembl-20261107-v1/ledger.json','.local/chembl-taskfirst-dq-20261107-v1/ledger.json',
        '.local/chembl-taskfirst-dqr-20261107-v1/ledger.json','.local/r0-design-review-20261107-v1/ledger.json']
    old=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in release_paths]
    save(PRIVATE/'old-ledger-pins-v1.json',{'records':old})
    out={'status':'PASS_BOUNDED_SMALL_FILE_INTEGRITY','utc':datetime.now(timezone.utc).isoformat(),
        'files':pins,'file_count':len(pins),'opaque_bytes_hashed':hashed,'cpu_seconds':time.process_time()-start,
        'fsmol_assays_by_role':dict(roles),'fsmol_structure_rows_by_role_from_existing_manifest':dict(counts),
        'large_source_archives_rehashed':False,'dataset_rows_arrays_or_labels_decoded':False,'source_http_or_ssh':0,
        'new_research_phase_or_budget':False,'old_ledger_pins':old}
    save(PUBLIC/'small-file-integrity-v1.json',out);print(json.dumps({k:v for k,v in out.items() if k not in {'files','old_ledger_pins'}}))
if __name__=='__main__':main()
