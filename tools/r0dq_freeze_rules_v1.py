"""Pin the declared frame recipe before querying the source database."""
import hashlib,json,sys
from pathlib import Path
from r0dq_core_v1 import LocalGuard,ROOT,PRIVATE,save,archive_code
sys.path.insert(0,str(ROOT))
from research.taskfirst_dq_v1.rules import RULES

if __name__=='__main__':
    guard=LocalGuard('frame-rule-freeze-v1',cpu_seconds=30,stage='frame',memory_mib=256)
    try:
        target=PRIVATE/'frame-rules-v1.json';assert not target.exists()
        save(target,RULES);archive_code(ROOT/'research/taskfirst_dq_v1/rules.py')
        print(json.dumps({'status':'FRAME_RULES_FROZEN_BEFORE_DATABASE_QUERIES','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                          'numeric_values_used':False,'real_database_queries_run':False}))
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
