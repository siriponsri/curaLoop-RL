"""Fresh task-scoped Docker admission controller; no historical task imports."""
import hashlib
import http.client
import json
import os
import socket
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TASK = Path("/home/chaw/curaloop-tasks/lr-sc1-20261113-v1")
IMAGE = "sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d"


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(1048576):
            result.update(block)
    return result.hexdigest()


class Unix(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(20)
        self.sock.connect("/var/run/docker.sock")


def api(method, path, payload=None):
    c = Unix("localhost")
    body = json.dumps(payload).encode() if payload is not None else None
    c.request(method, path, body, {"Content-Type": "application/json"})
    response = c.getresponse()
    raw = response.read(4194305)
    c.close()
    if response.status >= 300 or len(raw) > 4194304:
        raise RuntimeError(f"Docker {method} {path}: {response.status}: {raw[:300]!r}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return {"raw": raw.hex()}


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def bootstrap(payload):
    if TASK.exists() or TASK.is_symlink():
        raise RuntimeError("Fresh owned root required")
    TASK.mkdir(parents=True)
    for name in ("assets", "env", "control"):
        (TASK / name).mkdir()
    write(TASK / "release.json", payload["release"])
    (TASK / "remote.py").write_text(payload["source"])
    write(TASK / "bootstrap.json", {"status": "PASS", "uid": os.getuid(), "source_sha256": sha(TASK / "remote.py")})
    return {"status": "PASS_FRESH_ROOT_CREATED", "uid": os.getuid()}


def receive(payload):
    for name, expected in payload["files"].items():
        path = (TASK / name).resolve()
        if not path.is_relative_to(TASK) or path.is_symlink() or path.stat().st_size != expected["bytes"] or sha(path) != expected["sha256"]:
            raise RuntimeError("Transferred source identity differs")
    target = TASK / "assets/code"
    target.mkdir()
    with zipfile.ZipFile(TASK / "assets/code.zip") as archive:
        for item in archive.infolist():
            relative = Path(*Path(item.filename).parts[1:])
            if not relative.parts:
                continue
            path = (target / relative).resolve()
            if not path.is_relative_to(target) or item.file_size > 1048576:
                raise RuntimeError("Unexpected code member")
            if item.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as stream:
                    stream.write(archive.read(item))
    write(TASK / "receive.json", payload)
    return {"status": "PASS_FULL_RECEIVED_FILE_REREAD", "file_count": len(payload["files"])}


def run(mode, payload):
    if mode not in {"qualify-v2"}:
        raise ValueError(mode)
    root = TASK.resolve()
    if root != TASK or TASK.is_symlink():
        raise RuntimeError("Task root changed")
    release = json.loads((TASK / "release.json").read_text())
    cpu, wall = payload["cpu"], payload["wall"]
    if cpu <= 0 or wall <= 0 or cpu > 4000 or wall > 4200:
        raise ValueError("Admission attempt too large")
    control = TASK / "control" / mode
    control.mkdir(exist_ok=False)
    deadline = min(time.time() + wall, datetime.fromisoformat(release["deadline_utc"]).timestamp())
    write(control / "limits.json", {"deadline_epoch": deadline, "cpu_seconds": cpu, "initial_cpu": max(os.sched_getaffinity(0))})
    name = "curaloop-sc1-" + mode + "-20261113-v1"
    config = {"Image": IMAGE, "User": f"{os.getuid()}:{os.getgid()}", "WorkingDir": "/control",
              "Cmd": ["python", "-u", "/worker.py", mode],
              "Env": ["PYTHONPATH=/env", "HOME=/tmp", "PYTHONDONTWRITEBYTECODE=1", "OMP_NUM_THREADS=1", "OPENBLAS_NUM_THREADS=1", "MKL_NUM_THREADS=1"],
              "Labels": {"curaloop.task": "lr-sc1-20261113-v1", "curaloop.purpose": mode},
              "HostConfig": {"CpuPeriod": 100000, "CpuQuota": 100000, "Memory": 4294967296, "MemorySwap": 4294967296,
                  "PidsLimit": 96, "ReadonlyRootfs": True, "CapDrop": ["ALL"], "SecurityOpt": ["no-new-privileges"],
                  "NetworkMode": "bridge" if mode == "setup" else "none", "Tmpfs": {"/tmp": "rw,nosuid,size=512m,mode=1777"},
                  "Mounts": [{"Type": "bind", "Source": str(control), "Target": "/control", "ReadOnly": False},
                             {"Type": "bind", "Source": str(TASK / "env"), "Target": "/env", "ReadOnly": mode != "setup"},
                             {"Type": "bind", "Source": str(TASK / "assets"), "Target": "/assets", "ReadOnly": True},
                             {"Type": "bind", "Source": str(TASK / "inside-v2.py"), "Target": "/worker.py", "ReadOnly": True}]}}
    container = api("POST", "/containers/create?name=" + name, config)["Id"]
    write(control / "container-create.json", {"id": container, "config": config})
    api("POST", f"/containers/{container}/start")
    begin = time.monotonic()
    try:
        while True:
            state = api("GET", f"/containers/{container}/json")
            if not state["State"]["Running"]:
                break
            if time.monotonic() - begin >= wall + 10:
                api("POST", f"/containers/{container}/kill")
                state = api("GET", f"/containers/{container}/json")
                break
            time.sleep(.5)
        logs = api("GET", f"/containers/{container}/logs?stdout=1&stderr=1")
        write(control / "logs.json", logs)
        result = {"status": "PASS" if state["State"]["ExitCode"] == (124 if mode == "probe" else 0) else "FAIL",
                  "mode": mode, "container": container, "state": state["State"],
                  "host_limits": {k: state["HostConfig"][k] for k in ("CpuPeriod", "CpuQuota", "Memory", "MemorySwap", "NetworkMode", "ReadonlyRootfs")},
                  "wall_seconds": time.monotonic() - begin}
        if (control / "result.json").exists():
            result["worker_result"] = json.loads((control / "result.json").read_text())
        write(control / "receipt.json", result)
        return result
    finally:
        state = api("GET", f"/containers/{container}/json")
        if state["State"]["Running"]:
            api("POST", f"/containers/{container}/kill")
        # Stopped containers stay until owned return and final cleanup.


if __name__ == "__main__":
    payload = json.load(sys.stdin)
    action = sys.argv[1]
    if action == "bootstrap":
        result = bootstrap(payload)
    elif action == "receive":
        result = receive(payload)
    else:
        result = run(action, payload)
    print(json.dumps(result))
