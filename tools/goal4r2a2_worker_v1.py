"""Bounded metadata probe/acquisition/contracts worker; no scientific task access."""

import argparse
import hashlib
import importlib.util
import json
import os
import resource
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/chaw/curaloop-rl/goal4r2a2-20261106-v1')


def write_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def load_client(plan):
    path = ROOT / 'private-tools/pubchem_rest_request.py'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == plan['skill_client_sha256']
    spec = importlib.util.spec_from_file_location('pubchem_skill_client', path)
    client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client)
    return client


def request_description(client, plan, aid, output, suffix='', params=None):
    if aid not in plan['allowed_aids']:
        raise ValueError('AID outside fixed source roster')
    path = 'assay/aid/' + aid + '/description/JSON'
    payload = {'base_url': plan['base_url'], 'path': path, 'method': 'GET',
               'response_format': 'text', 'save_raw': True,
               'raw_output_path': str(output / ('description-' + aid + suffix + '.txt')),
               'timeout_sec': plan['per_request_timeout_seconds'], 'max_items': 1,
               'params': params or {}}
    started = datetime.now(timezone.utc).isoformat()
    result = client.execute(payload)
    raw = Path(payload['raw_output_path'])
    if raw.exists() and raw.stat().st_size > plan['maximum_response_bytes']:
        raise ValueError('Metadata response exceeds byte bound')
    record = {'requested_aid': aid, 'request_utc': started, 'request': payload,
              'result': result, 'response_sha256': hashlib.sha256(raw.read_bytes()).hexdigest() if raw.exists() else None,
              'response_bytes': raw.stat().st_size if raw.exists() else None}
    write_new(output / ('request-' + aid + suffix + '.json'), record)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--mode', choices=['probe', 'acquire', 'validate'], required=True)
    args = parser.parse_args()
    assert args.attempt.replace('-', '').isalnum()
    assert Path.cwd().resolve() == ROOT and ROOT.resolve() == ROOT and ROOT.stat().st_uid == os.getuid()
    output = ROOT / 'runs' / args.attempt
    output.mkdir(parents=True, exist_ok=False)
    begin, cpu = time.monotonic(), time.process_time()
    start_utc = datetime.now(timezone.utc).isoformat()
    cpuid = max(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpuid})
    os.nice(19)
    resource.setrlimit(resource.RLIMIT_CPU, (121, 122))
    resource.setrlimit(resource.RLIMIT_AS, (768 * 1024**2, 768 * 1024**2))
    done = threading.Event()
    def watch():
        while not done.wait(.25):
            if (time.process_time() - cpu >= 120 or time.monotonic() - begin >= 600
                    or datetime.now(timezone.utc) >= datetime(2026, 11, 6, 13, 5, 41, tzinfo=timezone.utc)):
                os._exit(124)
    threading.Thread(target=watch, daemon=True).start()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    status = 'FAIL'
    try:
        manifest = json.loads((ROOT / (args.bundle + '.json')).read_text())
        for row in manifest['files']:
            path = ROOT / row['path']
            assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        plan = json.loads((ROOT / 'research/configs/goal4r2a2_requests_v1.json').read_text())
        if args.mode == 'probe':
            record = request_description(load_client(plan), plan, plan['probe_aid'], output)
            result = {'status': 'PROBE_RESPONSE_RETAINED' if record['result'].get('ok') else 'ACCESS_FAILED',
                      'request': record, 'activity_rows_requested': False}
        else:
            from research.readiness_v1.jobs import execute
            result = execute(args.mode, ROOT, output, plan, begin, load_client, request_description)
        write_new(output / 'results.json', result)
        status = 'PASS'  # Includes a correctly retained ACCESS_FAILED/NO_GO result.
        print(json.dumps({'status': status, 'attempt': args.attempt, 'task_result': result.get('status')}))
    except BaseException as exc:
        write_new(output / 'failure.json', {'exception': type(exc).__name__, 'message': str(exc)})
        raise
    finally:
        done.set()
        write_new(output / 'resources.json', {'status': status, 'mode': args.mode,
                  'start_utc': start_utc, 'finish_utc': datetime.now(timezone.utc).isoformat(),
                  'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.monotonic() - begin,
                  'cpu_affinity': [cpuid], 'cpu_ceiling': 120, 'wall_ceiling': 600,
                  'memory_limit_bytes': 768 * 1024**2, 'python': sys.version})


if __name__ == '__main__':
    main()
