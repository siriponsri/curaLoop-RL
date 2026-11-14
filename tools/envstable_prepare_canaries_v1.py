"""Select only four exposed development assets; freeze source/scoring before runs."""
import hashlib,json,sys,tarfile
from pathlib import Path,PurePosixPath
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,write_new
if __name__=='__main__':
 authority('validation');old=ROOT/'.local/lr-sara-20261114-v1/native-assets-v1'
 cases=[x for x in json.loads((old/'private-cases.json').read_text()) if x['instance_id'] in [12,13,71,72]];assert len(cases)==4 and all(x['role']=='development' for x in cases)
 manifest=json.loads((old/'private-member-manifest.json').read_text());wanted=set()
 for c in cases:wanted.update(c['input_members']+c['evaluator_gold_members']+['benchmark/gold_programs/'+c['gold_program_name'],'benchmark/eval_programs/'+c['eval_script_name']])
 bundle=old/'native-assets.tar.gz';assert digest(bundle)=='3c94a1f848f0c49507e95f58f8698096b9eadc7b4da4160a44d27b999dfa7a23'
 target=ACCOUNT/'development-assets-v1';target.mkdir();selected={}
 with tarfile.open(bundle,'r|gz') as tar:
  for item in tar:
   name=item.name.removeprefix('./')
   if name not in wanted:continue
   assert item.isfile() and not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
   out=target/name;out.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256()
   with tar.extractfile(item) as f,out.open('xb') as w:
    while b:=f.read(1024**2):w.write(b);h.update(b)
   assert h.hexdigest()==manifest[name]['sha256'] and out.stat().st_size==manifest[name]['bytes'];selected[name]=manifest[name]
 assert set(selected)==wanted,(wanted-set(selected))
 tarpath=ACCOUNT/'development-assets-v1.tar'
 with tarfile.open(tarpath,'w') as tar:
  for name in sorted(selected):tar.add(target/name,arcname=name,recursive=False)
 plan=dict(schema='curaloop.environment-canary-protocol.v1',case_ids=[12,13,71,72],scope='Engineering native-development validation only; not agent comparison',reference_attempts_per_task=1,reference_cpu_seconds=2100,reference_wall_seconds=2400,grader_cpu_seconds=90,grader_wall_seconds=150,device='CPU only; unchanged source device selection with no visible GPU',network=False,source_edits=False,scorer_edits=False,precreated_output_directory='pred_results',fresh_cache_each_task=True,grader_gold_hidden_from_reference=True,scoring='Unchanged eval(); require tuple of length 2 with first item exactly int 0 or 1; never bool(tuple)',decision='ENVIRONMENT_READY requires all imports/workloads, offline reconstruction, two cold starts and four unchanged native+grader PASS; any failure is reported without scientific rerun',cases=[dict(instance_id=c['instance_id'],profile='profile-12' if c['instance_id'] in [12,13] else 'profile-71',gold_program='benchmark/gold_programs/'+c['gold_program_name'],eval_program='benchmark/eval_programs/'+c['eval_script_name'],output=c['output_fname'],input_members=c['input_members'],gold_members=c['evaluator_gold_members']) for c in cases],members=selected,asset_bundle_sha256=digest(tarpath),asset_bundle_bytes=tarpath.stat().st_size)
 write_new(ACCOUNT/'canary-protocol-private-v1.json',plan)
 write_new(PUBLIC/'canary-protocol-v1.json',{k:v for k,v in plan.items() if k not in ['members','cases'] }|dict(source_hashes={n:d['sha256'] for n,d in selected.items() if n.endswith('.py')},case_profiles={str(c['instance_id']):('profile-12' if c['instance_id'] in [12,13] else 'profile-71') for c in cases}))
 print(json.dumps(dict(status='PASS_DEVELOPMENT_ASSETS_AND_PROTOCOL_FROZEN',members=len(selected),bytes=tarpath.stat().st_size,sha256=digest(tarpath))))
