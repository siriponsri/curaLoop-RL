"""Read-only completion audit plus aggregate-only English delivery receipt."""
import ast,csv,hashlib,json,math,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_live_readback_v4 import pin_local_reader
TASK=ROOT/'.local/m2-costed-20261108-v2';PUB=ROOT/'docs/evidence/m2-costed-20261108-v2'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def new(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def main():
    pin_local_reader()
    revision=int(sys.argv[1]) if len(sys.argv)>1 else 1
    assert 1<=revision<=9
    output=PUB/f'delivery-validation-v{revision}.json'
    ledger=read(TASK/'ledger.json');result=read(PUB/'aggregate-results-v1.json');cpu=read(PUB/'cpu-accounting-v1.json')
    status=read(ROOT/'research/configs/m2_costed_status_20261108_v2.json')
    disposition=read(ROOT/'research/manifests/conditional_m3_p1_j1_disposition_20261109_v1.json')
    assert ledger['status']=='CLOSED_COMPLETE_FOR_OWNER_REVIEW' and not any(j['state']=='RESERVED' for j in ledger['jobs'])
    assert ledger['method_decision']==result['method_decision']==status['method_efficacy']=='INCONCLUSIVE'
    assert result['technical_closeout']==result['remote_exact_cleanup']=='PASS'
    assert result['counts']=={'prefix':48,'branch':1152,'tuning':576,'main':1920,'ablation':180,'transfer':288}
    assert result['audit']['verified_units']==4164 and ledger['attempted_units']==4254
    assert cpu['successful_units_this_release']==4248 and cpu['retained_not_dispatched_attempts']==6
    assert cpu['unique_synthetic_contexts_including_previous_profile']==96
    assert ledger['prior_retained_seconds']+sum(ledger['bucket_reserved_seconds'].values())==cpu['cumulative_charged_seconds']==114225<=172800
    assert all(ledger['bucket_reserved_seconds'][k]<=v for k,v in ledger['bucket_caps_seconds'].items())
    assert datetime.fromisoformat(ledger['closed_utc'])<datetime.fromisoformat(ledger['deadline_utc'].replace('Z','+00:00'))
    for row in ledger['jobs']:
        if row['state']=='CHARGED_UTILITIES_ENVELOPE':continue
        path=TASK/'jobs'/row['job']/'resource.json';r=read(path)
        assert sha(path)==row['resource_sha256'] and r['status']==row['state'] and r['attempt']==row['job']
        assert math.isfinite(r['cpu_seconds']) and 0<=r['cpu_seconds']<=row['reservation_seconds']
    assert read(TASK/'jobs/closeout-audit-v1/result.json')['status']=='PASS_COMPLETE_M2_CLOSEOUT_AUDIT'
    returned=read(TASK/'remote-return/verified-v1.json')
    assert returned==read(PUB/'complete-return-verified-v1.json') and returned['file_count']==27454
    assert returned['status']=='PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD'
    archive=TASK/'remote-return/export/full-task-v1.tar.gz'
    assert archive.stat().st_size==77321791 and sha(archive)==returned['archive_sha256']
    assert read(PUB/'scoped-delete-v1.json')['status']=='PASS_EXACT_DELETE_AFTER_FULL_RETURN'
    assert read(PUB/'fresh-absence-v1.json')['status']=='PASS_FRESH_EXACT_ABSENCE'
    preservation=read(PUB/'old-history-unchanged-v1.json')
    assert all(sha(ROOT/n)==h for n,h in preservation['paths'].items())
    older=read(ROOT/'docs/evidence/m2-selective-compute-20261108-v1/old-history-unchanged-v1.json')
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in older['records'])
    code=read(TASK/'code-stage-03.json');assert all(sha(ROOT/n)==h for n,h in code['code_pins'].items())
    scope=read(ROOT/'research/manifests/m2_data_scope_20261108_v1.json')
    assert len(scope['tasks'])==6 and all(sha(ROOT/t['private_input_path'])==t['expected_input_sha256'] for t in scope['tasks'])
    assert not ledger['final_outcomes_opened'] and not status['final_outcomes_opened'] and not status['m3_released']
    assert disposition['status']=='NOT_ACTIVATED_M2_ENTRY_NOT_MET' and disposition['m2_ledger_sha256']==sha(TASK/'ledger.json')
    assert not disposition['fresh_clock_started'] and not disposition['new_m3_root_created'] and not disposition['final_payloads_opened']
    assert not list((ROOT/'.local').glob('m3-*')),'UNEXPECTED_NEW_M3_ROOT'
    approval=read(ROOT/'research/manifests/conditional_m3_p1_j1_owner_approval_20261109_v1.json')
    assert approval['owner_option']=='A' and not approval['clock_started'] and not approval['protected_payload_access_now']
    summaries={(r['predictor'],r['regime'],r['arm']):r for r in result['main_summaries']};assert len(summaries)==32
    for r in result['paired_contrasts']:
        left,right=r['contrast'].split('-');p,c=r['predictor'],r['regime']
        assert abs(summaries[p,c,left]['new_positives']-summaries[p,c,right]['new_positives']-r['mean_delta_new_positives'])<1e-12
    for name,expected in [('main-summary-v1.csv',32),('discovery-curves-v1.csv',1056)]:
        with (PUB/name).open(encoding='utf-8',newline='') as f:assert len(list(csv.DictReader(f)))==expected
    qa=read(PUB/'figure-qa-v1.json');assert qa['status']=='PASS_STRUCTURAL_AND_FINAL_RENDER_REVIEW'
    assert qa['figure_count']==3 and qa['export_count']==9
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in qa['manual_review']['reviewed_files'])
    normalized=read(PUB/'svg-delivery-normalization-v1.json')
    assert normalized['status']=='PASS_FORMAT_ONLY_SVG_DELIVERY_NORMALIZATION' and not normalized['png_pdf_and_source_numbers_changed']
    assert len(normalized['files'])==3
    assert all(sha(ROOT/r['path'])==r['delivered_sha256'] and r['preflight']['passed'] for r in normalized['files'])
    tests=read(PUB/'constructed-checks-v1.json')
    assert len(tests['engine']['checks'])==11 and len(tests['analysis']['checks'])==3 and len(tests['pairing_supplement']['checks'])==3
    assert len(tests['transport']['checks'])==5
    docs=['README.md','GOAL.md','PLAN.md','START_HERE.md','HANDOFF.md','AGENTS.md','docs/00_project/CLAIM_LEDGER.md',
      'docs/01_paper/README.md','docs/01_paper/MANUSCRIPT.md','docs/01_paper/SUBMISSION_READINESS_20261104.md',
      'docs/01_paper/M2_EVIDENCE_POSITION_20261109.md','docs/03_research/M2_COSTED_RESULTS_20261108.md',
      'docs/06_execution/M2_OWNER_CHECKPOINT_20261108.md','docs/06_execution/M2_COSTED_EXECUTION_NOTES_20261108.md',
      'docs/06_execution/M2_TELEMETRY_REPAIR_20261109.md','docs/evidence/m2-costed-20261108-v2/README.md']
    broken=[];checked=0
    for name in docs:
        path=ROOT/name;text=path.read_text(encoding='utf-8');assert not re.search('[\u0e00-\u0e7f]',text),name
        links=re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)',text)+re.findall(r'href="([^"]+)"',text)
        for target in links:
            target=target.strip('<>');target=unquote(target.split('#',1)[0].split('?',1)[0])
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target):continue
            checked+=1
            resolved=(path.parent/target).resolve()
            if resolved!=output.resolve() and not resolved.exists():broken.append({'source':name,'target':target})
    assert not broken,broken
    manuscript=(ROOT/'docs/01_paper/MANUSCRIPT.md').read_text(encoding='utf-8')
    chapters=sorted((ROOT/'docs/01_paper').glob('[0-9][0-9]_*.md'));assert len(chapters)==10
    for chapter in chapters:
        transformed=re.sub(r'^(#{1,5}) ',r'#\1 ',chapter.read_text(encoding='utf-8'),flags=re.M).rstrip()
        assert transformed in manuscript,chapter.name
    changed=subprocess.run(['rtk','proxy','git','diff','--name-only'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    assert not any(re.match(r'docs/01_paper/[0-9][0-9]_',n) for n in changed),'HISTORICAL_CHAPTER_MODIFIED'
    assert not any(n.startswith('.local/') or n.startswith('research/raw_data/') for n in changed)
    for name in ['tools/m2c_closeout_audit_v2.py','tools/m2c_figures_v2.py','tools/m2c_write_report_v2.py','tools/m2c_check_delivery_v2.py']:
        ast.parse((ROOT/name).read_text(encoding='utf-8'))
    record={'status':'PASS_M2_COMPLETE_CLOSEOUT_DELIVERY_AUDIT','utc':datetime.now(timezone.utc).isoformat(),
      'validation_revision':revision,'supersedes':('delivery-validation-v1.json after final publication metadata and format-only SVG normalization' if revision>1 else None),
      'method_decision':'INCONCLUSIVE','scientific_gate':'NOT_PASSED','technical_closeout':'PASS','closed_ledger':True,
      'successful_fresh_units':4248,'biological_units':4164,'retained_not_dispatched_attempts':6,
      'cumulative_charged_cpu_seconds':114225,'original_cap_seconds':172800,'prior_history_sources_rechecked':len(older['records']),
      'returned_task_files':27454,'return_scope':'actual full export/extraction/two hash reads previously verified; archive digest reread during delivery',
      'remote_exact_absence':'PASS_AFTER_VERIFIED_RETURN','figures':3,'exports':9,'raster_visual_reviews':6,
      'local_file_links_checked':checked,'english_documents_checked':len(docs),'historical_chapters_assembled_unchanged':10,
      'conditional96h_grant_activated':False,'final_outcomes_opened':False,'new_method_p1_j1_executed':False,
      'product_runtime_tests':'NOT_RUN_NO_APPLICATION_RUNTIME_CHANGE','journal_submission':False,
      'scope':'No new molecular execution, dataset intake or source-role change; delivery/audit only.',
      'current_document_sha256':{n:sha(ROOT/n) for n in docs},
      'source_sha256':{n:sha(ROOT/n) for n in ['tools/m2c_closeout_audit_v2.py','tools/m2c_figures_v2.py','tools/m2c_write_report_v2.py','tools/m2c_check_delivery_v2.py']}}
    new(output,record);assert output.is_file()
    print(json.dumps({k:v for k,v in record.items() if not isinstance(v,dict)}))


if __name__=='__main__':main()
