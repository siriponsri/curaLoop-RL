"""Book reviewed return/audit envelopes only after all molecular units settle."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'
name=sys.argv[1]
choices={'return-export-v1':('dr-train','return_export',300,600),
 'return-fetch-v1':('local','return_fetch',240,1900),
 'return-verify-v1':('local','return_verify',300,1800),
 'remote-exact-cleanup-v1':('dr-train','remote_cleanup',60,120),
 'analysis-v1':('local','analysis',120,300),
 'figures-v1':('local','figure_render',180,600),
 'closeout-audit-v1':('local','closeout_audit',180,600)}
assert json.loads((TASK/'pipeline-status.json').read_text())['status']=='PASS_COMPLETE_FIXED_M2_MATRIX'
host,handler,reservation,wall=choices[name]
spec=dict(job=name,host=host,handler=handler,bucket='analysis_return_cleanup_retry_delivery',reservation_seconds=reservation,
 wall_seconds=wall,memory_bytes=536870912 if host=='local' else 4294967296,arguments={})
if host=='dr-train':spec.update(cpu=69,task_root=REMOTE)
path=TASK/'specs'/(name+'.json');new(path,spec);print(json.dumps(admin_call('reserve',path)))
