# CPU and time options before Goal 4R2-A3

6 November 2026. **PROPOSED ONLY; READY_FOR_OWNER_REVIEW.**

The owner requested alternatives for expanding resources before A3 and clarified
that the expansion concerns CPU and elapsed time only. No paid API/model service
is included. This planning document does not start A3, data intake, a new pilot
or P1. Base main: `0aeaf32600e262fd5cf150ee7d98d1d8e46e86b3`.

## Destination and current evidence

Choose an envelope that can turn the evidence-to-experiment direction into a
testable molecular decision study, with an optional product integration path.
The immediate deliverable is an observation/population decision; later method
and agent claims require their own valid evaluation.

The [A2 report](../03_research/GOAL4R2A2_READINESS_V1.md) records 105 matching
version/revision metadata pairs, ten passing engineering checks and a scientific
pilot NO_GO. Its three workers consumed 9.000529007 measured CPU-seconds;
1.1 CPU-hours was a conservative reserve-based charge. The blocking decisions
concern source/rights, follow-up observation support, scientific endpoint and
independent groups. A3 row-processing throughput and memory are NOT_MEASURED.
The proposed ceilings below are planning judgments, not runtime forecasts or
guarantees that twelve groups, a positive result or a publication will be obtained.

## Alternatives

| Option | Cumulative CPU ceiling | New elapsed window | Maximum concurrent CPU workers | Intended endpoint |
| --- | ---: | ---: | ---: | --- |
| A: focused qualification | 16 CPU-hours | 24 hours | 2 | Complete expanded A3 source/rights/observation/population qualification, with an eligible-cohort protocol or explicit NO_GO; no method campaigns |
| B: staged research programme, recommended | 48 CPU-hours | 72 hours | 4, initially 2 | A3 first; reserve subsequent resources for one approved development method pilot, essential robustness checks and a complete evidence delivery |
| C: research plus plugin prototype | 96 CPU-hours | 7 days | 4, initially 2 | A3, a larger approved development challenge and an approved P1 integration prototype; no automatic final study or journal submission |

All options use the existing dr-train CPU host subject to a fresh shared-resource
check. The previous task roots remain closed. No GPU, new paid compute/model
service or change to protected final outcomes is included. CPU totals cover
local and remote processing and declared utility/preservation reserves. The
concurrency ceiling does not reserve exclusive physical cores.

One CPU-hour is one CPU core used for one hour; four busy cores for twelve hours
consume 48 CPU-hours. Elapsed windows also include downloads, review, checks and
waiting. More workers do not override source request limits. An approval wait
does not automatically pause or extend the owner window. Unused old allowances
are not carried over; each approved envelope needs a new recorded start/deadline.

### A: focus resources on the next decision

Use the doubled A3 proposal to resolve source reconstruction, provider-specific
rights, endpoint/readout definitions and historical observation states. Only
after the pre-intake gates pass, use a bounded development-only data sample to
measure coverage, attrition, processing resources and protected-panel overlap.
Keep fully measured, censored/qualitative, invalid and never-followed-up states
separate. Report eligible biological groups without forcing the twelve-plus
ambition or silently substituting a new population.

Strength: a clear answer with the smallest expanded commitment. Limitation:
the endpoint is data readiness, so it provides no new decision-method or complete
agent performance evidence. A source with unresolvable rights or observation
support can still produce a valid NO_GO within this goal.

### B: staged research with a reserved pilot budget

Proposed internal allocation:

| Stage | CPU-hours | Release condition and artifact |
| --- | ---: | --- |
| Expanded A3 | 16 | Owner-approved pre-intake contract; source/rights and observation register, attrition, group/overlap report, measured processing profile and GO/NO_GO decision |
| One development pilot | 20 | Owner review after A3; frozen mechanism/estimand, eligible development roles, matched comparators and measured runtime canary before scaling |
| Essential robustness/reexecution | 8 | Same approved mechanism and exposure rules; prespecified sensitivity/ablations and reproduction, rather than open-ended model search |
| Reporting, transfer, preservation and closeout reserve | 4 | Reconciled artifacts, uncertainty/limitations, complete local return before scoped deletion and main delivery |

These allocations are caps within 48 hours of CPU, not promised consumption.
Stage processing charges its own preparation costs; the four-hour reserve covers
shared final preservation/delivery overhead without double charging it. The exact
launch ledger and reserve accounting must be specified in the execution contract.

