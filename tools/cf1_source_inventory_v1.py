"""Pin author code/metadata only; no dataset or results CSV payload intake."""
# ruff: noqa: E402

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, now, start


def fetch(url, name, maximum=4 * 1024**2):
    request = urllib.request.Request(url, headers={"User-Agent": "CuraLoop-Research-Source-Audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            data = response.read(maximum + 1)
            assert len(data) <= maximum
            receipt = {"url": url, "utc": now().isoformat(), "status": response.status,
                       "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    except urllib.error.HTTPError as error:
        new(TASK / "source-http" / (name + ".json"), {"url": url, "utc": now().isoformat(), "status": error.code})
        raise
    path = TASK / "source" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as file:
        file.write(data)
    new(TASK / "source-http" / (name.replace("/", "_") + ".json"), receipt)
    return data


def main():
    commit = json.loads(fetch("https://api.github.com/repos/dahvida/AIC_Finder/commits/main", "commit.json"))["sha"]
    tree = json.loads(fetch("https://api.github.com/repos/dahvida/AIC_Finder/git/trees/" + commit + "?recursive=1", "tree.json"))
    assert not tree["truncated"]
    blobs = [r for r in tree["tree"] if r["type"] == "blob"]
    paths = [r["path"] for r in blobs if r["path"] in ("README.md", "LICENSE", "environment.yml")
             or (r["path"].startswith("Scripts/") and r["path"].endswith(".py"))]
    assert len(paths) < 80
    for name in paths:
        data = fetch("https://raw.githubusercontent.com/dahvida/AIC_Finder/" + commit + "/" + name,
                     "code/" + name, maximum=512 * 1024)
        print("SOURCE", name, "bytes", len(data))
    datasets = [r for r in blobs if r["path"].startswith("Datasets/")]
    summary = {"status": "PASS_PINNED_SOURCE_INVENTORY", "commit": commit,
               "code_paths": paths, "dataset_metadata": datasets,
               "dataset_payload_downloaded": False, "confirmation_values_analyzed": False,
               "final16_access": False}
    new(TASK / "source-inventory.json", summary)
    new(PUBLIC / "source-inventory-v1.json", summary)
    print(json.dumps({"commit": commit, "dataset_metadata": datasets}, indent=2))


if __name__ == "__main__":
    guard = start("author-source-inventory", 180, 600)
    try:
        main()
        finish("author-source-inventory", guard, "PASS")
    except BaseException:
        finish("author-source-inventory", guard, "FAIL")
        raise
