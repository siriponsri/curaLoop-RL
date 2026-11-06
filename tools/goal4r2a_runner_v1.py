"""Single-process Linux fixture checks with bounded CPU/wall and immutable evidence."""

import argparse
import hashlib
import importlib.util
import io
import json
import os
import platform
import resource
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/chaw/curaloop-rl/goal4r2a-20261106-v1')
DEADLINE = datetime(2026, 11, 6, 11, 57, 53, tzinfo=timezone.utc)


def write_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--bundle', required=True)
    args = parser.parse_args()
    if not args.attempt.replace('-', '').isalnum() or not args.bundle.replace('-', '').isalnum():
        raise ValueError('Unsafe attempt/bundle ID')
    if Path.cwd().resolve() != ROOT or ROOT.resolve() != ROOT or ROOT.stat().st_uid != os.getuid():
        raise ValueError('Exact owned task root required')
    if datetime.now(timezone.utc) >= DEADLINE:
        raise RuntimeError('Owner window exhausted')
    output = ROOT / 'runs' / args.attempt
    output.mkdir(parents=True, exist_ok=False)
    started, cpu = time.monotonic(), time.process_time()
    cpuid = max(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpuid})
    os.nice(19)
    resource.setrlimit(resource.RLIMIT_CPU, (121, 122))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / 'src'))
    scratch = ROOT / '.scratch' / args.attempt
    scratch.mkdir(parents=True, exist_ok=False)
    tempfile.tempdir = str(scratch)
    completed = threading.Event()
    base = {'start_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
            'platform': platform.platform(), 'cpu_affinity': [cpuid], 'cpu_ceiling': 120,
            'wall_ceiling': 600, 'descendant_processes_allowed': False,
            'environment_installation': 'NONE_STDLIB_ONLY', 'source_bundle': args.bundle}
    write_new(output / 'started.json', base)

    def watchdog():
        while not completed.wait(.25):
            if (time.process_time() - cpu >= 120 or time.monotonic() - started >= 600
                    or datetime.now(timezone.utc) >= DEADLINE):
                write_new(output / 'resource-failure.json', {'status': 'FAIL_RESOURCE_LIMIT'})
                os._exit(124)
    threading.Thread(target=watchdog, daemon=True).start()
    try:
        manifest = json.loads((ROOT / (args.bundle + '.json')).read_text())
        for row in manifest['files']:
            path = ROOT / row['path']
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Executed source differs from bundle: ' + row['path'])
        case_path = ROOT / 'research/configs/goal4r2a_cases_v1.json'
        freeze = json.loads((ROOT / 'docs/evidence/goal4r2a-20261106-v1/cases-freeze-v1.json').read_text())
        if hashlib.sha256(case_path.read_bytes()).hexdigest() != freeze['cases_sha256']:
            raise ValueError('Pre-implementation cases differ')
        registry = json.loads((ROOT / 'research/manifests/goal4r2a_mfpcba_metadata_v1.json').read_text())
        definitions = []
        for name in registry['source_script_names']:
            ids = name.removesuffix('.sh').split('-')
            if len(ids) not in (1, 2) or not all(value.isdigit() for value in ids):
                raise ValueError('Invalid source script filename')
            definitions.append({'script': name, 'sd_aid': ids[-1], 'dr_aid': ids[0]})
        counts = {'definitions': len(definitions),
                  'unique_primary_aids': len({r['sd_aid'] for r in definitions}),
                  'unique_confirmatory_aids': len({r['dr_aid'] for r in definitions}),
                  'same_aid_definitions': sum(r['sd_aid'] == r['dr_aid'] for r in definitions)}
        if len({r['script'] for r in definitions}) != len(definitions) or counts != registry['expected_metadata_counts']:
            raise ValueError('Metadata projection counts disagree')
        write_new(output / 'metadata-audit.json', {'status': 'PASS_FILENAME_METADATA_PROJECTION',
                  'counts': counts, 'definitions': definitions, 'scientific_datasets_cleared': 0,
                  'eligible_count': 'UNKNOWN', 'activity_rows_read': False})
        spec = importlib.util.spec_from_file_location('rd_workflow_checks', ROOT / 'tests/rd_workflow_v1/test_workflow.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stream = io.StringIO()
        class Recorded(unittest.TextTestResult):
            records = []
            def addSuccess(self, test):
                super().addSuccess(test)
                self.records.append({'id': test.id(), 'status': 'PASS'})
            def addFailure(self, test, err):
                super().addFailure(test, err)
                self.records.append({'id': test.id(), 'status': 'FAIL'})
            def addError(self, test, err):
                super().addError(test, err)
                self.records.append({'id': test.id(), 'status': 'ERROR'})
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Recorded).run(suite)
        (output / 'tests.log').write_text(stream.getvalue(), encoding='utf-8')
        case_ids = [r['id'].split('.test_')[-1][:3] for r in result.records
                    if '.Cases.test_' in r['id']]
        expected = json.loads(case_path.read_text())['cases']
        if sorted(case_ids) != sorted(c['id'] for c in expected) or result.testsRun != 20:
            raise ValueError('Expected exactly twelve frozen cases and eight boundary checks')
        from curaloop_rd.demo import run_demo
        demo = run_demo(output / 'demo') if result.wasSuccessful() else None
        write_new(output / 'results.json', {'status': 'PASS' if result.wasSuccessful() else 'FAIL',
                  'tests': result.testsRun, 'records': result.records, 'frozen_cases': 12,
                  'boundary_checks': 8, 'demo': demo, 'source_sha256': {
                      r['path']: r['sha256'] for r in manifest['files']},
                  'scientific_campaigns': 0, 'live_provider_calls': 0, 'llm_calls': 0})
        status = 'PASS' if result.wasSuccessful() else 'FAIL_CHECKS'
    except BaseException as exc:
        write_new(output / 'failure.json', {'exception': type(exc).__name__, 'message': str(exc)})
        status = 'FAIL_EXCEPTION'
        raise
    finally:
        completed.set()
        write_new(output / 'resources.json', {**base, 'status': locals().get('status', 'FAIL_EXCEPTION'),
                  'finish_utc': datetime.now(timezone.utc).isoformat(),
                  'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.monotonic() - started})
    print(json.dumps({'status': status, 'attempt': args.attempt, 'tests': 20, 'cpu_seconds': time.process_time() - cpu}))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
