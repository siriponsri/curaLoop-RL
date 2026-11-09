# LR-CF1 controls and blinded admission protocol v1

**Owner choice A recorded; no confirmation values inspected.**

This implements the approved LR-CF1 envelope, not a new selector. Primary/
confirmation AIDs are canonical identifiers; conflicting SI codenames remain
aliases. The [metadata freeze](../evidence/lr-cf1-20261109-v1/metadata-admission-v1.json)
selects628/677,1040/1254,2661/2821,449739/489005,485270/492964 and485273/493155,
in numeric AID order. Six whole files passed Git-blob authentication. There is no
replacement after observing labels or performance. Other candidates and failed
source attempts remain recorded.

## Data admission before value analysis

Use authenticated compiled exclusion metadata only. Do not open any original
final16 payload. A Python3.12/RDKit2026.09.1 protection worker uses the same
canonical/isomeric-SMILES convention as that index; no new salt, charge, isotope
or tautomer normalization. Read source identifiers/SMILES first, exclude invalid
structures, all members of any within-file canonical-duplicate set, and exact
protected matches. Only then parse primary labels for retained records. Never
read a protected record's labels into a model or evaluator. Report safe aggregate
attrition, not protected identities. Shared compounds across distinct development
targets remain legitimate assay observations and are reported as dependence.

The source has binary Primary labels, numerical Score, and a blank-or-observed
Confirmatory field. Determine confirmation presence from the blank marker alone;
do not convert an unobserved value into0. Retain confirmation cell text opaquely
for an evaluator. Observation-supported U consists of retained primary hits with
a present confirmation. It must be nonempty for a campaign to be evaluable.
One-class/zero-positive confirmation outcomes are retained; they cannot exclude
a campaign or change the cohort. Require at least four evaluable campaigns and
at least two source-provider experiment blocks. Provider grouping is a conservative
reporting convention, not proof of biological independence. All selected targets
share one historical annotation-connected component; no family-generalization
claim is supported.

Enforce source ceilings before fitting: at most six whole files,1GiB source
transfer,2M primary rows and100k supported confirmation observations. Structural
and observation attrition are frozen before value analysis. A gate failure is
reported without adding another file or lowering an eligibility requirement.

## Features and structure groups

Modeling features use the source's radius2/1024-bit Morgan fingerprint calculation
under RDKit2022.09.4, from original retained source SMILES. A compact uint8 on-disk
representation may be converted to the source float32 input without changing bits;
check the conversion explicitly. Protection canonicalization and model features
are separate versioned operations linked by immutable source row identifiers.

The source MVS-A class may receive the lossless uint8 binary matrix: pinned
LightGBM3.1.1 converts non-floating matrices to float32 internally. This preserves
the full campaign and exact feature values while avoiding redundant dense copies.
Require constructed float32/uint8 source-model prediction/importance concordance
before using this memory adapter. It is a declared representation/resource
adaptation, not a reduced cohort, weaker model or correction to the author code.

Primary groups are RDKit Murcko scaffolds with chirality omitted. Empty Murcko
scaffolds receive an explicitly labelled acyclic fallback: the generic heavy-atom
topology of the complete molecule, atoms converted to carbon and bonds to single
by MakeScaffoldGeneric. Distinct topologies are distinct operational groups.
Do not treat an empty scaffold as one universal group or count every acyclic
compound as a unique ring scaffold.

For a fixed sensitivity, form greedy leader clusters using the same1024-bit
fingerprints and Tanimoto similarity>=0.60. Visit canonical SMILES/source-row ID
order; assign to the first qualifying leader, otherwise create a new leader.
No dense whole-library pairwise matrix, outcome-dependent threshold, later
regrouping or selection of the favorable definition is allowed. Report both D
definitions. These groups are operational chemotypes, not validated lead series.

## Six rankers, shared information

