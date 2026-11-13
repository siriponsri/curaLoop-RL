"""Upload owned admission assets, run guard/setup/qualification once, retain receipts."""
import base64
import json
import subprocess
import sys
from pathlib import Path
from tools.sc1_control_v1 import ACCOUNT, RELEASE, ROOT, digest, write_new
from tools.sc1_job_v1 import save

REMOTE = "/home/chaw/curaloop-tasks/lr-sc1-20261113-v1"
SSH = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "100.77.149.83"]


def reserve(identity, cpu):
    path = ACCOUNT / "ledger.json"
    ledger = json.loads(path.read_text())
    if any(item["id"] == identity for item in ledger["reservations"]):
        raise RuntimeError("Never repeat a retained remote attempt")
    if ledger.get("active_remote_jobs"):
        raise RuntimeError("Remote admission job already active")
    used = sum(item["cpu_seconds"] for item in ledger["reservations"] if item["stage"] == "admission")
    release = json.loads(RELEASE.read_text())
    if used + cpu > release["stage_caps_seconds"]["admission"]["cpu"]:
        raise RuntimeError("Admission allowance unavailable")
    ledger["reservations"].append({"id": identity, "stage": "admission", "cpu_seconds": cpu,
                                   "gpu_allocated_seconds": 0, "host": "dr-train", "status": "RESERVED",
                                   "accounting": "Conservative CPU allocation, not measured aggregate usage"})
    ledger["active_remote_jobs"] = [identity]
    save(path, ledger)


def settle(identity, result):
    target = ACCOUNT / "native-admission-v1" / (identity + ".json")
    write_new(target, result)
    path = ACCOUNT / "ledger.json"
    ledger = json.loads(path.read_text())
    for item in ledger["reservations"]:
        if item["id"] == identity:
            item["status"] = "PASS_TERMINAL_RETAINED" if result.get("status", "").startswith("PASS") else "FAIL_TERMINAL_RETAINED"
            item["receipt_sha256"] = digest(target)
    ledger["active_remote_jobs"] = []
    save(path, ledger)


def call(action, payload, timeout):
    if action == "bootstrap":
        source = (ROOT / "tools/sc1_remote_native_v1.py").read_text(encoding="utf-8")
        payload = dict(payload, source=source)
        code = base64.b64encode(source.encode()).decode()
        command = "python3 -c \"import base64;exec(base64.b64decode('" + code + "'))\" bootstrap"
    else:
        command = f"python3 {REMOTE}/remote.py {action}"
    result = subprocess.run(SSH + [command], input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"SSH operation {action} failed: {result.stderr[-1500:]} {result.stdout[-500:]}")
    return json.loads(result.stdout)


def prepare():
    reserve("native-transfer-remote-v1", 180)
    created = call("bootstrap", {"release": json.loads(RELEASE.read_text())}, 45)
    root = ROOT / "research/raw_data/external-benchmarks/scicode-2024"
    pairs = {
        "inside.py": ROOT / "tools/sc1_native_inside_v1.py",
        "assets/code.zip": root / "upstream-code.zip",
        "assets/test_data.h5": root / "evaluator-private/test_data.h5",
        "assets/problems_dev.jsonl": root / "upstream-hf/problems_dev.jsonl",
        "assets/problems_test.jsonl": root / "upstream-hf/problems_test.jsonl",
        "assets/development-selection.json": ROOT / "docs/evidence/lr-sc1-20261113-v1/development-selection-v1.json",
    }
    manifest = {}
    for destination, source in pairs.items():
        manifest[destination] = {"bytes": source.stat().st_size, "sha256": digest(source)}
        p = subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", str(source), f"100.77.149.83:{REMOTE}/{destination}"], capture_output=True, text=True, timeout=360)
        if p.returncode:
            raise RuntimeError("Owned transfer failed: " + p.stderr[-1200:])
    received = call("receive", {"files": manifest}, 90)
    settle("native-transfer-remote-v1", {"status": received["status"], "bootstrap": created, "files": manifest, "received": received})
    print(json.dumps({"status": received["status"], "files": len(manifest)}))


def execute(action):
    cpu, wall = {"probe": (10, 2), "setup": (1100, 900), "qualify": (3900, 4000)}[action]
    identity = "native-" + action + "-remote-v1"
    reserve(identity, cpu + 20)
    result = call(action, {"cpu": cpu, "wall": wall}, wall + 60)
    settle(identity, result)
    print(json.dumps(result))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "prepare":
        prepare()
    else:
        execute(action)
