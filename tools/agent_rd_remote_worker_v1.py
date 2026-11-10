"""Owned CPU-only Ollama sandbox on dr-train; no model or shared service changes."""

import argparse
import fcntl
import hashlib
import http.client
import json
import os
import resource
import socket
import struct
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote, urlencode

TASK = Path.home() / "curaloop-tasks/agent-rd-20261110-v1"
NAME = "curaloop-agent-rd-20261110-v1"
MODEL = "hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M"
DIGEST = "ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b"
STAGES = {"admission": 6000, "development": 36000, "evaluation": 201600}
MODEL_MEMORY = 12348030976  # 11.5 GiB container + 0.5 GiB Python control process.
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
    connection.request(method, (API_VERSION or "") + path, raw, {"Content-Type": "application/json"})
    response = connection.getresponse()
    data = response.read()
    connection.close()
    if response.status >= 300:
        raise RuntimeError("Docker Unix API " + path + ": " + str(response.status) + " " + data[:1000].decode(errors="replace"))
    return json.loads(data) if data else None


def execute(name, command, data=None, detached=False, timeout=30):
    config = {"AttachStdin": data is not None, "AttachStdout": not detached, "AttachStderr": not detached,
              "Tty": False, "Cmd": list(command)}
    identity = api("POST", "/containers/" + name + "/exec", config)["Id"]
    if detached:
        api("POST", "/exec/" + identity + "/start", {"Detach": True, "Tty": False})
        return b"", b""
    # Docker's documented exec stream upgrade, without the Go CLI's large virtual heap.
    body = b'{"Detach":false,"Tty":false}'
    request = ("POST " + API_VERSION + "/exec/" + identity + "/start HTTP/1.1\r\nHost: localhost\r\nConnection: Upgrade\r\nUpgrade: tcp\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)) + "\r\n\r\n").encode() + body
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
        channel, size = stream[cursor], struct.unpack(">I", stream[cursor + 4:cursor + 8])[0]
        assert channel in (1, 2) and cursor + 8 + size <= len(stream)
        (output if channel == 1 else errors).extend(stream[cursor + 8:cursor + 8 + size])
        cursor += 8 + size
    status = api("GET", "/exec/" + identity + "/json")
    assert not status["Running"] and status["ExitCode"] == 0, errors.decode(errors="replace")[:1800]
    return bytes(output), bytes(errors)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path = Path(path)
    temporary = path.with_suffix(".next")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def docker(*args, **kwargs):
    text = kwargs.pop("text", False)
    timeout = kwargs.pop("timeout", 30)
    if args[:2] == ("ps", "-a"):
        rows = api("GET", "/containers/json?" + urlencode({"all": "1", "filters": json.dumps({"name": ["^/" + NAME + "$"]})}))
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
        return SimpleNamespace(stdout=out.decode() if text else out, stderr=err.decode() if text else err, returncode=0)
    else:
        raise ValueError("No generic Docker/shell fallback")
    assert not kwargs
    return SimpleNamespace(stdout=out.decode() if text else out, stderr="" if text else b"", returncode=0)


def cpu_seconds():
    value = docker("exec", NAME, "cat", "/sys/fs/cgroup/cpu.stat", text=True, timeout=10).stdout
    return int(dict(line.split() for line in value.splitlines())["usage_usec"]) / 1e6


def http(path, body=None, timeout=20):
    assert path in ("/api/tags", "/api/ps", "/api/chat", "/api/version")
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else b""
    request = (("POST" if body is not None else "GET") + " " + path + " HTTP/1.0\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: " + str(len(data)) + "\r\nConnection: close\r\n\r\n").encode() + data
    # Static shell program; all model/request text travels as data on stdin.
    result = docker("exec", "-i", NAME, "/bin/bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/11434; cat >&3; cat <&3", input=request, timeout=timeout)
    header, content = result.stdout.split(b"\r\n\r\n", 1)
    if not header.startswith(b"HTTP/1.0 200") and not header.startswith(b"HTTP/1.1 200"):
        raise RuntimeError("Owned model HTTP failure: " + content[:500].decode(errors="replace"))
    return json.loads(content)


def bootstrap(payload):
    assert set(payload) == {"release", "worker_source"}
    release = payload["release"]
    assert not TASK.exists() and not TASK.is_symlink(), "Never recreate an existing task root"
    assert release["remote_root"] == str(TASK) and release["owned_container"] == NAME
    assert release["model"] == MODEL and release["model_digest"] == DIGEST
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert not docker("ps", "-a", "--filter", "name=^/" + NAME + "$", "--format", "{{.ID}}", text=True, timeout=10).stdout.strip()
    model_root = Path("/data/CIE/cache/ollama/models")
    assert model_root.is_dir() and not model_root.is_symlink()
    allowed = sorted(os.sched_getaffinity(0))[-3:]
    assert len(allowed) == 3
    os.sched_setaffinity(0, {allowed[-1]})
    image = json.loads(docker("image", "inspect", "ollama/ollama:0.12.6", text=True, timeout=10).stdout)[0]
    TASK.mkdir(parents=True, exist_ok=False)
    (TASK / "calls").mkdir()
    (TASK / "worker.py").write_text(payload["worker_source"])
    write(TASK / "release.json", release)
    (TASK / "control").mkdir()
    deadline = int(datetime.fromisoformat(release["deadline_utc"]).timestamp()) - 15
    (TASK / "control/limit.txt").write_text(str(deadline) + " " + str((STAGES["admission"] - 30) * 1000000) + "\n")
    # Watch inside the same cgroup: its CPU is included in the hard envelope.
    (TASK / "control/watch.sh").write_text('''#!/bin/bash
while true; do
 read deadline cap < /control/limit.txt
 usage=0
 while read key value; do if [[ "$key" == "usage_usec" ]]; then usage=$value; fi; done < /sys/fs/cgroup/cpu.stat
 if (( $(date +%s) >= deadline || usage >= cap )); then
  kill -TERM 1
  sleep 2
  kill -KILL 1
  exit 124
 fi
 sleep 2
done
''')
    creation = {"Image": image["Id"], "Cmd": ["serve"], "Labels": {"curaloop.task": "agent-rd-20261110-v1"},
                "Env": ["OLLAMA_MODELS=/models", "OLLAMA_HOST=127.0.0.1:11434", "OLLAMA_NUM_PARALLEL=1",
                        "OLLAMA_MAX_LOADED_MODELS=1", "OLLAMA_CONTEXT_LENGTH=4096", "CUDA_VISIBLE_DEVICES=-1", "NVIDIA_VISIBLE_DEVICES=void"],
                "HostConfig": {"NetworkMode": "none", "CpusetCpus": ",".join(map(str, allowed)), "NanoCpus": 3000000000,
                    "Memory": MODEL_MEMORY, "MemorySwap": MODEL_MEMORY, "PidsLimit": 128, "ReadonlyRootfs": True,
                    "Tmpfs": {"/tmp": "rw,size=256m", "/root/.ollama": "rw,size=64m"},
                    "Mounts": [{"Type": "bind", "Source": str(model_root), "Target": "/models", "ReadOnly": True},
                               {"Type": "bind", "Source": str(TASK / "control"), "Target": "/control", "ReadOnly": True}]}}
    created = api("POST", "/containers/create?name=" + NAME, creation)["Id"]
    config = json.loads(docker("inspect", NAME, text=True, timeout=10).stdout)[0]
    h = config["HostConfig"]
    assert h["NanoCpus"] == 3000000000 and h["Memory"] == h["MemorySwap"] == MODEL_MEMORY
    assert h["NetworkMode"] == "none" and h["ReadonlyRootfs"] and not h.get("Privileged") and not h.get("DeviceRequests")
    assert h["CpusetCpus"] == ",".join(map(str, allowed))
    write(TASK / "container-admission.json", {"status": "PASS_ENFORCED_CPU_MEMORY_SWAP_NETWORK_READONLY", "utc": stamp(),
          "container_id": created, "image_id": image["Id"], "cpus": allowed,
          "nano_cpus": h["NanoCpus"], "memory": h["Memory"], "swap_total": h["MemorySwap"],
          "network": "none", "public_ports": [], "model_cache_readonly": True, "gpu_devices_requested": False,
          "parent_address_space_cap": 536870912, "docker_cli_used": False, "docker_api_version": API_VERSION,
          "aggregate_conservative_memory_upper_bytes": MODEL_MEMORY + 536870912})
    write(TASK / "phase.json", {"phase": "admission", "cpu_base": 0, "cpu_cap": STAGES["admission"]})
    docker("start", NAME, timeout=30)
    docker("exec", "-d", NAME, "/bin/bash", "/control/watch.sh", timeout=10)
    write(TASK / "watchdog.json", {"mechanism": "INSIDE_SAME_CPU_CGROUP", "started_utc": stamp(), "deadline_epoch": deadline})
    for _ in range(60):
        try:
            tags = http("/api/tags", timeout=2)
            break
        except (OSError, ValueError, RuntimeError, AssertionError):
            time.sleep(.5)
    else:
        raise RuntimeError("Owned Ollama did not become ready")
    assert any(m["name"] == MODEL and m["digest"] == DIGEST for m in tags["models"])
    receipt = {"status": "PASS_ISOLATED_RUNTIME_NO_INFERENCE", "version": http("/api/version"), "loaded": http("/api/ps"),
               "container_cpu_seconds": cpu_seconds(), "utc": stamp(), "new_model_download": False,
               "shared_services_modified": False, "model_digest_verified": True}
    write(TASK / "bootstrap-receipt.json", receipt)
    print(json.dumps(receipt))


def phase(name):
    assert name in ("development", "evaluation")
    release = json.loads((TASK / "release.json").read_text())
    previous = json.loads((TASK / "phase.json").read_text())
    assert (previous["phase"], name) in (("admission", "development"), ("development", "evaluation"))
    target = TASK / ("phase-" + name + ".json")
    assert not target.exists(), "Never reset a used phase allowance"
    base = cpu_seconds()
    value = {"phase": name, "cpu_base": base, "cpu_cap": STAGES[name], "utc": stamp()}
    write(target, value)
    write(TASK / "phase.json", value)
    deadline = int(datetime.fromisoformat(release["deadline_utc"]).timestamp()) - 15
    temporary = TASK / "control/limit.next"
    temporary.write_text(str(deadline) + " " + str(int((base + STAGES[name] - 30) * 1000000)) + "\n")
    os.replace(temporary, TASK / "control/limit.txt")
    print(json.dumps(value))


def infer(payload):
    release = json.loads((TASK / "release.json").read_text())
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert set(payload) == {"call_id", "messages", "seed", "max_tokens", "format"}
    call_id = payload["call_id"]
    assert isinstance(call_id, str) and 1 <= len(call_id) <= 100 and all(c.isalnum() or c in "-_" for c in call_id)
    assert type(payload["seed"]) is int and 0 <= payload["seed"] <= 4294967295
    assert type(payload["max_tokens"]) is int and 1 <= payload["max_tokens"] <= 768
    assert isinstance(payload["messages"], list) and len(payload["messages"]) <= 12
    assert len(json.dumps(payload).encode()) <= 131072
    path = TASK / "calls" / (call_id + ".json")
    expected = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    if path.exists():
        existing = json.loads(path.read_text())
        assert existing["request_sha256"] == expected
        print(json.dumps(existing, ensure_ascii=False))
        if existing["status"] != "PASS_PROVIDER_RESPONSE":
            raise SystemExit(1)
        return
    recorded_phase = json.loads((TASK / "phase.json").read_text())
    assert cpu_seconds() < recorded_phase["cpu_base"] + recorded_phase["cpu_cap"] - 30
    before = cpu_seconds()
    row = {"call_id": call_id, "request_sha256": expected, "request": payload, "started_utc": stamp(), "cpu_before": before,
           "status": "RUNNING", "model": MODEL, "model_digest": DIGEST}
    write(path, row)
    start = time.monotonic()
    try:
        result = http("/api/chat", {"model": MODEL, "messages": payload["messages"], "format": payload["format"],
                  "stream": False, "keep_alive": "120h", "options": {"seed": payload["seed"], "temperature": .2,
                  "num_predict": payload["max_tokens"], "num_ctx": 4096, "num_thread": 3, "num_gpu": 0}}, timeout=600)
        running = http("/api/ps")
        assert all(m.get("size_vram") == 0 for m in running.get("models", [])), "GPU memory must remain zero"
        row.update(status="PASS_PROVIDER_RESPONSE", response=result, running_model_metadata=running)
    except BaseException as exc:
        row.update(status="FAIL_PROVIDER", error=repr(exc))
    row.update(finished_utc=stamp(), wall_seconds=time.monotonic() - start, cpu_after=cpu_seconds())
    row["container_cpu_seconds"] = row["cpu_after"] - before
    write(path, row)
    print(json.dumps(row, ensure_ascii=False))
    if row["status"].startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))
    if "bootstrap" not in sys.argv:
        os.sched_setaffinity(0, {sorted(os.sched_getaffinity(0))[-1]})
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("bootstrap", "status", "infer", "development", "evaluation"))
    args = parser.parse_args()
    if args.action == "bootstrap":
        bootstrap(json.load(sys.stdin))
    else:
        resource.setrlimit(resource.RLIMIT_CPU, (2, 3))
        with (TASK / "host-client.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            counter_path = TASK / "host-client-cpu.json"
            counter = json.loads(counter_path.read_text()) if counter_path.exists() else {
                "accounted_cpu_seconds": 60, "historical_probe_bootstrap_upper_seconds": 60,
                "hard_cap_seconds": 600, "inflight": None, "abrupt_attempts_charged": 0}
            if counter["inflight"]:
                counter["accounted_cpu_seconds"] += 3
                counter["abrupt_attempts_charged"] += 1
            assert counter["accounted_cpu_seconds"] + 3 <= 600, "Remote client CPU envelope exhausted"
            counter["inflight"] = {"pid": os.getpid(), "utc": stamp(), "reserved_cpu_seconds": 3}
            write(counter_path, counter)
            try:
                if args.action in ("development", "evaluation"):
                    phase(args.action)
                elif args.action == "infer":
                    infer(json.load(sys.stdin))
                else:
                    print(json.dumps({"container_cpu_seconds": cpu_seconds(), "phase": json.loads((TASK / "phase.json").read_text()),
                                      "admission": json.loads((TASK / "container-admission.json").read_text())}))
            finally:
                counter["accounted_cpu_seconds"] += sum(resource.getrusage(resource.RUSAGE_SELF)[:2])
                counter["inflight"] = None
                write(counter_path, counter)
