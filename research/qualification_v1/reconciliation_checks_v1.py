"""R01-R03 repair regressions, executed before cached metadata reconciliation."""

import copy
import hashlib
import json
import shutil

from .audit import write_new
from .contracts import QualificationError


def rejected(operation):
    try:
        operation()
    except QualificationError:
        return
    raise AssertionError('Invalid metadata accepted')


def run(root, output, config):
    from .reconcile_v1 import refseq_tokens, retired_supplement, family_overlay, validate_cached, REQUIRED, target_gate
    fixture = output / 'reconciliation-fixtures'
    fixture.mkdir(exist_ok=False)
    write_new(fixture / 'case-definitions.json', config)
    tokens = 'NP_003860.3 [O00748-1]; NP_003860.4;'
    parsed = refseq_tokens('O00748', tokens)
    assert parsed == [{'accession_version': 'NP_003860.3', 'isoform_tag': 'O00748-1'},
                      {'accession_version': 'NP_003860.4', 'isoform_tag': None}]
    for invalid in ['NP_003860.3 [P00001-1]', 'NP_003860', 'prefix NP_003860.3', 'NP_003860.3 trailing']:
        rejected(lambda: refseq_tokens('O00748', invalid))
    synthetic_overlay = {'O00748': {'tax_id': '9606', 'verdict': 'CLEAR'}}
    descriptor = {'target_metadata': [{'mol_id': {'protein_accession': 'NP_003860.2'}, 'organism': None}]}
    assert target_gate(descriptor, synthetic_overlay, {'NP_003860.3': {'O00748'}}, {'NP_003860': {'O00748'}},
                       {'uniprot_accessions': ['O00748']})[0] == 'QUARANTINE_PROTECTED_PROTEIN_BASE_ACCESSION'
    descriptor['target_metadata'][0]['mol_id']['protein_accession'] = 'NP_003860.3'
    assert target_gate(descriptor, synthetic_overlay, {'NP_003860.3': {'O00748'}}, {},
                       {'uniprot_accessions': []})[1] == []  # Missing taxon cannot clear.
    write_new(fixture / 'refseq.json', {'entry': 'O00748', 'tokens': tokens, 'parsed': parsed, 'null_organism': descriptor})

    supplement = retired_supplement(root, config)
    assert supplement == {'IPR050332': 'family'}
    source = fixture / 'retired-positive/private-inputs/protection-inputs'
    types = root / 'private-inputs/protection-inputs/interpro-ftp-entries110-curl-v2/body'
    copied = source / 'interpro-ftp-entries110-curl-v2/body'
    copied.parent.mkdir(parents=True)
    shutil.copyfile(types, copied)
    def protein(a, name, interpro):
        return {'Entry': a, 'Reviewed': 'reviewed', 'Organism (ID)': '9606', 'Protein names': 'Synthetic fixture',
                'Protein families': name, 'Sequence similarities': 'SIMILARITY: Belongs to the ' + name + '.',
                'InterPro': interpro, 'RefSeq': ''}
    write_new(source / 'family-registry-v3.json', {'family_records': [{'family_id': 'F1', 'broad_names_merged': ['old family']}],
              'assays': [{'family_id': 'F1', 'uniprot_accession': 'P1'},
                         {'family_id': 'F2', 'uniprot_accession': 'P2'}]})
    write_new(source / 'uniprot-family-bulk-v1/families.json', [protein('P1', 'old family', '')])
    write_new(source / 'uniprot-family-exposure-v1/families.json', [])
    proteins = [protein('P1', 'current family', 'IPR050332;'), protein('P2', 'different family', 'IPR050332;')]
    write_new(fixture / 'retired-positive/proteins.json', proteins)
    overlay, state = family_overlay(fixture / 'retired-positive', proteins,
                                    {'uniprot_accessions': ['P1'], 'family_ids': ['F1']}, supplement)
    assert not state['unresolved_current_anchors'] and state['retired_positive_protected_family_ids'] == ['IPR050332']
    assert overlay['P2']['verdict'] == 'QUARANTINE_SHARED_PROTECTED_FAMILY_OR_SUPERFAMILY'
    assert copied.read_bytes() == types.read_bytes()
    write_new(fixture / 'retired-positive/result.json', {'overlay': overlay, 'state': state})

    columns = sorted(REQUIRED)
    values = {'Entry': 'O00748', 'Reviewed': 'reviewed', 'Organism (ID)': '9606'}
    raw = ('\t'.join(columns) + '\n' + '\t'.join(values.get(k, '') for k in columns) + '\n').encode()
    spec = {'path': 'uniprotkb/search', 'params': {'query': 'synthetic'}, 'expected_accessions': ['O00748']}
    roster = {'path': spec['path'], 'params': spec['params'], 'utc': 'synthetic',
              'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    receipt = {'request': {'base_url': 'https://rest.uniprot.org', 'method': 'GET', 'path': spec['path'], 'params': spec['params']},
               'request_utc': 'synthetic', 'transport': {'headers': {'X-UniProt-Release': '2026_04'}},
               'response_sha256': roster['sha256'], 'response_bytes': len(raw), 'result': {'ok': True}}
    assert len(validate_cached(raw, receipt, spec, roster, '2026_04')) == 1
    rejected(lambda: validate_cached(raw + b'x', receipt, spec, roster, '2026_04'))
    rejected(lambda: validate_cached(raw, receipt, spec, roster, 'drifted'))
    other = copy.deepcopy(spec)
    other['expected_accessions'] = ['P1']
    rejected(lambda: validate_cached(raw, receipt, other, roster, '2026_04'))
    with (fixture / 'cached.tsv').open('xb') as handle:
        handle.write(raw)
    write_new(fixture / 'cached.json', {'specification': spec, 'roster': roster, 'receipt': receipt})
    ids = ['R01', 'R02', 'R03']
    assert ids == [c['id'] for c in config['cases']]
    result = {'status': 'PASS_THREE_RECONCILIATION_CHECKS', 'actual_case_ids': ids,
              'actual_external_requests': 0, 'fixtures_preserved_under_task': True}
    write_new(output / 'reconciliation-checks.json', result)
    return result
