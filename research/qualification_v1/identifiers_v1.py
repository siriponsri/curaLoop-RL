"""Outcome-blind SID/CID/structure qualification, with activity paths disabled."""

import hashlib
import re
import time
from collections import Counter

from .audit import write_new
from .contracts import QualificationError, positive_id, sample_ids, strict_json
from .network import Client, read


def identifier_list(values):
    if type(values) is not list or any(type(v) is not int or not positive_id(v) for v in values):
        raise QualificationError('Invalid integer identifier list')
    if len(set(values)) != len(values):
        raise QualificationError('Duplicate identifier list')
    return [str(v) for v in values]


def grouped(raw, key, target, allowed):
    data = strict_json(raw, byte_limit=16 * 1024**2)
    if set(data) != {'InformationList'} or set(data['InformationList']) != {'Information'}:
        raise QualificationError('Grouped identifier envelope required')
    rows = data['InformationList']['Information']
    if type(rows) is not list:
        raise QualificationError('Grouped identifier records required')
    result = {}
    for row in rows:
        if type(row) is not dict or set(row) != {key, target} or type(row[key]) is not int or not positive_id(row[key]):
            raise QualificationError('Unexpected grouped identity projection')
        identity = str(row[key])
        if identity not in allowed or identity in result:
            raise QualificationError('Unexpected or duplicate grouped source identity')
        result[identity] = identifier_list(row[target])
    return result


def structures(raw, allowed, protected):
    from rdkit import Chem, rdBase
    if rdBase.rdkitVersion != '2026.09.1':
        raise QualificationError('Canonicalization version differs')
    data = strict_json(raw, byte_limit=16 * 1024**2)
    if set(data) != {'PropertyTable'} or set(data['PropertyTable']) != {'Properties'}:
        raise QualificationError('Property table envelope differs')
    rows = data['PropertyTable']['Properties']
    if type(rows) is not list:
        raise QualificationError('Property records required')
    result = {}
    for row in rows:
        if (type(row) is not dict or set(row) != {'CID', 'SMILES', 'InChIKey'}
                or type(row['CID']) is not int or not positive_id(row['CID'])
                or type(row['SMILES']) is not str or not row['SMILES']
                or type(row['InChIKey']) is not str or not re.fullmatch(r'[A-Z]{14}-[A-Z]{10}-[A-Z]', row['InChIKey'])):
            raise QualificationError('Complete stereo/isotope property projection required')
        cid = str(row['CID'])
        if cid not in allowed or cid in result:
            raise QualificationError('Unexpected or duplicate property identity')
        # Native parser logs can contain complete input structures. Never publish them.
        try:
            with rdBase.BlockLogs():
                mol = Chem.MolFromSmiles(row['SMILES'])
                canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True) if mol else None
        except Exception:
            raise QualificationError('Native structure parser failed') from None
        verdict = 'NO_STRUCTURE' if canonical is None else 'PROTECTED_EXACT_CANONICAL' if canonical in protected else 'CLEARED_EXACT_CANONICAL_CONTROL'
        result[cid] = {'canonical_smiles': canonical, 'source_inchikey': row['InChIKey'], 'verdict': verdict}
    return result


def batches(values, size=100):
    return [values[i:i + size] for i in range(0, len(values), size)]


