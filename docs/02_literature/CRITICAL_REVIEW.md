# Critical review: adaptive screening under operational constraints

## Scope and central finding

This review asks what CuraLoop-RL must contribute beyond an existing model-guided selection loop. The relevant literature spans molecular screening, learned acquisition, asynchronous optimization and scientific software. Taken together, it makes broad novelty claims difficult: selecting molecules iteratively, using RL to guide acquisition, running tasks asynchronously and exposing a modular software API all have prior art. A defensible study must isolate a consequential decision problem and demonstrate what is learned from it.

The proposed direction is a comparative study of confirmed historical hit discovery when experiments remain pending and capacity and deadlines constrain further decisions. That direction is a research hypothesis, not a finding established by the literature search. Its value depends on fair comparisons and on a simulator that actually changes the available decisions when timing assumptions change.

## Assay evidence and benchmark definition

MoleculeNet (R01) establishes datasets, representations, split choices and metrics as parts of a molecular evaluation. TDC (R02) organizes therapeutics tasks and evaluation resources. Both support reuse of public evidence, but their inclusion does not make a custom replay an official benchmark reproduction. A study that changes sampling, labels or split rules must identify the resulting task precisely.

LIT-PCBA (R03, HAL author manuscript inspected) provides experimentally grounded active/inactive screening data and is a candidate source for multiple tasks. Its curation removes several assay artifacts and applies AVE splitting, but also selects target sets partly through baseline virtual-screening performance. That ascertainment restricts the target population and must be disclosed. The reported 15 sets are not automatically 15 independent biological replications or a locally imported registry. The later audit R19 reports identity and analog overlap in particular uses of that benchmark. The appropriate project response is a release-specific audit with disclosed standardization and split rules. Accepting or rejecting an entire dataset by name would avoid the actual question of which overlaps affect a particular evaluation.

GuacaMol (R25) concerns de novo molecular generation. It is useful here chiefly as a boundary: selecting existing molecules for an assay and generating new structures are different search problems. Adding generation would introduce new constraints about validity, novelty and synthesizability without resolving the current controller-transfer limitation.

## Model-guided screening and acquisition choice

MolPAL (R04) studies surrogate models and acquisition strategies for large docking pools, including strong Greedy behavior. Its computational hits are docking-score outcomes. The methodological lesson is to preserve a strong simple baseline and to avoid interpreting a docking advantage as experimental assay efficacy.

The inspected 2024 ChemRxiv v3 study R05 compares six arms on three LIT-PCBA-derived libraries, including nearest-hit similarity and exploitation without retraining. Every initial set is conditioned on a known active. Its results support examining initial knowledge, retraining and acquisition jointly, while providing no test of an unconditional zero-hit start. The associated journal version has not been compared. The supplied supplement's batch-size result is limited to ALDH1, and its plotted standard errors should not be treated as broad cross-target uncertainty. SimDMTA (R27) studies query behavior in a focused BRD4 docking workflow and finds a benefit for uncertainty sampling in that setting. The contrasting study settings make a universal ranking of acquisition policies implausible without a carefully defined population.

For CuraLoop, frozen-model Greedy and nearest-delivered-hit similarity are mandatory controls alongside Random and retrained Greedy. They distinguish the value of newly revealed labels from the value of using a larger predictor or a favorable initial hit. The design consequence is a matched predictor/acquisition comparison before claiming that adaptive control creates the gain. A better predictor, more favorable initial actives or a different batch size can change hit discovery without any contribution from the controller. Predictor quality and campaign utility should be reported separately.

## Learned acquisition and reinforcement learning

R06 links active learning to reinforcement learning for molecular generation, using a surrogate to reduce expensive oracle evaluation. Its action space and objective differ from a fixed historical assay pool. It supplies relevant sample-efficiency concepts but cannot be used as a direct numeric benchmark for CuraLoop's binary retrospective endpoint.

GLARE (R07) is closer: it frames molecular selection through a learned RL policy. The full paper also discusses batch-size and computational-time tradeoffs. CuraLoop therefore cannot establish novelty by asserting that RL or a screening-time tradeoff is absent from earlier work. Its proposed operational study must state a narrower difference and reproduce or adapt a credible comparison.

Learned acquisition is older than these chemical applications. R28 learns acquisition through reinforcement feedback in image tasks. Its relevance is methodological: a fixed set of handcrafted strategies is not the only possible action parameterization. Its success does not establish transfer to scarce-positive biological assays. The existing CuraLoop tables, trained on synthetic tasks and evaluated with complete Greedy fallback on HIV, provide no contrary evidence about transfer.

## Delay, pending work and resource allocation

Delayed feedback has its own established theory (R12). GP-BUCB (R13) explicitly addresses parallel selection and delayed observations. Local penalization (R11) addresses interactions between batch choices, and PLAyBOOK (R10) studies asynchronous operation when workers finish at different times. These sources rule out treating “results arrive later” as a novel optimization setting by itself.

