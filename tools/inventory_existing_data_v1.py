"""Bounded file-metadata inventory only; never load dataset/archive/label contents."""
import collections,json,os,time
from datetime import datetime,timezone
from pathlib import Path
import psutil

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.local/data-inventory-20261107-v1'
PUBLIC=ROOT/'docs/evidence/local-data-inventory-20261107-v1'
SKIP={'.git','.venv','venv','node_modules','vendor','linux-vendor','__pycache__','site-packages','manual-render-v2','lrbc-ui-20261106-v1'}
SUFFIXES=('.json','.jsonl','.csv','.tsv','.parquet','.sdf','.smi','.smiles','.npy','.npz','.pkl','.db','.sqlite','.sqlite3','.tar','.gz','.zip','.pdf')
SCOPES=[('repo/research',ROOT/'research'),('repo/.local',ROOT/'.local'),
    ('repo/src/curaloop/resources',ROOT/'src/curaloop/resources'),('repo/papers',ROOT/'papers'),
    ('workspace',Path(r'C:\Users\User\Documents\ChatGPT\Drug Discovery'))]
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def main():
    assert not PRIVATE.exists(),'Do not overwrite an existing inventory'
    proc=psutil.Process();core=max(proc.cpu_affinity());proc.cpu_affinity([core])
    if os.name=='nt':proc.nice(psutil.IDLE_PRIORITY_CLASS)
    started=time.monotonic();cpu=time.process_time();rows=[];skipped=[];errors=[];complete=True
    for scope,base in SCOPES:
        if not base.exists():errors.append({'scope':scope,'status':'ROOT_ABSENT'});continue
        for parent,dirs,names in os.walk(base,followlinks=False):
            parent=Path(parent);kept=[]
            for name in dirs:
                target=parent/name
                if name in SKIP or target==PRIVATE or target.is_symlink():skipped.append({'scope':scope,'path':target.relative_to(base).as_posix(),'reason':'DEPENDENCY_UI_CACHE_SELF_OR_ALIAS'} )
                else:kept.append(name)
            dirs[:]=kept
            for name in names:
                if not name.lower().endswith(SUFFIXES):continue
                path=parent/name
                if path.is_symlink():continue
                try:
                    st=path.stat();rows.append({'scope':scope,'path':path.relative_to(base).as_posix(),'bytes':st.st_size,
                        'mtime_utc':datetime.fromtimestamp(st.st_mtime,timezone.utc).isoformat()})
                except OSError as exc:errors.append({'scope':scope,'path':str(path.relative_to(base)),'error_type':type(exc).__name__})
                if len(rows)>=50000 or time.monotonic()-started>30:complete=False;break
            if not complete:break
        if not complete:break
    folders=collections.defaultdict(lambda:{'files':0,'bytes':0})
    for row in rows:
        rel=Path(row['path']);key=row['scope']+'/'+str(rel.parent).replace('\\','/')
        folders[key]['files']+=1;folders[key]['bytes']+=row['bytes']
    report={'schema':'curaloop.local-data-file-metadata.v1','status':'COMPLETE_WITHIN_DECLARED_SCOPE' if complete else 'PARTIAL_SCAN_CAP',
        'utc':datetime.now(timezone.utc).isoformat(),'roots':[{'scope':s,'absolute_root':str(p)} for s,p in SCOPES],
        'matching_files':len(rows),'matching_physical_bytes':sum(r['bytes'] for r in rows),
        'largest_files':sorted(rows,key=lambda r:r['bytes'],reverse=True)[:45],
        'folder_aggregates':[{'path':k,**v} for k,v in sorted(folders.items())],
        'skipped_directory_count':len(skipped),'skipped_directories':skipped,'errors':errors,
        'cpu_affinity':[core],'wall_seconds':time.monotonic()-started,'cpu_seconds':time.process_time()-cpu,
        'file_contents_read':False,'large_file_hashes_recomputed':False,'archive_members_or_db_rows_opened':False,
        'source_http_or_ssh':0,'new_research_phase_or_budget':False,
        'interpretation':'Physical files include duplicate returns, code/config/run artifacts and literature; byte totals are not independent datasets or usable measurement counts.'}
    PRIVATE.mkdir(parents=True)
    save(PRIVATE/'file-metadata-v1.json',{'files':rows,'summary':report})
    save(PUBLIC/'filesystem-summary-v1.json',report)
    print(json.dumps({k:report[k] for k in ['status','matching_files','matching_physical_bytes','skipped_directory_count','errors','wall_seconds','cpu_seconds']}))
if __name__=='__main__':main()
