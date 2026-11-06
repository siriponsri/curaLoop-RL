"""Metadata/protection qualification, with synthetic checks before outcome access."""

import collections
import hashlib
import importlib.util
import io
import json
import re
import unittest
from pathlib import Path

from .contracts import bind_columns, parse_source_script, programme_rights, protected_identity_index


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def checks(root, output):
    case_path = root / 'research/configs/goal4r2a3_cases_v1.json'
    freeze = json.loads((root / 'docs/evidence/goal4r2a3-20261106-v1/cases-freeze-v1.json').read_text())
    assert hashlib.sha256(case_path.read_bytes()).hexdigest() == freeze['cases_sha256']
    spec = importlib.util.spec_from_file_location('qualification_checks', root / 'tests/research/test_qualification_v1.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    class Recorded(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.executed = []
        def startTest(self, test):
            super().startTest(test)
            self.executed.append(test._testMethodName.split('_')[1])
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Recorded).run(suite)
    (output / 'checks.log').write_text(stream.getvalue(), encoding='utf-8')
    expected = [r['id'] for r in json.loads(case_path.read_text())['cases']]
    report = {'status': 'PASS' if result.wasSuccessful() and sorted(result.executed) == sorted(expected) else 'FAIL',
              'tests': result.testsRun, 'actual_case_ids': result.executed, 'case_sha256': freeze['cases_sha256'],
              'scientific_trials': 0}
    write_new(output / 'checks.json', report)
    if report['status'] != 'PASS':
        raise RuntimeError('Frozen qualification checks failed; retain full log')
    return report


