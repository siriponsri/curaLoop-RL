"""Served UI refinement QA using the preserved real mission, zero new inference."""

import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write
from playwright.sync_api import sync_playwright


def main():
    row = read(TASK / "browser-real-mission-v1.json")
    identity = row["mission_id"]
    database = Path(os.environ["CURALOOP_STORAGE_PATH"])
    root = database.parent / (database.stem + "-agent-rd")
    target = root / "missions" / (identity + ".json")
    target.parent.mkdir(parents=True, exist_ok=False)
    original = TASK / "jobs/actual-browser-model-acceptance-v1/disposable-api-agent-rd/missions" / (identity + ".json")
    shutil.copyfile(original, target)
    assert sha(original) == sha(target)
    captures = PUBLIC / "screens-v2"
    captures.mkdir(exist_ok=False)
    receipt = {"status": "RUNNING", "scope": "Author served-UI refinement check of the preserved actual v1 model mission; no new model inference",
               "real_model_mission_source_sha256": sha(original), "new_model_calls": 0, "page_errors": [], "external_requests": [], "screenshots": []}
    port = None
    for candidate in (5173, 8000):
        try:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", candidate))
            port = candidate
            break
        except OSError:
            pass
    assert port is not None
    base = f"http://127.0.0.1:{port}"
    receipt["owned_preview_port"] = port
    receipt["served_build_pins"] = {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / "frontend/dist").rglob("*") if p.is_file()}
    output = (TASK / "browser-review-v2.stdout.txt").open("wb")
    errors = (TASK / "browser-review-v2.stderr.txt").open("wb")
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                              cwd=ROOT, env={**os.environ, "CURALOOP_AGENT_INFERENCE_DISABLED": "1"}, stdout=output, stderr=errors)

    def get(path):
        with urllib.request.urlopen(base + path, timeout=30) as response:
            return json.load(response)

    try:
        for _ in range(100):
            assert server.poll() is None
            try:
                get("/api/v1/health")
                break
            except OSError:
                time.sleep(.2)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--disable-gpu", "--disable-webgl", "--disable-vulkan", "--use-gl=disabled", "--disable-background-networking"])
            context = browser.new_context(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
            page = context.new_page()
            page.on("pageerror", lambda error: receipt["page_errors"].append(str(error)))

            def boundary(route):
                if route.request.url.startswith(base + "/") or route.request.url.startswith(("data:", "blob:")):
                    route.continue_()
                else:
                    receipt["external_requests"].append(route.request.url)
                    route.abort()
            page.route("**/*", boundary)

            def capture(name, locator=None, full=False):
                path = captures / name
                (locator.screenshot(path=str(path)) if locator else page.screenshot(path=str(path), full_page=full))
                receipt["screenshots"].append(path.relative_to(ROOT).as_posix())

            page.goto(base + "/agent", wait_until="networkidle")
            page.locator(".agent-history-list button").first.wait_for()
            capture("01-agent-workspace-en.png")
            page.locator(".agent-history-list button").first.click()
            page.locator("#agent-result").wait_for()
            assert page.locator("#agent-campaign").input_value() == row["spec"]["campaign"]
            assert page.locator("#agent-goal").input_value() == row["spec"]["goal"]
            assert page.locator(".agent-timeline").get_attribute("open") is None
            page.evaluate("scrollTo(0, 0)")
            assert 0 <= page.locator("#agent-result").bounding_box()["y"] < 1100
            capture("02-agent-recorded-result-en.png", full=True)
            capture("03-agent-result-detail-en.png", page.locator(".agent-result"))
            page.locator(".agent-timeline summary").click()
            assert page.locator(".agent-timeline").get_attribute("open") is not None
            page.locator(".agent-timeline summary").click()
            page.get_by_role("button", name="Prepare local dossier", exact=True).click()
            page.get_by_role("link", name="Open dossier", exact=True).wait_for()
            page.get_by_role("button", name="ไทย", exact=True).click()
            capture("04-agent-recorded-result-th.png", full=True)
            page.locator(".agent-timeline summary").click()
            page.get_by_text("เรียกโมเดลจริงบน CPU ครั้งที่ 1", exact=True).wait_for()
            capture("05-agent-translated-trail-th.png", page.locator(".agent-timeline"))
            page.locator(".agent-timeline summary").click()
            page.set_viewport_size({"width": 390, "height": 844})
            page.locator(".agent-jump").click()
            capture("06-agent-mobile-result-th.png")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            receipt["result_jump_and_mobile_reflow"] = True
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.get_by_role("button", name="EN", exact=True).click()
            # The saved row and inference count stay byte-identical after browsing/export.
            assert get("/api/v1/agent/missions/" + identity) == row
            assert len(get("/api/v1/agent/missions")["items"]) == 1
            assert get("/api/v1/runs")["items"] == []
            assert not receipt["page_errors"] and not receipt["external_requests"]
            browser.close()
        receipt["status"] = "PASS_SERVED_UI_REFINEMENT_NO_NEW_INFERENCE"
    except BaseException as exc:
        receipt.update(status="FAIL", error=type(exc).__name__ + ": " + str(exc))
        raise
    finally:
        if server.poll() is None:
            server.terminate()
            server.wait(timeout=30)
        write(PUBLIC / "browser-refinement-v2.json", receipt, True)
        print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
