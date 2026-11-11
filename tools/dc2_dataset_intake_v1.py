"""Bounded metadata-only intake of the official verified SAB release."""

import hashlib
import json
import urllib.request
from collections import Counter

from dc2_admin_v1 import PUBLIC, TASK, authority, read, save, sha, write

FOLDER = TASK / "dataset-intake-v1"


def fetch(url, name, limit):
    target = FOLDER / name
    assert not target.exists()
    request = urllib.request.Request(url, headers={"User-Agent": "CuraLoop-LR-DC2-Research-Intake/1.0"})
    digest = hashlib.sha256()
    count = 0
    with urllib.request.urlopen(request, timeout=45) as response, target.open("xb") as output:
        declared = response.headers.get("Content-Length")
        if declared:
            assert int(declared) <= limit, (name, declared, limit)
        while block := response.read(65536):
            count += len(block)
            assert count <= limit, (name, count)
            digest.update(block)
            output.write(block)
        receipt = {"requested_url": url, "bytes": count, "sha256": digest.hexdigest(),
                   "etag": response.headers.get("ETag"), "content_type": response.headers.get("Content-Type")}
    assert sha(target) == receipt["sha256"]
    ledger = read(TASK / "ledger.json")
    ledger["downloads_bytes"] += count
    assert ledger["downloads_bytes"] <= read(TASK / "release.json")["total_new_download_cap_bytes"]
    save(ledger)
    return receipt


def main():
    import pyarrow.parquet as pq

    authority()
    FOLDER.mkdir(exist_ok=False)
    captures = {}
    captures["hf-repo-metadata.json"] = fetch("https://huggingface.co/api/datasets/osunlp/ScienceAgentBench",
                                             "hf-repo-metadata.json", 2 * 1024 ** 2)
    hf = json.loads((FOLDER / "hf-repo-metadata.json").read_text())
    revision = hf["sha"]
    prefix = f"https://huggingface.co/datasets/osunlp/ScienceAgentBench/resolve/{revision}/"
    captures["hf-README.md"] = fetch(prefix + "README.md", "hf-README.md", 128 * 1024)
    captures["verified.parquet"] = fetch(prefix + "data/verified-00000-of-00001.parquet", "verified.parquet", 4 * 1024 ** 2)
    captures["github-README.md"] = fetch("https://raw.githubusercontent.com/OSU-NLP-Group/ScienceAgentBench/main/README.md",
                                       "github-README.md", 256 * 1024)
    # Never read dataset previews, molecular rows, reference solutions or labels.
    columns = ["instance_id", "domain", "github_name", "subtask_categories", "eval_script_name", "output_fname"]
    rows = pq.read_table(FOLDER / "verified.parquet", columns=columns).to_pylist()
    assert len(rows) == 102 and len({row["instance_id"] for row in rows}) == 102
    write(FOLDER / "structural-task-catalog.json", rows)
    domains = Counter(row["domain"] for row in rows)
    repositories = Counter(row["github_name"] for row in rows)
    receipt = {"status": "PASS_OFFICIAL_VERIFIED_ANNOTATION_SNAPSHOT_NOT_FULL_BENCHMARK",
        "hf_revision": revision, "split": "verified", "rows": len(rows), "domain_counts": dict(domains),
        "repository_counts": dict(repositories), "captures": captures,
        "structural_columns_read": columns, "reference_solutions_read": False, "activity_labels_read": False,
        "full_archive_downloaded": False, "full_dataset_admitted": False, "new_model_calls": 0,
        "owner_steering": "Finish permitted dataset download/verification, then pause for explicit owner resume"}
    write(PUBLIC / "dataset-annotation-intake-v1.json", receipt)
    print(json.dumps({"status": receipt["status"], "revision": revision, "domain_counts": dict(domains),
                      "repository_counts": dict(repositories), "bytes": sum(c["bytes"] for c in captures.values())}))


if __name__ == "__main__":
    main()
