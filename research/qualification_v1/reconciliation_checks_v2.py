"""Preserve R01-R03 execution, then exercise positive protected-base conflicts."""

import hashlib
from .audit import write_new
from .reconciliation_checks_v1 import rejected
from .reconciliation_checks_v1 import run as original_checks


def run(root, output, config):
    from .reconcile_v2 import target_gate, validate_cached, REQUIRED
    original = dict(config, cases=config['cases'][:3])
    original_checks(root, output, original)
    overlay = {'P1': {'tax_id': '9606', 'verdict': 'QUARANTINE_PROTECTED_PROTEIN'},
               'P2': {'tax_id': '9606', 'verdict': 'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY'}}
    descriptor = {'target_metadata': [{'mol_id': {'protein_accession': 'NP_000001.2'},
                  'organism': {'org': {'db': [{'db': 'taxon', 'tag': {'id': 9606}}]}}}]}
    exact, bases, protection = {'NP_000001.2': {'P2'}}, {'NP_000001': {'P1', 'P2'}}, {'uniprot_accessions': ['P1']}
    verdict, resolved = target_gate(descriptor, overlay, exact, bases, protection)
    assert verdict == 'QUARANTINE_PROTECTED_PROTEIN_BASE_ACCESSION' and resolved == []
    assert target_gate(descriptor, overlay, exact, bases, {'uniprot_accessions': []}) == (
        'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY', ['P2'])
    columns = sorted(REQUIRED)
    spec = {'path': 'uniprotkb/search', 'params': {'query': 'synthetic'}, 'expected_accessions': ['P2']}
    malformed = []
    for values in [['P2'], ['P2'] * (len(columns) + 1),
                   [('P2' if k == 'Entry' else 'reviewed' if k == 'Reviewed' else 'not-a-taxon' if k == 'Organism (ID)' else '') for k in columns]]:
        raw = ('\t'.join(columns) + '\n' + '\t'.join(values) + '\n').encode()
        roster = {'path': spec['path'], 'params': spec['params'], 'utc': 'synthetic',
                  'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        receipt = {'request': {'base_url': 'https://rest.uniprot.org', 'method': 'GET', 'path': spec['path'], 'params': spec['params']},
                   'request_utc': 'synthetic', 'transport': {'headers': {'X-UniProt-Release': '2026_04'}},
                   'response_sha256': roster['sha256'], 'response_bytes': len(raw), 'result': {'ok': True}}
        rejected(lambda: validate_cached(raw, receipt, spec, roster, '2026_04'))
        malformed.append({'raw_utf8': raw.decode(), 'receipt': receipt, 'roster': roster})
    write_new(output / 'reconciliation-fixtures/malformed-tsv.json', {'specification': spec, 'cases': malformed})
    ids = ['R01', 'R02', 'R03', 'R04', 'R05']
    assert ids == [c['id'] for c in config['cases']]
    write_new(output / 'reconciliation-fixtures/base-exact-conflict.json', {'overlay': overlay,
              'descriptor': descriptor, 'exact': {k: sorted(v) for k, v in exact.items()},
              'bases': {k: sorted(v) for k, v in bases.items()}, 'protection': protection, 'verdict': verdict})
    write_new(output / 'reconciliation-checks-v2.json', {'status': 'PASS_FIVE_RECONCILIATION_CHECKS',
              'actual_case_ids': ids, 'actual_external_requests': 0, 'fixtures_preserved_under_task': True})
