"""Owned GPU worker; Docker I/O reused from preserved AgentRD source."""

import fcntl
import hashlib
import http.client
import json
import os
import re
import resource
import socket
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote, urlencode

TASK = Path.home() / "curaloop-tasks/lr-dc2-local-20261113-v1"
NAME = "curaloop-dc2-local-model-20261113-v1"
MODEL = "hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M"
DIGEST = "ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b"
GPU = "GPU-277ccc57-c3e5-0731-cd49-f4f8695f7089"
IMAGE = "sha256:a61a8fd395dbb931cc8cb1b5da7a2510746575c87113fdc45b647ee59ef7f808"
API_VERSION = None


class UnixConnection(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect("/var/run/docker.sock")


def api(method, path, body=None, timeout=30):
    global API_VERSION
    if API_VERSION is None and path != "/version":
        API_VERSION = "/v" + api("GET", "/version")["ApiVersion"]
    connection = UnixConnection("localhost", timeout=timeout)
    raw = json.dumps(body).encode() if body is not None else None
    connection.request(
        method, (API_VERSION or "") + path, raw, {"Content-Type": "application/json"}
    )
    response = connection.getresponse()
    data = response.read()
    connection.close()
    if response.status >= 300:
        raise RuntimeError(
            "Docker Unix API "
            + path
            + ": "
            + str(response.status)
            + " "
            + data[:1000].decode(errors="replace")
        )
    return json.loads(data) if data else None


def execute(name, command, data=None, detached=False, timeout=30):
    config = {
        "AttachStdin": data is not None,
        "AttachStdout": not detached,
        "AttachStderr": not detached,
        "Tty": False,
        "Cmd": list(command),
    }
    identity = api("POST", "/containers/" + name + "/exec", config)["Id"]
    if detached:
        api("POST", "/exec/" + identity + "/start", {"Detach": True, "Tty": False})
        return b"", b""
    # Docker's documented exec stream upgrade, without the Go CLI's large virtual heap.
    body = b'{"Detach":false,"Tty":false}'
    request = (
        "POST "
        + API_VERSION
        + "/exec/"
        + identity
        + "/start HTTP/1.1\r\nHost: localhost\r\nConnection: Upgrade\r\nUpgrade: tcp\r\nContent-Type: application/json\r\nContent-Length: "
        + str(len(body))
        + "\r\n\r\n"
    ).encode() + body
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect("/var/run/docker.sock")
    sock.sendall(request)
    header = b""
    while not header.endswith(b"\r\n\r\n") and len(header) < 16384:
        part = sock.recv(1)
        if not part:
            break
        header += part
    assert b"101 UPGRADED" in header.upper() or b"200 OK" in header.upper(), header
    if data is not None:
        sock.sendall(data)
    sock.shutdown(socket.SHUT_WR)
    stream = bytearray()
    while True:
        block = sock.recv(65536)
        if not block:
            break
        stream.extend(block)
        assert len(stream) <= 2097152
    sock.close()
    output, errors = bytearray(), bytearray()
    cursor = 0
    while cursor < len(stream):
        assert cursor + 8 <= len(stream)
        channel, size = stream[cursor], struct.unpack(">I", stream[cursor + 4 : cursor + 8])[0]
        assert channel in (1, 2) and cursor + 8 + size <= len(stream)
        (output if channel == 1 else errors).extend(stream[cursor + 8 : cursor + 8 + size])
        cursor += 8 + size
    status = api("GET", "/exec/" + identity + "/json")
    assert not status["Running"] and status["ExitCode"] == 0, errors.decode(errors="replace")[:1800]
    return bytes(output), bytes(errors)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def docker(*args, **kwargs):
    text = kwargs.pop("text", False)
    timeout = kwargs.pop("timeout", 30)
    if args[:2] == ("ps", "-a"):
        rows = api(
            "GET",
            "/containers/json?"
            + urlencode({"all": "1", "filters": json.dumps({"name": ["^/" + NAME + "$"]})}),
        )
        out = "\n".join(r["Id"] for r in rows).encode()
    elif args[:2] == ("image", "inspect"):
        out = json.dumps([api("GET", "/images/" + quote(args[2], safe="") + "/json")]).encode()
    elif args[0] == "inspect":
        out = json.dumps([api("GET", "/containers/" + args[1] + "/json")]).encode()
    elif args[0] == "start":
        api("POST", "/containers/" + args[1] + "/start")
        out = b""
    elif args[0] == "exec":
        rest = list(args[1:])
        detached = "-d" in rest
        rest = [v for v in rest if v not in ("-i", "-d")]
        out, err = execute(rest[0], rest[1:], kwargs.pop("input", None), detached, timeout)
        assert not kwargs
        return SimpleNamespace(
            stdout=out.decode() if text else out, stderr=err.decode() if text else err, returncode=0
        )
    else:
        raise ValueError("No generic Docker/shell fallback")
    assert not kwargs
    return SimpleNamespace(
        stdout=out.decode() if text else out, stderr="" if text else b"", returncode=0
    )


def cpu_seconds():
    value = docker("exec", NAME, "cat", "/sys/fs/cgroup/cpu.stat", text=True, timeout=10).stdout
    return int(dict(line.split() for line in value.splitlines())["usage_usec"]) / 1e6


def http(path, body=None, timeout=20):
    assert path in ("/api/tags", "/api/ps", "/api/chat", "/api/version")
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else b""
    request = (
        ("POST" if body is not None else "GET")
        + " "
        + path
        + " HTTP/1.0\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: "
        + str(len(data))
        + "\r\nConnection: close\r\n\r\n"
    ).encode() + data
    # Static shell program; all model/request text travels as data on stdin.
    result = docker(
        "exec",
        "-i",
        NAME,
        "/bin/bash",
        "-c",
        "exec 3<>/dev/tcp/127.0.0.1/11434; cat >&3; cat <&3",
        input=request,
        timeout=timeout,
    )
    header, content = result.stdout.split(b"\r\n\r\n", 1)
    if not header.startswith(b"HTTP/1.0 200") and not header.startswith(b"HTTP/1.1 200"):
        raise RuntimeError("Owned model HTTP failure: " + content[:500].decode(errors="replace"))
    return json.loads(content)


def read(path):
    return json.loads(Path(path).read_text())


def write_once(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def authority(*, execution=True):
    release = read(TASK / "release.json")
    if execution:
        assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert release["remote_root"] == str(TASK)
    assert release["model"] == MODEL and release["model_digest"] == DIGEST
    return release


def gpu_state():
    p = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=gpu_uuid,pid,used_gpu_memory",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return [s.strip() for s in p.stdout.splitlines() if s.strip().startswith(GPU + ",")]


def owned():
    value = api("GET", "/containers/" + NAME + "/json")
    assert value["Config"]["Labels"]["curaloop.task"] == "lr-dc2-local-20261113-v1"
    assert value["Image"] == IMAGE
    return value


def bootstrap(payload):
    assert not TASK.exists() and not TASK.is_symlink()
    assert TASK.parent.resolve().is_relative_to(Path.home().resolve())
    release = payload["release"]
    assert release["remote_root"] == str(TASK) and release["model"] == MODEL
    assert release["model_digest"] == DIGEST
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert hashlib.sha256(payload["worker_source"].encode()).hexdigest() == payload["worker_sha256"]
    manifest = Path(
        "/data/CIE/cache/ollama/models/manifests/hf.co/scb10x/typhoon2.1-gemma3-12b-gguf/Q4_K_M"
    )
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == DIGEST
    api("GET", "/images/" + quote(IMAGE, safe="") + "/json")
    TASK.mkdir(parents=True, exist_ok=False)
    for name in ("leases", "calls", "control"):
        (TASK / name).mkdir()
    (TASK / "worker.py").write_text(payload["worker_source"])
    write_once(TASK / "release.json", release)
    result = {
        "status": "PASS_OWNED_ROOT_NO_GPU_ALLOCATION",
        "utc": stamp(),
        "worker_sha256": payload["worker_sha256"],
        "model_digest": DIGEST,
        "image": IMAGE,
        "gpu_allocation": "NOT_RUN",
        "inference": "NOT_RUN",
    }
    write_once(TASK / "bootstrap-receipt.json", result)
    return result


def start_lease(payload):
    release = authority()
    identity = payload["lease_id"]
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,80}", identity)
    lease = TASK / "leases" / identity
    assert not lease.exists(), "Never replay or reset a lease"
    assert 30 <= payload["gpu_cap_seconds"] <= 3600
    assert 30 <= payload["cpu_cap_seconds"] <= 7200
    assert not gpu_state(), "Selected GPU is busy; do not evict it"
    containers = api("GET", "/containers/json?all=1")
    assert not any("/" + NAME in c["Names"] for c in containers)
    lease.mkdir()
    allowed = sorted(os.sched_getaffinity(0))[-3:]
    assert len(allowed) == 3
    began = time.time()
    deadline = min(
        began + payload["gpu_cap_seconds"],
        datetime.fromisoformat(release["deadline_utc"]).timestamp(),
    )
    (TASK / "control/limits.txt").write_text(
        f"{int(deadline) - 5} {int((payload['cpu_cap_seconds'] - 10) * 1000000)}\n"
    )
    watch = [
        "#!/bin/bash",
        "while true; do",
        " read deadline cap < /control/limits.txt",
        " usage=0",
        " while read key value; do if [[ $key == usage_usec ]]; then usage=$value; fi; done < /sys/fs/cgroup/cpu.stat",
        " if (( $(date +%s) >= deadline || usage >= cap )); then kill -TERM 1; sleep 1; kill -KILL 1; exit 124; fi",
        " sleep 1",
        "done",
        "",
    ]
    (TASK / "control/watch.sh").write_text("\n".join(watch))
    config = {
        "Image": IMAGE,
        "Cmd": ["serve"],
        "Labels": {"curaloop.task": "lr-dc2-local-20261113-v1", "curaloop.lease": identity},
        "Env": [
            "OLLAMA_MODELS=/models",
            "OLLAMA_HOST=127.0.0.1:11434",
            "OLLAMA_NUM_PARALLEL=1",
            "OLLAMA_MAX_LOADED_MODELS=1",
            "OLLAMA_CONTEXT_LENGTH=8192",
            "OLLAMA_KEEP_ALIVE=-1",
            "NVIDIA_VISIBLE_DEVICES=" + GPU,
            "NVIDIA_DRIVER_CAPABILITIES=compute,utility",
        ],
        "HostConfig": {
            "NetworkMode": "none",
            "NanoCpus": 2000000000,
            "CpusetCpus": ",".join(map(str, allowed[:2])),
            "Memory": 20 * 1024**3,
            "MemorySwap": 20 * 1024**3,
            "PidsLimit": 128,
            "ReadonlyRootfs": True,
            "Tmpfs": {"/tmp": "rw,size=256m", "/root/.ollama": "rw,size=64m"},
            "LogConfig": {"Type": "local", "Config": {"max-size": "5m", "max-file": "2"}},
            "DeviceRequests": [{"Driver": "nvidia", "DeviceIDs": [GPU], "Capabilities": [["gpu"]]}],
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": "/data/CIE/cache/ollama/models",
                    "Target": "/models",
                    "ReadOnly": True,
                },
                {
                    "Type": "bind",
                    "Source": str(TASK / "control"),
                    "Target": "/control",
                    "ReadOnly": True,
                },
            ],
        },
    }
    created = api("POST", "/containers/create?name=" + NAME, config)
    value = owned()
    h = value["HostConfig"]
    assert h["NanoCpus"] == 2000000000 and h["Memory"] == h["MemorySwap"] == 20 * 1024**3
    assert h["NetworkMode"] == "none" and h["ReadonlyRootfs"] and not h.get("Privileged")
    assert h["DeviceRequests"][0]["DeviceIDs"] == [GPU]
    write_once(
        lease / "start.json",
        {
            "lease_id": identity,
            "utc": stamp(),
            "allocated_start_epoch": began,
            "hard_deadline_epoch": deadline,
            "limits": payload,
            "container_id": created["Id"],
            "host_config": h,
        },
    )
    api("POST", "/containers/" + NAME + "/start")
    execute(NAME, ["/bin/bash", "/control/watch.sh"], detached=True)
    for _ in range(40):
        try:
            tags = http("/api/tags", timeout=2)
            break
        except (OSError, RuntimeError, ValueError, AssertionError):
            time.sleep(0.5)
    else:
        raise RuntimeError("Owned model did not become ready")
    assert any(m["name"] == MODEL and m["digest"] == DIGEST for m in tags["models"])
    result = {
        "status": "PASS_GPU_LEASE_STARTED_NO_INFERENCE",
        "lease_id": identity,
        "gpu_uuid": GPU,
        "model_digest": DIGEST,
        "cpu_seconds": cpu_seconds(),
        "running_model_metadata": http("/api/ps"),
        "utc": stamp(),
    }
    write_once(lease / "ready.json", result)
    return result


