"""Offline integrity/exposure checks for the retained preparatory packets."""

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from research.preparation_v1.candidate_audit import project_payload, select_ids, validate_url
from research.preparation_v1.expanded_gene_audit import operation, project
from research.preparation_v1.panel_audit import extract_task_ids

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/design-preparation-20261104-v1"
PANEL = ROOT / "docs/evidence/hts-panel-preparation-20261104-v1"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    checks = []
    retained_errors = []
    specs = [
        (PACKET, "request-receipts.json", "candidate-audit-20261104-v1", False),
        (
            ROOT / "docs/evidence/design-expansion-20261104-v1",
            "requests.json",
            "gene-audit-20261104-v1",
            True,
        ),
        (PANEL, "requests.json", "hts-panel-preparation-20261104-v1", True),
    ]
    for packet, receipt_name, raw_dir, expanded in specs:
        for receipt in read(packet / receipt_name):
            if receipt["status"] != "PASS":
                kind = operation(receipt["url"])
                assert kind == receipt["kind"] == "cids"
                assert receipt["error"] == "HTTPError: HTTP Error 404: PUGREST.NotFound"
                retained_errors.append(receipt)
                continue
            raw = (ROOT / "research/raw_data" / raw_dir / receipt["raw_file"]).read_bytes()
            assert sha(raw) == receipt["sha256"] and len(raw) == receipt["bytes"]
            if receipt["kind"] == "software_metadata":
                assert receipt["url"].startswith(
                    (
                        "https://api.github.com/repos/deepchem/deepchem/commits?",
                        "https://raw.githubusercontent.com/deepchem/deepchem/",
                    )
                )
                if receipt["url"].endswith("pcba_datasets.py"):
                    assert len(extract_task_ids(raw.decode())) == 128
            else:
                kind = operation(receipt["url"]) if expanded else validate_url(receipt["url"])
                assert kind == receipt["kind"]
                (project if expanded else project_payload)(kind, json.loads(raw))
            checks.append(
                {
                    "packet": packet.name,
                    "url": receipt["url"],
                    "bytes": len(raw),
                    "sha256": sha(raw),
                    "status": "PASS_SCHEMA_AND_CACHE_HASH",
                }
            )

    selection_path = ROOT / "research/configs/hts_feature_selection_v1.json"
    selection = read(selection_path)
    panel = read(PANEL / "selected-feature-audit.json")
    assert panel["status"] == "COMPLETE_WITH_OPEN_GATES"
    assert panel["selection_sha256"] == sha(selection_path.read_bytes())
    assert len(panel["records"]) == len(selection["records"]) == 23
    assert all(
        not r["outcomes_inspected"]
        and not r["file_rights_cleared"]
        and not r["final_role_assigned"]
        for r in panel["records"]
    )
    receipt_by_url = {r["url"]: r for r in read(PANEL / "requests.json")}
    for row in panel["records"]:
        if "feature_sample_cids" in row:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{row['aid']}/cids/JSON?cids_type=all"
            raw = (
                ROOT
                / "research/raw_data/hts-panel-preparation-20261104-v1"
                / receipt_by_url[url]["raw_file"]
            )
            cids = project("cids", read(raw))
            assert select_ids(row["aid"], cids, 200) == row["feature_sample_cids"]
    families = {r["family"] for r in panel["records"]}
    assert len(families) == 20
    completed = [r for r in panel["records"] if r["status"] != "FAILED_OR_EXCLUDED"]
    completed_families = {r["family"] for r in completed}
    assert len(completed) == 20 and len(completed_families) == 17

    simulation = read(PACKET / "simulation/simulation-receipt.json")
    assert (
        sha((ROOT / "research/configs/design_sensitivity_v1.json").read_bytes())
        == simulation["config_sha256"]
    )
    assert (
        sha((ROOT / "research/preparation_v1/design_sensitivity.py").read_bytes())
        == simulation["source_sha256"]
    )
    rows = list(csv.DictReader((PACKET / "simulation/all-sensitivity.csv").open()))
    assert len(rows) == 1080 and len(simulation["family_array_digests"]) == 216
    assert simulation["final_threshold_selected"] is None and not simulation["final_execution"]
    assert not simulation["candidate_outcomes_read"]

    old = "0f8e7898ab079f49f4212026b7b0ab2df24be8bf"
    old_paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", old], cwd=ROOT, text=True
    ).splitlines()
    protected = [
        p
        for p in old_paths
        if p.startswith(
            (
                "src/",
                "api/",
                "app/",
                "frontend/",
                "assets/",
                "docs/evidence/",
                "docs/manual/",
                "docs/diagrams/",
                "research/",
            )
        )
        and p != "research/README.md"
    ]
    protected += ["SOURCE_COMMIT.txt"]
    changed = []
    for offset in range(0, len(protected), 100):
        changed.extend(
            subprocess.check_output(
                ["git", "diff", "--name-only", old, "--", *protected[offset : offset + 100]],
                cwd=ROOT,
                text=True,
            ).splitlines()
        )
    assert not changed, changed

    summary_rows = []
    for r in panel["records"]:
        ref = r.get("overlaps", {}).get("all_previously_retrieved_NCATS_structures", {})
        summary_rows.append(
            {
                "aid": r["aid"],
                "planning_group": r["family"],
                "status": r["status"],
                "source_cids": r.get("all_unfiltered_cids"),
                "sample_valid_unique": r.get("sample_valid_unique"),
                "exact_seen_ncats": ref.get("exact_canonical_matches"),
                "near_seen_ncats": ref.get("queries_nearest_tanimoto_ge_0_8"),
                "final_ready": False,
            }
        )
    with (PANEL / "selected-feature-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)
    result = {
        "status": "PASS_OFFLINE_PREPARATION_INTEGRITY",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "verified_responses": len(checks),
        "retained_HTTP_404_attempts_without_cached_response_body": retained_errors,
        "total_request_attempts": len(checks) + len(retained_errors),
        "checks": checks,
        "selected_assays": len(panel["records"]),
        "provisional_groups_not_independent_certification": len(families),
        "completed_or_reused_feature_assays": len(completed),
        "feature_audited_planning_groups_not_independent_certification": len(completed_families),
        "final_ready_tasks": 0,
        "outcome_value_operations": 0,
        "preserved_previous_paths_git_diff": len(protected),
        "preservation_base": old,
        "checker_review": "Same implementer; schema/URL/cache checks, not independent domain or rights adjudication",
    }
    (PACKET / "offline-integrity.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ("checks", "retained_HTTP_404_attempts_without_cached_response_body")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
