"""Authenticated streamed LR-D23 dispatch over the reviewed one-core transport."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import json
import secrets
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import (
    REMOTE,
    TASK,
    authority,
    ledger_save,
    new,
    orchestration_start,
    read,
    sha,
    utility_finish,
)
from tools import d1_remote_v1 as legacy

OLD = ROOT / ".local/d1-operation-headroom-20261109-v1"


def configure():
    legacy.TASK, legacy.REMOTE = TASK, REMOTE
    legacy.configure()


def remote(code, stdin=None, timeout=60):
    configure()
    return legacy.transport.remote(code, stdin=stdin, timeout=timeout)


def probe():
    authority()
    profile = read(OLD / "ssh-profile.json")["selected_profile"]
    result = subprocess.run(["rtk", "proxy", "ssh", "-G", profile], capture_output=True, text=True, timeout=15)
    fields = dict(line.split(maxsplit=1) for line in result.stdout.splitlines() if len(line.split(maxsplit=1)) == 2)
    assert result.returncode == 0 and fields["user"] == "chaw" and fields["hostname"] == "100.77.149.83"
    assert "id_ed25519_dr_train" in result.stdout
    new(TASK / "ssh-profile.json", {"selected_profile": profile, "private_key_read": False, "config_changed": False})
    code = '''import json,os,pwd,resource,shutil,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(15)
allowed=sorted(os.sched_getaffinity(0));cpus=[69,70,71];assert all(c in allowed for c in cpus);os.sched_setaffinity(0,{69})
names=['lr-d23-20261109-v1','lr-d23-20261109-v1-export-v1','d1-operation-headroom-20261109-v1','d1-operation-headroom-20261109-v1-export-v1','m2-costed-20261108-v2','m2-costed-20261108-v2-export-v1']
paths=[Path.home()/'curaloop-tasks'/n for n in names];active=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   if p.stat().st_uid==os.getuid() and int(p.name)!=os.getpid() and b'curaloop-tasks/' in (p/'cmdline').read_bytes():active.append(int(p.name))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
mem=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'hostname':os.uname().nodename,'cpus':cpus,'owned_roots_absent':all(not p.exists() and not p.is_symlink() for p in paths),'active_owned_pids':active,'memory_available':mem,'disk_free':shutil.disk_usage(Path.home()).free}))
'''
    response = remote(code, timeout=30)
    new(TASK / "remote-probe-raw.json", {"exit_code": response.returncode, "stdout": response.stdout.decode(), "stderr": response.stderr.decode()})
    assert response.returncode == 0, "SSH_PROBE_FAILED_NO_AUTOMATIC_RETRY"
    value = json.loads(response.stdout)
    assert value["user"] == "chaw" and value["hostname"] == "dr-train" and value["owned_roots_absent"]
    assert not value["active_owned_pids"] and value["memory_available"] > 16 * 1024**3 and value["disk_free"] > 4 * 1024**3
    new(TASK / "remote-admission.json", value)
    print({"status": "PASS_READ_ONLY_REMOTE_ADMISSION", "cpus": value["cpus"]})


def bundle():
    authority()
    assert read(TASK / "admission/summary.json")["status"] == "PASS_OUTCOME_BLIND_ADMISSION"
    authenticated = {r["path"]: r for r in read(OLD / "remote-return/export/manifest.json")["files"]}
    original_code = read(ROOT / ".local/m2-costed-20261108-v2/code-stage-03.json")["code_pins"]
    code_paths = list(original_code)
    code_paths += ["research/d1_v1/__init__.py", "research/d1_v1/controls.py"]
    code_paths += [str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "research/lr_d23_v1").glob("*.py")
                   if p.name != "common.py"]
    files = [(ROOT / name, "code/" + name) for name in code_paths]
    for name, row in authenticated.items():
        if name.startswith("vendor/"):
            source = OLD / "remote-return/files" / name
            assert sha(source) == row["sha256"]
            files.append((source, name))
    admitted = read(TASK / "admission/features-and-mask-private.json")["pools"]
    projection = read(ROOT / ".local/m2-costed-20261108-v2/development-projection-manifest.json")["files"]
    assert {r["task_id"] for r in projection} == set(admitted) and len(admitted) == 6
    sources = {}
    for row in projection:
        task = row["task_id"]
        source = ROOT / ".local/m2-costed-20261108-v2" / row["path"]
        assert sha(source) == row["sha256"] and row["source_sha256"] == admitted[task]["input_sha256"]
        assert row["component"] == admitted[task]["group"]
        sources[task] = dict(sha256=row["sha256"], component=row["component"], rows=row["rows"])
        files.append((source, "inputs/" + task + ".json"))
    new(TASK / "sources.json", sources)
    manifest = {"schema": "curaloop.lr_d23.transport.v1", "biological_inputs_included": True,
                "payload_decode_before_technical_admission": False,
                "files": [{"path": name, "bytes": source.stat().st_size, "sha256": sha(source)} for source, name in files]}
    assert len(files) < 5000 and sum(row["bytes"] for row in manifest["files"]) < 512 * 1024**2
    new(TASK / "transport-manifest.json", manifest)
    with tarfile.open(TASK / "transport-technical-v1.tar.gz", "x:gz", compresslevel=1) as archive:
        for source, name in files:
            archive.add(source, arcname=name, recursive=False)
        archive.add(TASK / "transport-manifest.json", arcname="transport-manifest.json")
    new(TASK / "code-pins.json", {row["path"][5:]: row["sha256"] for row in manifest["files"] if row["path"].startswith("code/")})
    print({"status": "PASS_AUTHENTICATED_BUNDLE", "files": len(files), "bytes": (TASK / "transport-technical-v1.tar.gz").stat().st_size})


def book(name, handler, cpu, bucket, count, seconds_per_unit, extra=None):
    release, ledger = authority()
    assert name not in ledger["bookings"]
    reservation = count * seconds_per_unit
    if bucket != "utilities_handoff":
        current = ledger["retained_seconds"].get(bucket, 0)
        assert current + reservation <= ledger["stage_caps"][bucket]
        ledger["retained_seconds"][bucket] = current + reservation
    value = {"schema": "curaloop.lr_d23.permit.v1", "attempt": name, "token": secrets.token_hex(16),
             "task_root": REMOTE, "host": "dr-train", "cpu": cpu, "handler": handler,
             "reservation_seconds": reservation, "guard_cpu_seconds": reservation,
             "memory_bytes": 4294967296, "wall_seconds": min(7200, reservation * 3 + 120),
             "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
             "code_directory": "code", "code_pins": read(TASK / "code-pins.json"),
             "bundle_sha256": sha(TASK / "transport-technical-v1.tar.gz"), "final_outcomes_open": False}
    if extra:
        value.update(extra)
    ledger["bookings"][name] = {"status": "RESERVED", "bucket": bucket, "units": count,
                                "retained_seconds": reservation, "host": "dr-train", "cpu": cpu}
    ledger_save(ledger)
    new(TASK / "jobs" / name / "permit.json", value)
    return value


def render(name):
    configure()
    code, value = legacy.rendered(name)
    code = code.replace("d1-operation-headroom-20261109-v1", "lr-d23-20261109-v1")
    code = code.replace("curaloop-d1-20261109-v1-", "curaloop-lrd23-20261109-v1-")
    code = code.replace("research.d1_v1.worker", "research.lr_d23_v1.worker")
    code = code.replace("curaloop.m2_profile.", "curaloop.lr_d23.")
    compile(code, "<lr-d23-dispatch>", "exec")
    assert "curaloop-tasks/d1-" not in code and "curaloop-tasks/m2-" not in code
    return code, value


def dispatch(name):
    """No ledger mutation here; concurrent completions are settled by the parent."""
    code, value = render(name)
    folder = TASK / "jobs" / name
    path = folder / "remote-command.py"
    with path.open("x", encoding="utf-8", newline="\n") as file:
        file.write(code)
    if name == "bootstrap":
        assert len(code.encode()) * 4 / 3 < 26000, "BOOTSTRAP_COMMAND_TOO_LARGE_BEFORE_SSH"
        with (TASK / "transport-technical-v1.tar.gz").open("rb") as stream:
            response = remote(code, stdin=stream, timeout=value["wall_seconds"] + 60)
    else:
        stage = '''import hashlib,json,os,resource,signal,sys
from pathlib import Path
os.sched_setaffinity(0,{69});resource.setrlimit(resource.RLIMIT_CPU,(20,20));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));signal.alarm(30)
root=Path(__ROOT__);assert root.resolve()==root and root.is_dir() and not root.is_symlink()
assert not (root/'jobs'/__NAME__).exists()
data=sys.stdin.buffer.read(__SIZE__+1);assert len(data)==__SIZE__ and hashlib.sha256(data).hexdigest()==__SHA__
compile(data,'<authenticated-lrd23-command>','exec')
folder=root/'dispatch';folder.mkdir(exist_ok=True);path=folder/(__NAME__+'.py')
with path.open('xb') as f:f.write(data)
path.chmod(0o600);print(json.dumps({'status':'PASS_STREAMED_COMMAND','sha256':hashlib.sha256(data).hexdigest()}))
'''.replace("__ROOT__", repr(REMOTE)).replace("__NAME__", repr(name)).replace("__SIZE__", str(path.stat().st_size)).replace("__SHA__", repr(sha(path)))
        with path.open("rb") as stream:
            staged = remote(stage, stdin=stream, timeout=40)
        new(folder / "command-stage.json", {"exit_code": staged.returncode, "stdout": staged.stdout.decode(), "stderr": staged.stderr.decode()})
        assert staged.returncode == 0, "COMMAND_STAGE_FAILED_INSPECT_BEFORE_RETRY"
        assert json.loads(staged.stdout)["sha256"] == sha(path)
        short = "import runpy;runpy.run_path(" + repr(REMOTE + "/dispatch/" + name + ".py") + ",run_name='__main__')"
        response = remote(short, timeout=value["wall_seconds"] + 60)
    new(folder / "ssh-raw.json", {"exit_code": response.returncode, "stdout": response.stdout.decode(), "stderr": response.stderr.decode()})
    assert response.returncode == 0, "REMOTE_OUTCOME_UNCERTAIN_INSPECT_BEFORE_RETRY"
    result = json.loads(response.stdout)
    new(folder / "controller-result.json", result)
    for field in ("result", "resource", "kernel-proof", "failure"):
        if field in result:
            new(folder / (field + ".json"), result[field])
    return result


def settle(name, result):
    ledger = read(TASK / "ledger.json")
    status = "PASS" if result["exit_code"] == 0 and result.get("result", {}).get("status", "").startswith("PASS") else "FAIL"
    ledger["bookings"][name]["status"] = status
    ledger["bookings"][name]["resource_sha256"] = sha(TASK / "jobs" / name / "resource.json") if (TASK / "jobs" / name / "resource.json").exists() else None
    ledger_save(ledger)
    assert status == "PASS", "REMOTE_BATCH_FAILURE_RETAINED"


def bootstrap():
    archive = TASK / "transport-technical-v1.tar.gz"
    book("bootstrap", "bootstrap", 69, "utilities_handoff", 1, 60,
         {"arguments": {"archive_bytes": archive.stat().st_size, "archive_sha256": sha(archive)}})
    result = dispatch("bootstrap")
    settle("bootstrap", result)
    print({"status": "PASS_BOOTSTRAP"})


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("probe", "bundle", "bootstrap")
    limit = {"probe": (60, 90), "bundle": (180, 300), "bootstrap": (120, 360)}[action]
    guard = orchestration_start("local-" + action, *limit)
    try:
        globals()[action]()
        utility_finish("local-" + action, guard, "PASS")
    except BaseException:
        utility_finish("local-" + action, guard, "FAIL")
        raise
