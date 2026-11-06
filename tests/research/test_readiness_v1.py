"""Ten frozen metadata/schema contracts; synthetic examples, no benchmark rows."""

import copy
import json
import unittest
from pathlib import Path

from research.readiness_v1.contracts import (
    MetadataError, benchmark_blockers, compare_version, digest, feasibility_f1,
    normalize_description, observe, prospective_role, registry_coverage, strict_json,
    verify_manifest,
)


def payload():
    return {'PC_AssayContainer': [{'assay': {'descr': {
        'aid': {'id': 1, 'version': 1}, 'revision': 2, 'name': 'Synthetic metadata',
        'aid_source': {'db': {'name': 'Synthetic provider'}},
        'target': [{'mol_id': {'protein_accession': 'SYNTHETIC_ONLY'}}],
        'results': [{'tid': 1, 'name': 'Synthetic readout definition', 'unit': 0}],
    }}}]}


def raw(value):
    return json.dumps(value).encode()


class MetadataContracts(unittest.TestCase):
    def test_META01_metadata_identity_and_pointers(self):
        record = normalize_description(raw(payload()), '1', '2026-11-06T00:00:00Z')
        self.assertEqual(record['observed_aid'], 1)
        self.assertEqual(record['version']['value'], 1)
        self.assertEqual(record['version']['source_pointer'], '/PC_AssayContainer/0/assay/descr/aid/version')
        self.assertEqual(record['activity_rows_processed'], 0)
        self.assertEqual(record['readout_definitions'][0]['unit']['value'], 0)

    def test_META02_absent_null_zero(self):
        self.assertEqual(observe({}, 'x', '/x')['state'], 'ABSENT')
        self.assertEqual(observe({'x': None}, 'x', '/x')['state'], 'NULL')
        zero = observe({'x': 0}, 'x', '/x')
        self.assertEqual((zero['state'], zero['value']), ('VALUE', 0))
        self.assertEqual(observe({'x': False}, 'x', '/x')['value'], False)
        for state, value in [('ABSENT', 'missing'), ('NULL', None), ('VALUE', [])]:
            obj = payload()
            descr = obj['PC_AssayContainer'][0]['assay']['descr']
            if value == 'missing':
                del descr['results']
            else:
                descr['results'] = value
            record = normalize_description(raw(obj), '1', 'fixture')
            self.assertEqual(record['readout_definitions_field']['state'], state)
            from research.readiness_v1.jobs import summarize_record
            record['comparison'] = {}
            self.assertEqual(summarize_record(record)['readout_definition_count'], 0 if state == 'VALUE' else None)

    def test_META03_invalid_json_and_numeric_identity(self):
        for data in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e309}', b'\xff'):
            with self.subTest(data=data), self.assertRaises(MetadataError):
                strict_json(data)
        value = payload()
        value['PC_AssayContainer'][0]['assay']['descr']['aid']['id'] = True
        with self.assertRaises(MetadataError):
            normalize_description(raw(value), '1', 'fixture')
        value = payload()
        value['PC_AssayContainer'][0]['assay']['descr']['revision'] = True
        self.assertEqual(normalize_description(raw(value), '1', 'fixture')['revision']['state'], 'INVALID')

    def test_META04_wrong_duplicate_incomplete_roster(self):
        with self.assertRaises(MetadataError):
            normalize_description(raw(payload()), '2', 'fixture')
        record = normalize_description(raw(payload()), '1', 'fixture')
        with self.assertRaises(MetadataError):
            registry_coverage([record, record], ['1', '2'])
        with self.assertRaises(MetadataError):
            registry_coverage([record], ['1', '1'])
        coverage = registry_coverage([record], ['1', '2'])
        self.assertFalse(coverage['description_roster_complete'])
        self.assertEqual(coverage['missing_aids'], ['2'])

    def test_META05_match_does_not_certify_rows(self):
        record = normalize_description(raw(payload()), '1', 'fixture')
        result = compare_version(record, {'version': 1, 'revision': 2, 'last_modified': '2008-01-01'})
        self.assertEqual(result['version_revision_verdict'], 'MATCH_OBSERVED_VERSION_METADATA')
        self.assertEqual(result['historical_activity_rows_equivalent'], 'NOT_CERTIFIED')
        self.assertEqual(result['complete_publication_tuple'], 'INDETERMINATE')

    def test_META06_difference_missing_and_date_semantics(self):
        record = normalize_description(raw(payload()), '1', 'fixture')
        expected = {'version': 1, 'revision': 3, 'last_modified': '2008-01-01'}
        self.assertEqual(compare_version(record, expected)['version_revision_verdict'], 'DIFFERENT')
        record['revision']['state'] = 'ABSENT'
        self.assertEqual(compare_version(record, expected)['version_revision_verdict'], 'INDETERMINATE')
        self.assertEqual(compare_version(record, expected)['date_verdict'], 'NOT_COMPARABLE_OR_ABSENT')
        expected['version'] = True
        with self.assertRaises(MetadataError):
            compare_version(record, expected)

    def test_META07_unresolved_scientific_fields(self):
        value = payload()
        descr = value['PC_AssayContainer'][0]['assay']['descr']
        del descr['target']
        del descr['results'][0]['unit']
        record = normalize_description(raw(value), '1', 'fixture')
        self.assertEqual(record['targets']['state'], 'ABSENT')
        self.assertEqual(record['readout_definitions'][0]['unit']['state'], 'ABSENT')
        self.assertFalse(record['scientific_plan_ready'])

    def test_META08_bounded_metadata_envelope_only(self):
        for data in (b' ' * 101, b'[' * 33 + b'0' + b']' * 33):
            with self.subTest(data=data[:10]), self.assertRaises(MetadataError):
                strict_json(data, byte_limit=100)
        value = payload()
        value['PC_AssayContainer'][0]['assay']['data'] = None
        with self.assertRaises(MetadataError):
            normalize_description(raw(value), '1', 'fixture')
        for value in ({'question': 'SYNTHETIC', 'answer': None},
                      {'PC_AssayContainer': [{'assay': {'descr': {}, 'data': 'DO_NOT_PROCESS'}}]}):
            with self.subTest(value=value), self.assertRaises(MetadataError):
                normalize_description(raw(value), '1', 'fixture')

    def test_META09_benchmark_objective_rights_and_metrics(self):
        path = Path(__file__).resolve().parents[2] / 'research/manifests/goal4r2a2_benchmark_readiness_v1.json'
        manifest = json.loads(path.read_text())
        blockers = benchmark_blockers(manifest)
        self.assertIn('OUTPUT_OBJECTIVE_MISMATCH', blockers)
        self.assertIn('COMMERCIAL_DATA_REUSE_NOT_CLEARED', blockers)
        self.assertIn('NATIVE_RUNTIME_NOT_VERIFIED', blockers)
        # Two feasible attempts, only one solved; one infeasible attempt.
        flags = ([True, True, False], [True, True, True], [True, False, False])
        self.assertEqual(feasibility_f1(*flags, 'pinned_code_attempt'), .8)
        self.assertEqual(feasibility_f1(*flags, 'card_full_solution'), .5)
        # The card still counts an infeasible attempt as FP, regardless of quality.
        self.assertAlmostEqual(feasibility_f1([True, False], [True, True], [True, False], 'card_full_solution'), 2/3)

    def test_META10_exposure_and_split_identity(self):
        self.assertEqual(prospective_role('example-group', {'example-group'}, True, 'salt'), 'QUARANTINE')
        self.assertEqual(prospective_role('unknown-group', set(), False, 'salt'), 'QUARANTINE')
        for status in ('UNKNOWN', 'false', 1, None):
            self.assertEqual(prospective_role('unknown-group', set(), status, 'salt'), 'QUARANTINE')
        first = prospective_role('synthetic-group', set(), True, 'fixed-salt')
        self.assertEqual(first, prospective_role('synthetic-group', set(), True, 'fixed-salt'))
        self.assertIn(first, ('development', 'validation', 'evaluation'))
        manifest = {'source': 'synthetic-index', 'groups_resolved': False, 'actual_roster': 'NOT_FROZEN'}
        checksum = digest(manifest)
        self.assertTrue(verify_manifest(manifest, checksum))
        changed = copy.deepcopy(manifest)
        changed['groups_resolved'] = True
        with self.assertRaises(MetadataError):
            verify_manifest(changed, checksum)
