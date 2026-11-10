"""One-time pre-evaluation protocol/source lock, never outcome-guided replacement."""

import json
import subprocess
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write

from research.agent_rd_eval_v1.cases import ABLATION_CASES, cases, schedule
from research.agent_rd_eval_v1.oracle import gold

release, _ = authority()
assert all(sha(ROOT / p) == h for p, h in release["frozen_scientific_pins"].items())
target = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
assert not target.exists()
dev = read(PUBLIC / "development-coverage-v1.json")
assert len(dev["results"]) == 6
assert read(PUBLIC / "development-real-mission-v3.json")["status"] == "PASS_REAL_MODEL_MISSION"
assert read(PUBLIC / "component-checks-v4.json")["status"] == "PASS"
assert read(PUBLIC / "frontend-checks-v3.json")["status"] == "PASS"
assert read(PUBLIC / "browser-acceptance-v1.json")["status"] == "PASS_ACTUAL_LOCALHOST_REAL_MODEL_ACCEPTANCE"
assert read(PUBLIC / "browser-refinement-v2.json")["status"] == "PASS_SERVED_UI_REFINEMENT_NO_NEW_INFERENCE"
costs = {"extraction": read(PUBLIC / "development-real-mission-v3.json")["cost"]["model_cpu_seconds"]}
for row in dev["results"]:
    family = next(c["family"] for c in cases("development") if c["case_id"] == row["case_id"])
    costs[family] = max(costs.get(family, 0), row["score"]["cost"]["model_cpu_seconds"])
counts = {family: 0 for family in costs}
for card in cases("locked"):
    counts[card["family"]] += 9 + (3 if card["case_id"] in ABLATION_CASES else 0)
projection = sum(counts[f] * costs[f] for f in costs)
assert sum(counts.values()) == 312 and projection * 1.15 < 198600, "Observed development cost does not fit the existing evaluation envelope"
write(PUBLIC / "cpu-feasibility-v1.json", {"status": "HEURISTIC_FEASIBLE_NOT_GUARANTEED", "latest_interface_probe_cpu_by_family": costs,
      "planned_model_missions_by_family": counts, "projection_cpu_seconds": projection, "projection_with_15_percent_headroom": projection * 1.15,
      "evaluation_cap_cpu_seconds": 201600, "stop_headroom_cpu_seconds": 3000,
      "note": "One or two latest-interface observations per family, not an uncertainty bound. Earlier failed interface versions remain charged and reported. Hard stopping and all planned-unit dispositions apply."}, True)
folder = ROOT / "research/agent_rd_eval_v1/frozen"
folder.mkdir(exist_ok=False)
for split in ("development", "locked"):
    cards = cases(split)
    write(folder / (split + "-cases.json"), cards, True)
    write(folder / (split + "-oracle.json"), gold(cards), True)
write(folder / "schedule.json", schedule(), True)
paths = [*sorted((ROOT / "src/curaloop_rd/agent_rd").glob("*.py")), ROOT / "src/curaloop_rd/confirmation_study.py",
         *sorted((ROOT / "research/agent_rd_eval_v1").glob("*.py")), *sorted(folder.glob("*.json")),
         ROOT / "tools/agent_rd_evaluate_v1.py", ROOT / "tools/agent_rd_remote_v1.py", ROOT / "tools/agent_rd_remote_worker_v1.py",
         ROOT / "tools/agent_rd_supervisor_v1.py", ROOT / ".gitattributes",
         ROOT / "tools/agent_rd_freeze_v1.py", ROOT / "docs/08_agent_rd/COMPUTATIONAL_PROTOCOL_V1.md"]
assert all(path.is_file() for path in paths)
pins = {path.relative_to(ROOT).as_posix(): sha(path) for path in paths}
release = read(TASK / "release.json")
receipt = {"schema": "curaloop.agent-rd.protocol-freeze.v1", "status": "FROZEN_BEFORE_LOCKED_MODEL_CALLS",
           "utc": datetime.now(timezone.utc).isoformat(), "pre_freeze_commit": subprocess.check_output(["rtk", "proxy", "git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "pins": pins, "model": release["model"], "model_digest": release["model_digest"],
           "executed_remote_worker": "worker-v2.py", "executed_remote_worker_sha256": read(TASK / "remote-sync-v2-receipt-v1.json")["sha256"],
           "units": 408, "real_model_missions_planned": 312, "locked_cards": 32, "decoding_seeds": [17011, 17023, 17033],
           "development_coverage_receipt_sha256": sha(PUBLIC / "development-coverage-v1.json"),
           "readiness_receipt_sha256": sha(PUBLIC / "component-checks-v4.json"), "final16_access": False, "private_rows_access": False,
           "oracle_hidden_from_generator": True, "independent_expert_validation": False}
write(target, receipt, True)
write(PUBLIC / "protocol-freeze-v1.json", receipt, True)
print(json.dumps({"status": receipt["status"], "pins": len(pins), "units": 408}))
