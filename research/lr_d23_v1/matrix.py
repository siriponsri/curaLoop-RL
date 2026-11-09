"""Outcome-blind exact training/evaluation matrices and core assignment."""

import hashlib

TRAIN_SEEDS = (81001, 81013, 81029)
EVAL_SEEDS = (82003, 82013, 82037, 82051, 82067)
ARMS = ("candidate_v1", "G1", "Gk2", "Gk4", "T_k4_tau0.05", "frozen_cache_greedy", "nearest_hit")


def assigned_cpu(key, cpus):
    return cpus[int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big") % len(cpus)]


def training(sources, cpus, round_index):
    assert round_index in (0, 1)
    components = sorted({r["component"] for r in sources.values()})
    assert len(sources) == 6 and len(components) == 4
    units = []
    for fold, heldout in enumerate(components):
        allowed = [g for g in components if g != heldout]
        for task, meta in sorted(sources.items()):
            if meta["component"] == heldout:
                continue
            for n0 in (0, 16):
                for seed in TRAIN_SEEDS:
                    name = f"r{round_index}-p-g{fold}-{task}-n{n0}-s{seed}"
                    cpu = assigned_cpu(name, cpus)
                    base = {"name": name, "stage": "training_prefixes", "round": round_index,
                            "heldout": heldout, "training_components": allowed, "task_id": task,
                            "input_sha256": meta["sha256"], "n0": n0, "seed": seed, "budget": 32,
                            "predictor": "rf", "cpu_multiplier": 1., "cpu": cpu,
                            "control": "Gk2" if round_index == 0 else "candidate_v0"}
                    if round_index == 1:
                        base["gate_key"] = heldout + ":v0"
                    units.append(base)
                    for snapshot in (8, 16, 24):
                        for op in ("REUSE", "UPDATE"):
                            branch = dict(base, name=name.replace("-p-", "-b-") + f"-q{snapshot}-{op[0]}",
                                          stage="paired_branches", prefix=name, snapshot=snapshot, forced=op)
                            units.append(branch)
    assert sum(u["stage"] == "training_prefixes" for u in units) == 108
    assert sum(u["stage"] == "paired_branches" for u in units) == 648
    return {"schema": "curaloop.lr_d23.training_matrix.v1", "round": round_index,
            "units": units, "components": components, "labels_opened": False}


def evaluation(sources, cpus, predictor="rf", budget=32, multiplier=1., attribution=False):
    assert predictor in ("rf", "neighbor") and budget in (16, 32) and multiplier in (1., .5)
    assert not attribution or (predictor, budget, multiplier) == ("rf", 32, 1.)
    arms = ("no_history_v1", "candidate_v0") if attribution else ARMS
    units = []
    for task, meta in sorted(sources.items()):
        for n0 in (0, 16):
            for seed in EVAL_SEEDS:
                context = f"{predictor}-B{budget}-C{multiplier}-{task}-n{n0}-s{seed}"
                cpu = assigned_cpu("evaluation:" + context, cpus)
                for arm in arms:
                    name = ("attr-" if attribution else "eval-") + context + "-" + arm
                    value = {"name": name, "stage": "attribution" if attribution else "D2_primary",
                             "task_id": task, "input_sha256": meta["sha256"], "heldout": meta["component"],
                             "n0": n0, "seed": seed, "budget": budget, "predictor": predictor,
                             "cpu_multiplier": multiplier, "cpu": cpu, "control": arm}
                    if arm in ("candidate_v0", "candidate_v1", "no_history_v1"):
                        value["gate_key"] = meta["component"] + {"candidate_v0": ":v0", "candidate_v1": ":v1",
                                                               "no_history_v1": ":no_history"}[arm]
                    units.append(value)
    assert len(units) == (120 if attribution else 420)
    return {"schema": "curaloop.lr_d23.evaluation_matrix.v1", "units": units,
            "predictor": predictor, "budget": budget, "cpu_multiplier": multiplier, "labels_opened": False}


def batches(matrix, cpus, stage, maximum=24):
    """Chunk without splitting a matched prefix/pair or evaluation context."""
    groups = {}
    for unit in matrix["units"]:
        if unit["stage"] != stage:
            continue
        if stage == "paired_branches":
            key = unit["prefix"]
        elif stage == "training_prefixes":
            key = unit["name"]
        else:
            key = (unit["task_id"], unit["n0"], unit["seed"], unit["predictor"], unit["budget"], unit["cpu_multiplier"])
        groups.setdefault((unit["cpu"], str(key)), []).append(unit)
    output = []
    for cpu in cpus:
        current = []
        for (_, key), values in sorted(groups.items(), key=lambda item: hashlib.sha256(item[0][1].encode()).digest()):
            if values[0]["cpu"] != cpu:
                continue
            if current and len(current) + len(values) > maximum:
                output.append((cpu, current))
                current = []
            current.extend(sorted(values, key=lambda u: hashlib.sha256(("order:" + u["name"]).encode()).digest()))
        if current:
            output.append((cpu, current))
    assert sum(len(values) for _, values in output) == sum(u["stage"] == stage for u in matrix["units"])
    return output
