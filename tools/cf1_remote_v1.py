"""Fresh CF1 dispatch using the preserved one-core systemd transport."""
# ruff: noqa: E402

import json
import secrets
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import (
    REMOTE,
    TASK,
    authority,
    finish,
    new,
    read,
    save,
    sha,
    start,
)
from tools import m2c_remote_v2 as transport


def configure():
    transport.TASK, transport.REMOTE = TASK, REMOTE


def bundle():
    assert read(TASK / "runtime-probe-v1.json")["roots_absent"]
    assert read(TASK / "opaque-intake-v1.json")["status"] == "PASS_SIX_OPAQUE_WHOLE_FILES_AUTHENTICATED"
    dependencies = read(TASK / "dependency-inputs-v2.json")
    files = []
    names = ["research/__init__.py", "research/confirmation_v1/__init__.py", "research/confirmation_v1/technical_worker.py",
             "research/longrun_v1/__init__.py", "research/longrun_v1/guard.py",
             "research/m2_costed_v2/__init__.py", "research/m2_costed_v2/guard.py"]
    for name in names:
        files.append((ROOT / name, "code/" + name))
    for source, target in [("owner-source-a-v1.json", "owner-source-a.json"),
                           ("metadata-admission-v1.json", "metadata-admission.json"),
                           ("opaque-intake-v1.json", "opaque-intake.json"),
                           ("dependency-inputs-v2.json", "dependency-inputs.json")]:
        files.append((TASK / source, "inputs/" + target))
    files.append((TASK / dependencies["python"]["path"], "inputs/python38.tar.gz"))
    for row in dependencies["wheels"]:
        source = TASK / row["path"]
        assert sha(source) == row["sha256"]
        files.append((source, "wheels/" + row["filename"]))
    for row in read(TASK / "opaque-intake-v1.json")["files"]:
        source = TASK / row["private_path"]
        assert sha(source) == row["sha256"]
        files.append((source, "data/" + row["campaign"].replace("/", "-") + ".csv"))
    for name in ("MVS_A.py", "utils.py"):
        files.append((TASK / "source/code/Scripts" / name, "author/" + name))
    files.append((TASK / "source/code/LICENSE", "author/LICENSE"))
    old = ROOT / ".local/goal4r2a3-20261106-v1/remote-return/full-v1"
    assert sha(old / "manifest.json") == "eb2eeeef2de9915b08c35c0f73ac5bfeb32b1e5fff8fad3c081f8f3b8315aa0c"
    records = read(old / "manifest.json")["files"]
    for row in records:
        name = row["path"]
        if name.startswith("private-inputs/linux-vendor/"):
            source = old / "files" / name
            assert sha(source) == row["sha256"]
            files.append((source, "vendor/" + name[len("private-inputs/linux-vendor/"):]))
        elif name == "runs/metadata-audit-v1/protection-private.json":
            source = old / "files" / name
            assert sha(source) == row["sha256"]
            files.append((source, "inputs/protection-private.json"))
    manifest = {"schema": "curaloop.cf1.transport.v1", "biological_inputs_included": True,
                "biological_values_analyzed": False,
                "files": [{"path": name, "bytes": source.stat().st_size, "sha256": sha(source)} for source, name in files]}
    assert len({r["path"] for r in manifest["files"]}) == len(files) < 5000
    assert sum(r["bytes"] for r in manifest["files"]) < 512 * 1024**2
    new(TASK / "transport-manifest-v1.json", manifest)
    new(TASK / "code-pins-v1.json", {r["path"][5:]: r["sha256"] for r in manifest["files"] if r["path"].startswith("code/")})
    with tarfile.open(TASK / "transport-technical-v1.tar.gz", "x:gz", compresslevel=1) as archive:
        for source, name in files:
            archive.add(source, arcname=name, recursive=False)
        archive.add(TASK / "transport-manifest-v1.json", arcname="transport-manifest.json")
    print({"status": "PASS_CF1_AUTHENTICATED_BUNDLE", "files": len(files),
           "expanded_bytes": sum(r["bytes"] for r in manifest["files"]),
           "archive_bytes": (TASK / "transport-technical-v1.tar.gz").stat().st_size})


def book(name, handler, cpu, bucket, processor=69, extra=None):
    release, ledger = authority()
    assert name not in ledger["bookings"]
    if bucket != "utilities_return_handoff_delivery":
        ledger["retained_seconds"][bucket] = ledger["retained_seconds"].get(bucket, 0) + cpu
        assert ledger["retained_seconds"][bucket] <= ledger["stage_caps_seconds"][bucket]
    else:
        assert sum(r["cpu_cap"] for r in ledger["bookings"].values() if r["bucket"] == bucket) + cpu <= 43200
    value = {"schema": "curaloop.cf1.permit.v1", "attempt": name, "token": secrets.token_hex(16),
        "task_root": REMOTE, "host": "dr-train", "cpu": processor, "handler": handler,
        "reservation_seconds": cpu, "guard_cpu_seconds": cpu, "memory_bytes": 4294967296,
        "wall_seconds": min(3600, cpu * 3 + 120), "release_utc": release["release_utc"],
        "deadline_utc": release["deadline_utc"], "code_directory": "code", "code_pins": read(TASK / "code-pins-v1.json"),
        "bundle_sha256": sha(TASK / "transport-technical-v1.tar.gz"), "final_outcomes_open": False}
    if name == "bootstrap":
        value["arguments"] = {"archive_bytes": (TASK / "transport-technical-v1.tar.gz").stat().st_size,
                              "archive_sha256": value["bundle_sha256"]}
    if extra:
        value.update(extra)
    ledger["bookings"][name] = {"status": "RESERVED", "bucket": bucket, "cpu_cap": cpu,
                                "host": "dr-train", "cpu": processor, "handler": handler}
    save(ledger)
    new(TASK / "jobs" / name / "permit.json", value)


