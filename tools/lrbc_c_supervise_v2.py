"""One durable C worker and a fixed real stdio test client; no model/API calls."""

import hashlib
import json
import os
import select
import subprocess
import sys
import traceback
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())



def read_frame(fd, capture, buffer=b'', *, timeout=30, maximum=1024*1024):
    deadline=time.monotonic()+timeout
    while b'\n' not in buffer:
        remaining=deadline-time.monotonic()
        if remaining<=0 or not select.select([fd],[],[],remaining)[0]:
            raise TimeoutError('Absolute stdio frame deadline reached')
        chunk=os.read(fd,min(65536,maximum+1-len(buffer)))
        if not chunk:raise ValueError('EOF before a complete newline frame')
        capture.write(chunk);capture.flush();buffer+=chunk
        if len(buffer)>maximum:raise ValueError('Stdio frame too large')
    line,_,buffer=buffer.partition(b'\n')
    return line,buffer


def stdio_client(process, output, raw_stdout):
    # Deterministic engineering client, not an AI/LLM performance evaluation.
    transcript = (output / 'stdio-transcript-private.jsonl').open('x', encoding='utf-8', newline='\n')
    counter = 0
    pending = b''
    os.set_blocking(process.stdout.fileno(),False)
    responses = []
    def exchange(method, params=None, notification=False, raw=None):
        nonlocal counter,pending
        counter += 1
        request = {'jsonrpc': '2.0', 'method': method}
        if not notification: request['id'] = counter
        if params is not None: request['params'] = params
        payload = raw if raw is not None else json.dumps(request).encode()
        process.stdin.write(payload + b'\n'); process.stdin.flush()
        transcript.write(json.dumps({'direction': 'client', 'request': request if raw is None else 'SYNTHETIC_MALFORMED_JSON'}) + '\n'); transcript.flush()
        if notification: return
        line,pending=read_frame(process.stdout.fileno(),raw_stdout,pending)
        response = json.loads(line)
        if raw is None and response.get('id') != counter: raise ValueError('Response identity differs')
        transcript.write(json.dumps({'direction': 'server', 'response': response}) + '\n'); transcript.flush()
        responses.append(response)
        return response
    try:
        assert exchange('tools/list')['error']['message'] == 'INITIALIZATION_REQUIRED'
        initialized = exchange('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                            'clientInfo': {'name': 'curaloop-frozen-stdio-test-client', 'version': '1.0.0'}})
        assert initialized['result']['protocolVersion'] == '2025-11-25'
        exchange('notifications/initialized', notification=True)
        assert len(exchange('tools/list')['result']['tools']) == 4
        assert exchange('ping')['result'] == {}
        assert exchange('tools/call', {'name': 'evidence_search', 'arguments': {'query': '1259375'}})['result']['isError'] is False
        assert exchange('tools/call', {'name': 'evidence_inspect', 'arguments': {'source_id': 'D1259375'}})['result']['structuredContent']['source']['readouts'][1]['unit']['value'] == 5
        brief = {'report_id': 'readiness-ic50', 'question': 'Inspect the declared IC50 endpoint and unit.',
                 'kind': 'endpoint', 'source_ids': ['D1259375'], 'tid': 2}
        drafted = exchange('tools/call', {'name': 'draft_metadata_plan', 'arguments': brief})['result']['structuredContent']
        digest = drafted['report']['report_sha256']
        params = {'name': 'local_export', 'arguments': {'report_id': 'readiness-ic50', 'report_sha256': digest}}
        first = exchange('tools/call', params)['result']['structuredContent']
        repeated = exchange('tools/call', params)['result']['structuredContent']
        assert first == repeated and first['manifest']['delivered'] is False
        assert exchange('tools/call', {'name': 'evidence_inspect', 'arguments': {'source_id': 'alias_final_reserved'}})['result']['isError'] is True
        malformed = exchange('synthetic', raw=b'{"PRIVATE_STDIO_SENTINEL":1,"PRIVATE_STDIO_SENTINEL":2}')
        assert malformed['error']['message'] == 'PARSE_ERROR' and 'PRIVATE_STDIO_SENTINEL' not in json.dumps(malformed)
        return {'status': 'PASS', 'client': 'FROZEN_DETERMINISTIC_STDIO_ENGINEERING_CLIENT', 'responses': len(responses),
                'tools': 4, 'actual_os_stdio_transport': True, 'report_sha256': digest,
                'duplicate_export_identical': True, 'external_delivery': False, 'live_llm_evaluation': 'NOT_RUN'}
    finally: transcript.close()


def supervise(task_root, bundle, permit_path, mode, python):
    task_root, bundle, permit_path = task_root.resolve(), bundle.resolve(), permit_path.resolve()
    if mode not in ('acceptance', 'stdio', 'stdio-frame-checks') or not bundle.is_relative_to(task_root) or not permit_path.is_relative_to(task_root):
        raise ValueError('Owned paths and approved mode required')
    permit = json.loads(permit_path.read_text())
    if permit['output_partition'] != 'runs/' + permit['attempt'] or permit['stage'] != 'C': raise ValueError('Exact C partition required')
    if datetime.now(timezone.utc) >= datetime.fromisoformat(permit['deadline_utc'].replace('Z', '+00:00')): raise ValueError('Expired permit')
    sys.path.insert(0, str(bundle))
    from research.longrun_v1.worker import verify_bundle
    verify_bundle(bundle, bundle / 'bundle.json', permit['bundle_sha256'])
    output = task_root / permit['output_partition']; output.parent.mkdir(exist_ok=True); output.mkdir(exist_ok=False)
    write(output / 'claimed.json', {'attempt': permit['attempt'], 'token': permit['token'], 'permit_sha256': hashlib.sha256(permit_path.read_bytes()).hexdigest()})
    env = dict(os.environ)
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'): env[name] = '1'
    with (output / 'stdout-private.txt').open('xb') as stdout, (output / 'stderr-private.txt').open('xb') as stderr:
        process = subprocess.Popen([python, '-B', '-m', 'research.portfolio_v1.worker_v2', '--permit', str(permit_path),
                                    '--output', str(output), '--mode', mode], cwd=bundle, env=env,
                                    stdin=subprocess.PIPE if mode == 'stdio' else subprocess.DEVNULL,
                                    stdout=subprocess.PIPE if mode == 'stdio' else stdout, stderr=stderr)
        raw_stat = Path('/proc', str(process.pid), 'stat').read_text()
        identity = {'pid': process.pid, 'birth_id': 'linux-startticks:' + raw_stat.rsplit(')', 1)[1].split()[19], 'token': permit['token']}
        write(output / 'launch.json', identity)
        if mode == 'stdio':
            try: client = stdio_client(process, output, stdout)
            except Exception as error:
                (output / 'client-error-private.txt').write_text(traceback.format_exc())
                client = {'status': 'FAIL', 'error_type': type(error).__name__, 'live_llm_evaluation': 'NOT_RUN'}
            finally: process.stdin.close()
            write(output / 'stdio-client-result.json', client)
        try: code = process.wait(timeout=permit['wall_seconds'] + 30)
        except subprocess.TimeoutExpired: process.kill(); code = process.wait()
        resource = output / 'resources.json'
        if not resource.is_file():
            write(output / 'terminal-missing-resource.json', dict(identity, exit_code=code, observed_exited=True))
            raise RuntimeError('Resource evidence unavailable; lease retained')
        receipt = json.loads(resource.read_text()); receipt['verified_terminal'] = True
        if code != 0: receipt['status'] = 'FAIL'
        raw = (json.dumps(receipt, indent=2, allow_nan=False) + '\n').encode()
        (output / 'terminal-receipt.json').write_bytes(raw)
        write(output / 'terminal-proof.json', dict(identity, observed_exited=True, exit_code=code,
              receipt_sha256=hashlib.sha256(raw).hexdigest(), observation='SUPERVISOR_WAIT_ON_ORIGINAL_CHILD_HANDLE'))
    return {'attempt': permit['attempt'], 'exit_code': code, 'pid': process.pid, 'birth_id': identity['birth_id']}
