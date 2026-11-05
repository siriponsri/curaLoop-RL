"""Predefined nested aggregation for exposed-development diagnostic results."""

import hashlib
import json
import statistics
from collections import defaultdict


def read_phase(root, phase, expected, protocol, selected=None):
    from research.redesign_v1.worker import case_key, cases
    allowed = {case_key(c): c for c in cases(protocol, phase, selected)}
    tasks = {t["task_id"]: t for t in protocol["tasks"]}
    if len(allowed) != expected:
        raise ValueError("Frozen expected Cartesian case count differs.")
    folder = root / ".local/goal4r1-20261105-v1/runs" / (phase + "-v1")
    rows, identities = [], {}
    for shard in sorted(folder.glob("shard-*")):
        complete = json.loads((shard / "complete.json").read_text())
        resource = json.loads((shard / "resources.json").read_text())
        identity = json.loads((shard / "identity.json").read_text())
        config_hash = hashlib.sha256((root / "research/configs/goal4r1_protocol_v1.json").read_bytes()).hexdigest()
        if identity["protocol_sha256"] != config_hash:
            raise ValueError("Worker used a different protocol.")
        if complete["status"] != "PASS" or resource["status"] != "PASS":
            raise ValueError("Incomplete or failed scientific phase.")
        for item in complete["results"]:
            path = shard / item["file"]
            if path.resolve().parent != shard.resolve():
                raise ValueError("Result path escaped its shard.")
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError("Scientific result identity changed.")
            result = json.loads(data)
            key = hashlib.sha256(json.dumps(result["case"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if key != item["case_key"]:
                raise ValueError("Result case key differs.")
            if key not in allowed or result["case"] != allowed[key]:
                raise ValueError("Result case is not in frozen allocation.")
            if any(result.get(name) != value for name, value in allowed[key].items()):
                raise ValueError("Result metadata differs from its case.")
            target = tasks[result["task_id"]]
            if result["family_id"] != target["family_id"]:
                raise ValueError("Result component identity differs.")
            if result["role"] != "development" or result["status"] != "PASS" or item["case_key"] in identities:
                raise ValueError("Forbidden role, failed or duplicate result.")
            identities[item["case_key"]] = item["sha256"]
            rows.append(result)
    if len(rows) != expected or set(identities) != set(allowed):
        raise ValueError("Scientific phase is not the frozen complete case count.")
    return rows, identities


def components(rows, metric):
    groups = defaultdict(lambda: defaultdict(list))
    for r in rows:
        value = metric(r)
        if value is not None:
            groups[r["family_id"]][r["task_id"]].append(float(value))
    return {g: statistics.mean(statistics.mean(v) for v in assays.values())
            for g, assays in sorted(groups.items())}


def macro(rows, metric):
    values = components(rows, metric)
    return statistics.mean(values.values()) if values else None


def paired(left, right):
    def key(r):
        return r["task_id"], r["seed"], r["operation"]
    a, b = {key(r): r for r in left}, {key(r): r for r in right}
    if len(a) != len(left) or len(b) != len(right) or set(a) != set(b):
        raise ValueError("Unmatched paired campaign cells.")
    if any(a[k]["family_id"] != b[k]["family_id"] for k in a):
        raise ValueError("Paired component identities differ.")
    differences = [dict(a[k], difference=a[k]["metrics"]["new_hits"] - b[k]["metrics"]["new_hits"]) for k in sorted(a)]
    values = components(differences, lambda r: r["difference"])
    import numpy as np
    x = np.array(list(values.values()))
    draws = np.random.default_rng(20261105).choice(x, (10000, len(x)), replace=True).mean(axis=1)
    return {"mean_difference_H": float(x.mean()), "component_effects": values,
            "descriptive_bootstrap_95": np.quantile(draws, [.025, .975]).tolist(),
            "components": len(x), "range": [float(x.min()), float(x.max())],
            "interval_is_confirmatory_or_population_coverage": False}
