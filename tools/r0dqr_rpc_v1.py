"""Strict existing-profile transport; caller supplies the fresh utility guard."""
import base64,json,shlex,subprocess
from r0dqr_core_v1 import HOST,SSH_OPTIONS

def ssh(code,timeout=40):
    payload=base64.b64encode(code.encode()).decode()
    command='python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(payload)+'))')
    result=subprocess.run(['ssh',*SSH_OPTIONS,HOST,command],capture_output=True,timeout=timeout)
    if result.returncode:raise RuntimeError('Remote control error: '+result.stderr.decode(errors='replace')[:1000])
    return json.loads(result.stdout)
