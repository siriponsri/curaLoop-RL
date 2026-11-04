# Materials and methods: historical and development studies

## Dataset and initialization

The pilot uses the frozen `curaloop-hiv-1.0.0` derivative described in the resource manifest. The downloaded DeepChem HIV source contained 41,127 rows; seven invalid SMILES were removed under the documented preparation procedure. A label-blind random sample of 1,200 valid rows was retained. Canonical SMILES, Morgan radius-2 fingerprints with 1,024 bits and nonchiral Murcko scaffold identifiers were derived with RDKit. Historical CA/CM labels were mapped to active and CI to inactive.

Each campaign began with 48 uniformly sampled labelled compounds, selected without inspecting activity. These labels were preexisting sunk information, excluded from new-hit counts and campaign cost. Ten seeds, 0-9, were paired across five independent policies. The candidate pool, initial labels and scenario constraints were common within a seed; results were not shared between policies.

## Predictors and policies

Greedy and margin-based Uncertainty used `StandardScaler -> LogisticRegression`, with liblinear, C=1 and a maximum of 500 iterations. Only initial and subsequently delivered Boolean labels were used for fitting. A one-class observed set caused a labelled Random fallback. Predicted probabilities were uncalibrated. Greedy selected high predicted activity; Uncertainty used proximity to 0.5 as a margin score.

Frozen tabular Q-learning and contextual-bandit controllers selected among Random, Greedy and Uncertainty. Each controller had been trained on 160 synthetic episodes using seeds 10000-10159. The reward was newly delivered active hits minus 0.01 times newly settled assay cost. Their state lookup and explicit unseen-state Greedy fallback were retained during HIV evaluation. No HIV label was used for controller training.

## Scheduler and metrics

The recorded scenario used budget 30, unit assay cost, concurrent capacity 5 and a common delay of two simulated steps, with no jitter or missing outcomes. Accepted requests reserved cost once. Delivered outcomes settled cost once. Only unique newly delivered active results counted as new hits; seed labels, predictions and pending outcomes were excluded. The budget identity was spent plus reserved plus remaining equals total.

The recorded AUC-DB is the left-step integral of cumulative delivered hits against settled cost, carried to the configured budget and normalized by budget times the maximum affordable assay count. It is not AUROC or average precision. The historical comparisons summarize within-assay seed variation and include exploratory paired-bootstrap contrasts against Random.

## Separate predictor audit

A custom whole-scaffold hash split at seed 42 produced 960 training and 240 test molecules, containing 36 and six actives respectively and no shared Murcko scaffold. Scaling and fitting used training rows only. The evaluator's labels and fitted model were never passed to campaign policies. This is not an official MoleculeNet/TDC leaderboard reproduction.

## Evidence preservation

The historical HIV artifacts are retained unchanged. The separate NCATS studies below have new execution identities, frozen configurations and public run packets. Their versioned research modules are separate from the production UI and do not make the research configs supported inputs to the application CLI. This manuscript revision reads those completed artifacts; it does not rerun campaigns or retroactively preregister results. Software tests and browser verification are separate from chemical or operational validation.


## NCATS fixed-control development study

The [development protocol](../03_research/NCATS_DEVELOPMENT_PROTOCOL_V1.md)
was frozen at commit `4091e209fed78d04d48b13ef8ad719257302f684` before the
108 method runs. NCATS training exports identify AhR AID 743122, PPAR-gamma AID
743140 and p53 AID 720552, with CSV active=1/inactive=0. They are historical
pathway/toxicology endpoints, not therapeutic-efficacy labels. Canonical
duplicate groups with conflicting labels were excluded in full. Invalid rows
were excluded and consistent duplicates collapsed. Fixed structure/identity
hash ranking selected 600 compounds per endpoint without activity in the rank.
Raw/export/cohort hashes and attrition are retained in the development packet.
The cohorts overlap chemically and belong to one source panel; they are
explicitly exposed development resources rather than independent final tasks.

