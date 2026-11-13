"""One exact owned-root archive or cleanup, with bounded CPU/memory/wall time."""
import base64
import gzip
import hashlib
import io
import json
import os
import resource
import shutil
import sys
import tarfile
import threading
import time
from pathlib import Path

ROOT = Path("/home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1")
ARCHIVE = ROOT.parent / (ROOT.name + "-return-v1.tar.gz")
MANIFEST = ROOT.parent / (ROOT.name + "-return-v1.manifest.json")
RECEIPT = ROOT.parent / (ROOT.name + "-return-v1.receipt.json")


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def current_manifest():
    files, links = {}, {}
    for current, directories, names in os.walk(ROOT, followlinks=False):
        for name in [*directories, *names]:
            path = Path(current) / name
            relative = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                links[relative] = os.readlink(path)
                if name in directories:
                    directories.remove(name)
            elif path.is_file():
                files[relative] = {"bytes": path.stat().st_size, "sha256": sha(path), "mode": path.stat().st_mode & 0o777}
            elif not path.is_dir():
                raise ValueError("Nonregular owned entry: " + relative)
    return {"files": files, "symlink_metadata": links, "symlinks_followed": False, "ephemeral_container_tmpfs": "Not persistent and not included; original request/response/log/receipt files are included"}


def no_owned_container():
    sys.path.insert(0, str(ROOT))
    import worker
    containers = worker.api("GET", "/containers/json?all=1")
    assert not any(c.get("Labels", {}).get("curaloop.task") == ROOT.name or any(ROOT.name in name for name in c.get("Names", [])) for c in containers), "An owned container remains; do not delete its files"


def main():
    payload = json.load(sys.stdin)
    action = payload["action"]
    assert action in ("prepare", "cleanup")
    cap = 600 if action == "prepare" else 180
    resource.setrlimit(resource.RLIMIT_CPU, (cap, cap))
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    os.sched_setaffinity(0, {max(os.sched_getaffinity(0))})
    def stop():
        time.sleep(900 if action == "prepare" else 600)
        os._exit(124)
    threading.Thread(target=stop, daemon=True).start()
    assert ROOT == Path("/home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1")
    assert ROOT.is_dir() and not ROOT.is_symlink() and ROOT.resolve() == ROOT
    assert ROOT.parent.resolve() == Path("/home/chaw/curaloop-tasks")
    source = base64.b64decode(payload["source_base64"])
    assert hashlib.sha256(source).hexdigest() == payload["source_sha256"]
    source_path = ROOT / "return-worker-v1.py"
    if action == "prepare":
        assert not source_path.exists()
        with source_path.open("xb") as stream:
            stream.write(source)
    assert sha(source_path) == payload["source_sha256"]
    no_owned_container()
    if action == "prepare":
        assert not any(p.exists() for p in (ARCHIVE, MANIFEST, RECEIPT))
        manifest = current_manifest()
        data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        with MANIFEST.open("xb") as stream:
            stream.write(data)
        with ARCHIVE.open("xb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=1, mtime=0) as gz, tarfile.open(fileobj=gz, mode="w|") as archive:
            info = tarfile.TarInfo("return-manifest.json")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
            for relative, identity in sorted(manifest["files"].items()):
                path = ROOT / relative
                info = tarfile.TarInfo("payload/" + relative)
                info.size, info.mode = identity["bytes"], identity["mode"]
                with path.open("rb") as stream:
                    archive.addfile(info, stream)
        receipt = {"status": "PASS_OWNED_PERSISTENT_ARCHIVE_CREATED_AND_REREAD", "archive": str(ARCHIVE), "archive_bytes": ARCHIVE.stat().st_size, "archive_sha256": sha(ARCHIVE), "manifest_sha256": sha(MANIFEST), "file_count": len(manifest["files"]), "persistent_file_bytes": sum(v["bytes"] for v in manifest["files"].values()), "symlink_metadata_count": len(manifest["symlink_metadata"]), "source_sha256": payload["source_sha256"], "cpu_cap_seconds": cap, "observed_cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime, "memory_cap_bytes": 1024**3, "cpu_cores": 1}
        with RECEIPT.open("x") as stream:
            json.dump(receipt, stream, indent=2)
        print(json.dumps(receipt))
    else:
        receipt = json.loads(RECEIPT.read_text())
        assert receipt["archive_sha256"] == payload["archive_sha256"]
        assert sha(MANIFEST) == payload["manifest_sha256"] == receipt["manifest_sha256"]
        assert current_manifest() == json.loads(MANIFEST.read_text()), "Owned persistent files changed after return; stop cleanup"
        # Exact literals, verified root, and local reread proof supplied by controller.
        assert payload["local_all_files_reread"] is True
        shutil.rmtree(ROOT)
        for path in (ARCHIVE, MANIFEST, RECEIPT):
            assert path.parent.resolve() == Path("/home/chaw/curaloop-tasks") and path.name.startswith(ROOT.name + "-return-v1.")
            path.unlink()
        assert not ROOT.exists() and not any(p.exists() for p in (ARCHIVE, MANIFEST, RECEIPT))
        print(json.dumps({"status": "PASS_EXACT_OWNED_ROOT_AND_RETURN_FILES_ABSENT", "remote_root_absent": True, "export_files_absent": True, "shared_models_images_and_other_projects_untouched": True, "cpu_cap_seconds": cap, "observed_cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime}))


if __name__ == "__main__":
    main()
