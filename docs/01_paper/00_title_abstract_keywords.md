# Title, design abstract and contribution

**METHOD_FIRST_DESIGN_DRAFT; NOVELTY_HOLD; NOT_SUBMISSION_READY.** The current
candidate has a constructed reference, not molecular efficacy evidence. Historical
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
scalable predictive-scenario adapter and real-data method comparison remain
unexecuted. The product direction is an auditable R&D evidence/plan/report plugin,
whose workflow value requires separate evaluation.

## Intended contribution and present evidence

The intended contribution is a defensible acquisition method evaluated on
existing benchmarks. Current evidence is an executable mechanism adaptation and
focused novelty challenge, not a new benchmark, proven new algorithm or finished
results paper. See [design](../03_research/METHOD_FIRST_DESIGN_20261108.md) and
[closest work](../02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md).

## Keywords

Molecular active search; predictive-model ambiguity; rollout; computation budget;
baseline-relative decision making; reproducibility.
