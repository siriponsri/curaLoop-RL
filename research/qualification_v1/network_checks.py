"""Supplemental metadata-boundary checks; preserve all constructed fixtures in task."""

import json
import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from .audit import write_new
from .contracts import QualificationError


def run(root, output):
    from . import network
    definitions = json.loads((root / 'research/configs/goal4r2a3_network_cases_v1.json').read_text())
    fixture = output / 'metadata-boundary-fixtures'
    fixture.mkdir(exist_ok=False)
    executed = []
    first = fixture / 'pending'
    write_new(first / 'research/configs/goal4r2a3_policy_v1.json',
              json.loads((root / 'research/configs/goal4r2a3_policy_v1.json').read_text()))
    write_new(first / 'network-ledger.json', {'requests': [{'service': 'uniprot', 'status': 'RESERVED', 'charged_decoded_bytes': 0}], 'stopped_services': []})
    try:
        network.Client(first, first, 'uniprot', [])
    except QualificationError as error:
        assert 'reservation' in str(error)
    else:
        raise AssertionError('Pending network reservation was accepted')
    executed.append('N01')

    second, second_output = fixture / 'invalid-schema', fixture / 'invalid-schema-output'
    second_output.mkdir()
    write_new(second / 'runs/metadata-audit-v1/results.json', {'status': 'PASS_METADATA_PROTECTION_AND_TWELVE_CASES', 'fixture': True})
    write_new(second / 'runs/metadata-audit-v1/xref-requests.json', {'requests': [{'path': 'synthetic', 'params': {}, 'expected_accessions': ['P1']}]})
    original = network.Client
    class SyntheticClient:
        def __init__(self, fixture_root, fixture_output, service, specs):
            self.ledger_path = fixture_root / 'network-ledger.json'
            self.ledger = {'requests': [], 'stopped_services': []}
            self.service, self.guard = service, SimpleNamespace(failed=False)
        def request(self, spec, name):
            return b'Wrong\tHeader\nX\tY\n', {'transport': {'headers': {'x-uniprot-release': 'synthetic'}}}
        stop = original.stop
    with patch.object(network, 'Client', SyntheticClient):
        try:
            network.crossrefs(second, second_output)
        except QualificationError:
            pass
        else:
            raise AssertionError('Invalid successful response schema was accepted')
    assert network.read(second / 'network-ledger.json')['stopped_services'] == ['uniprot']
    assert network.read(second_output / 'results.json')['status'] == 'NO_GO_METADATA_ACCESS_OR_SCHEMA'
    executed.append('N02')

    third = fixture / 'current-anchor'
    source = third / 'private-inputs/protection-inputs'
    original_types = root / 'private-inputs/protection-inputs/interpro-ftp-entries110-curl-v2/body'
    copied_types = source / 'interpro-ftp-entries110-curl-v2/body'
    copied_types.parent.mkdir(parents=True)
    shutil.copyfile(original_types, copied_types)
    types = [line.split('\t')[0] for line in original_types.read_text().splitlines()[1:]
             if line.split('\t')[1].lower() == 'family'][:2]
    def protein(accession, family, ipr):
        return {'Entry': accession, 'Reviewed': 'reviewed', 'Organism (ID)': '9606',
                'Protein names': 'Synthetic test protein', 'Protein families': family,
                'Sequence similarities': 'SIMILARITY: Belongs to the ' + family + '.',
                'InterPro': ipr + ';', 'RefSeq': ''}
    write_new(source / 'family-registry-v3.json', {
        'assays': [{'family_id': 'F1', 'uniprot_accession': 'P1'}, {'family_id': 'F2', 'uniprot_accession': 'P2'}],
        'family_records': [{'family_id': 'F1', 'broad_names_merged': ['old family']}, {'family_id': 'F2', 'broad_names_merged': ['new family']}]})
    write_new(source / 'uniprot-family-bulk-v1/families.json', [protein('P1', 'old family', types[0])])
    write_new(source / 'uniprot-family-exposure-v1/families.json', [])
    protected = {'uniprot_accessions': ['P1'], 'family_ids': ['F1']}
    overlay, state = network.family_overlay(third, [protein('P1', 'new family', types[1]), protein('P2', 'new family', types[1])], protected)
    assert not state['unresolved_current_anchors']
    assert overlay['P2']['verdict'] == 'QUARANTINE_SHARED_PROTECTED_FAMILY_OR_SUPERFAMILY'
    missing, state = network.family_overlay(third, [protein('P2', 'unrelated family', types[1])], protected)
    assert state['unresolved_current_anchors'] == ['P1']
    assert missing['P2']['verdict'] == 'QUARANTINE_CURRENT_PROTECTED_ANNOTATION_UNRESOLVED'
    executed.append('N03')

    assert executed == [row['id'] for row in definitions['cases']]
    report = {'status': 'PASS_THREE_METADATA_BOUNDARY_CHECKS', 'actual_case_ids': executed,
              'actual_external_requests': 0, 'scientific_trials': 0,
              'fixtures_preserved_under_task': True}
    write_new(output / 'network-boundary-checks.json', report)
    return report
