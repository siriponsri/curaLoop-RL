"""Normal delivery metadata audit after closure; no dataset processing or replay."""
import ast,hashlib,json,re,shutil,time
from pathlib import Path
from urllib.parse import unquote,urlparse
from r0dq_core_v1 import ROOT,PRIVATE,PUBLIC,save,archive_code,now

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()

if __name__=='__main__':
    started=time.process_time();book=load(PRIVATE/'ledger.json');assert book['status']=='CLOSED'
    assert all(r['status'] not in {'ADMITTED','RUNNING','NOT_RECONCILED'} for r in book['jobs'])
    assert book['worker_reserved_seconds']+book['utility_reserved_seconds']==32910<=57600
    summary=load(PUBLIC/'qualification-summary-v2.json');assert summary['scientific_verdict']=='PILOT_ONLY_REVISE'
    assert load(PUBLIC/'qualification-acceptance-v1.json')['status']=='PASS_REAL_DERIVED_ARTIFACT_INVARIANTS'
    docs=[ROOT/name for name in ['README.md','START_HERE.md','GOAL.md','PLAN.md','HANDOFF.md','AGENTS.md']]
    docs+=list((ROOT/'docs/03_research').glob('R0DQ_*.md'))+list((ROOT/'docs/06_execution').glob('R0DQ_*.md'))+[PUBLIC/'README.md']
    links=0
    for path in docs:
        text=path.read_text(encoding='utf-8');text=re.sub(r'```.*?```','',text,flags=re.S)
        for target in re.findall(r'\]\(([^\n]+?)\)',text)+re.findall(r'href="([^"]+)"',text):
            target=target.strip('<>');parsed=urlparse(target)
            if parsed.scheme or target.startswith('#'):continue
            target=unquote(target.split('#',1)[0]);assert (path.parent/target).exists(),str(path)+': '+target;links+=1
    modules=list((ROOT/'tools').glob('r0dq_*.py'))+list((ROOT/'research/taskfirst_dq_v1').glob('*.py'))
    for path in modules:ast.parse(path.read_text(encoding='utf-8'))
    jsons=list(PUBLIC.glob('*.json'))+[ROOT/'research/manifests/chembl_taskfirst_dq_release_20261107_v1.json']
    for path in jsons:
        raw=path.read_bytes();json.loads(raw);assert b'\r\n' not in raw
    assert all(r['status']!='NOT_RECONCILED' for r in load(PUBLIC/'resource-receipts-v2.json')['receipts'])
    original=load(PRIVATE/'development-oa-access-v2-resource.json')
    assert original['status']=='PASS' and original['entry_source_sha256']==sha(ROOT/'tools/r0dq_access_v2.py')
    save(PUBLIC/'context-projection-validation-v2.json',{'status':'PASS_EXECUTED_PROCEDURAL_AND_ISOTOPE_CHECKS',
        'basis':'Existing successful access-v2 controller executes six procedural fixtures and an isotope-identifier assertion before requests',
        'entry_sha256':original['entry_source_sha256'],'projection_sha256':sha(ROOT/'tools/r0dq_context_projection_v1.py'),
        'new_test_run':False,'source_bodies_reviewed':0,'independent_semantic_review':False})
    full=load(PUBLIC/'complete-return-verified-v1.json');archive=PRIVATE/'remote-return/full-task-v1.tar.gz'
    assert archive.stat().st_size==full['archive_bytes']
    local_bytes=sum(f.stat().st_size for f in PRIVATE.rglob('*') if f.is_file());free=shutil.disk_usage(PRIVATE).free
    assert local_bytes<=28*1024**3 and free>=10*1024**3
    save(PUBLIC/'storage-closeout-v1.json',{'status':'PASS_FINAL_STORAGE_BOUNDS','local_owned_bytes':local_bytes,
        'local_free_bytes':free,'local_task_cap_bytes':28*1024**3,'local_reserve_bytes':10*1024**3,
        'remote_regular_task_snapshot_bytes':full['total_bytes'],'returned_archive_bytes':full['archive_bytes'],
        'peak_storage_profiler':False,'source_db_expanded_locally':False})
    archive_code(Path(__file__))
    result={'status':'PASS_DELIVERY_METADATA_AUDIT','local_links_checked':links,'python_modules_parsed':len(modules),
        'existing_json_records_validated':len(jsons),'reporting_cpu_seconds':time.process_time()-started,
        'source_or_activity_values_opened':False,'new_scientific_execution_or_clock':False,'utc':now(),
        'full_application_runtime_suite':'NOT_RUN; no application runtime change','all_current_book_jobs_terminal':True}
    save(PUBLIC/'delivery-audit-v1.json',result);print(json.dumps(result))
