# Proposed long run: LR-D23

Date: 9 November 2026, Asia/Bangkok. Status: **PROPOSED_NOT_RELEASED**.
The owner requested this proposal and authorized normal main commit/push of
completed D0/D1 work and the proposal. This is not approval to begin LR-D23.

## Destination

Close two research stages in one bounded release: **D2, one residual computation
candidate**, then **D3, development robustness**, conditional on the D2 gate.
Produce a complete evidence/reproduction package, an offline product handoff
and a paper methods/results insert. Stop for owner review before M3/final data,
actual product integration or a journal submission. Do not claim those later
phases are completed by preparing their inputs.

The proposed fresh ceiling is **24 CPU-hours / 72 elapsed hours / four combined
workers**, initially local one plus up to three dr-train workers. No clock or
scientific root starts until explicit owner approval. All old grants, including
D1's unused allowance and the inactive conditional 96-hour grant, stay closed.

## Why this is the next discriminating goal

[D1](../03_research/D1_OPERATION_HEADROOM_RESULTS_20261109.md) found real refresh
value: G1 exceeded frozen-cache by 3.875 mean new positives. Fixed Gk4 saved
73.9% scientific CPU but lost 0.53125 positives against G1, outside the approved
0.25 loss preference. The stale>=4 association (+1.1667 in eight states) motivates
a hypothesis, not an optimal threshold. PLAN changed choices but its small mean
increment does not justify another planning-heavy candidate now.

The question is whether a small state-dependent correction can recover the
discovery/compute gap beyond strong cheap controls under repeated decisions.
The contribution remains a proposed **method evaluated on published data**.
It is not a new benchmark publication, an RL claim, or a certified novel algorithm.
Ordinary retraining triggers, Ridge regression and approximate policy improvement
are established ideas; their combination alone is insufficient novelty.

## One candidate, frozen before experiments

Use fixed **Gk2 as the incumbent**, with a bounded residual gate choosing only
UPDATE or REUSE. Keep the original RF/neighbor predictor adapters unchanged.
Exclude PLAN from the candidate; retain the existing T comparator so its cost
and behavior remain visible. No acquisition-function or predictor search.

Proposed exact v1 mechanism:

1. Eight delivered-information features: remaining assay fraction, remaining CPU
   fraction, stale labels divided by B, cached margin, eligible cached-score
   standard deviation, observed positive fraction, recent prequential Brier
   error, and model availability. No shadow refit or post-operation ranking
   change is a free predecision feature. Charge feature extraction/inference.
2. A standardized Ridge model, alpha=1, predicts terminal new-positive difference
   UPDATE minus REUSE under the declared common continuation. Equal annotation-
   component training totals; training-only scaling. No hyperparameter search.
3. Begin with Gk2's action. Override toward UPDATE if predicted difference is
   greater than +0.25, toward REUSE if below -0.25, otherwise retain Gk2. This
   fixed per-state deadband is a heuristic, not a cumulative loss certificate.
   Apply the common CPU feasibility/interruption rules and log every fallback.
4. Two fixed training rounds for this same mechanism. Round 0 uses Gk2-generated
   states and a common Gk2 continuation to fit v0. Round 1 uses v0-generated
   states and a common frozen v0 continuation to fit final v1. Train v1 on
   round-1 targets; v0 is not selected using evaluation outcomes.

This addresses one identifiable mismatch in M2's fixed G1-tail supervision.
It is still one approximate improvement step: v1 deployment is not identical
to a v0 continuation. No policy-improvement, uncertainty or regret guarantee is
claimed. Do not call the deadband a calibrated safety bound.

At the start, write a precise algorithm/closest-work comparison and confirm
that the implementation actually realizes this mechanism. If it reduces to an
ordinary trigger without a defensible method question, stop the scientific
track with that finding. Complete the independent evidence/paper handoff instead
of inventing another mechanism. At most one candidate and two declared training
rounds; no third round or replacement thesis without owner consultation.

## Data and leakage contract

Use only the six already exposed FS-Mol development assays and four existing
annotation components. Preserve source identities, canonical structures,
annotation/dependence rules and old masks/roles. No new assay, download, split
of protected data, old validation payload, or final feature/label/presence access.

This proposal explicitly requests **full-pool development labels within each
training fold**. The old M2 training masks remain immutable historical provenance;
they are not silently rewritten. Full-pool training on the other components
avoids the masked-pool/full-pool frame mismatch in D1 reuse. It does not make the
exposed development evaluation independent or final.

Use four outer leave-one-annotation-component-out folds. For outer component g,
all training states, v0/v1 targets, scalers and models use only the other three
components. Generate round-1 trajectories separately for each outer fold: a
policy trained with g's labels must not generate training data for the fold
that claims to exclude g. Fixed Gk2 round-0 states may be cached when provenance
and information are identical. Evaluation labels are available only through
each campaign's private Oracle after the action commits.

