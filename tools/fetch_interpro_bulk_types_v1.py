"""Bounded official InterPro FTP listings/types; never assay outcomes."""

import argparse
import hashlib
import http.client
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"
BASE = "https://ftp.ebi.ac.uk/pub/databases/interpro/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--relative", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--transport", choices=("urllib", "curl"), default="urllib")
    args = parser.parse_args()
    if args.relative.startswith("/") or ".." in args.relative or "?" in args.relative:
        raise ValueError("Only public relative FTP resources allowed.")
    if not args.name.replace("-", "").isalnum():
        raise ValueError("Invalid immutable cache name.")
    folder = RAW / ("interpro-ftp-" + args.name)
    folder.mkdir(exist_ok=False)
    url = BASE + args.relative
    started, cpu = time.perf_counter(), time.process_time()
    data, headers, error, status = b"", {}, None, None
    try:
        if args.transport == "curl":
            result = subprocess.run(
                [
                    "curl.exe",
                    "--fail",
                    "--max-time",
                    "45",
                    "--retry",
                    "0",
                    "--max-filesize",
                    "10000000",
                    "--proto",
                    "=https",
                    "--silent",
                    "--show-error",
                    "--output",
                    str(folder / "body"),
                    "--dump-header",
                    str(folder / "headers.txt"),
                    "--write-out",
                    "%{http_code}",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=50,
            )
            status = int(result.stdout) if result.stdout.isdigit() else None
            data = (folder / "body").read_bytes() if (folder / "body").exists() else b""
            error = None if result.returncode == 0 else "curl_exit_" + str(result.returncode)
            (folder / "curl-stderr.txt").write_text(result.stderr, encoding="utf-8")
        else:
            req = urllib.request.Request(
                url, headers={"User-Agent": "CuraLoop-RL-PlanA-family-audit/1"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                if not response.url.startswith(BASE):
                    raise ValueError("Unexpected redirect origin.")
                status, headers = response.status, dict(response.headers)
                data = response.read(10_000_001)
    except urllib.error.HTTPError as exc:
        status, data, error = exc.code, exc.read(64000), type(exc).__name__
    except (urllib.error.URLError, TimeoutError, http.client.HTTPException, ConnectionError) as exc:
        error = type(exc).__name__
    finally:
        (folder / "body").write_bytes(data)
        report = {
            "url": url,
            "status": status,
            "error": error,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "headers": headers,
            "source_sha256_at_start": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "wall_seconds": time.perf_counter() - started,
            "cpu_seconds": time.process_time() - cpu,
            "assay_outcomes_requested": False,
        }
        (folder / "receipt.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "headers"}, indent=2))
    if status != 200 or error is not None or len(data) > 10_000_000:
        raise RuntimeError("Unavailable/oversize official bulk resource; no bypass/retry.")
    if "text/html" in headers.get("Content-Type", ""):
        import re

        print("LINKS", json.dumps(re.findall(r'href="([^"]+)"', data.decode("utf-8")), indent=2))


if __name__ == "__main__":
    main()
