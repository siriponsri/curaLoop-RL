"""Engineering cycle two: audit native ELF closure, prepare it, then fresh imports."""
import base64,hashlib,importlib.util,json,os,resource,sys
from pathlib import Path

AUDIT=r'''
import glob,json,re,subprocess
from pathlib import Path
targets=[]
for pattern in ['/env/base/rdkit/Chem/Draw/rdMolDraw2D*.so','/env/profile-15/rdkit/Chem/Draw/rdMolDraw2D*.so','/env/profile-53/rasterio/_base*.so']:
 targets.extend(glob.glob(pattern))
out=[]
for target in targets:
 p=subprocess.run(['ldd',target],capture_output=True,text=True,timeout=30)
 out.append(dict(path=target,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,missing=re.findall(r'([\w.+-]+\.so(?:\.\d+)*)\s+=>\s+not found',p.stdout)))
Path('/control/elf-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
'''

LIBRARIES=r'''
import json,subprocess,sys,traceback
from pathlib import Path
sys.path.insert(0,'/code');from envstable_overlay_v1 import extract_deb
packages=json.loads(Path('/control/packages.json').read_text());operations=[];result={}
def run(name,args):
 with Path('/control/'+name+'.log').open('wb') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=300)
 operations.append(dict(operation=name,exit_code=p.returncode))
 if p.returncode:raise RuntimeError(name+' failed')
try:
 for name in ('apt/lists/partial','apt/cache','apt/log','apt/state','debs/partial'):Path('/control/'+name).mkdir(parents=True,exist_ok=True)
 opts=['-o','APT::Sandbox::User=root','-o','Debug::NoLocking=true','-o','Dir::State=/control/apt/state','-o','Dir::State::status=/var/lib/dpkg/status',
  '-o','Dir::State::lists=/control/apt/lists','-o','Dir::Cache=/control/apt/cache','-o','Dir::Cache::archives=/control/debs','-o','Dir::Log=/control/apt/log']
 run('apt-update',['apt-get',*opts,'update'])
 run('apt-download',['apt-get',*opts,'-y','--download-only','--no-install-recommends','install',*packages])
 selected={}
 for path in list(sorted(Path('/packages').glob('*.deb')))+list(sorted(Path('/control/debs').glob('*.deb'))):
  name=subprocess.check_output(['dpkg-deb','-f',str(path),'Package'],text=True).strip()
  if name in {'libc6','libc-bin','base-files'}:raise RuntimeError('Base ABI package denied: '+name)
  selected[name]=path
 records=[extract_deb(path,Path('/syslibs-next')) for name,path in sorted(selected.items())]
 result=dict(status='PASS_LIBRARY_CLOSURE_PREPARED',packages=records,operations=operations)
except BaseException as e:result=dict(status='FAIL_LIBRARY_CLOSURE_PREPARATION',operations=operations,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc())
finally:Path('/control/library-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'])))
'''

def main():
 resource.setrlimit(resource.RLIMIT_CPU,(600,600));resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
 p=json.load(sys.stdin);t=Path('/home/chaw/curaloop-tasks/env-stable-lr-20261114-v1');assert hashlib.sha256((t/'release.json').read_bytes()).hexdigest()==p['release_sha256']
 (t/'repair-worker-v2.py').write_bytes(base64.b64decode(p['worker_b64']))
 def module(name,path):
  s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 rt=module('rt',t/'code/envstable_runtime_v1.py');old=module('oldbuild',t/'build-worker-v1.py');plan=json.loads((t/'build-plan-v1.json').read_text())
 assert (t/'build-result-v1.json').exists()
 common=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib',
  'TF_USE_LEGACY_KERAS=1','TF_CPP_MIN_LOG_LEVEL=2','LOKY_MAX_CPU_COUNT=1']
 mounts=[(t/'env','/env',True),(t/'systemlibs','/syslibs',True),(t/'home','/home/worker',False)]
 audit=rt.run('elf-audit-v2',AUDIT,cpu=120,wall=180,mounts=mounts,env=[*common,'LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu'],stage='build')
 rows=json.loads((t/'leases/elf-audit-v2/elf-result.json').read_text());missing=sorted({n for x in rows for n in x['missing']})
 mapping={'libXext.so.6':'libxext6','libexpat.so.1':'libexpat1','libSM.so.6':'libsm6','libICE.so.6':'libice6','libXrender.so.1':'libxrender1','libgomp.so.1':'libgomp1','libGL.so.1':'libgl1','libGLU.so.1':'libglu1-mesa','libfreetype.so.6':'libfreetype6','libfontconfig.so.1':'libfontconfig1','libudunits2.so.0':'libudunits2-0'}
 assert missing and not set(missing)-set(mapping),missing
 packages=sorted({mapping[n] for n in missing});(t/'systemlibs-v2').mkdir();(t/'systemlibs-v2').chmod(0o777)
 program='from pathlib import Path\nPath("/control/packages.json").write_text('+repr(json.dumps(packages))+')\n'+LIBRARIES
 prior=json.loads((t/'build-result-v1.json').read_text());remaining=20*1024**3-prior['dependency_receive_bytes'];assert remaining>0
 prep=rt.run('library-builder-v2',program,cpu=600,wall=800,network=True,network_bytes=remaining,
  mounts=[(t/'code','/code',True),(t/'packages','/packages',True),(t/'systemlibs-v2','/syslibs-next',False)],tmp_disk=True,stage='build')
 libs=json.loads((t/'leases/library-builder-v2/library-result.json').read_text());outcomes=[]
 if libs['status']=='PASS_LIBRARY_CLOSURE_PREPARED':
  for group in plan['groups']:
   home=t/'home-v2'/group['name'];home.mkdir(parents=True);home.chmod(0o777)
   imports=sorted({n for case in group['cases'] for n in case['imports']});gp=dict(group,imports=imports)
   program='from pathlib import Path\nPath("/control/plan.json").write_text('+repr(json.dumps(gp))+')\n'+old.IMPORTS
   receipt=rt.run('imports-'+group['name']+'-v2',program,cpu=120,wall=180,
    mounts=[(t/'env','/env',True),(t/'systemlibs-v2','/syslibs',True),(home,'/home/worker',False)],
    env=[*common,'LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu','PYTHONPATH=/env/'+group['name']+':/env/base'],tmp_disk=True,stage='build')
   path=t/'leases'/('imports-'+group['name']+'-v2')/'import-result.json'
   outcomes.append(dict(name=group['name'],cases=group['cases'],receipt=receipt,result=json.loads(path.read_text()) if path.exists() else None))
   (t/'repair-progress-v2.json').write_text(json.dumps(outcomes,indent=2))
 result=dict(status='ENGINEERING_CYCLE_2_COMPLETED',elf_audit=rows,missing_before=missing,packages_requested=packages,library_builder=prep,library_result=libs,profiles=outcomes,
  dependency_receive_bytes=prior['dependency_receive_bytes']+prep['resources']['network_receive_bytes'],host_process_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
  all_imports_pass=bool(outcomes) and len(outcomes)==len(plan['groups']) and all(x['result'] and x['result']['status']=='PASS_IMPORTS' for x in outcomes))
 (t/'repair-result-v2.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