Train on RF/B32/reference-C only. Candidate and deadband stay frozen for B16,
neighbor and tighter-compute transfer; no cell-specific retraining or tuning.
Seeds are within-assay repetitions; components are not certified biological
families. All six assays have already informed project development, including
this proposal. More runs cannot supply new biological independence.

## Work sequence and automatic continuation

| Stage | Deliverable | Gate and consequence |
| --- | --- | --- |
| A: freeze/admit | Algorithm, closest-work distinction, exact folds/seeds/spec hashes, synthetic guards, cost ledger | Outcome-blind admission first. Stop/re-cost on resource or substantive design mismatch. |
| B: D2 training/evaluation | Two fixed rounds, final v1, strong controls and two attribution checks | Proceed to D3 only if the frozen D2 usefulness/integrity gate passes. Otherwise close the candidate and report. |
| C: D3 development robustness | All prespecified predictor/budget/CPU cells, no retuning | Report successes and failures; restrict claims to their predeclared domains. Do not repair on D3 outcomes. |
| D: synthesis, always | Evidence/reproduction bundle, product handoff, English paper insert and owner checkpoint | Complete even after an early scientific stop, using the available evidence and truthful NOT_RUN labels. |

Stage D is documentation/artifact preparation. It does not train a substitute
method, perform a customer study, change the UI, or activate another phase.

## Fixed comparison and reporting contract

Seven arms: candidate v1, G1, fixed Gk2, fixed Gk4, fixed T(k4,tau0.05),
frozen-cache greedy and nearest-hit. The last two keep D1's tested one-class
and delivered-only behavior. No retuning of k, tau, deadband or alpha on the
evaluation outcomes. Two nonselectable attribution checks: no-history v1 and
round-0-only v0. Incumbent-only is already Gk2, not an extra arm.

Initialization is uniform n0=0/16; new positives exclude initial labels. Primary
endpoint is new delivered assay positives at fixed B/C, with measured scientific
CPU, whole-process/startup cost, deliveries, fitting/operation counts and learned/
fallback shares. Offline training cost is reported separately and included in a
break-even campaign calculation; tiny per-campaign seconds are not lab savings.

Before labels, derive C_ref =1.25 times the maximum complete synthetic G1 CPU
at the admitted public pool sizes across all leased cores, separately by
predictor/n0/B. Upper admission bounds: RF C_ref<=5s; neighbor C_ref<=1s.
Use common C_ref and 0.5*C_ref regimes. The tighter regime intentionally tests
compute-constrained operation; report interruptions/lost opportunities. Never
reduce a cap after seeing biological outcomes or truncate a reference to admit it.

Primary D2 is RF/B32/C_ref. D3 crosses RF/neighbor, B16/B32 and C_ref/0.5*C_ref:
eight cells total, with the primary cell reused rather than rerun.

Equal component totals, equal assays within components, and matched n0/seed
contexts define reported means. Report component ranges and joint-seed conditional
intervals; no population CI, seed multiplication of biological sample size, or
p-value gate. A mean-point frontier is descriptive, not statistical dominance.

## D2 usefulness gate, fixed before evaluation

All technical/data/role/pairing/resource gates must pass. A candidate advances
only when all of the following hold on the primary cell:

1. Relative to G1: mean hit loss <=0.25 and scientific CPU reduction >=20%.
2. Relative to fixed Gk2: either >=1 additional new positive with CPU no more
   than 10% higher, or >=20% scientific CPU saving with hit loss <=0.25.
3. At least three of four components have hit loss <=0.25 versus G1; no evaluated
   control dominates the candidate's mean discovery/CPU point. Publish every
   component effect, including failures.
4. The no-history and v0 checks, operation/fit counts and paired support allow
   attribution to the proposed mechanism rather than missing comparisons,
   free refits, hidden information or complete incumbent fallback. A weak or
   ambiguous attribution is reported as inconclusive, not repaired by relabelling.

These retain D1's engineering usefulness preferences and add a strong-incumbent
test; they are not clinically justified noninferiority margins. No post-result
relaxation. D3 transfer preferences scale hit margins by B/32: loss tolerance
0.25*(B/32), discovery gain 1*(B/32). Broad transfer requires the G1 saving/loss
preference in all eight cells; otherwise report the failed cells and a narrower
development claim. D3 failure does not authorize more methods or final access.

## Workload and fresh budget

Proposed new ceiling: **86,400 CPU-seconds / 72 elapsed hours / four combined
workers**. Absolute UTC/Bangkok deadline starts at release, not at this proposal.

