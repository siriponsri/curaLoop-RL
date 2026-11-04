# Goal 2: real-data planning prototype

Owner amendment, 4 November 2026: use real, paper-backed datasets and benchmarks;
SSH to dr-train is permitted. This supersedes Goal 1's synthetic-only/no-SSH
proposal. The parent is the sole repository writer; three agents independently
research methods, datasets and English evidence. No final study is authorized.

## Research decision and acceptance

Test whether a content/time/capacity upper relaxation eliminates root actions
while preserving an unpruned finite-model rollout decision. Compare discoveries
and measured computation on real historical assay labels. Tiny exact cases
test mathematical and implementation correctness; they are not the empirical
dataset. A useful prototype is not automatically a novel algorithm. Ordinary
scenario-wise perfect-information relaxation and branch-and-bound are known
tools. A failure to improve total computation falsifies this version's proposed
computational advantage. Do not select more favorable seeds/tasks afterward.

## Real input and benchmark identity

Reuse the three already exposed, hash-pinned NCATS challenge training derivatives:
AhR (AID 743122), PPAR-gamma (743140) and p53 (720552); 600 candidates each,
canonical isomeric RDKit structures and Morgan radius 2, 1024-bit nonchiral fingerprints.
The existing normalization, missing-label exclusion and conflicting-duplicate
removal remain unchanged. Raw/full cohort files stay ignored; preparation audit
receipts and hashes are public in the existing development evidence packet.
Raw and cohort hashes are inherited verbatim from ncats_development_v1.json.

