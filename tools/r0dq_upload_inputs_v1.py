"""Copy authenticated opaque dependency/protection bundle to the owned root."""
import json,subprocess,base64,shlex
from r0dq_core_v1 import ROOT,PRIVATE,REMOTE,HOST,SSH_OPTIONS,save,archive_code
from r0dq_transport_guard_v1 import TransportGuard


def main():
    manifest=json.loads((PRIVATE/'vendor-inputs-manifest-v1.json').read_text())
    target=REMOTE+'/vendor-inputs-v1.tar.gz'
    result=subprocess.run(['scp',*SSH_OPTIONS,str(PRIVATE/'vendor-inputs-v1.tar.gz'),HOST+':'+target],capture_output=True,timeout=240)
    assert result.returncode==0,result.stderr.decode(errors='replace')[:500]
    cpu=json.loads((PRIVATE/'ssh-admission-v1.json').read_text())['least_busy_cpu']
    code=r'''
import os,resource,json,hashlib
from pathlib import Path
os.nice(19);os.sched_setaffinity(0,{__CPU__})
resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));resource.setrlimit(resource.RLIMIT_CPU,(10,11))
root=Path(__ROOT__);path=root/'vendor-inputs-v1.tar.gz'
assert root.resolve()==root and path.is_file() and not path.is_symlink()
h=hashlib.sha256()
with path.open('rb') as stream:
 for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
assert h.hexdigest()==__EXPECTED__
print(json.dumps({'status':'PASS_OPAQUE_INPUT_BUNDLE_TRANSFER','bytes':path.stat().st_size,'sha256':h.hexdigest(),'unpacked':False}))
'''.replace('__CPU__',str(cpu)).replace('__ROOT__',repr(REMOTE)).replace('__EXPECTED__',repr(manifest['archive_sha256']))
    payload=base64.b64encode(code.encode()).decode();cmd='python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(payload)+'))')
    check=subprocess.run(['ssh',*SSH_OPTIONS,HOST,cmd],capture_output=True,timeout=30)
    assert check.returncode==0,check.stderr.decode(errors='replace')[:500]
    proof=json.loads(check.stdout);save(PRIVATE/'input-transfer-v1.json',proof)
    archive_code(ROOT/'tools/r0dq_transport_guard_v1.py');print(json.dumps(proof))


if __name__=='__main__':
    guard=TransportGuard('input-transfer-v1',cpu_seconds=60,wall=300,memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
