"""Verify frozen label-free protection and freeze the R0-R case selection."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import urllib.parse
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, ledger, save

sys.path.insert(0,str(ROOT))
from research.qualification_v1.contracts import protected_identity_index, family_gate

def run():
    from rdkit import Chem, rdBase
    assert rdBase.rdkitVersion == '2026.09.1'
    assert Chem.MolToSmiles(Chem.MolFromSmiles('C(C)O'),canonical=True,isomericSmiles=True) == 'CCO'
    old = ROOT / '.local/goal4r2a3-20261106-v1'
    policy = json.loads((ROOT/'research/configs/goal4r2a3_policy_v1.json').read_text())
    registry_path = old/'protection-inputs/family-registry-v3.json'
    assert hashlib.sha256(registry_path.read_bytes()).hexdigest() == policy['registry_sha256']
    registry = json.loads(registry_path.read_text())
    versions, pins = [], []
    for version,digest in policy['protected_manifests'].items():
        folder = old/'protection-inputs'/version
        manifest = folder/'manifest.json'
        assert hashlib.sha256(manifest.read_bytes()).hexdigest() == digest
        pins.append({'path':str(manifest.relative_to(ROOT)),'sha256':digest})
        for row in json.loads(manifest.read_text())['selected_assays']:
            if row['role'] != 'final':
                continue
            path = folder/row['feature_file']
            assert path.resolve().parent == folder.resolve() and not path.is_symlink()
            raw = path.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == row['feature_sha256']
            feature = json.loads(raw)
            assert feature['task_id'] == row['assay_id'] and feature['family_id'] == row['family_id']
            versions.append(feature)
            pins.append({'path':str(path.relative_to(ROOT)),'sha256':row['feature_sha256']})
    protection = protected_identity_index(versions,registry)
    assert protection['versioned_feature_files']==24 and protection['unique_canonical_structures']==4723
    assert len(protection['family_ids'])==14 and len(protection['uniprot_accessions'])==42
    save(PRIVATE/'protection-index-private.json',protection)
    save(PRIVATE/'protection-input-pins.json',{'registry_sha256':policy['registry_sha256'],'files':pins})
    old_r0 = ROOT/'.local/r0-chembl-20261107-v1'
    targets = json.loads((old_r0/'016-chembl37-selected-targets.html').read_text())['targets']
    selection = json.loads((old_r0/'selection-v1.json').read_text())
    known_sets = defaultdict(set)
    for row in registry['assays']:
        known_sets[row['uniprot_accession']].add(row['family_id'])
    known = {accession:next(iter(groups)) for accession,groups in known_sets.items() if len(groups)==1}
    target_gates = {}
    for target in targets:
        accessions = {row['accession'] for row in target['target_components'] if row.get('accession')}
        target_gates[target['target_chembl_id']] = family_gate(accessions,known,protection,bool(accessions))
    allowed, dispositions = [], []
    for row in selection['records']:
        gate = target_gates[row['target_chembl_id']]
        if row['assay_chembl_id'] in protection['assay_ids']:
            gate = 'QUARANTINE_PROTECTED_ASSAY'
        item = {**row,'protection_gate':gate}
        dispositions.append(item)
        if gate == 'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY':
            allowed.append(item)
    salt = 'CuraLoop-R0R-reference-feasibility-20261107-v1'
    rank = lambda row:hashlib.sha256((salt+row['assay_chembl_id']).encode()).hexdigest()
    chosen, documents_seen = [], set()
    # Alternate B/F up to six each; prefer unseen documents within each stratum.
    for _ in range(6):
        for category in ('B','F'):
            remaining = [row for row in allowed if row['assay_type']==category and row not in chosen]
            remaining.sort(key=lambda row:(row['document_chembl_id'] in documents_seen,rank(row)))
            if remaining:
                chosen.append(remaining[0]); documents_seen.add(remaining[0]['document_chembl_id'])
    assert len(chosen)<=12 and len({row['assay_chembl_id'] for row in chosen})==len(chosen)
    save(PRIVATE/'selection-freeze-v1.json',{'salt':salt,'source_release':'ChEMBL_37','cases':chosen,
        'dispositions':dispositions,'post_freeze_replacement_allowed':False,'outcomes_used':False})
    specs = {'status-before':{'url':'https://www.ebi.ac.uk/chembl/api/data/status.json'},
             'status-after':{'url':'https://www.ebi.ac.uk/chembl/api/data/status.json'}}
    fields = 'activity_id,assay_chembl_id,document_chembl_id,molecule_chembl_id,standard_type,standard_units'
    for row in chosen:
        parameters = {'assay_chembl_id':row['assay_chembl_id'],'only':fields,'limit':20,'order_by':'activity_id'}
        specs['projection-'+row['assay_chembl_id']]={'url':'https://www.ebi.ac.uk/chembl/api/data/activity.json?'+urllib.parse.urlencode(parameters)}
    save(PRIVATE/'request-registry.json',specs)
    ledger()
    report = {'status':'PASS_LABEL_FREE_PREFLIGHT_SELECTION_FROZEN','rdkit':rdBase.rdkitVersion,
              'protected_features_verified':24,'protected_structures':4723,
              'assay_gate_counts':dict(Counter(row['protection_gate'] for row in dispositions)),
              'eligible_assays':len(allowed),'selected_assays':len(chosen),
              'selected_categories':dict(Counter(row['assay_type'] for row in chosen)),
              'selected_documents':len(documents_seen),'independent_families_certified':False}
    save(PRIVATE/'preflight-report-v1.json',report)
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    guard=Guard('preflight-v1')
    try:
        run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__); raise
    else:
        guard.finish('PASS',charged_to='600-second utility reservation')
