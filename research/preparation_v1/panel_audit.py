"""HTS-panel identifier metadata discovery; never downloads a labeled dataset."""

import argparse
import ast
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen

from rdkit import Chem, rdBase
from rdkit.Chem import rdFingerprintGenerator

from .candidate_audit import ROOT, canonical, overlap, reference_structures, select_ids
from .expanded_gene_audit import operation, project

OUT = ROOT / "docs/evidence/hts-panel-preparation-20261104-v1"
RAW = ROOT / "research/raw_data/hts-panel-preparation-20261104-v1"
SOURCE_PATH = "deepchem/molnet/load_function/pcba_datasets.py"
COMMIT_URL = (
    "https://api.github.com/repos/deepchem/deepchem/commits?path=" + SOURCE_PATH + "&per_page=1"
)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def extract_task_ids(source):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "PCBA_TASKS" for t in node.targets
        ):
            names = ast.literal_eval(node.value)
            if not isinstance(names, list) or any(
                not isinstance(n, str) or not re.fullmatch(r"PCBA-\d+", n) for n in names
            ):
                raise ValueError("Unexpected task enumeration; never execute remote code.")
            ids = [int(n[5:]) for n in names]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate metadata identifiers.")
            return sorted(ids)
    raise ValueError("No literal PCBA_TASKS metadata list found.")


