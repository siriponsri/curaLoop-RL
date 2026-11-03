"""Lossless, public-only JSON and self-contained CSV event reports."""

import csv
import io
import json


def json_report(reports: list[dict]) -> str:
    return json.dumps({"schema_version": "1.1", "runs": reports}, ensure_ascii=False,
                      indent=2, sort_keys=True, allow_nan=False)


def csv_report(reports: list[dict]) -> str:
    """Each event row carries manifest + final metrics so CSV can stand alone."""
    stream = io.StringIO(newline="")
    fields = ["run_id", "policy_id", "scenario_id", "seed", "dataset_sha256", "algorithm_version",
              "data_origin", "scenario_origin", "manifest_json", "final_metrics_json",
              "event_index", "event_json", "step", "spent_units", "reserved_units",
              "remaining_units", "confirmed_hits", "pending_assays"]
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for report in reports:
        m = report["manifest"]
        for event, point in zip(report["events"], report["curve"], strict=True):
            row = {k: m[k] for k in ("run_id", "policy_id", "scenario_id", "seed", "algorithm_version",
                                     "data_origin", "scenario_origin")}
            row.update({"dataset_sha256": m["dataset"]["sha256"],
                        "manifest_json": json.dumps(m, ensure_ascii=False, sort_keys=True, allow_nan=False),
                        "final_metrics_json": json.dumps(report["metrics"], sort_keys=True, allow_nan=False),
                        "event_json": json.dumps(event, ensure_ascii=False, sort_keys=True, allow_nan=False)})
            row.update({k: point[k] for k in ("event_index", "step", "spent_units", "reserved_units",
                                            "remaining_units", "confirmed_hits", "pending_assays")})
            writer.writerow(row)
    return stream.getvalue()