def infer(payload):
    authority()
    identity = payload["call_id"]
    assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,120}", identity)
    lease = TASK / "leases" / payload["lease_id"]
    start = read(lease / "start.json")
    assert not (lease / "stop.json").exists() and time.time() < start["hard_deadline_epoch"] - 10
    assert owned()["Config"]["Labels"]["curaloop.lease"] == payload["lease_id"]
    target = TASK / "calls" / identity
    assert not target.exists(), "An attempted call is never implicitly repeated"
    assert len(json.dumps(payload).encode()) <= 131072
    assert 1 <= payload["max_tokens"] <= 2048 and len(payload["messages"]) <= 24
    target.mkdir()
    write_once(target / "request.json", payload)
    before, began = cpu_seconds(), time.time()
    body = {
        "model": MODEL,
        "messages": payload["messages"],
        "stream": False,
        "keep_alive": -1,
        "options": {
            "seed": payload["seed"],
            "temperature": 0.2,
            "num_predict": payload["max_tokens"],
            "num_ctx": 8192,
            "num_thread": 2,
        },
    }
    if payload.get("format") is not None:
        body["format"] = payload["format"]
    try:
        response = http(
            "/api/chat", body, timeout=min(600, int(start["hard_deadline_epoch"] - began - 5))
        )
        result = {
            "status": "PASS_REAL_MODEL_RESPONSE",
            "call_id": identity,
            "lease_id": payload["lease_id"],
            "utc": stamp(),
            "model": MODEL,
            "model_digest": DIGEST,
            "response": response,
            "wall_seconds": time.time() - began,
            "container_cpu_seconds_delta": cpu_seconds() - before,
            "running_model_metadata": http("/api/ps"),
            "gpu_processes": gpu_state(),
            "paid_cost_usd": 0,
            "provider_fallback": False,
        }
        write_once(target / "response.json", result)
        return result
    except BaseException as error:
        write_once(
            target / "failure.json",
            {
                "status": "FAIL_REAL_MODEL_ATTEMPT",
                "utc": stamp(),
                "error": type(error).__name__ + ":" + str(error)[:1200],
                "wall_seconds": time.time() - began,
            },
        )
        raise


