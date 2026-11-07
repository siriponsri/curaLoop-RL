"""Repair only the fixture backup transaction; retain the failed receipt."""
import json
from r0dq_core_v1 import LocalGuard,PRIVATE,ROOT,archive_code
from r0dq_fixtures_v1 import run

if __name__=='__main__':
    old=json.loads((PRIVATE/'projection-fixtures-v1-resource.json').read_text())
    assert old['status']=='FAIL_RESOURCE_LIMIT'
    guard=LocalGuard('projection-fixtures-v2',cpu_seconds=60,memory_mib=256)
    try:
        run('projection-fixtures-v2.json')
        archive_code(ROOT/'tools/r0dq_fixtures_v1.py')
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',previous_failed_fixture_retained=True)
