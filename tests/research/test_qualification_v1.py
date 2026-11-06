"""Twelve frozen qualification cases, using constructed records and fake transport."""

import copy
import hashlib
import json
import unittest

from research.qualification_v1.contracts import (QualificationError, bind_columns, coverage,
    exact_sid_filter, family_gate, normalize_observations, positive_id, programme_rights,
    protected_identity_index, public_aggregate, replicate_state, sample_ids, value_state)
from research.qualification_v1.transport import BoundedTransport, SafeSession
from research.readiness_v1.contracts import MetadataError, strict_json


DEFINITION = {'tid': 1, 'name': 'IC50', 'type': 1, 'unit': 5}
BINDINGS = bind_columns([DEFINITION], ['IC50'])


def payload(sid=1, value=2., **extra):
    row = {'sid': sid, 'outcome': 2, 'data': [{'tid': 1, 'value': {'fval': value}}], **extra}
    return {'PC_AssayContainer': [{'assay': {'descr': {'aid': {'id': 7, 'version': 1},
                                                    'revision': 1, 'results': [DEFINITION]}}, 'data': [row]}]}


def encoded(obj):
    return json.dumps(obj).encode()


def feature(smiles='CCO'):
    return {'task_id': 'synthetic-reserved', 'role': 'final', 'family_id': 'f-reserved',
            'family': 'Synthetic family', 'source_role': 'test', 'source_member': 'synthetic',
            'member_sha256': '0' * 64, 'outcome_values_present': False,
            'records': [{'candidate_id': 's-' + hashlib.sha256(smiles.encode()).hexdigest(),
                         'canonical_smiles': smiles, 'source_row': 0, 'morgan_on_bits': [], 'scaffold': ''}]}


class FakeResponse:
    def __init__(self, chunks=(b'{}',), status=200):
        self.chunks, self.status_code = chunks, status
        self.headers = {'content-type': 'application/json'}
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('Synthetic HTTP failure')

    def iter_content(self, chunk_size):
        return iter(self.chunks)

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, response):
        self.response, self.headers = response, {}

    def request(self, method, url, **kwargs):
        assert kwargs['stream'] is True and kwargs['allow_redirects'] is False
        return self.response

    def close(self):
        pass


