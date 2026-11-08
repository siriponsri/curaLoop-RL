"""Single-writer cumulative M2 ledger with per-stage and information gates."""
import argparse
import ctypes
import hashlib
import json
import os
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-costed-20261108-v2'
BIO={'prefix','branch','tuning','main','ablation','transfer','gate_fit','prepare_development'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def new(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def local_cpu():
    if os.name!='nt':return min(os.sched_getaffinity(0))
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.GetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
    a,b=ctypes.c_size_t(),ctypes.c_size_t();assert k.GetProcessAffinityMask(k.GetCurrentProcess(),ctypes.byref(a),ctypes.byref(b))
    return next(i for i in range(a.value.bit_length()) if a.value&(1<<i))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['begin','reserve','settle','status','admit'])
    p.add_argument('value',nargs='?');a=p.parse_args()
    if a.action=='begin':
        release=json.loads((ROOT/'research/manifests/m2_costed_release_20261108_v2.json').read_text())
        cfg=json.loads((ROOT/release['specification']).read_text())
        old=json.loads((ROOT/'.local/m2-selective-compute-20261108-v1/ledger.json').read_text())
        profile=json.loads((ROOT/'.local/m2-cpu-profile-20261108-v1/ledger.json').read_text())
        prior=sum(old['bucket_reserved_seconds'].values())+sum(profile['bucket_reserved_seconds'].values())
        assert prior==6922 and profile['status']=='CLOSED_COMPLETE_FOR_OWNER_REVIEW'
        assert sum(cfg['remaining_stage_cpu_seconds'].values())==164250 and prior+164250<=172800
        assert datetime.now(timezone.utc)<datetime.fromisoformat(release['deadline_utc'].replace('Z','+00:00'))
        TASK.mkdir(parents=True,exist_ok=False)
        new(TASK/'release-snapshot.json',dict(release,specification_sha256=sha(ROOT/release['specification'])))
        paths=['.local/m2-selective-compute-20261108-v1/ledger.json','.local/m2-cpu-profile-20261108-v1/ledger.json',
               'research/m2_v1/models.py','research/configs/m2_status_20261108_v1.json',
               'research/configs/m2_profile_status_20261108_v1.json']
        new(TASK/'previous-state-pins.json',{n:sha(ROOT/n) for n in paths})
        ledger={'schema':'curaloop.m2_costed.ledger.v2','status':'ACTIVE_TECHNICAL_ADMISSION',
            'release_utc':release['release_utc'],'deadline_utc':release['deadline_utc'],'prior_retained_seconds':prior,
            'remaining_grant_seconds':164250,'cumulative_cap_seconds':172800,
            'bucket_caps_seconds':cfg['remaining_stage_cpu_seconds'],
            'bucket_reserved_seconds':{k:0 for k in cfg['remaining_stage_cpu_seconds']},
            'attempted_units':0,'technical_admission':'NOT_RUN','development_labels_decoded':False,
            'final_outcomes_opened':False,'m3_released':False,'jobs':[]}
        ledger['bucket_reserved_seconds']['engineering_guards']=3600
        ledger['jobs']=[{'job':'serial-orchestration-utilities','host':'local','state':'CHARGED_UTILITIES_ENVELOPE',
                        'reservation_seconds':3600,'scope':'thin serial/three-slot orchestration, metadata/probe/source control; no unguarded ML or label decode'}]
        new(TASK/'ledger.json',ledger);print(json.dumps({'status':ledger['status'],'prior_retained_seconds':prior,'deadline':ledger['deadline_utc']}));return
    lock=TASK/'.ledger.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        ledger=json.loads((TASK/'ledger.json').read_text())
        if a.action=='reserve':
            s=json.loads(Path(a.value).read_text());job=s['job'];bucket=s['bucket'];n=s['reservation_seconds']
            assert ledger['status']in('ACTIVE_TECHNICAL_ADMISSION','ACTIVE_DEVELOPMENT')
            assert not any(j['job']==job for j in ledger['jobs'])
            assert type(n)is int and 0<n<=ledger['bucket_caps_seconds'][bucket]-ledger['bucket_reserved_seconds'][bucket]
            assert sum(ledger['bucket_reserved_seconds'].values())+n<=164250
            active=[j for j in ledger['jobs'] if j['state']=='RESERVED']
            assert len(active)<4 and sum(j['host']==s['host'] for j in active)<(1 if s['host']=='local' else 3)
            if s['host']=='dr-train':assert not any(j.get('cpu')==s['cpu'] and j['host']=='dr-train' for j in active)
            assert datetime.now(timezone.utc).timestamp()+s['wall_seconds']<datetime.fromisoformat(ledger['deadline_utc'].replace('Z','+00:00')).timestamp()
            if s['handler']in BIO:assert ledger['technical_admission']=='PASS' and ledger['status']=='ACTIVE_DEVELOPMENT'
            if s.get('execution_unit',False):
                assert ledger['attempted_units']<4386;ledger['attempted_units']+=1
            s.update(schema='curaloop.m2_costed.permit.v2',attempt=job,release_utc=ledger['release_utc'],deadline_utc=ledger['deadline_utc'])
            s['cpu']=local_cpu() if s['host']=='local' else s['cpu']
            assert s['memory_bytes']<=(536870912 if s['host']=='local' else 4294967296)
            s['guard_cpu_seconds']=s.get('guard_cpu_seconds',n-0.5)
            s['token']=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()[:24];s['bundle_sha256']=s['token']
            new(TASK/'jobs'/job/'permit.json',s)
            ledger['bucket_reserved_seconds'][bucket]+=n
            ledger['jobs'].append({'job':job,'bucket':bucket,'host':s['host'],'cpu':s['cpu'],
                                  'state':'RESERVED','reservation_seconds':n,'execution_unit':s.get('execution_unit',False)})
            out={'job':job,'permit':str(TASK/'jobs'/job/'permit.json')}
        elif a.action=='settle':
            row=next(j for j in ledger['jobs'] if j['job']==a.value);assert row['state']=='RESERVED'
            path=TASK/'jobs'/a.value/'resource.json';r=json.loads(path.read_text())
            assert r['attempt']==a.value and r['status']in('PASS','FAIL','FAIL_RESOURCE_LIMIT','FAIL_ADMISSION')
            row.update(state=r['status'],reported_cpu_seconds=r['cpu_seconds'],resource_sha256=sha(path));out=row
        elif a.action=='admit':
            result=json.loads((TASK/'technical-admission-result.json').read_text())
            assert result['status']=='PASS_COMPLETE_SYNTHETIC_ADMISSION' and result['unique_contexts']==96
            assert result['biological_labels_decoded'] is False
            ledger.update(technical_admission='PASS',status='ACTIVE_DEVELOPMENT',admission_result_sha256=sha(TASK/'technical-admission-result.json'))
            out={'technical_admission':'PASS','development_labels_conditionally_released':True}
        else:out=ledger
        if a.action!='status':
            tmp=TASK/'ledger.next.json';tmp.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8');os.replace(tmp,TASK/'ledger.json')
        print(json.dumps(out))
    finally:lock.unlink()


if __name__=='__main__':main()
