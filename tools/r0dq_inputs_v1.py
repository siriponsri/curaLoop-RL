"""Prepare authenticated label-free protection and cached Linux dependencies."""
import hashlib,json,tarfile
from pathlib import Path
from r0dq_core_v1 import LocalGuard,ROOT,PRIVATE,save,archive_code


def file_sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):digest.update(chunk)
    return digest.hexdigest()


def main():
    proposal=json.loads((ROOT/'research/manifests/chembl_taskfirst_plan_20261107_v1.json').read_text())
    pins=json.loads((ROOT/'.local/r0r-chembl-20261107-v1/protection-input-pins.json').read_text())
    registry_path=ROOT/'.local/goal4r2a3-20261106-v1/protection-inputs/family-registry-v3.json'
    assert file_sha(registry_path)==pins['registry_sha256']==proposal['historical_protection']['registry_sha256']
    registry=json.loads(registry_path.read_text())
    assert registry['assay_labels_accessed'] is False
    inputs=PRIVATE/'inputs';inputs.mkdir()
    (inputs/'family-registry-v3.json').write_bytes(registry_path.read_bytes())
    protection=ROOT/'.local/r0r-chembl-20261107-v1/protection-index-private.json'
    index=json.loads((ROOT/'docs/evidence/r0r-chembl-20261107-v1/private-artifact-index-v4.json').read_text())
    expected={r['path'].replace('\\','/'):r for r in index['artifacts']}
    row=expected[protection.relative_to(ROOT).as_posix()]
    assert file_sha(protection)==row['sha256']
    protected=json.loads(protection.read_text());assert protected['unique_canonical_structures']==4723 and protected['outcome_values_present'] is False
    save(inputs/'protected-identities.json',protected)
    assay_path=ROOT/'.local/r0-chembl-20261107-v1/014-chembl37-selected-assays.html'
    assays=json.loads(assay_path.read_text())['assays']
    old_projection=json.loads((ROOT/'.local/r0r-chembl-20261107-v1/accepted-projection-index-v1.json').read_text())
    exposures={'old_r0_assay_ids':sorted({r['assay_chembl_id'] for r in assays}),
        'old_r0_target_ids':sorted({r['target_chembl_id'] for r in assays}),
        'old_r0_document_ids':sorted({r['document_chembl_id'] for r in assays}),
        'old_r0r_molecule_ids':sorted(old_projection['molecule_ids']),
        'planning_exposed_ids':proposal['historical_protection']['additional_planning_exposed_ids'],
        'old_r0_assays_reused_as_new_candidates':False,'source_values_present':False}
    save(inputs/'exposure-register-v1.json',exposures)
    # The Linux assets are an already returned, pinned CPython3.12 dependency
    # tree, not a new package download or a global installation.
    vendor=ROOT/'.local/goal4r2a3-20261106-v1/linux-vendor'
    returns=json.loads((ROOT/'.local/goal4r2a3-20261106-v1/remote-return/full-v1/manifest.json').read_text())
    expected_vendor={r['path']:r for r in returns['files'] if r['path'].startswith('private-inputs/linux-vendor/')}
    chosen=[]
    tops={'numpy','numpy.libs','numpy-2.3.5.dist-info','rdkit','rdkit.libs','rdkit-2026.9.1.dist-info'}
    for path in sorted(vendor.rglob('*')):
        if not path.is_file() or path.relative_to(vendor).parts[0] not in tops:continue
        assert not path.is_symlink()
        rel=path.relative_to(vendor).as_posix();old=expected_vendor['private-inputs/linux-vendor/'+rel]
        digest=file_sha(path);assert digest==old['sha256'] and path.stat().st_size==old['bytes']
        chosen.append((path,'vendor/'+rel,digest,path.stat().st_size))
    assert chosen and sum(r[3] for r in chosen)<1024**3
    archive=PRIVATE/'vendor-inputs-v1.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=1) as tar:
        for path,rel,_,_ in chosen:tar.add(path,arcname=rel,recursive=False)
        for path in sorted(inputs.glob('*.json')):tar.add(path,arcname='inputs/'+path.name,recursive=False)
    manifest={'status':'PASS_PINNED_INPUTS_AND_OFFLINE_VENDOR','vendor_python_abi':'CPython3.12 Linux',
        'required_rdkit_runtime_version':'2026.09.1','source_file_count':len(chosen),'source_bytes':sum(r[3] for r in chosen),
        'archive_bytes':archive.stat().st_size,'archive_sha256':file_sha(archive),
        'files':[{'path':rel,'sha256':digest,'bytes':size} for _,rel,digest,size in chosen],
        'registry_sha256':pins['registry_sha256'],'protected_canonical_identities':4723,
        'network_packages_downloaded':False,'global_environment_changed':False}
    save(PRIVATE/'vendor-inputs-manifest-v1.json',manifest)
    archive_code(ROOT/'tools/r0dq_projection_v1.py')
    print(json.dumps({k:manifest[k] for k in ['status','source_file_count','source_bytes','archive_bytes','protected_canonical_identities']}))


if __name__=='__main__':
    guard=LocalGuard('pinned-inputs-v1',cpu_seconds=180,wall=600,memory_mib=256)
    try:main()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