def rendered(name):
    configure()
    original = transport.BOOTSTRAP
    try:
        transport.BOOTSTRAP = original.replace("manifest['biological_inputs_included'] is False", "manifest['biological_inputs_included'] is True")
        transport.BOOTSTRAP = transport.BOOTSTRAP.replace("'biological_inputs_included':False", "'biological_inputs_included':True")
        code, value = transport.render_dispatch("bootstrap" if name == "bootstrap" else "worker", name)
    finally:
        transport.BOOTSTRAP = original
    code = code.replace("m2-costed-20261108-v2", "lr-cf1-20261109-v1")
    code = code.replace("curaloop-m2c-20261108-v1-", "curaloop-cf1-20261109-v1-")
    code = code.replace("research.m2_costed_v2.worker", "research.confirmation_v1.technical_worker")
    code = code.replace("command=['/usr/bin/python3','-B','-m'", "command=[permit.get('interpreter','/usr/bin/python3'),'-B','-m'")
    code = code.replace("str(root/'vendor')+':'+str(working)", "(str(working) if permit.get('interpreter') else str(root/'vendor')+':'+str(working))")
    assert "curaloop-tasks/m2-" not in code and len(code.encode()) * 4 / 3 < 26000
    compile(code, "<cf1-remote-dispatch>", "exec")
    return code, value


def dispatch(name):
    code, permit = rendered(name)
    folder = TASK / "jobs" / name
    with (folder / "remote-command.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(code)
    if name == "bootstrap":
        with (TASK / "transport-technical-v1.tar.gz").open("rb") as stream:
            result = transport.remote(code, stdin=stream, timeout=permit["wall_seconds"] + 60)
    else:
        result = transport.remote(code, timeout=permit["wall_seconds"] + 60)
    new(folder / "ssh-response.json", {"exit_code": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0, "INSPECT_REMOTE_UNIT_AND_RECEIPTS_BEFORE_RETRY"
    return json.loads(result.stdout)


def settle(name, result):
    folder = TASK / "jobs" / name
    new(folder / "controller-result.json", result)
    for field in ("result", "resource", "kernel-proof", "failure"):
        if field in result:
            new(folder / (field + ".json"), result[field])
    status = "PASS" if result["exit_code"] == 0 and result.get("result", {}).get("status", "").startswith("PASS") else "FAIL"
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][name]["status"] = status
    ledger["bookings"][name]["controller_sha256"] = sha(folder / "controller-result.json")
    save(ledger)
    print({"job": name, "status": status, "result": result.get("result", {}).get("status")}, flush=True)
    return status


def execute(action):
    if action == "bootstrap":
        book("bootstrap", "bootstrap", 60, "utilities_return_handoff_delivery")
        assert settle("bootstrap", dispatch("bootstrap")) == "PASS"
    elif action == "environment":
        assert read(TASK / "jobs/bootstrap/result.json")["status"] == "PASS_AUTHENTICATED_STREAM_BOOTSTRAP"
        book("environment", "environment", 600, "admission_and_calibration")
        assert settle("environment", dispatch("environment")) == "PASS"
    elif action == "smoke":
        assert read(TASK / "jobs/environment/result.json")["status"] == "PASS_CPU_ENVIRONMENT_EXTRACTED_SMOKE_PENDING"
        book("smoke", "smoke", 180, "admission_and_calibration", extra={"interpreter": REMOTE + "/python/bin/python3.8"})
        assert settle("smoke", dispatch("smoke")) == "PASS"
    else:
        assert action == "protect" and read(TASK / "jobs/smoke/result.json")["status"] == "PASS_ORIGINAL_VERSION_CPU_RUNTIME_SMOKE"
        selected = read(TASK / "metadata-admission-v1.json")["selected"]
        names = []
        for i, row in enumerate(selected):
            key = row["campaign"].replace("/", "-")
            name = "protect-" + key
            book(name, "protect", 600, "admission_and_calibration", processor=69 + i % 3,
                 extra={"campaign": row["campaign"], "output_name": key})
            names.append(name)
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {pool.submit(dispatch, name): name for name in names}
            for future in as_completed(pending):
                name = pending[future]
                settle(name, future.result())  # Parent alone settles ledger writes.


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("bundle", "bootstrap", "environment", "smoke", "protect")
    guard = start("transport-" + action, 300, 4200 if action == "protect" else 2200,
                  bucket="utilities_return_handoff_delivery", orchestration=action != "bundle")
    try:
        bundle() if action == "bundle" else execute(action)
        finish("transport-" + action, guard, "PASS_TRANSPORT_" + action.upper())
    except BaseException:
        finish("transport-" + action, guard, "FAIL")
        raise
