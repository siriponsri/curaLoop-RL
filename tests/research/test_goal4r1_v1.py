"""Independent numerical references and public-boundary regressions for 4R1."""

import math
from dataclasses import replace

import numpy as np
import pytest
from scipy.linalg import cho_solve
from scipy.special import expit

from research.event_time import Campaign, Scenario
from research.planning_v3.belief import make_design
from research.planning_v3.mixture import Mixture
from research.study_v1.campaign import make_task, run_campaign as old_campaign, support_law
from research.redesign_v1.belief import design_for, fit_joint, observed_laplace, tanimoto
from research.redesign_v1.campaign import run_campaign
from research.redesign_v1.diagnostics import joint_scores, pair_ids
from research.redesign_v1.identity import load_task
from research.redesign_v1.policy import knn_scores, session


def payload(role="development"):
    return {"task_id": "constructed-public", "role": role, "family_id": "constructed",
            "records": [{"candidate_id": f"c{i:03d}", "morgan_on_bits": [i % 8, 30 + i // 8],
                         "active": i % 3 == 0} for i in range(40)]}


def operation():
    return {"id": "async_mixed", "role": "familiar", "capacity": 2,
            "law": {"1": .5, "4": .5}, "deadline": 8}


def test_covariance_and_anchor_scale_are_distinct():
    ids, packed = ("a", "b", "c", "d"), (1, 2, 1, 0)
    base = make_design(ids, packed)
    normal = design_for(ids, packed, "anchor_normalized")
    gp = design_for(ids, packed, "tanimoto_gp")
    assert np.array_equal(normal.x[:, 0], np.ones(4))
    assert np.array_equal(normal.x[:, 1:] * 8, base.x[:, 1:])
    assert not base.x.flags.writeable and not normal.x.flags.writeable
    assert gp.kernel[0, 1] == 4
    assert gp.kernel[0, 2] == 5
    assert gp.kernel[0, 0] == 5 + 1e-8
    assert np.allclose(gp.prior_chol @ gp.prior_chol.T, gp.kernel)
    assert np.linalg.eigvalsh(gp.kernel).min() > 0


@pytest.mark.parametrize("labels", [[0., 0.], [1., 1.], [0., 1.]])
def test_whitened_posterior_matches_independent_dual_reference(labels):
    gp = design_for(("a", "b", "c", "d"), (1, 3, 4, 5), "tanimoto_gp")
    indices = [0, 2]
    state, trace = observed_laplace(gp.kernel, indices, np.array(labels))
    assert trace["fallback"] is None
    lo, lh, beta, a = state
    f = lo @ beta
    p = expit(f)
    koo = gp.kernel[np.ix_(indices, indices)]
    mode_gradient = cho_solve((lo, True), f) + p - labels
    assert np.max(np.abs(mode_gradient)) < 1e-5
    cov_obs = lo @ cho_solve((lh, True), np.eye(2)) @ lo.T
    simulation_cov = gp.kernel - a @ koo @ a.T + a @ cov_obs @ a.T
    w = np.sqrt(p * (1 - p))
    b = np.eye(2) + w[:, None] * koo * w[None, :]
    cross = w[:, None] * gp.kernel[indices, :]
    dual_cov = gp.kernel - cross.T @ np.linalg.solve(b, cross)
    dual_mean = gp.kernel[:, indices] @ np.linalg.solve(koo, f)
    assert np.allclose(simulation_cov, dual_cov, atol=1e-10)
    assert np.allclose(a @ f, dual_mean, atol=1e-10)
    assert np.linalg.eigvalsh(dual_cov).min() >= -1e-10
    assert np.linalg.eigvalsh(gp.kernel - dual_cov).min() >= -1e-10


def test_one_class_updates_and_reproducible_joint_draws():
    gp = design_for(("a", "b", "c"), (1, 1, 2), "tanimoto_gp")
    prior, _ = fit_joint(gp, [], 101, "tanimoto_gp")
    positive, trace = fit_joint(gp, [("a", True)], 101, "tanimoto_gp")
    repeated, _ = fit_joint(gp, [("a", True)], 101, "tanimoto_gp")
    assert np.allclose(prior.mu, .5)
    assert positive.mu[0] > .5 and trace["one_class_start_retained"]
    assert trace["fallback"] is None
    assert np.array_equal(positive.p, repeated.p)
    assert float(prior.w @ (prior.p[:, 0] * prior.p[:, 1])) > prior.mu[0] * prior.mu[1]


def test_joint_scores_reference_manual_likelihood_and_marginals():
    model = Mixture([[.9, .8], [.1, .2]], [.5, .5])
    score = joint_scores(model, [(0, 1)], [True, False])
    joint = .5 * (.9 * .2 + .1 * .8)
    assert score["joint_log_loss"] == pytest.approx(-math.log(joint))
    assert score["product_marginal_log_loss"] == pytest.approx(-math.log(.25))
    assert score["conditional_second_label_log_loss"] == pytest.approx(-math.log(joint / .5))
    with pytest.raises(ValueError):
        joint_scores(Mixture([[.9, .8], [.1, .2]], [.6, .4]), [(0, 1)], [True, False])


def test_knn_smoothing_and_empty_or_one_class_starts():
    ids, bits = ("a", "b", "c"), (1, 1, 2)
    assert np.all(knn_scores(bits, ids, []) == .5)
    assert knn_scores(bits, ids, [("a", True)])[1] == pytest.approx(2 / 3)
    assert knn_scores(bits, ids, [("a", True)])[2] == .5
    assert np.all(knn_scores(bits, ids, [("a", False)]) > 0)


@pytest.mark.parametrize("method", ["greedy", "frozen_greedy", "event_dense"])
def test_old_control_scientific_signature_is_unchanged(method):
    data, op = payload(), operation()
    proto = {"initial_labels": 16, "budget": 12}
    old = old_campaign(data, 101, op, method, 128, proto)
    new = run_campaign(data, 101, op, "anchor_original__" + method, proto)
    assert old["scientific_sha256"] == new["scientific_sha256"]
    assert old["metrics"] == new["metrics"]


@pytest.mark.parametrize("variant", ["anchor_normalized", "tanimoto_gp"])
def test_policy_cannot_see_hidden_outcomes_or_due_times(variant):
    data, op = payload(), operation()
    task = make_task(data, 101, op)
    seed_ids = tuple(r["candidate_id"] for r in data["records"][:16])
    engine = Campaign(task, Scenario(12, 2, 8, seed_ids))
    obs = engine.observe()
    changed = replace(task, _outcomes=tuple((cid, y if cid in seed_ids else not y) for cid, y in task._outcomes),
                      durations=tuple((cid, 1 if d == 4 else 4) for cid, d in task.durations))
    other = Campaign(changed, Scenario(12, 2, 8, seed_ids)).observe()
    assert obs == other
    a = session(obs, variant + "__event_dense", 101, support_law(op), 2)
    b = session(other, variant + "__event_dense", 101, support_law(op), 2)
    assert a.select(obs)[0] == b.select(other)[0]
    with pytest.raises(ValueError):
        a.record_acceptance(("not-proposed",), 0)


@pytest.mark.parametrize("role", ["validation", "final", "test"])
def test_nondevelopment_rejected_before_records_or_file_read(tmp_path, role):
    with pytest.raises(ValueError):
        run_campaign({"role": role}, 101, operation(), "random", {})
    with pytest.raises(ValueError):
        load_task(tmp_path, {"tasks": [{"task_id": "x", "role": role}]}, "x")


def test_pair_construction_is_public_deterministic_unique():
    ids = tuple(f"c{i:03d}" for i in range(100))
    bits = tuple(1 << (i % 30) for i in range(100))
    pairs = pair_ids(ids, bits, list(range(100)))
    assert len(pairs) == len(set(pairs)) == 64
    assert pairs == pair_ids(ids, bits, list(range(100)))
    assert all(i < j for i, j in pairs)


def test_duplicate_fingerprints_with_contradictory_labels_are_retained():
    gp = design_for(("a", "b", "c"), (1, 1, 2), "tanimoto_gp")
    model, trace = fit_joint(gp, [("a", True), ("b", False)], 101, "tanimoto_gp")
    assert np.isfinite(model.p).all()
    assert trace["fallback"] is None
    assert model.mu[0] == pytest.approx(model.mu[1], abs=1e-4)


def test_launch_failure_keeps_full_durable_batch_reservation(tmp_path, monkeypatch):
    import sys
    import tools.goal4r1_admin_v1 as admin
    monkeypatch.setattr(admin, "TASK", tmp_path)
    monkeypatch.setattr(admin, "RUN", tmp_path / "run")
    monkeypatch.setattr(admin, "check_root", lambda: None)
    monkeypatch.setattr(sys, "argv", ["admin", "launch", "--phase", "constructed", "--shards", "4", "--cpu-seconds", "5"])
    def failed_launch(*args, **kwargs):
        import json
        jobs = json.loads((tmp_path / "run/reservations.json").read_text())["jobs"]
        assert len(jobs) == 4 and all(j["pid"] is None for j in jobs)
        raise OSError("constructed launch failure")
    monkeypatch.setattr(admin.subprocess, "Popen", failed_launch)
    with pytest.raises(OSError):
        admin.main()
    import json
    jobs = json.loads((tmp_path / "run/reservations.json").read_text())["jobs"]
    charges, active, _ = admin.state(jobs)
    assert active == 4 and charges["D0"] == admin.ALLOWANCE["D0"] + 4 * 7
    with pytest.raises(RuntimeError):
        admin.main()


def test_useful_pending_information_has_analytic_wait_value():
    from research.planning_v3.recourse import PublicState, RecoursePlanner
    model = Mixture([[0, .01, .99, .01, .99], [1, .99, .01, .99, .01]], [.5, .5])
    planner = RecoursePlanner(model, (2,), 2)
    state = PublicState(4, 2, frozenset({0}), ((0, 0),))
    values, _ = planner.evaluate_actions(state, [(), (1,)])
    assert values == pytest.approx([2.48, 1.99])


def test_irrelevant_information_cannot_improve_expected_fixed_list():
    from research.planning_v3.recourse import PublicState, RecoursePlanner
    model = Mixture([[.5, .8, .7, .6], [.5, .8, .7, .6]], [.5, .5])
    planner = RecoursePlanner(model, (2,), 2)
    state = PublicState(4, 2, frozenset({0}), ((0, 0),))
    values, _ = planner.evaluate_actions(state, [(), (1,)])
    assert values == pytest.approx([2., 2.])


def test_misleading_dependence_can_reverse_realized_policy_value():
    assumed = Mixture([[0, .01, .99, .01, .99], [1, .99, .01, .99, .01]], [.5, .5])
    truth = Mixture([[0, .99, .01, .99, .01], [1, .01, .99, .01, .99]], [.5, .5])
    expected = float(truth.mu[0])
    predicted = float(assumed.mu[0])
    for labels, mass, q in assumed.label_branches((0,)):
        chosen = sorted(range(1, 5), key=lambda i: (-float(q @ assumed.p[:, i]), i))[:2]
        true_q = next(tq for ty, tm, tq in truth.label_branches((0,)) if ty == labels)
        expected += mass * sum(float(true_q @ truth.p[:, i]) for i in chosen)
        predicted += mass * sum(float(q @ assumed.p[:, i]) for i in chosen)
    assert predicted == pytest.approx(2.48)
    assert expected == pytest.approx(.52)


def test_no_time_for_recourse_retains_only_direct_pending_reward():
    from research.planning_v3.recourse import PublicState, RecoursePlanner
    planner = RecoursePlanner(Mixture([[.7, .9, .8]], [1]), (2,), 2)
    state = PublicState(1, 2, frozenset({0}), ((0, 1),))
    values, _ = planner.evaluate_actions(state, [(), (1,)])
    assert values == pytest.approx([.7, .7])
