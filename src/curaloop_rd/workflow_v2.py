"""A content-checked, resumable local report outbox, including blocked reports."""

import json
import os
import re
import sqlite3
import uuid
from pathlib import Path

from .contracts_v2 import canonical, digest, validate_report


def atomic_same(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or path.parent.resolve() != path.parent:
        raise ValueError('Canonical owned path required')
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Existing immutable artifact differs')
        return
    temp = path.parent / ('.' + path.name + '.' + uuid.uuid4().hex)
    with temp.open('xb') as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())
    try:
        os.link(temp, path)
    except FileExistsError:
        if path.is_symlink() or path.read_bytes() != data:
            raise ValueError('Concurrent artifact differs')
    finally:
        temp.unlink()


def markdown(value):
    lines = ['# R&D evidence report', '', value['question'], '', 'Disposition: **' + value['disposition'] + '**',
             '', 'Cached metadata; no activity results or external delivery.', '', '| Fact | State | Value | Source locator |',
             '| --- | --- | --- | --- |']
    for c in value['claims']:
        e = c['evidence']
        cells = [c['key'], c['state'], str(c['value']), e['source_id'] + ' ' + e['locator']]
        lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in cells) + ' |')
    lines += ['', '## Captured source ledger', '']
    for sid, source in value['source_ledger'].items():
        cite = source['citation']
        lines += ['- ' + sid + ': [' + cite['url'] + '](' + cite['url'] + '). Capture SHA256: `' + source['sha256'] + '`.',
                  '  Request parameters: `' + json.dumps(cite.get('params', {}), sort_keys=True) + '`.']
    lines += ['', 'Report SHA256: `' + value['report_sha256'] + '`', '', 'Limits: ' + '; '.join(value['limits']), '']
    return '\n'.join(lines)


class Outbox:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if Path(root).is_symlink():
            raise ValueError('Canonical output root required')
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'state.sqlite'
        if self.path.is_symlink():
            raise ValueError('State link denied')
        self.db = sqlite3.connect(self.path)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS reports(id TEXT PRIMARY KEY,hash TEXT NOT NULL,body TEXT NOT NULL,revision INTEGER NOT NULL)')

    def close(self):
        self.db.close()

    def save(self, report_id, value, expected_revision, *, interrupt=False):
        validate_report(value)
        if not re.fullmatch('[A-Za-z0-9_-]{1,64}', report_id) or type(expected_revision) is not int:
            raise ValueError('Safe report identity and exact revision required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.db.execute('SELECT hash,body,revision FROM reports WHERE id=?', (report_id,)).fetchone()
            if row:
                if row[0] != value['report_sha256'] or row[1] != canonical(value) or row[2] != expected_revision:
                    raise ValueError('Stale revision or changed report')
            elif expected_revision != 0:
                raise ValueError('New reports start at revision zero')
            folder = self.root / report_id
            atomic_same(folder / 'report.json', (canonical(value) + '\n').encode())
            if interrupt:
                raise InterruptedError('SYNTHETIC_INTERRUPT_AFTER_PERSIST')
            atomic_same(folder / 'report.md', markdown(value).encode())
            receipt = {'report_sha256': value['report_sha256'], 'destination': 'LOCAL_PREVIEW_ONLY',
                       'delivered': False, 'revision': 1}
            atomic_same(folder / 'preview.json', (canonical(receipt) + '\n').encode())
            if not row:
                self.db.execute('INSERT INTO reports VALUES(?,?,?,1)', (report_id, value['report_sha256'], canonical(value)))
            self.db.commit()
            return receipt
        except BaseException:
            self.db.rollback()
            raise
