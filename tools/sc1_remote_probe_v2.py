"""Use the owner's existing IP-based SSH profile; the unconfigured alias is retained."""
import base64
import json
import subprocess
from tools.sc1_control_v1 import ACCOUNT, write_new

REMOTE = r'''
import http.client,json,os,socket,subprocess,shutil
from pathlib import Path
def cmd(args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=15)
    return {"returncode":p.returncode,"stdout":p.stdout[:12000],"stderr":p.stderr[:1200]}
class Unix(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.settimeout(10);self.sock.connect('/var/run/docker.sock')
def get(path):
    c=Unix('localhost');c.request('GET',path);r=c.getresponse();b=r.read(2097153);c.close()
    if r.status!=200 or len(b)>2097152:raise RuntimeError('Docker read-only query failed')
    return json.loads(b)
out={"uid":os.getuid(),"cpu_affinity":sorted(os.sched_getaffinity(0)),
"gpu":cmd(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits']),
"gpu_processes":cmd(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),
"owned_root_exists":Path('/home/chaw/curaloop-tasks/lr-sc1-20261113-v1').exists(),
"disk_free_bytes":shutil.disk_usage('/home/chaw').free}
try:
    out['docker_version']=get('/version')['Version']
    info=get('/info');out['docker_limits']={k:info.get(k) for k in ['MemoryLimit','SwapLimit','CpuCfsPeriod','CpuCfsQuota','NCPU','MemTotal','Runtimes']}
    out['images']=[{'Id':i['Id'],'RepoTags':i.get('RepoTags'),'Size':i['Size']} for i in get('/images/json') if any(any(s in t.lower() for s in ['ollama','python','scienceagent']) for t in i.get('RepoTags') or [])]
except Exception as e:out['docker_error']=str(e)
m=Path('/data/CIE/cache/ollama/models/manifests/hf.co/scb10x/typhoon2.1-gemma3-12b-gguf/Q4_K_M')
out['existing_typhoon_manifest_exists']=m.is_file()
if m.is_file():out['existing_typhoon_manifest']=json.loads(m.read_text())
print(json.dumps(out))
'''


def main():
    profile = subprocess.run(["ssh", "-G", "100.77.149.83"], capture_output=True, text=True, timeout=15)
    fields = {}
    for line in profile.stdout.splitlines():
        key, _, value = line.partition(" ")
        if key in {"hostname", "user", "identityfile", "port"}:
            fields.setdefault(key, []).append(value)
    if profile.returncode or fields.get("user") != ["chaw"] or fields.get("hostname") != ["100.77.149.83"] or not any("id_ed25519_dr_train" in name for name in fields.get("identityfile", [])):
        write_new(ACCOUNT / "ssh-probe-v2.json", {"status": "FAIL_PROFILE_IDENTITY", "profile": fields, "ssh_attempted": False})
        raise SystemExit(2)
    encoded = base64.b64encode(REMOTE.encode()).decode()
    command = "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""
    p = subprocess.run(["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "-o", "ConnectionAttempts=1", "100.77.149.83", command], capture_output=True, text=True, encoding="utf-8", timeout=65)
    record = {"status": "PASS_READ_ONLY_CONNECTIVITY" if p.returncode == 0 else "FAIL_SSH", "profile": fields,
              "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
              "model_inference": False, "remote_mutations": False,
              "alias_v1_connect_attempts": 0, "this_profile_connect_attempts": 1}
    write_new(ACCOUNT / "ssh-probe-v2.json", record)
    print(json.dumps(record))
    if p.returncode:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
