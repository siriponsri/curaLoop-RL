"""One controlled local-processing repair within the owner's existing R0-R.

No network call or new source. The original failed receipt/reservation remains.
Library setup uses the existing utility allocation; file CPU stays at 20s.
"""
import hashlib
import json
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT
from r0r_owner_batch_v1 import PhaseGuard
from r0r_owner_pdf_intake_v2 import run


def main():
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='ACTIVE'
    assert book['worker_reserved_seconds']+book['utility_charge_seconds']+20<=3600
    failed=[row for row in book['local_source_intakes'] if row['filename']=='CHEMBL1140235.pdf']
    assert len(failed)==1 and failed[0]['status']=='FAILED_RESOURCE_LIMIT_NO_MASKED_OUTPUT'
    assert 'output_path' not in failed[0]
    guard=Guard('owner-local-processing-repair-v1', wall=120, cpu_seconds=60)
    try:
        import fitz
        for name in ['r0r_owner_batch_v1.py','r0r_owner_pdf_intake_v2.py']:
            data=(ROOT/'tools'/name).read_bytes()
            (PRIVATE/'code'/(hashlib.sha256(data).hexdigest()+'.py')).write_bytes(data)
        PhaseGuard.enclosing_receipt='owner-local-processing-repair-v1-resource.json'
        factory=lambda name,wall,cpu_seconds: PhaseGuard(name.replace('owner-v2-','owner-local-repair-'),wall,cpu_seconds)
        run('CHEMBL1140235.pdf', guard_factory=factory, local_resource_repair=True)
        guard.finish('PASS', charged_to='20-second file reservation plus existing utility startup allocation',
                     failed_reservation_retained=True, network_requests=0)
    except Exception as exc:
        guard.finish('FAIL', error_type=type(exc).__name__)
        raise


if __name__=='__main__':
    main()
