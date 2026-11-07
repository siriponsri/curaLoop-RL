"""Authenticate carried identities, source metadata and offline vendor inputs."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
from r0dqr_core_v1 import ROOT,PRIVATE,PRIOR,REMOTE,HOST,SSH_OPTIONS,save,sha,archive_code
from r0dqr_transport_guard_v1 import TransportGuard
from r0dqr_rpc_v1 import ssh

def main():
    assert json.loads((PRIVATE/'source-reuse-v1.json').read_text())['status']=='PASS_REUSED_PINNED_ARCHIVE_WITH_FULL_OUTER_HASH'
    inputs=PRIVATE/'inputs';inputs.mkdir(exist_ok=False)
    prior_files=PRIOR/'remote-return/files';returned=json.loads((PRIOR/'remote-return/export-terminal/manifest.json').read_text())
    pins={r['path']:r for r in returned['files']}
    for rel in ['inputs/family-registry-v3.json','inputs/protected-identities.json','inputs/exposure-register-v1.json','inputs/additional-exposure-v1.json']:
        path=prior_files/rel;assert sha(path)==pins[rel]['sha256'];(inputs/Path(rel).name).write_bytes(path.read_bytes())
    framepath=prior_files/'jobs/frame-v3/frame-frozen.json';identpath=prior_files/'jobs/support-v1/identity-dispositions.json'
    assert sha(framepath)==pins['jobs/frame-v3/frame-frozen.json']['sha256'] and sha(identpath)==pins['jobs/support-v1/identity-dispositions.json']['sha256']
    frame=json.loads(framepath.read_text());identities=json.loads(identpath.read_text())
    carry={'schema':'curaloop.r0dqr.carried-exposure.v1','prior_frame_sha256':sha(framepath),'prior_identity_sha256':sha(identpath),
        'assay_chembl_ids':sorted({a['chembl_id'] for a in frame['assays']}),
        'target_chembl_ids':sorted({a['target_chembl_id'] for a in frame['assays']}),
        'document_chembl_ids':sorted({a['document_chembl_id'] for a in frame['assays']}),
        'canonical_sha256':sorted({r['canonical_sha256'] for r in identities['records'] if r['canonical_sha256']}),
        'old_numeric_activity_or_presence_flags_read':False,'unknown_final_mapping_must_be_quarantined':True}
    save(inputs/'r0dq-carried-exposure-v1.json',carry)
    access=json.loads((PRIOR/'oa-access-v2.json').read_text())
    save(inputs/'prior-access-cache-v1.json',{'records':access['records'],'repeat_http_authorized':False})
    snapshots=[]
    for rel in ['.local/r0-chembl-20261107-v1/ledger.json','.local/r0r-chembl-20261107-v1/ledger.json','.local/chembl-taskfirst-dq-20261107-v1/ledger.json']:
        path=ROOT/rel;old=json.loads(path.read_text());snapshots.append({'path':rel,'sha256':sha(path),
            'stopped_sources':old.get('stopped_sources',[]),'status':old['status']})
    save(inputs/'old-ledger-pins-and-stops-v1.json',{'records':snapshots,'all_stops_retained':True})
    vendor=PRIOR/'vendor-inputs-v1.tar.gz';vm=json.loads((PRIOR/'vendor-inputs-manifest-v1.json').read_text())
    assert sha(vendor)==vm['archive_sha256'];save(PRIVATE/'vendor-manifest-v1.json',vm)
    package=PRIVATE/'dqr-inputs-v1.tar.gz'
    with tarfile.open(package,'w:gz',compresslevel=1) as tar:
        for path in sorted(inputs.glob('*.json')):tar.add(path,arcname='inputs/'+path.name,recursive=False)
    artifacts=[{'local':str(vendor),'remote':'vendor-inputs-v1.tar.gz','bytes':vendor.stat().st_size,'sha256':sha(vendor)},
        {'local':str(package),'remote':package.name,'bytes':package.stat().st_size,'sha256':sha(package)}]
    for row in artifacts:
        remote=REMOTE+'/'+row['remote']
        ssh('import os,json;from pathlib import Path;p=Path('+repr(remote)+');assert p.parent.resolve()==p.parent and p.parent.stat().st_uid==os.getuid() and not p.exists();print(json.dumps({"status":"FRESH_INPUT_TARGET"}))')
        result=subprocess.run(['scp',*SSH_OPTIONS,row['local'],HOST+':'+remote],capture_output=True,timeout=120);assert result.returncode==0
    save(PRIVATE/'input-transfer-v1.json',{'status':'PASS_OPAQUE_INPUT_TRANSPORT_PENDING_REMOTE_HASH','files':artifacts,
        'prior_protected_canonical_identities':4723,'additional_known_exposed_identities':10151,
        'new_carried_identity_hashes':len(carry['canonical_sha256']),'activity_values_or_presence_flags_included':False})
    print(json.dumps({'status':'PASS_OPAQUE_INPUT_TRANSPORT_PENDING_REMOTE_HASH','files':len(artifacts),'carried_identity_hashes':len(carry['canonical_sha256'])}))

if __name__=='__main__':
    guard=TransportGuard('authenticated-inputs-v1',cpu_seconds=90,wall=360,memory_mib=256)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
