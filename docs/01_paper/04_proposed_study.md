# Proposed study: pending-aware screening

**Status: NOT_RUN.** The definitive implementation protocol is [Research protocol](../03_research/PROTOCOL.md), supported by data/split, scheduler, experiment and analysis specifications. This chapter describes planned work and is not a results section.

The primary study compares pending-aware and matched pending-blind acquisition on multiple eligible biological tasks under a fixed simulated deadline. Conditions vary duration heterogeneity and capacity while matching the candidate pool, initial knowledge, predictor and operational random realization. The primary endpoint is newly delivered active assay labels by the deadline. Time/budget discovery curves, active scaffold coverage, failure rates and computational overhead are secondary endpoints.

Task families are separated into controller development, validation and final evaluation. The engineering pilot is used to identify defects and estimate resources, not to establish the final generalization claim. Exact task roles, inclusion rules, primary contrast, material effect, repeats and stopping criteria are frozen before inspecting the final evaluation. Missingness is introduced as a separate sensitivity condition with a declared mechanism.

The baseline set includes Random, retrained Greedy, frozen-model Greedy, nearest-delivered-hit similarity, structural diversity, uncertainty with an explicit model, a simple exploration mixture and an asynchronous acquisition method matched to multi-hit retrieval. The final strong fixed policy is selected on development tasks only. A learned controller is evaluated only after its decisions can be audited. All fallback and infeasible-action counts remain visible. A method that always falls back is not treated as evidence for learned transfer.

The analysis estimates paired differences at the task level, with uncertainty that respects families/tasks and repeated seeds. Ablations remove pending and deadline information and separate predictor changes from policy changes. Tiny enumerated scenarios first establish that scheduling choices can affect the endpoint. Uniform-delay invariance is checked explicitly.

If the study finds no useful adaptive gain, the paper will report that result and identify the tested regimes. If the simulator cannot express a relevant decision tradeoff, the implementation must change before evaluating policies. If too few eligible tasks remain, the population and conclusion will be narrowed rather than inflated through extra seeds.

## Initialization, metrics and objective amendments

Primary starts are uniformly sampled without inspecting activity; zero-active starts remain eligible. A conditional-known-hit sensitivity follows a different initial-information distribution and is reported separately. The task registry preserves assay ID, functional phenotype, source release and eligibility attrition. LIT-PCBA's target ascertainment and unresolved description conflicts must be addressed before freezing tasks.

Report exact enrichment definitions and predictor-update cost. The simulator's assay clock and measured policy compute are separate unless a compute-aware scenario is explicitly defined. Best-observed-value EI is not automatically suitable for accumulating additional Boolean actives. [Baseline specification](../03_research/BASELINE_SPECIFICATION.md) and [metric concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md) govern the implementation amendment; neither is an executed result.
