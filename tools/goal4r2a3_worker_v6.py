"""Bounded one-CPU A3 qualification worker; no molecular policy campaigns."""

import argparse
import hashlib
import json
import os
import resource
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/chaw/curaloop-rl/goal4r2a3-20261106-v1')
DEADLINE = datetime(2026, 11, 7, 5, 13, 23, tzinfo=timezone.utc)


def write_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def main():
    if sys.flags.optimize != 0:
        raise RuntimeError('Qualification checks require Python assertions enabled')
    p = argparse.ArgumentParser()
    p.add_argument('--attempt', required=True)
    p.add_argument('--bundle', required=True)
    p.add_argument('--mode', choices=['offline-submit'], required=True)
    args = p.parse_args()
    assert args.attempt.replace('-', '').isalnum()
    assert Path.cwd().resolve() == ROOT and ROOT.resolve() == ROOT and ROOT.stat().st_uid == os.getuid()
    output = ROOT / 'runs' / args.attempt
    output.mkdir(parents=True, exist_ok=False)
    start, cpu = time.monotonic(), time.process_time()
    stamp = datetime.now(timezone.utc).isoformat()
    cpuid = max(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpuid})
    os.nice(19)
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
        os.environ[name] = '1'
    resource.setrlimit(resource.RLIMIT_CPU, (1801, 1802))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    done = threading.Event()
    def watch():
        while not done.wait(.25):
            if time.process_time() - cpu >= 1800 or time.monotonic() - start >= 3600 or datetime.now(timezone.utc) >= DEADLINE:
                os._exit(124)
    threading.Thread(target=watch, daemon=True).start()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / 'private-inputs/linux-vendor'))
    sys.path.insert(0, str(ROOT))
    status = 'FAIL'
    try:
        manifest = json.loads((ROOT / (args.bundle + '.json')).read_text())
        for row in manifest['files']:
            path = ROOT / row['path']
            assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
            assert path.stat().st_size == row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        from research.qualification_v1.submit_adapter_v1 import execute
        result = execute(ROOT, output)
        status = 'PASS'
        print(json.dumps({'status': status, 'attempt': args.attempt, 'result_status': result['status']}))
    except BaseException as error:
        write_new(output / 'failure.json', {'error_type': type(error).__name__, 'message': str(error)})
        from research.qualification_v1.public_receipts_v1 import worker_failure
        print(json.dumps(worker_failure(error)))
        raise SystemExit(1) from None
    finally:
        done.set()
        write_new(output / 'resources.json', {'status': status, 'mode': args.mode,
            'start_utc': stamp, 'finish_utc': datetime.now(timezone.utc).isoformat(),
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.monotonic() - start,
            'cpu_affinity': [cpuid], 'cpu_ceiling': 1800, 'wall_ceiling': 3600,
            'memory_limit_bytes': 4 * 1024**3, 'python': sys.version,
            'python_optimization': sys.flags.optimize, 'child_processes_allowed': False})


if __name__ == '__main__':
    main()
