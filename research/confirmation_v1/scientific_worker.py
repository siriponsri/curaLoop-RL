"""Frozen baseline/portfolio handlers, with an explicit evaluator release."""

import resource
import sys
import time
from pathlib import Path

from research.confirmation_v1.technical_worker import read, sha
from research.m2_costed_v2.guard import CostedGuard, new


def constructed(root, permit):
    import numpy as np
    from rdkit import Chem

    from research.confirmation_v1.features import (
        bitvectors,
        leader_groups,
        source_fingerprint_function,
        structure_group,
    )
    from research.confirmation_v1.portfolios import OPERATORS, select_prefix
    from research.confirmation_v1.rankers import author_class

    smiles = ["c1ccccc1", "Oc1ccccc1", "C1CCCCC1", "CCO", "CCCC", "CO"]
    molecules = [Chem.MolFromSmiles(value) for value in smiles]
    original = source_fingerprint_function(root)(molecules)
    compact = original.astype(np.uint8)
    assert np.array_equal(compact.astype(np.float32), original)
    groups = [structure_group(molecule) for molecule in molecules]
    assert groups[0] == groups[1] and groups[3].startswith("ACYCLIC:") and groups[3] != groups[4]
    fps = bitvectors(compact)
    rows = [{"record_id": "synthetic:" + str(i), "canonical_smiles": value} for i, value in enumerate(smiles)]
    first = leader_groups(fps, rows)
    order = list(reversed(range(len(rows))))
    reordered = leader_groups([fps[i] for i in order], [rows[i] for i in order])
    assert {rows[i]["record_id"]: first[i] for i in range(len(rows))} == {
        rows[i]["record_id"]: group for i, group in zip(order, reordered)}
    for operator in OPERATORS:
        selected = select_prefix(list(range(6)), groups, fps, 3, operator)
        assert len(selected) == len(set(selected)) == 3
        assert selected == select_prefix(list(range(6)), groups, fps, 3, operator)
    rng = np.random.RandomState(90101)
    values, labels = rng.randint(0, 2, (128, 32)), np.array([0, 1] * 64, dtype=np.float32)
    results = []
    for dtype in (np.float32, np.uint8):
        obj = author_class(root)(values.astype(dtype), labels, params="default", verbose=False, seed=90101)
        obj.params["num_threads"] = 1
        obj.get_model()
        results.append((obj.model.predict(obj.x), obj.get_importance()))
    assert np.array_equal(results[0][0], results[1][0])
    assert np.allclose(results[0][1], results[1][1], rtol=0.0, atol=1e-12)
    return {"status": "PASS_CONSTRUCTED_FROZEN_CONTROL_CHECKS", "checks": ["source_fingerprint_compact_identity",
        "acyclic_fallback", "fixed_leader_order_invariance", "common_operator_unique_deterministic_prefixes",
        "original_mvsa_float32_uint8_numerical_concordance"], "synthetic_fits": 2, "molecular_fits": 0,
        "confirmation_values_analyzed": False}


def selection_calibration(root, permit):
    import numpy as np

    from research.confirmation_v1.features import bitvectors, load
    from research.confirmation_v1.portfolios import OPERATORS, SEEDS, ranked, select_prefix

    descriptor = next(r for r in read(root / "inputs/feature-manifests-v1.json")["campaigns"] if r["campaign"] == permit["campaign"])
    _directory, bits, _labels, indices, rows = load(root, descriptor)
    fps, groups = bitvectors(bits[indices]), [row["group"] for row in rows]
    values = np.asarray([row["primary_score"] for row in rows])
    observed = []
    for seed in SEEDS:
        order = ranked(values, rows, seed)
        started = time.process_time()
        for operator in OPERATORS:
            selection = select_prefix(order, groups, fps, max(descriptor["budgets"]), operator)
            assert len(selection) == len(set(selection)) == max(descriptor["budgets"])
        observed.append(time.process_time() - started)
    return {"status": "PASS_SELECTION_COST_CALIBRATION_NO_VALUES", "campaign": permit["campaign"],
        "universe_size": len(rows), "maximum_budget": max(descriptor["budgets"]),
        "three_operator_cpu_seconds_by_seed": observed, "confirmation_values_analyzed": False}


def main():
    permit = read(sys.argv[1])
    root = Path(permit["task_root"])
    assert root == Path.home() / "curaloop-tasks/lr-cf1-20261109-v1" and root.resolve() == root
    assert read(root / "inputs/owner-source-a.json")["choice"] == "A"
    assert read(root / "inputs/blinded-support-v1.json")["status"] == "PASS_BLINDED_DATA_ADMISSION"
    for path, expected in permit["code_pins"].items():
        assert sha(root / permit.get("code_directory", "code") / path) == expected
    for path, expected in permit["source_code_pins"].items():
        assert sha(root / path) == expected
    job = root / "jobs" / permit["attempt"]
    guard = CostedGuard(job / "resource.json", permit)
    try:
        new(job / "kernel-proof.json", guard.kernel_proof())
        handler = permit["handler"]
        if handler == "constructed":
            result = constructed(root, permit)
        elif handler == "features":
            from research.confirmation_v1.features import prepare
            result = prepare(root, permit)
        elif handler == "fit":
            from research.confirmation_v1.rankers import fit
            result = fit(root, permit)
        elif handler == "selection_calibration":
            result = selection_calibration(root, permit)
        else:
            assert handler == "portfolio"
            from research.confirmation_v1.portfolios import evaluate
            result = evaluate(root, permit)
        cgroup = Path("/sys/fs/cgroup" + next(line.split("::", 1)[1] for line in Path("/proc/self/cgroup").read_text().splitlines() if line.startswith("0::")))
        cpu = dict(line.split() for line in (cgroup / "cpu.stat").read_text().splitlines())
        result["whole_cgroup_cpu_seconds_at_result"] = int(cpu["usage_usec"]) / 1000000.0
        result["measured_peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        result["measured_cgroup_memory_peak_bytes"] = int((cgroup / "memory.peak").read_text())
        new(job / "result.json", result)
        guard.finish("PASS")
    except BaseException as error:
        new(job / "failure.json", {"type": type(error).__name__, "message": str(error)[:240]})
        guard.finish("FAIL")
        raise


if __name__ == "__main__":
    main()
