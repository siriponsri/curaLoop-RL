"""Opt-in local Chromium E2E evidence from the actual running app, never a mockup.

Install: python -m pip install playwright; python -m playwright install chromium
Run: python scripts/browser_smoke.py
External browser HTTP requests are blocked during this test.
"""

import csv
import io
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/evidence/ui"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = (OUT / "server.txt").open("w", encoding="utf-8")
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
            page.goto("http://127.0.0.1:8502")
            expect(page.get_by_role("heading", name="Overview", exact=True)).to_be_visible(timeout=30000)
            page.evaluate("document.fonts.ready")
            expect(page.get_by_text("HISTORICAL_PUBLIC_DATA", exact=True)).to_be_visible()
            page.screenshot(path=str(OUT / "01-overview.png"), full_page=True)
            page.get_by_text("Scenario Setup · ตั้งเงื่อนไข", exact=True).click()
            expect(page.get_by_role("button", name="เริ่มการจำลอง / Apply scenario")).to_be_visible()
            page.screenshot(path=str(OUT / "02-scenario.png"), full_page=True)
            # Use B=5 to keep this live-browser smoke test short; no prefilled result data.
            page.get_by_role("spinbutton", name="งบทดสอบจำลอง / Budget units").fill("5")
            page.get_by_role("button", name="เริ่มการจำลอง / Apply scenario").click()
            expect(page.get_by_text("สร้าง run ใหม่แล้ว ไปที่ Screening Run เพื่อส่ง batch แรก")).to_be_visible()
            page.get_by_text("Screening Run · จำลองการคัดเลือก", exact=True).click()
            page.get_by_role("button", name="เลือก batch ถัดไป / Select", exact=True).click()
            expect(page.get_by_role("button", name="เลื่อนเวลา +1 / Advance", exact=True)).to_be_enabled(timeout=45000)
            page.screenshot(path=str(OUT / "03-pending.png"), full_page=True)
            for _ in range(2):
                page.get_by_role("button", name="เลื่อนเวลา +1 / Advance", exact=True).click()
                # Await the completed Streamlit rerun before another action.
                expect(page.get_by_test_id("stStatusWidget")).to_have_count(0, timeout=30000)
            expect(page.get_by_text("การจำลองครบแล้ว: ไม่มีผลค้าง และงบหรือ candidate ที่เลือกได้หมดแล้ว")).to_be_visible()
            page.screenshot(path=str(OUT / "04-delivered.png"), full_page=True)
            page.get_by_text("Compare & Export · เปรียบเทียบและส่งออก", exact=True).click()
            page.get_by_role("button", name="เปรียบเทียบนโยบาย / Compare policies", exact=True).click()
            expect(page.get_by_text("Comparison complete · matched initial conditions")).to_be_visible(timeout=90000)
            page.screenshot(path=str(OUT / "05-comparison.png"), full_page=True)
            with page.expect_download() as download:
                page.get_by_role("button", name="ดาวน์โหลด JSON / Full report", exact=True).first.click()
            download.value.save_as(str(OUT / "downloaded-report.json"))
            payload = json.loads((OUT / "downloaded-report.json").read_text())
            assert len(payload["runs"]) == 5
            assert all(r["metrics"]["spent_units"] == 5 for r in payload["runs"])
            with page.expect_download() as download:
                page.get_by_role("button", name="ดาวน์โหลด CSV / Event report", exact=True).first.click()
            download.value.save_as(str(OUT / "downloaded-report.csv"))
            rows = list(csv.DictReader(io.StringIO((OUT / "downloaded-report.csv").read_text(encoding="utf-8-sig"))))
            assert len(rows) == sum(len(r["events"]) for r in payload["runs"])
            page.set_viewport_size({"width": 390, "height": 844})
            page.screenshot(path=str(OUT / "06-mobile.png"), full_page=True)
            evidence = {"status": "PASS", "source": "Real local Streamlit + local test Chromium",
                        "pages": 4, "policies_compared": 5, "budget_units": 5,
                        "json_runs": len(payload["runs"]), "csv_events": len(rows),
                        "external_http_requests_blocked": external_requests,
                        "note": "External requests were blocked; localhost HTTP/WebSocket only. Screenshots were not generated by imagegen."}
            (OUT / "browser-smoke.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
            print(json.dumps(evidence, indent=2))
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=15)
        log.close()


if __name__ == "__main__":
    main()
