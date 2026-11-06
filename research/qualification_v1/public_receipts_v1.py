"""Public process receipts deliberately have no child-output/error-message input."""


def worker_failure(error):
    return {'status': 'FAIL', 'category': 'QUALIFICATION_PHASE_FAILED',
            'error_type': type(error).__name__}


def process_receipt(attempt, exit_code, resources):
    return {'status': 'PASS' if exit_code == 0 else 'FAIL', 'attempt': attempt,
            'exit_code': exit_code, 'resources': resources,
            'child_stdout_and_stderr': 'RETAINED_PRIVATELY_NOT_INCLUDED'}
