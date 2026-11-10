"""Post-run descriptive tables from frozen scored receipts, never new inference.

No new hypothesis, significance test or score replaces the frozen analysis.
The command refuses an active/in-progress matrix and preserves existing output.
"""

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"
FROZEN = ROOT / "research/agent_rd_eval_v1/frozen"
ORDER = ("B0", "B1", "B2", "P", "A-NOREPAIR")
TOLERANCE = 0.0005000001


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def csv_file(path, rows):
    assert rows
    with path.open("x", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    progress = read(PUBLIC / "locked-progress-v1.json")
    assert progress["status"] in ("COMPLETE", "INCOMPLETE")
    # The evaluator writes the public disposition on exit, not on unit progress.
    # An operational batch boundary is resumable and is not an analysis release.
    assert progress["stop_reason"] != "OPERATIONAL_BATCH_BOUNDARY"
    analysis = read(PUBLIC / "analysis-v1/analysis.json")
    freeze_path = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
    freeze = read(freeze_path)
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    identities = read(PUBLIC / "analysis-v1/source-pins.json")
    assert all(sha(ROOT / p) == h for p, h in identities.items())
    cards = {r["case_id"]: r for r in read(FROZEN / "locked-cases.json")}
    oracle = read(FROZEN / "locked-oracle.json")
    plan = read(FROZEN / "schedule.json")
    results = {}
    traces = {}
    for path in sorted((PUBLIC / "locked-results-v1").glob("*.json")):
        if path.name.endswith("-trace.json"):
            continue
        row = read(path)
        identity = row["unit"]["unit_id"]
        assert identity not in results
        results[identity] = row
        traces[identity] = read(path.with_name(identity + "-trace.json"))["payload"]
    assert len(results) == analysis["attempted"] == progress["attempted_units"]
    assert len(plan) == analysis["planned"] == progress["planned_units"]
    dispositions = {u["unit_id"]: u["status"] for u in progress["disposition"]}
    assert all(dispositions[u["unit_id"]] == ("ATTEMPTED" if u["unit_id"] in results else progress["stop_reason"])
               for u in plan)

    units, failure_counts, system_rows = [], Counter(), []
    for unit in plan:
        identity, case_id = unit["unit_id"], unit["case_id"]
        receipt, trace = results.get(identity), traces.get(identity)
        gold = oracle[case_id]
        expected = gold["expected_action"]
        required_keys = gold["required_keys"] if expected == "answer" else []
        required_limits = gold["required_limits"] if expected == "answer" else []
        report = trace.get("released") if trace else None
        terminal = bool(trace and trace["state"] in ("COMPLETED", "ABSTAINED") and isinstance(report, dict))
        values = report.get("values", {}) if terminal else {}
        limits = report.get("limitations", []) if terminal else []
        if not isinstance(values, dict):
            values = {}
        if not isinstance(limits, list):
            limits = []
        correct = sum(key in values and type(values[key]) in (int, float) and math.isfinite(values[key])
                      and abs(values[key] - gold["permitted_values"][key]) <= TOLERANCE for key in required_keys)
        covered = sum(key in values for key in required_keys)
        limits_correct = sum(key in limits for key in required_limits)
        observed = receipt["score"] if receipt else None
        if observed:
            failure_counts.update((unit["system"], reason) for reason in observed["failure_reasons"])
        calls = trace["calls"] if trace else []
        successful_calls = sum(c["status"] == "PASS" for c in calls)
        units.append({**unit, "family": cards[case_id]["family"], "disposition": dispositions[identity],
                      "terminal_state": trace["state"] if trace else None,
                      "expected_action": expected, "released_action": report.get("action") if terminal else None,
                      "task_success": observed["success"] if observed else None,
                      "source_check_valid": observed["source_checked_release"] if observed else None,
                      "required_numeric_keys": len(required_keys),
                      "required_numeric_keys_present": covered if receipt else None,
                      "required_numeric_keys_correct": correct if receipt else None,
                      "required_scope_codes": len(required_limits),
                      "required_scope_codes_present": limits_correct if receipt else None,
                      "successful_model_calls": successful_calls if receipt else None,
                      "malformed_model_responses": observed["raw_numeric"]["malformed_responses"] if observed else None,
                      "deterministic_abstention_fallback": observed["fallback"] == "DETERMINISTIC_ABSTENTION_AFTER_CAP" if observed else None,
                      "raw_numeric_claims": observed["raw_numeric"]["claims"] if observed else None,
                      "raw_numeric_errors": observed["raw_numeric"]["wrong"] + observed["raw_numeric"]["unsupported"] if observed else None,
                      "released_numeric_claims": observed["numeric"]["claims"] if observed else None,
                      "released_numeric_errors": observed["numeric"]["wrong"] + observed["numeric"]["unsupported"] if observed else None,
                      "unit_wall_seconds": receipt["unit_wall_seconds"] if receipt else None,
                      "known_model_cpu_seconds": observed["cost"]["model_cpu_seconds"] if observed else None,
                      "model_calls": observed["cost"]["model_calls"] if observed else None,
                      "failed_model_calls_unknown_cost": observed["cost"]["failed_calls"] if observed else None,
                      "recorded_tokens": observed["cost"]["model_tokens"] if observed else None})
    for system in ORDER:
        found = [r for r in units if r["system"] == system and r["disposition"] == "ATTEMPTED"]
        answers = [r for r in found if r["expected_action"] == "answer"]
        required_n = sum(r["required_numeric_keys"] for r in answers)
        required_correct = sum(r["required_numeric_keys_correct"] for r in answers)
        scope_n = sum(r["required_scope_codes"] for r in answers)
        scope_found = sum(r["required_scope_codes_present"] for r in answers)
        parsed_calls = sum(r["successful_model_calls"] for r in found)
        malformed = sum(r["malformed_model_responses"] for r in found)
        checked = sum(r["source_check_valid"] for r in found)
        checked_fail = sum(r["source_check_valid"] and not r["task_success"] for r in found)
        recovery_units = [r for r in found if r["family"] == "recovery"]
        system_rows.append({"system": system, "attempted": len(found), "answer_expected_attempted": len(answers),
                            "required_numeric_key_instances": required_n, "required_numeric_keys_correct": required_correct,
                            "required_numeric_key_correct_rate": rate(required_correct, required_n),
                            "required_scope_code_instances": scope_n, "required_scope_codes_present": scope_found,
                            "required_scope_code_presence_rate": rate(scope_found, scope_n),
                            "successful_model_response_count": parsed_calls, "malformed_model_responses": malformed,
                            "malformed_response_rate": rate(malformed, parsed_calls),
                            "source_check_valid_count": checked, "source_check_valid_but_task_failed": checked_fail,
                            "task_fail_rate_given_valid_source_check": rate(checked_fail, checked),
                            "recovery_attempted": len(recovery_units),
                            "recovery_task_successes": sum(r["task_success"] for r in recovery_units)})

    anchors = sorted({u["case_id"] for u in plan if u["system"] == "A-NOREPAIR"})
    anchor_rows = []
    for system in ("P", "A-NOREPAIR"):
        selected = [r for r in units if r["system"] == system and r["case_id"] in anchors]
        found = [r for r in selected if r["disposition"] == "ATTEMPTED"]
        anchor_rows.append({"system": system, "fixed_anchor_cases": len(anchors), "planned": len(selected),
                            "attempted": len(found), "not_run": len(selected) - len(found),
                            "task_successes": sum(r["task_success"] for r in found),
                            "success_rate_all_planned": rate(sum(r["task_success"] for r in found), len(selected)),
                            "known_model_cpu_seconds": sum(r["known_model_cpu_seconds"] for r in found),
                            "failed_model_calls_unknown_cost": sum(r["failed_model_calls_unknown_cost"] for r in found),
                            "model_calls": sum(r["model_calls"] for r in found),
                            "recorded_tokens": sum(r["recorded_tokens"] for r in found)})
    seed_rows = []
    for system in ORDER[:4]:
        for seed in (17011, 17023, 17033):
            selected = [r for r in units if r["system"] == system and r["seed"] == seed]
            found = [r for r in selected if r["disposition"] == "ATTEMPTED"]
            seed_rows.append({"system": system, "seed": seed, "planned": len(selected), "attempted": len(found),
                              "successes": sum(r["task_success"] for r in found),
                              "success_rate_all_planned": rate(sum(r["task_success"] for r in found), len(selected))})
    failure_rows = [{"system": system, "reason": reason, "count": count}
                    for (system, reason), count in sorted(failure_counts.items())]
    destination = PUBLIC / "descriptive-v1"
    destination.mkdir(exist_ok=False)
    for name, rows in (("all-planned-units", units), ("quality-details", system_rows), ("matched-ablation-anchors", anchor_rows),
                       ("all-system-seeds", seed_rows)):
        csv_file(destination / (name + ".csv"), rows)
    if failure_rows:
        csv_file(destination / "failure-reasons.csv", failure_rows)
    write(destination / "descriptive.json", {"status": "DESCRIPTIVE_SUPPLEMENT_NO_SCORE_CHANGE",
          "matrix_status": analysis["status"], "stop_reason": progress["stop_reason"],
          "planned": len(plan), "attempted": len(results), "quality": system_rows,
          "matched_ablation": anchor_rows, "anchor_case_ids": anchors, "system_seeds": seed_rows,
          "failure_reasons": failure_rows,
          "notes": ["Task and numeric scores come from frozen scorer; no new scientific score or inferential claim.",
                    "Required-field coverage aggregates the prespecified correct-field contract on attempted answer tasks.",
                    "Malformed rates use successful provider responses as denominator, including malformed outputs.",
                    "Malformed means JSON parsing failure or invalid values-map type under the frozen scorer, not every action-schema failure.",
                    "Empty-claim numerical error is NA, not a favorable zero.",
                    "Unknown failed-call cost and planned unattempted units remain explicit.",
                    "Ablation compares P only on the same eight fixed anchors; no full-matrix extrapolation.",
                    "No independent expert or actual private-data leakage validation."],
          "source_pins": {"analysis.json": sha(PUBLIC / "analysis-v1/analysis.json"),
                          "locked-progress-v1.json": sha(PUBLIC / "locked-progress-v1.json"),
                          "freeze": sha(freeze_path), "reporting_source": sha(Path(__file__))}})
    print(json.dumps({"status": "DESCRIPTIVE_SUPPLEMENT_CREATED", "planned": len(plan), "attempted": len(results)}))


if __name__ == "__main__":
    main()
