# Proposed final study: pending-aware screening

**Final-study status: NOT_FROZEN / NOT_RUN.** The [research protocol](../03_research/PROTOCOL.md), [candidate audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md) and [estimation sensitivity](../03_research/DESIGN_SENSITIVITY_V1.md) distinguish this future independent-family study from the completed NCATS development campaigns reported in Chapter 5. No final compound outcome values were inspected during preparation.

The primary study compares pending-aware and matched pending-blind acquisition on multiple eligible biological tasks under a fixed simulated deadline. Conditions vary duration heterogeneity and capacity while matching the candidate pool, initial knowledge, predictor and operational random realization. The primary endpoint is newly delivered active assay labels by the deadline. Time/budget discovery curves, active scaffold coverage, failure rates and computational overhead are secondary endpoints.

Task families are separated into controller development, validation and final evaluation. The engineering pilot is used to identify defects and estimate resources, not to establish the final generalization claim. The owner selected 12+ biological families and effect estimates with uncertainty, without a confirmatory material-effect threshold. Exact roles, eligibility, primary contrast, family weighting, interval procedure, repeats, failure/stopping rules and a numeric CPU cap must be frozen before final outcome access. Missingness is introduced as a separate sensitivity condition with a declared mechanism.

The baseline set includes Random, retrained Greedy, frozen-model Greedy, nearest-delivered-hit similarity, structural diversity, uncertainty with an explicit model, a simple exploration mixture and an asynchronous acquisition method matched to multi-hit retrieval. The final strong fixed policy is selected on development tasks only. A learned controller is evaluated only after its decisions can be audited. All fallback and infeasible-action counts remain visible. A method that always falls back is not treated as evidence for learned transfer.

The current estimation proposal averages paired repeats within tasks and tasks within families, then weights families equally, with uncertainty that respects that hierarchy. It requires adjudicated families and cannot infer independent units from a convenient group count. Ablations remove pending and deadline information and separate predictor changes from policy changes. Tiny enumerated scenarios first establish that scheduling choices can affect the endpoint. Uniform-delay invariance is checked explicitly.

If the study finds no useful adaptive gain, the paper will report that result and identify the tested regimes. If the simulator cannot express a relevant decision tradeoff, the implementation must change before evaluating policies. If too few eligible tasks remain, the population and conclusion will be narrowed rather than inflated through extra seeds.

## Initialization, metrics and objective amendments

Primary starts are uniformly sampled without inspecting activity; zero-active starts remain eligible. A conditional-known-hit sensitivity follows a different initial-information distribution and is reported separately. The task registry preserves assay ID, functional phenotype, source release and eligibility attrition. LIT-PCBA's target ascertainment and unresolved description conflicts must be addressed before freezing tasks.

Report exact enrichment definitions and predictor-update cost. The simulator's assay clock and measured policy compute are separate unless a compute-aware scenario is explicitly defined. Best-observed-value EI is not automatically suitable for accumulating additional Boolean actives. [Baseline specification](../03_research/BASELINE_SPECIFICATION.md) and [metric concordance](../02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md) govern the design. Six inexpensive controls and the Gaussian adapter have development execution evidence; a calibrated Bernoulli model, fixed mixture, within-batch conditioning and learned transfer remain open. These documents do not freeze a final comparison catalogue.


## Eligibility dependencies

Twenty completed/reused panel feature audits span 17 provisional planning
groups, including 14 human-annotated groups; quarantining mixed-endpoint CYP2C9
leaves 13. These are not certified independent families. Three additional panel
structure audits stopped at the prespecified payload cap. The earlier source
census and bounded gene search offer additional candidates, but exact file
rights, endpoint semantics, full-pool/cross-group chemical overlap and source
dependence remain unresolved. No final-ready task or validation/final role has
been assigned. Further attrition must be reported rather than repaired by
opening outcomes or relabelling related tasks. Development HIV/AhR/PPAR-gamma/
p53 resources cannot become untouched final holdouts.
