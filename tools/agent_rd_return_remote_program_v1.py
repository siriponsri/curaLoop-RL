"""Linux-only exact owned export/cleanup. Never touches shared model caches.

Invoked only after locked execution ends, by agent_rd_return_v1.py. Every file
is returned and reread before cleanup; resource reservations are never reset.
"""

import hashlib
import http.client
import json
import os
import resource
import shutil
import socket
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path("/home/chaw/curaloop-tasks/agent-rd-20261110-v1")
ARCHIVE = Path("/home/chaw/curaloop-tasks/agent-rd-20261110-v1-return-v1.tar.gz")
NAME = "curaloop-agent-rd-20261110-v1"
WORKER_SHA = "950a8ce694b5b993d0d4c9396fa4fdb96c5d0941f8f587280a12bb48d7983e8d"
API = None


class Connection(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect("/var/run/docker.sock")


def docker(method, path, *, raw=False, allowed=(200, 201, 204), timeout=35):
    global API
    if API is None and path != "/version":
        API = "/v" + docker("GET", "/version")["ApiVersion"]
    connection = Connection("localhost", timeout=timeout)
    connection.request(method, (API or "") + path)
    response = connection.getresponse()
    data = response.read(16 * 1024**2 + 1)
    connection.close()
    assert len(data) <= 16 * 1024**2, "Control response exceeds the bounded return buffer"
    assert response.status in allowed, f"Owned Docker operation failed: {response.status} {path}"
    return data if raw else json.loads(data) if data else None


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            value.update(block)
    return value.hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def validate_root():
    assert ROOT.is_absolute() and ROOT.parent == Path("/home/chaw/curaloop-tasks")
    assert ROOT.is_dir() and not ROOT.is_symlink() and ROOT.resolve() == ROOT
    assert ARCHIVE.parent == ROOT.parent and ARCHIVE.name == ROOT.name + "-return-v1.tar.gz"
    assert not ARCHIVE.is_symlink()
    assert digest(ROOT / "worker-v2.py") == WORKER_SHA
    release = json.loads((ROOT / "release.json").read_text())
    assert release["remote_root"] == str(ROOT) and release["owned_container"] == NAME
    assert release["model_digest"] == "ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b"
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    return release


def shared_inventory():
    # Read-only names/IDs/state only. No shared logs, env or configuration writes.
    rows = docker("GET", "/containers/json?all=1")
    return [{"id": row["Id"], "names": row["Names"], "state": row["State"]}
            for row in rows if any(n in ("/ollama-podi", "/ollama-labclear") for n in row["Names"])]


def owned_container(expected_id):
    assert isinstance(expected_id, str) and len(expected_id) == 64 and all(c in "0123456789abcdef" for c in expected_id)
    config = docker("GET", "/containers/" + expected_id + "/json")
    assert config["Id"] == expected_id and config["Name"] == "/" + NAME
    assert config["Config"]["Labels"]["curaloop.task"] == ROOT.name
    return config


def file_rows():
    rows = []
    for path in sorted(ROOT.rglob("*")):
        assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
        if path.is_dir():
            assert not path.is_mount()
            continue
        assert path.is_file() and path.stat().st_nlink == 1
        if path == ROOT / "return-v1/manifest.json":
            continue
        rows.append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    assert rows and sum(r["bytes"] for r in rows) < 1024**3
    return rows


def export(payload):
    validate_root()
    assert payload["locked_execution_finalized"] is True
    assert not ARCHIVE.exists()
    target = ROOT / "return-v1"
    target.mkdir(exist_ok=False)
    # Preserve this exact executed source as part of the complete return.
    (target / "executed-return-program.py").write_text(payload["source"], encoding="utf-8", newline="\n")
    before = shared_inventory()
    container = owned_container(payload["container_id"])
    write(target / "container-before-stop.json", container)
    stats = docker("GET", "/containers/" + container["Id"] + "/stats?stream=false", timeout=20) if container["State"]["Running"] else None
    write(target / "container-stats-before-stop.json", {"stats": stats, "scope": "Observed before exact owned stop; full phase reservations retained"})
    if container["State"]["Running"]:
        docker("POST", "/containers/" + container["Id"] + "/stop?t=15", allowed=(204, 304))
    stopped = owned_container(payload["container_id"])
    assert not stopped["State"]["Running"]
    write(target / "container-after-stop.json", stopped)
    logs = docker("GET", "/containers/" + container["Id"] + "/logs?" + urlencode({"stdout": 1, "stderr": 1, "timestamps": 1}), raw=True)
    (target / "owned-container-logs.docker-stream").write_bytes(logs)
    after = shared_inventory()
    assert before == after
    write(target / "shared-service-readonly-inventory.json", {"before": before, "after": after, "shared_services_modified": False})
    rows = file_rows()
    manifest = {"schema": "curaloop.agent-rd.private-return.v1", "remote_root": str(ROOT),
                "container_id": container["Id"], "worker_v2_sha256": WORKER_SHA,
                "utc": datetime.now(timezone.utc).isoformat(), "files": rows,
                "bytes": sum(r["bytes"] for r in rows), "model_weights_included": False,
                "manifest_self_excluded": True}
    write(target / "manifest.json", manifest)
    with tarfile.open(ARCHIVE, "x:gz", compresslevel=1) as archive:
        for row in rows:
            archive.add(ROOT / row["path"], arcname=row["path"], recursive=False)
        archive.add(target / "manifest.json", arcname="return-v1/manifest.json", recursive=False)
    assert ARCHIVE.stat().st_size < 1024**3
    return {"status": "EXPORTED_ALL_OWNED_FILES_CONTAINER_STOPPED_NOT_DELETED", "archive": str(ARCHIVE),
            "archive_sha256": digest(ARCHIVE), "archive_bytes": ARCHIVE.stat().st_size,
            "manifest_sha256": digest(target / "manifest.json"), "file_count_excluding_manifest": len(rows),
            "owned_container_id": container["Id"], "shared_services_modified": False,
            "all_code_and_data_deletion": "NOT_RUN_AWAIT_LOCAL_FULL_REREAD"}


def cleanup(payload):
    validate_root()
    assert payload["local_full_reread_pass"] is True
    assert ARCHIVE.is_file() and digest(ARCHIVE) == payload["archive_sha256"]
    manifest_path = ROOT / "return-v1/manifest.json"
    assert digest(manifest_path) == payload["manifest_sha256"]
    manifest = json.loads(manifest_path.read_text())
    assert file_rows() == manifest["files"], "Remote contents changed after complete return"
    before = shared_inventory()
    container = owned_container(payload["container_id"])
    assert not container["State"]["Running"]
    docker("DELETE", "/containers/" + container["Id"], allowed=(204,))
    # The resolved exact absolute roots were checked above. No computed parent deletion.
    shutil.rmtree(ROOT)
    ARCHIVE.unlink()
    assert not ROOT.exists() and not ARCHIVE.exists()
    rows = docker("GET", "/containers/json?all=1")
    assert not any(r["Id"] == container["Id"] or "/" + NAME in r["Names"] for r in rows)
    after = shared_inventory()
    assert before == after
    return {"status": "PASS_EXACT_OWNED_CLEANUP_AFTER_VERIFIED_RETURN", "remote_root_absent": True,
            "owned_export_absent": True, "owned_container_absent": True,
            "shared_services_modified": False, "shared_inventory_unchanged": True,
            "reused_model_cache_deleted": False, "utc": datetime.now(timezone.utc).isoformat()}


def absence(_payload):
    assert not ROOT.exists() and not ARCHIVE.exists()
    rows = docker("GET", "/containers/json?all=1")
    assert not any("/" + NAME in r["Names"] for r in rows)
    return {"status": "PASS_FRESH_OWNED_ABSENCE", "remote_root_absent": True,
            "owned_export_absent": True, "owned_container_absent": True,
            "reused_model_cache_deleted": False, "utc": datetime.now(timezone.utc).isoformat()}


def stream_archive(payload):
    validate_root()
    assert ARCHIVE.is_file() and not ARCHIVE.is_symlink()
    assert digest(ARCHIVE) == payload["archive_sha256"]
    assert ARCHIVE.stat().st_size < 1024**3
    with ARCHIVE.open("rb") as source:
        shutil.copyfileobj(source, sys.stdout.buffer, length=65536)
    sys.stdout.buffer.flush()
    result = {"status": "STREAMED_OWNED_ARCHIVE", "bytes": ARCHIVE.stat().st_size,
              "archive_sha256": payload["archive_sha256"],
              "measured_host_cpu_seconds": sum(resource.getrusage(resource.RUSAGE_SELF)[:2]),
              "host_cpu_hard_cap_seconds": 90, "cpu_affinity": sorted(os.sched_getaffinity(0))}
    print("AGENT_RD_RETURN_STREAM_RECEIPT " + json.dumps(result), file=sys.stderr)


def main():
    # Same admitted CPU set as the model; no new core or system permission.
    allowed = os.sched_getaffinity(0) & {69, 70, 71}
    assert allowed
    os.sched_setaffinity(0, {max(allowed)})
    resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))
    resource.setrlimit(resource.RLIMIT_CPU, (90, 90))
    os.nice(19)
    payload = json.load(sys.stdin)
    assert payload["action"] in ("export", "stream", "cleanup", "absence")
    if payload["action"] == "stream":
        stream_archive(payload)
        return
    result = {"export": export, "cleanup": cleanup, "absence": absence}[payload["action"]](payload)
    result["measured_host_cpu_seconds"] = sum(resource.getrusage(resource.RUSAGE_SELF)[:2])
    result["host_cpu_hard_cap_seconds"] = 90
    result["cpu_affinity"] = sorted(os.sched_getaffinity(0))
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
