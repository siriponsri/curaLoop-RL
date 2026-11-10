"""Read-only compact status of this fresh task, never old scientific folders."""

import json

from agent_rd_admin_v1 import TASK, read

for folder in ("development-coverage-v1", "locked-evaluation-v1"):
    root = TASK / folder
    if not root.exists():
        continue
    rows = []
    for path in sorted((root / "missions").glob("*.json"), key=lambda p: p.stat().st_mtime)[-3:]:
        row = read(path)["payload"]
        rows.append({"id": row["mission_id"], "system": row["system"], "state": row["state"], "cost": row["cost"],
                     "calls": [{"status": c["status"], "output": c.get("output"), "error": c.get("error")} for c in row["calls"]],
                     "verification": row["verification"], "error": row["error"]})
    print(json.dumps({"folder": folder, "missions": rows}, ensure_ascii=False))
