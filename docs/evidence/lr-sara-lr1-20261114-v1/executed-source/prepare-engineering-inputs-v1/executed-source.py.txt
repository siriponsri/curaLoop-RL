"""Select seven authorized Debian archives from the verified local owned return."""
import ast,json,sys,tarfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,write_new
def main():
 r,l=authority('engineering');assert l['attempts']['engineering'] is None
 src=ROOT/'.local/lr-sara-20261114-v1/remote-return-v1'
 proof=json.loads((ROOT/'docs/evidence/lr-sara-20261114-v1/owned-return-verification-v1.json').read_text())
 assert digest(src/'owned-manifest.json')==proof['manifest_sha256'] and digest(src/'owned-return.tar.gz')==proof['bundle_sha256']
 m=json.loads((src/'owned-manifest.json').read_text());wanted={k:v for k,v in m['files'].items() if k.startswith('leases/final-correction-setup-v1/debs/') and k.endswith('.deb')}
 assert len(wanted)==7;out=ACCOUNT/'engineering-input-v1';out.mkdir();debs=out/'debs';debs.mkdir();rows=[]
 with tarfile.open(src/'owned-return.tar.gz','r|gz') as archive:
  for item in archive:
   if item.name in wanted:
    assert item.isfile() and item.size==wanted[item.name]['bytes']
    dest=debs/Path(item.name).name
    with archive.extractfile(item) as f,dest.open('xb') as g:
     while block:=f.read(1024**2):g.write(block)
    assert digest(dest)==wanted[item.name]['sha256'];rows.append(dict(name=dest.name,bytes=dest.stat().st_size,sha256=digest(dest),source_member=item.name))
 assert len(rows)==7
 # Derive the already evidenced runtime guard with only new task identity/deadline routing.
 source=(ROOT/'tools/sara_docker_runtime_v1.py').read_text()
 source=source.replace('lr-sara-20261114-v1','lr-sara-lr1-20261114-v1').replace('curaloop-sara-','curaloop-saralr1-')
 source=source.replace("deadline=datetime.fromisoformat(release['technical_deadline_utc']).timestamp()","deadline=datetime.fromisoformat(release['deadlines_utc'][stage]).timestamp()")
 source=source.replace('network_bytes=0,tmp_disk=False):',"network_bytes=0,tmp_disk=False,stage='engineering'):")
 assert 'technical_deadline_utc' not in source;compile(source,'saralr1_runtime_v1.py','exec')
 runtime=ROOT/'tools/saralr1_runtime_v1.py'
 with runtime.open('x',encoding='utf-8',newline='\n') as f:f.write(source)
 program=ROOT/'tools/saralr1_acceptance_program_v1.py';patch=ROOT/'tools/saralr1_overlay_v1.py'
 for p in (program,patch):ast.parse(p.read_text(),feature_version=(3,10))
 matrix=dict(status='FROZEN_BEFORE_ONE_ENGINEERING_RUN',candidate=1,matrix_runs_max=1,
  debian_packages=sorted(rows,key=lambda x:x['name']),patch_source_sha256=digest(patch),acceptance_source_sha256=digest(program),runtime_source_sha256=digest(runtime),
  image='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d',
  expected_tests=['all-seven-payloads','retained-libgomp-independent-hash','actual-libgomp-libXrender-load','root-metadata-skipped-and-content-links-mode','eight-malformed-archive-rejections','streaming-sha-known-values','bind-root-owner-group-mode'],
  synthetic_fixtures_are='Engineering negative-path tests only, never substitutes for agent/native outcomes',native_references=0,provider_calls=0)
 write_new(PUBLIC/'frozen-engineering-matrix-v1.json',matrix);write_new(out/'matrix.json',matrix)
 print(json.dumps(dict(status='PASS_ENGINEERING_INPUTS_AND_CANDIDATE_FROZEN',packages=7,patch_sha256=digest(patch))))
if __name__=='__main__':main()
