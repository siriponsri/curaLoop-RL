"""Select one repair using only frozen D1 16-label component-macro log loss."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from research.redesign_v1.guard import GoalGuard
from research.redesign_v1.identity import CONFIG, PACKET, RUN, frozen, sha, write_new
from tools.goal4r1_reporting_v1 import components, macro, read_phase

ROOT = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")


def main():
    if Path.cwd().resolve() != ROOT:
        raise ValueError("Remote task only.")
    os.sched_setaffinity(0, {71})
    guard = GoalGuard(ROOT / RUN / "selection-resources.json", 120, 60)
    try:
        protocol = frozen(ROOT)
        rows, identities = read_phase(ROOT, "diagnosis", 576, protocol)
        summaries = []
        for predictor in protocol["diagnostic_predictors"]:
            for support in (16, 28):
                subset = [r for r in rows if r["predictor"] == predictor and r["support"] == support]
                if len(subset) != 48:
                    raise ValueError("Unbalanced diagnostic cells.")
                entry = {"predictor": predictor, "support": support,
                         "component_log_loss": components(subset, lambda r: r["log_loss"])}
                for metric in ("log_loss", "brier", "average_precision", "top12_precision", "fit_cpu_seconds", "fit_wall_seconds"):
                    entry[metric] = macro(subset, lambda r, m=metric: r[m])
                for metric in ("joint_log_loss", "product_marginal_log_loss", "permuted_log_loss", "conditional_second_label_log_loss"):
                    entry[metric] = macro(subset, lambda r, m=metric: r["joint"][m] if r["joint"] else None)
                entry["fallbacks"] = sum(bool(r["model_trace"]["fallback"]) for r in subset)
                entry["undefined_average_precision_cases"] = sum(r["average_precision"] is None for r in subset)
                summaries.append(entry)
        eligible = [r for r in summaries if r["support"] == 16 and r["predictor"] in protocol["repair_variants"]]
        selected = min(eligible, key=lambda r: (r["log_loss"], r["fit_cpu_seconds"], r["predictor"]))["predictor"]
        group_ids = sorted({r["family_id"] for r in rows})
        sensitivity = {}
        for omitted in group_ids:
            scores = {}
            for predictor in protocol["repair_variants"]:
                subset = [r for r in rows if r["support"] == 16 and r["predictor"] == predictor and r["family_id"] != omitted]
                scores[predictor] = (macro(subset, lambda r: r["log_loss"]), macro(subset, lambda r: r["fit_cpu_seconds"]))
            sensitivity[omitted] = min(scores, key=lambda m: (*scores[m], m))
        result = {"status": "PASS_SELECTION_FROZEN", "utc": datetime.now(timezone.utc).isoformat(),
                  "selected_repair": selected, "selection_population": "six exposed development assays, four components",
                  "selection_rule": protocol["selection"], "primary_support": 16,
                  "diagnosis_records": 576, "canary_records_reused": 0,
                  "summaries": summaries, "leave_one_component_out_selection_sensitivity": sensitivity,
                  "diagnostic_result_sha256": identities, "selection_is_independent_validation": False,
                  "source_sha256": sha(Path(__file__)), "reporting_source_sha256": sha(ROOT / "tools/goal4r1_reporting_v1.py")}
        write_new(ROOT / RUN / "selection.json", result)
        write_new(ROOT / PACKET / "selection-freeze-v1.json", {"status": "PASS_SELECTION_FROZEN",
                  "selected_repair": selected, "selection_sha256": sha(ROOT / RUN / "selection.json"),
                  "protocol_sha256": sha(ROOT / CONFIG), "utc": result["utc"], "used_final_or_validation": False})
        # Public summaries contain original aggregates only, never rows/labels.
        write_new(ROOT / PACKET / "predictor-diagnosis-v1.json", {k: v for k, v in result.items() if k != "diagnostic_result_sha256"})
        guard.finish("PASS", selected_repair=selected, d1_allowance_covers_this_process=True)
        print(json.dumps({"status": "PASS_SELECTION_FROZEN", "selected_repair": selected,
                          "summary_file": "predictor-diagnosis-v1.json", "records": 576}))
    except Exception as error:
        guard.finish("FAIL", exception_type=type(error).__name__)
        raise


if __name__ == "__main__":
    main()
