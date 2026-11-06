"""One guarded portfolio acceptance or actual stdio-server attempt."""

import argparse
import json
import sys
import traceback
from pathlib import Path

from research.longrun_v1.worker import verify_bundle, write_new, public_failure
from research.longrun_v1.guard import ResourceGuard


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--permit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--mode', choices=['acceptance', 'stdio'], required=True)
    args = p.parse_args()
    permit = json.loads(args.permit.read_text())
    if permit['stage'] != 'C' or args.output.name != permit['attempt'] or not args.output.is_dir():
        raise ValueError('Exact C permit and owned output required')
    guard = ResourceGuard(args.output / 'resources.json', permit)
    status = 'FAIL'
    try:
        root = Path.cwd()
        verify_bundle(root, root / 'bundle.json', permit['bundle_sha256'])
        if args.mode == 'acceptance':
            from .checks import execute
            result = execute(root, args.output)
        else:
            sys.path.insert(0, str(root / 'src'))
            from curaloop_rd.portfolio_v1 import Portfolio
            from curaloop_rd.mcp_v1 import serve
            app = Portfolio(root, root / 'inputs/workflow-registry.json', args.output / 'workspace')
            try: serve(app, sys.stdin.buffer, sys.stdout)
            finally: app.close()
            result = {'status': 'PASS', 'actual_stdio_server': True, 'shutdown': 'CLIENT_EOF',
                      'new_scientific_source_calls': 0, 'live_model_client': 'NOT_RUN'}
        write_new(args.output / 'result.json', result)
        status = 'PASS'
    except BaseException as error:
        (args.output / 'failure-private.txt').write_text(traceback.format_exc(), encoding='utf-8')
        write_new(args.output / 'failure.json', public_failure(error))
    finally: guard.finish(status)
    raise SystemExit(0 if status == 'PASS' else 1)


if __name__ == '__main__': main()
