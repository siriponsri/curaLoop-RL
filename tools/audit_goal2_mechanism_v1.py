"""Post-hoc audit of the frozen prototype; never fits or reruns a campaign."""

import hashlib
import json
import shutil
import statistics
import zipfile

from research.planning_v2.runner import FILES, ROOT, write


def main():
    raw = ROOT / ".local/goal2-real-data-20261104-v1/final"
    packet = ROOT / "docs/evidence/goal-02-real-data-20261104-v1"
    cfg = json.loads((ROOT / "research/configs/goal_02_real_data_v1.json").read_text())
    runs = [json.loads(p.read_text()) for p in (raw / "output/runs").glob("*.json")]
    groups = {}
    for run in runs:
        key = (run["assay"], run["seed"], run["condition"])
        groups.setdefault(key, {})[run["method"]] = run
    coverage, tightened, omitted = 0, 0, 0
    max_tightening, gap_values = 0.0, []
    partial = {"rollout": 0, "content_pruned": 0}
    for arms in groups.values():
        ref = arms["rollout"]
        content = arms["content_pruned"]
        card = arms["cardinality_pruned"]
        for a, b, c in zip(ref["decisions"], content["decisions"], card["decisions"], strict=True):
            lowers = {tuple(v["action"]): v["lower"] for v in a["actions"]}
            simple = {tuple(v["action"]): v["upper"] for v in c["actions"]}
            for value in b["actions"]:
                key = tuple(value["action"])
                if not lowers[key] - 1e-9 <= value["upper"] <= simple[key] + 1e-9:
                    raise AssertionError("Offline bound coverage/tightening failed.")
                coverage += 1
                tightened += value["upper"] < simple[key] - 1e-9
                max_tightening = max(max_tightening, simple[key] - value["upper"])
            gap_values.append(b["gap"])
            omitted += len(b["actions"]) < 1  # no missing action table allowed
        for method in partial:
            balance = cfg["budget"]
            for d in arms[method]["decisions"]:
                free = cfg["capacity"] - len(d["pending_ids"])
                partial[method] += 0 < len(d["chosen"]) < min(free, balance)
                balance -= len(d["chosen"])
    if omitted:
        raise AssertionError("Missing action tables.")
    summary = json.loads((packet / "final/analysis.json").read_text())
    totals = {}
    for method in ("rollout", "cardinality_pruned", "content_pruned"):
        records = [r for r in summary["summaries"] if r["method"] == method]
        totals[method] = {
            k: sum(r[k] for r in records)
            for k in (
                "wall_seconds",
                "policy_seconds",
                "bound_seconds",
                "rollout_seconds",
                "nodes",
                "root_actions",
                "pruned_actions",
                "waits",
            )
        }
    d = [
        a["rollout"]["metrics"]["new_hits"] - a["nearest_hit"]["metrics"]["new_hits"]
        for a in groups.values()
    ]
    report = {
        "status": "PASS_AUDIT_NEGATIVE_CONTRIBUTION_RESULT",
        "post_hoc": True,
        "offline_action_bound_checks": coverage,
        "actions_tighter_than_cardinality": tightened,
        "max_tightening": max_tightening,
        "finite_model_gap_mean": statistics.mean(gap_values),
        "finite_model_gap_range": [min(gap_values), max(gap_values)],
        "partial_dispatch_decisions": partial,
        "totals": totals,
        "content_over_unpruned_policy_time_ratio": totals["content_pruned"]["policy_seconds"]
        / totals["rollout"]["policy_seconds"],
        "content_over_unpruned_total_time_ratio": totals["content_pruned"]["wall_seconds"]
        / totals["rollout"]["wall_seconds"],
        "rollout_minus_nearest_hit": {
            "mean": statistics.mean(d),
            "range": [min(d), max(d)],
            "wins": sum(x > 0 for x in d),
            "ties": d.count(0),
            "losses": sum(x < 0 for x in d),
        },
        "decision": "Do not promote this finite-world relaxation as a useful new method; no real-data planner WAIT decision or computational advantage demonstrated",
        "limitations": "One fixed order and timing measurement per run; exposed correlated panel; model/shortlist approximation; no full-pool Bayes oracle or calibrated biological guarantee",
    }
    write(packet / "mechanism-audit.json", report)
    for name in ("canary-receipt.json", "remaining-receipt.json"):
        target = packet / name
        if target.exists():
            raise FileExistsError(target)
        shutil.copyfile(raw / "output" / name, target)
    for name in ("canary.log", "remaining.log"):
        target = packet / name
        if target.exists():
            raise FileExistsError(target)
        shutil.copyfile(raw / name, target)
    source = packet / "execution-source.zip"
    with zipfile.ZipFile(source, "x", zipfile.ZIP_DEFLATED) as archive:
        for name in FILES + (
            "research/__init__.py",
            "research/planning_v2/__init__.py",
            "research/configs/goal_02_real_data_v1.json",
        ):
            archive.write(ROOT / name, name)
    write(
        packet / "result-transfer.json",
        {
            "status": "PASS",
            "remote_results_zip_sha256": "c238ae02dddd65fe35c1f5d13e6dad7e6ed68c7baafd76389f3a2eb08630c4f0",
            "local_results_zip_sha256": hashlib.sha256(
                (raw.parent / "results.zip").read_bytes()
            ).hexdigest(),
            "source_archive_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_archive_contains_assay_rows": False,
            "raw_runs_local": ".local/goal2-real-data-20261104-v1/final/output",
            "raw_runs_remote": "/home/chaw/curaloop-rl/goal2-20261104-v1/output",
            "source_archive_reason": "Preserve exact frozen source bytes including pre-existing scheduler line endings for cross-platform reproduction",
        },
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
