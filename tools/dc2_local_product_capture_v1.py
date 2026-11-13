"""Inspect persisted actual model jobs after service restart, with inference disabled."""
import json
from playwright.sync_api import sync_playwright
from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, read, write
from dc2_local_product_service_v1 import service

def main():
    results = read(PUBLIC / "product-model-acceptance-v1.json")
    cases = [c for c in results["cases"] if c["result"]["state"] == "COMPLETED"]
    assert cases, "No successful actual model job exists; do not fabricate a screenshot"
    target = cases[0]["result"]["job_id"]
    output = PUBLIC / "model-product-screens-v1"
    output.mkdir(exist_ok=False)
    report = {"status": "RUNNING", "new_inference": False, "page_errors": [], "views": []}
    try:
        with service(TASK / "product-model-v1", reopen=True) as (url, request), sync_playwright() as pw:
            before = request("/api/v1/local-workflow/jobs")["items"]
            assert not request("/api/v1/local-workflow/runtime")["model_session_authorized"]
            browser = pw.chromium.launch(headless=True, args=["--disable-gpu", "--disable-background-networking"])
            page = browser.new_page(viewport={"width":1600,"height":1100}, reduced_motion="reduce")
            page.on("pageerror", lambda e: report["page_errors"].append(str(e)))
            page.goto(url + "/workflow", wait_until="networkidle")
            page.locator(".workflow-history button").filter(has_text=target[:8]).click()
            page.get_by_role("heading", name="Computed compounds", exact=True).wait_for()
            page.wait_for_function("() => {const i=document.querySelector('.workflow-molecule img');return i && i.complete && i.naturalWidth>0;}")
            page.screenshot(path=str(output / "actual-model-result-en.png"), full_page=True)
            for selector, name in ((".workflow-compose", "request-en.png"), (".workflow-compounds", "compounds-en.png"), (".workflow-status", "status-en.png")):
                page.locator(selector).screenshot(path=str(output / name))
            page.locator(".workflow-detail").last.locator("summary").click()
            page.locator(".workflow-detail").last.screenshot(path=str(output / "trace-en.png"))
            page.get_by_role("button", name="ไทย", exact=True).click()
            page.get_by_role("heading", name="สารที่คำนวณแล้ว", exact=True).wait_for()
            page.screenshot(path=str(output / "actual-model-result-th.png"), full_page=True)
            page.set_viewport_size({"width":390,"height":844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1")
            page.screenshot(path=str(output / "actual-model-mobile-th.png"), full_page=True)
            after = request("/api/v1/local-workflow/jobs")["items"]
            assert {r["job_id"]:r["revision"] for r in before} == {r["job_id"]:r["revision"] for r in after}
            report.update(status="PASS_ACTUAL_MODEL_SAVED_REOPEN_NO_NEW_INFERENCE", job_id=target, saved_jobs=len(after), same_revisions=True, model_session_authorized=False, screenshots=[p.relative_to(ROOT).as_posix() for p in output.glob("*.png")])
            assert not report["page_errors"]
            browser.close()
    except BaseException as error:
        report.update(status="FAIL_CAPTURE_RETAINED", error=str(error)[:1500])
        raise
    finally:
        write(PUBLIC / "model-product-browser-v1.json", report)
    print(json.dumps(report))

if __name__ == "__main__":
    main()
