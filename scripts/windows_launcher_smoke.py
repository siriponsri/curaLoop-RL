"""Exercise actual native CMD startup twice with isolated durable state."""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"


def request(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=20) as response:
        return json.load(response)


def main():
    if sys.platform != "win32":
        raise SystemExit("This check requires native Windows CMD.")
    try:
        request("/api/v1/health")
    except (OSError, URLError):
        pass
    else:
        raise SystemExit("Port 8000 is already in use. Stop your service before testing.")
    out = ROOT / "docs/evidence/poc-v0.3"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="curaloop-launcher-") as folder:
        env = dict(os.environ, CURALOOP_STORAGE_PATH=str(Path(folder) / "state.sqlite3"))
        snapshot = None
        records = []
        for index in range(2):
            with (out / f"windows-start-{index + 1}.txt").open("w", encoding="utf-8") as log:
                process = subprocess.Popen(
                    ["cmd.exe", "/d", "/c", str(ROOT / "Start-CuraLoop-Web.cmd"), "--no-browser"],
                    cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW,
                )
                try:
                    for _ in range(200):
                        if process.poll() is not None:
                            raise RuntimeError("Native launcher exited before serving the app.")
                        try:
                            health = request("/api/v1/health")
                            break
                        except OSError:
                            time.sleep(0.1)
                    else:
                        raise RuntimeError("Native launcher did not become ready.")
                    with urlopen(BASE + "/lab", timeout=10) as response:
                        assert b'<div id="root">' in response.read()
                    if snapshot is None:
                        snapshot = request("/api/v1/runs", {"scenario": {
                            "dataset": "synthetic_linear_v1", "candidate_count": 24,
                            "initial_count": 6, "budget_units": 6, "batch_size": 3,
                            "delay_steps": 2}, "policy": "random"})
                        snapshot = request(f"/api/v1/runs/{snapshot['session_id']}/select",
                                           {"expected_revision": snapshot["revision"]})
                        assert snapshot["report"]["metrics"]["pending_assays"] == 3
                    else:
                        recovered = request(f"/api/v1/runs/{snapshot['session_id']}")
                        assert recovered["revision"] == snapshot["revision"]
                        for key in ("events", "requests", "delivered_results", "metrics"):
                            assert recovered["report"][key] == snapshot["report"][key]
                    records.append({"start": index + 1, "health": health,
                                    "session_id": snapshot["session_id"],
                                    "pending_assays": 3, "served_spa": True})
                finally:
                    # Stop only the exact process tree created by this check.
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                   capture_output=True, check=False)
                    process.wait(timeout=15)
            time.sleep(0.5)
    (out / "windows-launchers.json").write_text(json.dumps({
        "status": "PASS", "native_cmd_starts": records,
        "recovery": "Pending ledger/revision retained exactly after abrupt process shutdown.",
        "first_run_setup": "Executed separately before baseline tests; see release report.",
    }, indent=2) + "\n", encoding="utf-8")
    print("PASS: native Windows CMD start, SPA serving and subsequent-start pending recovery.")


if __name__ == "__main__":
    main()