The [original challenge paper](https://doi.org/10.3389/fenvs.2015.00085), published
14 January 2016 in volume 3 (2015), supports these assay sources. The
[official data index](https://tripod.nih.gov/tox21/challenge/data.jsp) defines
1 = active, 0 = inactive. The paper's 8,043 training samples differ from the
pinned per-endpoint export row counts of 8,169, 8,184 and 8,634. Our 600-row derivatives are not an
exact leaderboard reproduction. Existing provider public-domain evidence is
recorded in [the rights review](DATA_RIGHTS_FOLLOWUP_20261104.md).

This is a NEW delivered-positive/deadline benchmark adaptation on a real
established dataset, not reproduction of its predictive classification metric.
The three correlated toxicology/pathway endpoints do not supply independent
target-family replication or therapeutic activity evidence. Final roles remain
untouched. [External acquisition](GOAL_02_DATASET_ACQUISITION_V1.md) prepares
FS-Mol and distinguishes its potency-threshold labels from sparse screening hits.

## Frozen scientific contract

- Primary paired contrast: content-pruned versus unpruned rollout, which MUST
  agree on selected actions and H(T); their measured computation is the target.
- Primary scientific metric H(T): NEW active labels delivered at or before T;
  seeds, predictions, pending work and missingness are not new hits.
- Uniform 24-label starts, seeds 0/1/2, all 600 candidates, capacity 2, unit cost 1,
  budget 12 and deadline 8 simulated units. Retain zero-active starts.
- Conditions: common duration 2; heterogeneous equiprobable 1/2/4, independently
  keyed by task/seed/candidate with no label input. Both are synthetic operations.
- 10 methods, 180 runs: Random; frozen empirical-model Greedy; updated empirical
  Greedy; analytical posterior-mean Greedy; nearest-hit; cheap pending-cluster
  WAIT; CPE rollout; unpruned hit rollout; cardinality-pruned and content-pruned
  hit rollout. All methods share feasibility, initialization and duration draws.
- The matched planning trio uses identical beliefs, shortlist and greedy
  continuation. Public features define 12 farthest-first Tanimoto clusters;
  independent cluster Beta(0.5, 9.5) latents update from delivered labels only.
  Each decision samples 16 full label/duration worlds. Model-based arms share
  this underlying model; structure/random controls do not use its scores.
  Analytical posterior-mean Greedy avoids particle noise.
  Frozen-model Greedy retains initial empirical scores. There is no neural/RL
  controller, cross-target pretraining, hyperparameter search or transfer.
- Enumerate all subsets up to free capacity from the 3 highest empirical-score
  candidates, plus WAIT when pending. After any root action, await the next
  delivery before work-conserving Greedy continuation. Partition hypothetical
  worlds by public event time and JOINT delivered labels before any new choice.
  Policy-known acceptance times provide ages; residual duration uses D-age | D>age.
- The cheap WAIT rule waits if the leading candidate shares a cluster with
  pending work and time remaining is at least max(duration)+min(duration).
  It uses no actual pending label/due time and has no tuned coefficient.
- CPE rollout maximizes the expected sum of previously completed NEW experiment
  counts at each subsequent launch, using the same selector. This is an
  [Azimi2011-inspired adaptation](https://proceedings.neurips.cc/paper_files/paper/2011/file/3a066bda8c96b9478bb0512f0a43028c-Paper.pdf),
  not its policy-switching generator, theorem or best-value reproduction.
  ENS/ANS and modern trained molecular predictors remain future strong controls;
  this prototype cannot claim superiority over those unimplemented methods.

## Bound semantics and proof obligations

For each forced root action and each finite world, include positive pending
requests that finish by T exactly once. Their unavoidable remaining processing
occupies workers, even if they are inactive or late. Give the planner perfect
knowledge of all remaining labels/durations, retain unit-cost budget and the
aggregate available worker-time, but relax machine packing and nonanticipativity.
Only include a new positive job if it can finish after the earliest free slot.
Take shortest positive durations until either budget or aggregate processing
is exhausted. This is an upper bound: every feasible future positive set meets
these necessary constraints; greedy shortest lengths maximize its cardinality.
Average over worlds. Compare with the looser pending-count+remaining-budget
cardinality bound. The feasible greedy rollout supplies a lower bound.

Skip an action only when its upper bound is strictly below the best evaluated
lower value. Deterministic ties retain the work-conserving Greedy action first.
The reported gap is relative to the shortlisted ROOT actions and finite model;
continuation relaxation permits all remaining pool candidates. It is not a
global root-action optimum, biological guarantee or new theorem. The finite
worlds are an empirical approximation, with no Monte Carlo coverage certificate.
Small support can become artificially informative after few hypothetical labels;
fresh worlds at real decisions avoid zero surviving particles, but do not
remove this bias or provide whole-campaign regret guarantees.

Exact nonanticipative tiny-state dynamic programming must enclose fixed-rollout
values between lower/upper bounds, test informative/irrelevant/XOR labels,
deadline reversal, direct pending reward, residual durations and binding budget.
Real run traces must verify shared scheduling, conservation, restoration and
identical choices for the pruning trio. Bounds/action certificates are not
evidence that the simple chemical posterior is calibrated.

## Compute, stopping and analysis

Use existing dr-train IP SSH profile with strict host verification. Inspect
live CPU/memory/load/jobs and lock availability; no job termination, key/config
change or GPU use. One serial process pinned to one allowed CPU, nice 19,
one-thread environment, 1 GiB virtual-memory ceiling and 1,800 cumulative run-wall
seconds (including model/bound overhead; external timeout also applies).
No paid resources or dependency installation. This is a bounded Goal 2 allocation,
not an estimate or approval for a 12-family final sweep.

Freeze exact source/config/input identities before run 1. Canary: 10 included
AhR/seed0/heterogeneous arms, then inspect failures/accounting/pruning concordance
before the remaining 170. Stop on any error, invalid bound, conservation/privacy
failure, output collision or cap. No retry with the same identity. Retain all
attempts and unfavorable outcomes. Raw runs stay ignored; publish their hashes,
metrics and decision diagnostics. Record policy wall/CPU/RSS separately from
simulated assay time. Compare paired win/tie/loss and effect distributions;
report seed variation descriptively, without treating 18 pairs as independent
biological tasks or claiming equivalence. No confirmatory margin is selected.

Cheap-control timing caveat: the common wrapper constructs 16 worlds even for
Random, analytical posterior mean and nearest-hit. Their reported costs include
avoidable wrapper overhead and are not optimized baseline runtime benchmarks.
The primary unpruned/cardinality/content trio has matched construction overhead.

Execution disclosure: one local integration smoke on exposed AhR/seed0/
heterogeneous/content-pruned ran before the freeze. Only stdout metrics survived;
the missing raw trace is explicitly recorded in the smoke disclosure. No
scientific parameter changed from that outcome. The remote canary repeats that
combination as a separate disclosed integration check, not independent evidence.
The formal driver writes immutable attempt-start markers and rejects unresolved
attempts, so killed runs cannot silently disappear or be replayed.

At completion report whether pruning is computationally useful, whether any
discovery effect survives cheap controls, and which claims failed. The wider
12+ family dataset/split study and final journal manuscript remain later goals.
JCAMD allows appropriate retrospective validation for genuinely novel methods;
this exposed three-endpoint prototype alone does not meet that standard.
