"""Real served-build acceptance, all 70 study views and actual screenshots."""

import json
import os
import socket
import subprocess
import sys
import time
import traceback
import urllib.parse
import urllib.request

from cf2p_admin_v1 import PUBLIC, ROOT, TASK, sha, write
from playwright.sync_api import sync_playwright


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    assert tag in ("v1", "v2", "v3", "v4", "v5")
    captures = PUBLIC / f"screens-{tag}"
    captures.mkdir(exist_ok=False)
    receipt = {"status": "RUNNING", "scope": "Actual local FastAPI production build; developer acceptance, not a user study",
               "views": [], "page_errors": [], "external_requests": [], "screenshots": [], "final16_access": False,
               "new_molecular_fits": 0, "browser_gpu_flags": ["--disable-gpu", "--disable-webgl", "--disable-vulkan", "--use-gl=disabled"]}
    # Existing origin protection admits these two local ports. Inspect availability;
    # never stop an owner's listener or widen the API origin policy for this QA.
    port = None
    for candidate in (5173, 8000):
        try:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", candidate))
            port = candidate
            break
        except OSError:
            continue
    if port is None:
        raise RuntimeError("Both permitted local preview ports are occupied; no listener changed")
    receipt["owned_preview_port"] = port
    base = f"http://127.0.0.1:{port}"
    env = dict(os.environ)
    source_paths = [ROOT / "api/main.py", ROOT / "src/curaloop_rd/confirmation_study.py"] + [p for p in (ROOT / "frontend/dist").rglob("*") if p.is_file()]
    source_pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in source_paths}
    receipt["served_source_pins"] = source_pins
    stdout = (TASK / f"browser-server-{tag}.stdout.txt").open("wb")
    stderr = (TASK / f"browser-server-{tag}.stderr.txt").open("wb")
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                              cwd=ROOT, env=env, stdout=stdout, stderr=stderr)

    def get(path, data=None):
        request = urllib.request.Request(base + path, data=json.dumps(data).encode() if data is not None else None,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    try:
        for _ in range(100):
            if server.poll() is not None:
                raise RuntimeError("Owned API stopped before health readiness")
            try:
                get("/api/v1/health")
                break
            except OSError:
                time.sleep(.2)
        else:
            raise RuntimeError("Owned API did not become ready")
        assert get("/api/v1/runs")["items"] == []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=receipt["browser_gpu_flags"] + ["--disable-background-networking"])
            receipt["browser_version"] = browser.version
            context = browser.new_context(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce", accept_downloads=True)
            page = context.new_page()
            page.on("pageerror", lambda error: receipt["page_errors"].append(str(error)))
            mutations = []
            page.on("request", lambda request: mutations.append(request.url) if request.method not in ("GET", "HEAD") else None)

            def boundary(route):
                url = route.request.url
                if url.startswith(base + "/") or url.startswith(("file:", "data:", "blob:")):
                    route.continue_()
                else:
                    receipt["external_requests"].append(url)
                    route.abort()
            page.route("**/*", boundary)

            def settled(campaign, budget):
                page.locator(f'.cf-table-section[data-cf-campaign="{campaign}"][data-cf-budget="{budget}"]').wait_for(timeout=30000)
                assert page.locator(".cf-table-section tbody tr").count() == 18

            def select(campaign, budget):
                previous_budget = int(page.locator("#cf-budget").input_value())
                page.locator("#cf-campaign").select_option(campaign)
                settled(campaign, previous_budget)
                page.locator("#cf-budget").select_option(str(budget))
                settled(campaign, budget)

            def capture(name, locator=None, full=False):
                path = captures / name
                if locator:
                    locator.screenshot(path=str(path))
                else:
                    page.screenshot(path=str(path), full_page=full)
                receipt["screenshots"].append(path.relative_to(ROOT).as_posix())

            def chart_integrity(label):
                geometry = page.locator(".cf-tradeoff").evaluate('''svg => ({
                  min_text_px: Math.min(...[...svg.querySelectorAll('text')].map(n => parseFloat(getComputedStyle(n).fontSize) * svg.getBoundingClientRect().width / 560)),
                  labels_inside_viewbox: [...svg.querySelectorAll('text')].every(n => {const b=n.getBBox(); return b.x>=0 && b.y>=0 && b.x+b.width<=560 && b.y+b.height<=540;}),
                  out_of_bounds: [...svg.querySelectorAll('text')].map(n => {const b=n.getBBox(); return {text:n.textContent,x:b.x,y:b.y,width:b.width,height:b.height};}).filter(b=>b.x<0||b.y<0||b.x+b.width>560||b.y+b.height>540)
                })''')
                receipt.setdefault("chart_geometry", {})[label] = geometry
                assert geometry["min_text_px"] >= 12 and geometry["labels_inside_viewbox"], geometry

            page.goto(base + "/confirmation", wait_until="networkidle")
            settled("equal", 10)
            assert not mutations and get("/api/v1/runs")["items"] == []
            receipt["direct_study_did_not_create_campaign"] = True
            page.get_by_role("link", name="Scenario builder", exact=True).click()
            page.get_by_role("button", name="Create campaign", exact=True).wait_for()
            assert not mutations and get("/api/v1/runs")["items"] == []
            page.get_by_role("link", name="Confirmation evidence", exact=True).click()
            settled("equal", 10)
            receipt["explicit_scenario_builder_reachable_without_auto_creation"] = True
            capture("01-confirmation-desktop-en.png")
            capture("02-tradeoff-en.png", page.locator(".cf-chart-panel"))
            capture("03-selected-arm-en.png", page.locator(".cf-arm-detail"))
            capture("04-all-arms-en.png", page.locator(".cf-table-section"))
            chart_integrity("desktop-en")
            page.locator(".cf-chart-panel").evaluate("el => el.style.filter = 'grayscale(1)'")
            page.locator(".cf-chart-panel").screenshot(path=str(TASK / f"chart-grayscale-{tag}.png"))
            page.locator(".cf-chart-panel").evaluate("el => el.style.filter = ''")
            svg = page.locator(".cf-tradeoff").evaluate('''el => {
              const clone=el.cloneNode(true); clone.setAttribute('xmlns','http://www.w3.org/2000/svg'); clone.setAttribute('width','560'); clone.setAttribute('height','540');
              const source=el.querySelectorAll('text'), target=clone.querySelectorAll('text');
              source.forEach((n,i)=> { const s=getComputedStyle(n); target[i].setAttribute('style',`font-family:${s.fontFamily};font-size:${s.fontSize};fill:${s.fill}`); });
              return clone.outerHTML;
            }''')
            (PUBLIC / f"tradeoff-ui-default-{tag}.svg").write_text(svg, encoding="utf-8", newline="\n")
            campaigns = ["equal"] + [c["campaign"] for c in get("/api/v1/studies/cf1")["campaigns"]]
            for locale in ("en", "th"):
                page.get_by_role("button", name="EN" if locale == "en" else "ไทย", exact=True).click()
                for campaign in campaigns:
                    for budget in (1, 2, 5, 10, 20):
                        select(campaign, budget)
                        data = get("/api/v1/studies/cf1?" + urllib.parse.urlencode({"campaign": campaign, "budget_percent": budget}))
                        expected = page.evaluate('''arms => arms.map(a => {
                          const f = n => n.toLocaleString('en-US', {maximumFractionDigits: 2});
                          return ['confirmed_positives','positive_structure_groups','positive_fingerprint_groups'].map(m => `${f(a.metrics[m].mean)} [${f(a.metrics[m].min)}, ${f(a.metrics[m].max)}]`).concat([f(100*a.metrics.hits_per_confirmation.mean)+'%',f(100*a.metrics.groups_per_confirmation.mean)+'%']);
                        })''', data["arms"])
                        actual = page.locator(".cf-table-section tbody tr").evaluate_all("rows => rows.map(r => [...r.querySelectorAll('td')].map(c => c.innerText.replace(/\\s+/g,' ').trim()))")
                        assert actual == expected, (locale, campaign, budget)
                        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                        receipt["views"].append({"locale": locale, "campaign": campaign, "budget_percent": budget,
                                                 "arms": 18, "five_displayed_metrics_match_actual_api": True})
            select("equal", 10)
            capture("05-confirmation-desktop-th.png")
            page.set_viewport_size({"width": 390, "height": 844})
            capture("06-confirmation-mobile-th.png", full=True)
            page.evaluate("scrollTo(0, 0)")
            capture("06a-confirmation-mobile-th-viewport.png")
            capture("06b-tradeoff-mobile-th.png", page.locator(".cf-chart-panel"))
            chart_integrity("mobile-th")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            # Mobile navigation is a real dialog. Reopen without changing filters.
            page.locator(".mobile-menu").click()
            assert page.get_by_role("dialog").is_visible()
            page.keyboard.press("Escape")
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.get_by_role("button", name="EN", exact=True).click()
            # A keyboard-operated chart point must update the detail/export selection.
            point = page.locator(".cf-tradeoff [role=button]").nth(4)
            point.focus()
            page.keyboard.press("Enter")
            assert point.get_attribute("aria-pressed") == "true"
            link = page.locator(".cf-arm-detail a[download]")
            with page.expect_download() as pending:
                link.click()
            download = pending.value
            path = TASK / "actual-browser-comparison.json"
            download.save_as(path)
            exported = json.loads(path.read_text(encoding="utf-8"))
            assert exported["selection"] == {"campaign": "equal", "budget_percent": 10, "ranker": "rf", "operator": "cluster_round_robin"}
            receipt["actual_download_selection"] = exported["selection"]
            assert not mutations and get("/api/v1/runs")["items"] == []

            # Controlled UI fault; real input-tamper rejection is covered separately.
            pattern = "**/api/v1/studies/cf1?*"
            page.route(pattern, lambda route: route.fulfill(status=503, json={"detail": "Injected unavailable-source response"}))
            page.reload(wait_until="networkidle")
            page.get_by_role("heading", name="Confirmation evidence unavailable").wait_for()
            assert page.locator(".cf-table-section").count() == 0
            capture("07-unavailable-state-en.png")
            page.unroute(pattern)
            page.get_by_role("button", name="Retry study").click()
            settled("equal", 10)
            receipt["injected_http503_retry_no_fake_metrics"] = True
            # Existing synthetic pending run: inspect/filter/export must preserve it.
            config = {"dataset": "synthetic_linear_v1", "candidate_count": 24, "initial_count": 6, "budget_units": 6, "batch_size": 3, "delay_steps": 2, "seed": 42}
            run = get("/api/v1/runs", {"scenario": config, "policy": "greedy"})
            url = "/api/v1/runs/" + run["session_id"]
            run = get(url + "/select", {"expected_revision": run["revision"]})
            before = get(url)
            assert before["pending"]
            page.goto(base + "/", wait_until="networkidle")
            page.get_by_role("link", name="Open CF1 study").wait_for()
            capture("08-overview-cf1-entry-en.png")
            page.get_by_role("link", name="Open CF1 study").click()
            settled("equal", 10)
            select("628/677", 5)
            assert get(url) == before
            receipt["existing_synthetic_pending_run_unchanged"] = True
            # Source context and per-campaign exact B remain inspectable.
            page.locator(".cf-provenance summary").click()
            assert page.locator(".cf-hash").count() == 4
            receipt["source_hashes_and_exact_budgets_visible"] = True
            cproof = read_cproof()
            folder = TASK / cproof["export_relative_to_private_root"]
            for locale in ("en", "th"):
                page.goto((folder / f"brief-{locale}.html").as_uri(), wait_until="load")
                assert page.locator("tbody tr").count() == 18
                capture(f"09-c-workspace-{locale}.png")
            assert not receipt["page_errors"] and not receipt["external_requests"]
            receipt["reduced_motion"] = page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            receipt["no_page_overflow_at_checked_viewports"] = True
            receipt["status"] = "PASS_ACTUAL_PRODUCTION_BROWSER"
            context.close()
            browser.close()
        assert all(sha(ROOT / p) == h for p, h in source_pins.items())
    except BaseException:
        receipt["status"] = "FAIL"
        receipt["failure"] = traceback.format_exc()
        raise
    finally:
        server.terminate()
        try:
            server.wait(timeout=20)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=10)
        stdout.close()
        stderr.close()
        receipt["owned_server_stopped"] = server.poll() is not None
        write(PUBLIC / f"browser-check-{tag}.json", receipt, True)
    print(json.dumps({"status": receipt["status"], "views": len(receipt["views"]), "screenshots": len(receipt["screenshots"])}))


def read_cproof():
    current = PUBLIC / "native-c-workspace-v2.json"
    return json.loads((current if current.exists() else PUBLIC / "native-c-workspace-v1.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
