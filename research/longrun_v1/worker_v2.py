"""Versioned metadata-workflow and R1 worker, preserving every executed v1 byte."""

import argparse
import json
import os
import traceback
from pathlib import Path

from .worker import verify_bundle, public_failure, write_new
from .guard import ResourceGuard


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--permit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--mode', choices=['workflow', 'q-fixtures', 'q-canary', 'q-full'], required=True)
    args = p.parse_args()
    permit = json.loads(args.permit.read_text())
    if args.output.name != permit['attempt'] or not args.output.is_dir():
        raise ValueError('Exclusive output partition required')
    guard = ResourceGuard(args.output / 'resources.json', permit)
    status = 'FAIL'
    try:
        root = Path.cwd()
        verify_bundle(root, root / 'bundle.json', permit['bundle_sha256'])
        if args.mode in ('q-canary', 'q-full') and permit['stage'] != 'R1':
            raise ValueError('Intake requires an explicit R1 resource permit')
        if args.mode == 'workflow':
            from .workflow_eval import execute
            result = execute(root, args.output)
        else:
            from .qualification import fixtures, execute
            result = fixtures(root, args.output) if args.mode == 'q-fixtures' else execute(
                root, args.output, 'canary' if args.mode == 'q-canary' else 'full')
        write_new(args.output / 'result.json', result)
        if result['status'].startswith('FAIL'):
            raise AssertionError('Frozen reference evaluation failed; complete results retained')
        status = 'PASS'
    except BaseException as error:
        (args.output / 'failure-private.txt').write_text(traceback.format_exc(), encoding='utf-8')
        write_new(args.output / 'failure.json', public_failure(error))
    finally:
        guard.finish(status)
    raise SystemExit(0 if status == 'PASS' else 1)


if __name__ == '__main__':
    main()
