"""Tiny local file-stat control; no data bytes or additional remote work."""
import json
from r0dq_core_v1 import PRIVATE,LocalGuard,now

if __name__=='__main__':
    guard=LocalGuard('return-stat-'+now().replace(':','').replace('.','').replace('+',''),cpu_seconds=2,wall=10,memory_mib=128)
    try:
        path=PRIVATE/'remote-return/full-task-v1.tar.gz.part'
        manifest=json.loads((PRIVATE/'remote-return/export-terminal/manifest.json').read_text())
        size=path.stat().st_size if path.exists() else 0
        print(json.dumps({'status':'RETURN_TRANSPORT_FILE_STAT','received_bytes':size,'expected_bytes':manifest['archive_bytes'],
            'percent':round(100*size/manifest['archive_bytes'],1),'archive_exists':path.with_suffix('').exists()}))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',control_only=True,reads_file_metadata_only=True)