The useful distinction is between rescaling the clock and changing the decision problem. With common delays, equal costs, fixed batches and no deadline, a policy may select exactly the same compounds and merely finish later. Heterogeneous durations and refill decisions can instead alter which labels are available before the next selection. A deadline makes late results relevant to the endpoint. This reasoning is a proposed simulator property to test, not a theorem inferred from a paper title.

Cost and fidelity add another dimension. R14 develops cost-aware multi-fidelity optimization; R15 combines multiple experimental fidelities in drug discovery and includes a prospective platform example. Those results depend on fidelity relationships and the actual experiments used. A binary, single-assay replay must not invent lower-fidelity measurements by adding noise and then claim biological multi-fidelity validation. Keep this extension separate until suitable linked measurements are available.

## Scientific software and integration

BoTorch (R16) provides optimization infrastructure that can support a probabilistic acquisition backend. PAL (R09) already coordinates concurrent active-learning components using MPI. BayBE (R26, publisher PDF inspected; manuscript software version 0.12.2) addresses practical experimental planning and explicitly includes distributed asynchronous workflows, partial measurements, serialization and historical backtesting. Its reaction-yield, transfer and stopping demonstrations show the importance of representation and campaign-level evaluation in those examples. They do not validate binary multi-hit retrieval or a savings percentage for CuraLoop. These alternatives matter both scientifically and commercially: an implementation comparison must acknowledge their capabilities.

ALF (R08) is a 2026 preprint presenting a common modular API for offline and online acquisition. Its inspected Appendix F describes synchronous oracle assumptions and unmodelled delayed/attrited feedback in the reported framework. That is a concrete version-specific limitation, not evidence that all active-learning software lacks asynchronous support. PAL, BayBE and asynchronous BO directly prevent that broader inference.

A stopping objective needs particular care. Optimizing the best measured value and accumulating many positive Boolean assay labels are different tasks. A direct expected-improvement rule can saturate once an active is known; an adaptation must define the value of further hits rather than copy a reaction-yield objective.

The product choice is consequently conditional. CuraLoop may provide a useful local replay, event-audit and reporting layer, or it may be better implemented as an adapter to an established framework. Either route needs an actual user problem and a clear interoperability contract. Another generic acquisition library is not a defensible business position merely because its interface is polished.

## Representations, uncertainty and evaluation

R17 evaluates learned molecular representations, while R18 examines dataset, model, metric and chemical-space evaluation choices. Together they motivate classical fingerprint controls and careful split design. The proposed study should separate a chemical extrapolation question from controller transfer across targets; neither is demonstrated by changing a random seed.

Uncertainty-based acquisition also requires a valid meaning of uncertainty. R22 develops Bayesian active learning in image settings; R23 studies deep-ensemble uncertainty; R24 examines calibration. These methodological sources do not validate a molecular predictor automatically. In CuraLoop, closeness of a single uncalibrated logistic output to 0.5 remains a margin heuristic, and any stronger uncertainty claim requires an explicitly assessed model.

R20 and R21 address evaluation instability and reproducibility in RL. Their implications for this project are methodological rather than biological: report uncertainty, preserve run configurations and expose variation. Twenty seeds on one HIV assay remain repetitions of one task. A claimed cross-target advantage requires independent task-level evidence and uncertainty that respects that structure.

## Metric and version discipline

The additional full texts reveal several comparison hazards. R03 defines early enrichment at a fixed false-positive rate, whereas R05 describes enrichment among acquired compounds. Neither name alone identifies the same denominator as a top-ranked library fraction. A common metric table and exact budget convention are needed before comparing values. The project also records a VDR agonism/antagonism description discrepancy between R05 and its supplement and the preprint's explicit argmin mutual-information direction. These are version-specific questions to resolve against exact data/code, not evidence that the source's labels or implementation are wrong. See [the full-text amendment](FULL_TEXT_REVIEW_ADDENDUM.md) and [the discrepancy register](VERSION_DISCREPANCIES.md).

## Proposed synthesis and remaining gap

The literature supports a demanding but manageable research design. Keep the existing POC as a tested local interface and regression reference. Add a versioned event-time experiment model, matched asynchronous controls and held-out-target evaluation. Make confirmed hits by a fixed simulated deadline the primary endpoint, retain budget-based metrics as secondary and expose failure/fallback shares.

The prospective contribution is an empirical characterization: which combinations of delay variability, capacity and data regime change policy rankings, and whether a controller can exploit those differences on tasks it did not tune against. Positive, null and failure outcomes all inform that characterization. The evidence must distinguish adaptation from model quality and scheduling assumptions.

This package supplies the review, protocol and manuscript groundwork. It does not supply the new multi-target experiment results. Before submission, refresh the literature, inspect exact comparator versions and decide whether the evidence supports a methods paper, a benchmark/software paper or a narrower reproducibility study.

## Sources

Stable source IDs R01-R28 resolve in [the reference register](REFERENCES.md). PDF status and checksums are in [the literature manifest](literature_manifest.json). Source-specific extraction and planned implications are in [the evidence notes](EVIDENCE_NOTES.md).
