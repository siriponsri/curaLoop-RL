"""Parent-only LR-BC preparation and dispatch; never accepts arbitrary commands."""

import argparse
import ast
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/lrbc-20261106-v1'
PUBLIC = ROOT / 'docs/evidence/lrbc-20261106-v1'
REMOTE = '/home/chaw/curaloop-rl/lrbc-20261106-v1'
HOST = '100.77.149.83'
OPTIONS = ['-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'IdentitiesOnly=yes',
           '-o', 'ConnectTimeout=10', '-o', 'ConnectionAttempts=1']
sys.path.insert(0, str(ROOT))
from research.longrun_v1.coordinator import Coordinator


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())


def ssh(source, timeout=60):
    result = subprocess.run(['ssh', *OPTIONS, HOST, 'python3 -B -'], input=source.encode(),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        name = 'ssh-failure-' + datetime.now(timezone.utc).strftime('%H%M%S%f') + '.txt'
        (PRIVATE / name).write_bytes(result.stdout + b'\n' + result.stderr)
        raise RuntimeError('SSH operation failed; private error retained: ' + name)
    return json.loads(result.stdout)


def local_capacity():
    class Memory(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in ('total', 'available', 'page_total', 'page_available',
                                                  'virtual_total', 'virtual_available', 'extended')]
    mem = Memory(); mem.length = ctypes.sizeof(mem)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
        raise ctypes.WinError()
    mask, system = ctypes.c_size_t(), ctypes.c_size_t()
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = ctypes.c_void_p
    k.GetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
    if not k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(mask), ctypes.byref(system)):
        raise ctypes.WinError()
    return {'available_memory_bytes': mem.available, 'allowed_cpus': [i for i in range(mask.value.bit_length())
                                                                    if mask.value & (1 << i)],
            'disk_free_bytes': shutil.disk_usage(ROOT).free}


def preflight():
    remote = ssh("""
import os,json,shutil,time
from pathlib import Path
root=Path(REMOTE)
assert root.parent.resolve()==Path('/home/chaw/curaloop-rl') and root.parent.stat().st_uid==os.getuid()
assert not root.is_symlink()
memory={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.split(':')[0] in ('MemAvailable','MemTotal')}
jobs=[]
for e in Path('/proc').iterdir():
 if not e.name.isdigit():continue
 try:
  c=(e/'cmdline').read_bytes().split(b'\\x00')
  if c and any(b'curaloop' in v.lower() for v in c): jobs.append({'pid':int(e.name),'current_task':any(REMOTE.encode() in v for v in c)})
 except (OSError,ValueError):pass
print(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'uid':os.getuid(),'allowed_cpus':sorted(os.sched_getaffinity(0)),
 'available_memory_bytes':memory['MemAvailable'],'disk_free_bytes':shutil.disk_usage(root.parent).free,'load_average':os.getloadavg(),
 'root_exists':root.exists(),'project_jobs_sanitized':jobs}))
""".replace('REMOTE', repr(REMOTE)))
    report = {'status': 'PASS_READ_ONLY', 'local': local_capacity(), 'dr-train': remote}
    write(PUBLIC / 'preflight-v1.json', report)
    print(json.dumps(report))


