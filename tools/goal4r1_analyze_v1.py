"""Complete fixed development challenge, pairing and actual-log readback."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from research.redesign_v1.guard import GoalGuard
from research.redesign_v1.identity import PACKET, RUN, frozen, sha, write_new
from tools.goal4r1_reporting_v1 import components, macro, paired, read_phase

ROOT = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")


def main():
    if Path.cwd().resolve() != ROOT:
        raise ValueError("Scientific analysis runs on dr-train.")
    os.sched_setaffinity(0, {71})
    guard = GoalGuard(ROOT / RUN / "analysis-resources.json", 600, 120)
    try:
        protocol = frozen(ROOT)
        proof = json.loads((ROOT / PACKET / "selection-freeze-v1.json").read_text())
        if (sha(ROOT / RUN / "selection.json") != proof["selection_sha256"] or
            sha(ROOT / "research/configs/goal4r1_protocol_v1.json") != proof["protocol_sha256"]):
            raise ValueError("Selection/protocol freeze identity differs.")
        selection = json.loads((ROOT / RUN / "selection.json").read_text())
        selected = selection["selected_repair"]
        if selected != proof["selected_repair"]:
            raise ValueError("Selected repair differs.")
        main_rows, main_hashes = read_phase(ROOT, "campaign", 2496, protocol)
        ablation_rows, ablation_hashes = read_phase(ROOT, "ablation", 576, protocol, selected)
        repeated, repeated_hashes = read_phase(ROOT, "reexecution", 52, protocol)
        canary, canary_hashes = read_phase(ROOT, "campaign_canary", 52, protocol)
        all_rows = main_rows + ablation_rows
        from research.event_time import Event, canonical, reconcile
        operation_map = {op["id"]: op for op in protocol["operations"]}
        for r in all_rows + repeated + canary:
            scientific = r["scientific"]
            if hashlib.sha256(canonical(scientific).encode()).hexdigest() != r["scientific_sha256"]:
                raise ValueError("Scientific signature changed.")
            metrics = reconcile(tuple(Event(**e) for e in scientific["events"]), 12, operation_map[r["operation"]]["deadline"])
            if metrics != r["metrics"] or metrics != scientific["metrics"]:
                raise ValueError("Actual event readback does not reconcile.")
            initial = scientific["initial_ids"]
            seed_events = [e for e in scientific["events"] if e["kind"] == "INITIAL_LABEL"]
            if len(initial) != len(set(initial)) or len(initial) != 16 or len(seed_events) != 16 or set(initial) != {e["candidate_id"] for e in seed_events}:
                raise ValueError("Initial-label accounting differs.")
            if any(e["cost"] != 1 for e in scientific["events"] if e["kind"] == "REQUEST_ACCEPTED"):
                raise ValueError("A campaign request cost is not unit cost.")
            if max(e["time"] for e in scientific["events"]) != operation_map[r["operation"]]["deadline"]:
                raise ValueError("Campaign did not end at declared deadline.")
        # Fresh processes must exactly reproduce original scientific identities;
        # no timing or model-fitting CPU is part of the deterministic signature.
        index = {(r["task_id"], r["seed"], r["operation"], r["arm"]): r for r in main_rows}
        matched = sum(index[(r["task_id"], r["seed"], r["operation"], r["arm"])]["scientific_sha256"] == r["scientific_sha256"] for r in repeated)
        if matched != 52:
            raise ValueError("Fresh-process scientific reexecution differs.")
        table, contrasts = [], []
        arms = protocol["main_arms"] + [selected + "__" + a for a in protocol["ablations"]]
        for role in ("familiar", "held_out"):
            cell = [r for r in all_rows if r["operation_role"] == role]
            for arm in arms:
                rows = [r for r in cell if r["arm"] == arm]
                table.append({"arm": arm, "operation_role_provenance": role,
                              "operation_exposure": "Previously evaluated; not untouched operating validation",
                              "campaigns": len(rows), "H": macro(rows, lambda r: r["metrics"]["new_hits"]),
                              "component_H": components(rows, lambda r: r["metrics"]["new_hits"]),
                              "policy_cpu": macro(rows, lambda r: r["policy_cpu_seconds"]),
                              "policy_wall": macro(rows, lambda r: r["policy_wall_seconds"]),
                              "optional_waits": sum(r["optional_waits"] for r in rows),
                              "campaigns_with_fallback": sum(any(d["trace"].get("fallback") for d in r["decisions"]) for r in rows)})
            pairs = []
            for variant in ("anchor_original", "anchor_normalized", "tanimoto_gp"):
                pairs.append((variant + "__event_dense", variant + "__greedy"))
                pairs.append((variant + "__greedy", variant + "__frozen_greedy"))
                if variant != "anchor_original":
                    pairs.append((variant + "__greedy", "anchor_original__greedy"))
            for comparator in ("anchor_original__event_dense", "anchor_original__greedy", "fingerprint_rf", "nearest_hit", "tanimoto_knn"):
                pairs.append((selected + "__event_dense", comparator))
            for method in protocol["ablations"]:
                pairs.append((selected + "__event_dense", selected + "__" + method))
            for a, b in pairs:
                effect = paired([r for r in cell if r["arm"] == a], [r for r in cell if r["arm"] == b])
                contrasts.append({"left": a, "right": b, "operation_role_provenance": role, **effect})
            for variant in ("anchor_normalized", "tanimoto_gp"):
                def gain_rows(v):
                    dense = [r for r in cell if r["arm"] == v + "__event_dense"]
                    greedy = [r for r in cell if r["arm"] == v + "__greedy"]
                    # Validate pairing before deriving the fixed factorial gain.
                    paired(dense, greedy)
                    g = {(r["task_id"], r["seed"], r["operation"]): r for r in greedy}
                    return [dict(r, metrics={"new_hits": r["metrics"]["new_hits"] -
                                g[(r["task_id"], r["seed"], r["operation"])]["metrics"]["new_hits"]}) for r in dense]
                effect = paired(gain_rows(variant), gain_rows("anchor_original"))
                contrasts.append({"left": variant + "__planning_gain", "right": "anchor_original__planning_gain",
                                  "contrast_type": "predictor_by_acquisition_interaction",
                                  "operation_role_provenance": role, **effect})
        details = []
        for arm in arms:
            rows = [r for r in all_rows if r["arm"] == arm]
            decisions = [d["trace"] for r in rows for d in r["decisions"]]
            details.append({"arm": arm, "campaigns": len(rows), "decisions": len(decisions),
                            "optional_waits": sum(r["optional_waits"] for r in rows),
                            "forced_waits": sum(r["forced_waits"] for r in rows),
                            "fallback_decisions": sum(bool(t.get("fallback")) for t in decisions),
                            "learned_controller_actions": 0,
                            "maximum_root_gap": max((t.get("planning", {}).get("gap", 0) for t in decisions), default=0)})
        public = {"status": "PASS_FIXED_CHALLENGE_AND_READBACK", "utc": datetime.now(timezone.utc).isoformat(),
                  "selected_repair": selected, "main_campaigns": 2496, "ablation_campaigns": 576,
                  "protocol_sha256": proof["protocol_sha256"], "selection_sha256": proof["selection_sha256"],
                  "selection_proof_sha256": sha(ROOT / PACKET / "selection-freeze-v1.json"),
                  "reexecution_cases": 52, "reexecution_signature_matches": matched,
                  "campaign_canary_cases": 52, "actual_campaign_executions": 3176,
                  "actual_event_logs_reconciled": len(all_rows) + len(repeated) + len(canary), "method_cells": table,
                  "paired_contrasts": contrasts, "mechanism": details,
                  "development_assays": 6, "annotation_components": 4, "new_validation_or_final_labels_used": False,
                  "intervals": "Descriptive component bootstrap; only4 connected components, not independent population coverage",
                  "joint_dependence_interpretation": "Includes shared-intercept/prevalence and chemical covariance; not isolated chemical mechanism or calibrated counterfactual VOI",
                  "operation_roles": "Original familiar/held_out flags retained as provenance; all four regimes were previously evaluated",
                  "source_sha256": sha(Path(__file__)), "reporting_source_sha256": sha(ROOT / "tools/goal4r1_reporting_v1.py"),
                  "final_study_design": "NOT_FROZEN", "novel_method_established": False}
        write_new(ROOT / PACKET / "results-v1.json", public)
        write_new(ROOT / RUN / "analysis-input-identities.json", {"campaign": main_hashes, "ablation": ablation_hashes, "reexecution": repeated_hashes, "canary": canary_hashes})
        guard.finish("PASS", actual_logs=len(all_rows) + len(repeated) + len(canary), covered_by_d3_utility_allowance=True)
        print(json.dumps({"status": public["status"], "campaigns": 3072, "reexecution_matches": matched,
                          "selected_repair": selected, "results_file": "results-v1.json"}))
    except Exception as e:
        guard.finish("FAIL", exception_type=type(e).__name__)
        raise


if __name__ == "__main__":
    main()
