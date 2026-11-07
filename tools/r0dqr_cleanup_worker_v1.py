"""Inline, kernel-capped cleanup only after an independently checked full return."""
import hashlib,json,os,shutil,stat,time
from pathlib import Path
from datetime import datetime,timezone

def run(authorization):
    started=time.process_time();root=Path(authorization['root']);export=Path(authorization['export'])
    assert root==Path('/home/chaw/curaloop-runs/chembl-taskfirst-dqr-20261107-v1')
    assert export==Path(str(root)+'-export-v1')
    assert datetime.now(timezone.utc)<datetime.fromisoformat(authorization['deadline_utc'])
    for path in [root,export]:
        assert path.resolve()==path and not path.is_symlink() and path.stat().st_uid==os.getuid()
        assert path.parent.resolve()==Path('/home/chaw/curaloop-runs')
    assert os.sched_getaffinity(0)=={authorization['cpu']} and os.getpriority(os.PRIO_PROCESS,0)==19
    cg=Path('/sys/fs/cgroup'+next(l.split('::',1)[1] for l in Path('/proc/self/cgroup').read_text().splitlines() if l.startswith('0::')))
    kernel={n:(cg/n).read_text().strip() for n in ['cpu.max','memory.max','memory.swap.max']}
    assert kernel=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
    def sha(path):
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
        return h.hexdigest()
    assert sha(export/'manifest.json')==authorization['manifest_sha256']
    manifest=json.loads((export/'manifest.json').read_text())
    assert manifest['archive_sha256']==authorization['archive_sha256']
    assert sha(export/'full-task-v1.tar.gz')==authorization['archive_sha256']
    expected={r['path']:r for r in manifest['files']};current={}
    for parent,dirs,files in os.walk(root,followlinks=False):
        for name in dirs+files:
            target=Path(parent)/name;meta=target.lstat();rel=target.relative_to(root).as_posix()
            assert meta.st_uid==os.getuid()
            if stat.S_ISLNK(meta.st_mode):
                assert {'path':rel,'target':os.readlink(target),'mode':stat.S_IMODE(meta.st_mode)} in manifest['aliases'];continue
            assert stat.S_ISREG(meta.st_mode) or stat.S_ISDIR(meta.st_mode)
            if stat.S_ISREG(meta.st_mode):current[rel]=target
    assert set(current)==set(expected)
    for rel,target in current.items():assert target.stat().st_size==expected[rel]['bytes'] and sha(target)==expected[rel]['sha256']
    # Every export helper/proof/log was also returned as a separately hashed
    # terminal capsule. No unknown export file may be deleted.
    exported={f.name:f for f in export.iterdir() if f.is_file()}
    assert set(exported)==set(authorization['export_file_pins'])|{'full-task-v1.tar.gz'}
    assert all(f.is_file() and not f.is_symlink() for f in export.iterdir())
    for name,pin in authorization['export_file_pins'].items():assert exported[name].stat().st_size==pin['bytes'] and sha(exported[name])==pin['sha256']
    shutil.rmtree(root);shutil.rmtree(export)
    assert not root.exists() and not export.exists()
    print(json.dumps({'status':'PASS_EXACT_DELETE_AFTER_FULL_RETURN','root':str(root),'export':str(export),
        'kernel':kernel,'cpu_affinity':sorted(os.sched_getaffinity(0)),'nice':19,'invocation_id':os.environ.get('INVOCATION_ID'),
        'cpu_seconds':time.process_time()-started,'utc':datetime.now(timezone.utc).isoformat()}))
