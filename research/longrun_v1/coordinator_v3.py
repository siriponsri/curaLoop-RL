"""Additive administrative failed-attempt closure; never certifies a prior PASS."""

import hashlib
import json
from datetime import datetime, timezone

from .coordinator_v2 import Coordinator as Base
from .coordinator import AdmissionError
from .windows_terminal_v2 import observe


class Coordinator(Base):
    def reconcile_failed_windows_identity(self, attempt, launch_bytes, receipt_bytes, proof_bytes):
        launch, receipt, proof = [json.loads(raw) for raw in (launch_bytes, receipt_bytes, proof_bytes)]
        receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()
        with self.transaction() as con:
            row = con.execute('SELECT * FROM jobs WHERE attempt=?', (attempt,)).fetchone()
            if not row or row['state'] != 'UNKNOWN' or row['host'] != 'local':
                raise AdmissionError('Only the original uncertain local attempt can be closed')
            permit = json.loads(row['permit'])
            if (launch['pid'] != row['pid'] or launch['birth_id'] != row['birth_id']
                    or proof['pid'] != row['pid'] or proof['birth_id'] != row['birth_id']
                    or proof['observed_exited'] is not True or proof['receipt_sha256'] != receipt_sha
                    or receipt['pid'] == row['pid'] or receipt['token'] != permit['token']
                    or launch['token'] != permit['token'] or proof['token'] != permit['token']
                    or receipt['attempt'] != attempt or receipt['bundle_sha256'] != permit['bundle_sha256']
                    or receipt['child_policy'] != 'WINDOWS_JOB_ACTIVE_PROCESS_LIMIT_ONE_NO_BREAKAWAY'):
                raise AdmissionError('Original wrapper/resource failure identities differ')
            observations = [observe(pid) for pid in (row['pid'], receipt['pid'])]
            completion = {'status': 'FAILED_RECONCILED', 'utc': datetime.now(timezone.utc).isoformat(),
                'original_failure': 'FAIL_TERMINAL_IDENTITY_BINDING', 'original_pass_certified': False,
                'terminal_cleanup_only': True, 'reservation_retained_seconds': row['reserved'],
                'worker_reported_cpu_seconds': receipt['cpu_seconds'], 'cpu_seconds': 0,
                'cpu_seconds_zero_means_not_added_to_verified_direct_handle_cpu': True,
                'native_observations': observations, 'wrapper_pid': row['pid'], 'wrapper_birth_id': row['birth_id'],
                'worker_pid': receipt['pid'], 'bundle_sha256': permit['bundle_sha256'],
                'receipt_sha256': receipt_sha, 'launch_sha256': hashlib.sha256(launch_bytes).hexdigest(),
                'proof_sha256': hashlib.sha256(proof_bytes).hexdigest()}
            con.execute('UPDATE jobs SET state=?,receipt_sha256=?,completion=? WHERE attempt=? AND state=?',
                        ('FAILED_RECONCILED', receipt_sha, json.dumps(completion, sort_keys=True), attempt, 'UNKNOWN'))
            return completion
