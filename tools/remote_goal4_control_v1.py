"""Strict existing-profile SSH controller for one explicitly owned Goal4 root."""

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "/home/chaw/curaloop-rl/plan-a-20261105-v2"
HOST = "100.77.149.83"
OPTIONS = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "IdentitiesOnly=yes",
           "-o", "ConnectTimeout=10", "-o", "ConnectionAttempts=1"]

PREFLIGHT = r'''
import json,os,shutil,socket,sys,time
from pathlib import Path
root=Path('/home/chaw/curaloop-rl/plan-a-20261105-v2')
parent=root.parent
memory={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.split(':')[0] in ('MemTotal','MemAvailable')}
jobs=[]
for entry in Path('/proc').iterdir():
    if not entry.name.isdigit(): continue
    try:
        command=(entry/'cmdline').read_bytes().split(b'\x00')
        if command and any(b'python' in command[0] or b'curaloop' in value for value in command[:2]):
            jobs.append({'pid':int(entry.name),'executable':Path(command[0].decode(errors='replace')).name,'this_task':any(str(root).encode() in value for value in command)})
    except (OSError,ValueError): pass
r={'status':'PASS_READ_ONLY_PREFLIGHT','host':socket.gethostname(),'uid':os.getuid(),'python':sys.version,'allowed_cpus':sorted(os.sched_getaffinity(0)),'load_average':os.getloadavg(),'memory':memory,'disk_free_bytes':shutil.disk_usage(parent).free,'project_parent_canonical':str(parent.resolve()),'task_root_exists':root.exists(),'python_jobs_sanitized':jobs,'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
assert parent.resolve()==Path('/home/chaw/curaloop-rl') and parent.stat().st_uid==os.getuid()
assert memory['MemAvailable']>8*1024**3 and r['disk_free_bytes']>8*1024**3
print(json.dumps(r,indent=2))
'''


