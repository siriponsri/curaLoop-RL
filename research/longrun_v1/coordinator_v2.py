"""Append-only R1 release around the tested immutable v1 accounting authority."""

import hashlib
import json
from datetime import datetime, timedelta, timezone

from .coordinator import Coordinator as Base, AdmissionError, parsed, stamp


class Coordinator(Base):
    def release_r1(self, evidence_sha256, source_allocation_sha256):
        if any(len(v) != 64 or any(c not in '0123456789abcdef' for c in v)
               for v in (evidence_sha256, source_allocation_sha256)):
            raise AdmissionError('Reviewed release and allocation digests required')
        with self.transaction() as con:
            cfg = self._meta(con, 'contract')
            start = datetime.now(timezone.utc)
            deadline = min(start + timedelta(hours=12), parsed(cfg['b_deadline_utc']))
            if deadline <= start or con.execute('SELECT 1 FROM gates WHERE stage=?', ('R1',)).fetchone():
                raise AdmissionError('R1 already released or expired')
            release = {'start_utc': start.isoformat(), 'deadline_utc': deadline.isoformat(),
                       'evidence_sha256': evidence_sha256, 'source_allocation_sha256': source_allocation_sha256}
            con.execute('INSERT INTO meta VALUES(?,?)', ('r1_release', json.dumps(release, sort_keys=True)))
            con.execute('INSERT INTO gates VALUES(?,?,?)', ('R1', evidence_sha256, 'PASS'))
            return release

    def reserve(self, attempt, stage, host, bundle_sha256, available_memory, *, now=None):
        if stage != 'R1':
            return super().reserve(attempt, stage, host, bundle_sha256, available_memory, now=now)
        with self.transaction() as con:
            release = self._meta(con, 'r1_release')
            if parsed(stamp(now)) >= parsed(release['deadline_utc']):
                raise AdmissionError('R1 subdeadline reached')
        # Super retains the original slot, CPU and cumulative charge atomically.
        # A failure after reservation leaves it held; no dispatch until this API returns.
        permit = super().reserve(attempt, stage, host, bundle_sha256, available_memory, now=now)
        with self.transaction() as con:
            release = self._meta(con, 'r1_release')
            if parsed(stamp(now)) >= parsed(release['deadline_utc']):
                raise AdmissionError('R1 expired after reservation; lease retained')
            permit['deadline_utc'] = release['deadline_utc']
            con.execute('UPDATE jobs SET permit=? WHERE attempt=? AND token=? AND state=?',
                        (json.dumps(permit, sort_keys=True), attempt, permit['token'], 'RESERVED'))
        return permit