def prepare():
    bundle = PRIVATE / 'bundles/r0-v2'
    bundle.mkdir(parents=True, exist_ok=False)
    paths = ['research/__init__.py', 'research/configs/lrbc_execution_v1.json',
             'research/configs/lrbc_r0_cases_v1.json', 'tools/lrbc_supervise_v1.py',
             'research/qualification_v1/__init__.py', 'research/qualification_v1/contracts.py',
             'research/readiness_v1/__init__.py', 'research/readiness_v1/contracts.py']
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'research/longrun_v1').glob('*.py')]
    for rel in sorted(paths):
        source = ROOT / rel
        if source.suffix == '.py':
            ast.parse(source.read_text(encoding='utf-8'))
        target = bundle / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    a3 = ROOT / '.local/goal4r2a3-20261106-v1/remote-return/full-v1/files/runs/observation-canary-v1'
    pins = {'observation-000.txt': 'bb77fb872d6b8159e433c02e7b526e10f1056e25bb052894d8653db9dddb9596',
            'phase-request-manifest-private.json': 'b337bbb03d42b0015459dd551edd4aadd7305bdbfbae32bdd89fddfb53b9e83d',
            'qualification-manifest-private.json': 'afca38be68334b60c2657099f316e839acb4a06c41264eedd68fe021c8ae7146',
            'observation-000-receipt.json': 'a97986604a7fcec76ec04973e1f14803cd159fab74ec45c3697f81087892cd4b'}
    (bundle / 'inputs').mkdir()
    for name, expected in pins.items():
        raw = (a3 / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Retained source pin differs')
    phase = json.loads((a3 / 'phase-request-manifest-private.json').read_text())
    original = json.loads((a3 / 'qualification-manifest-private.json').read_text())
    request = phase['requests'][0]
    fixed = [r for r in original['requests'] if r['aid'] == request['aid']]
    assert len(fixed) == 1 and request['sids'] == fixed[0]['sids'][:16]
    assert all(request[k] == fixed[0][k] for k in ('aid', 'bindings', 'version', 'revision', 'stage', 'script'))
    assert phase['qualification_manifest_sha256'] == pins['qualification-manifest-private.json']
    receipt = json.loads((a3 / 'observation-000-receipt.json').read_text())
    assert receipt['response_sha256'] == pins['observation-000.txt']
    assert receipt['request']['params'] == request['specification']['params']
    write(bundle / 'inputs/presence-request.json', request)
    shutil.copyfile(a3 / 'observation-000.txt', bundle / 'inputs/native-submit.json')
    write(bundle / 'inputs/provenance.json', {'original_pins': pins, 'new_activity_requests': 0,
          'role': 'DEVELOPMENT_EXPOSED', 'old_stop_unchanged': True})
    rows = []
    for file in sorted(bundle.rglob('*')):
        if file.is_file():
            raw = file.read_bytes()
            rows.append({'path': file.relative_to(bundle).as_posix(), 'bytes': len(raw),
                         'sha256': hashlib.sha256(raw).hexdigest()})
    write(bundle / 'bundle.json', {'schema': 'curaloop.lrbc.bundle.v1', 'files': rows})
    digest = hashlib.sha256((bundle / 'bundle.json').read_bytes()).hexdigest()
    archive = PRIVATE / 'r0-v2.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(bundle.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(bundle).as_posix())
    write(PUBLIC / 'bundle-r0-v2.json', {'bundle_sha256': digest, 'files': len(rows),
          'bytes': sum(r['bytes'] for r in rows), 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'source_files': [r for r in rows if not r['path'].startswith('inputs/')], 'private_inputs_in_git': False})
    print(json.dumps({'status': 'PREPARED_NOT_EXECUTED', 'bundle_sha256': digest, 'files': len(rows)}))


def create_remote():
    prior = json.loads((PUBLIC / 'preflight-v1.json').read_text())
    assert not prior['dr-train']['root_exists']
    report = ssh("""
import os,json
from pathlib import Path
p=Path(REMOTE);assert p.parent.resolve()==Path('/home/chaw/curaloop-rl') and p.parent.stat().st_uid==os.getuid()
os.umask(0o077);p.mkdir(exist_ok=False);(p/'bundles').mkdir();(p/'permits').mkdir();(p/'runs').mkdir()
print(json.dumps({'status':'PASS_NEW_OWNED_ROOT','root':str(p.resolve()),'uid':os.getuid()}))
""".replace('REMOTE', repr(REMOTE)))
    write(PUBLIC / 'root-created-v1.json', report)
    scp = subprocess.run(['scp', *OPTIONS, str(PRIVATE / 'r0-v2.zip'), HOST + ':' + REMOTE + '/r0-v2.zip'],
                         capture_output=True, timeout=60)
    if scp.returncode:
        (PRIVATE / 'scp-error-private.txt').write_bytes(scp.stderr)
        raise RuntimeError('Private bundle transport failed')
    expected = json.loads((PUBLIC / 'bundle-r0-v2.json').read_text())['archive_sha256']
    report = ssh("""
import os,json,hashlib,zipfile
from pathlib import Path,PurePosixPath
root=Path(REMOTE);assert root.resolve()==root and root.stat().st_uid==os.getuid()
archive=root/'r0-v2.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==EXPECTED
bundle=root/'bundles/r0-v2';bundle.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist())) and len(z.namelist())<100
 for i in z.infolist():
  name=PurePosixPath(i.filename)
  assert not name.is_absolute() and '..' not in name.parts and '\\\\' not in i.filename and not i.is_dir()
  assert i.file_size<16*1024**2 and ((i.external_attr>>16)&0o170000) in (0,0o100000)
  p=bundle/i.filename;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as h:h.write(z.read(i))
print(json.dumps({'status':'PASS_REMOTE_TRANSPORT','archive_sha256':EXPECTED,'files':len(z.namelist())}))
""".replace('REMOTE', repr(REMOTE)).replace('EXPECTED', repr(expected)))
    write(PUBLIC / 'remote-bundle-verified-v1.json', report)
    cfg = json.loads((ROOT / 'research/configs/lrbc_execution_v1.json').read_text())
    cpus = {'local': prior['local']['allowed_cpus'][-1:], 'dr-train': prior['dr-train']['allowed_cpus'][-4:]}
    Coordinator.initialize(PRIVATE / 'coordinator.sqlite', cfg, cpus)
    write(PUBLIC / 'coordinator-created-v1.json', {'status': 'PASS', 'cpu_roster': cpus,
          'single_authority': 'LOCAL_SQLITE_DELETE_JOURNAL', 'historical_charge_seconds': cfg['historical_cpu_seconds']})
    print(json.dumps(report))


def execute_one(attempt, host, mode):
    db = Coordinator(PRIVATE / 'coordinator.sqlite')
    if host == 'local':
        available = local_capacity()['available_memory_bytes']
    else:
        available = ssh("from pathlib import Path;import json;print(json.dumps({'bytes':next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))}))")['bytes']
    digest = json.loads((PUBLIC / 'bundle-r0-v2.json').read_text())['bundle_sha256']
    permit = db.reserve(attempt, 'R0', host, digest, available)
    local_permit = PRIVATE / 'permits' / (attempt + '.json')
    write(local_permit, permit)
    try:
        if host == 'local':
            from tools.lrbc_supervise_v1 import supervise
            result = supervise(PRIVATE, PRIVATE / 'bundles/r0-v2', local_permit, mode,
                               str(ROOT / '.venv/Scripts/python.exe'))
            folder = PRIVATE / 'runs' / attempt
        else:
            source = """
import os,json,sys
from pathlib import Path
root=Path(REMOTE);assert root.resolve()==root and root.stat().st_uid==os.getuid()
p=root/'permits'/PERMITNAME
with p.open('x') as h:json.dump(PERMIT,h);h.flush();os.fsync(h.fileno())
sys.path.insert(0,str(root/'bundles/r0-v2'))
from tools.lrbc_supervise_v1 import supervise
print(json.dumps(supervise(root,root/'bundles/r0-v2',p,MODE,sys.executable)))
""".replace('REMOTE', repr(REMOTE)).replace('PERMITNAME', repr(attempt + '.json')).replace('PERMIT', repr(permit)).replace('MODE', repr(mode))
            result = ssh(source, timeout=1860)
            # Minimal immediate receipts, followed by full-tree return at closeout.
            folder = PRIVATE / 'remote-immediate' / attempt
            folder.mkdir(parents=True, exist_ok=False)
            report = ssh("""
import json,base64
from pathlib import Path
p=Path(REMOTE)/'runs'/ATTEMPT
print(json.dumps({n:base64.b64encode((p/n).read_bytes()).decode() for n in ['launch.json','terminal-receipt.json','terminal-proof.json','result.json','failure.json'] if (p/n).is_file()}))
""".replace('REMOTE', repr(REMOTE)).replace('ATTEMPT', repr(attempt)))
            import base64
            for name, encoded in report.items():
                (folder / name).write_bytes(base64.b64decode(encoded, validate=True))
        launch = json.loads((folder / 'launch.json').read_text())
        db.mark_launch(permit, launch['pid'], launch['birth_id'])
        raw = (folder / 'terminal-receipt.json').read_bytes()
        proof = json.loads((folder / 'terminal-proof.json').read_text())
        db.finish(permit, raw, proof)
        resource = json.loads(raw)
        safe = {'attempt': attempt, 'host': host, 'mode': mode, 'status': resource['status'],
                'cpu_id': permit['cpu'], 'measured_worker_cpu_seconds': resource['cpu_seconds'],
                'retained_reservation_seconds': permit['reserved_cpu_seconds'], 'receipt_sha256': hashlib.sha256(raw).hexdigest(),
                'child_stdout_stderr': 'PRIVATE', 'source_requests': 0}
        write(PUBLIC / (attempt + '-process.json'), safe)
        print(json.dumps(safe), flush=True)
        if (folder / 'result.json').exists():
            write(PUBLIC / (attempt + '-result.json'), json.loads((folder / 'result.json').read_text()))
    except BaseException:
        from research.longrun_v1.coordinator import AdmissionError
        try:
            db.mark_unknown(permit)
        except AdmissionError:
            # A post-completion preservation error cannot undo a terminal state.
            pass
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['preflight', 'prepare', 'create', 'fixtures', 'native', 'presence'])
    args = p.parse_args()
    if args.action == 'preflight': preflight()
    elif args.action == 'prepare': prepare()
    elif args.action == 'create': create_remote()
    elif args.action == 'fixtures':
        # Low local memory pauses local launches; two remote jobs still test
        # distinct real CPU leases and concurrent durable reservations.
        local_ok = local_capacity()['available_memory_bytes'] >= 2 * 1024**3
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(execute_one, 'fixture-local-v1' if local_ok else 'fixture-remote-alt-v1',
                                   'local' if local_ok else 'dr-train', 'fixtures'),
                       pool.submit(execute_one, 'fixture-remote-v1', 'dr-train', 'fixtures')]
            for future in futures: future.result()
    elif args.action == 'native': execute_one('native-local-v1', 'local', 'native')
    elif args.action == 'presence':
        first = 'fixture-local-v1' if (PUBLIC / 'fixture-local-v1-process.json').exists() else 'fixture-remote-alt-v1'
        required = [json.loads((PUBLIC / (n + '-process.json')).read_text())['status'] for n in
                    (first, 'fixture-remote-v1')]
        assert required == ['PASS', 'PASS']
        execute_one('presence-remote-v1', 'dr-train', 'presence')


if __name__ == '__main__':
    main()
