# Novelty and comparator decision

## Claims already occupied by prior art

Iterative model-guided molecular screening, reinforcement-trained acquisition, batch/parallel selection, asynchronous optimization, multi-fidelity resource allocation and modular scientific acquisition frameworks all have prior art in the register. A local web interface is an implementation choice, not an algorithmic contribution. A provenance ledger is useful engineering but needs a comparative research case to support a paper centered on it.

## Candidate contribution

Test a narrow proposition: pending-aware acquisition can change the discovery-versus-time tradeoff under explicitly modelled capacity and duration variation, and its value depends on the task/data regime. The proposed contribution consists of the operational task definition, matched evaluation, empirical regime map and reusable evidence artifacts. A generalizing controller is an additional contribution only if it is actually used and improves a suitable held-out comparison.

## Required comparisons

Compare with a strong fixed policy selected on development data, an exploration/diversity baseline, an asynchronous acquisition method and a simple mixture. For software relevance assess adapters to an existing framework before duplicating infrastructure. Published headline metrics cannot be copied into a new table because datasets, costs, models and objectives differ. If an implementation cannot be reproduced, report the limitation and provide an explicitly named adaptation.

## Paper-route decision

If a new controller consistently adds value with a supported mechanism, consider a methods-centered paper. If it does not, a carefully executed benchmark can explain which conditions favor which policies. If the dominant contribution is a reusable tool with genuine research use, consider a software paper. A polished interface with only the existing HIV fallback benchmark does not yet establish any of these claims.

Before submission refresh the closest-work search and compare exact code versions. A single preprint's limitation does not establish a field-wide gap. Describe contribution as a bounded study result until broader evidence exists.

## Full-text amendment

R03's ascertainment narrows the benchmark population. R05's known-active starts and frozen-model/similarity arms sharpen the controls needed for a low-data claim. R26 confirms that backtesting, asynchronous planning and campaign stopping already exist in practical software. These findings strengthen an objective-matched comparative study and an integration-first assessment. They do not close the novelty search or establish a new controller's advantage. The associated R05 journal version and exact reproduction questions remain explicit in [the version register](VERSION_DISCREPANCIES.md).
