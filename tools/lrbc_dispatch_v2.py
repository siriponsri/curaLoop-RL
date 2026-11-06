"""Bounded second-stage preparation/dispatch. Parent is the only ledger writer."""

import argparse
import ast
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.lrbc_admin_v3 import PRIVATE, PUBLIC, REMOTE, HOST, OPTIONS, ssh, write
from research.longrun_v1.coordinator_v2 import Coordinator

A2 = ROOT / '.local/goal4r2a2-20261106-v1/remote-return/full-v1/files'
A3 = ROOT / '.local/goal4r2a3-20261106-v1/remote-return/full-v1/files'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_pin(source, target, expected=None):
    if source.is_symlink() or (expected and sha(source) != expected):
        raise ValueError('Source pin or canonical path differs')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as handle:
        handle.write(source.read_bytes())



def source_citation(sid, kind):
    if kind in ('description', 'request'):
        suffix = sid[1:].replace('_', '-').lower()
        path = A2 / 'runs/metadata-acquire-v1' / ('request-' + suffix + '.json')
        receipt = json.loads(path.read_text())
        request = receipt['request']
        aid = suffix.split('-')[0]
        return {'url': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/' + aid + '/description/JSON',
                'params': request.get('params', {}), 'receipt_sha256': sha(path)}
    if kind == 'uniprot':
        path = A3 / 'runs/xref-metadata-v1/xref-014-receipt.json'
        receipt = json.loads(path.read_text())
        return {'url': 'https://rest.uniprot.org/uniprotkb/search', 'params': receipt['request']['params'],
                'receipt_sha256': sha(path)}
    if kind == 'policy':
        path = A3 / 'private-inputs/source-evidence-manifest-v1.json'
        record = json.loads(path.read_text())['files'][70]
        assert record['url'] == 'https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/data-submission-policy.md'
        return {'url': record['url'], 'params': {}, 'receipt_sha256': sha(path)}
    path = A3 / 'private-inputs/source-evidence-manifest-v1.json'
    return {'url': 'urn:sha256:' + sha(path), 'params': {}, 'retained_file': 'source-evidence-manifest-v1.json'}


def source_allocation():
    destination = PRIVATE / 'r1-source-allocation.json'
    if destination.exists():
        return json.loads(destination.read_text())
    old = A3 / 'network-ledger.json'
    expected = 'dee45c033a03d4e7d800f5403f2b8ea6bfe11eb4b380aa0f0a86f5b821eab906'
    if sha(old) != expected:
        raise ValueError('Historical stopped ledger differs')
    ledger = json.loads(old.read_text())
    assert 'pubchem' in ledger['stopped_services']
    assert sum(r['service'] == 'pubchem' for r in ledger['requests']) == 24
    assert sum(r['charged_decoded_bytes'] for r in ledger['requests']) == 28715980
    manifest = A3 / 'runs/observation-canary-v1/qualification-manifest-private.json'
    assert sha(manifest) == 'afca38be68334b60c2657099f316e839acb4a06c41264eedd68fe021c8ae7146'
    value = {'status': 'HELD_FOR_REVIEWED_R1_NOT_TRAFFIC_RELEASE', 'historical_pug_calls': 24,
             'new_reserved_calls': 20, 'cumulative_reserved_pug_calls': 44, 'pug_call_ceiling': 96,
             'historical_uniprot_calls': 27, 'historical_decoded_bytes': 28715980,
             'new_reserved_decoded_bytes': 20971520, 'cumulative_decoded_byte_ceiling': 268435456,
             'per_response_decoded_ceiling': 1048576, 'inner_transport_threshold': 983040,
             'inner_threshold_guard_band_bytes': 65536, 'old_stop_preserved': True,
             'old_ledger_sha256': expected, 'original_manifest_sha256': sha(manifest),
             'new_phase_maximum_attempts_per_specification': 1, 'new_source_phase': 'LRBC_R1_NATIVE_ENVELOPE_V1',
             'paid_services_or_gpu': False}
    write(destination, value)
    write(PUBLIC / 'r1-source-allocation-v1.json', value)
    return value


