"""Native pipe tests for complete frame, partial frame deadline and size bounds."""

import io
import os


def execute(root, output):
    from tools.lrbc_c_supervise_v2 import read_frame
    checks = []
    def pipe(payload, close_writer=False):
        read, write = os.pipe()
        os.set_blocking(read, False)
        os.write(write, payload)
        if close_writer: os.close(write)
        return read, None if close_writer else write
    read, write = pipe(b'{}\n{}\n')
    try:
        capture = io.BytesIO()
        line, pending = read_frame(read, capture, timeout=.1)
        assert line == b'{}'
        line, pending = read_frame(read, capture, pending, timeout=.1)
        assert line == b'{}' and pending == b'' and capture.getvalue() == b'{}\n{}\n'
        checks.append('COMPLETE_AND_BUFFERED_FRAME')
    finally:
        os.close(read); os.close(write)
    read, write = pipe(b'{"partial":')
    try:
        try: read_frame(read, io.BytesIO(), timeout=.03)
        except TimeoutError: checks.append('PARTIAL_FRAME_ABSOLUTE_DEADLINE')
        else: raise AssertionError('Partial frame escaped deadline')
    finally:
        os.close(read); os.close(write)
    read, write = pipe(b'0123456789')
    try:
        try: read_frame(read, io.BytesIO(), timeout=.1, maximum=8)
        except ValueError: checks.append('FRAME_SIZE_LIMIT')
        else: raise AssertionError('Oversized frame admitted')
    finally:
        os.close(read); os.close(write)
    read, write = pipe(b'{"partial":', close_writer=True)
    try:
        try: read_frame(read, io.BytesIO(), timeout=.1)
        except ValueError: checks.append('EOF_WITHOUT_NEWLINE_REJECTED')
        else: raise AssertionError('Partial EOF frame admitted')
    finally: os.close(read)
    return {'status': 'PASS', 'pipe_boundary_checks': checks, 'count': len(checks),
            'actual_native_pipes': True, 'child_processes_created': 0, 'scientific_source_calls': 0}
