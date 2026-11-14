"""Publish metadata for reusing the verified artifact without reinstalling packages."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,write_new
if __name__=='__main__':
 authority('analysis_return');build=json.loads((PUBLIC/'profile-build-cycle1.json').read_text());cold=json.loads((PUBLIC/'offline-reconstruction-cold-starts-v1.json').read_text());profiles={};tasks={}
 for row in build['rows']:
  name=row['name'];paths=(['/env/addons-profile12'] if name=='profile-12' else [])+['/env/'+name]+([] if name=='base' else ['/env/base'])
  profiles[name]=dict(pythonpath=':'.join(paths),readonly_artifact_directories=['env/'+name]+(['env/addons-profile12'] if name=='profile-12' else [])+([] if name=='base' else ['env/base']),workload='tools/envstable_workloads_v2.py '+name)
  for c in row['cases']:
   i=str(c['instance_id']);assert i not in tasks;tasks[i]=dict(profile=name,required_imports=c['imports'],native_status='See native-development-canaries-v1.json' if int(i) in [12,13,71,72] else 'NOT_RUN_LOCKED')
 assert len(tasks)==30 and len(profiles)==13
 write_new(PUBLIC/'profile-adapter-contract-v1.json',dict(schema='curaloop.environment-adapter.v1',base_image='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d',python='3.10.22',content_lock_sha256=cold['reconstruction']['lock_sha256'],artifact_system_libraries='systemlibs-v2',library_environment='LD_LIBRARY_PATH=/syslibs/usr/lib/x86_64-linux-gnu',library_mount='/syslibs',profile_mount='/env',cache_environment=['HOME=/home/worker','PYSTOW_HOME=/home/worker/.data','XDG_CACHE_HOME=/home/worker/.cache','MPLCONFIGDIR=/home/worker/.cache/matplotlib'],all_cache_directories_prepared_before_exec=True,thread_environment=['OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1','LOKY_MAX_CPU_COUNT=1'],other_environment=['MPLBACKEND=Agg','PYTHONDONTWRITEBYTECODE=1','TF_USE_LEGACY_KERAS=1'],profiles=profiles,tasks=tasks,interpretation='Metadata adapter for the installed artifact; not a new scientific release or complete native qualification'))
 (ROOT/'docs/08_agent_rd/ENV_STABLE_ARTIFACT_REUSE_20261114.md').write_text('''# Reusing the ENV-STABLE-LR installed artifact

The authoritative mapping is [profile-adapter-contract-v1.json](../evidence/env-stable-lr-20261114-v1/profile-adapter-contract-v1.json).
Read the [final owner report](ENV_STABLE_LR_FINAL_OWNER_REPORT_20261114.md) before use.

The local ignored account `.local/env-stable-lr-20261114-v1/remote-return-v1/`
contains the full compressed archive and content/metadata manifest. Check both
hashes against `owned-return-verification-v1.json`. Inside the archive, `env/`
contains the installed profiles and `systemlibs-v2/` their prepared native-library
overlay. The independently copied `reconstructed/` artifact passed all13
workloads under two fresh worker/cache sets on the pinned shared base image.
The full lock and resolved package-version manifest are in
`leases/offline-reconstruct-v1/`.

Do not run the closed account's controller as a fresh research release. A future
authorized release must use a new owned root and accounting, retain protected
roles, verify the content lock, use the mapping's profile/addon precedence and
prepare library/cache directories before the fresh worker starts. Mount package
and scientific inputs read-only, keep grader gold separate from actors/reference
workers, and apply resource/conflict checks before any job. Reuse successful
development evidence; do not reinstall/search packages merely to start over.

The transfer archive stores identical bytes once and may refer to an earlier
member. A restoring program must validate member paths and manifest hashes,
copy alias bytes independently when metadata differs, and not follow arbitrary
symlinks. Blind extraction is not a demonstrated restoration procedure. Local
stream verification is complete; full restoration from that transfer archive on
a second host and fresh online dependency resolution were NOT_RUN. The retained
shared base image was not deleted; cross-host image provisioning was NOT_RUN.

These artifacts establish engineering behavior in the tested image. Only four
development references ran once. They do not establish thirty-task native
admission, agent reliability, scientific effect, independent expert validation,
user benefit, or manuscript readiness.
''',encoding='utf-8',newline='\n')
 print(json.dumps(dict(status='PASS_ARTIFACT_ADAPTER_METADATA',profiles=len(profiles),tasks=len(tasks))))
