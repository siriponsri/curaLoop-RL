"""Expanded owner-requested family discovery using outcome-free metadata only."""

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

from .candidate_audit import ROOT, canonical, overlap, project_payload, select_ids, validate_url

CONFIG = ROOT / "research/configs/expanded_gene_audit_v1.json"
RAW = ROOT / "research/raw_data/gene-audit-20261104-v1"
OUT = ROOT / "docs/evidence/design-expansion-20261104-v1"


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def operation(url):
    try:
        return validate_url(url)
    except ValueError:
        p = urlparse(url)
        if p.scheme != "https" or p.netloc != "pubchem.ncbi.nlm.nih.gov" or p.query or p.fragment:
            raise ValueError("Unknown origin/query in expanded metadata operation.") from None
        if re.fullmatch(r"/rest/pug/assay/target/genesymbol/[A-Z][A-Z0-9]*/aids/JSON", p.path):
            return "gene_aids"
        if re.fullmatch(r"/rest/pug/assay/aid/\d+(,\d+)+/description/JSON", p.path):
            return "batch_descriptions"
        raise ValueError(
            "Expanded discovery never permits outcome operations or filters."
        ) from None


def project(kind, data):
    if kind == "gene_aids":
        assert set(data) == {"IdentifierList"} and set(data["IdentifierList"]) == {"AID"}
        return sorted(set(data["IdentifierList"]["AID"]))
    if kind == "batch_descriptions":
        assert set(data) == {"PC_AssayContainer"}
        return [
            project_payload("description", {"PC_AssayContainer": [c]})
            for c in data["PC_AssayContainer"]
        ]
    return project_payload(kind, data)


