"""Freeze this bounded development allocation before observing method outcomes."""

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone

from .baselines import METHODS
from .fetch_sources import RAW, SOURCES
from .prepare_cohort import EXPECTED, OUT, ROOT
from .runner import digest, execution_identity


def main():
    config_path = ROOT / "research/configs/ncats_development_v1.json"
    if config_path.exists():
        raise ValueError("Freeze already exists; amendments need a new ID, not an overwrite.")
    audit = json.loads((OUT / "preparation-audit.json").read_text())
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("Commit implementation and protocol before freezing this allocation.")
    for assay in SOURCES:
        if hashlib.sha256((RAW / (assay + ".smiles")).read_bytes()).hexdigest() != EXPECTED[assay]:
            raise ValueError("Raw source changed: " + assay)
        if (
            hashlib.sha256((OUT / (assay + ".json")).read_bytes()).hexdigest()
            != audit["assays"][assay]["cohort_sha256"]
        ):
            raise ValueError("Prepared cohort changed: " + assay)
    cfg = {
        "schema_version": "curaloop.ncats-development-run.v1",
        "protocol_id": "ncats-three-assay-development-20261104-v1",
        "status": "FROZEN_DEVELOPMENT_ONLY",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "implementation_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "execution_source_sha256": execution_identity(),
        "final_evaluation": False,
        "assays": list(SOURCES),
        "cohort_sha256": {a: audit["assays"][a]["cohort_sha256"] for a in SOURCES},
        "raw_source_sha256": EXPECTED,
        "sample_size_per_assay": 600,
        "initial_count": 24,
        "initialization": "random.Random(seed).sample(sorted IDs,24); no label inspection; retain zero-active starts",
        "seeds": [0, 1, 2],
        "budget": 24,
        "capacity": 3,
        "deadline": 12,
        "unit_cost": 1,
        "decision_opportunities": "Integer grid 0..11 for every method; process all due events before refill; no new requests at T=12",
        "conditions": {"common": [2], "heterogeneous": [1, 2, 4]},
        "duration_generator": "foundation keyed_duration(task_id,seed,candidate_id,assay_type); no activity input",
        "methods": list(METHODS),
        "pending_lambda": 0.2,
        "predictor": {
            "family": "StandardScaler->LogisticRegression",
            "solver": "liblinear",
            "C": 1.0,
            "max_iter": 500,
        },
        "transductive_features": "All pool fingerprints public; scaler/classifier fit only revealed labels; no audit labels supplied",
        "primary_development_diagnostic": "pending_penalty minus greedy H(T), descriptive paired by assay/seed; not final H1 test",
        "common_negative_control": "Greedy/pending exact public event traces must match",
        "threads": 1,
        "max_cumulative_run_wall_seconds": 300,
        "concurrency": 1,
        "expected_runs": 108,
        "canary": "18 included runs: each assay/method, seed0, heterogeneous; retain failures; no repeats",
        "compute_costs": "No paid APIs/GPU; unit assay costs are synthetic; actual wall/CPU/peak working set measured",
        "unimplemented_controls": [
            "objective-matched asynchronous probabilistic comparator",
            "ensemble uncertainty",
            "learned controller",
        ],
        "inference": "One correlated NCATS panel, development endpoints only. No clinical, commercial, cross-target-transfer or prospective inference.",
    }
    config_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    packet = ROOT / "docs/evidence/ncats-development-20261104-v1"
    packet.mkdir(parents=True, exist_ok=True)
    for source, name in (
        (RAW / "source-receipts.json", "source-receipts.json"),
        (OUT / "preparation-audit.json", "preparation-audit.json"),
        (OUT / "exclusions.csv", "exclusions.csv"),
    ):
        if (packet / name).exists():
            raise ValueError("Evidence file already exists: " + name)
        shutil.copy2(source, packet / name)
    records = []
    for name, meta in SOURCES.items():
        records.append(
            {
                "task_id": "ncats2014-" + name + "-development-v1",
                "source_url": "https://tripod.nih.gov/tox21/challenge/download?id="
                + meta["download_id"]
                + "&sec=",
                "dataset_sha256": cfg["cohort_sha256"][name],
                "assay_endpoint": meta["endpoint"],
                "assay_id": "PubChem_AID_" + str(meta["aid"]) + "__NCATS_2014_CHALLENGE_TRAINING",
                "data_rights_status": "LOCAL_USE_REVIEWED",
                "controller_role": "development",
                "target_family": meta["family"],
                "source_release": "NCATS Tox21 Challenge 2014 training endpoint; unversioned export pinned by retrieved SHA256",
                "functional_phenotype": meta["endpoint"]
                + "; source binary activity, not therapeutic efficacy",
                "label_mapping": {"1": True, "0": False},
                "label_mapping_status": "RESOLVED_WITH_SOURCE_EVIDENCE",
                "label_mapping_evidence": "https://tripod.nih.gov/tox21/challenge/data.jsp (training table and 1/0 definition)",
                "preprocessing_version": "curaloop.ncats-development-cohort.v1",
                "source_ascertainment": "Public challenge training panel; label-blind 600-row derivative after structure/conflict audit",
                "initialization_regimes": ["uniform"],
                "source_discrepancy_ids": [],
            }
        )
    registry = {
        "schema_version": "curaloop.research.task-registry.v1",
        "status": "DEVELOPMENT_ONLY_FINAL_TEST_NOT_FROZEN",
        "records": records,
        "local_resource_files": {
            r["task_id"]: "research/raw_data/ncats-development-20261104/prepared-v1/" + a + ".json"
            for a, r in zip(SOURCES, records)
        },
    }
    (ROOT / "research/manifests/ncats_development_tasks_v1.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )
    freeze = {
        "status": "FROZEN_DEVELOPMENT_ONLY",
        "config_sha256": digest(cfg),
        "implementation_commit": cfg["implementation_commit"],
        "execution_source_sha256": cfg["execution_source_sha256"],
        "frozen_at_utc": cfg["frozen_at_utc"],
        "method_outcomes_inspected_before_freeze": False,
        "final_protocol_frozen": False,
    }
    (packet / "development-freeze.json").write_text(
        json.dumps(freeze, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(freeze, indent=2))


if __name__ == "__main__":
    main()
