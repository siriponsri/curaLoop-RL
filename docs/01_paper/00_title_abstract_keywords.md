# Title, design abstract and contribution

**METHOD_FIRST_M1_NEGATIVE_CHECKPOINT; NOT_SUBMISSION_READY.** The current
candidate has an executed small-pool adapter, but no molecular efficacy evidence. Historical
studies remain separate; neither benchmark publication nor software features
substitute for the requested method contribution.

## Conditional working title

CuraLoop: Computation-Bounded Molecular Active Search under Predictive-Model Ambiguity

The title is a research direction, not a finding of a new or superior algorithm.

## Design abstract

Molecular active search must allocate measurements and planning computation
while its predictive model remains uncertain. We propose to investigate a
baseline-relative rollout controller that evaluates deviations from a common
Greedy policy across declared predictive models, retains only completed favorable
comparisons and returns the baseline when further planning is unsupported or
interrupted. A small exact reference implements shared Greedy continuation traces
and distinguishes robust from mixture-expected scores. Constructed checks expose
both useful nonmyopic behavior and conservative fallback, and include a failure
when the true outcome lies outside the declared model set. These checks do not
establish molecular performance, calibration, real-world safety or algorithmic
novelty. Robust baseline improvement and nonmyopic active search are established
prior art; a substantive distinction remains to be demonstrated. Existing HIV,
Tox21 and FS-Mol resources are intended for later controlled evaluation with
matched predictors, cache access, measurement budgets and computation accounting.
Historical unfavorable planning results are retained as counterevidence. A
subsequent LR-M12 M1 investigation executed a delivered-information GP adapter,
17 constructed checks and 36 planning timing calls in 12 cases on two previously
exposed FS-Mol assays. Both method revisions retained strong prior-art overlap;
the confidence variant selected Greedy in all cases under its paired-trace cap.
This failed the transition gate, so M2 molecular comparisons were not run.
Predictive calibration and independent novelty review remain unresolved.
The product direction is an auditable R&D evidence/plan/report plugin,
whose workflow value requires separate evaluation.

## Intended contribution and present evidence

The intended contribution is a defensible acquisition method evaluated on
existing benchmarks. Current evidence is an executable mechanism adaptation and
focused novelty challenge, followed by a negative M1 gate, not a new benchmark,
proven new algorithm or finished results paper. See [M1 report](../03_research/LR_M12_M1_RESULTS_20261108.md),
[design](../03_research/METHOD_FIRST_DESIGN_20261108.md) and
[closest work](../02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md).

## Keywords

Molecular active search; predictive-model ambiguity; rollout; computation budget;
baseline-relative decision making; reproducibility.
