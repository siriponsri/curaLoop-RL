"""Book and dispatch the sole diagnostic import capture, no reference execution."""
import base64,json
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,reserve,settle,save,write_new
from tools.sara_transport_v1 import source_call

def main():
 r,l=authority('technical');assert not l['attempts']['diagnostic_imports']
 for i in (22,26):l['attempts']['diagnostic_imports'][str(i)]={'status':'DISPATCH_RESERVED','attempt':1}
 save(l)
 runtime=ROOT/'tools/sara_docker_runtime_v1.py';worker=ROOT/'tools/sara_diagnose_worker_v1.py'
 reserve('remote-diagnosis-v1','technical',1800,remote=True,scope='Prior-bundle reread/selected restoration, actual watchdog probes, one import for 22/26; no benchmark/model execution')
 result=source_call(worker,dict(runtime_b64=base64.b64encode(runtime.read_bytes()).decode(),runtime_sha256=digest(runtime)),ACCOUNT/'diagnose-transport-v1.json',timeout=1900)
 write_new(PUBLIC/'dependency-diagnosis-v1.json',result)
 l=json.loads((ACCOUNT/'ledger.json').read_text())
 for case in result['diagnosis']['cases']:l['attempts']['diagnostic_imports'][str(case['instance_id'])].update(status='CAPTURED',result=case['result']['status'])
 save(l)
 settle('remote-diagnosis-v1','PASS_CAPTURED_NOT_ENVIRONMENT_VALIDATED',measured_remote_host_process_cpu_seconds=result['remote_host_process_cpu_seconds'],
        measured_container_cpu_seconds=result['container']['resources']['aggregate_cpu_seconds'])
 print(json.dumps(result))

if __name__=='__main__':main()
