"""Analyze immutable actual unit receipts; no generated or mocked observations."""

import csv
import hashlib
import json

from agent_rd_admin_v1 import PUBLIC, ROOT, read, sha, write

from research.agent_rd_eval_v1.analysis import summarize
from research.agent_rd_eval_v1.scoring import score

frozen = ROOT / "research/agent_rd_eval_v1/frozen"
receipts = [p for p in sorted((PUBLIC / "locked-results-v1").glob("*.json")) if not p.name.endswith("-trace.json")]
assert receipts, "No actual locked results to analyze"
results = [read(path) for path in receipts]
plan, cards = read(frozen / "schedule.json"), read(frozen / "locked-cases.json")
truth = read(frozen / "locked-oracle.json")
card_map = {card["case_id"]: card for card in cards}
for receipt in results:
    unit = receipt["unit"]
    trace_path = PUBLIC / "locked-results-v1" / (unit["unit_id"] + "-trace.json")
    trace = read(trace_path)
    encoded = json.dumps(trace, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == receipt["mission_file_sha256"]
    row = trace["payload"]
    encoded_row = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    assert hashlib.sha256(encoded_row).hexdigest() == trace["sha256"]
    assert row["mission_id"] == receipt["mission_id"] and row["system"] == unit["system"] and row["seed"] == unit["seed"]
    assert score(card_map[unit["case_id"]], truth[unit["case_id"]], row) == receipt["score"]
value = summarize(plan, results, cards)
destination = PUBLIC / "analysis-v1"
destination.mkdir(exist_ok=False)
write(destination / "analysis.json", value, True)
write(destination / "source-pins.json", {p.relative_to(ROOT).as_posix(): sha(p) for p in [*receipts, *sorted((PUBLIC / "locked-results-v1").glob("*-trace.json"))]}, True)
for name, rows in (("systems", value["systems"]), ("families", value["families"]), ("paired-cases", value["paired_cases"]), ("seed-differences", value["seed_differences"])):
    with (destination / (name + ".csv")).open("x", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
print(json.dumps({"status": value["status"], "attempted": value["attempted"], "primary": value["primary"]}, indent=2))
