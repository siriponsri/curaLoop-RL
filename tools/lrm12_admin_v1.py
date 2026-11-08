"""Single-writer LR-M12 reservation/settlement; never reopen an older ledger."""

import argparse
import ctypes
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/lr-m12-20261108-v1'
LEDGER = PRIVATE / 'ledger.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def local_cpu():
    if os.name != 'nt':
        return min(os.sched_getaffinity(0))
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.GetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t),
                                            ctypes.POINTER(ctypes.c_size_t)]
    mask, system = ctypes.c_size_t(), ctypes.c_size_t()
    if not kernel.GetProcessAffinityMask(kernel.GetCurrentProcess(), ctypes.byref(mask), ctypes.byref(system)):
        raise ctypes.WinError(ctypes.get_last_error())
    return next(i for i in range(mask.value.bit_length()) if mask.value & (1 << i))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['reserve', 'settle', 'status'])
    parser.add_argument('input', nargs='?')
    args = parser.parse_args()
    lock = PRIVATE / '.ledger.lock'
    with lock.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        ledger = json.loads(LEDGER.read_text())
        if args.action == 'reserve':
            assert ledger['status'] == 'ACTIVE'
            spec = json.loads(Path(args.input).read_text())
            job = spec['job']
            assert re.fullmatch('[a-z0-9][a-z0-9-]{0,75}', job)
            assert not any(j['job'] == job for j in ledger['jobs'])
            bucket, host = spec['bucket'], spec['host']
            wall = spec['wall_seconds']
            assert type(wall) is int and wall > 0 and host in ('local', 'dr-train')
            assert datetime.now(timezone.utc).timestamp() + wall < datetime.fromisoformat(ledger['deadline_utc'].replace('Z', '+00:00')).timestamp()
            if bucket.startswith('m2_'):
                assert ledger['m2_release'] is True and ledger['m1_gate'] == 'PASS_PROVISIONAL'
            used = ledger['bucket_reserved_seconds'][bucket] + wall
            assert used <= ledger['bucket_caps_seconds'][bucket]
            active = [j for j in ledger['jobs'] if j['state'] == 'RESERVED']
            assert len(active) < 4
            assert sum(j['host'] == host for j in active) < (1 if host == 'local' else 3)
            cpu = local_cpu() if spec.get('cpu') is None and host == 'local' else spec['cpu']
            assert type(cpu) is int and cpu >= 0
            assert not any(j['host'] == host and j['cpu'] == cpu for j in active)
            memory = spec.get('memory_bytes', 1073741824 if host == 'local' else 4294967296)
            assert 0 < memory <= (1073741824 if host == 'local' else 4294967296)
            local_job = PRIVATE / 'jobs' / job
            local_job.mkdir(parents=True, exist_ok=False)
            code_paths = spec.get('code_paths', ['research/lr_m12_v1/guard.py', 'research/lr_m12_v1/worker.py',
                                                'research/longrun_v1/guard.py'])
            pins = {p: sha(ROOT / p) for p in code_paths}
            for path in code_paths:
                snapshot = local_job / 'code-snapshot' / path
                snapshot.parent.mkdir(parents=True, exist_ok=True)
                with snapshot.open('xb') as stream:
                    stream.write((ROOT / path).read_bytes())
            bundle = hashlib.sha256(json.dumps(pins, sort_keys=True).encode()).hexdigest()
            task_root = str(PRIVATE) if host == 'local' else spec['remote_task_root']
            permit = {'schema': 'curaloop.lr_m12.permit.v1', 'attempt': job, 'token': bundle[:24],
                      'host': host, 'cpu': cpu, 'wall_seconds': wall, 'guard_cpu_seconds': wall,
                      'reservation_seconds': wall, 'memory_bytes': memory,
                      'deadline_utc': ledger['deadline_utc'], 'release_utc': ledger['release_utc'],
                      'bundle_sha256': bundle, 'code_sha256': pins, 'task_root': task_root,
                      'handler': spec['handler'], 'arguments': spec.get('arguments', {})}
            write_new(local_job / 'permit.json', permit)
            ledger['bucket_reserved_seconds'][bucket] = used
            ledger['jobs'].append({'job': job, 'bucket': bucket, 'host': host, 'cpu': cpu,
                                   'reservation_seconds': wall, 'state': 'RESERVED',
                                   'permit_sha256': sha(local_job / 'permit.json')})
            result = {'permit': str(local_job / 'permit.json'), 'cpu': cpu,
                      'retained_seconds': sum(ledger['bucket_reserved_seconds'].values())}
        elif args.action == 'settle':
            job = args.input
            row = next(j for j in ledger['jobs'] if j['job'] == job)
            assert row['state'] == 'RESERVED'
            resource = PRIVATE / 'jobs' / job / 'resource.json'
            receipt = json.loads(resource.read_text())
            assert receipt['status'] in ('PASS', 'FAIL', 'FAIL_RESOURCE_LIMIT', 'FAIL_ADMISSION')
            assert receipt['attempt'] == job and receipt['host'] == row['host']
            row['state'] = receipt['status']
            row['resource_sha256'] = sha(resource)
            row['reported_cpu_seconds'] = receipt['cpu_seconds']
            result = {'job': job, 'state': row['state'],
                      'retained_seconds': sum(ledger['bucket_reserved_seconds'].values())}
        else:
            result = {'status': ledger['status'], 'reserved_seconds': ledger['bucket_reserved_seconds'],
                      'total_seconds': sum(ledger['bucket_reserved_seconds'].values()),
                      'active_jobs': [j['job'] for j in ledger['jobs'] if j['state'] == 'RESERVED'],
                      'm1_gate': ledger['m1_gate'], 'm2_release': ledger['m2_release']}
        if args.action != 'status':
            temp = PRIVATE / 'ledger.next.json'
            with temp.open('w', encoding='utf-8', newline='\n') as stream:
                json.dump(ledger, stream, indent=2)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, LEDGER)
        print(json.dumps(result))
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
