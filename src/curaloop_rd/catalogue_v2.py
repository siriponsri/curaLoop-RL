"""Registered, hash-bound metadata projections; no arbitrary path or role tools."""

import csv
import hashlib
import io
import json
from pathlib import Path

from .contracts_v2 import field


class Catalogue:
    def __init__(self, root, registry):
        self.root, self.registry = Path(root).resolve(), registry

    def inspect(self, source_id):
        # Authority is the fixed registry, never a caller-provided role/path.
        if source_id not in self.registry:
            raise ValueError('Unregistered source rejected before payload access')
        record = self.registry[source_id]
        if record['role'] != 'METADATA_ONLY_DEVELOPMENT_EXPOSED':
            raise ValueError('Source role is not cleared')
        path = self.root / record['path']
        if path.is_symlink() or not path.resolve().is_relative_to(self.root):
            raise ValueError('Unsafe source path')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256'] or len(raw) > 16 * 1024**2:
            raise ValueError('Source bytes changed or oversized')
        out = {'source_id': source_id, 'sha256': record['sha256'], 'kind': record['kind'],
               'citation': record['citation'], 'measurement_status': 'METADATA_ONLY'}
        if record['kind'] == 'description':
            obj = json.loads(raw)
            if set(obj) != {'PC_AssayContainer'} or len(obj['PC_AssayContainer']) != 1:
                raise ValueError('Description-only envelope required')
            container = obj['PC_AssayContainer'][0]
            if set(container) != {'assay'} or set(container['assay']) != {'descr'}:
                raise ValueError('Activity rows or unexpected fields denied')
            d = container['assay']['descr']
            out.update(aid=d['aid']['id'], version=d['aid']['version'], revision=d['revision'],
                       readouts=[{'tid': r['tid'], 'name': r['name'], 'type': r['type'],
                                  'unit': field(r, 'unit'), 'sunit': field(r, 'sunit'),
                                  'locator': '/PC_AssayContainer/0/assay/descr/results/' + str(i)}
                                 for i, r in enumerate(d.get('results', []))],
                       targets=[{'accession': t['mol_id'].get('protein_accession'),
                                 'locator': '/PC_AssayContainer/0/assay/descr/target/' + str(i) + '/mol_id/protein_accession'}
                                for i, t in enumerate(d.get('target', []))])
        elif record['kind'] == 'request':
            obj = json.loads(raw)
            out.update(requested_version=obj['request']['params']['version'],
                       http_status=obj['result']['status_code'], response_sha256=obj['response_sha256'])
        elif record['kind'] == 'uniprot':
            rows = list(csv.DictReader(io.StringIO(raw.decode()), delimiter='\t'))
            out['proteins'] = [{'entry': r['Entry'], 'reviewed': r['Reviewed'],
                                'refseq': r['RefSeq'], 'family': r['Protein families'],
                                'locator': 'TSV line ' + str(i + 2)} for i, r in enumerate(rows)]
        elif record['kind'] == 'policy':
            lines = raw.decode().splitlines()
            if not ('copyright' in lines[24].lower() and 'responsib' in lines[26].lower()):
                raise ValueError('Pinned policy support differs')
            out['copyright_clearance'] = 'NOT_ESTABLISHED_BY_PUBLIC_HOSTING'
            out['locator'] = 'lines 25,27'
        elif record['kind'] == 'attempts':
            obj = json.loads(raw)
            out['unavailable'] = [{'status': r['status'], 'locator': '/files/' + str(i)}
                                  for i, r in enumerate(obj['files']) if 66 <= i <= 69]
            if len(out['unavailable']) != 4 or any(r['status'] != 'ACCESS_FAILED' for r in out['unavailable']):
                raise ValueError('Expected unavailable-source support differs')
        else:
            raise ValueError('Unsupported metadata projection')
        return out

    def search(self, query):
        words = query.casefold().split()
        # Unavailable unrelated payloads are not opened by search.
        return [{'source_id': key, 'citation': r['citation']} for key, r in sorted(self.registry.items())
                if r['role'] == 'METADATA_ONLY_DEVELOPMENT_EXPOSED'
                and all(w in (key + ' ' + json.dumps(r['citation'], sort_keys=True)).casefold() for w in words)]
