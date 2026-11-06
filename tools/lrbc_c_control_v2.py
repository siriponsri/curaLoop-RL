"""Bounded second-stage preparation/dispatch. Parent is the only ledger writer."""

import argparse
import ast
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from datetime import datetime, timezone
PRIVATE = ROOT / '.local/lrbc-c-20261106-v1'
PUBLIC = ROOT / 'docs/evidence/lrbc-c-20261106-v1'
REMOTE = '/home/chaw/curaloop-rl/lrbc-c-20261106-v1'
HOST = '100.77.149.83'
OPTIONS = ['-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1']
PRIVATE.mkdir(parents=True,exist_ok=True)
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as h:
        json.dump(value,h,indent=2,allow_nan=False);h.write('\n');h.flush();os.fsync(h.fileno())
def ssh(source,timeout=60):
    result=subprocess.run(['ssh',*OPTIONS,HOST,'python3 -B -'],input=source.encode(),capture_output=True,timeout=timeout)
    if result.returncode:
        name='remote-error-'+datetime.now(timezone.utc).strftime('%H%M%S%f')+'.txt'
        (PRIVATE/name).write_bytes(result.stdout+b'\n'+result.stderr)
        raise RuntimeError('C remote failure retained privately: '+name)
    return json.loads(result.stdout)

from research.longrun_v1.coordinator_v2 import Coordinator

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_pin(source, target, expected=None):
    if source.is_symlink() or (expected and sha(source) != expected):
        raise ValueError('Source pin or canonical path differs')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as handle:
        handle.write(source.read_bytes())




def create():
    code="""
import os,json,shutil,time
from pathlib import Path
root=Path(__ROOT_PATH__);parent=root.parent
assert parent.resolve()==Path('/home/chaw/curaloop-rl') and parent.stat().st_uid==os.getuid()
assert not root.exists() and not root.is_symlink()
assert not Path('/home/chaw/curaloop-rl/lrbc-20261106-v1').exists()
memory=next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))
assert memory>16*1024**3 and shutil.disk_usage(parent).free>8*1024**3
cpus=sorted(os.sched_getaffinity(0));assert len(cpus)>=4
os.umask(0o077);root.mkdir();(root/'bundles').mkdir();(root/'permits').mkdir();(root/'runs').mkdir()
print(json.dumps({'status':'PASS_NEW_OWNED_C_ROOT','root':str(root),'allowed_cpus':cpus,'available_memory_bytes':memory,
 'disk_free_bytes':shutil.disk_usage(parent).free,'load_average':os.getloadavg(),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}))
""".replace('__ROOT_PATH__',repr(REMOTE))
    proof=ssh(code);write(PUBLIC/'root-created-v1.json',proof)
    cfg=json.loads((ROOT/'research/configs/lrbc_c_execution_v1.json').read_text())
    db=Coordinator.initialize(PRIVATE/'coordinator.sqlite',cfg,{'local':[11],'dr-train':proof['allowed_cpus'][-4:]})
    release=ROOT/'docs/evidence/lrbc-c-20261106-v1/release-v1.json'
    with db.transaction() as con:con.execute('INSERT INTO gates VALUES(?,?,?)',('C',sha(release),'PASS'))
    write(PUBLIC/'coordinator-created-v1.json',{'status':'PASS_C_SINGLE_AUTHORITY','historical_b_seconds':28800,'c_utility_seconds':1800,
          'c_worker_cap_seconds':171000,'c_increment_cap_seconds':172800,'scientific_source_requests_released':0})
    print(json.dumps(proof))

