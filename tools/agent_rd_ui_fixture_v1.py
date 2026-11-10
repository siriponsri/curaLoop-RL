"""Copy an actual aggregate-only development mission for interface regression."""

from agent_rd_admin_v1 import ROOT, TASK, read, write

row = read(TASK / "first-real-mission-v3.json")
assert row["state"] == "COMPLETED" and row["cost"]["model_calls"] == 1
keys = ("mission_id", "revision", "state", "created_utc", "spec", "events", "candidate", "released", "verification", "fallback", "error", "cost", "evidence")
fixture = {key: row[key] for key in keys}
fixture["calls"] = [{key: call[key] for key in ("call_id", "status", "output")} for call in row["calls"]]
fixture["tool_receipts"] = row["tool_receipts"]
write(ROOT / "frontend/src/__fixtures__/agent-real-development-v3.json", fixture, True)
print("Copied actual one-call development response; interface fixture is not new model evidence")
