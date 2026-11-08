"""Authenticate and stage only the newly admitted six-pool projection and frozen matrix."""
import base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import ssh_script
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'
paths=[f['path'] for f in json.loads((TASK/'development-projection-manifest.json').read_text())['files']]
paths+=['execution-matrix-v1.json','development-projection-manifest.json','implementation-freeze-v1.json']
blobs={p:base64.b64encode((TASK/p).read_bytes()).decode() for p in paths};pins={p:hashlib.sha256((TASK/p).read_bytes()).hexdigest() for p in paths}
source='''import base64,hashlib,json,os,resource
from pathlib import Path
os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(30,30));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
root=Path(__ROOT__);blobs=__BLOBS__;pins=__PINS__
assert root.resolve()==root and root==Path.home()/'curaloop-tasks/m2-costed-20261108-v2'
for name,encoded in blobs.items():
 assert not Path(name).is_absolute() and '..' not in Path(name).parts
 raw=base64.b64decode(encoded);assert hashlib.sha256(raw).hexdigest()==pins[name]
 target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb') as f:f.write(raw)
 target.chmod(0o600)
print(json.dumps({'status':'PASS_SCOPED_DEVELOPMENT_STAGE','files':len(blobs),'pins':pins,'final_outcomes_opened':False}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__BLOBS__',repr(blobs)).replace('__PINS__',repr(pins))
new(TASK/'data-stage-v1.json',ssh_script(source,60));print(json.dumps({'status':'PASS_SCOPED_DEVELOPMENT_STAGE','files':len(paths)}))
