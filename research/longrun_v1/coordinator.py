"""One local SQLite authority; remote workers receive immutable permits only."""

import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class AdmissionError(ValueError):
    pass


ACTIVE = ('RESERVED', 'DISPATCHED', 'RUNNING', 'UNKNOWN')


def stamp(value=None):
    return value or datetime.now(timezone.utc).isoformat()


def parsed(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


class Coordinator:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_file() or self.path.is_symlink():
            raise AdmissionError('Existing owned coordinator database required')

    @contextmanager
    def transaction(self):
        con = sqlite3.connect('file:' + self.path.resolve().as_posix() + '?mode=rw', uri=True,
                              timeout=10, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        con.execute('PRAGMA synchronous=FULL')
        con.execute('BEGIN IMMEDIATE')
        try:
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    @classmethod
    def initialize(cls, path, contract, cpus):
        path = Path(path)
        if path.exists() or set(cpus) != {'local', 'dr-train'}:
            raise AdmissionError('New database and explicit host CPU roster required')
        for ids in cpus.values():
            if not ids or len(set(ids)) != len(ids) or any(type(c) is not int or c < 0 for c in ids):
                raise AdmissionError('Invalid explicit CPU roster')
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents two initializers from resetting a ledger.
        with path.open('xb'):
            pass
        con = sqlite3.connect(path)
        try:
            con.execute('PRAGMA journal_mode=DELETE')
            con.execute('PRAGMA synchronous=FULL')
            con.executescript('''
CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE jobs(attempt TEXT PRIMARY KEY,stage TEXT NOT NULL,host TEXT NOT NULL,cpu INTEGER NOT NULL,
 state TEXT NOT NULL,reserved INTEGER NOT NULL,token TEXT UNIQUE NOT NULL,permit TEXT NOT NULL,
 pid INTEGER,birth_id TEXT,receipt_sha256 TEXT,completion TEXT);
CREATE TABLE gates(stage TEXT PRIMARY KEY,evidence_sha256 TEXT NOT NULL,status TEXT NOT NULL);
CREATE TABLE requests(id INTEGER PRIMARY KEY,service TEXT NOT NULL,charged_bytes INTEGER NOT NULL,
 state TEXT NOT NULL,identity TEXT UNIQUE NOT NULL);
CREATE TABLE source_releases(service TEXT PRIMARY KEY,evidence_sha256 TEXT NOT NULL);
''')
            for key, value in [('contract', contract), ('cpus', cpus), ('stopped_services', ['pubchem'])]:
                con.execute('INSERT INTO meta VALUES(?,?)', (key, json.dumps(value, sort_keys=True)))
            con.execute('INSERT INTO gates VALUES(?,?,?)', ('R0', hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest(), 'PASS'))
            con.commit()
        finally:
            con.close()
        return cls(path)

    @staticmethod
    def _meta(con, key):
        return json.loads(con.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()[0])

    def reserve(self, attempt, stage, host, bundle_sha256, available_memory, *, now=None):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', attempt) or not re.fullmatch(r'[0-9a-f]{64}', bundle_sha256):
            raise AdmissionError('Immutable safe attempt and source digest required')
        with self.transaction() as con:
            cfg, cpus = self._meta(con, 'contract'), self._meta(con, 'cpus')
            if host not in cpus or stage not in cfg['stage_caps_seconds']:
                raise AdmissionError('Unapproved host or stage')
            gate = con.execute('SELECT * FROM gates WHERE stage=?', (stage,)).fetchone()
            if not gate or gate['status'] != 'PASS':
                raise AdmissionError('Stage has no reviewed release')
            deadline = cfg['r0_deadline_utc'] if stage == 'R0' else cfg['bc_deadline_utc'] if stage == 'C' else cfg['b_deadline_utc']
            instant = stamp(now)
            if parsed(instant) >= parsed(deadline):
                raise AdmissionError('Absolute stage deadline reached')
            if con.execute('SELECT 1 FROM jobs WHERE attempt=?', (attempt,)).fetchone():
                raise AdmissionError('Attempt already reserved; no duplicate dispatch')
            active = list(con.execute("SELECT * FROM jobs WHERE state IN ('RESERVED','DISPATCHED','RUNNING','UNKNOWN')"))
            if len(active) >= cfg['maximum_combined_workers']:
                raise AdmissionError('Combined CPU slots exhausted')
            local_count = sum(r['host'] == 'local' for r in active)
            if host == 'local' and (local_count >= cfg['maximum_local_workers'] or sum(r['host'] == 'dr-train' for r in active) >= 4):
                raise AdmissionError('Local slot unavailable')
            if host == 'dr-train' and sum(r['host'] == 'dr-train' for r in active) >= (3 if local_count else 4):
                raise AdmissionError('Remote slot unavailable')
            busy = {r['cpu'] for r in active if r['host'] == host}
            free = [c for c in cpus[host] if c not in busy]
            if not free:
                raise AdmissionError('Distinct CPU lease unavailable')
            memory = cfg['local_initial_memory_bytes'] if host == 'local' else cfg['remote_job_memory_bytes']
            minimum_free = (1.5 * 1024**3 if host == 'local' else 8 * 1024**3)
            minimum_free += memory * (1 + sum(r['host'] == host for r in active))
            if type(available_memory) is not int or available_memory < max(minimum_free, memory):
                raise AdmissionError('Insufficient free memory at admission')
            reservation = cfg['initial_job_reservation_seconds']
            utility = cfg['r0_utility_reserve_seconds']
            stage_reserved = con.execute('SELECT COALESCE(SUM(reserved),0) FROM jobs WHERE stage=?', (stage,)).fetchone()[0]
            if stage_reserved + reservation + (utility if stage == 'R0' else 0) > cfg['stage_caps_seconds'][stage]:
                raise AdmissionError('Stage conservative CPU allowance exhausted')
            b_reserved = con.execute("SELECT COALESCE(SUM(reserved),0) FROM jobs WHERE stage!='C'").fetchone()[0]
            all_reserved = con.execute('SELECT COALESCE(SUM(reserved),0) FROM jobs').fetchone()[0]
            if stage != 'C' and cfg['historical_cpu_seconds'] + utility + b_reserved + reservation > cfg['b_cumulative_cap_seconds']:
                raise AdmissionError('Cumulative B allowance exhausted')
            if cfg['historical_cpu_seconds'] + utility + all_reserved + reservation > cfg['bc_cumulative_cap_seconds']:
                raise AdmissionError('Cumulative B+C allowance exhausted')
            token = str(uuid.uuid4())
            permit = {'attempt': attempt, 'stage': stage, 'host': host, 'cpu': free[0], 'token': token,
                      'reserved_cpu_seconds': reservation, 'guard_cpu_seconds': cfg['job_guard_cpu_seconds'],
                      'wall_seconds': cfg['job_wall_seconds'], 'memory_bytes': memory,
                      'bundle_sha256': bundle_sha256, 'deadline_utc': deadline, 'reserved_utc': instant,
                      'output_partition': 'runs/' + attempt, 'child_processes_allowed': False}
            con.execute('INSERT INTO jobs(attempt,stage,host,cpu,state,reserved,token,permit) VALUES(?,?,?,?,?,?,?,?)',
                        (attempt, stage, host, free[0], 'RESERVED', reservation, token, json.dumps(permit, sort_keys=True)))
            return permit

    def mark_launch(self, permit, pid, birth_id):
        if type(pid) is not int or pid <= 0 or type(birth_id) is not str or not birth_id:
            raise AdmissionError('Authoritative PID and birth identity required')
        with self.transaction() as con:
            row = con.execute('SELECT * FROM jobs WHERE attempt=? AND token=?', (permit['attempt'], permit['token'])).fetchone()
            if not row or row['state'] != 'RESERVED' or json.loads(row['permit']) != permit:
                raise AdmissionError('Stale or altered launch permit')
            con.execute('UPDATE jobs SET state=?,pid=?,birth_id=? WHERE attempt=?', ('RUNNING', pid, birth_id, permit['attempt']))

    def mark_unknown(self, permit):
        with self.transaction() as con:
            row = con.execute('SELECT * FROM jobs WHERE attempt=? AND token=?', (permit['attempt'], permit['token'])).fetchone()
            if not row or row['state'] not in ACTIVE or json.loads(row['permit']) != permit:
                raise AdmissionError('Unknown-state permit differs')
            con.execute('UPDATE jobs SET state=? WHERE attempt=?', ('UNKNOWN', permit['attempt']))

    def finish(self, permit, receipt_bytes, terminal_proof):
        if type(receipt_bytes) is not bytes:
            raise AdmissionError('Original terminal receipt bytes required')
        receipt_sha256 = hashlib.sha256(receipt_bytes).hexdigest()
        receipt = json.loads(receipt_bytes)
        if (receipt.get('verified_terminal') is not True or receipt.get('token') != permit['token']
                or receipt.get('attempt') != permit['attempt'] or receipt.get('host') != permit['host']
                or receipt.get('cpu_affinity') != [permit['cpu']]
                or receipt.get('actual_cpu_affinity') != [permit['cpu']]
                or receipt.get('bundle_sha256') != permit['bundle_sha256']
                or receipt.get('status') not in ('PASS', 'FAIL') or type(receipt.get('cpu_seconds')) not in (int, float)
                or not 0 <= receipt['cpu_seconds'] <= permit['reserved_cpu_seconds']):
            raise AdmissionError('Terminal receipt identity, affinity or CPU evidence differs')
        with self.transaction() as con:
            row = con.execute('SELECT * FROM jobs WHERE attempt=? AND token=?', (permit['attempt'], permit['token'])).fetchone()
            if not row or row['state'] not in ('RUNNING', 'UNKNOWN') or json.loads(row['permit']) != permit:
                raise AdmissionError('Terminal transition requires the original running permit')
            if (type(row['pid']) is not int or row['pid'] <= 0 or not row['birth_id']
                    or receipt.get('pid') != row['pid']
                    or terminal_proof.get('observed_exited') is not True or terminal_proof.get('pid') != row['pid']
                    or terminal_proof.get('birth_id') != row['birth_id']
                    or terminal_proof.get('receipt_sha256') != receipt_sha256
                    or type(terminal_proof.get('exit_code')) is not int
                    or (receipt['status'] == 'PASS') != (terminal_proof['exit_code'] == 0)):
                raise AdmissionError('Authoritative terminal process proof required')
            con.execute('UPDATE jobs SET state=?,receipt_sha256=?,completion=? WHERE attempt=?',
                        ('COMPLETED' if receipt['status'] == 'PASS' else 'FAILED', receipt_sha256,
                         json.dumps(receipt, sort_keys=True), permit['attempt']))

    def reserve_request(self, service, identity, max_bytes, *, metadata_only=False):
        with self.transaction() as con:
            cfg = self._meta(con, 'contract')
            approved = cfg.get('approved_requests', {}).get(identity)
            if not approved or approved['service'] != service or approved.get('metadata_only') != metadata_only:
                raise AdmissionError('Exact frozen request roster required before network reservation')
            if service not in cfg['request_caps'] or not identity:
                raise AdmissionError('Unapproved source identity')
            if service in self._meta(con, 'stopped_services'):
                raise AdmissionError('Historical source STOP remains; new source release required')
            if service == 'ncbi_metadata' and metadata_only is not True:
                raise AdmissionError('Metadata bucket cannot retrieve activity')
            used = con.execute('SELECT COUNT(*) FROM requests WHERE service=?', (service,)).fetchone()[0]
            if cfg['historical_requests'][service] + used >= cfg['request_caps'][service]:
                raise AdmissionError('Inherited source request ceiling exhausted')
            charged = con.execute('SELECT COALESCE(SUM(charged_bytes),0) FROM requests').fetchone()[0]
            if (type(max_bytes) is not int or not 0 < max_bytes <= cfg['per_response_byte_cap']
                    or cfg['historical_intake_decoded_bytes'] + charged + max_bytes > cfg['intake_decoded_byte_cap']):
                raise AdmissionError('Cumulative decoded-byte ceiling exhausted')
            try:
                con.execute('INSERT INTO requests(service,charged_bytes,state,identity) VALUES(?,?,?,?)',
                            (service, max_bytes, 'RESERVED', identity))
            except sqlite3.IntegrityError:
                raise AdmissionError('Request identity already reserved') from None

    def snapshot(self):
        with self.transaction() as con:
            cfg = self._meta(con, 'contract')
            jobs = [dict(r) for r in con.execute('SELECT * FROM jobs ORDER BY rowid')]
            requests = [dict(r) for r in con.execute('SELECT * FROM requests ORDER BY id')]
            return {'jobs': jobs, 'requests': requests, 'historical_cpu_seconds': cfg['historical_cpu_seconds'],
                    'utility_reserve_seconds': cfg['r0_utility_reserve_seconds'],
                    'retained_job_reservations_seconds': sum(r['reserved'] for r in jobs),
                    'stopped_services': self._meta(con, 'stopped_services')}
