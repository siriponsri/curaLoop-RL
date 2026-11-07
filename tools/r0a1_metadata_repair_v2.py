"""Preserve colon-separated residue labels without altering earlier exports."""
from r0a1_core_v1 import Guard,ROOT,archive_code
from r0a1_metadata_repair_v1 import run

if __name__=='__main__':
    guard=Guard('metadata-parser-repair-v2',cpu_seconds=60)
    try:
        run('metadata-context-v3.json','mask-checks-v3.json')
        archive_code(ROOT/'tools/r0a1_metadata_repair_v1.py')
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