def prepare(name, kind):
    if not name.replace('-', '').isalnum() or kind not in ('workflow', 'qualification', 'qualification-full'):
        raise ValueError('Safe versioned bundle name and approved kind required')
    bundle = PRIVATE / 'bundles' / name
    bundle.mkdir(parents=True, exist_ok=False)
    source_paths = ['research/__init__.py', 'research/configs/lrbc_execution_v1.json',
                    'research/configs/lrbc_r0_cases_v1.json', 'tools/lrbc_supervise_v2.py',
                    'research/qualification_v1/__init__.py', 'research/qualification_v1/contracts.py',
                    'research/qualification_v1/transport.py', 'research/readiness_v1/__init__.py',
                    'research/readiness_v1/contracts.py']
    modules = ['__init__', 'coordinator', 'coordinator_v2', 'guard', 'worker', 'worker_v2', 'fixtures', 'presence']
    modules += ['workflow_eval', 'reference_support'] if kind == 'workflow' else ['qualification']
    source_paths += ['research/longrun_v1/' + module + '.py' for module in modules]
    if kind == 'workflow':
        source_paths += ['research/configs/lrbc_workflow_cases_v1.json', 'research/configs/lrbc_workflow_references_v1.json']
        source_paths += ['src/curaloop_rd/' + module + '.py' for module in
                         ('__init__', 'contracts_v2', 'catalogue_v2', 'decision_v2', 'workflow_v2')]
    else:
        source_paths += ['research/configs/lrbc_r1_cases_v1.json']
    for rel in sorted(source_paths):
        if rel.endswith('.py'):
            ast.parse((ROOT / rel).read_text(encoding='utf-8'))
        copy_pin(ROOT / rel, bundle / rel)
    (bundle / 'inputs').mkdir()
    if kind == 'workflow':
        config = json.loads((ROOT / 'research/configs/lrbc_workflow_cases_v1.json').read_text())
        registry = {}
        for sid, (alias, relative, expected) in config['sources'].items():
            if sid == 'NCBI_SCHEMA':
                continue  # The current intents report declared enums without conversion.
            target = 'inputs/workflow/' + sid + '.txt'
            copy_pin((A2 if alias == 'A2' else A3) / relative, bundle / target, expected)
            kind_name = ('description' if sid.startswith('D') else 'request' if sid.startswith('R') else
                         'uniprot' if sid == 'UNIPROT014' else 'policy' if sid == 'NLM_POLICY' else 'attempts')
            citation = source_citation(sid, kind_name)
            registry[sid] = {'path': target, 'sha256': expected, 'role': 'METADATA_ONLY_DEVELOPMENT_EXPOSED',
                             'kind': kind_name, 'citation': citation}
        write(bundle / 'inputs/workflow-registry.json', registry)
    else:
        allocation = source_allocation()
        write(bundle / 'inputs/r1-allocation.json', allocation)
        manifest = A3 / 'runs/observation-canary-v1/qualification-manifest-private.json'
        assert sha(manifest) == allocation['original_manifest_sha256']
        original = json.loads(manifest.read_text())
        requests = {'full': original['requests'], 'canary': []}
        for row in original['requests']:
            small = dict(row, sids=row['sids'][:16])
            small['specification'] = {'path': row['specification']['path'], 'params': {'sid': ','.join(small['sids'])}}
            requests['canary'].append(small)
        write(bundle / 'inputs/r1-requests.json', requests)
        copy_pin(A3 / 'private-inputs/private-tools/pubchem_rest_request.py', bundle / 'inputs/pubchem_rest_request.py',
                 '78ddae6460e3dd701cda67df4454532899d20851f8212a74ec8d5b6e2988b690')
        if kind == 'qualification-full':
            passed = PUBLIC / 'r1-canary-v1-result.json'
            result = json.loads(passed.read_text())
            assert result['status'] == 'PASS_SOURCE_CANARY_ONLY'
            assert result['request_plan_sha256'] == sha(bundle / 'inputs/r1-requests.json')
            copy_pin(passed, bundle / 'inputs/r1-canary-result.json')
    rows = []
    for p in sorted(bundle.rglob('*')):
        if p.is_file():
            rows.append({'path': p.relative_to(bundle).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)})
    write(bundle / 'bundle.json', {'schema': 'curaloop.lrbc.bundle.v1', 'files': rows})
    archive = PRIVATE / (name + '.zip')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(bundle.rglob('*')):
            if p.is_file(): z.write(p, p.relative_to(bundle).as_posix())
    meta = {'bundle': name, 'kind': kind, 'bundle_sha256': sha(bundle / 'bundle.json'), 'archive_sha256': sha(archive),
            'files': len(rows), 'bytes': sum(r['bytes'] for r in rows),
            'source_files': [r for r in rows if not r['path'].startswith('inputs/')]}
    write(PUBLIC / ('bundle-' + name + '.json'), meta)
    print(json.dumps({'status': 'PREPARED_NOT_EXECUTED', 'bundle': name, 'bundle_sha256': meta['bundle_sha256']}))


