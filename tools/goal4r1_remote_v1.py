"""New-root strict SSH operations; no credentials or unrelated project writes."""

import argparse
import hashlib
import json
from pathlib import Path

from tools.remote_goal4_control_v1 import PREFLIGHT, ssh_script

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "/home/chaw/curaloop-rl/goal4r1-20261105-v1"
PACKET = ROOT / "docs/evidence/goal4r1-20261105-v1"


def decode_helper_output(raw):
    """Retain each JSON reply when a verified legacy core also emits a receipt."""
    remaining = raw.decode("utf-8").strip()
    decoder, records = json.JSONDecoder(), []
    while remaining:
        value, end = decoder.raw_decode(remaining)
        if type(value) is not dict:
            raise ValueError("Helper reply must be JSON objects only.")
        records.append(value)
        remaining = remaining[end:].lstrip()
    if not records:
        raise ValueError("Empty helper reply.")
    if len(records) == 1:
        return records[0]
    return {**records[-1], "preceding_stdout_records": records[:-1], "stdout_json_record_count": len(records)}


def write_new(name, data):
    PACKET.mkdir(parents=True, exist_ok=True)
    with (PACKET / name).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["preflight", "create", "unpack", "admin", "helper", "log"])
    parser.add_argument("--bundle")
    parser.add_argument("--admin-args", nargs=argparse.REMAINDER)
    parser.add_argument("--log-name")
    parser.add_argument("--brief", action="store_true")
    parser.add_argument("--helper-name", choices=["allocation", "select", "analyze", "audit", "return", "reporting_checks", "scratch", "return_preflight"])
    parser.add_argument("--helper-args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == "preflight":
        script = PREFLIGHT.replace("/home/chaw/curaloop-rl/plan-a-20261105-v2", REMOTE)
        # Reuse only the reviewed sanitized read-only probe, with a new root.
        data = decode_helper_output(ssh_script(script))
        write_new("remote-preflight-v1.json", data)
    elif args.action == "create":
        proof = json.loads((PACKET / "remote-preflight-v1.json").read_text())
        if proof["status"] != "PASS_READ_ONLY_PREFLIGHT" or proof["task_root_exists"]:
            raise ValueError("Fresh owned root required.")
        script = "import os,json; from pathlib import Path; p=Path(" + repr(REMOTE) + "); assert p.parent.resolve()==Path('/home/chaw/curaloop-rl') and p.parent.stat().st_uid==os.getuid(); os.umask(0o077); p.mkdir(exist_ok=False); print(json.dumps({'status':'PASS_NEW_OWNED_ROOT','root':str(p.resolve()),'uid':p.stat().st_uid}))"
        data = decode_helper_output(ssh_script(script))
        write_new("remote-created-v1.json", data)
    elif args.action == "unpack":
        if not args.bundle or not args.bundle.replace("-", "").isalnum():
            raise ValueError("Explicit bundle version required.")
        manifest = json.loads((ROOT / ".local/goal4r1-20261105-v1" / (args.bundle + ".json")).read_text())
        script = '''
import hashlib,json,os,shutil,zipfile
from pathlib import Path,PurePosixPath
root=Path(REMOTE)
assert root.resolve()==root and root.stat().st_uid==os.getuid()
os.umask(0o077)
archive=root/(BUNDLE+'.zip')
manifest=json.loads((root/(BUNDLE+'.json')).read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==EXPECTED==manifest['archive_sha256']
rows={r['path']:r for r in manifest['files']}
assert len(rows)==len(manifest['files'])<=100
frozen_before_unpack=(root/'docs/evidence/goal4r1-20261105-v1/protocol-freeze-v1.json').exists()
total=0
changed=[]
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(rows)
 for info in z.infolist():
  name=PurePosixPath(info.filename)
  assert not name.is_absolute() and '..' not in name.parts and '\\\\' not in info.filename and not info.is_dir()
  assert info.file_size==rows[info.filename]['bytes'] and info.file_size<=8*1024**2
  total+=info.file_size
  assert total<=16*1024**2
  data=z.read(info)
  assert hashlib.sha256(data).hexdigest()==rows[info.filename]['sha256']
  target=(root/info.filename).resolve()
  assert target.is_relative_to(root)
  if target.exists():
   assert not target.is_symlink()
   if target.read_bytes()==data: continue
   assert not frozen_before_unpack
   saved=root/'source-history'/BUNDLE/info.filename
   saved.parent.mkdir(parents=True,exist_ok=True)
   assert not saved.exists()
   shutil.copy2(target,saved)
   changed.append(info.filename)
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes(data)
print(json.dumps({'status':'PASS_CLOSED_UNPACK','files':len(rows),'bytes':total,'changed_sources_preserved':changed}))
'''
        prefix = "REMOTE=" + repr(REMOTE) + "\nBUNDLE=" + repr(args.bundle) + "\nEXPECTED=" + repr(manifest["archive_sha256"]) + "\n"
        data = decode_helper_output(ssh_script(prefix + script))
        write_new(args.bundle + "-unpacked-v1.json", data)
    elif args.action == "admin":
        values = args.admin_args or ["status"]
        script = "import os,subprocess; os.chdir(" + repr(REMOTE) + "); raise SystemExit(subprocess.call(['python3','tools/goal4r1_admin_v1.py']+" + repr(values) + "))"
        data = decode_helper_output(ssh_script(script))
    elif args.action == "helper":
        if not args.helper_name:
            raise ValueError("Allowlisted helper required.")
        name = "tools/goal4r1_" + args.helper_name + "_v1.py"
        if args.helper_name == "scratch":
            name = "tools/goal4r1_scratch_v2.py"
        expected = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        module = name[:-3].replace("/", ".")
        dependencies = {}
        if args.helper_name in ("select", "analyze", "reporting_checks", "audit"):
            dependency = "tools/goal4r1_reporting_v1.py"
            dependencies[dependency] = hashlib.sha256((ROOT / dependency).read_bytes()).hexdigest()
        script = "import os,hashlib; from pathlib import Path; os.chdir(" + repr(REMOTE) + "); p=Path(" + repr(name) + "); assert hashlib.sha256(p.read_bytes()).hexdigest()==" + repr(expected) + "; dependencies=" + repr(dependencies) + "; assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in dependencies.items()); command=[" + repr(REMOTE + "/.venv/bin/python") + ",'-m'," + repr(module) + "]+" + repr(args.helper_args or []) + "; os.execv(command[0],command)"
        if args.helper_name in ("return", "scratch", "return_preflight"):
            # Execute the locked helper from the project parent so no Python
            # ancestor remains inside TASK and incorrectly blocks preservation.
            script = "import os,resource,hashlib; from pathlib import Path; from datetime import datetime,timezone; task=Path(" + repr(REMOTE) + "); p=task/" + repr(name) + "; assert hashlib.sha256(p.read_bytes()).hexdigest()==" + repr(expected) + "; remaining=(datetime(2026,11,6,2,43,55,tzinfo=timezone.utc)-datetime.now(timezone.utc)).total_seconds(); assert remaining>6; os.chdir(task.parent); os.sched_setaffinity(0,{71}); os.nice(19); resource.setrlimit(resource.RLIMIT_CPU,(240,242)); resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3)); command=['/usr/bin/timeout','--signal=TERM','--kill-after=5s',str(min(1800,int(remaining)-5))+'s','/usr/bin/flock',str(task/'.admin.lock'),'python3',str(p)]+" + repr(args.helper_args or []) + "; os.execv(command[0],command)"
        data = decode_helper_output(ssh_script(script))
    else:
        if not args.log_name or '/' in args.log_name or '\\' in args.log_name:
            raise ValueError("One owned-root log filename required.")
        script = "from pathlib import Path; p=Path(" + repr(REMOTE) + ")/" + repr(args.log_name) + "; print(p.read_text()[-12000:])"
        print(ssh_script(script).decode())
        return
    if args.brief and args.action == "admin" and "jobs" in data:
        data = {k: data[k] for k in ("utc", "charges", "global_charge", "active")} | {
            "jobs": [{k: j[k] for k in ("phase", "shard", "status", "progress")} for j in data["jobs"]]}
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
