"""Opt-in local Chromium E2E evidence from the actual running app, never a mockup.

Install: python -m pip install playwright; python -m playwright install chromium
Run: python scripts/browser_smoke.py
External browser HTTP requests are blocked during this test.
"""

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "docs/evidence/poc-v0.3/streamlit-browser"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    log = (out / "server.txt").open("w", encoding="utf-8")
    server = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py",
                               "--server.port", "8502", "--server.address", "127.0.0.1"],
                              cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            try:
                with urlopen("http://127.0.0.1:8502/_stcore/health", timeout=1) as response:
                    assert response.status == 200
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError("Streamlit health endpoint unavailable")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(viewport={"width": 1500, "height": 1050}, accept_downloads=True)
            external_requests = []
            def route(request_route):
                host = urlparse(request_route.request.url).hostname
                if host not in ("127.0.0.1", "localhost", None):
                    external_requests.append(request_route.request.url)
                    request_route.abort()
                else:
                    request_route.continue_()
            context.route("**/*", route)
            page = context.new_page()

            def capture(name):
                expect(page.get_by_test_id("stStatusWidget")).to_have_count(0, timeout=30000)
                expect(page.get_by_text("No API keys or paid services required", exact=False)).to_be_visible()
                if name.startswith(("01-", "03-", "04-")):
                    expect(page.get_by_test_id("stMetricValue")).to_have_count(4)
                    expect(page.get_by_test_id("stMetricValue").first).to_be_visible()
                page.evaluate("document.fonts.ready")
                page.evaluate("async()=>{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));"
                              "await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}")
                assert not re.search(r"[\u0e00-\u0e7f]", page.locator("body").inner_text())
                page.evaluate("()=>{window.scrollTo(0,0);document.querySelector('[data-testid=stMain]')?.scrollTo(0,0);}")
                page.screenshot(path=str(out / name), full_page=True)

            page.goto("http://127.0.0.1:8502")
            expect(page.get_by_role("heading", name="Overview", exact=True)).to_be_visible(timeout=30000)
            page.evaluate("document.fonts.ready")
            expect(page.get_by_text("HISTORICAL_PUBLIC_DATA", exact=True)).to_be_visible()
            capture("01-overview.png")
            page.get_by_text("Scenario Setup", exact=True).click()
            expect(page.get_by_role("button", name="Apply scenario")).to_be_visible()
            capture("02-scenario.png")
            # Use B=5 to keep this live-browser smoke test short; no prefilled result data.
            page.get_by_role("spinbutton", name="Budget units").fill("5")
            page.get_by_role("button", name="Apply scenario").click()
            expect(page.get_by_text("New run created. Open Screening Run to select the first batch.")).to_be_visible()
            page.get_by_text("Screening Run", exact=True).click()
            page.get_by_role("button", name="Select batch", exact=True).click()
            expect(page.get_by_role("button", name="Advance +1", exact=True)).to_be_enabled(timeout=45000)
            capture("03-pending.png")
            for _ in range(2):
                page.get_by_role("button", name="Advance +1", exact=True).click()
                # Await the completed Streamlit rerun before another action.
                expect(page.get_by_test_id("stStatusWidget")).to_have_count(0, timeout=30000)
            expect(page.get_by_text("Campaign complete: no pending feedback; budget or eligible candidates are exhausted.")).to_be_visible()
            capture("04-delivered.png")
            page.get_by_text("Compare & Export", exact=True).click()
            page.get_by_role("button", name="Compare policies", exact=True).click()
            expect(page.get_by_text("Comparison complete · matched initial conditions")).to_be_visible(timeout=90000)
            capture("05-comparison.png")
            with page.expect_download() as download:
                page.get_by_role("button", name="Download JSON / Full report", exact=True).first.click()
            download.value.save_as(str(out / "downloaded-report.json"))
            payload = json.loads((out / "downloaded-report.json").read_text(encoding="utf-8"))
            assert len(payload["runs"]) == 5
            assert all(r["metrics"]["spent_units"] == 5 for r in payload["runs"])
            with page.expect_download() as download:
                page.get_by_role("button", name="Download CSV / Event ledger", exact=True).first.click()
            download.value.save_as(str(out / "downloaded-report.csv"))
            rows = list(csv.DictReader(io.StringIO((out / "downloaded-report.csv").read_text(encoding="utf-8-sig"))))
            assert len(rows) == sum(len(r["events"]) for r in payload["runs"])
            page.set_viewport_size({"width": 390, "height": 844})
            capture("06-mobile.png")
            evidence = {"status": "PASS", "source": "Real local Streamlit + local test Chromium",
                        "pages": 4, "policies_compared": 5, "budget_units": 5,
                        "json_runs": len(payload["runs"]), "csv_events": len(rows),
                        "external_http_requests_blocked": external_requests,
                        "note": "External requests were blocked; localhost HTTP/WebSocket only. Screenshots were not generated by imagegen."}
            (out / "browser-smoke.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
            print(json.dumps(evidence, indent=2))
            browser.close()
    finally:
        if server.poll() is None:
            if os.name == "nt":
                # A Windows venv redirector can own a second Python process.
                # Stop only the exact process tree created by this harness.
                subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"],
                               check=True, capture_output=True)
            else:
                server.terminate()
            server.wait(timeout=15)
        log.close()


if __name__ == "__main__":
    main()
