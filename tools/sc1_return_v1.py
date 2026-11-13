"""Return all owned bytes, independently reread them, then request exact cleanup."""
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath
from tools.sc1_control_v1 import ACCOUNT, PUBLIC, RELEASE, ROOT, digest, write_new
from tools.sc1_job_v1 import save
from tools.sc1_native_transport_v1 import SSH, REMOTE

OUT = ACCOUNT / "remote-return-v1"


def reserve(identity, cpu):
    path = ACCOUNT / "ledger.json"
    ledger = json.loads(path.read_text())
    if ledger.get("active_remote_jobs") or any(item["id"] == identity for item in ledger["reservations"]):
        raise RuntimeError("Remote attempt already exists or active")
    cap = json.loads(RELEASE.read_text())["stage_caps_seconds"]["analysis_delivery"]["cpu"]
    if sum(r["cpu_seconds"] for r in ledger["reservations"] if r["stage"] == "analysis_delivery") + cpu > cap:
        raise RuntimeError("Return allowance unavailable")
    ledger["reservations"].append({"id": identity, "stage": "analysis_delivery", "cpu_seconds": cpu,
                                   "gpu_allocated_seconds": 0, "host": "dr-train", "status": "RESERVED"})
    ledger["active_remote_jobs"] = [identity]
    save(path, ledger)


def settle(identity, result):
    path = OUT / (identity + ".json")
    write_new(path, result)
    ledger_path = ACCOUNT / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    for row in ledger["reservations"]:
        if row["id"] == identity:
            row.update(status=result["status"], receipt_sha256=digest(path),
                       measured_process_cpu_seconds=result.get("measured_process_cpu_seconds"))
    ledger["active_remote_jobs"] = []
    save(ledger_path, ledger)


def call(action, payload):
    p = subprocess.run(SSH + [f"python3 {REMOTE}/return-v1.py {action}"], input=json.dumps(payload), capture_output=True, text=True, timeout=930)
    if p.returncode:
        raise RuntimeError("Owned return/cleanup failed: " + p.stderr[-1600:])
    return json.loads(p.stdout)


def receive():
    OUT.mkdir(exist_ok=False)
    reserve("return-prepare-remote-v1", 520)
    source = ROOT / "tools/sc1_return_remote_v1.py"
    p = subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", str(source), f"100.77.149.83:{REMOTE}/return-v1.py"], capture_output=True, text=True, timeout=45)
    if p.returncode:
        raise RuntimeError("Return worker upload failed")
    receipt = call("prepare", {})
    settle("return-prepare-remote-v1", receipt)
    for key, filename in (("archive", "owned-persistent.tar.gz"), ("manifest", "manifest.json")):
        p = subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "100.77.149.83:" + receipt[key], str(OUT / filename)], capture_output=True, text=True, timeout=600)
        if p.returncode:
            raise RuntimeError("Owned archive/manifest download failed: " + p.stderr[-1000:])
    archive = OUT / "owned-persistent.tar.gz"
    manifest_path = OUT / "manifest.json"
    if archive.stat().st_size != receipt["archive_bytes"] or digest(archive) != receipt["archive_sha256"] or digest(manifest_path) != receipt["manifest_sha256"]:
        raise RuntimeError("Returned source transport identity failed")
    expected = json.loads(manifest_path.read_text())["files"]
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            name = PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or not name.parts or name.parts[0] != "files" or ".." in name.parts:
                raise RuntimeError("Unsafe returned archive member")
            relative = PurePosixPath(*name.parts[1:]).as_posix()
            if relative in seen or relative not in expected or member.size != expected[relative]["bytes"]:
                raise RuntimeError("Unexpected returned file identity")
            target = OUT.joinpath(*name.parts).resolve()
            if not target.is_relative_to((OUT / "files").resolve()):
                raise RuntimeError("Returned target escaped owned folder")
            target.parent.mkdir(parents=True, exist_ok=True)
            h = hashlib.sha256()
            with bundle.extractfile(member) as source, target.open("xb") as output:
                while chunk := source.read(1048576):
                    h.update(chunk)
                    output.write(chunk)
            if h.hexdigest() != expected[relative]["sha256"]:
                raise RuntimeError("Extracted bytes differ")
            seen.add(relative)
    if seen != set(expected):
        raise RuntimeError("Incomplete owned file set")
    for name, identity in expected.items():
        target = OUT / "files" / name
        if target.stat().st_size != identity["bytes"] or digest(target) != identity["sha256"]:
            raise RuntimeError("Independent local reread failed")
    result = {"status": "PASS_FULL_OWNED_RETURN_AND_INDEPENDENT_REREAD", "file_count": len(expected),
              "file_bytes": sum(x["bytes"] for x in expected.values()), "archive_bytes": archive.stat().st_size,
              "archive_sha256": receipt["archive_sha256"], "manifest_sha256": receipt["manifest_sha256"],
              "local_full_reread_passed": True, "remote_cleanup": "NOT_RUN_UNTIL_VERIFICATION"}
    write_new(OUT / "reread-v1.json", result)
    write_new(PUBLIC / "remote-return-v1.json", result)
    print(json.dumps(result))


def cleanup():
    receipt = json.loads((OUT / "reread-v1.json").read_text())
    if receipt["status"] != "PASS_FULL_OWNED_RETURN_AND_INDEPENDENT_REREAD":
        raise RuntimeError("Local full reread required")
    reserve("return-cleanup-remote-v1", 520)
    result = call("cleanup", receipt)
    settle("return-cleanup-remote-v1", result)
    write_new(PUBLIC / "remote-cleanup-v1.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    receive() if sys.argv[1] == "receive" else cleanup()
