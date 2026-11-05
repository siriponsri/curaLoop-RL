"""Reuse only hash-identified exposed development files; never open final data."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def main():
    packet = ROOT / "docs/evidence/goal4r1-20261105-v1"
    run = ROOT / ".local/goal4r1-20261105-v1"
    proof = json.loads((ROOT / "docs/evidence/goal4-20261105-v1/label-access-development-v1.json").read_text())
    original = ROOT / ".local/plan-a-20261105-v2/private-inputs/development"
    if proof["role"] != "development" or sha(original / "manifest.json") != proof["private_manifest_sha256"]:
        raise ValueError("Prior exposed-development manifest mismatch.")
    output = run / "private-inputs"
    ignored = subprocess.run(["git", "check-ignore", "--quiet", str(output / "probe.json")], cwd=ROOT).returncode
    if ignored != 0:
        raise ValueError("Private output is not ignored.")
    output.mkdir(exist_ok=False)
    tasks = proof["tasks"]
    if len(tasks) != 6 or len({t["family_id"] for t in tasks}) != 4 or any(t["role"] != "development" for t in tasks):
        raise ValueError("Frozen development roster mismatch.")
    for task in tasks:
        source = original / (task["task_id"] + ".json")
        if source.is_symlink() or sha(source) != task["sha256"]:
            raise ValueError("Prior private file differs.")
        shutil.copyfile(source, output / source.name)
        if sha(output / source.name) != task["sha256"]:
            raise ValueError("Private copy mismatch.")
    old = json.loads((ROOT / "research/configs/goal4_protocol_v1.json").read_text())
    variants = ["anchor_original", "anchor_normalized", "tanimoto_gp"]
    arms = [v + "__" + m for v in variants for m in ("greedy", "frozen_greedy", "event_dense")]
    arms += ["fingerprint_rf", "tanimoto_knn", "nearest_hit", "random"]
    config = {"schema": "curaloop.goal4r1.protocol.v1", "status": "DRAFT_D0_CHECKS_PENDING",
              "start_utc": "2026-11-05T14:43:55Z", "deadline_utc": "2026-11-06T02:43:55Z",
              "cpu_cap_seconds": 28800, "phase_caps_seconds": {"D0": 3600, "D1": 7200, "D2": 10800, "D3": 7200},
              "host_workers_max": 4, "compute_host": "dr-train", "worker_memory_bytes": 1024**3,
              "permitted_outcome_roles": ["development"], "tasks": tasks,
              "seeds": old["seeds"], "operations": old["operations"], "initial_labels": 16, "budget": 12,
              "hypotheses": 128, "repair_variants": variants[1:], "main_arms": arms,
              "diagnostic_predictors": variants + ["fingerprint_rf", "tanimoto_knn", "nearest_hit"],
              "diagnostic_supports": [16, 28], "query": "Same complement of nested28support for both supports",
              "knn": {"k": 8, "weights": "Tanimoto", "smoothing": "Beta(1,1)", "tie": "candidate ID"},
              "gp": {"intercept_variance": 4, "tanimoto_amplitude": 1, "nugget": 1e-8,
                     "likelihood": "logistic Bernoulli", "inference": "observed-coordinate whitened MAP/Laplace",
                     "optimizer": {"maxiter": 100, "ftol": 1e-12, "gtol": 1e-8, "maxls": 30}, "clip": 1e-9,
                     "sampling": "128 antithetic correlated pool functions via conditional Gaussian simulation"},
              "ablations": ["no_wait", "no_pending_information", "timing_blind_tail"],
              "canary_reuse": False, "canary": "Largest development pool then taskID, seed101, all supports/predictors or all four operations/13arms",
              "selection": "Minimum equal-component-macro query logloss at16support; exact tie lower mean fit CPU then lexicographic repair ID",
              "bootstrap_draws": 10000, "bootstrap_seed": 20261105,
              "runtime_packages": {"numpy": "2.3.5", "scipy": "1.17.0", "scikit-learn": "1.8.0",
                                   "threadpoolctl": "3.6.0", "joblib": "1.5.3", "pytest": "9.2.0"},
              "final_outcome_use": False, "learned_controller": False}
    write(ROOT / "research/configs/goal4r1_protocol_v1.json", config)
    write(packet / "development-input-reuse-v1.json", {"status": "PASS_HASH_VERIFIED_EXPOSED_DEVELOPMENT_REUSE",
          "tasks": tasks, "prior_manifest_sha256": proof["private_manifest_sha256"],
          "role": "development", "new_source_projection": False, "outcome_rows_emitted": False,
          "private_output_ignored": True, "final_outcome_files": 0})
    print(json.dumps({"status": "PASS", "tasks": len(tasks), "groups": 4, "rows": sum(t["rows"] for t in tasks),
                      "private_rows_emitted": False, "main_campaigns": 2496, "ablation_campaigns": 576}))


if __name__ == "__main__":
    main()
