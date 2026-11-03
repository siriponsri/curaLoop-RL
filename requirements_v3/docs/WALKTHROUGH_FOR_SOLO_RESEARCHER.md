# Walkthrough: one toy screening campaign

Assume a library of 5,000 candidate molecules with structures visible to software. The retrospective dataset contains assay labels for all 5,000, but the policy **must not see them** until it selects a molecule. An initial common, published seed of 50 assay results is available to all methods. There are 200 simulated assay units for subsequent tests; each confirmed assay costs 1 unit. These numbers are **an explanatory example**, not measured real costs or expected results.

## Round 1

The predictor learns from the common 50 visible results. Policy A greedily selects 10 molecules with high predicted active probability. Policy B selects 10 uncertain molecules. Policy C samples 10 at random. The simulator charges each policy's separate run the same cost and returns actual historical assay labels for those 10 IDs, either instantly or after an optional simulated delay.

## Round 2

Each policy updates *only* with its revealed results, retrains the same predictor type and chooses the next batch. A contextual bandit or RL agent might switch between greedy and uncertainty-based decisions based on its observation: remaining budget, past revealed hit rate, model uncertainty and pending results. It cannot inspect full labels to plan a better batch.

## After 200 units

The evaluator, which is isolated from policies, reads the event log and computes cumulative unique confirmed actives recovered per spent unit; secondary metrics include molecular diversity, total time under delayed-result assumptions, predictor calibration, and runtime. Different policy results may be better or worse. The desired outcome is a credible explanation of *why and when* a policy helps, not a forced positive result.

## Why the Digital Twin idea adds value later

The screening workflow has state: spending, assay queue, pending measurements, throughput and calibration. These features can model changing conditions more realistically than a one-off molecular ranking. However, a simulation of those conditions is *not yet a digital twin*. Only after documented real-world feedback, predictive validation and decision relevance could the project make that transition.

## What to study first

You do not need to know medicinal chemistry to write the first oracle or budget ledger. Learn Python testing, RDKit basic SMILES parsing, binary classification, precision-recall for imbalanced labels, then pool-based active learning. Read the LIT-PCBA original paper and GLARE/SimDMTA/MF-BO before planning any claim of algorithmic novelty.