def get(url, receipts):
    special = url == COMMIT_URL or bool(
        re.fullmatch(
            r"https://raw\.githubusercontent\.com/deepchem/deepchem/[0-9a-f]{40}/(?:deepchem/molnet/load_function/pcba_datasets\.py|LICENSE)",
            url,
        )
    )
    kind = "software_metadata" if special else operation(url)
    if len(receipts) >= 80 or sum(r.get("bytes", 0) for r in receipts) >= 96_000_000:
        raise ValueError("Panel audit request/payload cap reached.")
    if any(
        r.get("access_denied") and urlparse(r["url"]).hostname == urlparse(url).hostname
        for r in receipts
    ):
        raise ValueError("Origin access denial retained; no bypass.")
    time.sleep(0.55)
    entry = {"url": url, "kind": kind, "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(url, timeout=20) as response:
            raw = response.read(8_000_001)
        entry["bytes"] = len(raw)
        if len(raw) > 8_000_000:
            raise ValueError("Panel metadata response exceeds cap.")
        if not special:
            value = project(kind, json.loads(raw))
        else:
            value = raw.decode("utf-8")
        name = hashlib.sha256(url.encode()).hexdigest() + ".txt"
        (RAW / name).write_bytes(raw)
        entry.update(status="PASS", sha256=hashlib.sha256(raw).hexdigest(), raw_file=name)
        return value
    except Exception as error:
        entry.update(
            status="FAIL",
            error=type(error).__name__ + ": " + str(error),
            access_denied=isinstance(error, HTTPError) and error.code in (401, 403),
        )
        raise
    finally:
        receipts.append(entry)
        save(OUT / "requests.json", receipts)


def metadata():
    if RAW.exists() or OUT.exists():
        raise ValueError("Keep prior panel attempts; use a new version.")
    RAW.mkdir(parents=True)
    OUT.mkdir(parents=True)
    (OUT / ".gitattributes").write_text(
        "*.json whitespace=trailing-space,space-before-tab,cr-at-eol\n*.csv whitespace=trailing-space,space-before-tab,cr-at-eol\n*.xml whitespace=trailing-space,space-before-tab,cr-at-eol\n",
        newline="\n",
    )
    receipts = []
    commits = json.loads(get(COMMIT_URL, receipts))
    sha = commits[0]["sha"]
    assert re.fullmatch(r"[0-9a-f]{40}", sha)
    source_url = f"https://raw.githubusercontent.com/deepchem/deepchem/{sha}/{SOURCE_PATH}"
    source = get(source_url, receipts)
    license_text = get(
        f"https://raw.githubusercontent.com/deepchem/deepchem/{sha}/LICENSE", receipts
    )
    ids = extract_task_ids(source)
    records = []
    for offset in range(0, len(ids), 32):
        block = ids[offset : offset + 32]
        descriptions = get(
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/"
            + ",".join(map(str, block))
            + "/description/JSON",
            receipts,
        )
        assert {d["aid"]["id"] for d in descriptions} == set(block)
        records.extend(descriptions)
        print(f"METADATA {len(records)}/{len(ids)}", flush=True)
    result = {
        "status": "METADATA_ONLY_COMPLETE",
        "source_code_commit": sha,
        "source_url": source_url,
        "software_license_header": license_text.splitlines()[0],
        "software_license_is_not_dataset_license": True,
        "identifier_count": len(ids),
        "records": sorted(records, key=lambda d: d["aid"]["id"]),
        "discovery_source": "All literal PCBA_TASKS identifiers in pinned official DeepChem loader; loader/CSV URLs never executed or fetched",
        "outcome_values_requested": 0,
        "final_roles_assigned": False,
        "local_code_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
    }
    save(OUT / "panel-metadata.json", result)


def features(selection_path):
    result_path = OUT / "selected-feature-audit.json"
    if result_path.exists():
        raise ValueError("Do not overwrite selected candidate audits.")
    metadata = json.loads((OUT / "panel-metadata.json").read_text())
    selection = json.loads(selection_path.read_text())
    ids = {d["aid"]["id"] for d in metadata["records"]}
    assert len(selection["records"]) <= 24 and all(r["aid"] in ids for r in selection["records"])
    assert all(not r.get("final_role_assigned", False) for r in selection["records"])
    receipts = json.loads((OUT / "requests.json").read_text())
    started, cpu = time.perf_counter(), time.process_time()
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    refs = {
        name: {
            "structures": keys,
            "fingerprints": [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in sorted(keys)],
        }
        for name, keys in reference_structures().items()
    }
    prior = json.loads(
        (ROOT / "docs/evidence/design-preparation-20261104-v1/candidate-audit.json").read_text()
    )
    old = {r["aid"]: r for r in prior["records"]}
    rows = []
    for entry in selection["records"]:
        if time.perf_counter() - started > 600:
            raise RuntimeError("Panel feature audit cap reached; retain completed records.")
        aid = entry["aid"]
        row = dict(entry)
        try:
            if aid in old:
                row.update(
                    status="VERIFIED_EXISTING_FEATURE_AUDIT_REUSED",
                    reused_audit_packet="design-preparation-20261104-v1",
                    sample_valid_unique=old[aid]["sample_valid_unique"],
                    overlaps=old[aid]["overlaps"],
                    all_unfiltered_cids=old[aid]["all_unfiltered_cid_count"],
                )
            else:
                cids = get(
                    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/JSON?cids_type=all",
                    receipts,
                )
                row["all_unfiltered_cids"] = len(cids)
                if len(cids) < 600:
                    raise ValueError(
                        "Fewer than 600 unfiltered source compounds; binary eligibility remains uninspected."
                    )
                chosen = select_ids(aid, cids, 200)
                properties = get(
                    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
                    + ",".join(map(str, chosen))
                    + "/property/IsomericSMILES/JSON",
                    receipts,
                )
                assert {r["CID"] for r in properties} == set(chosen)
                structures = [canonical(r["SMILES"]) for r in properties]
                valid = sorted(set(filter(None, structures)))
                row.update(
                    status="FEATURE_AUDIT_COMPLETE_OPEN_GATES",
                    sample_valid_unique=len(valid),
                    sample_invalid=sum(s is None for s in structures),
                    feature_sample_cids=chosen,
                    overlaps=overlap(valid, refs, generator),
                )
        except Exception as error:
            row.update(status="FAILED_OR_EXCLUDED", error=type(error).__name__ + ": " + str(error))
        row.update(outcomes_inspected=False, file_rights_cleared=False, final_role_assigned=False)
        rows.append(row)
        save(result_path, {"status": "IN_PROGRESS", "records": rows})
        print(f"{row['status']} AID={aid} {row.get('family')}", flush=True)
    save(
        result_path,
        {
            "status": "COMPLETE_WITH_OPEN_GATES",
            "records": rows,
            "rdkit_version": rdBase.rdkitVersion,
            "wall_seconds": time.perf_counter() - started,
            "process_cpu_seconds": time.process_time() - cpu,
            "selection_sha256": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
            "family_labels": "Implementer-proposed functional/homology groups; require independent domain adjudication",
            "outcome_values_read": 0,
            "final_ready_tasks": 0,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path)
    args = parser.parse_args()
    features(args.features) if args.features else metadata()