def ssh_script(source, timeout=120):
    result = subprocess.run(["ssh", *OPTIONS, HOST, "python3 -"], input=source.encode(),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        print(result.stderr.decode(errors="replace")[-4000:])
        raise RuntimeError(f"Remote operation failed with exit {result.returncode}.")
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["preflight", "create", "unpack", "status", "return-preflight", "absence"])
    args = parser.parse_args()
    packet = ROOT / "docs/evidence/goal4-20261105-v1"
    if args.action == "preflight":
        payload = ssh_script(PREFLIGHT)
        report = json.loads(payload)
        path = packet / "remote-preflight-v1.json"
    elif args.action == "create":
        proof = json.loads((packet / "remote-preflight-v1.json").read_text())
        if proof["status"] != "PASS_READ_ONLY_PREFLIGHT" or proof["task_root_exists"]:
            raise ValueError("Fresh owned remote root required.")
        source = "import os,json; from pathlib import Path; p=Path(" + repr(REMOTE) + "); assert p.parent.resolve()==Path('/home/chaw/curaloop-rl') and p.parent.stat().st_uid==os.getuid(); os.umask(0o077); p.mkdir(exist_ok=False); print(json.dumps({'status':'PASS_NEW_OWNED_ROOT','root':str(p.resolve()),'uid':p.stat().st_uid}))"
        payload = ssh_script(source)
        report = json.loads(payload)
        path = packet / "remote-root-created-v1.json"
    elif args.action == "unpack":
        expected = json.loads((packet / "remote-input-bundle-v1.json").read_text())["archive_sha256"]
        source = r'''
import os,json,hashlib,zipfile
from pathlib import Path,PurePosixPath
root=Path('/home/chaw/curaloop-rl/plan-a-20261105-v2')
assert root.resolve()==root and root.stat().st_uid==os.getuid()
os.umask(0o077)
archive=root/'remote-input-v1.zip'
manifest=json.loads((root/'remote-input-v1-manifest.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==EXPECTED==manifest['archive_sha256']
rows={r['path']:r for r in manifest['files']}
assert len(rows)==len(manifest['files']) and len(rows)<=250
total=0
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(rows)
    for info in z.infolist():
        name=PurePosixPath(info.filename)
        assert not name.is_absolute() and '..' not in name.parts and '\\' not in info.filename and not info.is_dir()
        assert ((info.external_attr>>16)&0o170000) in (0,0o100000)
        assert info.file_size==rows[info.filename]['bytes'] and info.file_size<=16*1024**2
        total+=info.file_size
        assert total<=32*1024**2
        data=z.read(info)
        assert hashlib.sha256(data).hexdigest()==rows[info.filename]['sha256']
        target=(root/info.filename).resolve()
        assert target.is_relative_to(root) and not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as handle: handle.write(data)
print(json.dumps({'status':'PASS_CLOSED_REMOTE_UNPACK','files':len(rows),'bytes':total,'archive_sha256':EXPECTED}))
'''
        payload = ssh_script("EXPECTED=" + repr(expected) + "\n" + source)
        report = json.loads(payload)
        path = packet / "remote-input-verified-v1.json"
    elif args.action == "absence":
        source = r'''
import json,socket,time
from pathlib import Path
names=['goal2-20261104-v1','plan-a-20261105-v1','plan-a-20261105-v1-return','plan-a-20261105-v2','plan-a-20261105-v2-return']
paths=[Path('/home/chaw/curaloop-rl')/name for name in names]
print(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'host':socket.gethostname(),'paths':{str(path):{'exists':path.exists(),'is_symlink':path.is_symlink()} for path in paths},'status':'PASS_ALL_SCOPED_ROOTS_ABSENT' if all(not path.exists() and not path.is_symlink() for path in paths) else 'FAIL'},indent=2))
'''
        report = json.loads(ssh_script(source))
        path = packet / "remote-absence-v1.json"
    elif args.action == "return-preflight":
        source = r'''
import os,json,stat
from pathlib import Path
root=Path('/home/chaw/curaloop-rl/plan-a-20261105-v2')
assert root.resolve()==root and root.stat().st_uid==os.getuid()
links=[];names=[];unsupported=[];total=0;foreign=[]
for parent,dirs,files in os.walk(root,followlinks=False):
    for name in dirs+files:
        p=Path(parent)/name; info=p.lstat(); rel=p.relative_to(root).as_posix()
        if stat.S_ISLNK(info.st_mode): links.append({'path':rel,'target':os.readlink(p)})
        elif stat.S_ISREG(info.st_mode): names.append(rel);total+=info.st_size
        elif not stat.S_ISDIR(info.st_mode): unsupported.append(rel)
        if info.st_uid!=os.getuid():foreign.append(rel)
reserved={'CON','PRN','AUX','NUL'}|{f'{prefix}{n}' for prefix in ('COM','LPT') for n in range(1,10)}
unsafe=[name for name in names if any(part.endswith((' ','.')) or part.split('.')[0].upper() in reserved or any(ord(c)<32 or c in '<>:"\\|?*' for c in part) for part in name.split('/'))]
fold={};collisions=[]
for name in names:
    folded=name.casefold()
    if folded in fold:collisions.append([fold[folded],name])
    fold[folded]=name
r={'status':'PASS_RETURN_PREFLIGHT' if not(links or unsupported or foreign or unsafe or collisions) and len(names)<=50000 and total<=16*1024**3 else 'FAIL_RETURN_PREFLIGHT','file_count_observed':len(names),'bytes_observed':total,'symlinks':links,'unsupported':unsupported,'foreign_owner_entries':foreign,'unsafe_windows_names':unsafe,'casefold_collisions':collisions,'longest_relative_path':max(names,key=len) if names else None,'longest_relative_path_characters':max(map(len,names),default=0),'not_final_frozen_inventory':True}
print(json.dumps(r,indent=2))
'''
        report = json.loads(ssh_script(source))
        path = packet / "remote-return-preflight-v1.json"
    else:
        source = r'''
import os,json,time
from pathlib import Path
root=Path('/home/chaw/curaloop-rl/plan-a-20261105-v2')
assert root.resolve()==root and root.stat().st_uid==os.getuid()
jobs=[]
for folder in sorted((root/'.local/plan-a-20261105-v2/runs').glob('*/*')):
    if not folder.is_dir(): continue
    resource_path=folder/'resources.json'
    if not resource_path.exists(): continue
    r=json.loads(resource_path.read_text())
    progress=folder/'progress.jsonl'
    last=None
    if progress.exists():
        with progress.open('rb') as h:
            h.seek(max(0,progress.stat().st_size-4096)); lines=h.read().splitlines()
        if lines:
            try: last=json.loads(lines[-1])
            except ValueError: pass
    proc=Path('/proc')/str(r['pid'])
    live=False
    cpu=None
    rss=None
    if proc.exists():
        try:
            command=(proc/'cmdline').read_bytes()
            live=b'research.study_v1.worker' in command and Path(os.readlink(proc/'cwd')).resolve()==root
            stat=(proc/'stat').read_text().split()
            cpu=(int(stat[13])+int(stat[14]))/os.sysconf('SC_CLK_TCK')
            rss=int((proc/'statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
        except (OSError,ValueError): pass
    jobs.append({'phase':folder.parent.name,'shard':folder.name,'status':r['status'],'pid':r['pid'],'confirmed_live':live,'observed_cpu_seconds':cpu,'observed_rss_bytes':rss,'progress':last,'complete_receipt_exists':(folder/'complete.json').exists(),'failure_receipt_exists':(folder/'failure.json').exists()})
print(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'jobs':jobs},indent=2))
'''
        report = json.loads(ssh_script(source))
        print(json.dumps(report, indent=2))
        return
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
