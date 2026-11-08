# CuraLoop positioning after M1: primary literature review

8 November 2026, Asia/Bangkok. **DISCUSSION REVIEW ONLY.** Owner requested web
search and reading of the existing literature folder before choosing another
direction. No new scientific release, labels, campaign, SSH, method revision or
phase transition. LR-M12 stays closed. Recommendations below are proposals.

## Assessment

The literature supports a distinction between an original acquisition algorithm
and a useful, original computational strategy built with established components.
It does not support treating a combination of active learning, an agent, a budget,
robustness and provenance as novel by itself. CuraLoop currently has stronger
engineering evidence than evidence for either kind of research contribution.

The specific M1 robust objective should remain an established-method adaptation.
The negative M1 transition is retained. Its small diagnostic allocation does not
establish that nonmyopic molecular selection lacks value, that every predictor is
inadequate, or that the broader product/research programme must be abandoned.

## What was actually read

This is a targeted, single-reviewer search, not a systematic review or independent
novelty certificate. Primary sources and raw extracted paper text were preferred;
generated discovery descriptions were leads only. Search themes were molecular
active search, acquisition adaptation, compute/discovery tradeoffs, robust
baseline improvement, metareasoning, scientific planning frameworks and agents.

Local reading covered the 28-record `literature_manifest.json`,
`REVIEW_METHOD.md`, `NOVELTY_AND_COMPARATORS.md`,
`REDESIGN_DEEP_REVIEW_20261105.md`,
`METRIC_AND_INITIALIZATION_CONCORDANCE.md`, and the retained M0/M1 reports.
These documents were read as prior analyses, not substituted for paper methods.

**Local PDF-original access remains unresolved.** The current
`docs/02_literature` and `papers` folders contain registers, citations and review
documents. No R01-R28 original PDFs were found in them or the inspected research
PDF locations. The historical register describes copies held outside the public
payload; it does not prove those copies are available in this checkout. The owner
has been asked for the intended literature-folder path. Do not claim all 28 PDFs
or 731 pages were reread. Dataset/masked-method PDFs elsewhere in the project
were not opened to fill this gap.

Fresh source access was uneven: selected raw MolPAL, adaptive-acquisition, BMPS,
ALF and two 2026 preprints were read through alphaXiv; ANS, Query Matters,
ChemCrow and PaperQA2 had accessible primary HTML. ENS's primary record was
refreshed and its detailed M1 review retained. GLARE's official abstract and PDF
opening were accessible, but later full-method requests timed out; one stalled
owned local download was stopped. BayBE's publisher request returned 403; current
publisher-indexed text and the official paper repository were inspected, with
the earlier local full-text review retained separately. No access control was
bypassed and unavailable text is not classified as newly read full text.

## Closest work: objective, mechanism and limits