def upload(name):
    meta = json.loads((PUBLIC / ('bundle-' + name + '.json')).read_text())
    result = subprocess.run(['scp', *OPTIONS, str(PRIVATE / (name + '.zip')), HOST + ':' + REMOTE + '/' + name + '.zip'],
                            capture_output=True, timeout=60)
    if result.returncode:
        (PRIVATE / (name + '-transport-error-private.txt')).write_bytes(result.stderr)
        raise RuntimeError('Private bundle transport failed')
    code = '''
import os,json,hashlib,zipfile
from pathlib import Path,PurePosixPath
root=Path(__ROOT_PATH__);assert root.resolve()==root and root.stat().st_uid==os.getuid()
archive=root/(__BUNDLE_NAME__+'.zip');assert hashlib.sha256(archive.read_bytes()).hexdigest()==__ARCHIVE_SHA__
bundle=root/'bundles'/__BUNDLE_NAME__;bundle.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist())) and len(z.namelist())<=100
 for info in z.infolist():
  name=PurePosixPath(info.filename)
  assert not name.is_absolute() and '..' not in name.parts and chr(92) not in info.filename
  assert not info.is_dir() and info.file_size<=16*1024**2 and ((info.external_attr>>16)&0o170000) in (0,0o100000)
  path=bundle/info.filename;path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb') as h:h.write(z.read(info))
print(json.dumps({'status':'PASS_TRANSPORT','bundle':__BUNDLE_NAME__,'files':len(z.namelist())}))
'''.replace('__ROOT_PATH__', repr(REMOTE)).replace('__BUNDLE_NAME__', repr(name)).replace('__ARCHIVE_SHA__', repr(meta['archive_sha256']))
    report = ssh(code)
    write(PUBLIC / (name + '-transport.json'), report)
    print(json.dumps(report))


def release():
    fixture = json.loads((PUBLIC / 'r1-fixtures-v1-result.json').read_text())
    review = PUBLIC / 'r1-release-review-v1.json'
    assert fixture['status'] == 'PASS' and json.loads(review.read_text())['status'] == 'GO_UNCHANGED_COHORT_R1_ONLY'
    value = Coordinator(PRIVATE / 'coordinator.sqlite').release_r1(sha(review), sha(PRIVATE / 'r1-source-allocation.json'))
    write(PUBLIC / 'r1-release-v1.json', value)
    print(json.dumps(value))


