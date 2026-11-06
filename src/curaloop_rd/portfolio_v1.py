"""One internal metadata core behind the three thin portfolio interfaces."""

import html
import json
import re
from pathlib import Path

from .catalogue_v2 import Catalogue
from .contracts_v2 import canonical, digest, validate_report
from .decision_v2 import decide
from .workflow_v2 import Outbox, atomic_same

VERSION = 'curaloop-metadata-portfolio-1.0'
LIMITS = {'scope': 'INTERNAL_CACHED_METADATA_RESEARCH', 'molecular_replay': 'UNMET',
          'live_agent_evaluation': 'NOT_RUN', 'commercial_data_rights': 'NOT_CLEARED',
          'external_delivery': False, 'new_scientific_source_calls': 0}

TOOLS = [
    {'name': 'evidence_search', 'description': 'Search the registered cached metadata catalogue; no live retrieval.',
     'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string', 'maxLength': 512}}, 'required': ['query'], 'additionalProperties': False}},
    {'name': 'evidence_inspect', 'description': 'Inspect a registered positive metadata projection and captured citation.',
     'inputSchema': {'type': 'object', 'properties': {'source_id': {'type': 'string', 'maxLength': 64}}, 'required': ['source_id'], 'additionalProperties': False}},
    {'name': 'draft_metadata_plan', 'description': 'Persist a readiness/gap plan and cited report. Does not release molecular experiments.',
     'inputSchema': {'type': 'object', 'properties': {'report_id': {'type': 'string', 'pattern': '^[A-Za-z0-9_-]{1,64}$'},
       'question': {'type': 'string', 'maxLength': 2048}, 'kind': {'type': 'string', 'enum': ['endpoint', 'historical', 'identity', 'rights', 'unavailable']},
       'source_ids': {'type': 'array', 'items': {'type': 'string', 'maxLength': 64}, 'minItems': 1, 'maxItems': 4, 'uniqueItems': True},
       'tid': {'type': 'integer', 'minimum': 1}},
       'required': ['report_id', 'question', 'kind', 'source_ids'], 'additionalProperties': False}},
    {'name': 'local_export', 'description': 'Create an idempotent portable local handoff and visual preview; never sends to a team tool.',
     'inputSchema': {'type': 'object', 'properties': {'report_id': {'type': 'string', 'pattern': '^[A-Za-z0-9_-]{1,64}$'},
                        'report_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}},
                        'required': ['report_id', 'report_sha256'], 'additionalProperties': False}}
]
for _tool in TOOLS:
    _tool['outputSchema'] = {'type': 'object'}
    _tool['annotations'] = {'readOnlyHint': _tool['name'].startswith('evidence_'), 'destructiveHint': False,
                            'idempotentHint': True, 'openWorldHint': False}


def safe_id(value):
    if type(value) is not str or not re.fullmatch('[A-Za-z0-9_-]{1,64}', value):
        raise ValueError('Safe bounded identity required')
    return value


