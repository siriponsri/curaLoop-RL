"""Versioned D1 transport using the reviewed M2 one-core systemd mechanism."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import hashlib
import json
import secrets
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import OLD, TASK, authority, new, now, read, save_ledger, sha
from tools import m2c_remote_v2 as transport

REMOTE = "/home/chaw/curaloop-tasks/d1-operation-headroom-20261109-v1"


def configure():
    transport.TASK = TASK
    transport.REMOTE = REMOTE


def probe():
    authority()
    profile = read(OLD / "ssh-profile.json")["selected_profile"]
    result = subprocess.run(["rtk", "proxy", "ssh", "-G", profile], capture_output=True, text=True, timeout=15)
    values = dict(line.split(maxsplit=1) for line in result.stdout.splitlines() if len(line.split(maxsplit=1)) == 2)
    assert result.returncode == 0 and values["user"] == "chaw" and values["hostname"] == "100.77.149.83"
    assert "id_ed25519_dr_train" in result.stdout
    new(TASK / "ssh-profile.json", {"selected_profile": profile, "user": "chaw",
                                     "configuration_changed": False, "private_key_read": False})
    configure()
    code = '''import json,os,pwd,resource,shutil,signal,time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(15)
allowed=sorted(os.sched_getaffinity(0));cpu=69 if 69 in allowed else allowed[0];os.sched_setaffinity(0,{cpu})
paths=[Path.home()/'curaloop-tasks'/n for n in ('d1-operation-headroom-20261109-v1','d1-operation-headroom-20261109-v1-export-v1','m2-costed-20261108-v2','m2-costed-20261108-v2-export-v1')]
active=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   command=(p/'cmdline').read_bytes()
   if p.stat().st_uid==os.getuid() and b'curaloop-tasks/' in command and b'python3 -B -c' not in command and int(p.name)!=os.getpid():active.append(int(p.name))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
memory=next(int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'hostname':os.uname().nodename,'cpu':cpu,'roots_absent':all(not p.exists() and not p.is_symlink() for p in paths),'active_owned_pids':active,'memory_available':memory,'disk_free':shutil.disk_usage(Path.home()).free,'process_cpu':time.process_time()}))
'''
    response = transport.remote(code, timeout=30)
    new(TASK / "remote-probe-raw.json", {"exit_code": response.returncode,
                                         "stdout": response.stdout.decode(), "stderr": response.stderr.decode()})
    assert response.returncode == 0, "SSH_PROBE_FAILED_NO_RETRY"
    data = json.loads(response.stdout)
    assert data["user"] == "chaw" and data["hostname"] == "dr-train"
    assert data["roots_absent"] and not data["active_owned_pids"]
    assert data["memory_available"] >= 8 * 1024**3 and data["disk_free"] >= 4 * 1024**3
    new(TASK / "remote-admission.json", data)
    print({"status": "PASS_READ_ONLY_REMOTE_ADMISSION", "cpu": data["cpu"]})


def bundle():
    authority()
    assert read(TASK / "remote-admission.json")["roots_absent"]
    archived = {row["path"]: row for row in read(OLD / "remote-return/export/manifest.json")["files"]}
    files = []
    for name in read(OLD / "code-stage-03.json")["code_pins"]:
        files.append((ROOT / name, "code/" + name))
    for name in ("research/d1_v1/__init__.py", "research/d1_v1/controls.py", "research/d1_v1/worker.py"):
        files.append((ROOT / name, "code/" + name))
    for name, row in archived.items():
        if name.startswith("vendor/"):
            source = OLD / "remote-return/files" / name
            assert sha(source) == row["sha256"]
            files.append((source, name))
    projection = read(OLD / "development-projection-manifest.json")
    assert len(projection["files"]) == 6
    for row in projection["files"]:
        source = OLD / row["path"]
        assert sha(source) == row["sha256"]
        files.append((source, "inputs/" + row["task_id"] + ".json"))
    manifest = {"schema": "curaloop.d1.transport.v1", "biological_inputs_included": True,
                "biological_payload_decode_before_calibration": False,
                "files": [{"path": name, "bytes": source.stat().st_size, "sha256": sha(source)}
                          for source, name in files]}
    assert len(manifest["files"]) < 5000 and sum(r["bytes"] for r in manifest["files"]) < 512 * 1024**2
    new(TASK / "transport-manifest.json", manifest)
    with tarfile.open(TASK / "transport-technical-v1.tar.gz", "x:gz") as archive:
        for source, name in files:
            archive.add(source, arcname=name, recursive=False)
        archive.add(TASK / "transport-manifest.json", arcname="transport-manifest.json")
    code_pins = {r["path"][5:]: r["sha256"] for r in manifest["files"] if r["path"].startswith("code/")}
    new(TASK / "code-pins.json", code_pins)
    print({"status": "PASS_D1_BUNDLE", "files": len(files), "archive_bytes": (TASK / "transport-technical-v1.tar.gz").stat().st_size})


def permit(name):
    release, ledger = authority()
    cpu = read(TASK / "remote-admission.json")["cpu"]
    caps = {"bootstrap": (60, 120), "calibration": (900, 1100), "controls": (1200, 1600)}
    reservation, wall = caps[name]
    if name != "bootstrap":
        assert name not in ledger["retained_reservations_seconds"]
        ledger["retained_reservations_seconds"][name] = reservation
    value = {"schema": "curaloop.d1.permit.v1", "attempt": name, "token": secrets.token_hex(16),
             "task_root": REMOTE, "host": "dr-train", "cpu": cpu, "handler": name,
             "reservation_seconds": reservation, "guard_cpu_seconds": reservation,
             "wall_seconds": wall, "memory_bytes": 4294967296,
             "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
             "code_directory": "code", "code_pins": read(TASK / "code-pins.json"),
             "bundle_sha256": sha(TASK / "transport-technical-v1.tar.gz"), "final_outcomes_open": False}
    if name == "bootstrap":
        value["arguments"] = {"archive_bytes": (TASK / "transport-technical-v1.tar.gz").stat().st_size,
                              "archive_sha256": value["bundle_sha256"]}
    elif name == "calibration":
        value["contexts"] = [dict(n=n, n0=n0, policy=policy, repeat=repeat)
                             for n in (128, 303) for n0 in (0, 16)
                             for policy in ("G1", "P") for repeat in ([0] if policy == "G1" else [0, 1])]
    else:
        result = read(TASK / "jobs/calibration/result.json")
        assert result["status"] == "PASS"
        value["calibration_status"] = "PASS"
        value["calibration_sha256"] = sha(TASK / "jobs/calibration/result.json")
        caps_old = read(OLD / "technical-admission-result.json")["caps"]
        units = []
        for row in read(OLD / "development-projection-manifest.json")["files"]:
            for n0 in (0, 16):
                for seed in (71003, 71017):
                    for control in ("frozen_cache_greedy", "G1", "Gk_k4", "T_k4_tau0.05", "nearest_hit"):
                        units.append(dict(task_id=row["task_id"], input_sha256=row["sha256"], n0=n0,
                                          seed=seed, control=control, cost_priors=caps_old[f"rf:{n0}:32"]["operation_cost_priors"]))
        units.sort(key=lambda row: hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest())
        for i, row in enumerate(units):
            row["name"] = f"control-{i:03d}"
        assert len(units) == 120
        value["units"] = units
        new(TASK / "controls-freeze-v1.json", {"frozen_utc": now().isoformat(), "units": units,
                                                "code_pins": value["code_pins"], "outcomes_read": False})
    ledger["jobs"][name] = {"status": "RESERVED", "host": "dr-train", "reservation_seconds": reservation}
    save_ledger(ledger)
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
    code = code.replace("m2-costed-20261108-v2", "d1-operation-headroom-20261109-v1")
    code = code.replace("curaloop-m2c-20261108-v1-", "curaloop-d1-20261109-v1-")
    code = code.replace("research.m2_costed_v2.worker", "research.d1_v1.worker")
    assert "curaloop-tasks/m2-costed" not in code
    compile(code, "<d1-remote-dispatch>", "exec")
    return code, value


def dispatch(name):
    permit(name)
    code, value = rendered(name)
    folder = TASK / "jobs" / name
    with (folder / "remote-command.py").open("x", encoding="utf-8") as file:
        file.write(code)
    if name == "bootstrap":
        with (TASK / "transport-technical-v1.tar.gz").open("rb") as stream:
            response = transport.remote(code, stdin=stream, timeout=value["wall_seconds"] + 60)
    else:
        response = transport.remote(code, timeout=value["wall_seconds"] + 60)
    new(folder / "ssh-raw.json", {"exit_code": response.returncode,
                                  "stdout": response.stdout.decode(), "stderr": response.stderr.decode()})
    assert response.returncode == 0, "REMOTE_DISPATCH_ERROR_INSPECT_RETAINED_OUTCOME_BEFORE_RETRY"
    data = json.loads(response.stdout)
    new(folder / "controller-result.json", data)
    for field in ("result", "resource", "kernel-proof", "failure"):
        if field in data:
            new(folder / (field + ".json"), data[field])
    ledger = read(TASK / "ledger.json")
    ledger["jobs"][name]["status"] = "PASS" if data["exit_code"] == 0 and data.get("result", {}).get("status", "").startswith("PASS") else "FAIL"
    save_ledger(ledger)
    print({"job": name, "exit_code": data["exit_code"], "status": data.get("result", {}).get("status")})
    assert ledger["jobs"][name]["status"] == "PASS", "REMOTE_JOB_FAILED_PRESERVE_EVIDENCE"


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "probe":
        probe()
    elif action == "bundle":
        bundle()
    else:
        assert action in ("bootstrap", "calibration", "controls")
        dispatch(action)
