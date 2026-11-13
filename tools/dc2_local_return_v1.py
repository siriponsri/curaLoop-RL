"""Return all owned persistent file bytes and reread before separate exact cleanup."""
import base64
import json
import shutil
import subprocess
import sys
import tarfile

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write

WORKER = ROOT / "tools/dc2_local_return_worker_v1.py"
SSH = ["rtk", "proxy", "ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "100.77.149.83"]


def reserve(identity, cpu):
    release, ledger = authority()
    assert identity not in ledger["bookings"]
    ledger["retained_cpu_seconds"]["return_delivery"] += cpu
    assert ledger["retained_cpu_seconds"]["return_delivery"] <= ledger["stage_cpu_caps_seconds"]["return_delivery"]
    assert sum(ledger["retained_cpu_seconds"].values()) <= release["cpu_cap_seconds"]
    ledger["bookings"][identity] = {"status": "RESERVED", "host": "dr-train-return", "bucket": "return_delivery", "cpu_cap": cpu, "gpu_cap": 0}
    save(ledger)


def remote(action, **extra):
    source = WORKER.read_bytes()
    program = base64.b64encode(source).decode()
    payload = {"action": action, "source_base64": program, "source_sha256": sha(WORKER), **extra}
    identity = "remote-persistent-" + action + "-v1"
    reserve(identity, 600 if action == "prepare" else 180)
    result = subprocess.run([*SSH, "python3 -c \"import base64;exec(compile(base64.b64decode('" + program + "'),'<retained-return-worker-v1>','exec'))\""], input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True, timeout=1000 if action == "prepare" else 650)
    write(TASK / (identity + "-transport.json"), {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][identity]["status"] = "PASS" if result.returncode == 0 else "FAIL"
    save(ledger)
    assert result.returncode == 0, result.stderr[-1800:]
    return json.loads(result.stdout)


def prepare():
    output = TASK / "remote-return-v1"
    output.mkdir(exist_ok=False)
    receipt = remote("prepare")
    write(output / "remote-archive-receipt.json", receipt)
    archive_path = output / "owned-persistent-files.tar.gz"
    result = subprocess.run(["rtk", "proxy", "scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "100.77.149.83:" + receipt["archive"], str(archive_path)], capture_output=True, text=True, timeout=900)
    write(output / "download-receipt.json", {"returncode": result.returncode, "stderr": result.stderr})
    assert result.returncode == 0, result.stderr
    assert archive_path.stat().st_size == receipt["archive_bytes"] and sha(archive_path) == receipt["archive_sha256"]
    restored = output / "files"
    restored.mkdir()
    with tarfile.open(archive_path, mode="r:gz") as archive:
        first = archive.next()
        assert first.name == "return-manifest.json" and first.isfile() and first.size < 32*1024**2
        data = archive.extractfile(first).read()
        manifest = json.loads(data)
        with (output / "return-manifest.json").open("xb") as stream:
            stream.write(data)
        assert sha(output / "return-manifest.json") == receipt["manifest_sha256"]
        seen = set()
        for member in archive:
            if member.name == "return-manifest.json":
                continue
            assert member.isfile() and member.name.startswith("payload/")
            relative = member.name[len("payload/"):]
            assert relative in manifest["files"] and relative not in seen
            target = restored / relative
            assert target.resolve().is_relative_to(restored.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream, archive.extractfile(member) as incoming:
                shutil.copyfileobj(incoming, stream, 1024**2)
            identity = manifest["files"][relative]
            assert target.stat().st_size == identity["bytes"]
            # Fresh on-disk reread, not just transport or streaming checksums.
            assert sha(target) == identity["sha256"], relative
            seen.add(relative)
    assert len(seen) == receipt["file_count"] == len(manifest["files"])
    result = {**receipt, "status": "PASS_ALL_OWNED_PERSISTENT_FILE_BYTES_RETURNED_AND_REREAD", "local_all_files_reread": True, "local_private_path": str(output), "symlinks": "Targets retained as manifest metadata; not followed or reconstructed on Windows", "ephemeral_tmpfs": "Not persistent; not claimed returned", "cleanup": "NOT_RUN_YET"}
    write(PUBLIC / "full-remote-return-v1.json", result)
    print(json.dumps(result))


def cleanup():
    receipt = read(PUBLIC / "full-remote-return-v1.json")
    assert receipt["local_all_files_reread"]
    output = TASK / "remote-return-v1"
    assert sha(output / "owned-persistent-files.tar.gz") == receipt["archive_sha256"]
    manifest = read(output / "return-manifest.json")
    assert sha(output / "return-manifest.json") == receipt["manifest_sha256"]
    for relative, identity in manifest["files"].items():
        assert sha(output / "files" / relative) == identity["sha256"]
    result = remote("cleanup", archive_sha256=receipt["archive_sha256"], manifest_sha256=receipt["manifest_sha256"], local_all_files_reread=True)
    fresh = subprocess.run([*SSH, "test ! -e /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1 && test ! -e /home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1-return-v1.tar.gz && printf 'PASS_FRESH_OWNED_ABSENCE'"], capture_output=True, text=True, timeout=30)
    assert fresh.returncode == 0 and fresh.stdout == "PASS_FRESH_OWNED_ABSENCE"
    write(PUBLIC / "owned-cleanup-v1.json", {**result, "fresh_independent_ssh_absence_observation": fresh.stdout, "full_return_receipt_sha256": sha(PUBLIC / "full-remote-return-v1.json")})
    print(json.dumps(result))


if __name__ == "__main__":
    assert len(sys.argv) == 2 and sys.argv[1] in ("prepare", "cleanup")
    prepare() if sys.argv[1] == "prepare" else cleanup()
