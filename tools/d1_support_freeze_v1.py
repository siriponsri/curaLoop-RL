"""Outcome-blind reuse freeze: hash files, inspect specifications, never parse utility."""
# ruff: noqa: E402 -- repository-only CLI bootstraps the source import path.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import (
    OLD,
    PUBLIC,
    TASK,
    finish_job,
    new,
    now,
    read,
    sha,
    start_job,
)


def main():
    guard = start_job("support")
    try:
        matrix = read(OLD / "execution-matrix-v1.json")
        assert sha(OLD / "execution-matrix-v1.json") == read(OLD / "main-execution-freeze.json")["matrix_sha256"]
        returned = read(OLD / "remote-return/verified-v1.json")
        export_manifest = OLD / "remote-return/export/manifest.json"
        assert sha(export_manifest) == returned["manifest_sha256"]
        authenticated = {f["path"]: f for f in read(export_manifest)["files"]}
        lookup = {entry["job"]: entry for entry in matrix["entries"]}
        entries = []
        pins = {}
        sources = []
        for entry in matrix["entries"]:
            args = entry["arguments"]
            if args["predictor"] != "rf":
                continue
            if entry["handler"] == "branch":
                prefix = lookup[args["prefix_job"]]
                if prefix["arguments"]["policy"] != "MIX" or args["snapshot"] not in (8, 16):
                    continue
            elif entry["handler"] == "main":
                if args["regime"] != "cheap" or args["policy"] not in ("G1", "Gk", "T"):
                    continue
            else:
                continue
            assert args["budget"] == 32
            assert args["training"] == (entry["handler"] == "branch")
            job = entry["job"]
            spec = OLD / "specs" / (job + ".json")
            frozen = read(OLD / ("branch-execution-freeze.json" if entry["handler"] == "branch" else "main-execution-freeze.json"))
            assert sha(spec) == frozen["spec_pins"][job]
            for filename in ("result.json", "resource.json", "trace-private.json"):
                relative = "jobs/" + job + "/" + filename
                path = OLD / "remote-return/files" / relative
                assert path.is_file() and not path.is_symlink()
                assert sha(path) == authenticated[relative]["sha256"]
                pins[str(path.relative_to(ROOT)).replace("\\", "/")] = sha(path)
            # Freeze result/trace hashes without parsing either file.
            entries.append(entry)
        assert sum(e["handler"] == "branch" for e in entries) == 144
        assert sum(e["handler"] == "main" for e in entries) == 180
        for name in (
            "research/d1_v1/common.py", "research/d1_v1/analysis.py",
            "tools/d1_analyze_v1.py", "tools/d1_support_freeze_v1.py",
        ):
            sources.append({"path": name, "sha256": sha(ROOT / name)})
        freeze = {
            "schema": "curaloop.d1.reuse_freeze.v1", "frozen_utc": now().isoformat(),
            "status": "FROZEN_BEFORE_D1_UTILITY_ANALYSIS", "entries": entries,
            "pins": pins, "analysis_sources": sources,
            "prefix_generator": "MIX seed 211, snapshots 8/16",
            "estimates_scope": "original masked training pools; original calibrated caps; not new seed71003/full pools",
            "main_controls_scope": "original full development pools and fold-selected Gk/T, five main seeds",
            "different_populations_not_paired": True,
            "selection_rule": "all RF MIX branches at8/16, both regimes; all RF cheap main G1/Gk/T",
            "primary_contrasts": ["UPDATE-REUSE", "PLAN-UPDATE", "PLAN-REUSE"],
            "equal_weighting": "within component equal assays; within assay equal available n0/snapshot cells",
            "predecision_context_bins": {"stale_labels": ["<4", ">=4"], "remaining_assays": [16, 24],
                                         "cached_margin": ["<=0.05", ">0.05"], "recent_brier": ["<=0.25", ">0.25"]},
            "minimum_useful_effect": read(TASK / "release.json")["minimum_useful_effect_new_hits_B32"],
            "new_utility_values_parsed_during_freeze": False,
            "new_molecular_units_dispatched": 0, "final_outcomes_open": False,
        }
        new(TASK / "reuse-freeze-v1.json", freeze)
        new(PUBLIC / "support-admission-v1.json", {
            "status": "PASS_AUTHENTICATED_REUSE_MANIFEST_FROZEN",
            "frozen_utc": freeze["frozen_utc"], "freeze_sha256": sha(TASK / "reuse-freeze-v1.json"),
            "branch_units": 144, "paired_state_regime_contexts": 48, "states": 24,
            "main_control_units": 180, "files_authenticated_without_utility_decode": len(pins),
            "scope": freeze["estimates_scope"], "main_controls_scope": freeze["main_controls_scope"],
            "different_populations_not_paired": True,
            "utility_values_read": False, "final_outcomes_open": False,
        })
        finish_job("support", guard, "PASS")
        print({"status": "PASS_REUSE_FREEZE", "branch_units": 144, "main_controls": 180})
    except BaseException:
        finish_job("support", guard, "FAIL")
        raise


if __name__ == "__main__":
    main()