class Fetcher:
    def __init__(self, cfg):
        self.cfg, self.receipts, self.bytes, self.blocked, self.start = (
            cfg,
            [],
            0,
            False,
            time.monotonic(),
        )

    def get(self, url):
        kind = operation(url)
        if (
            self.blocked
            or len(self.receipts) >= self.cfg["max_HTTP_requests"]
            or self.bytes >= self.cfg["max_payload_bytes_before_next_request"]
            or time.monotonic() - self.start > self.cfg["max_HTTP_wall_seconds_before_next_request"]
        ):
            raise ValueError("Prespecified expanded-audit access/resource cap reached.")
        time.sleep(0.55)
        receipt = {
            "url": url,
            "kind": kind,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with urlopen(url, timeout=20) as response:
                raw = response.read(self.cfg["max_response_bytes"] + 1)
                self.bytes += len(raw)
                if len(raw) > self.cfg["max_response_bytes"]:
                    raise ValueError("Expanded metadata response exceeds cap.")
                answer = project(kind, json.loads(raw))
                name = hashlib.sha256(url.encode()).hexdigest() + ".json"
                (RAW / name).write_bytes(raw)
                receipt.update(
                    status="PASS",
                    sha256=hashlib.sha256(raw).hexdigest(),
                    bytes=len(raw),
                    raw_file=name,
                )
                return answer
        except Exception as error:
            if isinstance(error, HTTPError) and error.code in (401, 403):
                self.blocked = True
            receipt.update(
                status="FAIL",
                error=type(error).__name__ + ": " + str(error),
                no_retry_or_bypass=True,
            )
            raise
        finally:
            self.receipts.append(receipt)
            save(OUT / "requests.json", self.receipts)


def main():
    if RAW.exists() or OUT.exists():
        raise ValueError("Keep existing expanded attempts; use a new version.")
    cfg = json.loads(CONFIG.read_text())
    RAW.mkdir(parents=True)
    OUT.mkdir(parents=True)
    (OUT / ".gitattributes").write_text(
        "*.json whitespace=trailing-space,space-before-tab,cr-at-eol\n*.csv whitespace=trailing-space,space-before-tab,cr-at-eol\n*.xml whitespace=trailing-space,space-before-tab,cr-at-eol\n",
        newline="\n",
    )
    start, cpu = time.perf_counter(), time.process_time()
    from .candidate_audit import reference_structures

    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    refs = {
        name: {
            "structures": keys,
            "fingerprints": [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in sorted(keys)],
        }
        for name, keys in reference_structures().items()
    }
    fetcher, records = Fetcher(cfg), []
    for gene, family in cfg["genes_and_provisional_families"].items():
        row = {
            "gene_query": gene,
            "provisional_family": family,
            "status": "NOT_YET_SELECTED",
            "candidate_metadata": [],
            "selection_history": [],
            "outcomes_read": False,
            "final_role_assigned": False,
            "rights": "Source/depositor and exact file rights not cleared; no license inferred from API access",
        }
        try:
            aids = fetcher.get(
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/target/genesymbol/{gene}/aids/JSON"
            )
            row["unfiltered_gene_aid_count"] = len(aids)
            checked = 0
            for offset in range(
                0, min(len(aids), cfg["metadata_AID_limit_per_gene"]), cfg["metadata_block_size"]
            ):
                block = aids[offset : offset + cfg["metadata_block_size"]]
                url = (
                    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/"
                    + ",".join(map(str, block))
                    + "/description/JSON"
                )
                descriptions = fetcher.get(url)
                if not isinstance(descriptions, list):
                    descriptions = [descriptions]
                assert {d["aid"]["id"] for d in descriptions} == set(block)
                for d in sorted(descriptions, key=lambda x: x["aid"]["id"]):
                    aid = d["aid"]["id"]
                    row["candidate_metadata"].append(d)
                    if not re.search(r"\b(?:q?HTS|uHTS|screening|screen)\b", d["name"], re.I):
                        row["selection_history"].append(
                            {"aid": aid, "reason": "NOT_HTS_OR_SCREENING_TITLED"}
                        )
                        continue
                    if checked >= cfg["max_membership_checks_per_gene"]:
                        break
                    checked += 1
                    try:
                        ids = fetcher.get(
                            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/JSON?cids_type=all"
                        )
                    except Exception as error:
                        row["selection_history"].append(
                            {"aid": aid, "reason": "MEMBERSHIP_FAILED", "error": str(error)}
                        )
                        continue
                    if len(ids) < cfg["minimum_unfiltered_CIDs"]:
                        row["selection_history"].append(
                            {
                                "aid": aid,
                                "reason": "FEWER_THAN_600_UNFILTERED_CIDS",
                                "n_cids": len(ids),
                            }
                        )
                        continue
                    chosen = select_ids(aid, ids, cfg["feature_sample_CIDs"])
                    properties = fetcher.get(
                        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
                        + ",".join(map(str, chosen))
                        + "/property/IsomericSMILES/JSON"
                    )
                    assert {p["CID"] for p in properties} == set(chosen)
                    structures = [canonical(p["SMILES"]) for p in properties]
                    valid = sorted(set(filter(None, structures)))
                    row.update(
                        status="FEATURE_AUDITED_CANDIDATE_NOT_FINAL_ELIGIBLE",
                        selected_aid=aid,
                        selected_metadata=d,
                        all_unfiltered_cids=len(ids),
                        feature_sample_cids=chosen,
                        sample_valid_unique=len(valid),
                        sample_invalid=sum(s is None for s in structures),
                        overlaps=overlap(valid, refs, generator),
                        final_gates=[
                            "target/species/context confirmation",
                            "file-level rights",
                            "binary endpoint definition",
                            "family adjudication",
                            "full feature-only pool audit",
                        ],
                    )
                    row["selection_history"].append(
                        {"aid": aid, "reason": "FIRST_METADATA_HTS_AND_SIZE_QUALIFIED_NO_OUTCOMES"}
                    )
                    break
                if "selected_aid" in row or checked >= cfg["max_membership_checks_per_gene"]:
                    break
            if "selected_aid" not in row:
                row["status"] = "NO_CANDIDATE_WITHIN_PRESPECIFIED_METADATA_BOUNDS"
        except Exception as error:
            row.update(status="PARTIAL_OR_FAILED", error=type(error).__name__ + ": " + str(error))
        records.append(row)
        save(OUT / "expanded-audit.json", {"status": "IN_PROGRESS", "records": records})
        print(row["status"] + " " + gene + " AID=" + str(row.get("selected_aid")), flush=True)
    result = {
        "status": "COMPLETE_WITH_OPEN_GATES",
        "records": records,
        "requested_gene_families": len(records),
        "feature_audited_candidates": sum("selected_aid" in r for r in records),
        "final_cleared_tasks": 0,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "code_lf_sha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "rdkit_version": rdBase.rdkitVersion,
        "outcome_value_requests": 0,
        "final_execution": False,
        "material_threshold": None,
        "wall_seconds": time.perf_counter() - start,
        "process_cpu_seconds": time.process_time() - cpu,
        "HTTP_requests": len(fetcher.receipts),
        "HTTP_payload_bytes": fetcher.bytes,
        "reviewer": "Same implementer, provisional family labels; not independent biological/legal review",
    }
    save(OUT / "expanded-audit.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
