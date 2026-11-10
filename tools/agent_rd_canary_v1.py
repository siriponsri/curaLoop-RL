"""First development-only end-to-end real-model mission and cost observation."""

import json
import sys

from agent_rd_admin_v1 import PUBLIC, TASK, write

from curaloop_rd.agent_rd.contracts import MissionSpec
from curaloop_rd.agent_rd.engine import MissionEngine
from curaloop_rd.agent_rd.store import MissionStore

tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
assert tag in ("v1", "v2", "v3")
store = MissionStore(TASK / ("development-missions-" + tag))
spec = MissionSpec(goal="Report only the mean H and D for the first arm using b10:a0:H and b10:a0:D. State development_only and seed_range_not_ci.",
                   campaign="628/677", budgets=[10], arms=["mvsa/top_ranked"], export_requested=True)
row = store.create(spec, seed=17011)
write(TASK / ("first-real-mission-id-" + tag + ".json"), {"mission_id": row["mission_id"]}, True)
row = MissionEngine(store).run(row["mission_id"])
write(TASK / ("first-real-mission-" + tag + ".json"), row, True)
receipt = {"status": "PASS_REAL_MODEL_MISSION" if row["state"] == "COMPLETED" and row["verification"]["valid"] else "RETAINED_MODEL_MISSION_NOT_COMPLETED",
           "scope": "development canary, not locked evaluation", "mission_id": row["mission_id"],
           "state": row["state"], "released": row["released"], "verification": row["verification"],
           "fallback": row["fallback"], "cost": row["cost"], "error": row["error"]}
write(PUBLIC / ("development-real-mission-" + tag + ".json"), receipt, True)
print(json.dumps(receipt, indent=2))
