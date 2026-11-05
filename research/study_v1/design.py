"""Finite protocol-allowlisted case design; no labels or timing-based utility."""

import hashlib

from research.event_time import canonical


def case_key(case):
    return hashlib.sha256(canonical(case).encode()).hexdigest()


def cases(protocol, tasks, phase, seeds=None, selected=None):
    if phase not in ("canary", "development", "crossed", "benchmark", "reexecution", "calibration"):
        raise ValueError("Unknown study phase.")
    dev = sorted((t for t in tasks if t["role"] == "development"), key=lambda t: t["assay_id"])
    val = sorted((t for t in tasks if t["role"] == "validation"), key=lambda t: t["assay_id"])
    if not dev or not val or any(t["role"] not in ("development", "validation", "final") for t in tasks):
        raise ValueError("Fixed development/validation source roster required.")
    largest = sorted(dev, key=lambda t: (-t["retained_structures"], t["assay_id"]))[0]
    familiar = [op for op in protocol["operations"] if op["role"] == "familiar"]
    if phase != "canary" and (seeds not in (protocol["seeds"][:4], protocol["seeds"][:8])):
        raise ValueError("Only a frozen seed prefix is admitted.")
    if phase not in ("canary", "development") and selected not in protocol["hypotheses"]:
        raise ValueError("Selected configuration required.")
    result = []

    def add(task, seed, op, method, m, repetition=0):
        result.append({"task_id": task["assay_id"], "role": task["role"], "seed": seed,
                       "operation": op["id"], "method": method, "hypotheses": m, "repetition": repetition})

    if phase == "benchmark":
        for op in familiar:
            for repetition in range(5):
                order = ("event_dense", "event_screened") if repetition % 2 == 0 else ("event_screened", "event_dense")
                for method in order:
                    add(largest, protocol["seeds"][0], op, method, selected, repetition)
        return result
    if phase == "calibration":
        for task in dev + val:
            for seed in seeds:
                add(task, seed, familiar[0], "calibration", selected)
        return result
    roster = [largest] if phase == "canary" else dev if phase == "development" else dev + val
    if phase == "reexecution":
        roster = [dev[0], val[0]]
    for task in roster:
        operations = familiar if phase in ("canary", "development") else protocol["operations"]
        if phase == "crossed" and task["role"] == "development":
            operations = [op for op in operations if op["role"] == "held_out"]
        for seed in ([protocol["seeds"][0]] if phase in ("canary", "reexecution") else seeds):
            for op in operations:
                for m in (protocol["hypotheses"] if phase in ("canary", "development") else [selected]):
                    for method in protocol["methods"]:
                        add(task, seed, op, method, m)
    assert len({case_key(case) for case in result}) == len(result)
    assert all(case["role"] != "final" for case in result)
    return result
