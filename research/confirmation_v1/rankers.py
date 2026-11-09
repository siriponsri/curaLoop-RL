"""Frozen primary-only ranking controls; no confirmation input API."""

import importlib.util
import time

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from research.confirmation_v1.features import load
from research.confirmation_v1.technical_worker import read, sha
from research.m2_costed_v2.guard import new


def author_class(root):
    specification = importlib.util.spec_from_file_location("pinned_aic_mvsa", str(root / "author/MVS_A.py"))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.sample_analysis


def accumulated_importance(obj):
    total = np.zeros(len(obj.y), dtype=np.float64)
    for i in range(obj.n_estimators):
        # Retain the author code's zero/all-iterations checkpoint and leaf bound.
        predictions = obj.model.predict(obj.x, start_iteration=0, num_iteration=i)
        weight = sum(abs(obj.model.get_leaf_output(i, leaf)) for leaf in range(int(obj.n_leaves[i])))
        gradient = predictions - obj.y
        hessian = predictions * (1.0 - predictions)
        total += np.minimum(1.0, np.sqrt(gradient * gradient + weight * hessian * hessian))
    return total


def fit(root, permit):
    manifest = next(r for r in read(root / "inputs/feature-manifests-v1.json")["campaigns"] if r["campaign"] == permit["campaign"])
    _directory, bits, labels, universe, rows = load(root, manifest)
    output = root / "models" / permit["output_name"]
    output.mkdir(parents=True, exist_ok=False)
    method, seed = permit["ranker"], permit["seed"]
    started = time.process_time()
    if method == "mvsa":
        # Exact binary values are retained. LightGBM3.1.1 converts non-float
        # matrices to float32 internally; this avoids two redundant dense copies.
        obj = author_class(root)(bits, labels.astype(np.float32), params="default", verbose=False, seed=seed)
        obj.params["num_threads"] = 1
        obj.get_model()
        training = time.process_time() - started
        scoring_start = time.process_time()
        source_values = obj.get_importance()
        independently_accumulated = accumulated_importance(obj)
        assert np.isfinite(source_values).all() and np.isfinite(independently_accumulated).all()
        maximum = float(np.max(np.abs(source_values - independently_accumulated)))
        assert np.allclose(source_values, independently_accumulated, rtol=1e-9, atol=1e-8)
        np.save(str(output / "mvsa-scores.npy"), source_values[universe], allow_pickle=False)
        np.save(str(output / "gbm-probabilities.npy"), obj.model.predict(obj.x[universe]), allow_pickle=False)
        obj.model.save_model(str(output / "primary-gbm.txt"))
        scoring = time.process_time() - scoring_start
        details = {"source_reproduction": "PASS_FULL_PRIMARY_SCORE_CONCORDANCE", "maximum_absolute_difference": maximum,
                   "tree_count": obj.n_estimators, "source_constructor": "default", "input_value_dtype": "uint8_lossless_binary",
                   "source_internal_dataset_cast": "float32", "resource_parameter_override": {"num_threads": 1}}
    else:
        assert method == "rf"
        model = RandomForestClassifier(n_estimators=128, max_features="sqrt", min_samples_leaf=1,
                                       bootstrap=True, max_depth=None, n_jobs=1, random_state=seed)
        model.fit(bits, labels)
        training = time.process_time() - started
        scoring_start = time.process_time()
        probabilities = model.predict_proba(bits[universe])
        if 1 in model.classes_:
            values = probabilities[:, list(model.classes_).index(1)]
        else:
            values = np.zeros(len(universe))
        np.save(str(output / "rf-probabilities.npy"), values, allow_pickle=False)
        joblib.dump(model, str(output / "primary-rf.joblib"), compress=0)
        scoring = time.process_time() - scoring_start
        details = {"single_class_training": len(model.classes_) == 1, "n_estimators": 128, "n_jobs": 1}
    result = {"status": "PASS_PRIMARY_ONLY_RANKER", "campaign": permit["campaign"], "ranker": method, "seed": seed,
              "directory": str(output.relative_to(root)), "files": {p.name: sha(p) for p in output.iterdir() if p.is_file()},
              "training_cpu_seconds": training, "scoring_serialization_cpu_seconds": scoring,
              "primary_rows": len(labels), "universe_size": len(rows), "details": details,
              "model_fits": 1, "confirmation_values_analyzed": False, "final16_access": False}
    new(output / "manifest.json", result)
    return result
