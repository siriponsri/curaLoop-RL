"""Exact expectations for declared illustrative policies, not a new controller."""

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
output = parser.parse_args().output
assert not output.exists()
output.parent.mkdir(parents=True, exist_ok=True)
cases = []
for informative, deadline in itertools.product((True, False), (1, 2)):
    worlds = [(z, z) for z in (0, 1)] if informative else list(itertools.product((0, 1), repeat=2))
    immediate_candidate_hits = Fraction(0)
    wait_candidate_hits = Fraction(0)
    pending_hits = Fraction(0)
    for z, pending_label in worlds:
        # A1 submitted at t=0 delivers at t=1 and reveals Z.
        # At t=1, one remaining unit buys a known-active distinct compound.
        immediate_candidate_hits += Fraction(z + (1 if deadline >= 2 else 0), len(worlds))
        # WAIT retains two units; after P at t=1 two workers are free.
        # Informative P identifies two actives. Otherwise A1+B1 yields one.
        wait_candidate_hits += Fraction(
            (2 if informative else 1) if deadline >= 2 else 0, len(worlds)
        )
        pending_hits += Fraction(pending_label, len(worlds))
    cases.append(
        {
            "pending_label_informative": informative,
            "deadline": deadline,
            "equally_likely_worlds": worlds,
            "expected_new_candidate_hits_immediate": str(immediate_candidate_hits),
            "expected_new_candidate_hits_wait": str(wait_candidate_hits),
            "expected_common_pending_hits": str(pending_hits),
            "expected_H_T_immediate": str(immediate_candidate_hits + pending_hits),
            "expected_H_T_wait": str(wait_candidate_hits + pending_hits),
            "wait_minus_immediate": str(wait_candidate_hits - immediate_candidate_hits),
        }
    )
assert [r["wait_minus_immediate"] for r in cases] == ["-1/2", "1/2", "-1/2", "-1/2"]
result = {
    "status": "PASS_EXACT_ILLUSTRATIVE_EXPECTATIONS",
    "assumptions": "Two workers; one existing pending P completes at1; one worker free at0; remaining uncommitted budget2; A1,A2 active iff Z=1, B1,B2 active iff Z=0. Unit costs/durations, deterministic public turnaround, Z Bernoulli(1/2). Informative P=Z; uninformative P independent Bernoulli(1/2). Delivery at deadline counts; no new dispatch at deadline.",
    "equal_observable_scalar_summaries": "Same queue length/age, capacity, budget, deadline and all marginal activity probabilities. Joint dependence between pending P and candidates differs.",
    "cases": cases,
    "interpretation": "AtT2, posterior content can reverse dispatch/WAIT preference despite equal scalar summaries. T1 favors immediate dispatch. Direct pending reward is counted equally. This is a constructed motivation, not a new-priority theorem, assay result, trained algorithm, universal-optimality claim or selected material-effect threshold.",
    "new_campaigns_models_or_final_outcomes": 0,
}
output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
