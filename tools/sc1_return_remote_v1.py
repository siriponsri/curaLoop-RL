"""Archive and remove only verified LR-SC1-owned persistent paths after local reread."""
import hashlib
import http.client
import json
import os
import resource
import shutil
import socket
import sys
import tarfile
import threading
import time
import urllib.parse
from pathlib import Path

TASK = Path("/home/chaw/curaloop-tasks/lr-sc1-20261113-v1")
EXPORT = TASK.parent / "lr-sc1-20261113-v1-return.tar.gz"
MANIFEST = TASK.parent / "lr-sc1-20261113-v1-return-manifest.json"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1048576):
            h.update(chunk)
    return h.hexdigest()


def api(method, path):
    class Unix(http.client.HTTPConnection):
        def connect(self):
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(20)
            self.sock.connect("/var/run/docker.sock")
    c = Unix("localhost")
    c.request(method, path)
    r = c.getresponse()
    raw = r.read(4194305)
    c.close()
    if r.status >= 300 or len(raw) > 4194304:
        raise RuntimeError("Owned Docker query failed")
    return json.loads(raw) if raw else None


def owned_containers():
    query = urllib.parse.quote(json.dumps({"label": ["curaloop.task=lr-sc1-20261113-v1"]}))
    out = api("GET", "/containers/json?all=1&filters=" + query)
    for item in out:
        full = api("GET", "/containers/" + item["Id"] + "/json")
        if full["Config"]["Labels"].get("curaloop.task") != "lr-sc1-20261113-v1" or full["State"]["Running"]:
            raise RuntimeError("Unexpected active or foreign container; no deletion")
    return out


def files():
    if TASK.is_symlink() or TASK.resolve() != TASK or TASK.stat().st_uid != os.getuid():
        raise RuntimeError("Owned root identity changed")
    out = {}
    size = 0
    for path in sorted(TASK.rglob("*")):
        if path.is_symlink():
            raise RuntimeError("Unexpected symbolic link; do not archive/delete")
        if path.is_file():
            size += path.stat().st_size
            if size > 64 * 1024**3 or not path.resolve().is_relative_to(TASK):
                raise RuntimeError("Owned disk/path scope exceeded")
            out[path.relative_to(TASK).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha(path)}
    return out


def prepare():
    if EXPORT.exists() or MANIFEST.exists():
        raise FileExistsError("Preserve existing return")
    containers = owned_containers()
    manifest = {"schema": "curaloop.lr-sc1.remote-persistent-files.v1", "root": str(TASK),
                "files": files(), "owned_stopped_containers": [item["Id"] for item in containers]}
    with MANIFEST.open("x") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    with tarfile.open(EXPORT, "w:gz", compresslevel=1) as archive:
        for name in manifest["files"]:
            archive.add(TASK / name, arcname="files/" + name, recursive=False)
    return {"status": "PASS_OWNED_PERSISTENT_ARCHIVE_PREPARED", "archive": str(EXPORT), "manifest": str(MANIFEST),
            "archive_bytes": EXPORT.stat().st_size, "archive_sha256": sha(EXPORT), "manifest_sha256": sha(MANIFEST),
            "files": len(manifest["files"]), "uncompressed_bytes": sum(item["bytes"] for item in manifest["files"].values()),
            "remote_cleanup": "NOT_RUN_AWAIT_LOCAL_RETURN_REREAD"}


def cleanup(payload):
    if not payload.get("local_full_reread_passed") or sha(MANIFEST) != payload["manifest_sha256"] or sha(EXPORT) != payload["archive_sha256"]:
        raise RuntimeError("Exact locally returned archive identity required")
    manifest = json.loads(MANIFEST.read_text())
    if files() != manifest["files"]:
        raise RuntimeError("Remote files changed after return; preserve them")
    containers = owned_containers()
    if set(item["Id"] for item in containers) != set(manifest["owned_stopped_containers"]):
        raise RuntimeError("Owned container inventory changed")
    for item in containers:
        api("DELETE", "/containers/" + item["Id"] + "?v=0")
    # Every literal target has passed resolved ownership/path and returned-byte
    # checks above. This uses one Python filesystem API end-to-end.
    shutil.rmtree(TASK)
    EXPORT.unlink()
    MANIFEST.unlink()
    if TASK.exists() or EXPORT.exists() or MANIFEST.exists() or owned_containers():
        raise RuntimeError("Exact owned cleanup incomplete")
    return {"status": "PASS_EXACT_OWNED_REMOTE_CLEANUP", "removed_container_count": len(containers),
            "task_root_absent": True, "exports_absent": True, "other_projects_shared_models": "UNTOUCHED"}


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (500, 505))
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    os.sched_setaffinity(0, {max(os.sched_getaffinity(0))})
    os.nice(19)
    def stop():
        time.sleep(900)
        os._exit(124)
    threading.Thread(target=stop, daemon=True).start()
    payload = json.load(sys.stdin)
    result = prepare() if sys.argv[1] == "prepare" else cleanup(payload)
    result["measured_process_cpu_seconds"] = time.process_time()
    print(json.dumps(result))


if __name__ == "__main__":
    main()
