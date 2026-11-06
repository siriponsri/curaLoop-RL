# Parallel long-run proposal: remaining B and conditional C

6 November 2026. **PROPOSED; NOT EXECUTION AUTHORITY.**

Owner request: propose a bundled long run across local CPU and dr-train.
Inspected main: `440fce2d731bff3e6ad4df47e34492be5554b916`.
This proposal starts no study, opens no new assay outcomes and creates no remote
task root. It preserves the [A3 closeout](GOAL4R2A3_CLOSEOUT_20261106.md) and
[standing B/C plan](PLAN_B_WITH_CONDITIONAL_C_20261106.md).

## Destination and two approval options

| Option | Additional CPU allowance | Cumulative ceiling including prior A3 | Endpoint |
| --- | ---: | ---: | --- |
| LR-B | 42.5 CPU-hours | B: 48 CPU-hours | Qualified data or explicit NO_GO; one bounded development pilot where valid; robustness; B potential decision and complete evidence return |
| LR-BC, recommended for the requested portfolio | At most 90.5 CPU-hours | B+C: 96 CPU-hours | LR-B, then at most 48 additional C CPU-hours only if the existing potential gates pass |

The previous 5.5-hour conservative A3 charge remains charged. Neither option
adds a fresh allowance to the unused old allowance. C is a conditional allocation,
not mandatory consumption. Workflow potential may support a scoped product
continuation without molecular-method superiority; the two claims stay separate.

Preserve existing absolute deadlines: B by 9 November 2026, 05:13:23 UTC /
12:13:23 Bangkok; combined B+C by 13 November at the same time. C also has at
most 96 elapsed hours from its recorded release. Approval does not restart these
clocks. A fresh full-duration window would require an explicit amendment.

This proposed consolidated contract would permit bounded stage advancement
without a new routine permission request at each gate. It would replace the
manual A3-to-pilot checkpoint only within the delegated decisions below. The
new repair goal would explicitly replace the old A3 operational subwindow for
new repair work only: R0 ends by its recorded start plus eight hours, R1 by its
recorded start plus twelve hours, both also bounded by B's absolute deadline.
The old A3 closeout/deadline stays historical and immutable. This subwindow
change is part of the proposed approval, not an extension already in force.

## Current resources, not reserved capacity

[Read-only capacity inspection](../evidence/parallel-longrun-proposal-20261106-v1/capacity-snapshot-v1.json)
found:

| Host | Observed resources | Initial role |
| --- | --- | --- |
| Local Windows | i5-13420H, 8 physical cores/12 logical processors; about 15.67 GiB visible RAM, 2.14 GiB free; about 61.28 GiB free on C | One light worker for contracts, metadata validation, tool integration, documentation, figures and bounded cross-host reproduction |
| dr-train | 72 logical CPUs allowed by affinity; about 125.76 GiB RAM, 115.52 GiB available; 109.45 GiB disk free; load averages about 0.42/0.64/0.75 at inspection | Initially three single-CPU workers for data processing and scientific comparisons |

The host is shared. Visible CPUs, low load and free RAM are not exclusive
reservations. Recheck resources/conflicts before each launch. The closed A3 root
was absent during inspection and must not be recreated.

The local repository virtual environment reports Python 3.12.10, RDKit 2026.9.1,
NumPy 2.3.5 and scikit-learn 1.8.0. Package metadata is not a native-runtime or
cross-platform parity test. Use the project environment explicitly; do not
upgrade global packages or frozen environments as part of routine setup.

## Parallel execution envelope

- Maximum **four project CPU workers combined across both hosts**, not four per
  host. Default split: one local plus three remote. If local RAM is insufficient,
  use zero local plus up to four remote workers after fresh admission checks.
- Start the local worker with one logical CPU and a 512 MiB process-tree memory
  ceiling. Pause local heavy work if free RAM falls below 1.5 GiB. Larger local
  jobs may use at most 1 GiB only after a recorded native canary and at least
  4 GiB free RAM at admission. More than 1 GiB requires an owner amendment;
  otherwise move the job to an admitted remote slot.
- Start remote jobs with one CPU, single numerical-library threads, nice19 and
  at most 4 GiB each. Record affinity, child-process policy, per-job CPU/wall
  bounds and durable reservations before dispatch.
- Planned host allocation for LR-B: about 6 local / 36.5 remote CPU-hours.
  Conditional C: about 6 local / 42 remote. These are scheduling allocations,
  not two independent allowances. Transfer unused allocation between hosts only
  within the combined stage/goal ceilings; never reset either ledger.
- Count failures, preparation, transport, validation, reconstruction and cleanup
  within the ceilings. Use a coordinator to reserve budget across both machines.
  CPU-heavy verification, archive construction and preservation occupy the same
  four worker slots; they are not extra uncounted parallel workers.
