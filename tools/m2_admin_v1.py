"""Single-writer M2 reservation ledger; closed studies are read-only pins."""
import argparse
import ctypes
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/m2-selective-compute-20261108-v1'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')


def cpu_id():
    if os.name != 'nt':
        return min(os.sched_getaffinity(0))
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = ctypes.c_void_p
    k.GetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
    a, b = ctypes.c_size_t(), ctypes.c_size_t()
    if not k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(a), ctypes.byref(b)):
        raise ctypes.WinError(ctypes.get_last_error())
    return next(i for i in range(a.value.bit_length()) if a.value & (1 << i))


def begin():
    release = json.loads((ROOT / 'research/manifests/m2_release_20261108_v1.json').read_text())
    plan = json.loads((ROOT / release['plan_config']).read_text())
    assert release['cpu_cap_seconds'] == 172800 and release['automatic_m3'] is False
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release['deadline_utc'].replace('Z', '+00:00'))
    PRIVATE.mkdir(parents=True, exist_ok=False)
    pins = json.loads((ROOT / '.local/lr-m12-20261108-v1/old-ledger-pins-v1.json').read_text())
    new(PRIVATE / 'previous-ledger-pins.json', pins)
    historical = ['.local/lr-m12-20261108-v1/ledger.json',
                  'research/configs/lr_m12_status_20261108_v1.json',
                  'docs/evidence/lr-m12-20261108-v1/m1-freeze-v2.json']
    new(PRIVATE / 'additional-history-pins.json', {p: sha(ROOT / p) for p in historical})
    new(PRIVATE / 'release-snapshot.json', dict(release,
        plan_sha256=sha(ROOT / release['plan_config']), scope_sha256=sha(ROOT / release['data_scope']),
        plan_document_sha256=sha(ROOT / plan['plan_document'])))
    ledger = {'schema': 'curaloop.m2.ledger.v1', 'status': 'ACTIVE',
        'release_utc': release['release_utc'], 'deadline_utc': release['deadline_utc'],
        'cpu_cap_seconds': 172800,
        'bucket_caps_seconds': {k: int(v * 3600) for k,v in plan['stage_cpu_hours'].items()},
        'bucket_reserved_seconds': {k: 0 for k in plan['stage_cpu_hours']}, 'jobs': [],
        'scientific_units_attempted': 0, 'final_outcomes_opened': False, 'm3_released': False}
    # Conservative envelope for serial metadata inspection, thin orchestration and delivery.
    ledger['bucket_reserved_seconds']['implementation_guards_setup'] = 1200
    ledger['jobs'].append({'job': 'setup-utilities-envelope', 'bucket': 'implementation_guards_setup',
        'host': 'local', 'reservation_seconds': 1200, 'state': 'RESERVED_UTILITIES_ENVELOPE',
        'scope': 'serial lightweight inspection, admission/orchestration; no unguarded ML or payload decode'})
    new(PRIVATE / 'ledger.json', ledger)
    print(json.dumps({'status': 'ACTIVE', 'release': release['release_utc'], 'deadline': release['deadline_utc'],
                      'retained_seconds': 1200, 'local_cpu': cpu_id()}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['begin', 'reserve', 'utilities', 'settle', 'status'])
    p.add_argument('value', nargs='?')
    args = p.parse_args()
    if args.action == 'begin':
        begin(); return
    lock = PRIVATE / '.ledger.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    try:
        ledger = json.loads((PRIVATE / 'ledger.json').read_text())
        if args.action == 'utilities':
            spec=json.loads(Path(args.value).read_text())
            assert ledger['status']=='ACTIVE' and spec['bucket']=='analysis_return_cleanup_delivery_retry'
            assert not any(j['job']==spec['job'] for j in ledger['jobs'])
            seconds=spec['reservation_seconds'];bucket=spec['bucket']
            assert type(seconds) is int and 0 < seconds <= 1200
            assert ledger['bucket_reserved_seconds'][bucket]+seconds <= ledger['bucket_caps_seconds'][bucket]
            ledger['bucket_reserved_seconds'][bucket]+=seconds
            ledger['jobs'].append(dict(spec,host='local',state='RESERVED_UTILITIES_ENVELOPE'))
            output={'retained_seconds':seconds,'scope':spec['scope']}
        elif args.action == 'reserve':
            spec = json.loads(Path(args.value).read_text())
            assert ledger['status'] == 'ACTIVE'
            assert not any(j['job'] == spec['job'] for j in ledger['jobs'])
            bucket, seconds = spec['bucket'], spec['reservation_seconds']
            assert type(seconds) is int and seconds > 0
            assert ledger['bucket_reserved_seconds'][bucket] + seconds <= ledger['bucket_caps_seconds'][bucket]
            active = [j for j in ledger['jobs'] if j['state'] == 'RESERVED']
            assert len(active) < 4
            assert sum(j['host'] == spec['host'] for j in active) < (1 if spec['host'] == 'local' else 3)
            assert sum(ledger['bucket_reserved_seconds'].values()) + seconds <= 172800
            if spec['handler'] == 'calibration':
                status=json.loads((ROOT/'research/configs/m2_status_20261108_v1.json').read_text())
                assert status['scientific_release_open'], 'SCIENTIFIC_RELEASE_STOPPED_AT_OWNER_CHECKPOINT'
                assert seconds == 31 and spec['guard_cpu_seconds'] == 30.5
                assert ledger['scientific_units_attempted'] < 4400
                ledger['scientific_units_attempted'] += 1
            assert datetime.now(timezone.utc).timestamp()+spec['wall_seconds'] < datetime.fromisoformat(ledger['deadline_utc'].replace('Z','+00:00')).timestamp()
            spec['cpu'] = cpu_id() if spec['host'] == 'local' else spec['cpu']
            spec['attempt'] = spec['job']
            spec['schema'] = 'curaloop.m2.permit.v1'
            spec['guard_cpu_seconds'] = spec.get('guard_cpu_seconds', seconds)
            spec['deadline_utc'] = ledger['deadline_utc']
            spec['release_utc'] = ledger['release_utc']
            spec['token'] = hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:24]
            spec['bundle_sha256'] = spec['token']
            new(PRIVATE / 'jobs' / spec['job'] / 'permit.json', spec)
            row = {'job': spec['job'], 'bucket': bucket, 'host': spec['host'], 'cpu': spec['cpu'],
                   'reservation_seconds': seconds, 'state': 'RESERVED'}
            ledger['jobs'].append(row)
            ledger['bucket_reserved_seconds'][bucket] += seconds
            output = {'permit': str(PRIVATE / 'jobs' / spec['job'] / 'permit.json'), 'row': row}
        elif args.action == 'settle':
            row = next(j for j in ledger['jobs'] if j['job'] == args.value)
            assert row['state'] == 'RESERVED'
            resource = json.loads((PRIVATE / 'jobs' / args.value / 'resource.json').read_text())
            assert resource['attempt'] == args.value and resource['status'] in ('PASS','FAIL','FAIL_RESOURCE_LIMIT','FAIL_ADMISSION')
            row['state'] = resource['status']
            row['reported_cpu_seconds'] = resource['cpu_seconds']
            row['resource_sha256'] = sha(PRIVATE / 'jobs' / args.value / 'resource.json')
            output = row
        else:
            output = ledger
        if args.action != 'status':
            temp = PRIVATE / 'ledger.next.json'
            temp.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
            os.replace(temp, PRIVATE / 'ledger.json')
        print(json.dumps(output))
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