def metadata(root, output):
    policy = json.loads((root / 'research/configs/goal4r2a3_policy_v1.json').read_text())
    from rdkit import Chem, rdBase
    import numpy
    assert rdBase.rdkitVersion == policy['canonicalization']['rdkit']
    assert numpy.__version__ == '2.3.5'
    assert Chem.MolToSmiles(Chem.MolFromSmiles('C(C)O'), canonical=True, isomericSmiles=True) == 'CCO'
    tests = checks(root, output)
    source = root / 'private-inputs'
    inputs = json.loads((source / 'private-inputs-manifest-v1.json').read_text())
    # Every copied native/protection file is byte-checked by the worker bundle;
    # repeat the semantic feature hash/role checks before building its index.
    registry = json.loads((source / 'protection-inputs/family-registry-v3.json').read_text())
    assert hashlib.sha256((source / 'protection-inputs/family-registry-v3.json').read_bytes()).hexdigest() == policy['registry_sha256']
    versions = []
    for version, digest in policy['protected_manifests'].items():
        folder = source / 'protection-inputs' / version
        path = folder / 'manifest.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        for row in json.loads(path.read_text())['selected_assays']:
            if row['role'] != 'final':
                continue
            path = folder / row['feature_file']
            assert path.resolve().parent == folder.resolve() and not path.is_symlink()
            raw = path.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == row['feature_sha256']
            feature = json.loads(raw)
            assert feature['task_id'] == row['assay_id'] and feature['family_id'] == row['family_id']
            assert len(feature['records']) == row['retained_structures']
            versions.append(feature)
    protection = protected_identity_index(versions, registry)
    assert protection['versioned_feature_files'] == 24 and len(protection['family_ids']) == 14
    assert len(protection['assay_ids']) == 85 and len(protection['uniprot_accessions']) == 42
    write_new(output / 'protection-private.json', protection)
    public_protection = {k: v for k, v in protection.items() if k != 'canonical_smiles'}
    public_protection['private_index_sha256'] = hashlib.sha256((output / 'protection-private.json').read_bytes()).hexdigest()
    public_protection['source_inputs_manifest_sha256'] = hashlib.sha256((source / 'private-inputs-manifest-v1.json').read_bytes()).hexdigest()
    write_new(output / 'protection-summary.json', public_protection)
    descriptions = json.loads((source / 'description-metadata-input-v1.json').read_text())['records']
    rights, by_aid = [], {}
    for record in descriptions:
        comments = record['comment_notices']
        if type(comments) is not list or any(type(c) is not str for c in comments):
            raise RuntimeError('Unexpected source notice schema')
        flags = sorted(set(re.findall(r'copyright|confidential|licen[cs]e|permission|proprietary|commercial use|redistribution|unpublished',
                                     '\n'.join(comments), flags=re.I)))
        record['restriction_flags'] = flags
        verdict = programme_rights(record, policy, notices_checked=True)
        provider = (record.get('provider') or {}).get('db', {}).get('name')
        rights.append({'aid': record['aid'], 'provider': provider,
                       'raw_category': record['project_category_raw'], 'category_present': record['project_category_present'],
                       'source_sha256': record['source_sha256'], 'notice_review_flags': flags, 'internal_use': verdict,
                       'publication': 'NOT_CLEARED', 'redistribution': 'NOT_CLEARED', 'commercial_data': 'NOT_CLEARED'})
        record['rights_verdict'] = verdict
        by_aid[record['aid']] = record
    schema_path = source / 'source-evidence/pcassay2.asn'
    schema = schema_path.read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(schema)).encode() + b'\0' + schema).hexdigest() == policy['schema_pin']['git_blob_oid']
    directory = json.loads((root / 'docs/evidence/goal4r2a3-20261106-v1/source-directory-v1.json').read_text())
    candidates = []
    for row in directory['files']:
        path = source / 'pinned-source' / row['path']
        raw = path.read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob_oid']
        parsed = parse_source_script(raw.decode('utf-8'))
        numbers = Path(row['path']).stem.split('-')
        assert parsed['confirmation_aid'] == numbers[0] and parsed['primary_aid'] == numbers[-1]
        record = {'script': row['path'], 'script_sha256': hashlib.sha256(raw).hexdigest(), **parsed}
        try:
            record['primary_bindings'] = bind_columns(by_aid[parsed['primary_aid']]['readout_definitions'], parsed['primary_columns'])
            record['confirmation_bindings'] = bind_columns(by_aid[parsed['confirmation_aid']]['readout_definitions'], parsed['confirmation_columns'])
            record['binding_status'] = 'EXACT_NAME_TID_UNIT_BINDING'
        except ValueError as error:
            record.update(binding_status='QUARANTINE_BINDING', error_type=type(error).__name__)
        record['both_programme_rights_supported'] = all(by_aid[parsed[role]]['rights_verdict'] == 'INTERNAL_RESEARCH_USE_SUPPORTED_BY_MLP_POLICY'
                                                       for role in ('primary_aid', 'confirmation_aid'))
        record['target_family_gate'] = 'UNRESOLVED_PENDING_XREF_METADATA'
        candidates.append(record)
    assert len(candidates) == 60
    write_new(output / 'source-binding-register.json', {'records': candidates, 'activity_rows': 0})
    write_new(output / 'rights-register.json', {'records': rights, 'policy_sha256': hashlib.sha256((root / 'research/configs/goal4r2a3_policy_v1.json').read_bytes()).hexdigest(),
                                               'internal_use_counts': dict(collections.Counter(r['internal_use'] for r in rights)),
                                               'raw_category_counts': dict(collections.Counter(str(r['raw_category']) for r in rights))})
    ids = sorted({r['uniprot_accession'] for r in registry['assays']})
    assert (len(ids) + 39) // 40 <= policy['maximum_uniprot_metadata_requests']
    requests = []
    for start in range(0, len(ids), 40):
        batch = ids[start:start + 40]
        requests.append({'path': 'uniprotkb/search', 'params': {
            'query': '(' + ' OR '.join('accession:' + a for a in batch) + ') AND reviewed:true',
            'format': 'tsv', 'fields': policy['uniprot_fields'], 'size': 500}, 'expected_accessions': batch})
    write_new(output / 'xref-requests.json', {'status': 'FROZEN_METADATA_ONLY_REQUESTS', 'requests': requests,
                                            'expected_accessions': ids, 'assay_outcomes_requested': False})
    report = {'status': 'PASS_METADATA_PROTECTION_AND_TWELVE_CASES', 'checks': tests,
              'native_canary': {'rdkit': rdBase.rdkitVersion, 'numpy': numpy.__version__, 'canonicalization': 'PASS'},
              'script_bodies_checked': len(candidates), 'exact_bindings': sum(r['binding_status'] == 'EXACT_NAME_TID_UNIT_BINDING' for r in candidates),
              'both_programme_rights_supported_pairs': sum(r['both_programme_rights_supported'] for r in candidates),
              'internal_use_counts': dict(collections.Counter(r['internal_use'] for r in rights)),
              'protected_unique_structures': protection['unique_canonical_structures'],
              'protected_family_groups': 14, 'protected_registry_proteins': 42,
              'xref_queries': len(requests), 'activity_requests': 0, 'scientific_campaigns': 0,
              'family_gate': 'PENDING_METADATA', 'source_exact_historical_rows': 'NOT_CERTIFIED'}
    write_new(output / 'results.json', report)
    return report