- Keep all arms of a scientific comparison in the same host/environment block.
  Do not run only controls on local and only the candidate on dr-train and call
  their timing difference an algorithmic gain.
- Local reproduction uses fixed subsets containing all compared arms. Freeze
  exact accounting checks and numerical tolerances before comparing platforms.
  It is cross-host computational reproduction, not external scientific validation.

The old A3 launcher intentionally holds a root execution lock for a whole job,
and its worker chooses the maximum allowed CPU ID. It is not a parallel runner.
Create a new reviewed runner version with distinct leased CPU slots, atomic
cross-host budget reservations and per-attempt output locks. Never start three
old workers and assume they use three distinct cores. Keep source/network intake
serialized under a shared request ledger; parallelize pure preprocessing and
independent task/seed experiment blocks. Run timing comparisons in a separately
controlled block with competing project jobs paused. Test coordination using
synthetic fixtures before any scientific batch.

Automated intake retains the known cumulative charges: 24 of 96 PubChem requests,
27 of 32 UniProt requests and 28,715,980 of 268,435,456 decoded bytes. Thus at most
72 further PUG and five further UniProt requests remain without an amendment.
This proposed approval additionally allows at most 64 metadata-only calls to
official NCBI protein/document/schema endpoints; their source/field roster must
be frozen before use. This is a non-PUG/non-UniProt bucket: any request to those
services still debits its inherited counter, regardless of a metadata label.
These calls cannot retrieve assay activity or substitute for a
bulk activity download. New metadata bytes share the same cumulative decoded
byte ceiling; each response is capped at 16 MiB. This ledger is not a claim to
measure all browser/search traffic or historical preparation downloads.
Retain the source's stricter rate limit and at least 1.1 seconds between these
intake requests. Preserve failure latches; no automatic retry after 403/429,
schema denial or an unchanged stopped request. Other data APIs or increased
ceilings need an explicit owner amendment. Literature discovery/reading uses
existing approved tools, with bounded searches rather than a bulk crawler.

## Bundled work and dependencies

| Work package | Local lane | dr-train lane | Dependency and release |
| --- | --- | --- | --- |
| R0: endpoint, provenance and population decision | Inspect source protocols/metadata; missing-TID diagnostics without inspecting new activity values; draft data/model cards and novelty comparison; prepare the new coordinator | Validate synthetic parallel-runner/resource fixtures; reconcile cached target identities, exposure and family metadata; audit candidate manifests | Starts after the new contract; no new activity requests in this package |
| R1: revised data qualification | Implement/review versioned parsers and boundary fixtures; prepare immutable request plans | After release, run exact filtered two-stage canaries and bounded qualification; canonicalize/exclude protected identities | Requires documented source rights, endpoint semantics, population and protection gates |
| Shared evidence/plugin core | Typed tools, evidence/plan/report identity, persistence, resume and local/preview exports | Test against permitted returned real-source metadata and validated development inputs | Can progress during data audits; live agent evaluation waits for a verified client/model/quota |
| Scientific development pilot | Prepare analysis/figures and cross-host canaries | Matched predictor/control/candidate experiments; shard independent task/seed blocks | Requires qualified observations and a frozen scientific protocol |
| Real-source workflow evaluation | Build source-grounded cases and deterministic checks; integrate one verified client where available | Execute comparable permitted case batches; retain failures and costs | Freeze tasks, reference evidence, metrics and controls before evaluation; synthetic tests alone do not pass |
| Robustness and reporting | Reconcile results, uncertainty, limitations, journal requirements and English documentation | Essential ablations, per-group effects and same-project reexecution | Follows the corresponding comparison; no unplanned candidate search |
| Conditional C portfolio | Thin Evidence Workspace, Decision Workbench and Integration Kit interfaces around the same core | Harden validated capabilities, run bounded regressions/reproduction | Only after a recorded POTENTIAL_SUFFICIENT verdict |

Three lanes can therefore progress together: data/science on dr-train, light
engineering/integration locally, and read-only literature/protocol review. CPU
jobs and specialist-agent roles are different counts. The parent remains sole
writer to main; specialists review read-only and workers write disjoint versioned
output partitions. Do not concurrently overwrite a shared scientific result file.

## Remaining B budget

| Package | CPU-hour ceiling, including its overhead |
| --- | ---: |
| R0 metadata/endpoint/provenance decision | 4 |
| R1 bounded data qualification and source/structure gates | 6 |
| One development pilot, including prespecified molecular/workflow comparisons where feasible | 20 |
| Essential robustness and reexecution | 8 |
| Reporting, complete return, verification and cleanup | 4 |
| Contingency held centrally | 0.5 |
| Remaining B | 42.5 |

