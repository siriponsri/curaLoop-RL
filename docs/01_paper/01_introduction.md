# Introduction

The current research objective is a method for molecular active search evaluated
on existing assay tasks. Candidate selection consumes a measurement budget, while
lookahead consumes computation and depends on a predictive model that can be
wrong. A useful method must improve a discovery/compute tradeoff over strong
matched controls and explain which mechanism creates that improvement.

The [current design](../03_research/METHOD_FIRST_DESIGN_20261108.md) examines
baseline-relative predictive-scenario rollout. The [primary-source review](../02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md)
finds close overlap with established robust policy improvement and nonmyopic
active search. The exact constructed reference is therefore a mechanism candidate
and adaptation, not an established novel algorithm. Generic caching and an agent
wrapper are insufficient novelty claims.

Historical work supplies useful counterevidence: complete controller fallback,
null/unfavorable pending-aware comparisons and later gains substantially explained
by a stronger predictor. Those results remain recorded, not relabeled as evidence
for the new method. The unchanged historical methods/results chapters below
describe their own populations and protocols.

New real-data comparisons require a credible predictive-scenario adapter, matched
predictor/update/cache access, explicit measurement/compute accounting and preserved
exposure/protected outcomes. A new benchmark publication is not the selected
fallback. The R&D plugin is a separate application path whose factual and workflow
benefit must be assessed independently.
