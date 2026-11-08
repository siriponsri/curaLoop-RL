# LR-M12 proposal: method viability and exposed-development evidence

**PROPOSED_NOT_STARTED. No data/compute release, clock, SSH or job starts from
this document.** Date: 8 November 2026, Asia/Bangkok. Planning base:
`c35a8420fba201dd7ecb93e9ee78f1b295833143`.

## Goal and phase count

Deliver a defensible GO / REVISE / NO-GO decision on the method candidate using
a focused reduction/novelty audit, scalable delivered-information predictor
adapter and controlled experiments on already exposed development assays.
The owner wants a method paper evaluated on existing datasets, not a new
benchmark publication. A positive method result is not guaranteed.

The [current roadmap](../../PLAN.md) has six phases: M0, M1, M2, M3, P1 and J1.
M0 design/constructed implementation is complete for review, with novelty HOLD.
This proposal targets **two additional phases: M1 and M2**. On conditional success,
M0-M2 deliverables will be complete and M3/P1/J1 remain. It does not promise a
publishable paper, finished plugin, journal acceptance or production release.

| Phase | Required deliverable | Status / relation to this proposal |
| --- | --- | --- |
| M0 | Formal design, focused closest work, exact constructed reference/checks and old-document reconciliation | Complete for review; retained, not rerun as new science |
| M1 | Reduction audit, substantive candidate distinction, scalable predictive adapter, privacy/identity tests and measured pilot allocation | Included first |
| M2 | Fixed development comparison, ablations, discovery/compute analysis, failures and reproduction evidence | Included only after M1 permits it |
| M3 | Frozen protected evaluation and uncertainty/dependence analysis | Excluded; later owner decision |
| P1 | New method integration into the existing R&D plugin and independent workflow assessment | Excluded as a completed phase; existing product remains available |
| J1 | Method-supported manuscript, figures, reproducibility and human/venue review | Excluded as a completed phase; drafts may be reconciled only |

M1 can finish with a documented NO-GO. In that case M2 stays NOT_RUN and only one
additional phase's investigation is completed. M2 can finish with unfavorable or
inconclusive results; completed execution is not a scientific GO. Do not label
both phases complete merely because the budget expires.

## Proposed fresh grant

**24 additional CPU-hours / 72 elapsed hours / at most four combined CPU workers**.
Set the release and absolute deadline after owner approval, using Asia/Bangkok
for user-facing times. All previous clocks and conservative charges remain closed.

| Allocation ceiling | CPU-hours | Included work |
| --- | ---: | --- |
| M1 method/adapter/controls | 8 | Focused executable reductions, up to two method revisions, predictor adapter, calibration diagnostics, leakage guards and timing admission |
| M2 fixed development comparisons | 10 | Frozen paired allocation including failures; no post-result tuning |
| M2 ablations/reproduction | 3 | Targeted mechanism removal, same-implementer reproduction, misspecification/fallback diagnostics |
| Source/environment/full return and cleanup | 2 | Scoped input checks, environment, all remote-file return/reread and exact owned cleanup |
| Utilities and English delivery | 1 | Controls, receipts, failure accounting, reporting and normal main delivery |
| Total | 24 | Fresh upper bound, not a runtime estimate or guaranteed sufficient allocation |

No borrowing old unused resources or automatic extension. The 72 hours are an
elapsed deadline, not 72 CPU-hours or a requirement to keep a process busy.
If admission or measured feasibility fails, report it and continue independent
work inside the released scope; do not exceed the cap or silently change the study.

### Parallel execution

- Local: at most one CPU worker / 1 GiB for bounded preparation, tests, metadata
  and aggregation. Larger fitting/planning runs use dr-train.
- dr-train: up to three isolated workers, each at most one CPU-equivalent / 4 GiB,
  admitted only after current account, available resources and actual kernel
  quota/memory/starting-affinity checks. Use only the existing configured chaw
  identity; no key, SSH config, privilege or host change.
- Freeze code/config/input hashes before parallel campaigns. Split independent
  assay/seed cells, give each isolated outputs/models, and retain common initial
  observations and allowed predictor settings. Parent remains sole code writer.
- Model/check work that depends on an unfrozen interface remains sequential.
  More concurrent workers do not imply independent biological samples.

## Data and access requested

Use existing local licensed/internal-research resources only, with current
source and intended-use records checked before launch. No new dataset download,
ChEMBL activity audit, QP/QC revival or MF-PCBA reconstruction is included.

1. HIV replay and three prepared Tox21 endpoints: exposed adapter/engineering
   smoke checks only. Do not promote them into untouched tests.
2. FS-Mol: the six already exposed development assays for the main development
   comparison. The two old exposed validation assays may be used only as a
   post-configuration-freeze development sensitivity; they are not fresh validation.
3. Permit controlled extraction/decoding of **only the previously allowed exposed
   compound pools within those assays**, using their frozen feature/identity
   manifests and the existing pinned source. An exposed assay name does not
   authorize every raw source row. Enforce canonical/source protection before
   label projection; if safe isolation cannot be established, withhold that input
   and report the blocker. The evaluator
   may read the admitted exposed binary labels for retrospective evaluation; the policy/predictor
   receives labels only through declared initial/delivered observations.
4. No reserved-final assay/label/presence inspection, new final role/split, raw
   potency-value query or human reference-gold construction. Do not decode the
   sixteen reserved-final feature files. Preserve all exact/canonical/source and
   exposed/protected constraints and every source STOP.
5. Predictive worlds must be generated by an admitted predictor using public
   features and delivered information. Never feed withheld historical label
   vectors to the planner as predictive scenarios. Add adversarial provenance
   and oracle-boundary checks before a real campaign.