def run_checks(root, output):
    import json
    import os
    from .reconciliation_checks_v1 import rejected
    definition = read(root / 'research/configs/goal4r2a3_identifier_cases_v1.json')
    fixture = output / 'identifier-fixtures'
    fixture.mkdir()
    write_new(fixture / 'definitions.json', definition)
    def encoded(value):
        return json.dumps(value).encode()
    grouped_fixture = {'InformationList': {'Information': [{'SID': 1, 'CID': [10]}, {'SID': 2, 'CID': [20, 21]}]}}
    assert grouped(encoded(grouped_fixture), 'SID', 'CID', {'1', '2'}) == {'1': ['10'], '2': ['20', '21']}
    for invalid in [{'IdentifierList': {'CID': [10, 20]}},
                    {'InformationList': {'Information': [{'SID': 3, 'CID': [10]}]}},
                    {'InformationList': {'Information': [{'SID': 1, 'CID': [True]}]}},
                    {'InformationList': {'Information': [{'SID': 1, 'CID': [10]}, {'SID': 1, 'CID': [20]}]}}]:
        rejected(lambda: grouped(encoded(invalid), 'SID', 'CID', {'1', '2'}))
    write_new(fixture / 'grouped.json', grouped_fixture)
    props = {'PropertyTable': {'Properties': [
        {'CID': 1, 'SMILES': 'OCC', 'InChIKey': 'AAAAAAAAAAAAAA-BBBBBBBBBB-C'},
        {'CID': 2, 'SMILES': '[13CH4]', 'InChIKey': 'AAAAAAAAAAAAAA-BBBBBBBBBB-C'}]}}
    result = structures(encoded(props), {'1', '2'}, {'CCO'})
    assert result['1']['verdict'] == 'PROTECTED_EXACT_CANONICAL' and result['2']['verdict'] == 'CLEARED_EXACT_CANONICAL_CONTROL'
    assert result['2']['canonical_smiles'] == '[13CH4]'
    write_new(fixture / 'properties.json', props)
    invalid = {'PropertyTable': {'Properties': [{'CID': 3, 'SMILES': 'SENTINEL_PRIVATE_INVALID_STRUCTURE__',
                                                'InChIKey': 'AAAAAAAAAAAAAA-BBBBBBBBBB-C'}]}}
    captured = [fixture / 'native-stdout.log', fixture / 'native-stderr.log']
    originals = [os.dup(1), os.dup(2)]
    try:
        with captured[0].open('wb') as stdout, captured[1].open('wb') as stderr:
            os.dup2(stdout.fileno(), 1)
            os.dup2(stderr.fileno(), 2)
            assert structures(encoded(invalid), {'3'}, set())['3']['verdict'] == 'NO_STRUCTURE'
    finally:
        os.dup2(originals[0], 1)
        os.dup2(originals[1], 2)
        for fd in originals:
            os.close(fd)
    assert all(b'SENTINEL_PRIVATE_INVALID_STRUCTURE__' not in p.read_bytes() for p in captured)
    write_new(fixture / 'invalid-property-private.json', invalid)
    sample = sample_ids([str(i) for i in range(1, 300)], 'synthetic', 128)
    retained = [i for i in sample if i != sample[0]]
    assert len(retained) == 127 and set(retained) < set(sample)
    assert sample_ids(list(reversed([str(i) for i in range(1, 300)])), 'synthetic', 128) == sample
    write_new(fixture / 'sampling.json', {'sample': sample, 'retained_without_replacement': retained})
    ids = ['I01', 'I02', 'I03']
    assert ids == [c['id'] for c in definition['cases']]
    write_new(output / 'identifier-checks.json', {'status': 'PASS_THREE_IDENTIFIER_CHECKS', 'actual_case_ids': ids,
              'actual_external_requests': 0, 'fixtures_preserved_under_task': True})


