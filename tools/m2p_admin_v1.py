"""Fresh one-hour M2 profiling ledger, separate from the closed molecular release."""
import argparse
import ctypes
import hashlib
import json
import os
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TASK=ROOT/'.local/m2-cpu-profile-20261108-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def local_cpu():
    if os.name!='nt':return min(os.sched_getaffinity(0))
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.GetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
    a,b=ctypes.c_size_t(),ctypes.c_size_t()
    assert k.GetProcessAffinityMask(k.GetCurrentProcess(),ctypes.byref(a),ctypes.byref(b))
    return next(i for i in range(a.value.bit_length()) if a.value&(1<<i))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['begin','reserve','utilities','settle','status'])
    p.add_argument('value',nargs='?');a=p.parse_args()
    if a.action=='begin':
        release=json.loads((ROOT/'research/manifests/m2_profile_release_20261108_v1.json').read_text())
        spec=json.loads((ROOT/release['specification']).read_text())
        old=ROOT/'.local/m2-selective-compute-20261108-v1/ledger.json'
        prior=json.loads(old.read_text())
        assert prior['status']=='CLOSED_OWNER_RESOURCE_CHECKPOINT'
        assert sum(prior['bucket_reserved_seconds'].values())==4112
        assert sum(spec['cpu_reservations_seconds'].values())==3600
        assert datetime.now(timezone.utc)<datetime.fromisoformat(release['deadline_utc'].replace('Z','+00:00'))
        TASK.mkdir(parents=True,exist_ok=False)
        new(TASK/'release-snapshot.json',dict(release,specification_sha256=sha(ROOT/release['specification'])))
        history=[old,ROOT/'docs/evidence/m2-selective-compute-20261108-v1/fresh-absence-v1.json',
                 ROOT/'research/m2_v1/models.py',ROOT/'research/configs/m2_status_20261108_v1.json']
        history += [ROOT/r['path'] for r in json.loads((ROOT/'.local/m2-selective-compute-20261108-v1/previous-ledger-pins.json').read_text())['records']]
        new(TASK/'previous-state-pins.json',{x.relative_to(ROOT).as_posix():sha(x) for x in history})
        ledger={'schema':'curaloop.m2_profile.ledger.v1','status':'ACTIVE_SYNTHETIC_ONLY',
            'release_utc':release['release_utc'],'deadline_utc':release['deadline_utc'],
            'cpu_cap_seconds':3600,'cumulative_previous_seconds':4112,'cumulative_cap_seconds':172800,
            'bucket_caps_seconds':spec['cpu_reservations_seconds'],
            'bucket_reserved_seconds':{k:0 for k in spec['cpu_reservations_seconds']},
            'attempted_profiles':0,'jobs':[],'biological_data_opened':False,'final_outcomes_opened':False}
        # All lightweight serial launch/probe activity is conservatively charged here.
        ledger['bucket_reserved_seconds']['setup_transport']=20
        ledger['bucket_reserved_seconds']['analysis_delivery']=100
        ledger['jobs']=[{'job':'setup-orchestration','state':'CHARGED_UTILITIES_ENVELOPE','host':'local','reservation_seconds':20},
                        {'job':'delivery-orchestration','state':'CHARGED_UTILITIES_ENVELOPE','host':'local','reservation_seconds':100}]
        new(TASK/'ledger.json',ledger)
        print(json.dumps({'status':ledger['status'],'release':ledger['release_utc'],'deadline':ledger['deadline_utc']}));return
    lock=TASK/'.ledger.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        ledger=json.loads((TASK/'ledger.json').read_text())
        if a.action=='utilities':
            spec=json.loads(Path(a.value).read_text());bucket=spec['bucket'];n=spec['reservation_seconds']
            assert ledger['status']=='ACTIVE_SYNTHETIC_ONLY' and bucket=='return_verification_cleanup' and 0<n<=60
            assert not any(j['job']==spec['job'] for j in ledger['jobs'])
            assert ledger['bucket_reserved_seconds'][bucket]+n<=ledger['bucket_caps_seconds'][bucket]
            ledger['bucket_reserved_seconds'][bucket]+=n
            ledger['jobs'].append(dict(spec,host='local',state='CHARGED_UTILITIES_ENVELOPE'));out=spec
        elif a.action=='reserve':
            spec=json.loads(Path(a.value).read_text());job=spec['job'];bucket=spec['bucket'];n=spec['reservation_seconds']
            assert ledger['status']=='ACTIVE_SYNTHETIC_ONLY'
            assert not any(j['job']==job for j in ledger['jobs'])
            assert type(n)is int and 0<n<=ledger['bucket_caps_seconds'][bucket]-ledger['bucket_reserved_seconds'][bucket]
            active=[j for j in ledger['jobs'] if j['state']=='RESERVED']
            assert len(active)<2 and not any(j['host']==spec['host'] for j in active)
            assert datetime.now(timezone.utc).timestamp()+spec['wall_seconds']<datetime.fromisoformat(ledger['deadline_utc'].replace('Z','+00:00')).timestamp()
            if spec['handler']=='profile':
                assert n==185 and spec['wall_seconds']==240 and ledger['attempted_profiles']<14
                assert spec['arguments']['n']==303 and spec['arguments']['budget']==32 and spec['arguments']['policy']in('G1','P')
                ledger['attempted_profiles']+=1
            spec.update(schema='curaloop.m2_profile.permit.v1',attempt=job,
                release_utc=ledger['release_utc'],deadline_utc=ledger['deadline_utc'])
            spec['cpu']=local_cpu() if spec['host']=='local' else spec['cpu']
            assert spec['memory_bytes']<=(536870912 if spec['host']=='local' else 4294967296)
            spec['guard_cpu_seconds']=spec.get('guard_cpu_seconds',n-0.5)
            spec['token']=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:24]
            spec['bundle_sha256']=spec['token']
            new(TASK/'jobs'/job/'permit.json',spec)
            ledger['bucket_reserved_seconds'][bucket]+=n
            ledger['jobs'].append({'job':job,'bucket':bucket,'host':spec['host'],'state':'RESERVED','reservation_seconds':n})
            out={'job':job,'permit':str(TASK/'jobs'/job/'permit.json')}
        elif a.action=='settle':
            row=next(j for j in ledger['jobs'] if j['job']==a.value);assert row['state']=='RESERVED'
            resource=TASK/'jobs'/a.value/'resource.json';r=json.loads(resource.read_text())
            assert r['status']in('PASS','FAIL','FAIL_RESOURCE_LIMIT') and r['attempt']==a.value
            row.update(state=r['status'],reported_cpu_seconds=r['cpu_seconds'],resource_sha256=sha(resource));out=row
        else:out=ledger
        if a.action!='status':
            tmp=TASK/'ledger.next.json';tmp.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8');os.replace(tmp,TASK/'ledger.json')
        print(json.dumps(out))
    finally:lock.unlink()


if __name__=='__main__':main()