def stop_lease(payload):
    authority(execution=False)
    lease = TASK / "leases" / payload["lease_id"]
    start = read(lease / "start.json")
    assert not (lease / "stop.json").exists()
    value = owned()
    usage = cpu_seconds() if value["State"]["Running"] else None
    if value["State"]["Running"]:
        api("POST", "/containers/" + NAME + "/stop?t=5", timeout=15)
    value = owned()
    assert not value["State"]["Running"]
    result = {
        "status": "PASS_OWNED_LEASE_STOPPED",
        "utc": stamp(),
        "lease_id": payload["lease_id"],
        "allocated_wall_seconds": time.time() - start["allocated_start_epoch"],
        "retained_gpu_seconds": start["limits"]["gpu_cap_seconds"],
        "container_cpu_seconds_observed": usage,
        "final_container_state": value["State"],
        "gpu_processes_after_stop": gpu_state(),
    }
    write_once(lease / "final-container-inspection.json", value)
    write_once(lease / "stop.json", result)
    api("DELETE", "/containers/" + NAME)
    return result


def watchdog_probe(payload):
    authority()
    assert payload["lease_id"].startswith("guard-probe-")
    lease = TASK / "leases" / payload["lease_id"]
    start = read(lease / "start.json")
    observations = []
    if payload["kind"] == "cpu":
        execute(
            NAME, ["/bin/bash", "-c", "while :; do :; done & while :; do :; done"], detached=True
        )
    else:
        assert payload["kind"] == "wall"
    while time.time() < start["hard_deadline_epoch"] + 8:
        state = owned()["State"]
        if not state["Running"]:
            result = {
                "status": "PASS_WATCHDOG_ACTUALLY_TERMINATED_CONTAINER",
                "kind": payload["kind"],
                "elapsed_seconds": time.time() - start["allocated_start_epoch"],
                "state": state,
                "observations": observations,
                "model_calls": 0,
            }
            write_once(lease / "watchdog-probe.json", result)
            return result
        try:
            observations.append(
                {
                    "wall_seconds": time.time() - start["allocated_start_epoch"],
                    "cpu_seconds": cpu_seconds(),
                }
            )
        except (OSError, RuntimeError, AssertionError):
            pass
        time.sleep(1)
    raise RuntimeError("Watchdog did not terminate its owned container")


if __name__ == "__main__":
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[-3:])
    payload = json.load(sys.stdin)
    action = sys.argv[1]
    if action == "bootstrap":
        result = bootstrap(payload)
    else:
        with (TASK / "control.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if action == "start":
                result = start_lease(payload)
            elif action == "infer":
                result = infer(payload)
            elif action == "stop":
                result = stop_lease(payload)
            elif action == "watchdog-probe":
                result = watchdog_probe(payload)
            elif action == "verify-model-bytes":
                authority()
                out, _ = execute(
                    NAME,
                    [
                        "sha256sum",
                        "/models/blobs/sha256-4a1f36682cbeae8153f64a496ebcee10a23378abae631e905865fabfd3b21388",
                    ],
                    timeout=120,
                )
                actual = out.decode().split()[0]
                assert actual == "4a1f36682cbeae8153f64a496ebcee10a23378abae631e905865fabfd3b21388"
                result = {
                    "status": "PASS_FULL_EXISTING_MODEL_BLOB_HASH",
                    "sha256": actual,
                    "utc": stamp(),
                }
                write_once(TASK / "leases" / payload["lease_id"] / "model-blob-hash.json", result)
            else:
                raise ValueError("Unregistered action")
    print(json.dumps(result, ensure_ascii=False))