| Ranker | Frozen rule |
| :--- | :--- |
| Random | Uniform seeded permutation of U |
| Primary Score | Higher retained source Score first; no confirmation training |
| MVS-A | Lower importance first from the unchanged author class/default-string branch |
| GBM | Higher primary-hit probability from that same fitted LightGBM model; no extra fit |
| RF |128 trees, default bootstrap, sqrt feature sampling, no depth cap, leaf minimum1, n_jobs1, fixed seed; fit only retained primary labels |
| Nearest primary hit | Maximum Tanimoto similarity to another retained primary hit, excluding self; a singleton reference set receives0 |

Fit each primary-only model once per campaign/seed and cache its ranks. RF's
single-class probability is1 if the sole training class is1, otherwise0; no
class-balance filter or confirmation-based model selection. Seeds are90101,
90113,90133,90149 and90163. Rank ties use a shared deterministic SHA256
seed/source-row-ID key and final row-ID tie break. Models, scores and grouping
never use confirmation-positive values.

Keep the author's100-iteration/default1.0 regularization/0.95 feature fraction
conventions, including observed checkpoint/leaf-loop behavior. Set thread count1
in the default parameter dictionary only as a declared resource restriction.
Do not use the source's broken custom-dict branch or silently repair its algorithm.

## Three common portfolio operators

1. Top-ranked: first B positions of the ranker.
2. Ranked cluster round-robin: order Murcko/fallback groups by their best-ranked
   member, retain within-group rank order, and take one per group in repeated
   passes until B. Acyclic groups follow the same rule.
3. Classical max-min: start with the top-ranked compound; repeatedly maximize
   minimum Tanimoto distance to selected compounds across all U, using rank order
   only to resolve distance ties. Cache each prefix up to the largest B. This can
   intentionally make different rankers similar; retain those redundant controls.

Apply all three operators to every ranker/seed, on the same U and at identical
B. Budgets are ceil({1,2,5,10,20}% of |U|), with duplicate integer budgets merged.
Freeze actual counts and the complete cell manifest after blinded support checks,
before confirmation analysis. At most2700 cells. H(B) counts source-confirmed
positives; D(B) counts fixed groups containing at least one selected positive.
Missing/unperformed confirmation is never a negative; source0 combines inactive
and inconclusive. No calibrated clinical or monetary interpretation is attached.

## Reproduction and resource release

Before portfolio value analysis, verify retained source Score mapping/direction,
the original source fingerprint calculation, and direct author MVS-A importance
against an independently accumulated bounded-memory calculation on the same
trained model. Preserve the source's actual iteration arguments and leaf loop.
Use rtol1e-9/atol1e-8 for accumulated scores; report source/adapter differences.
This is a qualified processed-repository code/score reproduction. Exact source
figures, raw-assay history or unmodified binary dependency builds are not claimed.
The original paper's full-primary percentile thresholds differ from fixed-count
selection within U; report this endpoint adaptation explicitly.

Calibrate actual CPU/RAM and verify one-core-equivalent cgroup,4GiB memory and
zero swap before scientific jobs. Prepare a CPU-only Python3.8.16 environment
with matching core scientific package versions where available; retain exact
wheel/interpreter hashes and compatibility evidence. Never install GPU packages
or modify an existing environment. Require the exact projected matrix to fit
remaining stage and48h total reservations before releasing evaluator values.
Keep source acquisition, failures, setup, profiling, feature calculation, fitting,
selection and return costs distinct from confirmation counts.

## Analysis and stopping

Report all18 nominal arms, every campaign/block effect, H/D curves and hit/coverage
tradeoffs including unfavorable results. Show conditional seed variation; four
provider blocks and one annotation component do not justify confident population
or biological-generalization intervals. No seed is an independent campaign.
No post-outcome parameter, margin, budget, group or method selection is permitted.
If fixed diversified baselines explain the tradeoff, recommend new-method NO_GO.
Otherwise propose one separately costed mechanism for owner review, without
training it. Complete offline product/paper/reproducibility handoff either way.
