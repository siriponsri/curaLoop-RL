"""Small normal-delivery audit after scientific closure; no source processing."""
import ast,json,re,shutil,time
from pathlib import Path
from urllib.parse import unquote,urlparse
from r0dqr_core_v1 import ROOT,PRIVATE,PUBLIC,save,sha,archive_code,now

if __name__=='__main__':
    started=time.process_time();book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='CLOSED'
    assert all(j['status']=='PASS' for j in book['jobs'])
    assert book['worker_reserved_seconds']+book['utility_reserved_seconds']<=14400
    summary=json.loads((PUBLIC/'phase-summary-v1.json').read_text());assert summary['scientific_verdict']=='REVISE'
    assert json.loads((PUBLIC/'acceptance-v1.json').read_text())['check_count']>=12
    docs=[ROOT/name for name in ['README.md','START_HERE.md','GOAL.md','PLAN.md','HANDOFF.md','AGENTS.md']]
    docs+=list((ROOT/'docs/03_research').glob('R0DQR_*.md'))+list((ROOT/'docs/06_execution').glob('R0DQR_*.md'))+[PUBLIC/'README.md']
    links=0;deferred=[]
    for path in docs:
        text=path.read_text(encoding='utf-8');text=re.sub(r'```.*?```','',text,flags=re.S)
        assert not re.search('[\u0e00-\u0e7f]',text),'English documentation required: '+str(path)
        for target in re.findall(r'\]\(([^\n]+?)\)',text)+re.findall(r'href="([^"]+)"',text):
            target=target.strip('<>');parsed=urlparse(target)
            if parsed.scheme or target.startswith('#'):continue
            target=unquote(target.split('#',1)[0]);resolved=(path.parent/target).resolve()
            if resolved in {(PUBLIC/'delivery-audit-v1.json').resolve(),(PUBLIC/'storage-closeout-v1.json').resolve()}:
                deferred.append(resolved)
            else:assert resolved.exists(),str(path)+': '+target
            links+=1
    modules=list((ROOT/'tools').glob('r0dqr_*.py'))+list((ROOT/'research/taskfirst_dqr_v1').glob('*.py'))
    for path in modules:ast.parse(path.read_text(encoding='utf-8'));assert b'\r\n' not in path.read_bytes();archive_code(path)
    records=list(PUBLIC.glob('*.json'))+[ROOT/'research/manifests/chembl_taskfirst_dqr_release_20261107_v1.json']
    for path in records:json.loads(path.read_bytes());assert b'\r\n' not in path.read_bytes()
    full=json.loads((PUBLIC/'complete-return-verified-v1.json').read_text());archive=PRIVATE/'remote-return/full-task-v1.tar.gz'
    assert archive.stat().st_size==full['archive_bytes']
    # The full archive was already streamed and hashed before deletion; this
    # delivery audit does not replay that expensive processing or claim a new hash.
    size=sum(f.stat().st_size for f in PRIVATE.rglob('*') if f.is_file());free=shutil.disk_usage(PRIVATE).free
    assert size<=28*1024**3 and free>=10*1024**3
    save(PUBLIC/'storage-closeout-v1.json',{'status':'PASS_FINAL_STORAGE_BOUNDS','local_owned_bytes':size,'local_free_bytes':free,
        'local_task_cap_bytes':28*1024**3,'local_free_reserve_bytes':10*1024**3,'remote_snapshot_regular_bytes':full['total_bytes'],
        'returned_archive_bytes':full['archive_bytes'],'source_db_expanded_locally':False,'peak_storage_profiler':False})
    result={'status':'PASS_ENGLISH_DELIVERY_METADATA_AUDIT','local_links_checked':links,'python_modules_parsed':len(modules),
        'json_records_validated':len(records),'cpu_seconds':time.process_time()-started,'utc':now(),
        'source_or_activity_value_queries':0,'new_scientific_clock_or_job':False,'all_phase_jobs_terminal':True,
        'covered_by_original_retained_utility_envelope':True,'full_application_runtime_suite':'NOT_RUN_NO_PRODUCT_RUNTIME_CHANGE'}
    save(PUBLIC/'delivery-audit-v1.json',result)
    assert all(path.exists() for path in deferred)
    print(json.dumps(result))
