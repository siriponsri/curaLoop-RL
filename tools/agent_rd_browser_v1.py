"""Actual localhost built UI -> API -> real model -> verified dossier acceptance."""

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, sha, write
from playwright.sync_api import sync_playwright

from research.agent_rd_eval_v1.oracle import expected_values
from research.agent_rd_eval_v1.scoring import score


def main():
    captures = PUBLIC / "screens-v1"
    captures.mkdir(exist_ok=False)
    receipt = {"status": "RUNNING", "scope": "Author localhost acceptance, not independent expert or user validation",
               "page_errors": [], "external_requests": [], "screenshots": [], "new_assay_or_final16_access": False}
    port = None
    for candidate in (5173, 8000):
        try:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", candidate))
            port = candidate
            break
        except OSError:
            pass
    assert port is not None, "No owned preview port; do not stop another listener"
    base = f"http://127.0.0.1:{port}"
    receipt["owned_preview_port"] = port
    source_paths = [ROOT / "api/main.py", ROOT / "api/agent_rd_routes.py", *sorted((ROOT / "src/curaloop_rd/agent_rd").glob("*.py")),
                    *[p for p in (ROOT / "frontend/dist").rglob("*") if p.is_file()]]
    receipt["served_source_pins"] = {p.relative_to(ROOT).as_posix(): sha(p) for p in source_paths}
    server = None

    def get(path, raw=False):
        with urllib.request.urlopen(base + path, timeout=30) as response:
            data = response.read()
        return data if raw else json.loads(data)

    def start_server():
        nonlocal server
        out = (TASK / ("browser-server-" + str(time.time_ns()) + ".stdout.txt")).open("wb")
        err = (TASK / ("browser-server-" + str(time.time_ns()) + ".stderr.txt")).open("wb")
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                                  cwd=ROOT, env=dict(os.environ), stdout=out, stderr=err)
        for _ in range(100):
            assert server.poll() is None, "Owned server stopped before readiness"
            try:
                get("/api/v1/health")
                return
            except OSError:
                time.sleep(.2)
        raise RuntimeError("Owned server readiness timeout")

    def stop_server():
        if server and server.poll() is None:
            server.terminate()
            server.wait(timeout=30)

    try:
        start_server()
        assert get("/api/v1/runs")["items"] == []
        assert get("/api/v1/agent/missions")["items"] == []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--disable-gpu", "--disable-webgl", "--disable-vulkan", "--use-gl=disabled", "--disable-background-networking"])
            receipt["browser_version"] = browser.version
            context = browser.new_context(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce", accept_downloads=True)
            page = context.new_page()
            page.on("pageerror", lambda error: receipt["page_errors"].append(str(error)))
            mutations = []
            page.on("request", lambda request: mutations.append({"url": request.url, "method": request.method}) if request.method not in ("GET", "HEAD") else None)

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
            page.get_by_text("No generated results are shown before execution.", exact=True).wait_for()
            assert not mutations
            receipt["page_open_starts_no_mission_or_simulator"] = True
            capture("01-agent-empty-en.png")
            page.get_by_role("button", name="ไทย", exact=True).click()
            page.get_by_label("โจทย์ที่ต้องการศึกษา", exact=True).wait_for()
            capture("02-agent-empty-th.png")
            page.get_by_role("button", name="EN", exact=True).click()
            page.locator("#agent-campaign").select_option("628/677")
            page.locator("#agent-goal").fill("Compare the first two arms. Report delta:b10:H and delta:b10:D, plus b10:a0:H and b10:a0:D. Include development_only and seed_range_not_ci.")
            page.get_by_role("button", name="Run research mission", exact=True).click()
            page.get_by_text("ACTUAL MISSION STATE", exact=True).wait_for()
            capture("03-agent-actual-running-en.png")
            started = time.monotonic()
            while time.monotonic() - started < 2400:
                items = get("/api/v1/agent/missions")["items"]
                if items:
                    identity = items[0]["mission_id"]
                    row = get("/api/v1/agent/missions/" + identity)
                    if row["state"] in ("COMPLETED", "ABSTAINED", "FAILED"):
                        break
                page.wait_for_timeout(2000)
            else:
                raise RuntimeError("Actual model mission did not finish within acceptance wall cap")
            write(TASK / "browser-real-mission-v1.json", row, True)
            receipt["actual_mission"] = {key: row[key] for key in ("mission_id", "state", "cost", "verification", "fallback", "error")}
            assert row["state"] in ("COMPLETED", "ABSTAINED") and row["released"] is not None, receipt["actual_mission"]
            assert row["cost"]["model_calls"] > 0 and row["cost"]["paid_cost_usd"] == 0
            card = {"expected_action": "answer", "acceptable_reasons": [], "required_keys": ["delta:b10:H", "delta:b10:D", "b10:a0:H", "b10:a0:D"],
                    "required_limits": ["development_only", "seed_range_not_ci"], "fault": None, "recovery": False}
            receipt["actual_task_score"] = score(card, {**card, "permitted_values": expected_values(row["spec"])}, row)
            receipt["integration_acceptance_does_not_imply_task_success"] = True
            page.locator(".agent-result").wait_for(timeout=15000)
            capture("04-agent-real-result-en.png", full=True)
            capture("05-agent-result-detail-en.png", page.locator(".agent-result"))
            page.get_by_role("button", name="Prepare local dossier", exact=True).click()
            dossier_link = page.get_by_role("link", name="Open dossier", exact=True)
            dossier_link.wait_for()
            dossier_path = dossier_link.get_attribute("href")
            prefix = dossier_path.rsplit("/", 1)[0] + "/"
            manifest = get(prefix + "manifest.json")
            assert len(manifest["files"]) == 4
            for name, expected in manifest["files"].items():
                content = get(prefix + name, raw=True)
                assert len(content) == expected["bytes"] and hashlib.sha256(content).hexdigest() == expected["sha256"]
            receipt["dossier_files_reread_match_manifest"] = True
            with context.expect_page() as opened:
                dossier_link.click()
            report = opened.value
            report.wait_for_load_state("networkidle")
            assert report.get_by_role("heading", name="Pharmaceutical evidence dossier", exact=True).is_visible()
            report.screenshot(path=str(captures / "06-agent-dossier-en.png"), full_page=True)
            receipt["screenshots"].append((captures / "06-agent-dossier-en.png").relative_to(ROOT).as_posix())
            report.close()
            page.get_by_role("button", name="ไทย", exact=True).click()
            capture("07-agent-real-result-th.png", full=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.evaluate("scrollTo(0, 0)")
            capture("08-agent-mobile-th.png", full=True)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            receipt["mobile_no_document_overflow"] = True
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.get_by_role("button", name="EN", exact=True).click()
            stop_server()
            start_server()
            recovered = get("/api/v1/agent/missions/" + identity)
            assert recovered == row, "Completed mission changed or reran after actual API restart"
            page.reload(wait_until="networkidle")
            page.locator(".agent-history-list button").first.click()
            page.locator(".agent-result").wait_for()
            receipt["actual_server_restart_preserves_result_without_new_model_call"] = True
            page.goto(base + "/confirmation", wait_until="networkidle")
            page.locator(".cf-table-section tbody tr").first.wait_for()
            assert page.locator(".cf-table-section tbody tr").count() == 18
            assert get("/api/v1/runs")["items"] == []
            receipt["existing_confirmation_and_simulator_store_unchanged"] = True
            receipt["mutations"] = mutations
            assert not receipt["page_errors"] and not receipt["external_requests"]
            browser.close()
        receipt["status"] = "PASS_ACTUAL_LOCALHOST_REAL_MODEL_ACCEPTANCE"
    except BaseException as exc:
        receipt["status"] = "FAIL"
        receipt["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        stop_server()
        write(PUBLIC / "browser-acceptance-v1.json", receipt, True)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
