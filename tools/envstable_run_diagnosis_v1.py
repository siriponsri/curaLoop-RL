"""Reserve fresh controls once; diagnostic failure remains repairable in scope."""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,save,write_new
from tools.envstable_transport_v1 import call
def main():
 r,l=authority('diagnosis');folder=ACCOUNT/'diagnosis-inputs';folder.mkdir();files=[]
 old=json.loads((ROOT/'docs/evidence/lr-sara-lr1-20261114-v1/frozen-engineering-matrix-v1.json').read_text())
 for row in old['debian_packages']:
  path=ROOT/'.local/lr-sara-lr1-20261114-v1/engineering-input-v1/debs'/row['name'];assert digest(path)==row['sha256']
  files.append(dict(path='packages/'+path.name,sha256=digest(path),bytes_b64=base64.b64encode(path.read_bytes()).decode()))
 overlay=(ROOT/'tools/saralr1_overlay_v1.py').read_bytes();target=ROOT/'tools/envstable_overlay_v1.py'
 with target.open('xb') as f:f.write(overlay)
 for path in (target,ROOT/'tools/envstable_runtime_v1.py'):
  files.append(dict(path='code/'+path.name,sha256=digest(path),bytes_b64=base64.b64encode(path.read_bytes()).decode()))
 write_new(PUBLIC/'diagnostic-control-plan-v1.json',dict(status='FROZEN_BEFORE_CONTROLS',A='Directories absent at Python startup; prepare then load in same process',B='Separate preparation then fresh consuming Python',C='Directories present before Python; prepare then load in same process',debian_packages=old['debian_packages'],worker_sha256=digest(ROOT/'tools/envstable_diagnosis_worker_v1.py'),overlay_sha256=digest(target),ordinary_network=False,scientific_attempts=0))
 reserve('remote-loader-controls-v1','diagnosis',900,remote=True,scope='Matched startup controls A/B/C and real CPU/wall probes; no science')
 result=call(ROOT/'tools/envstable_diagnosis_worker_v1.py',dict(files=files),ACCOUNT/'diagnosis-transport-v1.json',timeout=800)
 write_new(PUBLIC/'loader-controls-v1.json',result);settle('remote-loader-controls-v1','PASS_CONTROLS_CAPTURED',measured_host_process_cpu_seconds=result['host_process_cpu_seconds'])
 l=json.loads((ACCOUNT/'ledger.json').read_text());l['diagnosis_mechanism_supported']=result['mechanism_supported'];l['status']='ACTIVE_BUILD';save(l)
 print(json.dumps(dict(status=result['status'],mechanism_supported=result['mechanism_supported'],controls={k:v['result'] for k,v in result['controls'].items()})))
if __name__=='__main__':main()
