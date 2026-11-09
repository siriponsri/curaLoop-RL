"""Reconcile D1 evidence, write an English owner report and close only D1."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import (
    PUBLIC,
    TASK,
    finish_job,
    new,
    now,
    read,
    save_ledger,
    sha,
    start_job,
)
from research.d1_v1.control_analysis import summarize_controls


def main():
    guard = start_job("report")
    try:
        returned = read(TASK / "remote-return/verified-v1.json")
        assert returned["status"] == "PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD"
        assert read(PUBLIC / "fresh-absence-v1.json")["status"] == "PASS_FRESH_EXACT_ABSENCE"
        files = TASK / "remote-return/files"
        calibration = read(files / "jobs/calibration/result.json")
        controls = read(files / "jobs/controls/result.json")
        assert calibration["status"] == controls["status"] == "PASS"
        assert len(calibration["contexts"]) == 12 and len(controls["units"]) == 120
        controls_summary = summarize_controls(controls["units"])
        new(PUBLIC / "controls-summary-v1.json", controls_summary)
        with (PUBLIC / "controls-summary-v1.csv").open("x", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["arm", "mean_new_hits", "mean_scientific_cpu_seconds", "mean_deliveries", "hit_delta_G1", "cpu_saving_G1"])
            for arm, values in controls_summary["arms"].items():
                writer.writerow([arm, values["hits"]["mean"], values["scientific_cpu_seconds"]["mean"],
                                 values["deliveries"]["mean"], values["comparisons"]["G1"]["hit_delta"]["mean"],
                                 values["comparisons"]["G1"]["cpu_saving_fraction"]])
        pins = read(ROOT / "docs/evidence/m2-diagnostics-20261109-v1/preservation-pins-v1.json")["pins"]
        assert all(sha(ROOT / name) == value for name, value in pins.items())
        frozen = read(TASK / "reuse-freeze-v1.json")
        assert all(sha(ROOT / row["path"]) == row["sha256"] for row in frozen["analysis_sources"])
        bundle = read(TASK / "transport-manifest.json")
        for row in bundle["files"]:
            if row["path"].startswith("code/"):
                assert sha(ROOT / row["path"][5:]) == row["sha256"]
                assert sha(files / row["path"]) == row["sha256"]
        ledger = read(TASK / "ledger.json")
        for name in ("return-export-v1", "return-fetch-v1", "return-verify-v1", "remote-exact-cleanup-v1"):
            resource = TASK / "jobs" / name / "resource.json"
            assert read(resource)["status"] == "PASS"
            assert name not in ledger["jobs"]
            ledger["jobs"][name] = {"status": "PASS", "resource_sha256": sha(resource),
                                    "reservation_bucket": "utilities_setup_analysis_tests_return_report"}
        save_ledger(ledger)
        assert all(row["status"] == "PASS" for name, row in ledger["jobs"].items() if name != "report")
        charge = sum(ledger["retained_reservations_seconds"].values())
        assert charge == 4500
        reused = read(PUBLIC / "reuse-results-v1.json")
        report = [
            "# D1: operation headroom and cheap-control investigation",
            "",
            "Date: 9 November 2026, Asia/Bangkok. Status: COMPLETE_FOR_OWNER_REVIEW.",
            "Scientific interpretation: limited context-dependent headroom; no new method superiority established.",
            "No D2/M3 release, gate training, final16 access or conditional96-hour activation.",
            "",
            "## What was actually completed",
            "",
            "The owner's D1 approval released a fresh 4 CPU-hours / 24 hours / one combined worker.",
            "Thresholds were frozen before D1 diagnostic utility: +1 new positive per B32, or >=20%",
            "scientific CPU saving with mean hit loss <=0.25. These are exploratory engineering",
            "preferences, not clinically justified or confirmatory thresholds.",
            "",
            "Reused 144 authenticated RF MIX branch units at 24 states / 48 state-regime contexts",
            "and 180 original main-control units. The reuse freeze authenticated 972 files before",
            "utility decoding. This did not create independent replication. These paired effects",
            "use the original masked training pools, seed211 and calibrated C, not new full pools",
            "or the proposed fallback seed71003/C5/65. Original caps and source roles were retained.",
            "",
            "The fresh counterfactual matrix was unnecessary and NOT_RUN. H3's missing five-arm",
            "catalogue was evaluated separately: 120 new campaigns (6 exposed development assays",
            "x uniform n0=0/16 x seeds71003/71017 x five fixed controls), using full pools/B32/C5.",
            "All timed new campaigns ran serially in one dr-train service on CPU69, with aggregate",
            "CPUQuota100%, MemoryMax4GiB, swap0 and single-thread libraries. Twelve complete",
            "synthetic full-reference contexts passed before biological H3 payload decoding.",
            "",
            "## H1/H2: same-state forced operation, common G1 continuation",
            "",
            "| Original regime | Contrast | Mean delta new hits | Mean added scientific CPU seconds | First choices changed / 24 |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
        for regime, comparisons in reused["paired"].items():
            for contrast, values in comparisons.items():
                report.append(f"| {regime} | {contrast} | {values['assigned_hit_effect']['mean']:.4f} | {values['assigned_cpu_effect_seconds']['mean']:.4f} | {values['action_changes']} |")
        report += [
            "",
            "All 24 assigned states had executed support for these contrasts in each regime.",
            "The first action changed often; PLAN's weak average benefit is not explained by",
            "always choosing the same compound. Mean UPDATE/PLAN discovery effects did not reach",
            "+1 across the whole assigned slice. These are one-operation effects followed by",
            "G1, not evaluation of a repeatedly deployed computation policy.",
            "",
            "The prespecified stale>=4 bin contains only eight states. UPDATE-REUSE is +1.1667",
            "there, versus +0.21875 in stale<4. Bins have different assay/component composition;",
            "this is an exploratory association, not causal evidence that k4 is optimal. The",
            "bin cannot replace the full-cohort estimand or establish a learned trigger. Likewise",
            "a favorable remaining-budget bin is not a license to select the horizon afterward.",
            "Ranking changes after a hypothetical refit remain unidentified from retained traces.",
            "",
            "## H3: fresh full-pool matched controls",
            "",
            "| Arm | Mean new hits | Mean scientific CPU seconds | Delta hits vs G1 | CPU saving vs G1 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for arm, values in controls_summary["arms"].items():
            comparison = values["comparisons"]["G1"]
            report.append(f"| {arm} | {values['hits']['mean']:.4f} | {values['scientific_cpu_seconds']['mean']:.5f} | {comparison['hit_delta']['mean']:.4f} | {comparison['cpu_saving_fraction']:.1%} |")
        report += [
            "",
            "Frozen-cache fits only initial information; one-class starts never gain a later",
            "RF fit. Nearest-hit uses delivered positives only, with an explicit seeded no-active",
            "fallback. Its prequential0.5 field is a placeholder, not a calibrated posterior.",
            "Gk is fixed k4; T is fixed k4/tau0.05 and may use PLAN. This is distinct from M2's",
            "fold-selected Gk (k2 here) and inherited T evidence. Do not mix old five-seed controls",
            "with new two-seed controls or masked-prefix effects to manufacture a paired gain.",
            "",
            "Detailed component effects and every pairwise incumbent contrast are in the JSON.",
            "A mean CPU/discovery preference can support using a cheap existing control; it is",
            "not novelty evidence. No residual or learned policy was trained/evaluated in D1.",
            "",
            "## Uncertainty and claims",
            "",
            "Six assays/four annotation components remain the biological scope. Components are",
            "not certified independent families. Snapshot dependence, one MIX seed and only two",
            "fresh control seeds preclude broad population claims. Equal component totals and",
            "equal assays within components were used. No population CI/p-value was invented.",
            "Binary retrospective unit-cost synchronous FS-Mol cannot establish rare-hit,",
            "clinical, laboratory-dollar, asynchronous-latency or commercial performance.",
            "Batch startup is paid once and measured in the whole-process resource receipt;",
            "individual C includes fingerprints/graphs, model initialization, fitting and choice.",
            "Scientific CPU savings are not end-to-end runtime savings or total-host CPU claims.",
            "",
            "## Closure and next owner decision",
            "",
            f"Retained D1 charge: {charge:,}/14,400 seconds ({charge/3600:.2f}/4 CPU-hours):",
            "2,400 utilities +900 synthetic admission +1,200 controls. No old allowance was reused.",
            "This is conservative reservation accounting, not a reconstructed whole-session CPU",
            "measurement. Unused allowance is closed rather than automatically spent on D2.",
            f"Full remote return: {returned['file_count']:,} task files / {returned['total_bytes']:,} bytes",
            f"plus {returned['export_file_count']} export files. Every file was locally reread/hash-verified",
            "before exact owned task/export cleanup and fresh absence. All 58 old preservation",
            "pins, including ten historical ledgers and frozen predictor/engine bytes, match.",
            "",
            "Next decision is whether a distinct bounded D2 residual hypothesis is justified",
            "against the strongest cheap controls. D1 does not automatically qualify a new",
            "method: inspect component heterogeneity and residual room first. Any D2 needs its",
            "own fixed candidate, data/compute scope and owner release. Do not relax thresholds,",
            "repeat M1, enlarge the cohort, open final16, or pivot to benchmark publication.",
            "Product/workflow value stays separate; no product changes or clinical/business",
            "validation occurred. Current work remains local on main, without commit/push.",
            "",
            "Independent scientific/code review and a full study reexecution are NOT_RUN.",
        ]
        path = ROOT / "docs/03_research/D1_OPERATION_HEADROOM_RESULTS_20261109.md"
        with path.open("x", encoding="utf-8", newline="\n") as file:
            file.write("\n".join(report) + "\n")
        new(PUBLIC / "closure-audit-v1.json", {
            "status": "PASS_D1_TECHNICAL_CLOSURE", "scientific_decision": "OWNER_REVIEW_NO_AUTOMATIC_D2",
            "new_synthetic_contexts": 12, "new_control_campaigns": 120, "new_counterfactual_branches": 0,
            "old_branch_units_reused": 144, "old_main_control_units_reused": 180,
            "historical_preservation_files": len(pins), "old_ledgers_reopened": False,
            "retained_cpu_seconds": charge, "cap_seconds": 14400,
            "report_sha256": sha(path), "final_outcomes_open": False,
            "conditional96h_activated": False, "new_learned_gate_fits": 0,
            "independent_review": "NOT_RUN",
        })
        finish_job("report", guard, "PASS")
        ledger = read(TASK / "ledger.json")
        ledger.update(status="CLOSED_COMPLETE_FOR_OWNER_REVIEW", closed_utc=now().isoformat(),
                      scientific_decision="OWNER_REVIEW_NO_AUTOMATIC_D2", final_outcomes_open=False)
        save_ledger(ledger)
        print({"status": "D1_COMPLETE_FOR_OWNER_REVIEW", "retained_cpu_seconds": charge,
               "controls": {arm: {"hits": v["hits"]["mean"], "cpu": v["scientific_cpu_seconds"]["mean"]}
                            for arm, v in controls_summary["arms"].items()}})
    except BaseException:
        finish_job("report", guard, "FAIL")
        raise


if __name__ == "__main__":
    main()
