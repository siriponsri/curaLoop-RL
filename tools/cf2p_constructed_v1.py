"""Twelve exact, hand-constructed mechanism checks. No data or model fitting."""

import json
import math
import sys
from fractions import Fraction as F
from itertools import combinations, product

from cf2p_admin_v1 import PUBLIC, write


def coverage(selected, outcome, groups):
    return len({groups[i] for i in selected if outcome[i]})


def expected(selected, distribution, groups):
    return sum(p * coverage(selected, y, groups) for y, p in distribution)


def independent(probabilities):
    return [(y, math.prod(p if v else 1 - p for p, v in zip(probabilities, y)))
            for y in product((0, 1), repeat=len(probabilities))]


def main():
    cases = []
    def record(key, claim, **values):
        cases.append({"id": key, "status": "PASS", "claim": claim,
                      "values": {k: float(v) if isinstance(v, F) else v for k, v in values.items()}})

    iid = independent([F(2, 5), F(2, 5)])
    correlated = [((0, 0), F(3, 5)), ((1, 1), F(2, 5))]
    assert expected((0, 1), iid, (0, 0)) == F(16, 25)
    assert expected((0, 1), correlated, (0, 0)) == F(2, 5)
    record("C01", "Identical marginals do not identify joint group coverage", independent=F(16, 25), perfectly_correlated=F(2, 5))

    def with_b(base):
        return [(tuple(y) + (b,), p * (F(3, 10) if b else F(7, 10))) for y, p in base for b in (0, 1)]
    positive = with_b(correlated)
    negative = with_b([((1, 0), F(2, 5)), ((0, 1), F(2, 5)), ((0, 0), F(1, 5))])
    g = (0, 0, 1)
    assert expected((0, 1), positive, g) < expected((0, 2), positive, g)
    assert expected((0, 1), negative, g) > expected((0, 2), negative, g)
    record("C02", "Same marginal predictions can reverse the optimal two-item batch", same_group_positive=F(2, 5), same_group_negative=F(4, 5), cross_group=F(7, 10))

    distribution = [((0, 0, 0, 0), F(1, 4)), ((1, 1, 0, 1), F(1, 2)), ((0, 1, 1, 0), F(1, 4))]
    groups = (0, 0, 1, 2)
    subsets = [set(c) for k in range(5) for c in combinations(range(4), k)]
    tests = 0
    for a, b in product(subsets, repeat=2):
        if a <= b:
            for i in set(range(4)) - b:
                assert expected(a | {i}, distribution, groups) - expected(a, distribution, groups) >= expected(b | {i}, distribution, groups) - expected(b, distribution, groups)
                tests += 1
    record("C03", "Static expected coverage stays submodular under an arbitrary fixed joint law", checked_marginal_inequalities=tests)

    coupled = [((0, 0), F(1, 2)), ((1, 1), F(1, 2))]
    prior_gain = expected((1,), coupled, (0, 1))
    success_mass = sum(p for y, p in coupled if y[0] == 1)
    conditioned = [(y, p / success_mass) for y, p in coupled if y[0] == 1]
    conditional_gain = expected((0, 1), conditioned, (0, 1)) - expected((0,), conditioned, (0, 1))
    assert conditional_gain == 1 > prior_gain == F(1, 2)
    record("C04", "Static submodularity does not imply adaptive submodularity: a positive in one group raises another group's conditional gain", prior_other_group_gain=prior_gain, conditional_other_group_gain=conditional_gain)
    observed = (1, 0)
    world_a, world_b = observed + (0,), observed + (1,)
    assert world_a[:2] == world_b[:2] and sum(world_a) != sum(world_b)
    record("C05", "Primary-hit-only observations do not identify full-library outcomes", observed_confirmed_positives=1, compatible_full_library_totals=[1, 2])

    for outcome in product((0, 1), repeat=3):
        assert coverage((0, 1, 2), outcome, (0, 1, 2)) == sum(outcome)
    record("C06", "One selected item per group makes D equal H without a second independent achievement", outcome_patterns=8)

    distribution = independent([F(9, 10), F(9, 10), F(1, 100)])
    quota = expected((0, 2), distribution, (0, 0, 1))
    same_group = expected((0, 1), distribution, (0, 0, 1))
    assert quota == F(91, 100) < same_group == F(99, 100)
    record("C07", "A one-per-group quota can lose expected positive-group coverage to classical probability-aware selection", quota=quota, probability_aware=same_group)

    distribution = independent([F(9, 10), F(4, 5), F(7, 10)])
    d_top = expected((0, 1), distribution, (0, 0, 1))
    d_spread = expected((0, 2), distribution, (0, 0, 1))
    h_top, h_spread = F(17, 10), F(8, 5)
    assert h_top > h_spread and d_top < d_spread
    record("C08", "A classical hit/coverage tradeoff exists with independent labels", top_H=h_top, top_D=d_top, spread_H=h_spread, spread_D=d_spread)
    assert h_top + F(1, 10) * d_top > h_spread + F(1, 10) * d_spread
    assert h_top + d_top < h_spread + d_spread
    record("C09", "Preference weights change the chosen portfolio; a toy weight is not an owner-approved material-effect criterion", illustrative_weights=[0.1, 1.0])

    primary, confirmation = (F(9, 10), F(4, 5)), (F(1, 10), F(7, 10))
    assert primary[0] > primary[1] and confirmation[0] < confirmation[1]
    record("C10", "Correcting primary-to-confirmation calibration can change ranking without creating a new optimizer", primary_top_confirmation=confirmation[0], calibrated_top_confirmation=confirmation[1])
    for outcome in product((0, 1), repeat=4):
        labels = [1 + groups[i] if y else 0 for i, y in enumerate(outcome)]
        utility = sum(min(1, labels.count(c)) for c in (1, 2, 3))
        assert utility == coverage(range(4), outcome, groups)
    record("C11", "Known-group binary confirmation coverage embeds in a multiclass diminishing-returns utility", checked_outcome_patterns=16, utility="sum_g min(1, positive_count_g)")

    worlds = [((0, 1, 0), F(1, 2)), ((1, 0, 1), F(1, 2))]
    static_best = max(sum(p * sum(y[i] for i in s) for y, p in worlds) for s in combinations(range(3), 2))
    adaptive = sum(p * (y[0] + (y[2] if y[0] else y[1])) for y, p in worlds)
    assert adaptive == F(3, 2) > static_best == F(1)
    record("C12", "Feedback can have value under a known joint model; this does not distinguish the mechanism from Bayesian active search", adaptive=adaptive, static=static_best)
    assert len(cases) == 12
    result = {"status": "PASS_TWELVE_CONSTRUCTED_FALSIFICATION_CASES", "molecular_data_used": False,
              "model_fits": 0, "final16_access": False, "cases": cases,
              "interpretation": "Exact illustrative mechanism checks, not empirical utility, novelty proof or a new algorithm evaluation"}
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    assert tag in ("v1", "v2")
    write(PUBLIC / f"constructed-falsification-{tag}.json", result, True)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
