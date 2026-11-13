"""Select a free already-authorized GPU before any product cases, without model changes."""
import base64
import hashlib
import json
import subprocess

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write


def main():
    _, ledger = authority()
    assert not any(k.startswith("product-") for k in ledger.get("provider_attempts", {}))
    original = ROOT / "tools/dc2_local_model_worker_v1.py"
    derived = ROOT / "tools/dc2_local_product_worker_v1.py"
    old = "GPU-277ccc57-c3e5-0731-cd49-f4f8695f7089"
    new = "GPU-044a8b11-4729-458b-a07b-297e45439419"
    source = original.read_bytes()
    assert source.count(old.encode()) == 1 and not derived.exists()
    data = source.replace(old.encode(), new.encode())
    derived.write_bytes(data)
    program = '''import base64,hashlib,json,os,resource,subprocess,sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(10,10))
resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
os.sched_setaffinity(0,{max(os.sched_getaffinity(0))})
payload=json.load(sys.stdin)
gpu=subprocess.check_output(["nvidia-smi","--query-compute-apps=gpu_uuid,pid,used_gpu_memory","--format=csv,noheader"],text=True,timeout=10)
assert not any(line.startswith(payload["gpu_uuid"]+",") for line in gpu.splitlines()),"Selected alternative GPU busy; do not evict"
root=Path("/home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1")
assert root.is_dir() and not root.is_symlink()
target=root/"worker-product-v1.py"
assert not target.exists()
data=base64.b64decode(payload["source_base64"])
assert hashlib.sha256(data).hexdigest()==payload["sha256"]
target.write_bytes(data)
assert hashlib.sha256(target.read_bytes()).hexdigest()==payload["sha256"]
print(json.dumps({"status":"PASS_FREE_GPU_WORKER_INSTALLED_NO_INFERENCE","source_sha256":payload["sha256"],"gpu_uuid":payload["gpu_uuid"],"cpu_cap_seconds":10,"memory_cap_bytes":256*1024**2,"other_gpu_processes_retained":True}))
'''
    identity = "product-device-install-control-v1"
    assert identity not in ledger["bookings"]
    ledger["retained_cpu_seconds"]["implementation"] += 10
    assert ledger["retained_cpu_seconds"]["implementation"] <= ledger["stage_cpu_caps_seconds"]["implementation"]
    ledger["bookings"][identity] = {"host": "dr-train-control", "status": "RESERVED", "bucket": "implementation", "cpu_cap": 10, "gpu_cap": 0}
    save(ledger)
    result = subprocess.run(["rtk", "proxy", "ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "100.77.149.83", "python3 -c \"import base64;exec(base64.b64decode('" + base64.b64encode(program.encode()).decode() + "'))\""], input=json.dumps({"source_base64": base64.b64encode(data).decode(), "sha256": hashlib.sha256(data).hexdigest(), "gpu_uuid": new}), text=True, encoding="utf-8", capture_output=True, timeout=30)
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][identity]["status"] = "PASS" if result.returncode == 0 else "FAIL"
    save(ledger)
    write(TASK / "product-device-install-v1.json", {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    assert result.returncode == 0, result.stderr
    receipt = {**json.loads(result.stdout), "prior_selected_gpu": old, "reason": "V100 occupied by an unrelated Python process; free RTX 2080 Ti used within existing one-GPU authorization. Same checkpoint, model settings, prompts, cases and scoring. No external comparative experiment exists.", "original_worker_sha256": sha(original), "product_worker_sha256": sha(derived), "model_change": False, "cpu_quota": 2, "host_memory_cap_gib": 20, "gpu_quota": 1, "automatic_case_repeats": False, "model_may_partially_offload_to_cpu": True}
    write(PUBLIC / "product-device-selection-v1.json", receipt)
    print(json.dumps(receipt))

if __name__ == "__main__":
    main()
