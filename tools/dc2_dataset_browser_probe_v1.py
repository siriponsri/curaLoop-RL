"""One fresh anonymous browser access check; no user session or inference."""

import json

from dc2_admin_v1 import PUBLIC, TASK, authority, read, sha, write


def main():
    from playwright.sync_api import sync_playwright

    authority()
    original = read(PUBLIC / "dataset-archive-probe-v1.json")
    url = original["official_archive_url"] + "&download=1"
    downloads = []
    errors = []
    outcome = {}
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=False)
        page = context.new_page()

        def download_seen(download):
            downloads.append({"suggested_filename": download.suggested_filename,
                              "download_url": download.url})
            download.cancel()

        page.on("download", download_seen)
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(1500)
            outcome.update(http_status=response.status if response else None, title=page.title())
            content = page.content().encode("utf-8")
            if len(content) <= 1024 ** 2:
                target = TASK / "dataset-intake-v1/archive-browser-response-v1.html"
                target.write_bytes(content)
                outcome.update(response_bytes=len(content), response_sha256=sha(target))
        except Exception as exc:
            errors.append(str(exc)[:1200])
        context.close()
        browser.close()
    # Potential expiring anonymous download URLs stay in private operational
    # records. No signed URL, browser cookies or user session is published.
    write(TASK / "dataset-intake-v1/archive-browser-downloads-v1.json", downloads)
    result = {"status": "PUBLIC_BROWSER_DOWNLOAD_LINK_OBSERVED" if downloads else "BLOCKED_OFFICIAL_ARCHIVE_BROWSER_ACCESS",
              "anonymous_new_browser": True, "user_authenticated_browser_used": False,
              "attempts": 1, "full_archive_downloaded": False,
              "download_filenames": [d["suggested_filename"] for d in downloads],
              "private_download_url_record": "Stored only in the private intake folder",
              "errors": errors, "model_calls": 0, "gpu_allocated_seconds": 0, **outcome}
    write(PUBLIC / "dataset-archive-browser-probe-v1.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