class Portfolio:
    def __init__(self, source_root, registry_path, workspace):
        self.source_root, self.registry_path = Path(source_root).resolve(), Path(registry_path).resolve()
        if Path(registry_path).is_symlink() or not self.registry_path.is_relative_to(self.source_root):
            raise ValueError('Canonical registered source authority required')
        registry = json.loads(self.registry_path.read_text())
        if not registry or len(registry) > 256:
            raise ValueError('Bounded registry required')
        self.catalogue = Catalogue(self.source_root, registry)
        self.workspace = Path(workspace).resolve()
        if Path(workspace).is_symlink(): raise ValueError('Canonical workspace required')
        self.box = Outbox(self.workspace)

    def close(self): self.box.close()

    def call(self, name, arguments):
        descriptors = {t['name']: t for t in TOOLS}
        if name not in descriptors or type(arguments) is not dict:
            raise ValueError('Unsupported tool or argument shape')
        schema = descriptors[name]['inputSchema']
        if set(arguments) - set(schema['properties']) or not set(schema['required']) <= set(arguments):
            raise ValueError('Missing or unsupported arguments')
        if name == 'evidence_search':
            query = arguments['query']
            if type(query) is not str or not 1 <= len(query) <= 512: raise ValueError('Bounded query required')
            return {'sources': self.catalogue.search(query), 'limits': LIMITS}
        if name == 'evidence_inspect':
            return {'source': self.catalogue.inspect(safe_id(arguments['source_id'])), 'limits': LIMITS}
        report_id = safe_id(arguments['report_id'])
        if name == 'draft_metadata_plan':
            question, kind, sources = arguments['question'], arguments['kind'], arguments['source_ids']
            if type(question) is not str or not 1 <= len(question) <= 2048 or kind not in ('endpoint', 'historical', 'identity', 'rights', 'unavailable'):
                raise ValueError('Bounded supported metadata intent required')
            if type(sources) is not list or not 1 <= len(sources) <= 4 or any(type(s) is not str for s in sources) or len(sources) != len(set(sources)):
                raise ValueError('Unique registered source identities required')
            expected = {'endpoint': 1, 'historical': 4, 'identity': 2, 'rights': 1, 'unavailable': 1}[kind]
            if len(sources) != expected: raise ValueError('Intent source arity differs')
            brief = {'question': question, 'kind': kind, 'source_ids': sources}
            if kind == 'endpoint':
                if type(arguments.get('tid')) is not int or arguments['tid'] <= 0: raise ValueError('Positive exact readout ID required')
                brief['tid'] = arguments['tid']
            elif 'tid' in arguments: raise ValueError('Readout ID is not applicable to this intent')
            value = decide(brief, self.catalogue)
            row = self.box.db.execute('SELECT revision FROM reports WHERE id=?', (report_id,)).fetchone()
            receipt = self.box.save(report_id, value, row[0] if row else 0)
            plan = self._plan(value)
            atomic_same(self.workspace / report_id / 'readiness-plan.json', (canonical(plan) + '\n').encode())
            return {'report_id': report_id, 'report': value, 'readiness_plan': plan, 'preview': receipt, 'limits': LIMITS}
        requested = arguments['report_sha256']
        if type(requested) is not str or not re.fullmatch('[a-f0-9]{64}', requested): raise ValueError('Exact report digest required')
        row = self.box.db.execute('SELECT body,revision FROM reports WHERE id=?', (report_id,)).fetchone()
        if row is None: raise ValueError('Unknown report')
        value = validate_report(json.loads(row[0]))
        if value['report_sha256'] != requested: raise ValueError('Requested report identity differs')
        for sid, source in value['source_ledger'].items():
            current = self.catalogue.inspect(sid)
            if current['sha256'] != source['sha256'] or current['citation'] != source['citation']:
                raise ValueError('Source changed since report creation')
        self.box.save(report_id, value, row[1])
        folder = self.workspace / report_id
        plan = self._plan(value)
        if (folder / 'readiness-plan.json').read_bytes() != (canonical(plan) + '\n').encode():
            raise ValueError('Readiness plan content changed')
        visual = self._visual(report_id, value, plan)
        atomic_same(folder / 'workspace.html', visual.encode())
        manifest = {'schema': VERSION, 'report_id': report_id, 'report_sha256': requested,
                    'files': {p.name: __import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in
                              [folder / n for n in ('report.json', 'report.md', 'preview.json', 'readiness-plan.json', 'workspace.html')]},
                    'destination': 'LOCAL_PREVIEW_ONLY', 'delivered': False, 'limits': LIMITS}
        atomic_same(folder / 'handoff-manifest.json', (canonical(manifest) + '\n').encode())
        return {'manifest': manifest, 'local_folder': str(folder), 'limits': LIMITS}

    @staticmethod
    def _plan(value):
        actions = {
          'METADATA_REPORT': ['Review the declared metadata and intended-use limits.', 'Define and qualify a scientific endpoint/population before any molecular experiment.'],
          'BLOCKED_ENDPOINT_UNRESOLVED': ['Obtain the source-declared unit or definition.', 'Consult the study owner before a material endpoint change.'],
          'BLOCKED_HISTORICAL_IDENTITY': ['Obtain independent provenance of the exact historical snapshot before reconstruction claims.'],
          'BLOCKED_RIGHTS_UNRESOLVED': ['Obtain intended-use clearance before redistribution or commercial packaging.'],
          'BLOCKED_REQUIRED_SOURCE': ['Obtain the missing permitted source through an owner-approved route.', 'Keep unsupported conclusions blocked; do not retry automatically.']}
        return {'scope': 'METADATA_READINESS_AND_GAPS_ONLY', 'disposition': value['disposition'],
                'report_sha256': value['report_sha256'], 'next_actions': actions[value['disposition']],
                'molecular_experiments_released': False, 'qualified_molecular_replay': 'UNMET'}

    @staticmethod
    def _visual(report_id, value, plan):
        esc = lambda text: html.escape(str(text), quote=True)
        facts = ''.join('<tr><td>' + esc(c['key']) + '</td><td>' + esc(c['state']) + '</td><td>' + esc(c['value']) + '</td><td>' + esc(c['evidence']['source_id']) + '</td></tr>' for c in value['claims'])
        actions = ''.join('<li>' + esc(a) + '</li>' for a in plan['next_actions'])
        sources = ''.join('<li><strong>' + esc(sid) + '</strong><p>' + esc(s['citation']['url']) + '</p><code>' + esc(s['sha256']) + '</code></li>' for sid, s in value['source_ledger'].items())
        return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CuraLoop Evidence Workspace</title><style>
