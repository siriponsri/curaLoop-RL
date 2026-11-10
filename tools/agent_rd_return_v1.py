"""Return every owned remote byte, reread, then delete only verified owned roots.

Run each named stage once under agent_rd_admin_v1.py after the supervisor ends.
An interrupted stage is evidence, not authority to overwrite or reset it.
"""

import base64
import json
import subprocess
import sys
import tarfile
from pathlib import PurePosixPath

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, reserve, save, sha, write

WORK = TASK / "remote-return-v1"
SOURCE = ROOT / "tools/agent_rd_return_remote_program_v1.py"
ARCHIVE = WORK / "all-owned-remote-files-v1.tar.gz"


def require_finalized():
    authority()
    ledger = read(TASK / "ledger.json")
    assert ledger["bookings"]["locked-supervisor-v1"]["status"] != "RESERVED"
    assert read(TASK / "supervisor-v1/completion.json")["evaluation_exit_code"] == 0
    progress = read(PUBLIC / "locked-progress-v1.json")
    assert progress["status"] in ("COMPLETE", "INCOMPLETE") and progress["stop_reason"] != "OPERATIONAL_BATCH_BOUNDARY"
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    return progress


def container_id():
    invocations = sorted((TASK / "locked-evaluation-v1").glob("invocation-*.json"))
    assert invocations
    identities = {read(p)["phase"]["admission"]["container_id"] for p in invocations}
    assert len(identities) == 1
    return identities.pop()


