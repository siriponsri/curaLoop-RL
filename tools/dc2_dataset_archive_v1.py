"""Probe the publisher-linked SAB archive; do not infer or open scoring gold."""

import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from dc2_admin_v1 import PUBLIC, TASK, authority, sha, write


def main():
    authority()
    folder = TASK / "dataset-intake-v1"
    source = folder / "github-README.md"
    links = re.findall(r"\[benchmark artifacts\]\((https://[^)]+)\)", source.read_text(encoding="utf-8"))
    assert len(links) == 1 and urllib.parse.urlsplit(links[0]).hostname == "buckeyemailosu-my.sharepoint.com"
    url = links[0] + "&download=1"
    request = urllib.request.Request(url, headers={"User-Agent": "CuraLoop-LR-DC2-Research-Intake/1.0", "Range": "bytes=0-65535"})
    result = {"utc": datetime.now(timezone.utc).isoformat(), "source_readme_sha256": sha(source),
              "official_archive_url": links[0], "expected_name": "benchmark_verified.zip",
              "request": "Anonymous official public link with download=1, bounded range probe; no login or credentials",
              "model_calls": 0, "gpu_allocated_seconds": 0, "gold_content_opened": False}
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            info = {key: response.headers.get(key) for key in ("Content-Length", "Content-Range", "Content-Type", "Content-Disposition", "ETag")}
            final = urllib.parse.urlsplit(response.url)
            result.update(http_status=response.status, headers=info, final_host=final.hostname,
                          final_path=final.path, source_access="PUBLIC_ANONYMOUS")
            prefix = response.read(65536)
            (folder / "archive-prefix-v1.bin").write_bytes(prefix)
            result.update(prefix_bytes=len(prefix), prefix_sha256=sha(folder / "archive-prefix-v1.bin"))
            if prefix.startswith(b"PK\x03\x04"):
                result["status"] = "PASS_ARCHIVE_PREFIX_ONLY_NOT_FULL_DOWNLOAD"
                result["content_is_zip_prefix"] = True
            else:
                result["status"] = "BLOCKED_ARCHIVE_NOT_ZIP_RESPONSE"
                result["content_is_zip_prefix"] = False
    except urllib.error.HTTPError as exc:
        result.update(status="BLOCKED_OFFICIAL_ARCHIVE_ACCESS", http_status=exc.code,
                      error=str(exc), prefix_bytes=0, source_access="UNAVAILABLE_TO_ANONYMOUS_REQUEST")
    except (TimeoutError, OSError) as exc:
        result.update(status="BLOCKED_ARCHIVE_TRANSPORT", error=str(exc), prefix_bytes=0)
    result["full_archive_downloaded"] = False
    write(PUBLIC / "dataset-archive-probe-v1.json", result)
    print({k: result[k] for k in ("status", "full_archive_downloaded", "prefix_bytes")})


if __name__ == "__main__":
    main()