def execute(root, output):
    run_checks(root, output)
    gate = root / 'runs/cached-reconciliation-v2'
    definition = read(root / 'research/configs/goal4r2a3_identifier_cases_v1.json')
    protection_path = root / 'runs/metadata-audit-v1/protection-private.json'
    if (hashlib.sha256((gate / 'pair-metadata-gates.json').read_bytes()).hexdigest() != definition['metadata_gate_sha256']
            or hashlib.sha256(protection_path.read_bytes()).hexdigest() != definition['protected_index_sha256']):
        raise QualificationError('Pinned metadata admission or protected index differs')
    if read(gate / 'results.json')['status'] != 'PASS_CACHED_METADATA_RECONCILIATION':
        raise QualificationError('Reviewed metadata reconciliation required')
    pairs = read(gate / 'pair-metadata-gates.json')['selected']
    if not 0 < len(pairs) <= 12 or any(p['metadata_admitted'] is not True for p in pairs):
        raise QualificationError('No admitted pair roster')
    salt = read(root / 'research/configs/goal4r2a3_policy_v1.json')['selection_salt']
    protected = set(read(protection_path)['canonical_smiles'])
    aids = sorted({p[k] for p in pairs for k in ('primary_aid', 'confirmation_aid')}, key=int)
    specs = [{'path': 'assay/aid/' + a + '/sids/JSON', 'params': {'sids_type': 'all', 'list_return': 'grouped'}} for a in aids]
    write_new(output / 'sid-request-plan-private.json', {'requests': specs, 'metadata_gate_sha256': hashlib.sha256((gate / 'pair-metadata-gates.json').read_bytes()).hexdigest(), 'activity_paths': 'DISABLED'})
    client = None
    source_sids, sampled, mapping, property_rows = {}, [], {}, {}
    try:
        client = Client(root, output, 'pubchem', specs)
        for i, (aid, spec) in enumerate(zip(aids, specs)):
            raw, _ = client.request(spec, 'aid-sids-' + str(i).zfill(3))
            rows = grouped(raw, 'AID', 'SID', {aid})
            if set(rows) != {aid}:
                raise QualificationError('Missing requested AID identity')
            source_sids[aid] = set(rows[aid])
        for p in pairs:
            common = source_sids[p['primary_aid']] & source_sids[p['confirmation_aid']]
            ids = sample_ids(list(common), salt + ':' + p['script'], 128)
            sampled.append({'script': p['script'], 'primary_aid': p['primary_aid'], 'confirmation_aid': p['confirmation_aid'],
                            'common_listed_sids': len(common), 'sampled_sids': ids, 'metadata_binding': p})
        all_sids = sorted({s for p in sampled for s in p['sampled_sids']}, key=int)
        groups = batches(all_sids)
        specs = [{'path': 'substance/sid/' + ','.join(g) + '/cids/JSON', 'params': {'cids_type': 'all', 'list_return': 'grouped'}} for g in groups]
        write_new(output / 'sample-and-cid-request-plan-private.json', {'pairs': sampled, 'requests': specs, 'replacement_after_exclusion': False, 'activity_paths': 'DISABLED'})
        if groups:
            time.sleep(1.1)
            client = Client(root, output, 'pubchem', specs)
            for i, (g, spec) in enumerate(zip(groups, specs)):
                raw, _ = client.request(spec, 'sid-cids-' + str(i).zfill(3))
                mapping.update(grouped(raw, 'SID', 'CID', set(g)))
        cids = sorted({v[0] for v in mapping.values() if len(v) == 1}, key=int)
        groups = batches(cids)
        specs = [{'path': 'compound/cid/' + ','.join(g) + '/property/SMILES,InChIKey/JSON', 'params': {}} for g in groups]
        write_new(output / 'structure-request-plan-private.json', {'requests': specs, 'ambiguous_cids': 'EXCLUDED', 'activity_paths': 'DISABLED'})
        if groups:
            time.sleep(1.1)
            client = Client(root, output, 'pubchem', specs)
            for i, (g, spec) in enumerate(zip(groups, specs)):
                raw, _ = client.request(spec, 'cid-structure-' + str(i).zfill(3))
                property_rows.update(structures(raw, set(g), protected))
    except Exception as error:
        if client is not None:
            client.stop('IDENTIFIER_OR_STRUCTURE_ACCESS_OR_SCHEMA_FAILURE')
        write_new(output / 'results.json', {'status': 'NO_GO_IDENTIFIER_OR_STRUCTURE_ACCESS_OR_SCHEMA',
                  'error_type': type(error).__name__, 'completed_aid_sid_lists': len(source_sids),
                  'activity_requests': 0, 'scientific_campaigns': 0})
        raise
    attrition, release = [], []
    for p in sampled:
        states, allowed = Counter(), []
        for sid in p['sampled_sids']:
            linked = mapping.get(sid, [])
            if len(linked) != 1:
                states['ambiguous_or_missing_cid'] += 1
                continue
            row = property_rows.get(linked[0])
            state = row['verdict'] if row else 'MISSING_PROPERTY_RECORD'
            states[state] += 1
            if state == 'CLEARED_EXACT_CANONICAL_CONTROL':
                allowed.append(sid)
        release.append(dict(p, cleared_sids=allowed))
        attrition.append({'script': p['script'], 'primary_aid': p['primary_aid'], 'confirmation_aid': p['confirmation_aid'],
                          'primary_listed_sids': len(source_sids[p['primary_aid']]), 'confirmation_listed_sids': len(source_sids[p['confirmation_aid']]),
                          'common_listed_sids': p['common_listed_sids'], 'sampled_sids': len(p['sampled_sids']),
                          'states': dict(states), 'cleared_sids': len(allowed)})
    write_new(output / 'structure-qualification-private.json', {'pairs': release, 'sid_cids': mapping, 'cid_properties': property_rows})
    write_new(output / 'attrition.json', {'records': attrition, 'sample_condition': 'SOURCE_COMMON_LISTED_SIDS; NO_OUTCOME_BASED_SELECTION_OR_REPLACEMENT'})
    report = {'status': 'PASS_IDENTIFIER_AND_EXACT_STRUCTURE_CONTROL', 'metadata_pairs': len(pairs),
              'known_family_components': len({g['family_id'] for p in pairs for g in p['target_family_gate']}),
              'unique_sampled_sids': len(all_sids), 'pairs_with_cleared_sids': sum(bool(p['cleared_sids']) for p in release),
              'activity_requests': 0, 'scientific_campaigns': 0, 'chemical_ood_claim': False}
    write_new(output / 'results.json', report)
    return report
