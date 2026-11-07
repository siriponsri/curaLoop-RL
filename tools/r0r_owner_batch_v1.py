"""Warm the existing PDF library once; preserve each file's 20-second ceiling.

Only unattempted files run here. A bounded repair of local processing is a
separate operator action; stopped HTTP sources remain closed.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
import threading
import time
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, save
from r0r_owner_pdf_intake_v2 import run

FILES = ('CHEMBL1140224_supplement.pdf', 'CHEMBL1140235_supplement.pdf', 'CHEMBL1156448.pdf')


class PhaseGuard:
    """Per-file monitor inside one already OS-limited, single-CPU process."""
    enclosing_receipt = 'owner-batch-v1-resource.json'
    def __init__(self, name, wall, cpu_seconds):
        self.started = time.monotonic()
        self.cpu = time.process_time()
        self.cpu_limit = cpu_seconds
        self.wall_limit = wall
        self.path = PRIVATE/(name+'-phase-resource.json')
        assert not self.path.exists()
        self.completed = threading.Event()
        self.base = {'schema':'curaloop.r0r.file-phase.v1', 'pid':os.getpid(),
                     'start_utc':datetime.now(timezone.utc).isoformat(),
                     'cpu_limit_seconds':cpu_seconds, 'wall_limit_seconds':wall,
                     'enclosing_os_guard':self.enclosing_receipt,
                     'scope':'File phase only; library startup is in the enclosing receipt'}
        self.write('RUNNING')
        threading.Thread(target=self.watch, daemon=True).start()

    def write(self, status, **extra):
        save(self.path, {**self.base, 'status':status,
                        'wall_seconds':time.monotonic()-self.started,
                        'cpu_seconds':time.process_time()-self.cpu, **extra})

    def watch(self):
        while not self.completed.wait(.1):
            if time.process_time()-self.cpu >= self.cpu_limit or time.monotonic()-self.started >= self.wall_limit:
                self.write('FAIL_RESOURCE_LIMIT')
                os._exit(124)

    def finish(self, status, **extra):
        self.completed.set()
        self.write(status, **extra)


def main():
    book = json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='ACTIVE'
    assert book['worker_reserved_seconds']+book['utility_charge_seconds']+20*len(FILES)<=3600
    for filename in FILES:
        assert not any(row.get('filename')==filename for row in book.get('local_source_intakes', []))
    # Reconcile the terminated job without changing/retrying its source or charge.
    for row in book.get('local_source_intakes', []):
        if row['filename']=='CHEMBL1140235.pdf' and row['status']=='RESERVED':
            receipt=json.loads((PRIVATE/'owner-v2-CHEMBL1140235-resource.json').read_text())
            assert receipt['status']=='FAIL_RESOURCE_LIMIT'
            row.update(status='FAILED_RESOURCE_LIMIT_NO_MASKED_OUTPUT',
                       failure_receipt='owner-v2-CHEMBL1140235-resource.json',
                       reattempt='NOT_RUN_AT_RECONCILIATION', scientific_result='NOT_EVALUABLE')
    save(PRIVATE/'ledger.json', book)
    guard=Guard('owner-batch-v1', wall=180, cpu_seconds=60)
    try:
        import fitz  # The large import is performed once inside the OS guard.
        from r0r_owner_methods_mask_v2 import safety_checks
        checks=safety_checks()
        save(PRIVATE/'owner-mask-checks-v2.json', checks)
        for module in ['r0r_owner_pdf_intake_v2.py','r0r_owner_methods_mask_v2.py']:
            raw=(ROOT/'tools'/module).read_bytes()
            (PRIVATE/'code'/(hashlib.sha256(raw).hexdigest()+'.py')).write_bytes(raw)
        for filename in FILES:
            run(filename, guard_factory=PhaseGuard)
        guard.finish('PASS', charged_to='Three 20-second file reservations; startup remains within the existing utility allocation',
                     file_phases=3, library_imported_once=True)
    except Exception as exc:
        guard.finish('FAIL', error_type=type(exc).__name__)
        raise


if __name__=='__main__':
    main()