def run(name, attempt, mode):
    meta = json.loads((PUBLIC / ('bundle-' + name + '.json')).read_text())
    assert json.loads((PUBLIC / (name + '-transport.json')).read_text())['status'] == 'PASS_TRANSPORT'
    db = Coordinator(PRIVATE / 'coordinator.sqlite')
    stage = 'R1' if mode in ('q-canary', 'q-full') else 'R0'
    if stage == 'R1':
        release_record = json.loads((PUBLIC / 'r1-release-v1.json').read_text())
        assert release_record['source_allocation_sha256'] == sha(PRIVATE / 'r1-source-allocation.json')
        if mode == 'q-full':
            assert json.loads((PUBLIC / 'r1-canary-v1-result.json').read_text())['status'] == 'PASS_SOURCE_CANARY_ONLY'
        # At-most-once SOURCE PHASE claim, independent of attempt names.
        write(PRIVATE / (mode + '-source-claim.json'), {'attempt': attempt, 'bundle': name, 'release': release_record})
    available = ssh("from pathlib import Path;import json;print(json.dumps({'bytes':next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))}))")['bytes']
    permit = db.reserve(attempt, stage, 'dr-train', meta['bundle_sha256'], available)
    write(PRIVATE / 'permits' / (attempt + '.json'), permit)
    try:
        code = '''
import os,json,sys
from pathlib import Path
root=Path(__ROOT_PATH__);assert root.resolve()==root and root.stat().st_uid==os.getuid()
p=root/'permits'/__PERMIT_NAME__
with p.open('x') as h:json.dump(__PERMIT_BODY__,h);h.flush();os.fsync(h.fileno())
sys.dont_write_bytecode=True;sys.path.insert(0,str(root/'bundles'/__BUNDLE_NAME__))
from tools.lrbc_supervise_v2 import supervise
print(json.dumps(supervise(root,root/'bundles'/__BUNDLE_NAME__,p,__MODE__,sys.executable)))
'''.replace('__ROOT_PATH__', repr(REMOTE)).replace('__PERMIT_NAME__', repr(attempt + '.json')).replace(
            '__PERMIT_BODY__', repr(permit)).replace('__BUNDLE_NAME__', repr(name)).replace('__MODE__', repr(mode))
        result = ssh(code, timeout=1860)
        folder = PRIVATE / 'remote-immediate' / attempt
        folder.mkdir(parents=True, exist_ok=False)
        fetched = ssh('''
import base64,json
from pathlib import Path
p=Path(__ROOT_PATH__)/'runs'/__ATTEMPT__
print(json.dumps({n:base64.b64encode((p/n).read_bytes()).decode() for n in
 ['launch.json','terminal-receipt.json','terminal-proof.json','result.json','failure.json'] if (p/n).is_file()}))
'''.replace('__ROOT_PATH__', repr(REMOTE)).replace('__ATTEMPT__', repr(attempt)))
        for name_, encoded in fetched.items():
            (folder / name_).write_bytes(base64.b64decode(encoded, validate=True))
        launch = json.loads((folder / 'launch.json').read_text())
        db.mark_launch(permit, launch['pid'], launch['birth_id'])
        raw = (folder / 'terminal-receipt.json').read_bytes()
        db.finish(permit, raw, json.loads((folder / 'terminal-proof.json').read_text()))
        resource = json.loads(raw)
        safe = {'attempt': attempt, 'stage': stage, 'mode': mode, 'host': 'dr-train', 'status': resource['status'],
                'cpu_id': permit['cpu'], 'worker_cpu_seconds': resource['cpu_seconds'],
                'retained_reservation_seconds': permit['reserved_cpu_seconds'],
                'terminal_receipt_sha256': hashlib.sha256(raw).hexdigest(), 'private_streams': 'NOT_INCLUDED'}
        write(PUBLIC / (attempt + '-process.json'), safe)
        if (folder / 'result.json').exists():
            write(PUBLIC / (attempt + '-result.json'), json.loads((folder / 'result.json').read_text()))
        print(json.dumps(safe))
    except BaseException:
        from research.longrun_v1.coordinator import AdmissionError
        try: db.mark_unknown(permit)
        except AdmissionError: pass
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['prepare', 'upload', 'run', 'release-r1'])
    p.add_argument('--bundle')
    p.add_argument('--kind', choices=['workflow', 'qualification', 'qualification-full'])
    p.add_argument('--attempt')
    p.add_argument('--mode', choices=['workflow', 'q-fixtures', 'q-canary', 'q-full'])
    args = p.parse_args()
    if args.action == 'prepare': prepare(args.bundle, args.kind)
    elif args.action == 'upload': upload(args.bundle)
    elif args.action == 'run': run(args.bundle, args.attempt, args.mode)
    else: release()


if __name__ == '__main__':
    main()
