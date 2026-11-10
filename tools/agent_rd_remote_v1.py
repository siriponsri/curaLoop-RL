"""Parent-owned SSH transport; public task payloads only, no paid provider."""

import argparse
import base64
import json
import subprocess

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, write


def call(action, payload=None, timeout=660):
    assert action in ("bootstrap", "sync-v2", "status", "infer", "development", "evaluation")
    release = read(TASK / "release.json")
    if action == "bootstrap":
        source = (ROOT / "tools/agent_rd_remote_worker_v1.py").read_text(encoding="utf-8")
        encoded = base64.b64encode(source.encode()).decode()
        command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))" bootstrap'
        payload = {"release": release, "worker_source": source}
    elif action == "sync-v2":
        source = (ROOT / "tools/agent_rd_remote_worker_v1.py").read_text(encoding="utf-8")
        program = "import sys,json,hashlib;from pathlib import Path;p=Path.home()/'curaloop-tasks/agent-rd-20261110-v1/worker-v2.py';assert p.parent.is_dir() and not p.exists();s=json.load(sys.stdin)['source'];p.write_text(s);print(json.dumps({'status':'PASS_VERSIONED_WORKER_COPY','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))"
        encoded = base64.b64encode(program.encode()).decode()
        command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
        payload = {"source": source}
    else:
        worker = "worker-v2.py" if (TASK / "remote-sync-v2-receipt-v1.json").exists() else "worker.py"
        command = "python3 " + release["remote_root"] + "/" + worker + " " + action
    result = subprocess.run(["rtk", "proxy", "ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                             "-o", "ConnectTimeout=15", "100.77.149.83", command],
                            input=json.dumps(payload, ensure_ascii=False) if payload is not None else "", capture_output=True,
                            text=True, encoding="utf-8", timeout=timeout)
    if result.returncode:
        raise RuntimeError("Owned model transport failed: " + result.stderr[-1800:] + "\n" + result.stdout[-1200:])
    return json.loads(result.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("bootstrap", "sync-v2", "status", "development", "evaluation"))
    args = parser.parse_args()
    value = call(args.action, timeout=240)
    write(TASK / ("remote-" + args.action + "-receipt-v1.json"), value, True)
    if args.action == "bootstrap":
        write(PUBLIC / "remote-runtime-admission-v1.json", value, True)
    print(json.dumps(value, indent=2))