The candidate scientific question is whether resolving missing/conflicting
evidence improves the choice of confirmation measurements or justified stopping
under a fixed budget. Freeze one concrete decision principle before development
outcomes are used to select it. Hold the chemical predictor and resource model
fixed when comparing decision policies. Include a cheap fixed rule, a strong
statistical policy and an applicable published multifidelity method when the
observation contract is compatible. Multifidelity budget-aware search already
has direct prior art; adding agent tools is not by itself a new contribution.
[ICML 2021 primary paper](https://proceedings.mlr.press/v139/nguyen21f.html).

Report source-measured confirmed outcomes within the explicitly qualified
population, effect estimates/uncertainty and mechanism ablations. Cost/time
parameters remain simulated unless supported by actual operational evidence.
No full-library oracle is inferred from selectively observed follow-ups.

Strength: a route from data qualification to evidence about a distinct decision
method, with useful stop points before the larger allocation. Limitation: success
depends on A3 eligibility and a defensible mechanism; the allocation cannot
guarantee novelty, superiority or twelve independent final groups.

This is the recommended balance for the current research goal. JCAMD states
that properly retrospective validation can suffice for novel methods or
innovative computational strategies, while prioritizing experimental validation.
Our inference is that a well-controlled molecular decision study is a better
fit than generic connector functionality alone. Acceptance is not guaranteed.
[Current JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope).

### C: add a product integration stream

Indicative allocation: A3 16, development method work 40, P1 prototype 24,
and reproduction/reporting/preservation 16 CPU-hours, totaling 96. Each later
stream requires its own approved contract and predecessor checks; increasing
the envelope alone does not authorize all of them.

The P1 target is a real permitted paper/database-to-evidence-to-plan/report path,
with typed plugin tools, resumable retrieval, conflict reporting and local export/
delivery preview. Use fixed failure cases and source-backed expectations.
Live model-assisted evaluation is conditional on an existing verified client,
allowed quota and explicit run scope; a CPU budget does not supply model access
or authorize billable calls. Without that access, deliver/test the connector and
deterministic workflow infrastructure and report live agent performance NOT_RUN.
No team-tool write or commercial data permission is implied.

Strength: creates research artifacts and a concrete integration prototype for
later business testing. Limitation: combines two substantial workstreams and
introduces client/runtime dependencies; CPU-only resources do not guarantee a
fully evaluated autonomous agent. Customer value, laboratory savings and demand
remain separate empirical questions. MolDesignBench remains conditional auxiliary
design evaluation, with its output/rights restrictions preserved from A2.

## Decision map and next ready work

| Decision | Evidence needed | Dependency | Owner and resolution test |
| --- | --- | --- | --- |
| D1: resource envelope | Choose A/B/C, CPU/window/concurrency and whether downstream budgets are reserved | Current owner choice | Owner; record selected ceiling without starting its clock prematurely |
| D2: exact A3 intake contract | Rights/intended use, historical versus named current reconstruction, source operations/byte/request limits and protected-data exclusions | D1 | Lead prepares; owner resolves material source/population changes before intake |
| D3: observed population readiness | Explicit observation masks, attrition, endpoint semantics, group/chemical exclusions and measured processing profile | D2 and permitted sample | Lead plus read-only review; GO only for a stated identifiable population, otherwise NO_GO/UNKNOWN |
| D4: method pilot release | One justified mechanism, fixed controls/estimand/exposure rules and bounded canary forecast | D3 and owner review | Owner releases the next goal; no automatic model rescue or family-threshold relaxation |
| D5: P1 integration release | Verified client/tools, permitted source access and local/preview destination scope | Option C or a separate P1 choice | Owner; product implementation/evaluation recorded separately from molecular evidence |

If D3 fails, preserve the evidence and ask for the material source/design decision.
Remaining B/C CPU is held rather than spent on extra candidates. Background
metadata review can shortlist one alternative paper-backed source; no replacement
activity intake or changed scientific population is automatic. Human rights,
source-access or editorial decisions cannot be solved by extending CPU alone.

## Exclusions, verification and handoff

All three options exclude new paid services, GPU/model training, protected final
outcome release, automatic final-study execution, real team/customer writes,
provider contact, journal submission and actual laboratory work. Source-access
failures are retained; an owner download request must identify the exact URL
and local target path. Preserve all previous frozen source/results.

This proposal was prepared from the current repository, A2 evidence and primary
source refresh. No SSH, activity/task-row intake, scientific campaign, new model
run or payment was performed. The planning work uses the decision-planning skill;
no subagent or independent scientific validation is claimed for this proposal.

Next ready decision: **select A, B or C**. Recommendation: **B as a reserve
envelope, with only the initial 16 CPU-hour A3 stage released after its exact
intake contract is agreed**. Review A3 before releasing the remaining 32 CPU-hours.
The budget choice and the later scientific/product execution decisions are
separate. Status: **READY_FOR_OWNER_REVIEW**.
