"""Actual React/FastAPI production-mode localhost E2E, screenshots and accessibility evidence.

Uses Python Playwright (local anonymous browser), not a generated UI or external site.
python scripts/web_browser_smoke.py --output docs/evidence/poc-v0.3/browser
"""

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    expect.set_options(timeout=30000)
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "docs/evidence/poc-v0.3/browser")
    parser.add_argument("--manual", action="store_true", help="Capture additional loaded views for the English operator manual.")
    parser.add_argument("--port", type=int, choices=(8000, 5173), default=8000,
                        help="Use an approved loopback origin; 5173 avoids an owner's running production service.")
    args = parser.parse_args()
    base_url = f"http://127.0.0.1:{args.port}"
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    manual = out / "manual"
    if args.manual:
        manual.mkdir(exist_ok=True)
    log = (out / "server.txt").open("w")
    state = tempfile.TemporaryDirectory(prefix="curaloop-browser-")
    env = dict(os.environ, CURALOOP_STORAGE_PATH=str(Path(state.name) / "state.sqlite3"))

    def start_server():
        command = ([sys.executable, "scripts/start_web.py", "--no-browser"] if args.port == 8000 else
                   [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(args.port)])
        process = subprocess.Popen(
            command,
            cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
        )
        for _ in range(200):
            if process.poll() is not None:
                raise RuntimeError("Owned API process exited before becoming ready")
            try:
                with urlopen(base_url + "/api/v1/health", timeout=1) as response:
                    if response.status == 200:
                        return process
            except OSError:
                time.sleep(0.1)
        raise RuntimeError("API failed to start")

    try:
        with urlopen(base_url + "/api/v1/health", timeout=1):
            raise RuntimeError(f"Port {args.port} is already occupied; use another approved test port.")
    except OSError:
        pass
    server = start_server()

    def stop_server():
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"],
                           capture_output=True, check=False)
        else:
            server.terminate()
        server.wait(timeout=15)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(
                viewport={"width": 1440, "height": 1000},
                accept_downloads=True,
                base_url=base_url,
                reduced_motion="reduce",
            )
            external = []
            errors = []
            captures = []
            overflows = []
            a11y = {}
            context.route(
                "**/*",
                lambda route: (
                    route.continue_()
                    if urlparse(route.request.url).hostname in ("127.0.0.1", "localhost", None)
                    else (external.append(route.request.url), route.abort())
                ),
            )
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))

            def manual_detail(name, selector):
                if args.manual:
                    page.locator(selector).screenshot(path=str(manual / (name + ".png")))

            def capture(name):
                expect(page.locator(".initial-loading")).to_have_count(0)
                headings = {
                    "/": "Every assay is a decision.",
                    "/scenario": "Scenario builder",
                    "/lab": "Simulation lab",
                    "/compounds": "Compound explorer",
                    "/benchmarks": "Benchmark arena",
                    "/evidence": "Research evidence",
                    "/presentation": "Guided presentation",
                }
                if name != "18-mobile-navigation":
                    expect(
                        page.locator(".main-content h1").filter(
                            has_text=headings[urlparse(page.url).path]
                        )
                    ).to_be_visible(timeout=40000)
                if urlparse(page.url).path == "/" and page.viewport_size["width"] >= 1100:
                    expect(page.locator(".specimen-image")).to_be_visible(timeout=30000)
                if urlparse(page.url).path == "/compounds":
                    expect(page.locator(".compound-item").first).to_be_visible(timeout=30000)
                expect(page.locator(".chart-loading")).to_have_count(0, timeout=30000)
                page.evaluate("document.fonts.ready")
                page.evaluate(
                    "async()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager');await Promise.all([...document.images].map(i=>i.decode()));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}"
                )
                page.evaluate("window.scrollTo(0,0)")
                overflow = page.evaluate("document.documentElement.scrollWidth > innerWidth")
                if overflow:
                    overflows.append(name)
                page.screenshot(path=str(out / (name + ".png")), full_page=True)
                captures.append(name)
                if args.manual:
                    height = min(page.viewport_size["height"], 820)
                    page.screenshot(path=str(manual / (name + ".png")),
                                    clip={"x": 0, "y": 0, "width": page.viewport_size["width"], "height": height})

            def audit(name):
                script = ROOT / "frontend/node_modules/axe-core/axe.min.js"
                if script.exists():
                    page.add_script_tag(path=str(script))
                    result = page.evaluate(
                        "async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})"
                    )
                    a11y[name] = [
                        {
                            "id": v["id"],
                            "impact": v["impact"],
                            "description": v["description"],
                            "node_count": len(v["nodes"]),
                            "nodes": [
                                {"target": n["target"], "summary": n.get("failureSummary", "")}
                                for n in v["nodes"]
                            ],
                        }
                        for v in result["violations"]
                    ]

            context.add_init_script("localStorage.setItem('curaloop-language','th')")
            page.goto("/")
            expect(page.locator("html")).to_have_attribute("lang", "en")
            expect(page.get_by_role("button", name="TH", exact=True)).to_have_count(0)
            expect(
                page.get_by_role(
                    "heading", name="Every assay is a decision. Make yours reproducible."
                )
            ).to_be_visible(timeout=40000)
            page.evaluate("document.fonts.ready")
            assert page.evaluate("document.fonts.check('14px CuraThai')")
            capture("01-overview")
            audit("overview")
            page.get_by_role("link", name="Scenario builder", exact=True).click()
            expect(page.get_by_role("heading", name="Scenario builder")).to_be_visible()
            page.get_by_label("Screening budget", exact=True).fill("5")
            capture("02-scenario")
            audit("scenario")
            page.get_by_role("button", name="Create campaign", exact=True).click()
            expect(page.get_by_role("heading", name="Simulation lab")).to_be_visible(timeout=30000)
            capture("03-simulation-before")
            page.get_by_role("button", name="Select batch", exact=True).click()
            expect(page.get_by_role("button", name="Advance time", exact=True)).to_be_enabled(
                timeout=45000
            )
            session_id = page.evaluate("localStorage.getItem('curaloop-session')")
            current = context.request.get("/api/v1/runs/" + session_id).json()
            assert current["report"]["metrics"]["pending_assays"] == 5
            assert (
                current["report"]["metrics"]["confirmed_hits"] == 0
                and not current["report"]["delivered_results"]
            )
            capture("04-simulation-pending")
            manual_detail("04-pending-ledger", ".lab-board")
            audit("lab")
            # A real process restart must retain revision, pending privacy and budget.
            before_restart = current
            stop_server()
            time.sleep(0.4)
            server = start_server()
            page.reload()
            expect(page.get_by_role("heading", name="Simulation lab")).to_be_visible(timeout=40000)
            recovered = context.request.get("/api/v1/runs/" + session_id).json()
            assert recovered["revision"] == before_restart["revision"]
            for key in ("events", "requests", "delivered_results", "metrics"):
                assert recovered["report"][key] == before_restart["report"][key]
            stale = context.request.post("/api/v1/runs/" + session_id + "/select",
                                         data={"expected_revision": 0})
            assert stale.status == 409
            capture("04b-recovered-pending")
            page.get_by_role("button", name="Advance time", exact=True).click()
            expect(page.locator(".lab-context .small-mono")).to_contain_text("step 1")
            page.get_by_role("button", name="Advance time", exact=True).click()
            expect(page.get_by_text("Completed", exact=True)).to_be_visible()
            capture("05-simulation-delivered")
            manual_detail("05-delivered-ledger", ".lab-board")
            manual_detail("05-decisions", ".decisions-section")
            current = context.request.get("/api/v1/runs/" + session_id).json()
            assert (
                current["report"]["metrics"]["delivered_assays"] == 5
                and current["report"]["metrics"]["spent_units"] == 5
            )
            page.get_by_role("button", name="Reconcile replay", exact=True).click()
            expect(page.get_by_text("Public event replay reconciled successfully.")).to_be_visible()
            page.get_by_role("link", name="Compound explorer", exact=True).click()
            expect(page.locator(".compound-item").first).to_be_visible(timeout=30000)
            page.get_by_role("combobox", name="Compound status").select_option("eligible")
            expect(page.locator(".compound-item").first).to_be_visible()
            assert (
                context.request.get(
                    "/api/v1/runs/" + session_id + "/candidates?status=eligible"
                ).json()["items"][0]["revealed_active"]
                is None
            )
            if page.locator(".compound-item img").count():
                expect(page.locator(".compound-item img").first).to_be_visible()
                page.wait_for_function(
                    "document.querySelector('.compound-item img').naturalWidth>0"
                )
            capture("06-compound-explorer")
            audit("compounds")
            page.get_by_role("button", name="Next compound page").click()
            expect(page.locator(".pagination")).to_contain_text("Page 2")
            inspect_button = page.get_by_role("button", name=re.compile("^Inspect ")).first
            inspect_button.click()
            expect(page.get_by_role("dialog")).to_be_visible()
            expect(page.get_by_role("dialog")).to_contain_text("Unrevealed")
            capture("06b-compound-dialog")
            page.keyboard.press("Escape")
            expect(inspect_button).to_be_focused()
            page.get_by_role("link", name="Benchmark arena", exact=True).click()
            page.get_by_role("checkbox", name=re.compile("Q-learning")).check()
            page.get_by_role("checkbox", name=re.compile("Contextual bandit")).check()
            page.get_by_role("button", name="Run comparison", exact=True).click()
            expect(page.get_by_role("heading", name="Comparison complete")).to_be_visible(
                timeout=120000
            )
            # Completed comparison remains available after route reload and server restart.
            page.reload()
            expect(page.get_by_role("heading", name="Comparison complete")).to_be_visible(timeout=40000)
            capture("07-benchmark")
            manual_detail("07-comparison-results", ".benchmark-result")
            audit("benchmarks")
            with page.expect_download() as download:
                page.get_by_role("link", name="JSON", exact=True).first.click()
            download.value.save_as(str(out / "comparison-download.json"))
            payload = json.loads((out / "comparison-download.json").read_text())
            assert len(payload["runs"]) == 5 and all(
                r["metrics"]["spent_units"] == 5 for r in payload["runs"]
            )
            assert len({tuple(r["manifest"]["initial_label_ids"]) for r in payload["runs"]}) == 1
            with page.expect_download() as download:
                page.get_by_role("link", name="CSV", exact=True).first.click()
            download.value.save_as(str(out / "comparison-download.csv"))
            csv_rows = list(
                csv.DictReader(
                    io.StringIO((out / "comparison-download.csv").read_text(encoding="utf-8-sig"))
                )
            )
            assert len(csv_rows) == sum(len(r["events"]) for r in payload["runs"])
            page.get_by_role("link", name="Research evidence", exact=True).click()
            expect(page.get_by_role("heading", name="Research evidence")).to_be_visible()
            expect(page.get_by_text(re.compile("300 / 300 requests")).first).to_be_visible()
            capture("08-evidence")
            audit("evidence")
            with page.expect_download() as download:
                page.get_by_role("link", name="JSON", exact=True).first.click()
            download.value.save_as(str(out / "run-download.json"))
            manual_detail("08-export-resume", ".resume-section")
            # Invalid import must leave the selected saved campaign intact.
            page.get_by_label("Resume JSON file").set_input_files({
                "name": "invalid-run.json", "mimeType": "application/json",
                "buffer": b'{"runs":[null]}',
            })
            page.get_by_role("button", name="Validate & resume").click()
            expect(page.get_by_role("alert").first).to_be_visible()
            assert page.evaluate("localStorage.getItem('curaloop-session')") == session_id
            page.get_by_label("Resume JSON file").set_input_files(str(out / "run-download.json"))
            page.get_by_role("button", name="Validate & resume").click()
            expect(
                page.get_by_text("Snapshot reconciled. Your campaign is ready in Simulation lab.")
            ).to_be_visible(timeout=30000)
            assert not re.search(r"[\u0E00-\u0E7F]", page.locator("body").inner_text())
            expect(page.locator("html")).to_have_attribute("lang", "en")
            capture("09-english-evidence-legacy-preference")
            audit("english-evidence")
            saved_row = page.get_by_role("row").filter(has_text=session_id[:12])
            saved_row.get_by_role("button", name="Open campaign", exact=True).click()
            page.wait_for_function("id=>localStorage.getItem('curaloop-session')===id", arg=session_id)
            capture("09b-saved-campaign-reopened")
            manual_detail("09-saved-campaigns", ".saved-runs")
            saved_row.get_by_role("button", name="Inspect saved revisions", exact=True).click()
            expect(page.get_by_role("heading", name="Recover a validated revision")).to_be_visible()
            manual_detail("09-revision-recovery", ".saved-runs")
            page.get_by_role("button", name="Recover selected revision", exact=True).click()
            page.wait_for_function("id=>localStorage.getItem('curaloop-session')!==id", arg=session_id)
            restored_id = page.evaluate("localStorage.getItem('curaloop-session')")
            revision_run = context.request.get("/api/v1/runs/" + restored_id).json()
            assert revision_run["report"]["events"] == current["report"]["events"]
            capture("09c-validated-revision-recovered")
            page.get_by_role("link", name="Guided presentation", exact=True).click()
            expect(page.get_by_role("heading", name="Guided presentation")).to_be_visible()
            page.get_by_role("button", name="Next chapter").click()
            expect(page.get_by_role("heading", name="What is real?")).to_be_visible()
            capture("10-presentation")
            audit("presentation")
            for chapter in ("Select, then wait", "Adapt with evidence", "Compare honestly"):
                page.get_by_role("button", name="Next chapter").click()
                expect(page.get_by_role("heading", name=chapter, exact=True)).to_be_visible()
            expect(page.get_by_role("button", name="Next chapter")).to_be_disabled()
            page.get_by_role("button", name="Back", exact=True).click()
            expect(page.get_by_role("heading", name="Adapt with evidence", exact=True)).to_be_visible()
            page.set_viewport_size({"width": 390, "height": 844})
            for path, name in [
                ("/", "11-mobile-overview"),
                ("/scenario", "12-mobile-scenario"),
                ("/lab", "13-mobile-lab"),
                ("/benchmarks", "14-mobile-benchmark"),
                ("/compounds", "15-mobile-compounds"),
                ("/evidence", "16-mobile-evidence"),
                ("/presentation", "17-mobile-presentation"),
            ]:
                page.goto(path)
                expect(page.locator(".initial-loading")).to_have_count(0, timeout=40000)
                capture(name)
                audit(name)
                if path == "/compounds":
                    page.get_by_role("button", name=re.compile("^Inspect ")).first.click()
                    capture("15b-mobile-compound-dialog")
                    page.keyboard.press("Escape")
                if path == "/lab":
                    region = page.get_by_role("region", name="Experiment decision table")
                    region.focus()
                    expect(region).to_be_focused()
                    page.keyboard.press("ArrowRight")
                    page.wait_for_function("document.querySelector('.table-scroll').scrollLeft>0")
                    page.screenshot(path=str(out / "13b-mobile-keyboard-table.png"), full_page=True)
                    captures.append("13b-mobile-keyboard-table")
                    events_region = page.get_by_role("region", name="Event timeline")
                    events_region.focus()
                    page.keyboard.press("ArrowDown")
                    page.wait_for_function("document.querySelector('.event-list').scrollTop>0")
            page.get_by_role("button", name="Open navigation").click()
            expect(page.get_by_role("dialog")).to_be_visible()
            capture("18-mobile-navigation")
            page.get_by_role("dialog").get_by_role(
                "link", name="Research evidence", exact=True
            ).click()
            expect(page.get_by_role("heading", name="Research evidence")).to_be_visible()
            assert not re.search(r"[\u0E00-\u0E7F]", page.locator("body").inner_text())
            capture("19-mobile-english-evidence")
            audit("mobile-english-evidence")
            # Verify exact observed active/inactive/missing rendering from real API runs.
            statuses = {}
            for label, missing in [("observed", 0), ("missing", 100)]:
                cfg = {
                    "dataset": "synthetic_linear_v1",
                    "seed": 42,
                    "candidate_count": 24,
                    "initial_count": 6,
                    "budget_units": 18,
                    "batch_size": 3,
                    "delay_steps": 2,
                    "assay_cost_units": 1,
                    "delay_jitter": 0,
                    "missing_percent": missing,
                }
                created = context.request.post(
                    "/api/v1/runs", data={"scenario": cfg, "policy": "random"}
                ).json()
                sid = created["session_id"]
                page.evaluate("sid=>localStorage.setItem('curaloop-session',sid)", sid)
                page.goto("/lab")
                expect(page.get_by_role("heading", name="Simulation lab")).to_be_visible(
                    timeout=40000
                )
                page.get_by_role("button", name="Select batch", exact=True).click()
                expect(page.get_by_role("button", name="Advance time", exact=True)).to_be_enabled(
                    timeout=40000
                )
                expect(page.locator(".table-scroll")).to_contain_text("Pending")
                if label == "observed":
                    capture("20-mobile-lab-pending")
                page.get_by_role("button", name="Finish campaign", exact=True).click()
                expect(page.get_by_text("Completed", exact=True)).to_be_visible(timeout=60000)
                live = context.request.get("/api/v1/runs/" + sid).json()
                metrics = live["report"]["metrics"]
                if label == "observed":
                    assert metrics["confirmed_hits"] > 0
                    expect(page.locator(".table-scroll")).to_contain_text("Observed active")
                    expect(page.locator(".table-scroll")).to_contain_text("Observed inactive")
                else:
                    assert metrics["missing_assays"] == 18 and metrics["confirmed_hits"] == 0
                    expect(page.locator(".table-scroll")).to_contain_text("Missing outcome")
                statuses[label] = metrics
                capture("21-mobile-lab-" + label)
                audit("mobile-lab-" + label)
                expect(page.get_by_text("Synthetic fixture", exact=True)).to_be_visible()
                if label == "observed":
                    page.goto("/presentation")
                    expect(page.get_by_role("heading", name="Guided presentation")).to_be_visible(timeout=40000)
                    page.get_by_role("button", name="Next chapter").click()
                    expect(page.get_by_text("This campaign uses synthetic descriptors", exact=False)).to_be_visible()
                    capture("22-mobile-synthetic-presentation")
                    page.goto("/")
                    expect(page.get_by_text("Synthetic labels and operations.", exact=False)).to_be_visible(timeout=40000)
                    capture("23-mobile-synthetic-overview")
                    page.goto("/benchmarks")
                    expect(page.get_by_role("heading", name="Benchmark arena")).to_be_visible(timeout=40000)
                    expect(page.get_by_text("Synthetic fixture", exact=True)).to_be_visible()
                    capture("24-mobile-synthetic-benchmarks")

            # Reset invokes the actual engine and keeps prior revision history.
            page.get_by_role("button", name="Reset campaign", exact=True).click()
            expect(page.get_by_role("button", name="Select batch", exact=True)).to_be_enabled(timeout=30000)
            reset = context.request.get("/api/v1/runs/" + sid).json()
            assert reset["report"]["metrics"]["spent_units"] == 0
            assert not reset["report"]["requests"] and not reset["pending"]
            mobile_overflow = page.evaluate("document.documentElement.scrollWidth > innerWidth")
            assert not mobile_overflow
            result = {
                "status": "PASS",
                "source": "Actual built Vite assets served by FastAPI at " + base_url,
                "platform": sys.platform,
                "browser_version": browser.version,
                "pending_restart_recovery": True,
                "legacy_thai_preference_english": True,
                "desktop": [1440, 1000],
                "mobile": [390, 844],
                "screenshots": captures,
                "horizontal_overflow": overflows,
                "browser_errors": errors,
                "blocked_external_requests": external,
                "json_comparison_runs": len(payload["runs"]),
                "csv_event_rows": len(csv_rows),
                "observed_status_checks": statuses,
                "frontend_build_sha256": context.request.get("/api/v1/meta").json()[
                    "frontend_build_sha256"
                ],
                "axe_route_count": len(a11y),
                "axe_violation_count": sum(len(v) for v in a11y.values()),
                "workflow": "create -> select -> delayed reveal -> replay -> explore -> compare 5 policies -> download JSON/CSV -> resume -> English legacy locale -> presentation -> mobile",
            }
            (out / "accessibility.json").write_text(json.dumps(a11y, indent=2), encoding="utf-8")
            (out / "browser-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps(result, indent=2))
            assert not overflows, overflows
            assert not errors, errors
            assert not external, external
            assert all(not v for v in a11y.values()), a11y
            browser.close()
    finally:
        stop_server()
        log.close()
        state.cleanup()


if __name__ == "__main__":
    main()
