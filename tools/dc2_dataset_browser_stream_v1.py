"""Stream one official anonymous archive with a size gate and no gold access."""

import asyncio
import base64
import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone

from dc2_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write


async def main():
    from playwright.async_api import async_playwright

    release, ledger = authority()
    url = read(PUBLIC / "dataset-archive-probe-v1.json")["official_archive_url"] + "&download=1"
    folder = ROOT / "research/raw_data/external-benchmarks/scienceagentbench-verified-20260430"
    assert folder.resolve().is_relative_to((ROOT / "research/raw_data").resolve())
    folder.mkdir(parents=True, exist_ok=True)
    target, partial = folder / "benchmark_verified.zip", folder / "benchmark_verified.zip.part"
    assert not target.exists() and not partial.exists()
    available = min(release["benchmark_download_cap_bytes"], release["total_new_download_cap_bytes"]) - ledger["downloads_bytes"]
    result = {"status": "NOT_STARTED", "utc": datetime.now(timezone.utc).isoformat(),
              "model_calls": 0, "gpu_allocated_seconds": 0, "reference_solutions_opened": False,
              "archive_extracted": False, "anonymous_fresh_browser": True, "bytes_received": 0,
              "benchmark_remaining_download_cap_bytes": available}
    done = asyncio.Event()
    received = 0
    private_members = []
    async with async_playwright() as runtime:
        browser = await runtime.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=False)
        page = await context.new_page()
        session = await context.new_cdp_session(page)

        async def intercept(event):
            nonlocal received, private_members
            identity = event["requestId"]
            headers = {h["name"].lower(): h["value"] for h in event.get("responseHeaders", [])}
            disposition = headers.get("content-disposition", "")
            is_archive = "benchmark_verified.zip" in disposition.lower() or "application/zip" in headers.get("content-type", "").lower()
            if not is_archive:
                await session.send("Fetch.continueRequest", {"requestId": identity})
                return
            handle = None
            try:
                size = int(headers.get("content-length", "0"))
                result.update(http_status=event.get("responseStatusCode"), content_type=headers.get("content-type"),
                              declared_content_length=size, content_disposition=disposition)
                if not 0 < size <= available:
                    result["status"] = "BLOCKED_ARCHIVE_SIZE_UNKNOWN_OR_EXCEEDS_APPROVED_CAP"
                    return
                if event.get("responseStatusCode") != 200:
                    result["status"] = "BLOCKED_ARCHIVE_NON_FULL_RESPONSE"
                    return
                handle = (await session.send("Fetch.takeResponseBodyAsStream", {"requestId": identity}))["stream"]
                digest = hashlib.sha256()
                with partial.open("xb") as output:
                    while True:
                        block = await session.send("IO.read", {"handle": handle, "size": min(1048576, size - received or 1)})
                        data = base64.b64decode(block["data"]) if block.get("base64Encoded") else block["data"].encode("utf-8")
                        assert received + len(data) <= size <= available
                        output.write(data)
                        digest.update(data)
                        received += len(data)
                        if block.get("eof"):
                            break
                    output.flush()
                    os.fsync(output.fileno())
                assert received == size, (received, size)
                identity_sha = digest.hexdigest()
                assert sha(partial) == identity_sha
                with zipfile.ZipFile(partial) as archive:
                    members = archive.infolist()
                    expanded = sum(item.file_size for item in members)
                    assert expanded <= 12 * 1024 ** 3
                    assert all(not item.filename.startswith(("/", "\\")) and ".." not in item.filename.replace("\\", "/").split("/")
                               for item in members)
                    private_members = [{"name": item.filename, "bytes": item.file_size,
                                        "compressed_bytes": item.compress_size, "crc32": item.CRC,
                                        "encrypted": bool(item.flag_bits & 1)} for item in members]
                    result.update(member_count=len(members), declared_expanded_bytes=expanded,
                                  encrypted_member_count=sum(bool(item.flag_bits & 1) for item in members))
                os.rename(partial, target)
                result.update(status="PASS_OFFICIAL_ARCHIVE_DOWNLOADED_HASH_REREAD_AND_DIRECTORY_CHECKED",
                              sha256=identity_sha, relative_path=target.relative_to(ROOT).as_posix(),
                              full_archive_downloaded=True, crc_full_decompression="NOT_RUN_BEFORE_OWNER_RESUME")
            except Exception as exc:
                result.update(status="FAIL_BOUNDED_ARCHIVE_TRANSFER_OR_STRUCTURE_CHECK", error=str(exc)[:1500])
            finally:
                if handle:
                    await session.send("IO.close", {"handle": handle})
                await session.send("Fetch.failRequest", {"requestId": identity, "errorReason": "Aborted"})
                done.set()

        session.on("Fetch.requestPaused", intercept)
        await session.send("Fetch.enable", {"patterns": [{"urlPattern": "*", "requestStage": "Response"}]})
        navigation = asyncio.create_task(page.goto(url, wait_until="domcontentloaded", timeout=1500000))
        try:
            await asyncio.wait_for(done.wait(), timeout=1500)
        except TimeoutError:
            result.update(status="BLOCKED_BROWSER_ARCHIVE_STREAM_TIMEOUT")
        finally:
            await context.close()
            await browser.close()
            await asyncio.gather(navigation, return_exceptions=True)
    result["bytes_received"] = received
    if received:
        ledger = read(TASK / "ledger.json")
        ledger["downloads_bytes"] += received
        assert ledger["downloads_bytes"] <= release["total_new_download_cap_bytes"]
        save(ledger)
    if private_members:
        write(TASK / "dataset-intake-v1/archive-directory-v1.json", private_members)
    write(PUBLIC / "dataset-archive-intake-v1.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
