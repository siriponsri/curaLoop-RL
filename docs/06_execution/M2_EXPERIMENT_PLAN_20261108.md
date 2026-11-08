# M2 experiment plan: predictor-aware selective computation

8 November 2026, Asia/Bangkok. **CONTRIBUTION_APPROVED; EXPERIMENT_NOT_RELEASED.**
Planning checkpoint: `e0e80c900f340daeed2f1bca7194e66ab9f46f44`.

The owner approved the [contribution](../03_research/M2_CONTRIBUTION_PROPOSAL_20261108.md)
and requested this plan for consideration before execution. No implementation,
fit, campaign, SSH session or new activity/final-data access is authorized by this
document. The proposed grant is **48 fresh CPU-hours / 96 elapsed hours / at most
four combined workers**. Its clock has not started. M3 remains a separate owner
decision, regardless of the M2 result.

## 1. Question and contribution

Can a small learned controller choose when to **reuse**, **update**, or **plan**
from observable screening history, improving delivered assay-positive discovery
under separate assay and computation limits over strong fixed and adaptive rules?

The proposed contribution is a molecular computational strategy with outcome-based
operation supervision and identifiable computation accounting. General
metareasoning, learned acquisition and portfolios are established prior art.
This study tests incremental utility; it does not certify a new RL algorithm,
theorem, clinical benefit or commercial savings. Creating a benchmark publication
is not the objective. The prior M1 NO-GO remains unchanged.

This is **one bounded M2 development study**, including implementation and
technical admission. It does not require another open-ended M1 revision cycle.
The investigation closes with a report even if the method is unsupported.

## 2. Data requested for this release

Use only the six previously exposed, prepared **FS-Mol development pools** below.
The [metadata allowlist](../../research/manifests/m2_data_scope_20261108_v1.json)
pins their expected input/feature hashes and source receipts. There are **1,285
task rows, historically 1,107 distinct canonical structures, and four annotation
components**. These are not four independently certified biological families.

| Assay | Rows | Holdout component |
| --- | ---: | --- |
| CHEMBL1614225 | 168 | Globin annotation component |
| CHEMBL1738549 | 303 | MIT/TFE annotation component |
| CHEMBL1738553 | 248 | MIT/TFE annotation component |
| CHEMBL1737942 | 270 | TNF annotation component |
| CHEMBL3705420 | 167 | Quarantined, broadly connected annotation component |
| CHEMBL2219098 | 129 | Same quarantined component |

