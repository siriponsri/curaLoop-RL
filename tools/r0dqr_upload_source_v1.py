"""Transfer existing pinned archive once; no scientific HTTP download."""
import json,subprocess
from r0dqr_core_v1 import PRIVATE,REMOTE,HOST,SSH_OPTIONS,save,ARCHIVE_SHA
from r0dqr_transport_guard_v1 import TransportGuard
from r0dqr_rpc_v1 import ssh

if __name__=='__main__':
    guard=TransportGuard('source-archive-transport-v1',cpu_seconds=180,wall=1800,memory_mib=256)
    try:
        proof=json.loads((PRIVATE/'source-reuse-v1.json').read_text());assert proof['source_sha256']==ARCHIVE_SHA
        source=PRIVATE/'source/chembl_37_sqlite.tar.gz';assert source.stat().st_size==5764252857
        ssh('import json,os;from pathlib import Path;r=Path('+repr(REMOTE)+');assert r.resolve()==r and r.stat().st_uid==os.getuid();p=r/"source";p.mkdir(exist_ok=False);print(json.dumps({"status":"FRESH_ARCHIVE_COPY_TARGET"}))')
        result=subprocess.run(['scp',*SSH_OPTIONS,str(source),HOST+':'+REMOTE+'/source/chembl_37_sqlite.tar.gz'],capture_output=True,timeout=1700)
        if result.returncode:
            (PRIVATE/'archive-transport-error-private.txt').write_bytes(result.stderr);raise RuntimeError('Archive transport failed; no automatic repeat')
        save(PRIVATE/'archive-transport-v1.json',{'status':'PASS_SOURCE_ARCHIVE_TRANSPORT_PENDING_REMOTE_DIGEST','bytes':source.stat().st_size,
            'expected_sha256':ARCHIVE_SHA,'new_bulk_http_requests':0})
        print(json.dumps({'status':'PASS_SOURCE_ARCHIVE_TRANSPORT_PENDING_REMOTE_DIGEST','bytes':source.stat().st_size}))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