Profile a canary before assigning the pilot's exact cases. Cap new candidate
selection at two prespecified variants plus an unchanged anchor; controls are
specified separately. A negative comparison does not authorize another search.
R0 has a proposed eight-hour elapsed ceiling; other subwindows must be fixed
before their launches and remain within the absolute goal deadline.

Conditional C retains the original 48 CPU-hour allocation: 12 hardening, 24 shared
portfolio construction, 12 reproduction/demonstrations/documentation/preservation.
Its scope follows the capability actually supported by B, not every proposed
feature or an assumed scientific superiority result.

## Gates that may advance automatically after explicit long-run approval

1. **Environment/source gate:** native canaries pass; old source/results remain
   immutable; rights and protected identities are explicit; no final outcome is
   an input. Missing permissions quarantine a source.
2. **Observation gate:** an endpoint and conditional population are justified by
   published assay protocol/source semantics before new outcomes. Exact filtered
   primary and confirmation responses validate. Missing/censored/unmeasured states
   stay distinct. Original STOP/NO_GO records remain unchanged; a new, explicitly
   released source attempt must reference them rather than clearing history.
3. **Scientific gate:** freeze outcome, controls, estimand, exposure rules,
   independent units and maximum trials before fitting/evaluation. Retain strong
   same-predictor Greedy and appropriate multifidelity/cost-aware controls.
4. **Workflow gate:** evaluate permitted real-source cases against an appropriate
   simpler control. Freeze metrics such as evidence/endpoint correctness,
   unsupported recommendations, plan validity, failures and costs. No fabricated
   expert ratings, user-time savings or LLM capability claims.
5. **Potential gate:** apply all five checks in the standing B/C plan: valid
   intended use, useful real-source capability, fair comparison/uncertainty,
   reproduction/review and feasible licensed product continuation. Record the
   actual evidence and the C tasks it supports. A positive point estimate or
   passed fixtures alone is insufficient.

There is no new numerical significance/material-effect cutoff. Estimate effects,
uncertainty and heterogeneity as the owner requested. Twelve or more verified
biological groups remains the broader-study ambition, not an invented journal
minimum or guaranteed cohort. A smaller valid development pilot must be labelled
as such and cannot become broad-transfer validation through relabelling.

## Delegated choices and human decision boundaries

The proposed long-run approval may delegate routine versioned parser repairs,
implementation of an already justified source-defined endpoint, task sharding,
and gate-based progression after scoped review. It does not delegate a material
change of the scientific endpoint, replicate aggregation, phenotype or target
population merely because the frozen endpoint is incomplete. The known A3 gap
may require such a choice: if source evidence does not resolve it unambiguously,
R0 produces reviewable alternatives and pauses the dependent molecular branch
for the owner's decision while independent engineering/workflow work continues.
Offline engineering repairs may use at most two prespecified repair attempts
per failed batch; this is not permission to retry stopped live intake.
R0 must freeze the candidate source roster, exact request/byte limits and roles
before intake. Existing consumption and exposure follow every new contract.
No bulk fallback, missing-value floor or outcome-selected source replacement is
authorized. Additional source candidates need paper, phenotype and intended-use
review before access, rather than an assumption that public data are unrestricted.

Consult the owner before an unresolved/material endpoint or population change,
unavailable rights, increased budget/deadline, protected final-label release,
new paid model/API service, real team write, deployment or publication action.
If potential is uncertain, report alternatives. Continue independent authorized
engineering/documentation when a scientific branch is blocked; do not keep
retrying an unchanged failure to consume the long-run allowance.

An existing verified client/quota may support agent evaluation. CPU authority
alone does not provide or authorize billable LLM access. Without that access,
implement/test the tool surface and report live-agent evaluation NOT_RUN.

## Deliverables and endpoint of the long run

- Versioned dataset/endpoint/exposure manifests and actual coverage, or a fully
  evidenced NO_GO with the remaining decision stated precisely.
- One bounded development comparison with controls, uncertainty, costs and
  failures where its data gate passes; no promised favorable result.
- A real-source workflow demonstration/evaluation where source and client gates
  pass, otherwise an accurate separation of implemented tools from unrun agent work.
- B_POTENTIAL_DECISION and a conditional C release or stop, with research and
  product potential labelled separately.
- If released, the three thin portfolio packages, an end-to-end demonstration,
  English documentation and a journal-readiness report reflecting actual evidence.
- All owned remote code/data/artifacts returned and completely reread/hash-verified
  before exact scoped deletion; fresh absence and normal main delivery readback.

This endpoint is an evidenced B decision and, conditionally, a product portfolio.
It is not guaranteed publishability, automatic use of the old final panel, or
actual journal submission. A final independent study/manuscript submission remains
a later explicit decision supported by the resulting evidence.

**Status: READY_FOR_OWNER_DECISION. No long-run execution has started.**