| Source and inspected scope | What is already occupied | Consequence for CuraLoop |
| --- | --- | --- |
| R04: [MolPAL](https://arxiv.org/abs/2012.07127), inspected v1 preprint methods/results/conclusion; associated Chemical Science paper is 2021 | Model-guided pool screening; surrogate/acquisition/batch comparisons; strong Greedy and large-library docking recovery | A retrained predictor plus Greedy is a serious baseline. Docking-score top-k recovery is not discovery of measured binary assay actives. A useful application/strategy need not begin with a new fundamental acquisition formula. |
| R27: [Query Matters](https://pmc.ncbi.nlm.nih.gov/articles/PMC13014458/), JCIM 2026; Experimental Section, hit definition, results and conclusions | Simulated DMTA with an RF, greedy/uncertainty/guided-random/hybrid queries in a BRD4 scaffold-focused pool | Its uncertainty result is conditional on this setup. Its top-50 predicted-list hit assessment against docking-defined hits is not cumulative newly delivered actives. Do not import its percentage as a target for CuraLoop. |
| [ENS](https://proceedings.mlr.press/v70/jiang17d.html), ICML 2017; current record plus retained M1 objective/method reading | Remaining-budget-aware cumulative-positive discovery and an efficient approximation | Planning beyond Greedy and budget awareness already exist. The M1 horizon-four rollout is not an ENS reproduction or full-remaining-budget method. |
| [ANS](https://arxiv.org/html/2405.15031v1), 2024 preprint; Sections 3-5 and experimental table | Imitation of ENS using synthetic training, transferring a cheaper nonmyopic policy to real tasks; measured targets/time frontier | Cheap or learned nonmyopic decisions are not an untouched gap. Starts contain a known positive and negative; compare uniform/zero-hit starts separately. Count offline training and preprocessing when making resource claims. |
| R28: [Adaptive Acquisition](https://arxiv.org/abs/1906.11471), IJCAI 2019; raw method pages, state/action/reward and evaluation passages | Reinforcement feedback learns an acquisition policy from a heuristic-filtered candidate set | An adaptive controller choosing acquisitions is established. Vision prediction-oriented AL is adjacent evidence, not an objective-matched molecular hit-search baseline. |
| R07: [GLARE](https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html), NeurIPS 2025; official abstract/opening only in this pass | Reinforced molecular active selection and learned balancing of chemical criteria | Broad RL-based molecular acquisition claims are occupied. Its initialization, exact policy action and complete compute accounting need the full paper before defining an exact reproduction. No headline EF number is transplanted. |
| [BMPS](https://arxiv.org/abs/1711.06892v3), UAI 2018; raw metalevel-MDP and application/overhead passages | Select/stop computations using expected decision utility minus computation cost | "When to think versus act" is established metareasoning. A molecular adaptation must identify a useful difference and include controller overhead; generic compute gating cannot be the entire novelty argument. |
| [Robust baseline regret](https://arxiv.org/abs/1607.03842), 2016; retained M1 Section 3/equation 2 reduction | Within-model return difference, worst-case improvement and zero-valued baseline | Keep the M1 reduction. Relabeling its min-over-model score as a new acquisition principle would be unsupported. MDP guarantees do not transfer to an uncalibrated finite GP forecast. |
| R26: [BayBE](https://doi.org/10.1039/D5DD00050E), Digital Discovery 2025; indexed publisher text, [official paper repository](https://github.com/emdgroup/baybe-paper), retained earlier full-text review | Modular experimental planning, chemical encodings, asynchronous workflows, serialization and practical extensions | Integration with an existing planner deserves consideration. New connectors or local report export alone are not a demonstrated method advance or a cleared commercial advantage. Current full-paper refresh is incomplete. |
| R08: [ALF](https://arxiv.org/abs/2609.31197), September 2026 preprint; architecture, Section 4 and Appendix F | A common offline/online acquisition API with interchangeable dataset/model/acquisition/search/oracle components | A generic scientific active-learning framework is occupied. The reported campaigns use computational stand-ins and a synchronous complete-feedback loop; that source-specific limit does not establish a field-wide delayed-feedback gap. |
| [ChemCrow v2](https://arxiv.org/html/2304.05376v2) and [PaperQA2 v2](https://arxiv.org/html/2409.13740v2), selected methods/evaluation passages | Chemistry tool use, cited literature synthesis, source-fidelity assessment and abstention-oriented evaluation | "Search papers, call molecular tools, write a cited report" is an established agent pattern. Evaluate the correctness of source-to-decision handoffs and actual effort separately from answer fluency or connector count. Do not mix ChemCrow preprint and journal tool inventories. |

These descriptions concern inspected versions and author-reported findings. No
published result was independently reproduced in this review.

## What apparently conflicting acquisition results really imply

MolPAL's strong Greedy result and Query Matters' favorable uncertainty result do
not identify a universal winner. They differ in target space, training population,
surrogate, labels, budget and endpoint. The latter focuses on a constrained BRD4
chemical space with docking as pseudoexperimental feedback. Inference: useful
research should explain the conditions under which a decision strategy earns
its extra cost, rather than demand a single policy beat all alternatives.

ANS is a particularly important challenge to a cheap-planning claim: its paper
already reports discovery versus decision time. A Pareto plot alone would be an
evaluation format, not the missing contribution. The mechanism creating any new
frontier must survive a strong predictor, ordinary rollout, a cheap policy,
matched caches and an equally informed simple switching rule.

## Two new close leads and why their limitations matter

[PRISMS](https://arxiv.org/html/2610.01827v1), October 2026 preprint, combines
pairwise ranking information through a Bradley-Terry graph model and escalates
queries using a Fisher-information criterion. Selected Sections 3/4.1 and
Appendix A were inspected. Its main drug-screening experiments reveal historical
labels, and the higher-fidelity ranker is principally a 75%-accurate simulated
oracle made by perturbing ground-truth comparisons. The limited agentic-ranker
case is not equivalent to a complete prospective drug-discovery validation.
Inference: multi-source/agent-assisted prioritization is already an active area;
the existence of this preprint neither validates CuraLoop nor requires copying
its synthetic oracle. Recreating its ranking channel would change our data and
information contract and is not authorized here.

[Budget-Constrained Compound Library Prioritization](https://arxiv.org/abs/2606.26624),
June 2026 preprint, presents static risk-annotated Top-k selection, conformal
intervals, leakage checks and auditable export around a 2D activity proxy.
Selected formulation/data/control/limitation sections were inspected. Its
target-free aggregate activity proxy and static ranking differ from a
task-specific sequential binary assay campaign. The paper explicitly limits its
RF/Chemprop comparisons and reports one full training fold; its existence is
not evidence that those scientific choices are sufficient or accepted by a journal.
Inference: generic "risk-aware, auditable pre-screening" is also not an empty
positioning category. A declared limitation is a boundary on claims, not an
automatic defect or an automatic opportunity for us.

## Current standing versus possible research standing

| Proposed description | Current assessment |
| --- | --- |
| A novel general RL acquisition algorithm | UNSUPPORTED. Existing learned-acquisition literature is close; CuraLoop has no new learned-policy evidence in M1. |
| A novel robust baseline-improvement objective | UNSUPPORTED. M1's algebraic overlap remains. |
| A proven molecular discovery/compute improvement | NOT_ESTABLISHED. M1 measured isolated calls, not sequential discovery effects. |
| A local auditable retrospective decision workbench with an offline evidence/report workflow | IMPLEMENTED_SCOPE, with historical verification. Useful engineering capability; business demand and new-method integration remain untested. |
| A molecular computational strategy that selectively spends prediction/planning effort when useful | PLAUSIBLE_RESEARCH_POSITION_ONLY. Metareasoning/ENS/ANS are close prior art; the exact distinct mechanism and benefit still need evidence. |
| A new public benchmark publication | NOT_SELECTED_BY_OWNER. Existing datasets remain evaluation instruments. |

The most defensible research discussion is therefore about a **specific,
testable molecular decision strategy**, with the existing robust rollout retained
as a control or component. There is no evidence-based reason to market the
current min-over-model formula itself as the central invention.

A possible question, not a selected new goal, is: can information available at
decision time identify when extra predictor/planning computation improves
cumulative assay discovery enough to justify its overhead, relative to a strong
fixed policy, always-plan policy and a cheap switching control under the same
information and resource access? A meaningful answer could be a useful
computational strategy if its mechanism and findings are substantive. This
review does not certify that question as novel or promise positive results.

Avoid a new circular gate: provisional differentiation and executable fair
controls establish readiness to test; the subsequent development comparison
establishes empirical value. Neither should be mislabeled publication readiness.
Changing the approved gate still requires the owner, and the old M1 observations
or verdict must not be rewritten to make a new gate appear historically passed.

## Journal and product implications

The [JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope) covers
theory and applications and distinguishes novel methods or innovative
computational strategies, for which appropriate retrospective validation may
suffice; prospective validation is encouraged. Inference: a new fundamental
algorithm/theorem is not the only possible route, but a familiar pipeline without
a substantive computational or scientific contribution is not thereby qualified.
This is a venue-fit interpretation, not editorial assurance or acceptance advice.

For product work, an evidence-to-decision layer could integrate an established
planner and measure source fidelity, recovery, abstention, reproducibility and
analyst effort. Compare with ordinary tools and existing frameworks. A product
can have practical differentiation without an algorithmic novelty claim; there
is currently no customer or measured workflow advantage established here.

## What remains before a firm owner decision

1. Resolve the owner's literature-folder path and reread the actual available
   PDFs, especially GLARE, BayBE and the supplied R05 version/supplement. Do not
   purchase missing papers or retry stopped publisher endpoints automatically.
2. Agree one contribution statement and the exact prior-art difference being
   tested. Decide whether the intended claim is an algorithm or a computational
   strategy. No new dataset publication is required by that distinction.
3. If the owner later releases a development comparison, freeze the candidate,
   objective, permitted data, controls and accounting first. Preserve null and
   harmful results. Keep protected outcomes and the closed LR-M12 budget closed.

No new M1/M2 goal, dataset expansion or experiment is launched by this review.