class QualificationCases(unittest.TestCase):
    def test_Q01_strict_records(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e309}'):
            with self.assertRaises(MetadataError):
                strict_json(raw)
        self.assertEqual(strict_json(b'{"zero":0,"null":null}'), {'zero': 0, 'null': None})
        self.assertFalse(positive_id(True))
        self.assertFalse(positive_id('0'))
        self.assertTrue(positive_id('17'))

    def test_Q02_programme_rights(self):
        policy = {'intended_use': 'INTERNAL_NONCOMMERCIAL_COMPUTATIONAL_QUALIFICATION',
                  'policy_evidence': [{'category': 1, 'url': 'https://grants.nih.gov/synthetic'}]}
        self.assertEqual(programme_rights({'project_category_raw': 1}, policy, True), 'INTERNAL_RESEARCH_USE_SUPPORTED_BY_MLP_POLICY')
        for category in (None, 255, True, '1'):
            self.assertTrue(programme_rights({'project_category_raw': category}, policy, True).startswith('QUARANTINE'))
        self.assertTrue(programme_rights({'project_category_raw': 1}, policy).startswith('QUARANTINE'))
        self.assertTrue(programme_rights({'project_category_raw': 1, 'restriction_flags': ['notice']}, policy, True).startswith('QUARANTINE'))

    def test_Q03_protected_identity(self):
        registry = {'assays': [{'assay_id': 'A', 'family_id': 'f-reserved', 'uniprot_accession': 'P1'}]}
        result = protected_identity_index([feature(), feature('CCO'), feature('CC')], registry)
        self.assertEqual(result['unique_canonical_structures'], 2)
        self.assertEqual(result['record_positions'], 3)
        self.assertEqual(result['assay_ids'], ['A'])
        bad = feature()
        bad['records'][0]['activity'] = 1
        with self.assertRaises(QualificationError):
            protected_identity_index([bad], registry)

    def test_Q04_family_quarantine(self):
        protected = {'uniprot_accessions': ['P1'], 'family_ids': ['F1']}
        self.assertEqual(family_gate({'P2'}, {'P2': 'F2'}, protected, True), 'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY')
        for args in [({'P1'}, {'P1': 'F1'}, True), ({'P2'}, {'P2': 'F1'}, True),
                     ({'P3'}, {}, True), ({'P2'}, {'P2': 'F2'}, 'UNKNOWN')]:
            self.assertTrue(family_gate(args[0], args[1], protected, args[2]).startswith('QUARANTINE'))

    def test_Q05_outcome_independent_sample(self):
        first = sample_ids(['1', '2', '3', '4'], 'fixed', 2, excluded=['4'])
        self.assertEqual(first, sample_ids(['4', '3', '2', '1', '1'], 'fixed', 2, excluded=['4']))
        self.assertNotIn('4', first)
        self.assertEqual(len(first), 2)

    def test_Q06_exact_filter_and_transport(self):
        self.assertEqual(exact_sid_filter(['1', '2'], {'1', '2'}), {'sid': '1,2'})
        for ids in ([], ['1', '1'], ['3'], ['01'], ['1'] * 129):
            with self.assertRaises(QualificationError):
                exact_sid_filter(ids, {'1', '2'})
        spec = [{'path': 'assay/aid/7/JSON', 'params': {'sid': '1'}}]
        def make(response, limit=10):
            return BoundedTransport('https://pubchem.ncbi.nlm.nih.gov/rest/pug', spec, 1, limit, 20,
                                    interval=0, session_factory=lambda: FakeSession(response))
        good = make(FakeResponse())
        response = SafeSession(good).request('GET', good.base_url + '/assay/aid/7/JSON', params={'sid': '1'}, timeout=1)
        self.assertEqual(response._content, b'{}')
        for fake in (FakeResponse(status=302), FakeResponse(chunks=(b'123456', b'123456'))):
            guard = make(fake)
            with self.assertRaises(QualificationError):
                SafeSession(guard).request('GET', guard.base_url + '/assay/aid/7/JSON', params={'sid': '1'}, timeout=1)
            self.assertTrue(fake.closed)
            self.assertTrue(guard.failed)
            before = len(guard.attempts)
            with self.assertRaisesRegex(QualificationError, 'Transport stopped'):
                SafeSession(guard).request('GET', guard.base_url + '/assay/aid/7/JSON', params={'sid': '1'}, timeout=1)
            self.assertEqual(len(guard.attempts), before)
        with self.assertRaises(QualificationError):
            SafeSession(make(FakeResponse())).request('GET', 'https://example.com/assay/aid/7/JSON', params={'sid': '1'}, timeout=1)

    def test_Q07_identifiers_before_values(self):
        bad = payload(sid=99, value='PROTECTED_SENTINEL_NEVER_INTERPRET')
        with self.assertRaisesRegex(QualificationError, 'row identifier'):
            normalize_observations(encoded(bad), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)

    def test_Q08_replicates(self):
        first = normalize_observations(encoded(payload(value=1)), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)['records'][0]
        second = normalize_observations(encoded(payload(value=2)), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)['records'][0]
        self.assertEqual(replicate_state([first, second]), 'CONFLICTING_REPLICATES')
        self.assertEqual(replicate_state([first, first]), 'CONSISTENT_OBSERVATION')
        self.assertIn('NOT_PROOF_UNTESTED', replicate_state([]))

    def test_Q09_observation_states(self):
        self.assertEqual(value_state(0)['value'], 0)
        self.assertEqual(value_state(0, concentration=True)['state'], 'INVALID_NONPOSITIVE_CONCENTRATION')
        self.assertEqual(value_state(None)['state'], 'NULL')
        self.assertEqual(value_state('>10')['state'], 'CENSORED')
        self.assertEqual(value_state('inactive')['state'], 'QUALITATIVE_OR_UNRESOLVED_TEXT')
        self.assertEqual(value_state(1., comment='qualifier unresolved')['state'], 'QUALIFIER_REVIEW')
        obj = payload()
        obj['PC_AssayContainer'][0]['data'][0]['data'] = []
        record = normalize_observations(encoded(obj), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)['records'][0]
        self.assertEqual(record['readouts']['1']['state'], 'MISSING_TID')
        with self.assertRaises(QualificationError):
            normalize_observations(encoded(payload(value=True)), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)

    def test_Q10_source_identity(self):
        result = normalize_observations(encoded(payload()), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)
        self.assertEqual(result['historical_rows_equivalent'], 'NOT_CERTIFIED')
        self.assertEqual((result['assay_version'], result['assay_revision']), (1, 1))
        for field, invalid in [('outcome', True), ('outcome', 99), ('version', '1')]:
            bad_result = payload(**{field: invalid})
            with self.assertRaises(QualificationError):
                normalize_observations(encoded(bad_result), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)
        with self.assertRaises(QualificationError):
            normalize_observations(encoded(payload()), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=2)
        for field, invalid in [('type', True), ('type', 1.0), ('unit', True), ('unit', 5.0), ('sunit', 5)]:
            malformed = copy.deepcopy(payload())
            malformed['PC_AssayContainer'][0]['assay']['descr']['results'][0][field] = invalid
            with self.assertRaises(QualificationError):
                normalize_observations(encoded(malformed), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)
        with self.assertRaises(QualificationError):
            normalize_observations(encoded(payload(comment={})), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)
        with self.assertRaises(QualificationError):
            normalize_observations(encoded(payload()), '8', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)
        bad = copy.deepcopy(payload())
        bad['PC_AssayContainer'][0]['assay']['descr']['results'][0]['unit'] = 14
        with self.assertRaises(QualificationError):
            normalize_observations(encoded(bad), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)

    def test_Q11_denominators(self):
        result = coverage({'1', '2', '3'}, {'1', '2'}, {'1'})
        self.assertIsNone(result['listed_total'])
        self.assertEqual((result['sampled'], result['returned'], result['eligible']), (3, 2, 1))
        self.assertTrue(result['unreturned_is_not_assumed_untested'])
        with self.assertRaises(QualificationError):
            coverage({'1'}, {'2'}, set())

    def test_Q12_public_exposure_boundary(self):
        observations = normalize_observations(encoded(payload(value=73.12345)), '7', {'1'}, BINDINGS, role='DEVELOPMENT_EXPOSED', expected_version=1, expected_revision=1)
        public = public_aggregate(observations, ['1'])
        self.assertNotIn('73.12345', json.dumps(public))
        self.assertFalse(public['raw_outcomes_or_values_included'])
        role_missing = dict(observations)
        del role_missing['role']
        with self.assertRaises(QualificationError):
            public_aggregate(role_missing, ['1'])
        observations['role'] = 'final'
        with self.assertRaises(QualificationError):
            public_aggregate(observations, ['1'])
