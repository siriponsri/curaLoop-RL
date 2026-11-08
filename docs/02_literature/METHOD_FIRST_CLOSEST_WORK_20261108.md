# Focused method-first review and novelty challenge

**M0 review record.** The [executed M1 follow-up](../03_research/LR_M12_M1_RESULTS_20261108.md)
adds a formal robust-regret reduction, selected full-method MCTS-SPIBB inspection
and rollout-confidence allocation prior art. It concludes insufficient method
distinction; conditional M2 was not run. Inspection scopes in the table below
describe the earlier M0 review, not the expanded M1 reading.

Date: 8 November 2026, Asia/Bangkok. Bounded public primary-source review;
not a systematic review or a claim that every 2026 method was covered. No
assay-source endpoint, project row, private PDF or protected outcome was accessed.
Owner Deep Research is a source lead; its opaque chat references are not citations.

## Closest work and consequences

| Primary work | Inspected scope | Established overlap | Consequence for the candidate |
| --- | --- | --- | --- |
| [Jiang et al., ICML 2017, ENS](https://proceedings.mlr.press/v70/jiang17d.html) | Official record and selected PDF introduction/methods, especially the remaining-budget approximation; no reproduction | Budget-aware nonmyopic binary active search already exists, including computational approximation/pruning | Neither full-budget planning nor improved discovery relative to myopic Greedy is novel by itself |
| [Petrik, Chow and Ghavamzadeh, 2016](https://arxiv.org/abs/1607.03842) | Primary preprint PDF, introduction, robust-regret formulation and selected approximate-method passages; journal/version equivalence not asserted | Within-model return difference against a baseline, robust improvement and fallback are established | The prototype objective is an adaptation. Finite horizon or a different application alone does not establish a new algorithm |
| [Laroche et al., ICML 2019, SPIBB](https://proceedings.mlr.press/v97/laroche19a.html) | Official abstract and PDF introduction only | Baseline bootstrapping under uncertainty is established for batch RL | Compare assumptions and adaptations; the prototype has no offline occupancy-count guarantee |
| [Castellini et al., ICML 2023, MCTS-SPIBB](https://proceedings.mlr.press/v202/castellini23a.html) | Official abstract only; appendix/code not inspected | Online tree search for safe policy improvement is established | Tree-search safety/scalability cannot be advertised as a new combination without a stronger distinction |
| [Kirschner et al., AISTATS 2020, DRBO](https://proceedings.mlr.press/v108/kirschner20a.html) | Official abstract/metadata only | Distributional context uncertainty and robust optimization are established | Robust context/model language is not a novelty argument; its optimization objective differs from cumulative binary discovery |
| [Nguyen et al., ICML 2021, multifidelity search](https://proceedings.mlr.press/v139/nguyen21f.html) | Official record/abstract; no full-method reproduction in this task | Budgeted cheap/expensive information allocation is established | An eventual multifidelity extension must compare objective-matched controls and cannot be the present data-ready claim |
| [Micheli et al., AISTATS 2025, continuous-context DRBO](https://proceedings.mlr.press/v258/micheli25a.html) | Official search metadata/abstract lead only | Context-distribution robustness is an active established direction | Detailed overlap remains unresolved; do not claim no prior continuous-context method exists |

The mathematical and implementation implications above are our assessment of
the inspected scopes. They do not transfer any external theorem or result to
CuraLoop. The prior AssayMatch and PCAM access limitations remain documented in
[the earlier adoption record](../03_research/DEEP_RESEARCH_ADOPTION_20261108.md);
no stopped resolver was retried or paid article purchased.

## Candidate selection

- **Generic paper-evidence VOI:** not selected as the mandatory core. Established
  decision-region/VOI theory and missing natural source-only uncertainty make
  renaming this a new controller unconvincing; paired-context qualification
  currently dominates the work.
- **A newly trained RL controller:** not selected for this design. No learned
  controller evidence or adequate training/generalization programme is available;
  earlier stronger-predictor results must not be credited to a controller.
- **Computation-bounded baseline-relative rollout:** selected as an executable
  method candidate to challenge, not a certified novelty claim. Existing binary
  tasks can exercise its objective without a new continuous multi-context dataset.

## Novelty decision and falsification

**NOVELTY_HOLD_PRIOR_ART_OVERLAP.** Robust regret/fallback and nonmyopic search
are covered. Shared exact tails and interruption-aware retention are concrete
implementation mechanisms, but are insufficient alone to claim algorithmic novelty.

The potentially useful research distinction is a demonstrably better computation/
discovery frontier for posterior-coupled active search under predictive ambiguity.
It needs an efficient construction with justified uncertainty and advantages over
an established robust adaptation given identical caches, predictor and compute.
The constructed reference supplies neither molecular evidence nor that advantage.

Reject the candidate method claim if a standard robust policy-improvement
adaptation with the same cache and budget reproduces the behavior/tradeoff, if
benefits disappear with a strong matched predictor, if all meaningful regimes
fall back, or if credible scenario construction is computationally impractical.
Model-set failure must remain visible; passing finite-model algebra does not
make a recommendation reliable outside that model set.

This owner instruction authorizes method design and correction of old planning
documents. It does not authorize forcing a positive novelty finding or switching
the paper back to benchmark publication if this candidate fails. Next evidence
needed: mathematical reduction audit plus a bounded exposed-data adapter/scaling
comparison under a separately specified resource/data grant.