Source: [FS-Mol, Stanley et al., NeurIPS Datasets and Benchmarks 2021](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html),
[official implementation](https://github.com/microsoft/FS-Mol), upstream commit
`92aa95daba3f43863227e65be85a07b4a2ee754f`. Existing prepared inputs use canonical
isomeric SMILES and nonchiral Morgan radius-2, 1,024-bit fingerprints. Historical
preparation receipts, rather than a new raw-data extraction, define these pools.
Source ChEMBL 27 and later annotation provenance must remain distinguishable;
this is not a qualified ChEMBL 37 benchmark. Upstream task-count discrepancies
are retained in the [dataset card](../03_research/FSMOL_DATASET_CARD_V2.md).

**Endpoint semantics:** FS-Mol binary labels are assay-relative, potency-derived
classifications. A positive is not a validated therapeutic hit, sparse HTS hit
call or clinical outcome. Source balance must not be represented as realistic
screening prevalence. No activity values, concentration-response curves or new
thresholds are needed.

Approval would newly permit decoding these six development-label files for
training histories, counterfactual continuations and paired development evaluation.
An evaluator holds their full labels; deployed policy state receives only initial
and subsequently delivered labels. Gate-training targets may use future labels
only inside training components. No cross-campaign label cache is permitted.

**Excluded:** old validation pools (330 rows), all final pools (16 assays / 5,015
rows / 12 historical components), their features/labels/presence masks, full source
assays/archive enumeration, new ChEMBL/MF-PCBA/HIV/Tox21 intake and new downloads.
The six allowed input files must be freshly hash-checked before decoding after
release. Existing metadata-only protected-identity checks remain mandatory; no
protected payload is decoded to perform them. A protection mismatch stops work.

Retain all original roles, raw bytes, notices and exposure history. One source
test assay has a historical custom development role; its source role does not
turn it into an unexposed test set. Conflicting dataset-license notices remain
documented. This proposal requests scoped private research, not commercial data
rights or public row redistribution. Publish code and aggregate evidence only;
keep labels, fingerprints, structures and per-compound histories private.

## 3. Development separation and leakage controls

Use four **leave-one-annotation-component-out** folds. For each fold, fit the
gate/scaler and choose tunable controls using only the other three components.
Evaluate the held-out component once with frozen recipes. All assays in a
component stay together. The assay surrogate may learn delivered labels within
its own evaluation campaign, as required for sequential active search.

Before label decoding, construct one global, outcome-blind **meta-training mask**
using only the six permitted feature sidecars: remove from every meta-training
pool any canonical structure occurring in more than one of the four components.
Keep all original evaluation pools unchanged. Preserve and hash the derived mask;
do not rewrite source data or frozen roles. Cache training trajectories once on
these masked pools, then filter by component for each fold. This prevents a
held-out evaluation molecule from supplying gate-training outcomes through
another component while avoiding fold-specific repeated supervision generation.

Every masked training pool must retain at least 48 structures (16 initial + 32
new queries). If not, stop at a feasibility checkpoint and report the missing
coverage; do not replace assays, lower the minimum or enlarge data automatically.
No outcome/class-balance filtering is allowed. One-class prefixes stay in the study.

The four groups are the principal dependence units. Shared scaffolds and similar
compounds remain; no chemical OOD or population-wide family generalization claim
is supported. This cohort has prior development exposure, so even grouped results
are exploratory. New development recipes must be frozen before evaluation, with
no manual outer-fold result inspection while selecting configurations.

## 4. Common simulator and predictor settings

Primary assay budget **B = 32 newly delivered labels**, initial labels **n0 = 0 or
16**, unit assay cost, batch size one, immediate deterministic delivery, no
missingness. Initial labels are a common sunk observation allocation and excluded
from discovery counts. Report total observed labels as well. Uniform, seeded
initial sampling must not force a positive, reject a seed or balance outcomes.

The deliberately synchronous setting isolates computation allocation. It does not
test asynchronous scheduling, lab latency, multifidelity assays or a physical
digital twin. Those require later protocols, not added scenarios in this grant.

| Predictor stratum | Frozen specification and limitation |
| --- | --- |
| Primary random forest (RF) | 64 trees, max depth 6, min leaf 2, sqrt feature subsampling, bootstrap true, no class weighting, one thread; no predictor hyperparameter search. Probabilities are uncalibrated. |
| Secondary Tanimoto-neighbor | Public, deterministic 16-neighbor graph; p(i) = (1 + sum similarity(i,j) y(j)) / (2 + sum similarity(i,j)), summing observed graph neighbors. Beta(1,1) smoothing is an adapter choice, not a reproduced author model. |

Use the same per-campaign predictor seed, tie-breaking and public caches across
paired policies. RF uses a common seeded uniform fallback until two classes are
observed; fit only then and charge it. Constant probabilities use common seeded
ties. No pseudo-positive or hidden-label repair. Record predictor diagnostics on
delivered observations as selection-biased diagnostics, not pool calibration.

Each campaign has a maximum CPU budget C in addition to B. Charge feature/graph
preparation, scoring, all fits, gate inference, planning and fallbacks. An initial
common fit is not free. Offline gate/target-generation costs are reported
separately and included in the total project budget; report amortization rather
than presenting an offline-trained policy as free computation.

## 5. Operations, planner and learned gate

**REUSE:** choose the highest cached surrogate score without refitting.
**UPDATE:** refit using delivered labels, then use the same cheap acquisition.
**PLAN:** update if needed, then invoke the matched nonmyopic planner. Cached
values from interrupted work cannot become new recommendations.

RF planning uses an **ENS-inspired approximation**, not an exact ENS reproduction:
a shortlist of at most eight candidates, formed from four highest cached means
and four highest p(1-p), deduplicated and filled deterministically. Include the
cheap winner. For candidate i and r remaining assays, clone/refit the same RF
under hypothetical y(i)=0 and 1, then score

`p(i) * [1 + top_sum(r-1, p_after_i=1)] + (1-p(i)) * top_sum(r-1, p_after_i=0)`.

The tail is a nonadaptive greedy batch, excludes observed points and i, and is
clipped to eligible pool size. No true outcome enters hypothetical updates. The
secondary neighbor planner evaluates this full-remaining-budget expected top-sum
objective across all eligible candidates using the stated neighbor adapter.
Describe it as an **ENS-objective neighbor reference**, not reproduction of the
authors' full implementation or published performance. All PLAN-capable policies
share identical planner, shortlist and cache opportunities.

The gate comprises two **Ridge(alpha=1)** regressors predicting terminal-hit
differences UPDATE minus REUSE and PLAN minus REUSE. No gate architecture search.
Scale using training components only. Features: remaining B/C fractions, observed
counts/class fraction, new deliveries since last fit, cached ranking margin and
dispersion, public neighbor support, prequential errors recorded before each
delivery, availability masks, and previously charged operation costs. Computing
features must not invoke planning or fit an extra ensemble. Prequential errors
are history signals, not unbiased calibration estimates.

Cost estimates use observed past-operation EWMA (weight 0.5 on the newest cost),
initialized from outcome-blind technical profiles. Choose the feasible operation
with largest positive predicted terminal-hit gain; break ties by estimated cost,
then fixed REUSE/UPDATE/PLAN order. With no positive predicted gain, reuse. Missing
model state uses the common cold-start rule. The gate stays fixed during outer
evaluation; only the surrogate and declared cost history update.

Estimated feasibility is not a resource guarantee. A charged CPU interrupt discards
partial work. Use a cached cheap selection only if its computation fits the
remaining C; otherwise stop new requests and retain the shorter campaign. Never
finish B using free fallbacks after exhausting C. Report all acquired counts and
interruptions. No inherited M1 confidence or safety certificate applies.

## 6. Mandatory matched comparisons

Run eight arms under both predictor strata, n0 settings and CPU regimes:

| ID | Policy | Purpose / fixed tuning allowance |
| --- | --- | --- |
| R | Uniform Random | Basic discovery and overhead reference |
| G1 | Greedy, update after every delivery | Strong principal fixed baseline |
| Gk | Greedy, update every k deliveries | k in {2,4,8}, training components only |
| U | Update each delivery, select largest p(1-p) | Uncertainty heuristic; not a calibrated-UCB claim |
| P | Always PLAN | Same planner and hard budgets as the gate |
| T | Cached threshold operation rule | Three configurations below, training components only |
| E | Exp3 operation portfolio | Same three operations; gamma=0.1, equal initial weights; selected operation receives observed next binary outcome only |
| L | Learned operation gate | The proposed strategy |

For T, configurations (staleness k, top-margin threshold tau) are (2,0.02),
(4,0.05), (8,0.10). If staleness >= k, UPDATE; otherwise if cached margin <= tau
and at least eight assays remain, PLAN; otherwise REUSE. Apply common startup and
resource feasibility rules. Exp3 is a practical adaptive comparator, with
importance-weighted observed reward and standard exploration mixture; no
stationary-bandit regret guarantee is claimed for this adaptive environment.
Do not compute every arm's expensive nominee to select the next operation.

At every step all arms use the same cost estimator and hard guard. If a fixed
arm's requested UPDATE/PLAN is estimated infeasible, it uses REUSE if feasible;
otherwise it stops. Thus P means plan while feasible with a charged cheap tail,
not a deliberately stranded baseline. E samples only estimated-feasible
operations, renormalizing its exploration mixture and recording the actual
selection probability for its importance-weighted update. An unexpected overrun
uses the interrupt rule above. Synthetic profiles log scoring/update/plan costs
separately to initialize the common estimator without extra biological data.

Select Gk/T by training-component-balanced mean H/B, averaged equally across the
two n0 and CPU settings and two tuning seeds; ties use less CPU then the fixed
configuration order. Precompute the six generic configurations on training-mask
pools, then exclude the held-out component for each selection. No outer-outcome
selection of a best baseline. Primary contrasts are **L-G1, L-T and L-E**.
Gk/P/U/R are required contextual comparisons, not controls dropped after results.

## 7. Counterfactual supervision and seed separation

For each predictor: six masked assays x two n0 x two behavior traces = 24 prefix
campaigns of B=32. Traces are G1 with seed 101 and a per-query 50/50 Random/G1 mix
with seed 211. Snapshot after 0,8,16,24 new deliveries (96 states per predictor).
From each snapshot, force each of the three operations, then continue with common
G1 under the remaining B and each of two C regimes. Subtract prefix CPU, retain
infeasible states with reasons and pair continuation randomness. At most **576
branches per predictor** supply realized terminal hits and actual computation.

The regression target is the paired terminal-hit difference for this forced
operation followed by G1, not an optimal policy value or proof of causal benefit
under arbitrary trajectories. Correlated branches are training examples, not
independent scientific replicates. No future-label feature or branch target enters
outer evaluation. Report support gaps and operation frequency.

Tuning seeds: **301,401**. Outer evaluation seeds: **1009,2027,3041,4051,5059**.
Use fixed hash-derived per-assay streams and separate fitting/branch streams;
reuse the same initial draw and evaluator randomness across paired arms. These
are new development seeds, not a new unexposed cohort.

RF ablations at Ccheap, all five evaluation seeds: remove history/error features
and refit the gate; disallow UPDATE; disallow PLAN. The latter two use the same
gate with restricted action sets. No-history removes delivery/class/error/staleness
and past-cost features while retaining remaining budgets and current public/cached
ranking features. Report attribution limits of these interventions.

RF budget transfer uses B=16, the first three evaluation seeds, both n0/C regimes
and G1/T/E/L. Freeze the B=32-trained gate and chosen controls; do not retune for
this sensitivity. A failure limits transfer claims without rewriting the primary
endpoint. No new delay/missingness/more-data sweep is included.

## 8. Outcome-blind CPU calibration and feasibility stop

Before biological-label campaigns, use explicitly synthetic labels and public or
constructed binary features at N={128,303}, n0={0,16}, B={16,32}, both predictors,
G1/P and three technical repeats: **96 technical campaigns**. These synthetic
outcomes never count as molecular evidence or gate supervision.

For each predictor/n0/B, define Ccheap = 1.25 x maximum measured G1 CPU over N and
repeats; Cplan = max(Ccheap, 1.25 x maximum P CPU). Include preparation and the
common initial fit. If Cplan/Ccheap < 1.5, omit the Cplan regime, retaining the
predeclared primary Ccheap cap and reducing work. Report the absent separated
CPU regime explicitly. This is a technical maximum from three repeats,
not a statistical coverage guarantee. Save calibration before viewing development
outcomes; do not choose caps to favor L.

**Resource-fit stop:** either calibrated cap above 30 CPU-seconds per campaign,
an unenforceable hard limit, or insufficient training-mask coverage stops dependent
molecular work for owner review. Do not truncate the always-plan cap, reduce its
shortlist, change predictors or force an artificial bottleneck after this gate.
The 30-second cap is a proposed admission bound, not a measured RF runtime.

## 9. Workload and fresh resource grant requested

| Work | Intended upper-bound units | Calculation |
| --- | ---: | --- |
| Synthetic calibration | 96 | 2 N x 2 n0 x 2 B x 2 predictors x 2 policies x 3 repeats |
| Development prefixes | 48 | 2 predictors x 6 assays x 2 n0 x 2 traces |
| Forced continuations | 1,152 | 2 predictors x 96 states x 3 operations x 2 C |
| Gk/T tuning | 576 | 2 predictors x 6 assays x 2 n0 x 2 C x 2 seeds x 6 configurations |
| Main paired comparison | 1,920 | 2 predictors x 6 assays x 2 n0 x 2 C x 5 seeds x 8 arms |
| RF ablations | 180 | 6 assays x 2 n0 x 1 C x 5 seeds x 3 ablations |
| RF B=16 transfer | 288 | 6 assays x 2 n0 x 2 C x 3 seeds x 4 arms |
| **Total intended** | **4,260** | Includes correlated branches and synthetic work |

Maximum **4,400 attempted units**, including up to 140 failed/reproduction/diagnostic
attempts. No replacement seed or parameter change based on an unfavorable result.
Timeouts, interruptions and failures remain in the registry. Never describe these
counts as thousands of independent assays, molecules, families or replications.

Each attempted unit reserves at most **31 aggregate CPU-seconds**: up to 30 for
scientific computation and one for bounded startup/serialization, with a 120-second
wall timeout. Input parsing/writes have their own charged project utilities.
Build a real interruptible, single-thread executor; if it cannot enforce this
bound on the admitted platform, do not launch campaigns there. Non-scientific
overhead exceeding its reservation is not silently excluded: stop and reconcile
within the total cap. Synthetic profiling may stop sooner than its full unit cap.

| Project allocation | CPU-hours ceiling |
| --- | ---: |
| Implementation, guards, constructed checks and setup | 4 |
| Synthetic resource admission | 1 |
| Prefixes, branch targets and gate fitting | 11 |
| Control tuning | 5 |
| Main comparison | 17 |
| Ablations and budget transfer | 4.5 |
| Analysis, reproduction/retry reserve, return, cleanup and delivery | 5.5 |
| **Fresh total** | **48** |

4,260 x 31 seconds = 36.6833 CPU-hours of intended unit reservations, leaving
11.3167 hours for fitting, engineering and other charged utilities. This is a
conservative reservation calculation, not a runtime forecast. Stage ceilings and
the overall ceiling both bind. Failures consume budget; no old allowance is reused.
Do not borrow between stages or expand work without an owner amendment. Stage
under-runs remain unused; limited retries must fit the final reserve and total cap.

**Placement:** local at most one CPU / 512 MiB for independent engineering,
constructed checks and analysis; dr-train at most three workers, each one
CPU-equivalent / 4 GiB. At most four workers combined, BLAS/OpenMP threads=1,
aggregate CPU limits and initial core affinity as previously permitted. Reserve
capacity for platform/return work before launching. All timed molecular comparisons
run on dr-train; pair within the same worker and randomize policy order. Record
hardware, software and affinity. Never compare local and remote timings as if
matched. No GPU, paid service or API budget is requested.

After approval only, use existing chaw SSH credentials/profile without changing
keys, config or privileges. Admission must demonstrate actual CPU/memory/timeout
enforcement before copying permitted inputs. If unavailable, report and request a
placement amendment; do not silently use an unmatched platform.

Proposed fresh private root: `.local/m2-selective-compute-20261108-v1`;
remote root: `/home/chaw/curaloop-tasks/m2-selective-compute-20261108-v1`.
Both remain uncreated by this plan. Start a fresh closed-by-default ledger only
after approval and preflight. Stop deadline = release + **96 hours**, with a reserved
return/cleanup window. Actual completion may be much earlier; no background waiting
is needed to consume the full allowance. Verify complete evidence/code/data return
and reread hashes before deleting only the resolved, explicitly owned remote root
and its exact exports, then verify absence. Keep old task roots/ledgers untouched.

## 10. Endpoints and uncertainty

Primary endpoint: newly delivered binary positives H at the joint **B=32, Ccheap**
limit, excluding initial labels. Average seeds and n0 equally within assay, assays
equally within component, then the four components equally. Report each component
and raw paired L-G1/L-T/L-E differences, not just a pooled winner. H/B uses the
assigned B even when C stops acquisition; report actual requested/delivered counts.

Secondary: discovery curve versus acquisition budget, area under that curve,
H/B, total charged CPU, wall time, update/planning/gate fractions, fallback and
interrupt counts, predictor diagnostics, Cplan frontier, no-history/action ablations,
neighbor stratum and B=16 transfer. No conversion of CPU into money/lab cost or
clinically meaningful benefit. Report offline training cost and sensitivity to
amortizing it over 1,10,100 future campaigns, without claiming demand exists.

Show all four component effects and their range. A paired seed-vector bootstrap
(10,000 resamples of the five shared seed indices, jointly across all fixed assays
and arms) may produce a 95% **conditional seed-variability interval on this fixed
cohort**. It is not a biological-family confidence interval. Training seeds and
counterfactual branches do not increase evaluation independence.

With four groups, an exact two-sided sign-flip test has only 16 assignments and
minimum attainable p=0.125. Do not require p<0.05 for exploratory potential or
claim confirmatory significance using dependent seed/campaign rows. The owner has
not specified a minimum economically/clinically meaningful effect or a
noninferiority margin; report effect sizes and uncertainty without inventing one.

## 11. Predeclared decisions for owner consideration

| Decision | Rule and implication |
| --- | --- |
| Technical PASS | Complete registered work or declared collapsed regimes; zero protected-data/future-feature/budget violations; matched controls, full accounting, returned artifacts and reproducible aggregate report. All exclusions/failures retained. A breach invalidates affected inference. |
| PROMISING_DEVELOPMENT_SIGNAL | Technical PASS; RF at Ccheap has positive component-balanced mean H differences versus each of G1, T and E; L-G1 positive in at least 3/4 components; full L has positive mean advantage over its no-history ablation; no gain explained by unequal budgets, hidden information or uncharged work. This is a proposed exploratory consistency rule, not a significance or practical-effect threshold. Intervals may cross zero and must still be shown. |
| EFFICIENCY_SIGNAL_ONLY | Equal recorded discovery with lower CPU but no positive primary discovery signal. Describe exact empirical equality; do not claim noninferiority without an owner-approved margin. |
| INCONCLUSIVE | Valid but mixed/weak effects, insufficient component support, incomplete matrix, or resource/coverage stop. Report what was learned; no automatic extra mechanism, tuning sweep or data expansion. |
| NOT_SUPPORTED_IN_THIS_STUDY | No incremental benefit over simple/adaptive controls across the measured regimes, a gate reduced to constant/fallback behavior, or extra overhead without discovery gain and no history contribution. This does not prove every future variant fails. |

Neighbor or Cplan failure limits the supported domain; universal wins are not a
requirement for a conditional strategy. Report all results and failed ablations
alongside any RF primary signal. An all-cheap controller may have an efficiency
finding, but does not establish useful learned planning allocation.

**M2 completion is not publication readiness.** Even promising results require
independent protected evaluation, stronger generalization evidence, a defensible
novelty argument and manuscript/reproduction review. Do not open the existing
final set to resolve an ambiguous development result. The owner decides whether
to design M3, revise a narrow claim, stop research or pursue product work separately.

## 12. Deliverables, gates and current approval boundary

After an execution release, perform these stages in order; independent engineering
and analysis may run locally alongside admitted remote units:

1. Freeze code/config/hash manifest and fresh resource ledger; validate information
   boundaries with constructed sentinels. No labels before identity/protection checks.
2. Check the outcome-blind training mask, resource enforcement and synthetic caps.
   Stop for owner review on a substantive feasibility change.
3. Generate masked development training continuations, fit grouped gates and choose
   declared controls. Freeze fold artifacts and configuration before outer outcomes.
4. Run the main matrix, declared ablations/transfer and bounded reproduction checks.
   Log negative/partial results without manual outcome-dependent redesign.
5. Produce aggregate results, per-group effects, uncertainty, compute ledger,
   operation/failure analysis, claim limits and full private return/cleanup receipt.
   Commit English documentation/code/aggregate evidence to main; stop before M3.

The [disabled plan configuration](../../research/configs/m2_experiment_plan_20261108_v1.json)
is a specification, not an executable dispatcher. This planning delivery reads
only authored metadata/receipts and changes guidance. It creates no scientific
clock or study root. The required next decision is owner approval or amendment
of **this complete M2 scope, development-label/counterfactual access and fresh
48 CPU-hour / 96-hour grant**. No execution is inferred from contribution approval.

## Evidence basis and reading limits

Data counts/expected identities come from the existing
[feature-cohort receipt](../evidence/plan-a-20261105-v1/feature-cohort-v2-result.json),
[data inventory](../03_research/LOCAL_DATA_INVENTORY_20261107.md), dataset card and
the private LR-M12 admitted-input metadata. No six-pool payload was reopened for
this plan. Expected historical hashes are not new raw-file admission checks.

Method/control choices follow the scoped [M2 reading receipt](../02_literature/M2_READING_RECEIPT_20261108.json)
and contribution matrix: [ENS](https://proceedings.mlr.press/v70/jiang17d.html),
[GP-Hedge](https://arxiv.org/abs/1009.5419v2), MolPAL, ANS, BMPS, Learning Active
Learning and online acquisition portfolios. Proposed RF/gate/Exp3 adapters and
numerical budgets are design decisions for this experiment, not reported author
results or proof that the method will succeed.
