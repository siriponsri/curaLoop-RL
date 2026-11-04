"""Second-pass local audit and immutable public-run evidence packaging.

This verifies the completed development allocation; it is not an independent
scientific review and never calls a selector or reruns a campaign.
"""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from research.event_time import Event, reconcile

from .runner import digest, execution_identity, plan


def audit(config_path: Path, folder: Path, packet: Path):
    cfg = json.loads(config_path.read_text())
    ledger = json.loads((folder / "ledger.json").read_text())
    assert digest(cfg) == ledger["config_sha256"]
    assert execution_identity() == cfg["execution_source_sha256"]
    expected = {}
    for assay, seed, condition, method in plan(cfg):
        identity = dict(
            config_sha256=digest(cfg), assay=assay, seed=seed, condition=condition, method=method
        )
        expected[digest(identity)[:24]] = identity
    assert len(expected) == cfg["expected_runs"] == 108
    assert set(ledger["attempts"]) == set(expected), "Incomplete/extra run allocation"
    matched = defaultdict(list)
    rows = []
    artifacts = {}
    for run_id, entry in ledger["attempts"].items():
        path = folder / (run_id + ".json")
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        run = json.loads(data)
        assert run["identity"] == entry["identity"] == expected[run_id]
        assert run["status"] == entry["status"] and run["status"] in ("COMPLETE", "FAILED")
        assert run["execution"]["execution_source_sha256"] == execution_identity()
        artifacts[run_id + ".json"] = data
        identity = run["identity"]
        if run["status"] != "COMPLETE":
            rows.append({**identity, "run_id": run_id, "status": "FAILED"})
            continue
        events = [Event(**e) for e in run["snapshot"]["events"]]
        metrics = reconcile(tuple(events), cfg["budget"], cfg["deadline"])
        assert metrics == run["snapshot"]["metrics"]
        assert all(run["metrics"][k] == value for k, value in metrics.items())
        assert run["restoration_verified"] and metrics["missing"] == 0
        assert metrics["spent"] + metrics["reserved"] + metrics["uncommitted"] == 24
        accepted = [e.candidate_id for e in events if e.kind == "REQUEST_ACCEPTED"]
        assert len(accepted) == len(set(accepted)) == run["selector"]["selected_requests"]
        assert not set(accepted) & set(run["initial_ids"])
        assert (
            sum(run["selector"]["fallback_reasons"].values())
            == run["selector"]["fallback_requests"]
        )
        for trace in run["decisions"]:
            tick = trace["time"]
            known = [
                e
                for e in events
                if e.kind in ("INITIAL_LABEL", "RESULT_DELIVERED") and e.time <= tick
            ]
            requested = {
                e.candidate_id for e in events if e.kind == "REQUEST_ACCEPTED" and e.time < tick
            }
            settled = {
                e.candidate_id for e in events if e.kind == "RESULT_DELIVERED" and e.time <= tick
            }
            assert trace["known_labels"] == len(known)
            assert trace["known_actives"] == sum(e.active for e in known)
            assert set(trace["pending_ids"]) == requested - settled
            assert len(trace["chosen"]) <= cfg["capacity"] - len(trace["pending_ids"])
        if identity["method"] == "frozen_greedy":
            assert run["selector"]["fit_attempts"] == 1
            if run["initial_active_count"] == 0:
                assert run["selector"]["fallback_requests"] == len(accepted)
        key = (identity["assay"], identity["seed"], identity["condition"])
        matched[key].append((run["initial_ids"], run["schedule_sha256"], run["decision_grid"]))
        rows.append(
            {
                **identity,
                "run_id": run_id,
                "status": "COMPLETE",
                "initial_actives": run["initial_active_count"],
                **run["metrics"],
                "selected_requests": len(accepted),
                "selector_fallback_requests": run["selector"]["fallback_requests"],
                "fit_successes": run["selector"]["fit_successes"],
                "attempt_wall_seconds": run["attempt_wall_seconds"],
                "attempt_cpu_seconds": run["attempt_cpu_seconds"],
            }
        )
    for points in matched.values():
        # Slots/eligible counts naturally differ, but opportunities, starts and realizations do not.
        assert len({digest((p[0], p[1])) for p in points}) == 1
        assert all([t["time"] for t in p[2]] == list(range(cfg["deadline"])) for p in points)
    public = packet / "runs"
    public.mkdir(parents=True, exist_ok=True)
    artifacts["ledger.json"] = (folder / "ledger.json").read_bytes()
    artifacts["canary-check.json"] = (folder / "canary-check.json").read_bytes()
    for name, data in artifacts.items():
        target = public / name
        if target.exists():
            assert target.read_bytes() == data, "Refuse to overwrite different evidence"
        else:
            target.write_bytes(data)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (packet / "results" / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(
            sorted(rows, key=lambda r: (r["assay"], r["seed"], r["condition"], r["method"]))
        )
    failed = sum(row["status"] == "FAILED" for row in rows)
    result = {
        "status": "PASS" if not failed else "FAIL_WITH_RETAINED_RUN_FAILURES",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": "Single implementer, explicit second-pass audit; not independent review",
        "config_sha256": digest(cfg),
        "execution_source_sha256": execution_identity(),
        "expected_runs": 108,
        "actual_runs": len(rows),
        "failed": failed,
        "matched_assay_seed_condition_cells": len(matched),
        "public_event_accounting_and_decision_information_counts": "PASS for completed runs",
        "run_byte_copies_and_hashes": "PASS",
        "final_protocol_frozen": False,
        "artifacts": {
            name: hashlib.sha256(data).hexdigest() for name, data in sorted(artifacts.items())
        },
    }
    (packet / "execution-audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in result.items() if k != "artifacts"}, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args()
    audit(args.config, args.runs, args.packet)
