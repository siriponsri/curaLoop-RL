"""Durable at-most-once supervisor. Private output only; authority lives locally."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())


def birth(process):
    if os.name != 'nt':
        # Parse after the final comm parenthesis, which may contain spaces.
        raw = Path('/proc', str(process.pid), 'stat').read_text()
        return 'linux-startticks:' + raw.rsplit(')', 1)[1].split()[19]
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    values = [wintypes.FILETIME() for _ in range(4)]
    if not kernel.GetProcessTimes(int(process._handle), *(ctypes.byref(v) for v in values)):
        raise ctypes.WinError(ctypes.get_last_error())
    return 'windows-creation:' + str((values[0].dwHighDateTime << 32) | values[0].dwLowDateTime)


def supervise(task_root, bundle, permit_path, mode, python):
    task_root, bundle, permit_path = task_root.resolve(), bundle.resolve(), permit_path.resolve()
    if not bundle.is_relative_to(task_root) or not permit_path.is_relative_to(task_root):
        raise ValueError('Task-owned canonical paths required')
    permit = json.loads(permit_path.read_text())
    if permit['output_partition'] != 'runs/' + permit['attempt']:
        raise ValueError('Exact partition required')
    if datetime.now(timezone.utc) >= datetime.fromisoformat(permit['deadline_utc'].replace('Z', '+00:00')):
        raise ValueError('Expired permit')
    # Verify before any worker code execution; claims never get erased for retry.
    sys.path.insert(0, str(bundle))
    from research.longrun_v1.worker import verify_bundle
    verify_bundle(bundle, bundle / 'bundle.json', permit['bundle_sha256'])
    output = task_root / permit['output_partition']
    output.parent.mkdir(exist_ok=True)
    output.mkdir(exist_ok=False)
    write(output / 'claimed.json', {'token': permit['token'], 'attempt': permit['attempt'],
                                  'permit_sha256': hashlib.sha256(permit_path.read_bytes()).hexdigest(),
                                  'supervisor_pid': os.getpid(), 'utc': datetime.now(timezone.utc).isoformat()})
    env = dict(os.environ)
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[name] = '1'
    with (output / 'stdout-private.txt').open('xb') as stdout, (output / 'stderr-private.txt').open('xb') as stderr:
        process = subprocess.Popen([python, '-B', '-m', 'research.longrun_v1.worker', '--permit', str(permit_path),
                                    '--output', str(output), '--mode', mode], cwd=bundle, env=env,
                                   stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
        identity = {'pid': process.pid, 'birth_id': birth(process), 'token': permit['token']}
        write(output / 'launch.json', identity)
        # wait() observes the original child handle, never a recycled PID.
        try:
            code = process.wait(timeout=permit['wall_seconds'] + 30)
        except subprocess.TimeoutExpired:
            process.kill(); code = process.wait()
        resource = output / 'resources.json'
        if not resource.is_file():
            # Hold ledger lease for explicit reconciliation; never invent a receipt.
            write(output / 'terminal-missing-resource.json', dict(identity, exit_code=code, observed_exited=True))
            raise RuntimeError('Worker ended without usable resource evidence')
        receipt = json.loads(resource.read_text())
        receipt.update(verified_terminal=True)
        if code != 0:
            receipt['status'] = 'FAIL'
        receipt_bytes = (json.dumps(receipt, indent=2, allow_nan=False) + '\n').encode()
        (output / 'terminal-receipt.json').write_bytes(receipt_bytes)
        proof = dict(identity, observed_exited=True, exit_code=code,
                     receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
                     observation='SUPERVISOR_WAIT_ON_ORIGINAL_CHILD_HANDLE')
        write(output / 'terminal-proof.json', proof)
    return {'attempt': permit['attempt'], 'pid': identity['pid'], 'birth_id': identity['birth_id'],
            'exit_code': code, 'receipt_sha256': proof['receipt_sha256']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--permit', type=Path, required=True)
    p.add_argument('--mode', choices=['fixtures', 'native', 'presence'], required=True)
    p.add_argument('--python', default=sys.executable)
    args = p.parse_args()
    print(json.dumps(supervise(args.root, args.bundle, args.permit, args.mode, args.python)))


if __name__ == '__main__':
    main()