def remote(action, extra=None, binary=None):
    require_finalized()
    WORK.mkdir(exist_ok=True)
    command_source = SOURCE.read_text(encoding="utf-8")
    encoded = base64.b64encode(command_source.encode()).decode()
    remote_command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
    command = ["rtk", "proxy", "ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
               "-o", "ConnectTimeout=15", "100.77.149.83", remote_command]
    name = "remote-return-" + action + "-v1"
    payload = {"action": action, "container_id": container_id(), **(extra or {})}
    if action == "export":
        payload.update(locked_execution_finalized=True, source=command_source)
    reserve(name, "return_delivery", 90, "remote-return", ["fixed_owned_return_program", action, sha(SOURCE)])
    result = None
    try:
        if binary is None:
            result = subprocess.run(command, input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8", timeout=300)
            (WORK / (action + ".stdout.txt")).write_text(result.stdout, encoding="utf-8")
            (WORK / (action + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
            assert result.returncode == 0, result.stderr[-1800:]
            receipt = json.loads(result.stdout)
        else:
            assert not binary.exists()
            with binary.open("xb") as output:
                result = subprocess.run(command, input=json.dumps(payload).encode(), stdout=output, stderr=subprocess.PIPE, timeout=600)
            errors = result.stderr.decode("utf-8", errors="replace")
            (WORK / (action + ".stderr.txt")).write_text(errors, encoding="utf-8")
            assert result.returncode == 0, errors[-1800:]
            receipt_lines = [line.removeprefix("AGENT_RD_RETURN_STREAM_RECEIPT ") for line in errors.splitlines()
                             if line.startswith("AGENT_RD_RETURN_STREAM_RECEIPT ")]
            assert len(receipt_lines) == 1
            receipt = json.loads(receipt_lines[0])
        write(WORK / (action + "-receipt-v1.json"), receipt, True)
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][name].update(status="PASS", measured_cpu_seconds=receipt["measured_host_cpu_seconds"],
                                        receipt_sha256=sha(WORK / (action + "-receipt-v1.json")))
        save(ledger)
        return receipt
    except BaseException:
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][name].update(status="FAIL", exit_code=result.returncode if result else None,
                                        measured_cpu_seconds=None, retained_unknown_cost_seconds=90)
        save(ledger)
        raise


def export():
    assert not WORK.exists(), "Preserve prior return stages instead of overwriting"
    receipt = remote("export")
    assert receipt["status"] == "EXPORTED_ALL_OWNED_FILES_CONTAINER_STOPPED_NOT_DELETED"
    print(json.dumps(receipt))


def fetch():
    exported = read(WORK / "export-receipt-v1.json")
    streamed = remote("stream", {"archive_sha256": exported["archive_sha256"]}, binary=ARCHIVE)
    assert ARCHIVE.stat().st_size == exported["archive_bytes"] == streamed["bytes"]
    assert sha(ARCHIVE) == exported["archive_sha256"]
    print(json.dumps({"status": "PASS_ARCHIVE_RETURN_IDENTITY", "bytes": ARCHIVE.stat().st_size}))


def verify():
    require_finalized()
    exported = read(WORK / "export-receipt-v1.json")
    assert sha(ARCHIVE) == exported["archive_sha256"]
    destination = WORK / "files"
    destination.mkdir(exist_ok=False)
    names = set()
    total = 0
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            assert not name.is_absolute() and ".." not in name.parts and member.isfile()
            assert member.name not in names and not member.issym() and not member.islnk()
            names.add(member.name)
            total += member.size
            assert total < 1024**3
            target = destination.joinpath(*name.parts)
            assert target.resolve().is_relative_to(destination.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            assert source is not None
            with target.open("xb") as output:
                while block := source.read(1024**2):
                    output.write(block)
            assert target.stat().st_size == member.size
    manifest_path = destination / "return-v1/manifest.json"
    assert sha(manifest_path) == exported["manifest_sha256"]
    manifest = read(manifest_path)
    assert names == {r["path"] for r in manifest["files"]} | {"return-v1/manifest.json"}
    assert len(manifest["files"]) == exported["file_count_excluding_manifest"]
    for row in manifest["files"]:
        path = destination / row["path"]
        assert path.stat().st_size == row["bytes"] and sha(path) == row["sha256"]
    freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    assert sha(destination / "worker-v2.py") == freeze["executed_remote_worker_sha256"]
    assert (destination / "worker.py").is_file()
    matched_calls = 0
    for path in sorted((PUBLIC / "locked-results-v1").glob("*-trace.json")):
        trace = read(path)["payload"]
        for call in trace["calls"]:
            if call["status"] != "PASS":
                continue
            remote_call = read(destination / "calls" / (call["call_id"] + ".json"))
            assert remote_call == call["receipt"], "Returned provider file differs from the frozen actual trace"
            assert remote_call["model_digest"] == freeze["model_digest"]
            assert all(m.get("size_vram") == 0 for m in remote_call["running_model_metadata"]["models"])
            matched_calls += 1
    status_counts = {}
    for path in (destination / "calls").glob("*.json"):
        state = read(path)["status"]
        status_counts[state] = status_counts.get(state, 0) + 1
    receipt = {"status": "PASS_COMPLETE_RETURN_AND_FULL_FILE_REREAD", "files_reread": len(names),
               "content_bytes": total, "archive_sha256": sha(ARCHIVE), "manifest_sha256": sha(manifest_path),
               "matched_locked_successful_call_files": matched_calls, "all_remote_call_statuses": status_counts,
               "worker_v1_sha256": sha(destination / "worker.py"), "worker_v2_sha256": sha(destination / "worker-v2.py"),
               "model_weights_included": False, "private_compound_rows_included": False,
               "cleanup": "NOT_RUN_BEFORE_THIS_FULL_REREAD"}
    write(WORK / "verification-v1.json", receipt, True)
    write(PUBLIC / "complete-remote-return-v1.json", receipt, True)
    print(json.dumps(receipt))


def cleanup():
    verified = read(WORK / "verification-v1.json")
    assert verified["status"] == "PASS_COMPLETE_RETURN_AND_FULL_FILE_REREAD"
    assert sha(ARCHIVE) == verified["archive_sha256"]
    # Recheck local returned files immediately before the irreversible owned deletion.
    manifest = read(WORK / "files/return-v1/manifest.json")
    assert sha(WORK / "files/return-v1/manifest.json") == verified["manifest_sha256"]
    assert all(sha(WORK / "files" / r["path"]) == r["sha256"] for r in manifest["files"])
    receipt = remote("cleanup", {"local_full_reread_pass": True, "archive_sha256": verified["archive_sha256"],
                                 "manifest_sha256": verified["manifest_sha256"]})
    write(PUBLIC / "owned-remote-cleanup-v1.json", receipt, True)
    print(json.dumps(receipt))


def absence():
    assert read(PUBLIC / "owned-remote-cleanup-v1.json")["status"] == "PASS_EXACT_OWNED_CLEANUP_AFTER_VERIFIED_RETURN"
    receipt = remote("absence")
    write(PUBLIC / "fresh-remote-absence-v1.json", receipt, True)
    print(json.dumps(receipt))


if __name__ == "__main__":
    assert sys.argv[1] in ("export", "fetch", "verify", "cleanup", "absence")
    {"export": export, "fetch": fetch, "verify": verify, "cleanup": cleanup, "absence": absence}[sys.argv[1]]()