Each endpoint used seeds 0/1/2, 24 uniformly sampled initial labels, unit assay
cost, budget 24, concurrent capacity 3 and simulated deadline T=12. Conditions
used common duration 2 or heterogeneous durations 1/2/4 from a candidate-keyed
schedule. Initial labels and operational realizations were matched across
methods while fitted policy states remained independent. Initial labels are
sunk knowledge and excluded from newly delivered hits. All outcomes due at T
are processed atomically and count; no new request starts at T. No missingness
was configured. Zero-active starts were retained with declared fallbacks.

The six methods were Random, frozen Greedy, retrained Greedy, nearest-delivered-
hit similarity, structural diversity and a matched pending-similarity penalty.
Predictive controls use StandardScaler and liblinear logistic regression with
C=1 and max_iter=500. The penalty subtracts 0.2 times maximum Morgan/Tanimoto
similarity to the current pending set from predicted activity. Excluding already
requested candidates is shared by every arm and is not the treatment. Newly
chosen simultaneous batch members do not diversify one another. This is a
finite-pool heuristic, not a reproduction of a probabilistic asynchronous method.
The included canary and complete grid used the same frozen settings; resume
verified identities instead of repeating completed campaigns.

## Fresh-environment reproduction

A separate detached local clone of `d57838d41b30d956c7fd72ac502c1765653fd087`
and a new venv with system-site packages disabled regenerated the three cohort
hashes from pinned source bytes. Seven exact-version wheels were installed
offline; pip check and recorded distribution-path checks passed. The frozen
108-run grid was then reproduced and compared for scientific metrics, event
histories, initialization, schedules, selected scores and non-timing counters.
Runtime and environment metadata were compared separately. The implementer,
base Python interpreter and Windows host were shared. This tests fresh-
environment reproducibility, not independent scientific review or a second
biological sample. The [reproduction report](../03_research/NCATS_REPRODUCTION_V1.md)
retains setup/driver limitations and exact command logs.

## Gaussian-surrogate development amendment

The [Gaussian protocol](../03_research/NCATS_GAUSSIAN_PROTOCOL_V1.md) was frozen
at `a9d9c8f0747be3e2c7d8c41b42dc53efd049a40a` after the logistic pilot was
exposed and before any new Gaussian method runs. Three fixed arms, GP mean,
pending-blind GP-UCB and pending-conditioned GP-UCB, used the same three pools,
starts, seeds and operational conditions, giving 54 new campaigns. The sklearn
1.8.0 GaussianProcessRegressor uses a unit binary-Tanimoto kernel, alpha=0.1,
optimizer=None, normalize_y=False and kappa=1. Pending locations condition the
covariance while the observed-label posterior mean remains unchanged; no actual
pending outcome enters acquisition.

Gaussian regression on Boolean labels is an approximation. Its means/scores
are not labelled calibrated probabilities, and the adapter is not a GP-BUCB
reproduction. Acquisition uses marginal optimistic multi-hit scores rather than
plain best-value expected improvement. Simultaneous new batch members do not
condition one another. One-class Random fallback remains explicit. The matched
Gaussian pair isolates its declared pending term; comparison against logistic
Greedy also changes the predictor and cannot isolate pending awareness.

## Preparatory audit and hierarchical sensitivity

The [candidate audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md) requests only
assay metadata, unfiltered membership and structures. No new candidate compound
outcome values are requested. Exact response hashes, versions, access errors,
feature-sample rules, overlap counts and unresolved data grants are retained.
Raw source AIDs are not a reproduction of prepared LIT-PCBA or DeepChem data.

The [design sensitivity](../03_research/DESIGN_SENSITIVITY_V1.md) simulates
family, task and paired-repeat variation under explicitly hypothetical profiles,
with 216 cells, 10,000 replicates per cell and five effect values. Its 1,080
reported rows are assumptions-driven planning outputs, not observed assay
effects or calibrated final-study power. Repeated seeds do not increase the
number of independent families. The owner's current direction is 12+ families
and effect estimates with uncertainty, without a confirmatory material-effect
threshold. No final allocation or outcome access is created by this preparation.
