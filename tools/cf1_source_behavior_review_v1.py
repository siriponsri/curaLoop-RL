"""Constructed author-code probes; no LightGBM training or molecular labels."""
# ruff: noqa: E402

import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start


def main():
    import numpy as np

    path = TASK / "source/dependency-review/lightgbm-v3.1.1-basic.py"
    assert sha(path) == read(TASK / "source-http/dependency-review_lightgbm-v3.1.1-basic.py.json")["sha256"]
    raw = path.read_bytes()
    dependency = raw.decode()
    phrase = "If <= 0, all iterations from start_iteration are used (no limits)."
    assert phrase in dependency.replace("``", "")
    path = TASK / "source/code/Scripts/MVS_A.py"
    parsed = ast.parse(path.read_text())
    classes = [node for node in parsed.body if isinstance(node, ast.ClassDef) and node.name == "sample_analysis"]
    assert len(classes) == 1
    namespace = {"np": np, "lgb": type("FakeLGBM", (), {"Dataset": staticmethod(lambda x, y: None)})}
    exec(compile(ast.Module(body=classes, type_ignores=[]), str(path), "exec"), namespace)
    cls = namespace["sample_analysis"]

    class Model:
        def __init__(self):
            self.leaf_calls, self.iteration_calls = [], []

        def get_leaf_output(self, tree, leaf):
            self.leaf_calls.append((tree, leaf))
            return (1.0, -2.0, 4.0)[leaf]

        def predict(self, data, start_iteration, num_iteration):
            self.iteration_calls.append(num_iteration)
            return np.array([0.25, 0.75])

    obj = cls.__new__(cls)
    obj.model = Model()
    obj.n_leaves = np.array([2, 2, 2])  # Constructed maximum zero-based leaf index.
    value = obj.get_l1(0)
    assert value == 3.0 and obj.model.leaf_calls == [(0, 0), (0, 1)]
    obj.y, obj.x, obj.n_estimators, obj.verbose = np.array([1, 0]), np.zeros((2, 1)), 3, False
    trajectory = obj.get_importance(return_trajectory=True)
    assert trajectory.shape == (2, 3) and obj.model.iteration_calls == [0, 1, 2]
    expected = np.sqrt((np.array([0.25, 0.75]) - obj.y)**2 + 3.0 * (0.25 * 0.75)**2)
    assert np.allclose(trajectory[:, 0], expected)
    assert np.array_equal(obj.get_score(np.array([1.0, 0.0]), 0.0), np.array([0.0, 0.0]))
    assert np.array_equal(obj.get_score(np.array([0.0, 1.0]), 0.0), np.array([1.0, 1.0]))
    defaults = cls(np.zeros((2, 1)), np.array([0, 1]), params="default", verbose=False, seed=90101)
    custom = cls(np.zeros((2, 1)), np.array([0, 1]), params={"num_threads": 1}, verbose=False)
    assert defaults.params["reg_lambda"] == 1.0 and defaults.params["feature_fraction"] == 0.95
    assert not hasattr(custom, "params")
    result = {
        "status": "PASS_CONSTRUCTED_SOURCE_BEHAVIOR_PROBES", "author_source_sha256": sha(path),
        "dependency_source_sha256": sha(TASK / "source/dependency-review/lightgbm-v3.1.1-basic.py"),
        "dependency_tag": "v3.1.1", "si_pages_visually_checked_for_equation": [3, 4],
        "checks": [
            {"name": "score_equation_and_clipping", "status": "PASS", "scope": "Synthetic arrays only"},
            {"name": "leaf_l1_loop", "status": "OBSERVED_CONVENTION", "maximum_leaf_index": 2,
             "indices_visited": [0, 1], "source_l1": 3.0, "all_three_constructed_leaf_l1": 7.0},
            {"name": "checkpoint_iteration_arguments", "status": "OBSERVED_CONVENTION", "arguments": [0, 1, 2],
             "pinned_dependency_zero_argument_means": "ALL_ITERATIONS_NOT_EMPTY_MODEL"},
            {"name": "dictionary_parameter_branch", "status": "OBSERVED_CONVENTION",
             "instance_dictionary_does_not_set_params": True, "default_string_branch_parameters_verified": True},
        ],
        "real_lightgbm_runtime_test": False, "molecular_inputs_used": False, "baseline_reproduction": False,
        "model_fits": 0, "confirmation_values_analyzed": False, "source_implementation_modified": False,
        "source_correction_applied": False,
    }
    new(TASK / "source-behavior-review-v2.json", result)
    new(PUBLIC / "source-behavior-review-v2.json", result)
    print(result)


if __name__ == "__main__":
    guard = start("constructed-source-behavior-v2", 180, 600, bucket="technical_retry_reserve")
    try:
        main()
        finish("constructed-source-behavior-v2", guard, "PASS_SOURCE_PROBES_NOT_REPRODUCTION")
    except BaseException:
        finish("constructed-source-behavior-v2", guard, "FAIL")
        raise
