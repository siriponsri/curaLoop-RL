"""Actual served deterministic workflow and bilingual/mobile browser acceptance."""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write
from dc2_local_product_service_v1 import service


def main():
    version = sys.argv[1] if len(sys.argv) == 2 else "v1"
    assert version in ("v1", "v2", "v3", "v4", "v5")
    captures = PUBLIC / ("product-screens-" + version)
    captures.mkdir(exist_ok=False)
    report = {"status": "RUNNING", "scope": "Author engineering acceptance, actual deterministic RDKit subprocess, zero model calls", "page_errors": [], "external_requests": [], "views": []}
    try:
        with service(TASK / ("product-browser-" + version)) as (url, request), sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--disable-gpu", "--disable-webgl", "--disable-vulkan", "--disable-background-networking"])
            context = browser.new_context(viewport={"width": 1600, "height": 1100}, reduced_motion="reduce")
            page = context.new_page()
            page.on("pageerror", lambda e: report["page_errors"].append(str(e)))
            def boundary(route):
                if route.request.url.startswith((url + "/", "data:", "blob:")):
                    route.continue_()
                else:
                    report["external_requests"].append(route.request.url)
                    route.abort()
            context.route("**/*", boundary)
            page.goto(url + "/workflow", wait_until="networkidle")
            page.get_by_role("heading", name="Your analysis starts here.").wait_for()
            assert request("/api/v1/local-workflow/jobs")["items"] == []
            page.screenshot(path=str(captures / "01-empty-en.png"), full_page=True)
            page.locator("#molecular_weight_max").fill("100")
            page.get_by_role("button", name="Run analysis", exact=True).click()
            page.get_by_role("heading", name="Computed compounds", exact=True).wait_for(timeout=60000)
            row = request("/api/v1/local-workflow/jobs")["items"][0]
            detail = request("/api/v1/local-workflow/jobs/" + row["job_id"])
            assert detail["result"]["counts"] == {"input_rows": 7, "valid": 5, "selected": 2, "rejected": 2}
            assert not detail["provider_calls"]
            assert {c["compound_id"] for c in detail["data"]["compounds"] if c["selected"]} == {"ethanol", "benzene"}
            page.get_by_role("button", name="ethanol", exact=True).click()
            page.get_by_alt_text("2D structure of ethanol", exact=True).wait_for()
            page.wait_for_function("() => { const img = document.querySelector('.workflow-molecule img'); return img && img.complete && img.naturalWidth > 0; }", timeout=15000)
            page.screenshot(path=str(captures / "02-result-en.png"), full_page=True)
            page.locator("#workflow-search").fill("benzene")
            assert page.locator(".workflow-compounds tbody tr").count() == 1
            page.locator("#workflow-search").fill("")
            with page.expect_download() as downloading:
                page.get_by_role("link", name="Download bundle", exact=True).click()
            downloaded = TASK / ("product-browser-" + version) / "downloaded.zip"
            downloading.value.save_as(str(downloaded))
            assert sha(downloaded) == detail["result"]["bundle_sha256"]
            page.get_by_role("button", name="ไทย", exact=True).click()
            page.get_by_role("heading", name="สารที่คำนวณแล้ว", exact=True).wait_for()
            page.screenshot(path=str(captures / "03-result-th.png"), full_page=True)
            for locale in ("th", "en"):
                page.set_viewport_size({"width": 390, "height": 844})
                if locale == "en":
                    page.get_by_role("button", name="EN", exact=True).click()
                page.screenshot(path=str(captures / f"04-mobile-{locale}.png"), full_page=True)
                report["overflow_elements"] = page.evaluate("() => [...document.querySelectorAll('main *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1).slice(0,15).map(e => ({tag:e.tagName,cls:e.className,right:e.getBoundingClientRect().right}))")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "Whole page horizontal overflow"
                report["views"].append({"locale": locale, "width": 390, "page_overflow": False})
            page.set_viewport_size({"width": 1600, "height": 1100})
            page.reload(wait_until="networkidle")
            page.locator(".workflow-history button").first.click()
            page.get_by_role("heading", name="Computed compounds", exact=True).wait_for()
            assert len(request("/api/v1/local-workflow/jobs")["items"]) == 1
            # Constraint validation is a UI check, not a synthesized model response.
            page.locator("#molecular_weight_max").fill("0")
            assert not page.locator("#molecular_weight_max").evaluate("e => e.checkValidity()")
            report.update(status="PASS_ACTUAL_SERVED_WORKFLOW_EN_TH", result=detail, download_sha256=sha(downloaded), saved_reopen_without_rerun=True, rendered_structure=True, screenshots=[p.relative_to(ROOT).as_posix() for p in captures.glob("*.png")])
            assert not report["page_errors"] and not report["external_requests"]
            browser.close()
    except BaseException as error:
        report.update(status="FAIL_ACTUAL_BROWSER_ATTEMPT", error=type(error).__name__ + ": " + str(error)[:1600])
        raise
    finally:
        write(PUBLIC / ("product-browser-" + version + ".json"), report)
    print(json.dumps({"status": report["status"], "screenshots": len(report["screenshots"]), "counts": report["result"]["result"]["counts"]}))

if __name__ == "__main__":
    main()
