"""Own a separate loopback preview; never stop an existing service or borrow storage."""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager

from dc2_local_admin_v1 import ROOT


@contextmanager
def service(folder, *, session=None, reopen=False):
    folder.mkdir(exist_ok=reopen)
    port = 18083
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", port))
    url = f"http://127.0.0.1:{port}"
    env = {**os.environ, "CURALOOP_STORAGE_PATH": str(folder / "local-api.sqlite3"), "CURALOOP_AGENT_INFERENCE_DISABLED": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
    env.pop("CURALOOP_LOCAL_WORKFLOW_SESSION", None)
    if session:
        env["CURALOOP_LOCAL_WORKFLOW_SESSION"] = str(session)

    def request(path, body=None, *, binary=False):
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        call = urllib.request.Request(url + path, data, {"Content-Type": "application/json"})
        with urllib.request.urlopen(call, timeout=40) as response:
            return response.read() if binary else json.load(response)

    tag = "reopened-" if reopen else ""
    out, err = (folder / (tag + "server.stdout.txt")).open("xb"), (folder / (tag + "server.stderr.txt")).open("xb")
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)], cwd=ROOT, env=env, stdout=out, stderr=err)
    try:
        for _ in range(150):
            if process.poll() is not None:
                raise RuntimeError("Owned preview stopped: " + (folder / "server.stderr.txt").read_text(errors="replace")[-1000:])
            try:
                request("/api/v1/local-workflow/runtime")
                break
            except OSError:
                time.sleep(.2)
        else:
            raise TimeoutError("Owned preview did not become ready")
        yield url, request
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        out.close()
        err.close()


def await_job(request, identity, *, seconds=600):
    began = time.monotonic()
    while time.monotonic() - began < seconds:
        row = request("/api/v1/local-workflow/jobs/" + identity)
        if row["state"] in ("COMPLETED", "FAILED", "CANCELLED", "ABSTAINED", "INTERRUPTED"):
            return row
        time.sleep(.25)
    raise TimeoutError("Product case exceeded bounded observation window")
