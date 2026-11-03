"""Cross-platform localhost launcher. Does not install software or kill other services."""

import argparse
import json
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args()
    if sys.version_info < (3, 11):
        raise SystemExit("Python 3.11+ is required.")
    if not (ROOT / "frontend/dist/index.html").exists():
        raise SystemExit("Built frontend missing. In frontend/: npm ci && npm run build")
    sys.path.insert(0, str(ROOT))
    import fastapi  # noqa: F401
    import uvicorn

    from curaloop.domain import Scenario
    from curaloop.service import RunService

    run = RunService(
        Scenario(
            dataset="hiv_moleculenet_replay_v1", candidate_count=24, initial_count=6, budget_units=0
        )
    )
    assert run.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
    if args.check:
        print("Preflight PASS: Python, FastAPI, engine, historical data and built frontend.")
        return
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", 8000))
        except OSError:
            try:
                with urlopen("http://127.0.0.1:8000/api/v1/health", timeout=2) as response:
                    same = json.load(response).get("service") == "curaloop-local"
            except Exception:
                same = False
            if same:
                print("CuraLoop-RL is already running at http://127.0.0.1:8000")
                if not args.no_browser:
                    webbrowser.open("http://127.0.0.1:8000")
                return
            raise SystemExit(
                "Port 8000 is used by another application. Close it yourself or choose a different port manually. No process was stopped."
            )
    if not args.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    print("CuraLoop-RL: http://127.0.0.1:8000 · loopback only · Ctrl+C to stop")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, workers=1)


if __name__ == "__main__":
    main()
