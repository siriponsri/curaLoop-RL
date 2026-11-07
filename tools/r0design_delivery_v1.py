"""Normal English delivery audit; no scientific execution or source access."""
import ast,json,re,time
from pathlib import Path
from r0design_core_v1 import ROOT,PRIVATE,PUBLIC,save,sha,archive_code,now

if __name__=='__main__':
    started=time.process_time();book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='CLOSED'
    assert all(j['status']=='PASS' for j in book['jobs']) and book['worker_reserved_seconds']+900<=3600
    summary=json.loads((PUBLIC/'phase-readout-v1.json').read_text())
    for rel,digest in summary['documents_sha256'].items():assert sha(ROOT/rel)==digest
    for pin in json.loads((PRIVATE/'input-pins-v1.json').read_text())['old_ledgers']:assert sha(ROOT/pin['path'])==pin['sha256']
    docs=[ROOT/p for p in ['README.md','START_HERE.md','GOAL.md','PLAN.md','HANDOFF.md','AGENTS.md']]
    docs+=list((ROOT/'docs/03_research').glob('R0_DESIGN_REVIEW*.md'))+list((ROOT/'docs/06_execution').glob('R0_DESIGN_REVIEW*.md'))
    docs+=[ROOT/'docs/06_execution/R0_SUPPORT_CENSUS_PROPOSAL_20261107.md',PUBLIC/'README.md']
    links=0;deferred=[]
    for path in docs:
        text=path.read_text(encoding='utf-8');assert not re.search('[\u0e00-\u0e7f]',text)
        text=re.sub(r'```.*?```','',text,flags=re.S)
        for target in re.findall(r'\]\(([^\n]+?)\)',text)+re.findall(r'href="([^"]+)"',text):
            target=target.strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            target=target.split('#',1)[0];resolved=(path.parent/target).resolve()
            if resolved==(PUBLIC/'delivery-audit-v1.json').resolve():deferred.append(resolved)
            else:assert resolved.exists(),str(path)+': '+target
            links+=1
    modules=list((ROOT/'tools').glob('r0design_*.py'))
    for path in modules:
        ast.parse(path.read_text());assert b'\r\n' not in path.read_bytes();archive_code(path)
    configs=[ROOT/'research/configs/r0_design_review_protocol_20261107_v1.json',ROOT/'research/manifests/r0_design_review_release_20261107_v1.json']
    for p in list(PUBLIC.glob('*.json'))+configs:json.loads(p.read_bytes());assert b'\r\n' not in p.read_bytes()
    assert configs[0].read_bytes()==(PUBLIC/'protocol-proposed-v1.json').read_bytes()
    private_bytes=sum(p.stat().st_size for p in PRIVATE.rglob('*') if p.is_file());assert private_bytes<64*1024**2
    result={'status':'PASS_ENGLISH_DESIGN_DELIVERY_AUDIT','local_links_checked':links,'modules_parsed':len(modules),
        'frozen_protocol_and_document_pins_verified':True,'old_ledgers_unchanged':True,'private_review_bytes':private_bytes,
        'all_review_jobs_terminal':True,'source_http_ssh_or_data_queries':0,'new_scientific_clock':False,
        'covered_by_original_retained_utility_envelope':True,'cpu_seconds':time.process_time()-started,'utc':now(),
        'independent_domain_review':'NOT_RUN','application_runtime_suite':'NOT_RUN_NO_PRODUCT_RUNTIME_CHANGE'}
    save(PUBLIC/'delivery-audit-v1.json',result);assert all(p.exists() for p in deferred);print(json.dumps(result))
