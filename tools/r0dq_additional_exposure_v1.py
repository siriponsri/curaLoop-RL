"""Authenticate known exposed structures without parsing historical labels."""
import gzip,hashlib,json,re,subprocess,sys
from pathlib import Path
from r0dq_core_v1 import ROOT,PRIVATE,REMOTE,HOST,SSH_OPTIONS,save,archive_code
from r0dq_remote_job_v1 import ssh
from r0dq_transport_guard_v1 import TransportGuard

def main():
    sys.path.insert(0,str(ROOT/'.venv/Lib/site-packages'))
    from rdkit import Chem,rdBase,RDLogger
    assert rdBase.rdkitVersion=='2026.09.1';RDLogger.DisableLog('rdApp.*')
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    def canonical(text):
        assert len(text)<4096
        mol=Chem.MolFromSmiles(text)
        return Chem.MolToSmiles(mol,canonical=True,isomericSmiles=True) if mol else None
    prior=json.loads((ROOT/'research/configs/goal_02_real_data_v1.json').read_text())
    refs=set();pins=[]
    for assay in ['ahr','pparg','p53']:
        path=ROOT/f'research/raw_data/ncats-development-20261104/{assay}.smiles'
        digest=sha(path);assert digest==prior['raw_source_sha256'][assay]
        pins.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest,'projection':'First tab-separated SMILES field only'})
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                smi=canonical(line.split('\t',1)[0].rstrip('\r\n'))
                if smi:refs.add(smi)
    path=ROOT/'src/curaloop/resources/hiv_replay_v1.json.gz';digest=sha(path)
    assert digest==json.loads((ROOT/'src/curaloop/resources/hiv_manifest.json').read_text())['resource_sha256']
    assert path.stat().st_size<8*1024**2
    with gzip.open(path,'rb') as stream:raw=stream.read(32*1024**2)
    assert len(raw)<32*1024**2
    # Fixed JSON string-field projector: decode canonical_smiles strings only.
    # No historical object/number/label parser is invoked.
    matches=re.findall(rb'"canonical_smiles"\s*:\s*("(?:[^"\\]|\\.)*")',raw)
    assert matches
    for value in matches:
        smi=canonical(json.loads(value))
        if smi:refs.add(smi)
    pins.append({'path':path.relative_to(ROOT).as_posix(),'sha256':digest,'projection':'canonical_smiles string tokens only; numeric/object labels never parsed'})
    assert len(refs)==8678,'Prior identity count must agree with frozen preparation manifest'
    policy=json.loads((ROOT/'research/configs/goal4r2a3_policy_v1.json').read_text());count=0
    for version,expected in policy['protected_manifests'].items():
        folder=ROOT/'research/raw_data/external-benchmarks/fs-mol-0.1'/('feature-cohort-'+version)
        manifest=folder/'manifest.json';assert sha(manifest)==expected
        for row in json.loads(manifest.read_text())['selected_assays']:
            if row['role']=='final':continue
            feature=folder/row['feature_file'];assert sha(feature)==row['feature_sha256']
            obj=json.loads(feature.read_text());assert obj['outcome_values_present'] is False and obj['role'] in {'development','validation'}
            for record in obj['records']:
                assert set(record)=={'candidate_id','canonical_smiles','source_row','morgan_on_bits','scaffold'}
                smi=record['canonical_smiles'];assert record['candidate_id']=='s-'+hashlib.sha256(smi.encode()).hexdigest();refs.add(smi)
            pins.append({'path':feature.relative_to(ROOT).as_posix(),'sha256':row['feature_sha256'],'role':obj['role'],'projection':'Verified label-free canonical structure field'})
            count+=1
    artifact={'schema':'curaloop.r0dq.known-exposed-identities.v1','canonical_smiles':sorted(refs),'prior_reference_identity_count':8678,
        'nonfinal_feature_files_verified':count,'source_pins':pins,'old_activity_or_final_outcome_values_parsed':False,
        'universal_pretraining_or_chemical_OOD_clearance':False,'rdkit':rdBase.rdkitVersion}
    target=PRIVATE/'additional-exposure-v1.json';assert not target.exists();save(target,artifact)
    remote=REMOTE+'/additional-exposure-v1.json'
    ssh('import json;from pathlib import Path;p=Path('+repr(remote)+');assert not p.exists() and not p.is_symlink();print(json.dumps({"status":"FRESH_ADDITIONAL_IDENTITY_INPUT"}))')
    ret=subprocess.run(['scp',*SSH_OPTIONS,str(target),HOST+':'+remote],capture_output=True,timeout=60);assert ret.returncode==0
    pin={'sha256':sha(target),'bytes':target.stat().st_size,'canonical_identity_count':len(refs),'nonfinal_feature_files_verified':count}
    save(PRIVATE/'additional-exposure-pin-v1.json',pin)
    print(json.dumps({'status':'PASS_AUTHENTICATED_ADDITIONAL_IDENTITIES_TRANSFERRED',**pin}))

if __name__=='__main__':
    guard=TransportGuard('additional-exposed-identities-v1',cpu_seconds=180,wall=600,memory_mib=512)
    try:main()
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
