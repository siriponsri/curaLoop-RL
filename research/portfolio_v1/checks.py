"""Frozen C01-C10 engineering checks on retained permitted metadata."""

import copy
import hashlib
import io
import json
import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch


def execute(root, output):
    sys.path.insert(0, str(root / 'src'))
    from curaloop_rd.portfolio_v1 import Portfolio, VERSION
    from curaloop_rd.mcp_v1 import Session, serve, MAX_MESSAGE_BYTES
    from curaloop_rd.contracts_v2 import canonical
    from curaloop_rd.workflow_v2 import Outbox
    def rejected(call):
        try: call()
        except ValueError: return
        raise AssertionError('Expected boundary rejection')
    app = Portfolio(root, root / 'inputs/workflow-registry.json', output / 'workspace')
    cases = []
    try:
        found = app.call('evidence_search', {'query': '1259375'})
        assert any(r['source_id'] == 'D1259375' for r in found['sources'])
        source = app.call('evidence_inspect', {'source_id': 'D1259375'})['source']
        assert source['readouts'][1]['unit'] == {'state': 'VALUE', 'value': 5}
        assert source['citation']['url'].endswith('/1259375/description/JSON')
        cases.append('C01')
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('Unexpected payload access')):
            rejected(lambda: app.call('evidence_inspect', {'source_id': 'alias_final_reserved'}))
        cases.append('C02')
        brief = {'report_id': 'readiness-ic50', 'question': 'Inspect the declared IC50 endpoint and unit.',
                 'kind': 'endpoint', 'source_ids': ['D1259375'], 'tid': 2}
        drafted = app.call('draft_metadata_plan', brief)
        assert drafted['report']['disposition'] == 'METADATA_REPORT'
        assert drafted['readiness_plan']['molecular_experiments_released'] is False
        blocked = app.call('draft_metadata_plan', dict(brief, report_id='blocked-log', tid=3))
        assert blocked['report']['disposition'] == 'BLOCKED_ENDPOINT_UNRESOLVED'
        assert blocked['report']['claims'][-1]['state'] == 'ABSENT'
        cases.append('C03')
        params = {'report_id': brief['report_id'], 'report_sha256': drafted['report']['report_sha256']}
        exported = app.call('local_export', params)
        assert app.call('local_export', params) == exported
        assert exported['manifest']['delivered'] is False and exported['manifest']['destination'] == 'LOCAL_PREVIEW_ONLY'
        assert len(list((output / 'workspace/readiness-ic50').iterdir())) == 6
        cases.append('C04')
        for name, arguments in [('evidence_inspect', {'source_id': '../escape'}), ('evidence_search', {'query': 'x', 'path': 'secret'}),
                                 ('unsupported', {}), ('draft_metadata_plan', dict(brief, report_id='bad', tid=True))]:
            rejected(lambda name=name, arguments=arguments: app.call(name, arguments))
        cases.append('C05')
        session = Session(app)
        assert session.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'})['error']['message'] == 'INITIALIZATION_REQUIRED'
        assert session.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'initialize',
               'params': {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'fixture', 'version': '1'}}})['result']['protocolVersion'] == '2025-11-25'
        assert session.handle({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) is None
        assert len(session.handle({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/list'})['result']['tools']) == 4
        assert len(session.handle({'jsonrpc': '2.0', 'id': 30, 'method': 'tools/list',
                                   'params': {'_meta': {'progressToken': 'bounded-check'}}})['result']['tools']) == 4
        bad_session = Session(app)
        assert 'error' in bad_session.handle({'jsonrpc': '2.0', 'id': 31, 'method': 'initialize',
            'params': {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {}}})
        assert session.handle({'jsonrpc': '2.0', 'id': 4, 'method': 'ping'})['result'] == {}
        cases.append('C06')
        sentinel = 'PRIVATE_MCP_BODY_SENTINEL'
        buffer = io.StringIO()
        serve(app, io.BytesIO(('{"' + sentinel + '":1,"' + sentinel + '":2}\n').encode()), buffer)
        assert sentinel not in buffer.getvalue() and 'PARSE_ERROR' in buffer.getvalue()
        buffer = io.StringIO(); serve(app, io.BytesIO(b'x' * (MAX_MESSAGE_BYTES + 2)), buffer)
        assert len(buffer.getvalue().splitlines()) == 1
        cases.append('C07')
        # Separate mutable fixture tree, never modify the frozen source bundle.
        copied = output / 'source-mutation-fixture'
        (copied / 'inputs').mkdir(parents=True)
        shutil.copytree(root / 'inputs/workflow', copied / 'inputs/workflow')
        shutil.copyfile(root / 'inputs/workflow-registry.json', copied / 'inputs/workflow-registry.json')
        other = Portfolio(copied, copied / 'inputs/workflow-registry.json', output / 'mutation-workspace')
        try:
            value = other.call('draft_metadata_plan', brief)
            registry = json.loads((copied / 'inputs/workflow-registry.json').read_text())
            (copied / registry['D1259375']['path']).write_text(sentinel, encoding='utf-8')
            rejected(lambda: other.call('local_export', {'report_id': brief['report_id'], 'report_sha256': value['report']['report_sha256']}))
        finally: other.close()
        box = Outbox(output / 'interruption-fixture')
        try:
            try: box.save('interrupted', drafted['report'], 0, interrupt=True)
            except InterruptedError: pass
            else: raise AssertionError('Fault not injected')
            box.save('interrupted', drafted['report'], 0)
            rejected(lambda: box.save('interrupted', drafted['report'], 0))
        finally: box.close()
        cases.append('C08')
        rejected(lambda: app.call('draft_metadata_plan', dict(brief, question='Valid changed report content')))
        html = (output / 'workspace/readiness-ic50/workspace.html').read_text()
        assert all(title in html for title in ['Evidence Workspace', 'Decision Workbench', 'Integration Kit', drafted['report']['report_sha256']])
        assert 'Molecular replay unmet' in html and 'Live agent untested' in html and '<script' not in html
        cases.append('C09')
        # C10 intra-process artifact inventory; parent additionally compares fresh processes and full return.
        manifest = exported['manifest']
        for name, expected in manifest['files'].items():
            assert hashlib.sha256((output / 'workspace/readiness-ic50' / name).read_bytes()).hexdigest() == expected
        cases.append('C10')
        assert cases == [c['id'] for c in json.loads((root / 'research/configs/lrbc_c_cases_v1.json').read_text())['cases']]
        return {'status': 'PASS', 'case_ids': cases, 'case_count': len(cases), 'core_version': VERSION,
                'demo_report_sha256': drafted['report']['report_sha256'], 'demo_manifest': manifest,
                'content_signature_sha256': hashlib.sha256(canonical(manifest).encode()).hexdigest(),
                'scope': 'INTERNAL_METADATA_READINESS_REPORTS_ONLY', 'qualified_molecular_replay': 'UNMET',
                'live_agent_evaluation': 'NOT_RUN', 'new_scientific_source_calls': 0,
                'synthetic_faults_labelled': True, 'actual_stdio_transport': 'SEPARATE_FROZEN_TRANSCRIPT_JOB_REQUIRED'}
    finally: app.close()
