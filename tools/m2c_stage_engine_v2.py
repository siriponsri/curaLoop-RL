"""Stage a new immutable code projection and run data-free constructed checks."""
import base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call,batch,ssh_script
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'


def main():
    version=sys.argv[1];directory='code-engine-'+version;name='engine-checks-'+version
    paths=['research/__init__.py','research/longrun_v1/__init__.py','research/longrun_v1/guard.py',
       'research/m2_v1/__init__.py','research/m2_v1/models.py']
    paths+=sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'research/m2_costed_v2').glob('*.py'))
    pins={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    assert pins['research/m2_v1/models.py']=='7a7403e5906dc0b74883f9d2eb35b50a438f13273d82cd2c9ddb25430ba722dc'
    blobs={p:base64.b64encode((ROOT/p).read_bytes()).decode() for p in paths}
    source='''import base64,hashlib,json,os,resource
from pathlib import Path
os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(20,20));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
root=Path(__ROOT__);directory=__DIR__;pins=__PINS__;blobs=__BLOBS__
assert root.resolve()==root and root==Path.home()/'curaloop-tasks/m2-costed-20261108-v2'
dest=root/directory;dest.mkdir(exist_ok=False)
for name,encoded in blobs.items():
 assert not Path(name).is_absolute() and '..' not in Path(name).parts
 raw=base64.b64decode(encoded);assert hashlib.sha256(raw).hexdigest()==pins[name]
 target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb') as f:f.write(raw)
 target.chmod(0o600)
print(json.dumps({'status':'PASS_CODE_STAGE','code_directory':directory,'code_pins':pins}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__DIR__',repr(directory)).replace('__PINS__',repr(pins)).replace('__BLOBS__',repr(blobs))
    stage=ssh_script(source,45);new(TASK/('code-stage-'+version+'.json'),stage)
    spec={'job':name,'host':'dr-train','cpu':69,'handler':'synthetic_checks','bucket':'engineering_guards',
      'reservation_seconds':60,'wall_seconds':120,'memory_bytes':4294967296,'task_root':REMOTE,
      'code_directory':directory,'code_pins':pins,'arguments':{}}
    path=TASK/'specs'/f'{name}.json';new(path,spec);admin_call('reserve',path)
    output=batch([name],action='worker');admin_call('settle',name)
    print(json.dumps({'job':name,'resource':output['results'][0].get('resource',{}).get('status'),
      'result':output['results'][0].get('result'),'failure':output['results'][0].get('failure')}),flush=True)
    assert output['results'][0]['exit_code']==0,'ENGINE_CHECKS_FAILED'


if __name__=='__main__':main()
