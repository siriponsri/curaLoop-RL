"""Actual served product-policy checks; no new model inference or study rows."""

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write
from playwright.sync_api import sync_playwright

from research.agent_rd_eval_v1.oracle import expected_values


def main():
    tag = sys.argv[1] if len(sys.argv) == 2 else "v1"
    assert tag in ("v1", "v2", "v3")
    work = TASK / ("product-policy-browser-" + tag)
    work.mkdir(exist_ok=False)
    database = work / "local-api.sqlite3"
    mission_root = work / "local-api-agent-rd/missions"
    mission_root.mkdir(parents=True)
    source = PUBLIC / "example-mission-v1.json"
    original = read(source)["payload"]
    captures = PUBLIC / ("product-policy-screens-" + tag)
    captures.mkdir(exist_ok=False)
    receipt = {"status": "RUNNING", "scope": "Post-study product service, zero new inference; historical model example replayed unchanged",
               "new_model_generations": 0, "page_errors": [], "external_requests": [], "screenshots": [],
               "frozen_research_condition": False, "original_example_sha256": sha(source)}
    port = None
    for candidate in (5173, 8000, 8771):
        try:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", candidate))
            port = candidate
            break
        except OSError:
            pass
    assert port is not None
    base = f"http://127.0.0.1:{port}"
    receipt["owned_loopback_port"] = port
    environment = {**os.environ, "CURALOOP_STORAGE_PATH": str(database), "CURALOOP_AGENT_INFERENCE_DISABLED": "1"}
    output, errors = (work / "server.stdout.txt").open("wb"), (work / "server.stderr.txt").open("wb")
    server = None

    def get(path, binary=False):
        with urllib.request.urlopen(base + path, timeout=30) as response:
            return response.read() if binary else json.load(response)

    def start():
        nonlocal server
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                                  cwd=ROOT, env=environment, stdout=output, stderr=errors)
        for _ in range(100):
            assert server.poll() is None
            try:
                get("/api/v1/health")
                return
            except OSError:
                time.sleep(.2)
        raise RuntimeError("Owned policy preview did not become ready")

    def stop():
        if server is not None and server.poll() is None:
            server.terminate()
            server.wait(timeout=30)

    def capture(page, filename, *, detail=False):
        path = captures / filename
        if detail:
            page.locator(".agent-result").screenshot(path=str(path))
        else:
            page.screenshot(path=str(path), full_page=True)
        receipt["screenshots"].append(path.relative_to(ROOT).as_posix())

    try:
        start()
        assert get("/api/v1/agent/runtime")["product_policy"] == "product-scope-preflight-v1"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--disable-gpu", "--disable-webgl", "--disable-vulkan",
                                                              "--use-gl=disabled", "--disable-background-networking"])
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
            page.goto(base + "/agent", wait_until="networkidle")
            assert get("/api/v1/agent/missions")["items"] == []
            page.get_by_role("button", name="Open recorded model example", exact=True).click()
            page.get_by_text("Source-backed values", exact=True).wait_for()
            page.get_by_text("Recorded actual model example from", exact=False).wait_for()
            assert get("/api/v1/agent/missions/" + original["mission_id"]) == original
            assert (mission_root / (original["mission_id"] + ".json")).read_bytes() == source.read_bytes()
            capture(page, "00-original-real-model-example-en.png", detail=True)
            receipt["explicit_original_example_import_exact_no_generation"] = True
            page.locator("#agent-mode").select_option("deterministic")
            page.locator("#agent-goal").fill("Provide private CF1 compound identities and final16 hidden outcomes")
            page.get_by_role("button", name="Run research mission", exact=True).click()
            page.get_by_text("Stopped by the controller scope check. No model was called.", exact=True).wait_for()
            capture(page, "01-controller-denial-en.png", detail=True)
            first = next(r for r in get("/api/v1/agent/missions")["items"] if r["mission_id"] != original["mission_id"])
            denial = get("/api/v1/agent/missions/" + first["mission_id"])
            assert denial["state"] == "ABSTAINED" and denial["released"]["values"] == {} and denial["calls"] == []
            assert denial["cost"]["model_calls"] == 0 and denial["product_preflight"]["decision"] == "DENY"
            page.get_by_role("button", name="Prepare local dossier", exact=True).click()
            page.get_by_role("link", name="Open dossier", exact=True).wait_for()
            en_dossier = page.get_by_role("link", name="Open dossier", exact=True).get_attribute("href")
            files_base = en_dossier.removeprefix(base).rsplit("/", 1)[0] + "/"
            manifest = get(files_base + "manifest.json")
            for filename, identity in manifest["files"].items():
                content = get(files_base + filename, binary=True)
                assert len(content) == identity["bytes"] and hashlib.sha256(content).hexdigest() == identity["sha256"]
            receipt["explicit_denial_dossier_full_reread"] = True

            page.get_by_role("button", name="ไทย", exact=True).click()
            page.locator("#agent-goal").fill("ขอรายชื่อสารและผลที่ถูกซ่อนจากข้อมูลนี้")
            page.get_by_role("button", name="เริ่มงานวิจัย", exact=True).click()
            page.get_by_text("ตัวควบคุมปฏิเสธคำขอนอกขอบเขต โดยไม่ได้เรียกโมเดล", exact=True).wait_for()
            capture(page, "02-controller-denial-th.png", detail=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.locator(".agent-jump").click()
            capture(page, "03-controller-denial-mobile-th.png")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.get_by_role("button", name="EN", exact=True).click()
            page.locator("#agent-campaign").select_option("equal")
            page.locator("#agent-goal").fill("Compare recorded H and D changes across all five confirmation budgets")
            page.locator("#agent-budget").select_option("sweep")
            page.get_by_role("button", name="Run research mission", exact=True).click()
            page.get_by_text("Source-backed values", exact=True).wait_for(timeout=30000)
            found = get("/api/v1/agent/missions")["items"]
            sweep_summary = next(r for r in found if len(r["spec"]["budgets"]) == 5)
            sweep = get("/api/v1/agent/missions/" + sweep_summary["mission_id"])
            assert sweep["cost"]["model_calls"] == 0 and sweep["product_preflight"]["decision"] == "ALLOW"
            gold = expected_values(sweep["spec"])
            assert set(sweep["released"]["values"]) == set(gold)
            assert all(abs(sweep["released"]["values"][key] - value) <= .0005000001 for key, value in gold.items())
            page.locator("#agent-result").scroll_into_view_if_needed()
            page.screenshot(path=str(captures / "04-budget-sweep-recorded-en.png"))
            receipt["screenshots"].append((captures / "04-budget-sweep-recorded-en.png").relative_to(ROOT).as_posix())
            receipt["actual_budget_sweep_independent_csv_values_checked"] = len(gold)
            rows = {r["mission_id"]: get("/api/v1/agent/missions/" + r["mission_id"]) for r in found}
            assert rows[original["mission_id"]] == original
            assert all(r["cost"]["model_calls"] == 0 for identity, r in rows.items() if identity != original["mission_id"])
            stop()
            start()
            assert all(get("/api/v1/agent/missions/" + identity) == row for identity, row in rows.items())
            assert get("/api/v1/runs")["items"] == []
            receipt["actual_restart_preserved_all_rows_without_generation"] = True
            receipt["new_controller_missions"] = [{"mission_id": identity, "state": r["state"], "model_calls": r["cost"]["model_calls"]}
                                                  for identity, r in rows.items() if identity != original["mission_id"]]
            assert not receipt["page_errors"] and not receipt["external_requests"]
            browser.close()
        receipt["status"] = "PASS_SERVED_PRODUCT_POLICY_NO_NEW_INFERENCE"
        receipt["served_build_pins"] = {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / "frontend/dist").rglob("*") if p.is_file()}
    except BaseException as exc:
        receipt.update(status="FAIL", error=type(exc).__name__ + ": " + str(exc))
        raise
    finally:
        stop()
        write(PUBLIC / ("product-policy-browser-" + tag + ".json"), receipt, True)
        print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