:root{color-scheme:dark;--bg:#091a22;--panel:#102b35;--line:#284550;--ink:#e9f3f3;--muted:#a8c0c5;--accent:#6de0c3}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:42px 28px}nav{display:flex;gap:24px;flex-wrap:wrap;padding:18px 0;border-block:1px solid var(--line)}a{color:var(--accent)}header p,.muted{color:var(--muted)}h1{font-size:clamp(32px,5vw,56px);line-height:1.12;margin:14px 0}h2{font-size:26px}.eyebrow{letter-spacing:.14em;text-transform:uppercase;font-size:12px;color:var(--accent)}.badge{display:inline-block;border:1px solid var(--line);border-radius:30px;padding:6px 14px;color:#ffdc91;font-size:13px}.card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px 8px;border-bottom:1px solid var(--line)}code{overflow-wrap:anywhere;font-size:12px}li{margin:12px 0}li p{margin:4px 0;overflow-wrap:anywhere}details{margin:18px 0}summary{cursor:pointer;color:var(--accent)}.grid{display:grid;grid-template-columns:2fr 1fr;gap:24px}@media(max-width:720px){.grid{grid-template-columns:1fr}main{padding:24px 16px}table{font-size:12px}.card{padding:16px}}
</style><main><header><div class="eyebrow">CuraLoop / Internal research prototype</div><h1>Evidence before decisions.</h1><p>One traceable path from registered metadata to a readiness plan and local handoff.</p><span class="badge">Cached metadata · Molecular replay unmet · Live agent untested</span></header><nav><a href="#evidence">Evidence Workspace</a><a href="#decision">Decision Workbench</a><a href="#integration">Integration Kit</a></nav>''' + '<section class="card"><div class="eyebrow">' + esc(report_id) + '</div><h2>' + esc(value['question']) + '</h2><span class="badge">' + esc(value['disposition']) + '</span></section><section id="evidence" class="card"><h2>Evidence Workspace</h2><p class="muted">Declared fields and missingness are preserved.</p><table><thead><tr><th>Fact</th><th>State</th><th>Value</th><th>Source</th></tr></thead><tbody>' + facts + '</tbody></table><details><summary>Inspect captured provenance</summary><ul>' + sources + '</ul></details></section><section id="decision" class="card"><h2>Decision Workbench</h2><p>Metadata readiness and gaps. No molecular experiment has been released.</p><ol>' + actions + '</ol></section><section id="integration" class="card"><h2>Integration Kit</h2><p>Portable files with a stable report identity. Destination: local preview only.</p><p><a href="report.md">English report</a> · <a href="report.json">Structured evidence</a> · <a href="readiness-plan.json">Readiness plan</a> · <a href="handoff-manifest.json">Handoff manifest</a></p><code>' + esc(value['report_sha256']) + '</code></section><footer class="muted">Internal metadata research. No commercial data clearance, autonomous-agent efficacy or molecular benefit is established.</footer></main></html>'
