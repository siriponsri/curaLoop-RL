"""Charge/guard one trusted local LR-SAR1 job without touching old ledgers."""
from __future__ import annotations
import argparse
import json
import os
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.sar1_control_v1 import ACCOUNT, ROOT, authority, digest, save_ledger
from tools.dc2_local_guard_v1 import LocalGuard


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--stage', required=True)
    parser.add_argument('--cpu', type=int, required=True)
    parser.add_argument('--wall', type=int, required=True)
    parser.add_argument('script', type=Path)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    release, ledger = authority()
    if ledger['active_jobs'] or not args.id.replace('-', '').replace('_', '').isalnum():
        raise RuntimeError('One unique local attempt required')
    if any(r['id'] == args.id for r in ledger['reservations']):
        raise RuntimeError('Attempt already retained')
    if ledger['status'].startswith('ACTIVE_CLOSEOUT'):
        if args.stage not in ('analysis_return', 'owner_report_delivery'):
            raise RuntimeError('Failed gate allows closeout only')
        if args.script.name not in {'sar1_report_v1.py', 'sar1_closeout_v1.py'}:
            raise RuntimeError('No further research after failed gate')
    stage_used = sum(r['cpu_seconds'] for r in ledger['reservations'] if r['stage'] == args.stage)
    total_used = sum(r['cpu_seconds'] for r in ledger['reservations'])
    if args.cpu <= 0 or args.wall <= 0 or stage_used + args.cpu > release['stage_caps_seconds'][args.stage]['cpu']:
        raise RuntimeError('Stage ceiling exceeded')
    if total_used + args.cpu > release['cpu_cap_seconds']:
        raise RuntimeError('Total ceiling exceeded')
    script = args.script.resolve()
    if not script.is_relative_to(ROOT / 'tools') or not script.name.startswith('sar1_'):
        raise RuntimeError('Task-owned trusted workers only')
    receipt = ACCOUNT / 'jobs' / args.id / 'resources.json'
    receipt.parent.mkdir(parents=True, exist_ok=False)
    entry = {'id': args.id, 'stage': args.stage, 'cpu_seconds': args.cpu,
             'gpu_allocated_seconds': 0, 'status': 'RESERVED', 'pid': os.getpid(),
             'script': script.relative_to(ROOT).as_posix(), 'script_sha256': digest(script),
             'args': args.args, 'started_utc': datetime.now(timezone.utc).isoformat(),
             'receipt': receipt.relative_to(ROOT).as_posix()}
    ledger['reservations'].append(entry)
    ledger['active_jobs'].append(args.id)
    save_ledger(ledger)
    guard, code = None, 1
    try:
        guard = LocalGuard(receipt, args.cpu, release['deadline_utc'], args.wall)
        sys.argv = [str(script)] + args.args
        runpy.run_path(str(script), run_name='__main__')
        code = 0
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    finally:
        status = 'PASS' if code == 0 else 'FAIL'
        if guard:
            guard.finish(status)
        ledger = json.loads((ACCOUNT / 'ledger.json').read_text(encoding='utf-8'))
        entry = next(r for r in ledger['reservations'] if r['id'] == args.id)
        entry.update(status=status, exit_code=code, finished_utc=datetime.now(timezone.utc).isoformat())
        if receipt.exists():
            entry.update(receipt_sha256=digest(receipt),
                         measured_cpu_seconds=json.loads(receipt.read_text())['aggregate_cpu_seconds'])
        ledger['active_jobs'].remove(args.id)
        save_ledger(ledger)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
