"""Frozen L01-L12 synthetic checks. No HTTP, scientific rows or child workers."""

import copy
import hashlib
import json
import os
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .coordinator import Coordinator, AdmissionError
from .presence import project


def rejected(call):
    try:
        call()
    except (AdmissionError, ValueError, sqlite3.IntegrityError):
        return
    raise AssertionError('Expected fail-closed rejection')


def run(root, output, contract):
    cases = []
    serial = 0
    def fresh(cfg=None):
        nonlocal serial
        serial += 1
        return Coordinator.initialize(output / ('fixture-' + str(serial) + '.sqlite'), cfg or contract,
                                      {'local': [0], 'dr-train': [10, 11, 12, 13]})
    def reserve(db, attempt, host='dr-train', **kwargs):
        return db.reserve(attempt, 'R0', host, 'a' * 64, 64 * 1024**3,
                          now='2026-11-06T10:00:00Z', **kwargs)
    def finish(db, permit, status='PASS'):
        db.mark_launch(permit, 42, 'synthetic-birth')
        receipt = dict(attempt=permit['attempt'], token=permit['token'], host=permit['host'], pid=42,
                       cpu_affinity=[permit['cpu']], actual_cpu_affinity=[permit['cpu']],
                       bundle_sha256=permit['bundle_sha256'], status=status, cpu_seconds=.01,
                       verified_terminal=True)
        raw = json.dumps(receipt).encode()
        proof = dict(observed_exited=True, pid=42, birth_id='synthetic-birth',
                     receipt_sha256=hashlib.sha256(raw).hexdigest(), exit_code=0 if status == 'PASS' else 1)
        db.finish(permit, raw, proof)
        return receipt, proof

    db = fresh()
    for i in range(14):
        finish(db, reserve(db, 'charge-' + str(i)))
    before = db.snapshot()
    rejected(lambda: reserve(db, 'fifteenth'))
    assert before == db.snapshot() and before['historical_cpu_seconds'] == 19800
    assert before['retained_job_reservations_seconds'] + before['utility_reserve_seconds'] == 14400
    cases.append('L01')

    db = fresh()
    barrier = threading.Barrier(8)
    def concurrent(i):
        barrier.wait()
        try:
            return reserve(db, 'race-' + str(i), host='local' if i < 3 else 'dr-train')
        except AdmissionError:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        admitted = [p for p in pool.map(concurrent, range(8)) if p]
    assert len(admitted) == 4 and sum(p['host'] == 'local' for p in admitted) <= 1
    assert len({(p['host'], p['cpu']) for p in admitted}) == len(admitted)
    cases.append('L02')
    rejected(lambda: reserve(db, admitted[0]['attempt']))
    assert len(db.snapshot()['jobs']) == 4
    cases.append('L03')

    db = fresh(); permit = reserve(db, 'unknown')
    db.mark_launch(permit, 42, 'original-birth'); db.mark_unknown(permit)
    restarted = Coordinator(db.path)
    assert restarted.snapshot()['jobs'][0]['state'] == 'UNKNOWN'
    assert restarted.snapshot()['retained_job_reservations_seconds'] == 900
    rejected(lambda: reserve(restarted, 'unknown'))
    bad = dict(permit, cpu=99)
    rejected(lambda: restarted.mark_unknown(bad))
    cases.append('L04')
    receipt = dict(attempt=permit['attempt'], token=permit['token'], host=permit['host'], pid=42,
                   cpu_affinity=[permit['cpu']], actual_cpu_affinity=[permit['cpu']], bundle_sha256=permit['bundle_sha256'],
                   status='PASS', cpu_seconds=.01, verified_terminal=True)
    raw = json.dumps(receipt).encode()
    proof = dict(observed_exited=True, pid=42, birth_id='wrong-birth', receipt_sha256=hashlib.sha256(raw).hexdigest(), exit_code=0)
    rejected(lambda: restarted.finish(permit, raw, proof))
    for changes in ({'host': 'local'}, {'cpu_affinity': [99]}, {'bundle_sha256': 'c' * 64},
                    {'cpu_seconds': float('nan')}, {'cpu_seconds': 901}, {'verified_terminal': False}, {'pid': 99}):
        changed = json.dumps(dict(receipt, **changes)).encode()
        rejected(lambda changed=changed: restarted.finish(permit, changed,
                 dict(proof, birth_id='original-birth', receipt_sha256=hashlib.sha256(changed).hexdigest())))
    rejected(lambda: restarted.finish(permit, raw, dict(proof, birth_id='original-birth', exit_code=1)))
    restarted.finish(permit, raw, dict(proof, birth_id='original-birth'))
    rejected(lambda: restarted.finish(permit, raw, dict(proof, birth_id='original-birth')))
    db2 = fresh(); unlaunched = reserve(db2, 'unknown-before-launch'); db2.mark_unknown(unlaunched)
    rejected(lambda: db2.finish(unlaunched, raw, proof))
    cases.append('L05')

    db = fresh()
    rejected(lambda: db.reserve('expired', 'R0', 'local', 'a' * 64, 16 * 1024**3, now=contract['r0_deadline_utc']))
    rejected(lambda: db.reserve('locked-c', 'C', 'dr-train', 'a' * 64, 16 * 1024**3,
                               now='2026-11-06T10:00:00Z'))
    cases.append('L06')
    rejected(lambda: db.reserve('low-ram', 'R0', 'local', 'a' * 64, 1024**3,
                               now='2026-11-06T10:00:00Z'))
    permit = reserve(db, 'local-tier', host='local')
    assert permit['memory_bytes'] == 512 * 1024**2 and permit['child_processes_allowed'] is False
    rejected(lambda: reserve(db, 'second-local', host='local'))
    cases.append('L07')

    cfg = copy.deepcopy(contract)
    cfg['approved_requests'] = {'stopped': {'service': 'pubchem', 'metadata_only': False},
                                'metadata': {'service': 'ncbi_metadata', 'metadata_only': True},
                                'last-uniprot': {'service': 'uniprot', 'metadata_only': True}}
    db = fresh(cfg)
    rejected(lambda: db.reserve_request('pubchem', 'stopped', 100))
    rejected(lambda: db.reserve_request('ncbi_metadata', 'metadata', 100, metadata_only=False))
    rejected(lambda: db.reserve_request('uniprot', 'unlisted', 100, metadata_only=True))
    db.reserve_request('ncbi_metadata', 'metadata', 100, metadata_only=True)
    rejected(lambda: db.reserve_request('ncbi_metadata', 'metadata', 100, metadata_only=True))
    assert db.snapshot()['stopped_services'] == ['pubchem']
    cases.append('L08')

    # Actual source verifier is the same function used by the worker.
    from .worker import verify_bundle, public_failure
    verify_bundle(root, root / 'bundle.json', hashlib.sha256((root / 'bundle.json').read_bytes()).hexdigest())
    rejected(lambda: verify_bundle(root, root / 'bundle.json', '0' * 64))
    rejected(lambda: reserve(fresh(), '../unsafe'))
    cases.append('L09')
    sentinel = 'PRIVATE_RESPONSE_SECRET_7a4f'
    assert sentinel not in json.dumps(public_failure(ValueError(sentinel)))
    cases.append('L10')

    binding = dict(name='Synthetic', tid=1, type=1, unit_present=True, unit=5, sunit_present=False, sunit=None)
    request = dict(aid='1', version=1, revision=1, sids=['10', '11'], bindings=[binding])
    native = {'PC_AssaySubmit': {'assay': {'descr': {'aid': {'id': 1, 'version': 1}, 'revision': 1,
               'results': [dict(tid=1, name='Synthetic', type=1, unit=5)]}},
               'data': [dict(sid=10, data=[dict(tid=1, value=sentinel)]), dict(sid=11, data=[])]}}
    projected = project(json.dumps(native).encode(), request)
    assert projected['rows_with_all_selected_tids'] == 1 and sentinel not in json.dumps(projected)
    poison = copy.deepcopy(native)
    poison['PC_AssaySubmit']['data'][1] = dict(sid=99, data='UNTOUCHABLE')
    rejected(lambda: project(json.dumps(poison).encode(), request))
    rejected(lambda: project(json.dumps(native).encode(), dict(request, bindings=[])))
    rejected(lambda: project(b'{"duplicate":1,"duplicate":2}', request))
    rejected(lambda: project(b'{"nonfinite":NaN}', request))
    for key in ('version', 'id'):
        malformed = copy.deepcopy(native)
        malformed['PC_AssaySubmit']['assay']['descr']['aid'][key] = True
        rejected(lambda malformed=malformed: project(json.dumps(malformed).encode(), request))
    malformed = copy.deepcopy(native)
    malformed['PC_AssaySubmit']['data'][0]['data'][0]['tid'] = 999
    rejected(lambda: project(json.dumps(malformed).encode(), request))
    cases.append('L11')
    assert json.loads(json.dumps(projected, sort_keys=True)) == projected
    cases.append('L12')
    frozen = json.loads((root / 'research/configs/lrbc_r0_cases_v1.json').read_text())
    assert cases == [case['id'] for case in frozen['cases']]
    return {'status': 'PASS', 'case_ids': cases, 'case_count': len(cases),
            'synthetic_engineering_only': True, 'source_requests': 0,
            'partition_signature_sha256': hashlib.sha256(json.dumps(projected, sort_keys=True).encode()).hexdigest()}
