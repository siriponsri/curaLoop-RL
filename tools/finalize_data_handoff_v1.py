"""Validate the metadata/prompt handoff; no source parsing, remote call or study run."""
import argparse,ast,hashlib,json,re,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.local/data-inventory-20261107-v1'
PUBLIC=ROOT/'docs/evidence/local-data-inventory-20261107-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj,allow_identical=False):
    payload=(json.dumps(obj,indent=2,allow_nan=False)+'\n').encode()
    if path.exists():
        if allow_identical and path.read_bytes()==payload:return
        raise FileExistsError('Refusing to replace existing handoff evidence: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(payload)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',type=int,default=1)
    revision=parser.parse_args().revision
    if revision<1:raise ValueError('Positive validation revision required')
    validation_path=PUBLIC/('handoff-validation-v'+str(revision)+'.json')
    if validation_path.exists():raise FileExistsError(str(validation_path))
    started=time.process_time();raw=json.loads((PRIVATE/'file-metadata-v1.json').read_text())
    summary=dict(raw['summary']);assert summary['status']=='COMPLETE_WITHIN_DECLARED_SCOPE' and not summary['errors']
    summary['matching_apparent_bytes']=summary.pop('matching_physical_bytes')
    summary['physical_allocated_disk_bytes']='NOT_MEASURED'
    summary['byte_metric']='Sum of matching files st_size; no hard-link/sparse/compression allocation deduplication'
    summary['supersedes']='filesystem-summary-v1.json byte metric label only; no changed count, rescan or source read'
    save(PUBLIC/'filesystem-summary-v2.json',summary,allow_identical=True)
    checks=['complete_metadata_scan_with_declared_scope_and_exclusions','apparent_file_bytes_not_claimed_as_unique_data_or_disk_allocation']
    integrity=json.loads((PUBLIC/'small-file-integrity-v1.json').read_text());assert integrity['file_count']==28
    assert integrity['fsmol_assays_by_role']=={'development':6,'validation':2,'final':16}
    assert sum(integrity['fsmol_structure_rows_by_role_from_existing_manifest'].values())==6630
    checks.append('28_existing_small_file_digest_matches_and_fsmol_manifest_counts')
    lengths={
        'research/raw_data/external-benchmarks/fs-mol-0.1/fsmol.tar':4871086080,
        '.local/chembl-taskfirst-dqr-20261107-v1/source/chembl_37_sqlite.tar.gz':5764252857,
        '.local/chembl-taskfirst-dq-20261107-v1/remote-return/full-task-v1.tar.gz':11070386037,
        '.local/chembl-taskfirst-dqr-20261107-v1/remote-return/full-task-v1.tar.gz':11071998021,
        'research/raw_data/external-benchmarks/mf-pcba-2023/metadata/ci2c01569.pdf':3271821,
        'research/raw_data/external-benchmarks/mf-pcba-2023/metadata/ci2c01569_si_001.pdf':4674245}
    for path,size in lengths.items():assert (ROOT/path).is_file() and (ROOT/path).stat().st_size==size
    checks.append('large_archives_and_mfpcba_pdfs_current_size_only_no_fresh_hash_claim')
    for row in json.loads((PRIVATE/'old-ledger-pins-v1.json').read_text())['records']:assert sha(ROOT/row['path'])==row['sha256']
    checks.append('all_six_old_ledger_hashes_unchanged')
    sources=['src/curaloop/resources/hiv_manifest.json','research/manifests/ncats_development_tasks_v1.json',
        'docs/03_research/FSMOL_DATASET_CARD_V2.md','docs/evidence/plan-a-20261105-v1/feature-cohort-v2-result.json',
        'docs/03_research/GOAL4_RESULTS_V1.md','docs/03_research/GOAL4R1_RESULTS_V1.md',
        'docs/03_research/R0DQ_QUALIFICATION_RESULTS_20261107.md','docs/03_research/R0DQR_TAXONOMY_TASK_FEASIBILITY_20261107.md',
        'docs/03_research/GOAL4R2A3_QUALIFICATION_V1.md','docs/06_execution/B_POTENTIAL_DECISION_LRBC_20261106.md',
        'research/manifests/goal4r2a2_benchmark_readiness_v1.json','docs/evidence/r0r-chembl-20261107-v1/interim-summary-v6.json']
    save(PUBLIC/'evidence-source-pins-v1.json',{'sources':[{'path':p,'sha256':sha(ROOT/p)} for p in sources],
        'current_web_or_source_revalidation':False,'scope':'Existing authored cards/manifests/aggregate receipts only'},allow_identical=True)
    docs=[ROOT/'docs/03_research/LOCAL_DATA_INVENTORY_20261107.md',ROOT/'docs/02_literature/DEEP_RESEARCH_PROMPT_20261107.md',PUBLIC/'README.md']
    links=0;future=[]
    for path in docs:
        text=path.read_text();assert not re.search('[\u0e00-\u0e7f]',text)
        for target in re.findall(r'\]\(([^\n]+?)\)',text):
            target=target.strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',target) or target.startswith('#'):continue
            dest=(path.parent/target.split('#',1)[0]).resolve()
            if dest==validation_path.resolve():future.append(dest)
            else:assert dest.exists(),str(path)+': '+target
            links+=1
    modules=[ROOT/'tools/inventory_existing_data_v1.py',ROOT/'tools/inventory_data_integrity_v1.py',ROOT/'tools/finalize_data_handoff_v1.py']
    for path in modules:ast.parse(path.read_text())
    checks.append('english_handoff_local_links_and_helper_syntax')
    result={'status':'PASS_LOCAL_DATA_INVENTORY_AND_DEEP_RESEARCH_HANDOFF','checks':checks,'local_links_checked':links,
        'prompt_words':len(docs[1].read_text().split()),'document_sha256':{str(p.relative_to(ROOT)):sha(p) for p in docs[:2]},
        'helper_sha256':{str(p.relative_to(ROOT)):sha(p) for p in modules},
        'raw_dataset_rows_or_labels_loaded':False,'old_final_outcomes_opened':False,'source_http_or_ssh':0,
        'new_scientific_budget_clock_split_or_model_run':False,'independent_semantic_or_biology_review':'NOT_RUN',
        'cpu_seconds':time.process_time()-started,'utc':datetime.now(timezone.utc).isoformat()}
    result['validation_revision']=revision
    result['supersedes']='handoff-validation-v1.json document/helper hashes after editorial and navigation updates' if revision==2 else None
    save(validation_path,result);assert all(p.exists() for p in future);print(json.dumps(result))
if __name__=='__main__':main()
