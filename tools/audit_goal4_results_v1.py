"""Stream verified retained logs: count/cost/seed endpoints and all dense pairs."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / ".local/plan-a-20261105-v1/remote-return/goal4-full-v1"
PACKET = ROOT / "docs/evidence/goal4-20261105-v1"


def main():
    output = PACKET / "actual-log-readback-v1.json"
    if output.exists():
        raise FileExistsError("Keep readback attempts.")
    guard = Guard(PACKET / "actual-log-readback-resources-v1.json", 1800, 1024**3, 600)
    from research.benchmark_v3.prepare_features_v2 import sha_file, write_new
    from research.event_time import canonical
    from research.study_v1.identity import RUN_RELATIVE, verify_frozen, verify_selection
    from research.study_v1.design import case_key, cases
    from research.study_v1.admin import roster
    proof = json.loads((FOLDER / "local-verification-with-manifest.json").read_text())
    assert proof["status"] == "PASS_LOCAL_ALL_FILES_VERIFIED" and proof["manifest_unchanged_during_verification"]
    assert proof["manifest_sha256"] == sha_file(FOLDER / "manifest.json")
    retained = FOLDER / "files"
    protocol = verify_frozen(retained)
    selected = verify_selection(retained, protocol)["selected_hypotheses"]
    run = retained / RUN_RELATIVE
    allocation = json.loads((run / "allocation.json").read_text())
    pairs, totals = defaultdict(dict), {}
    for phase in ("development", "crossed", "benchmark", "reexecution"):
        expected = {case_key(case): case for case in cases(protocol, roster(retained), phase, allocation["seeds"], selected)}
        seen = set()
        for directory in sorted((run / "runs" / phase).glob("shard-*")):
            complete = json.loads((directory / "complete.json").read_text())
            assert complete["status"] == "PASS"
            for item in complete["results"]:
                path = (directory / item["file"]).resolve()
                assert path.parent == directory.resolve() and sha_file(path) == item["sha256"]
                result = json.loads(path.read_text())
                key = item["case_key"]
                assert key not in seen and result["case"] == expected[key]
                assert result["status"] == "PASS" and result["role"] in ("development", "validation")
                seen.add(key)
                science, metrics = result["scientific"], result["metrics"]
                assert hashlib.sha256(canonical(science).encode()).hexdigest() == result["scientific_sha256"]
                assert science["metrics"] == metrics
                initial = set(science["initial_ids"])
                assert len(initial) == protocol["initial_labels"]
                accepted, settled = set(), set()
                hits = area = previous = 0
                for event in science["events"]:
                    assert previous <= event["time"] <= metrics["time"]
                    area += (event["time"]-previous)*hits
                    previous = event["time"]
                    cid = event["candidate_id"]
                    if event["kind"] == "REQUEST_ACCEPTED":
                        assert cid not in accepted | initial and event["cost"] == 1
                        accepted.add(cid)
                    elif event["kind"] == "RESULT_DELIVERED":
                        assert cid in accepted and cid not in settled and type(event["active"]) is bool
                        settled.add(cid)
                        hits += int(event["active"])
                area += (metrics["time"]-previous)*hits
                assert metrics["new_hits"] == hits and metrics["time_discovery_area"] == area
                assert metrics["delivered"] == metrics["spent"] == len(settled)
                assert metrics["accepted_exposure"] == len(accepted) <= protocol["budget"]
                assert metrics["reserved"] == metrics["pending"] == len(accepted-settled)
                assert metrics["uncommitted"] == protocol["budget"]-len(accepted)
                op = next(op for op in protocol["operations"] if op["id"] == result["operation"])
                assert metrics["time"] == op["deadline"] and metrics["missing"] == 0
                if phase in ("development", "crossed") and result["method"] in ("event_dense", "event_screened"):
                    pairing = (result["task_id"], result["seed"], result["operation"], result["hypotheses"])
                    pairs[pairing][result["method"]] = result["scientific_sha256"]
        assert seen == set(expected)
        totals[phase] = len(seen)
    assert len(pairs) == 448 and all(set(pair) == {"event_dense", "event_screened"} for pair in pairs.values())
    matched = sum(pair["event_dense"] == pair["event_screened"] for pair in pairs.values())
    assert matched == len(pairs)
    report = {"status": "PASS_ACTUAL_LOG_READBACK", "campaigns_audited": totals,
              "initials_excluded_cost_pending_deadline_and_area_reconciled": True,
              "main_dense_screened_pairs": len(pairs), "equal_complete_scientific_signatures": matched,
              "all_three_development_M_and_selected_M_crossed_included": True,
              "full_retained_tree_sha256": proof["tree_sha256"], "audit_source_sha256": sha_file(Path(__file__)),
              "raw_input_outcomes_or_final_labels_opened": False,
              "scope": "Verified retained delivered-event logs; not an independent biological experiment or chemistry reprocessing"}
    write_new(output, report)
    guard.finish("PASS", audited_campaigns=sum(totals.values()))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
