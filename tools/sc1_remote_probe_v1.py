"""One read-only, noninteractive SSH inventory; no shared host/model changes."""
import json
import shutil
import subprocess
import sys
from tools.sc1_control_v1 import ACCOUNT, write_new


def main():
    metadata = subprocess.run(["ssh", "-G", "dr-train"], capture_output=True, text=True, timeout=15)
    fields = {}
    for line in metadata.stdout.splitlines():
        key, _, value = line.partition(" ")
        if key in {"hostname", "user", "identityfile", "port"}:
            fields.setdefault(key, []).append(value)
    if metadata.returncode or fields.get("user") != ["chaw"]:
        write_new(ACCOUNT / "ssh-probe-v1.json", {"status": "FAIL_PROFILE_IDENTITY", "profile": fields, "ssh_attempted": False})
        raise SystemExit(2)
    command = """printf 'SC1_READONLY\\n'; id -un; python3 --version; command -v docker; docker version --format '{{.Server.Version}}'; docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | head -n 15; nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu --format=csv,noheader; df -B1 /home/chaw /data/CIE/cache/ollama/models; find /data/CIE/cache/ollama/models/manifests -maxdepth 6 -type f 2>/dev/null | head -n 12"""
    attempt = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "ConnectionAttempts=1", "dr-train", command], capture_output=True, text=True, timeout=55)
    record = {"status": "PASS_READ_ONLY_CONNECTIVITY" if attempt.returncode == 0 else "FAIL_SSH", "profile": fields,
              "returncode": attempt.returncode, "stdout": attempt.stdout, "stderr": attempt.stderr,
              "model_inference": False, "remote_mutations": False}
    write_new(ACCOUNT / "ssh-probe-v1.json", record)
    print(json.dumps(record))
    if attempt.returncode:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