6. Literature work may inspect lawful public primary methods/code/docs for the
   candidate and controls. No paid article, model/API, cloud/GPU or blocked-source
   retry. Inaccessible critical evidence stays UNKNOWN; request owner help only
   for a concrete missing item that is necessary to proceed.

Binary FS-Mol assay-relative potency labels retain their meaning. Do not claim
continuous Ki/Kd, sparse therapeutic hits, chemical OOD or certified independent
families. No raw rows or third-party payloads are redistributed publicly.

## M1 deliverables and transition gate

1. Compare the candidate formally with robust baseline regret, ENS/ordinary
   rollout and safe-improvement tree search. Record exact reductions and scope
   of primary/code inspection; do not infer novelty from names or combined features.
2. Implement at most two declared method revisions plus preserved controls, under
   the same binary active-search objective. Generic gate/cache changes alone
   do not pass. An endpoint, data-population or business-goal change needs the owner.
3. Implement a tractable predictor-to-scenario adapter and strong controls with
   shared representation/update/information contracts. Diagnose calibration,
   approximation error, model-set sensitivity and runtime. Gaussian/binary
   approximations must be named and cannot inherit external safety guarantees.
4. Measure scaling before committing the development allocation. The exact
   12-candidate/horizon-6 reference cannot simply be called production-scalable.
   Freeze feasible pool/horizon/scenario/compute settings using resource evidence,
   with no favorable-outcome rule or hidden performance-based task replacement.
5. Produce a locked candidate, denominator/exposure manifest, information-boundary
   checks, matched-cache robust control and resource forecast for M2.

**Automatic M2 continuation is allowed only if** the written review supports a
substantive provisional method distinction, the adapter/guards execute, the
matched controls are ready, and the frozen allocation fits remaining CPU/time/
memory. This is a same-implementer provisional judgment, not independent novelty
certification. No meaningful-effect margin has been specified by the owner.

If the candidate reduces to established robust improvement plus caching, if model
scenarios cannot be built credibly/scalably, or if the distinction remains unclear,
finish the M1 report and consult the owner before dependent M2 campaigns. Preserve
all negative evidence. Do not auto-pivot to a benchmark paper or try unlimited
new method families to obtain a positive result.

## M2 bounded development plan

Freeze the exact permitted assay IDs, input hashes, candidate/configuration,
initial seeds, budgets and analysis before the full development comparisons.
All arms share the same predictor/representation/update opportunities except
explicitly labeled frozen-model controls. Compare:

- Random, frozen-model and retrained strong Greedy;
- nearest-hit, diversity and explicit uncertainty;
- objective-matched ENS-style adaptation and ordinary mixture rollout;
- matched robust baseline-relative adaptation with the same cache access;
- the selected method candidate.

These are at most ten arms, not ten reproductions of published methods.
Use uniform initialization, retain zero-hit starts and separate any known-hit
sensitivity. Do not fit models using evaluation labels or share fitted campaign
states across arms.

Proposed maximum intended matrix, subject to M1 timing admission before freeze:

| Block | Maximum executions |
| --- | ---: |
| Six exposed development assays x three measurement budgets x three seeds x ten arms | 540 |
| Two old exposed validation assays, post-freeze development sensitivity, same allocation | 180 |
| Six development assays x one fixed budget x three seeds x four ablations | 72 |
| Adapter/timing/reproduction diagnostics | 48 |
| Intended total | 840 |

Hard ceiling **900 attempted executions**, including failed attempts and repairs;
CPU/time ceilings take precedence. Proposed measurement budgets are 16/32/64
where the frozen pool supports them. These are development settings, not a power
calculation or new panel eligibility floors. Freeze a smaller feasible matrix
only from resource/structural evidence before the full readout; disclose omitted
cells. Do not drop unfavorable tasks/results or add seeds after effect inspection.

Primary outputs: paired new historical assay actives versus measurement count,
plus measured policy CPU/wall time, memory, predictor calls, fallback/deviation,
timeouts and failures. Include matched-cache/compute controls, model ambiguity,
misspecification and interrupted-planning ablations. Expanded-state savings are
not a wall-clock speedup. Report effect/uncertainty by assay and conservative
source/group structure; seeds do not establish family-level generalization.

M2 scientific GO needs a useful, reproducible distinction/tradeoff over the strong
matched controls and a defensible method account. Do not select a success margin
from pilot results. Report favorable, null, harmful and all-Greedy regimes. A
negative bounded comparison can close M2 as an investigation without approving M3.

## Return, cleanup and completion

Use fresh exact owned local/remote roots only after release. Record storage
admission and a source/dependency/input/output manifest. Transfer only the selected
exposed development bundle; do not copy an entire protected-label archive merely
for convenience. No ChEMBL database restore is needed.

Every regular owned remote code, dependency, input/data and result file must be
returned and reread/hash-verified locally with terminal receipts before exact
task/export cleanup and a fresh absence check. Preserve originals on incomplete
return; do not delete other projects, shared caches or old task roots.

Deliver an English method/reduction report, frozen development protocol/config,
source and tests, complete/private run evidence, aggregate effects/compute figures,
negative findings, reproduction receipt, updated manuscript/claims and detailed
HANDOFF. Normal main integration/push is included; no history rewrite or unrelated
changes. Separate executed evidence, scientific verdict and phase completion.

At the owner checkpoint, propose M3 and P1 only if justified. P1 can later proceed
alongside M3 where interfaces are stable, but neither is closed by LR-M12. J1
requires supported research claims and human/venue review. No final outcomes,
live team writes, customer study, payment, deployment, journal submission or
acceptance is included in this proposed goal.