| Bounded allocation | Maximum units | Retained envelope seconds |
| --- | ---: | ---: |
| Synthetic admission: 24 contexts per leased remote core, three cores | 72 x15s | 1,080 |
| Training prefixes: 18 outer-fold training-assay memberships x2 n0 x3 seeds x2 rounds | 216 x10s | 2,160 |
| Paired branches: 216 prefixes x3 snapshots x2 operations | 1,296 x10s | 12,960 |
| Gate fits: four folds x(v0,v1,no-history v1) | 12 x120s | 1,440 |
| D2 primary: six assays x2 n0 x5 seeds x7 arms | 420 x10s | 4,200 |
| Two attribution checks at the primary setting | 120 x10s | 1,200 |
| D3: seven additional cells, same 420-unit matrix | 2,940 x10s | 29,400 |
| Identical-context technical retries only | <=96 x10s | 960 |
| Setup/transport/guards/tests/complete return/cleanup/report and handoff | bounded utility jobs | 6,000 |
| Planned upper reservation | 5,076 intended units, <=5,172 attempts | **59,400 (16.5 CPU-hours)** |
| Unallocated headroom inside the ceiling | not an extra study allowance | **27,000 (7.5 CPU-hours)** |

Training seeds: 81001/81013/81029; evaluation seeds: 82003/82013/82037/82051/82067.
Snapshots after deliveries8/16/24; cold/infeasible states remain visible, with no
outcome-selected replacements. Gate fitting requires adequate executed support
in every outer training fold; stop if fewer than 30 supported paired states or
fewer than two represented training components remain. Freeze exact manifests
and budget reservations before each stage's first unit.

Per-campaign envelope is at most5s scientific +5s startup/reporting. Neighbor
may be cheaper, but budget it at the same conservative10s upper bound. No PLAN
reference campaign is proposed. Preserve failed/censored work; allow at most two
technical retries per exact unit and the total96 ceiling. No scientific retune
counts as a technical retry. Do not silently spend headroom on more seeds/methods.

## Parallel operation and preservation

- dr-train: up to three serial single-process molecular workers, each aggregate
  CPU-equivalent1 /4GiB /swap0, using fresh resource proof, the existing chaw
  profile and fresh task-root namespace. Same matched context/branches use the
  same admitted core; outcome-blind order and common library versions.
- Local: one lightweight worker for manifests, link/source tests, summaries and
  artifact preparation, target <=1GiB. No local molecular timing used to compare
  with remote measurements. Parent remains the sole code/document writer.
- Combined at most four. Local orchestration/helpers and all failures/transport/
  return work count in the fresh grant. No GPU, paid API, credentials/config/
  privilege changes, unrelated deletion, or live team writes.

Return every new owned code/dependency/input/output/trace file, independently
reread/hash-verify locally, then delete only the exact authenticated task/export
roots and observe absence. Preserve all old ledgers, STOPs, source/result pins
and exposed/protected roles. Never recreate D1/M2 closed roots.

## Product and journal deliverables

Product handoff: versioned aggregate evidence bundle, typed result/schema example,
decision-card text and provenance/limitations for the existing EN/TH dashboard and
offline R&D plugin. Keep best supported controls visible. Actual UI/integration,
customer effort measurement, live connectors and business validation need their
own phase decision; do not call a JSON bundle a deployed product.

Journal handoff: English algorithm/experiment description, comparison table,
positive/negative results insert, reproducibility commands, limitations and claim
map. Preserve old manuscript/results bytes; no acceptance/readiness guarantee.
Independent/domain/author review and an owner-approved M3 protocol remain ahead.
Venue/fees need a fresh check at that time; no submission/payment is authorized.

## Prior-art verification boundary

Primary pages checked9 November: [Regol et al., ICML2025](https://proceedings.mlr.press/v267/regol25a.html)
formulate cost-aware model retraining under limited information; [Jiang et al.,
ICML2017](https://proceedings.mlr.press/v70/jiang17d.html) establish finite-budget
nonmyopic active search as prior work. Neither certifies this residual candidate
or its superiority. The Regol PDF endpoint returned an unsupported content type
in the browser tool; its full text was not read in preparing this proposal.
Use the existing literature/reading receipts and verify selected full methods
before a novelty claim. Do not transfer theorems or another study's improvements.

## Owner approval scope

Approval would release this exact D2 -> conditional D3 sequence, full-development
training-label scope, fresh24 CPU-hours/72 hours/four-worker ceiling, independent
handoff work and normal code/aggregate/document main commit/push at closure.
Stop for a material mechanism/cohort/endpoint/rights/resource change; continue
only the independent authorized handoff tasks while asking for that decision.

Final16 features/labels/presence, M3, an external dataset, actual P1 integration,
live team writes/deployment, paid services and journal submission remain excluded.
The recommended stopping point is the completed D2/D3 development report and an
owner decision, including an honest early-stop report if the candidate fails.
