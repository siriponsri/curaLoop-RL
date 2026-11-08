"""Resume only the authenticated M2 export archive over a binary SSH stream."""
import base64
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'.local/m2-selective-compute-20261108-v1'
EXPORT='/home/chaw/curaloop-tasks/m2-selective-compute-20261108-v1-export-v1'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def command(code):
    profile=json.loads((LOCAL/'existing-ssh-profile.json').read_text())['selected_profile']
    encoded=base64.b64encode(code.encode()).decode()
    return ['rtk','proxy','ssh','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',
        profile,"python3 -B -c 'exec(__import__(\"base64\").b64decode(\""+encoded+"\"))'"]


def save(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')


def probe():
    r=subprocess.run(command("import resource,sys;resource.setrlimit(resource.RLIMIT_CPU,(5,5));sys.stdout.buffer.write(b'M2-TRANSPORT-PROBE')"),capture_output=True,timeout=30)
    result={'exit_code':r.returncode,'binary_passthrough':r.stdout==b'M2-TRANSPORT-PROBE',
            'stdout_bytes':len(r.stdout),'stderr':r.stderr.decode(errors='replace')}
    save(LOCAL/'binary-passthrough-probe.json',result)
    print(json.dumps(result));assert r.returncode==0 and result['binary_passthrough']


def resume():
    assert json.loads((LOCAL/'binary-passthrough-probe.json').read_text())['binary_passthrough']
    target=LOCAL/'remote-return/export';archive=target/'full-task-v1.tar.gz'
    assert archive.is_file() and archive.resolve().is_relative_to(LOCAL.resolve())
    # Caller stops the exact owned first transfer before this action.
    original=json.loads((LOCAL/'remote-return/transport-receipt.json').read_text())
    assert original['exit_code'] != 0
    partials=LOCAL/'transport-partials';partials.mkdir(exist_ok=False)
    old=partials/'failed-scp-v1.tar.gz.partial'
    shutil.copyfile(archive,old)
    offset=archive.stat().st_size
    assert old.stat().st_size==offset and sha(old)==sha(archive)
    receipt={'first_transfer':original,'partial_bytes':offset,'partial_sha256':sha(old)}
    code="""import base64,hashlib,json,os,resource,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(30,30));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(60)
os.sched_setaffinity(0,{69})
p=Path(__EXPORT__);assert p.resolve()==p and not p.is_symlink()
names={'full-task-v1.tar.gz','manifest.json','permit.json','kernel-proof.json','resource.json','result.json','terminal.json'}
assert {f.name for f in p.iterdir()}==names
out={}
for name in sorted(names-{'full-task-v1.tar.gz'}):
 f=p/name;assert f.is_file() and not f.is_symlink() and f.stat().st_size<4*1024**2
 out[name]=base64.b64encode(f.read_bytes()).decode()
print(json.dumps(out))
""".replace('__EXPORT__',repr(EXPORT))
    r=subprocess.run(command(code),capture_output=True,timeout=90)
    assert r.returncode==0,r.stderr.decode(errors='replace')[-500:]
    small=json.loads(r.stdout)
    for name,encoded in small.items():
        assert name in ('manifest.json','permit.json','kernel-proof.json','resource.json','result.json','terminal.json')
        data=base64.b64decode(encoded);path=target/name
        if path.exists():assert path.read_bytes()==data
        else:
            with path.open('xb') as f:f.write(data)
    manifest=json.loads((target/'manifest.json').read_text())
    trusted=json.loads((LOCAL/'jobs/return-export-v1/result.json').read_text())
    assert sha(target/'manifest.json')==trusted['manifest_sha256']
    expected=manifest['archive_bytes'];pin=manifest['archive_sha256']
    assert 0<offset<expected and expected<512*1024**2
    code="""import hashlib,os,resource,signal,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(90,90));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(1800)
os.sched_setaffinity(0,{69});os.nice(19)
path=Path(__ARCHIVE__);assert path.resolve()==path and not path.is_symlink() and path.stat().st_size==__SIZE__
with path.open('rb') as f:
 f.seek(__OFFSET__)
 for block in iter(lambda:f.read(1048576),b''):sys.stdout.buffer.write(block)
sys.stdout.buffer.flush()
""".replace('__ARCHIVE__',repr(EXPORT+'/full-task-v1.tar.gz')).replace('__SIZE__',str(expected)).replace('__OFFSET__',str(offset))
    with archive.open('ab') as out:
        r=subprocess.run(command(code),stdout=out,stderr=subprocess.PIPE,timeout=1830)
    receipt.update(exit_code=r.returncode,stderr=r.stderr.decode(errors='replace'),
        final_bytes=archive.stat().st_size,expected_bytes=expected,
        final_sha256=sha(archive),expected_sha256=pin,transport='resumed binary SSH stream')
    save(LOCAL/'remote-return/transport-resume-v1.json',receipt)
    assert r.returncode==0 and archive.stat().st_size==expected and sha(archive)==pin
    print(json.dumps({'status':'PASS_RESUMED_TRANSPORT_PENDING_FULL_REREAD','bytes':expected,'resumed_at':offset}))


if __name__=='__main__':
    assert sys.argv[1] in ('probe','resume')
    globals()[sys.argv[1]]()
