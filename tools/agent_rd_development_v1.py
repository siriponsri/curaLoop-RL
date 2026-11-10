"""Fixed development-only coverage probes, actual existing model only."""

import json

from agent_rd_admin_v1 import PUBLIC, TASK, write

from curaloop_rd.agent_rd.contracts import MissionSpec
from curaloop_rd.agent_rd.store import MissionStore
from research.agent_rd_eval_v1.cases import cases
from research.agent_rd_eval_v1.execution import execute
from research.agent_rd_eval_v1.oracle import gold
from research.agent_rd_eval_v1.scoring import score

work = TASK / "development-coverage-v1"
work.mkdir(exist_ok=False)
store = MissionStore(work / "missions")
cards = {c["case_id"]: c for c in cases("development")}
truth = gold(list(cards.values()))
units = [("D-B01", "B2"), ("D-B01", "P"), ("D-C02", "P"), ("D-D01", "P"), ("D-E02", "P"), ("D-F01", "P")]
results = []
for identity, system in units:
    card = cards[identity]
    unit = {"unit_id": identity + "--17011--" + system, "case_id": identity, "system": system, "seed": 17011}
    row = store.create(MissionSpec.model_validate(card["spec"]), system=system, seed=17011)
    write(work / (unit["unit_id"] + ".json"), {**unit, "mission_id": row["mission_id"], "status": "STARTED"}, True)
    row = execute(card, unit, store, work, identity=row["mission_id"])
    value = {**unit, "mission_id": row["mission_id"], "state": row["state"], "score": score(card, truth[identity], row)}
    write(work / (unit["unit_id"] + "-result.json"), value, True)
    results.append(value)
    print(json.dumps(value), flush=True)
    write(work / "progress.json", {"results": results, "locked_evaluation": "NOT_STARTED"})
write(PUBLIC / "development-coverage-v1.json", {"status": "COMPLETE_RETAIN_ALL_OUTCOMES", "results": results,
      "scope": "Development probes only; not locked evaluation, independent expert or biological validation"}, True)
