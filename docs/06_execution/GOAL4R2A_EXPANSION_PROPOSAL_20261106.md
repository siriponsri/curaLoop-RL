# Dataset and benchmark expansion after the 4R2-A audit

6 November 2026. **PROPOSED_ONLY; EXPANSION EXECUTION NOT_AUTHORIZED.**

The owner invited immediate proposals when the current feasibility audit reveals
a need to expand dataset or benchmark coverage. This document supplies that
proposal while the approved 4R2-A engineering/metadata work continues.

## Recommendation

Prioritise source-version and observation coverage before adding assay counts.
Then use a separate external workflow benchmark to test the complete agent.
MF-PCBA and a molecular-agent benchmark answer different questions; their task
counts must not be pooled as independent biological families.

| Candidate | Purpose | Required work before use | Current disposition |
| --- | --- | --- | --- |
| MF-PCBA historical-source reconstruction and PubChem assay-description metadata for its 60 definitions | Establish source equivalence, endpoints, targets and confirmation relationships | Use the now-available SI version registry; reconcile code, censor qualifiers, stage selection, provider rights and protected-panel exclusion; do not retrieve activity tables yet | Recommended prerequisite; no scientific cohort cleared |
| [MolDesignBench v1](https://arxiv.org/html/2609.27349v1) and [official benchmark repository](https://github.com/KU-AGI/MolDesignBench) | Evaluate interpreting molecular constraints and detecting infeasible requests with an external task source | Pin release, license, tool/runtime contract and fresh evaluation split; verify model/tool quotas before running an agent | Recommended next external workflow benchmark; not confirmation-assay evidence |
| [Autonomous Science Bench v1](https://arxiv.org/html/2610.18449v1) | Evaluate sequential experimental-agent decisions with an authoritative measurement interface | Distinguish replay/twin/live, source rights, hidden evaluation, public-data exposure and resource requirements | Optional subsequent benchmark; defer until the molecular contribution and integration are clearer |

The benchmark papers were inspected as primary publications/preprints during the
proposal review. No external benchmark dataset was downloaded or evaluated by
this expansion proposal. A task source being public does not certify its licence
or suitability for the intended run.

## Why MF-PCBA needs more source work

The [pinned code metadata](../../research/manifests/goal4r2a_mfpcba_metadata_v1.json)
describes 60 script definitions, 54 unique primary AIDs, 60 unique confirmatory
AIDs and nine definitions with the same AID for both stages. Counts began as a
filename-convention projection, not an independent parse of every script body.
The later owner-supplied SI corroborated all 60 pairs in Table S2; Table S19
specifies version/revision/date for all 105 distinct AIDs.
Certified independent biological groups and cleared pilot datasets are both
zero in this audit; the actual eligible counts remain unknown.

Observed source-code differences include median primary aggregation versus the
paper's mean, live unversioned source retrieval, and different default/missing
handling between same-AID and separate-AID paths. These require reconciliation
before claiming paper-exact reconstruction. First-page inspection identified
the initial private owner PDF as the 12-page primary article. The separate
47-page SI was subsequently supplied, and the publication-specific version
tuples are now available. Matching downloaded activity rows to those tuples
remains untested.

Useful bounded metadata-review leads are shared-primary forks:
`1259416 -> 1259418/1259420`, `1832 -> 1960/1964`,
`2221 -> 435010/449749/449750`, `504558 -> 588343/588398`,
and `652115 -> 720591/720597`. These source-ID relationships are not certified
counter-assay pairs, distinct targets or independent families.

Exact measured potency, tested-but-censored/qualitative confirmation and no
follow-up are distinct states. A default numerical floor does not identify their
phenotype or a physical censor bound. Full-primary-library policy evaluation
cannot treat unobserved confirmations as a queryable oracle. A prespecified
fully observed confirmation cohort would answer a conditional-population
question and needs an explicit owner-approved design.

## Proposed next bounded decision: 4R2-A2

After 4R2-A closes, consider **4R2-A2: source-and-benchmark readiness**, initially
4 cumulative CPU-hours / 12 elapsed hours / at most two workers, with dr-train
processing. This is a proposed new budget, not an extension or unused allowance.

Deliverables would be a versioned metadata registry, justified measured-outcome
population or explicit NO_GO, an overlap/exposure plan, and an external workflow
benchmark compatibility/split report. No bulk activity intake, model campaign,
paid API or team-tool write is automatically included. Outcome-data access and
scientific pilot execution require the resulting concrete protocol and approval.

Do not add a dataset just to reach a numerical count. Retain the ambition of
12 or more verified biological groups for a later broad molecular study, report
what is actually eligible, and consult before changing that design. If the
evidence cannot support a novel identifiable molecular decision study, the
engineering product can proceed through the separately proposed P1 integration
and user evaluation; it does not inherit a scientific novelty claim.
