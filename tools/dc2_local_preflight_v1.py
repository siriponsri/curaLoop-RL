"""Read-only local/source/remote inventory; does not allocate a model or GPU."""

import base64
import importlib.util
import json
import shutil
import subprocess
from datetime import datetime, timezone

import pyarrow.parquet as pq
from dc2_local_admin_v1 import OLD_TASK, PUBLIC, TASK, authority, sha, write

REMOTE = r"""
import hashlib,http.client,json,os,socket,subprocess
from pathlib import Path
class Unix(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.settimeout(10); self.sock.connect('/var/run/docker.sock')
def get(path):
    c=Unix('localhost',timeout=10); c.request('GET',path)
    r=c.getresponse(); b=r.read(2097153); c.close()
    assert r.status==200 and len(b)<=2097152,(path,r.status)
    return json.loads(b)
def cmd(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=15)
        return {'exit_code':p.returncode,'stdout':p.stdout[:16000],'stderr':p.stderr[:1000]}
    except (OSError,subprocess.TimeoutExpired) as e:
        return {'error':type(e).__name__}
out={'uid':os.getuid(),'cpu_affinity':sorted(os.sched_getaffinity(0)),
     'remote_owned_root_exists':(Path.home()/'curaloop-tasks/lr-dc2-local-20261113-v1').exists(),
     'gpu':cmd(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits']),
     'gpu_processes':cmd(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'])}
try:
    v=get('/version'); out['docker_version']={k:v[k] for k in ['Version','ApiVersion','Os','Arch']}
    info=get('/info'); out['docker_limits']={k:info.get(k) for k in ['MemoryLimit','SwapLimit','CpuCfsPeriod','CpuCfsQuota','NCPU','MemTotal','Runtimes']}
    images=get('/images/json'); out['available_relevant_images']=[{'Id':i['Id'],'RepoTags':i.get('RepoTags'),'Size':i['Size']} for i in images if any(any(x in t.lower() for x in ['ollama','python','scienceagent']) for t in i.get('RepoTags') or [])]
except Exception as e: out['docker_error']=type(e).__name__+':'+str(e)[:600]
root=Path('/data/CIE/cache/ollama/models')
manifest=root/'manifests/hf.co/scb10x/typhoon2.1-gemma3-12b-gguf/Q4_K_M'
out['existing_model_manifest_exists']=manifest.is_file()
if manifest.is_file():
    raw=manifest.read_bytes(); m=json.loads(raw)
    out['existing_model_manifest_sha256']=hashlib.sha256(raw).hexdigest()
    out['existing_model_layers']=[{'mediaType':l['mediaType'],'digest':l['digest'],'bytes':l['size'],'exists':(root/'blobs'/l['digest'].replace(':','-')).is_file()} for l in m['layers']]
print(json.dumps(out))
"""


def main():
    authority()
    out = TASK / "preflight-v1"
    out.mkdir(exist_ok=False)
    annotation = OLD_TASK / "dataset-intake-v1/verified.parquet"
    schema = pq.read_schema(annotation)
    columns = ["instance_id", "domain", "github_name", "eval_script_name", "output_fname"]
    rows = pq.read_table(annotation, columns=columns).to_pylist()
    write(out / "structural-rows.json", rows)
    packages = {
        p: importlib.util.find_spec(p) is not None
        for p in ("rdkit", "pyarrow", "pandas", "fastapi", "pyzipper", "pymupdf")
    }
    encoded = base64.b64encode(REMOTE.encode()).decode()
    command = "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""
    result = subprocess.run(
        [
            "rtk",
            "proxy",
            "ssh",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            "ConnectTimeout=15",
            "100.77.149.83",
            command,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=65,
    )
    write(
        out / "ssh-receipt.json",
        {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr},
    )
    remote = json.loads(result.stdout) if result.returncode == 0 else {"status": "SSH_FAILED"}
    write(out / "remote-inventory.json", remote)
    receipt = {
        "status": "PASS_READ_ONLY_INVENTORY" if result.returncode == 0 else "BLOCKED_SSH",
        "utc": datetime.now(timezone.utc).isoformat(),
        "packages": packages,
        "archive_tools": {n: shutil.which(n) for n in ("7z", "7za", "tar")},
        "annotation_sha256": sha(annotation),
        "annotation_columns": schema.names,
        "structural_rows": len(rows),
        "ssh_exit_code": result.returncode,
        "remote": remote,
        "gpu_allocation": "NOT_RUN",
        "model_calls": 0,
        "archive_extraction": "NOT_RUN",
        "local_guard_scope": "Controller and SSH child",
        "remote_inventory_cpu": "Small unmetered read-only control operation covered by administrative allowance; not a measured zero",
    }
    write(PUBLIC / "read-only-preflight-v1.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
