"""Check canonical identities and freeze accessible methods requests."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, save
from r0r_methods_mask_v1 import safety_checks

def run():
    from rdkit import Chem, rdBase
    assert rdBase.rdkitVersion=='2026.09.1'
    book=json.loads((PRIVATE/'ledger.json').read_text())
    item=next(row for row in book['attempts'] if row['source']=='molecule-identities' and row['status']=='PASS')
    molecules=json.loads((ROOT/item['output_path']).read_text())['molecules']
    wanted=set(json.loads((PRIVATE/'accepted-projection-index-v1.json').read_text())['molecule_ids'])
    assert len(molecules)<=240 and {row['molecule_chembl_id'] for row in molecules}==wanted
    protected=set(json.loads((PRIVATE/'protection-index-private.json').read_text())['canonical_smiles'])
    dispositions=[]
    for row in molecules:
        structure=row.get('molecule_structures') or {}
        smiles=structure.get('canonical_smiles')
        molecule=Chem.MolFromSmiles(smiles) if smiles else None
        if molecule is None:
            verdict='QUARANTINE_UNRESOLVED_STRUCTURE';canonical=None
        else:
            canonical=Chem.MolToSmiles(molecule,canonical=True,isomericSmiles=True)
            verdict='EXCLUDE_PROTECTED_EXACT_IDENTITY' if canonical in protected else 'NO_EXACT_PROTECTED_CANONICAL_MATCH'
        dispositions.append({'molecule_id':row['molecule_chembl_id'],'status':verdict,
                             'canonical_sha256':hashlib.sha256(canonical.encode()).hexdigest() if canonical else None})
    save(PRIVATE/'molecule-dispositions-v1.json',{'rdkit':rdBase.rdkitVersion,'records':dispositions,
        'normalization':'canonical/isomeric; no salt-charge-isotope-tautomer normalization',
        'chemical_OOD_certified':False})
    registry_path=PRIVATE/'request-registry.json'
    save(PRIVATE/'request-registry-before-methods-v1.json',json.loads(registry_path.read_text()))
    specs=json.loads(registry_path.read_text())
    access=[]
    for item in book['attempts']:
        if item['source'].startswith('paper-access-') and item['status']=='PASS':
            payload=json.loads((ROOT/item['output_path']).read_text())
            hits=payload.get('resultList',{}).get('result',[])
            allowed=hits[0] if len(hits)==1 else None
            available=bool(allowed and allowed.get('isOpenAccess')=='Y' and allowed.get('pmcid'))
            record={'document_id':item['source'].removeprefix('paper-access-'),
                    'doi':allowed.get('doi') if allowed else None,'pmcid':allowed.get('pmcid') if allowed else None,
                    'epmc_open_access':available,'other_routes_checked':False}
            access.append(record)
            if available:
                specs['methods-'+record['document_id']]={'url':'https://www.ebi.ac.uk/europepmc/webservices/rest/'+record['pmcid']+'/fullTextXML','kind':'methods_xml'}
    save(registry_path,specs)
    save(PRIVATE/'paper-access-register-v1.json',{'records':access,'non_pmc_does_not_mean_unavailable':True})
    checks=safety_checks()
    save(PRIVATE/'methods-mask-offline-checks-v1.json',checks)
    print(json.dumps({'status':'PASS_IDENTITY_CHECKS_AND_METHODS_REQUEST_FREEZE',
        'molecules':len(molecules),'molecule_gate_counts':dict(Counter(row['status'] for row in dispositions)),
        'source_documents':len(access),'pmc_open_access_documents':sum(row['epmc_open_access'] for row in access),
        'mask_checks':checks},indent=2))

if __name__=='__main__':
    guard=Guard('identity-and-methods-v1')
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',charged_to='600-second utility reservation')
