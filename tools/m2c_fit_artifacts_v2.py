"""Freeze training-only gate or control artifacts without inspecting evaluation results."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,batch
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'
kind=sys.argv[1];assert kind in('gates','controls');name='fit-'+kind;code=json.loads((TASK/'code-stage-03.json').read_text())
matrix=TASK/('control-fit-matrix-v2.json' if kind=='controls' and (TASK/'control-fit-matrix-v2.json').exists() else 'execution-matrix-v1.json');components=json.loads(matrix.read_text())['components']
spec=dict(job=name,host='dr-train',cpu=69,handler='gate_fit',bucket='training_prefixes_branches_gate' if kind=='gates' else 'control_tuning',
 reservation_seconds=120,wall_seconds=180,memory_bytes=4294967296,task_root=REMOTE,code_directory=code['code_directory'],code_pins=code['code_pins'],
 arguments=dict(kind=kind,matrix_path=matrix.name,matrix_sha256=hashlib.sha256(matrix.read_bytes()).hexdigest(),components=components),
 development_admission='PASS',final_outcomes_opened=False)
path=TASK/'specs'/(name+'.json');new(path,spec);admin_call('reserve',path);out=batch([name],action='worker');admin_call('settle',name)
assert out['results'][0]['resource']['status']=='PASS',out['results'][0].get('failure')
print(json.dumps({'status':out['results'][0]['result']['status'],'artifacts':len(out['results'][0]['result']['artifacts'])}))