def prepare(name):
    if not name.replace('-','').isalnum():raise ValueError('Safe versioned bundle name required')
    bundle=PRIVATE/'bundles'/name;bundle.mkdir(parents=True,exist_ok=False)
    source_paths=['research/__init__.py','research/longrun_v1/__init__.py','research/longrun_v1/coordinator.py',
      'research/longrun_v1/guard.py','research/longrun_v1/worker.py','research/portfolio_v1/__init__.py',
      'research/portfolio_v1/worker.py','research/portfolio_v1/worker_v2.py','research/portfolio_v1/checks.py','research/portfolio_v1/stdio_checks_v1.py','tools/lrbc_c_supervise_v2.py',
      'research/configs/lrbc_c_execution_v1.json','research/configs/lrbc_c_cases_v1.json']
    source_paths+=['src/curaloop_rd/'+m+'.py' for m in ['__init__','contracts_v2','catalogue_v2','decision_v2','workflow_v2','portfolio_v1','mcp_v1']]
    for rel in source_paths:
        if rel.endswith('.py'):ast.parse((ROOT/rel).read_text(encoding='utf-8'))
        copy_pin(ROOT/rel,bundle/rel)
    returned=ROOT/'.local/lrbc-20261106-v1/remote-return/full-v1/files'
    proof=json.loads((ROOT/'.local/lrbc-20261106-v1/remote-return-manifest.json').read_text())
    pins={r['path']:r for r in proof['files']}
    for p in (returned/'bundles/workflow-v1/inputs').rglob('*'):
        if p.is_file():
            rel=p.relative_to(returned).as_posix()
            assert sha(p)==pins[rel]['sha256']
            copy_pin(p,bundle/'inputs'/p.relative_to(returned/'bundles/workflow-v1/inputs'))
    rows=[{'path':p.relative_to(bundle).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(bundle.rglob('*')) if p.is_file()]
    write(bundle/'bundle.json',{'schema':'curaloop.lrbc.bundle.v1','files':rows})
    archive=PRIVATE/(name+'.zip')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(bundle.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(bundle).as_posix())
    write(PUBLIC/('bundle-'+name+'.json'),{'bundle':name,'bundle_sha256':sha(bundle/'bundle.json'),'archive_sha256':sha(archive),
      'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'source_files':[r for r in rows if not r['path'].startswith('inputs/')]})
    print(json.dumps({'status':'PREPARED_NOT_EXECUTED','bundle':name,'bundle_sha256':sha(bundle/'bundle.json')}))

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


def run(name, attempt, mode):
    meta = json.loads((PUBLIC / ('bundle-' + name + '.json')).read_text())
    assert json.loads((PUBLIC / (name + '-transport.json')).read_text())['status'] == 'PASS_TRANSPORT'
    db = Coordinator(PRIVATE / 'coordinator.sqlite')
    stage = 'C'
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
from tools.lrbc_c_supervise_v2 import supervise
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
 ['launch.json','terminal-receipt.json','terminal-proof.json','result.json','failure.json','stdio-client-result.json'] if (p/n).is_file()}))
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
        if (folder/'stdio-client-result.json').exists():
            write(PUBLIC/(attempt+'-stdio-client.json'),json.loads((folder/'stdio-client-result.json').read_text()))
        if mode=='stdio':
            client=json.loads((folder/'stdio-client-result.json').read_text())
            passed=resource['status']=='PASS' and client['status']=='PASS'
            write(PUBLIC/(attempt+'-acceptance.json'),{'status':'PASS' if passed else 'FAIL',
                  'worker_process_status':resource['status'],'engineering_client_status':client['status'],
                  'actual_os_stdio_transport':client.get('actual_os_stdio_transport',False),'live_model_evaluation':'NOT_RUN'})
            if not passed:raise RuntimeError('Combined stdio acceptance failed; worker exit proof and client evidence retained separately')
        print(json.dumps(safe))
    except BaseException:
        from research.longrun_v1.coordinator import AdmissionError
        try: db.mark_unknown(permit)
        except AdmissionError: pass
        raise



def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['create','prepare','upload','run','parallel-acceptance'])
    p.add_argument('--bundle');p.add_argument('--attempt');p.add_argument('--mode',choices=['acceptance','stdio','stdio-frame-checks']);args=p.parse_args()
    if args.action=='create':create()
    elif args.action=='prepare':prepare(args.bundle)
    elif args.action=='upload':upload(args.bundle)
    elif args.action=='run':run(args.bundle,args.attempt,args.mode)
    else:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(run,args.bundle,name,'acceptance') for name in ['acceptance-first-v1','acceptance-reproduce-v1']]
            for f in futures:f.result()

if __name__=='__main__':main()
