# Confirmation-portfolio feasibility: methods and development results

This is an English research insert for owner/domain review, not a submission
manuscript or an independent final evaluation. The results section is completed
only after the private evaluator and independent aggregate checks finish.

## Question and relationship to previous work

Given a fixed number of follow-up confirmation measurements, which published
primary-only ranking and classical diversification controls recover source-
confirmed positive compounds and operational structure groups? This feasibility
study tests whether a distinct method-development opportunity remains after
strong shared controls. A diversity quota or scaffold-aware hybrid alone is not
claimed as a novel contribution: the
[MVS-A paper](https://doi.org/10.1021/acscentsci.3c01517) already examines structural
diversity and discusses such combinations. The related ranking/data-valuation
work [Hesse et al.](https://doi.org/10.1021/acs.jcim.4c01547) also limits a generic
ranking-plus-diversity novelty argument. Its separate dataset rows were not
imported. The older CuraLoop scheduler experiments remain separately reported
with their original inconclusive outcomes.

## Source, population and provenance

The source is the author-provided
[AIC_Finder repository](https://github.com/dahvida/AIC_Finder/tree/04c58e85188e724ec5ff44cbed2e7b960f6f3df3),
snapshot `04c58e85188e724ec5ff44cbed2e7b960f6f3df3`. The main paper and owner-supplied
25-page Supporting Information were reviewed. Thirteen of seventeen SI campaign
codenames conflict with repository aliases despite identical AID pairs. With
explicit owner approval, numeric primary/confirmation AIDs and the pinned
repository govern; conflicting names remain in the concordance register.
This is qualified processed-repository code/score reproduction, without a claim
of raw-assay equivalence or reproduction of every original paper table/figure.

Six whole campaigns were selected in numeric AID order before outcomes:
628/677, 1040/1254, 2661/2821, 449739/489005, 485270/492964 and 485273/493155.
The six files contain 1,341,881 source rows and total 77,576,150 bytes. Their
Git-blob identities and SHA-256 hashes were authenticated. Protection checks use
only previously authenticated compiled exclusion metadata, never original
final16 payloads. Exact protected canonical-structure matches, invalid structures
and all members of within-file canonical duplicate sets are excluded before
primary labels reach modeling. Source row ordinals remain stable; gaps in four
stored Pandas index columns are valid source filtering, not a reduced cohort.
The original failed dense-index assertion and four technical repairs are retained.

After these exclusions, 1,333,191 primary observations remain. The eligible
universe U is restricted to retained primary hits with a nonblank historical
confirmation field: 6,896 assay-specific observations across the six campaigns.
Eligibility uses observation presence, not confirmation positivity. Missing
confirmation is never imputed as a negative. Source confirmation 0 combines
inactive and inconclusive calls; original states cannot be recovered from that
collapsed field. These counts do not identify prospective whole-library policy
value, calibrated pharmacological efficacy or a causal wet-lab saving.

There are four source-provider blocks and one historical annotation-connected
component. Provider blocks are a reporting convention, not proof of biological
independence. Compounds shared across development targets remain legitimate
assay-specific records and create dependence. No biological-family generalization,
scaffold-disjoint extrapolation or chemical-OOD claim is made. All six campaigns
are exposed development data; final16 remains sealed.

## Molecular features, groups and rankers

Features use the original author radius-2, 1024-bit Morgan calculation under
RDKit 2022.09.4. Binary uint8 storage preserves exact float32 feature values;
source LightGBM converts nonfloating input to float32 internally. Constructed
float32/uint8 model and influence concordance precedes molecular fitting. No
campaign truncation, descriptor substitution or model reduction was performed.

Primary operational groups are nonchiral Murcko scaffolds. Empty scaffolds use
the complete molecule's generic heavy-atom topology, explicitly labelled acyclic.
The fixed sensitivity is greedy leader clustering at Morgan Tanimoto >=0.60,
visited in canonical-SMILES/record-ID order and assigned to the first eligible
leader. Neither grouping uses confirmation-positive values. These definitions
are operational structural groupings, not experimentally validated lead series.

The six rankers are uniform Random; higher primary Score; lower MVS-A influence;
higher GBM primary-hit probability; higher RF primary-hit probability; and maximum
Tanimoto similarity to another retained primary hit, excluding self. The nearest
reference includes unconfirmed primary hits, with singleton similarity 0.
Primary Score direction is fixed from source semantics. Model fitting uses all
retained primary labels only. Predictions are in-sample primary-ranking controls,
not an independent primary-classification generalization test.

MVS-A uses the unchanged author class and default-string parameter branch,
including its actual checkpoint convention (`num_iteration=0` uses all trees)
and upper-exclusive leaf loop. We preserve those implementation conventions
rather than silently repair them. Only the thread count is restricted to 1.
Each real MVS-A influence vector must agree with an independently accumulated
bounded-memory calculation on the same complete primary pool to rtol 1e-9 and
atol 1e-8. GBM probabilities reuse the same model. RF uses 128 bootstrap trees,
sqrt feature sampling, leaf minimum 1, no depth limit and n_jobs=1. Single-class
training is handled without discarding campaigns. No confirmation labels train
or tune any ranker.

Seeds are 90101, 90113, 90133, 90149 and 90163. Rank ties use a deterministic
SHA-256 seed/record-ID key followed by record ID. Each primary-only model is
fitted once per campaign/seed; calibration fits are reused in that matrix.

## Matched portfolios and outcomes

Every ranker receives the same three classical operators: top-ranked, ranked
group round-robin, and max-min Tanimoto diversity. Round-robin visits groups in
best-member rank order with ranked members. Max-min starts with the top-ranked
compound and repeatedly maximizes minimum distance across U; rank resolves ties
only. Therefore different rankers may yield redundant max-min controls, which
are retained. Prefixes are cached, without a whole-library pairwise matrix.

Budgets are ceil(1%, 2%, 5%, 10%, 20% of campaign U), merging duplicate integer
budgets. The actual five counts are frozen per campaign before value analysis.
Six campaigns, six rankers, three operators, five seeds and five budgets give
2,700 cells. All selections for a campaign are committed before the evaluator
converts any confirmation value. H counts selected source-confirmed positives;
D counts fixed groups with at least one selected positive. The fixed fingerprint
definition is reported as a sensitivity. H/B and D/B express counts per
confirmation, not currency, simulated assay time or clinical benefit.

All 18 arms and every campaign/budget are reported. Five-seed means, sample SD
and observed ranges describe conditional algorithm/tie variation. Seeds are
not independent biological units. Equal-campaign and provider summaries are
descriptive, without population confidence intervals or p-values. Paired H/D
contrasts use the same campaign, seed and budget. Empirical nondominance is
computed from H and D with at least one strict improvement; ties remain ties.
No meaningful-effect threshold is invented from the development results.

## Compute and reproducibility

The original ceiling is 48 CPU-hours and 96 elapsed hours, at most four combined
workers: one lightweight local worker and up to three dr-train scientific workers.
Each remote job has one-core-equivalent CPU quota, 4 GiB RAM, zero swap, an initial
assigned core, numerical threads 1 and CPU/wall/deadline enforcement. Real kernel
proofs accompany all scientific jobs. Models use an isolated CPU-only Python
3.8.16, NumPy 1.22.3, SciPy 1.8.1, pandas 1.4.4, scikit-learn 1.0.2 and LightGBM
3.1.1 environment. Interpreter and wheel hashes, core scientific versions and
full private artifacts are retained. Hardware-specific dependency binaries and
resource adaptations are disclosed; exact original binary builds are not claimed.

Whole-job CPU includes import, input validation, fitting, score checking and
serialization. Model-fit time is recorded separately. Feature calculation,
source acquisition, technical failures, calibration, selection, orchestration
and full return are separate costs. Conservative retained reservations are
reported separately from measured CPU. Original failed bootstrap/index attempts
are not erased or refunded. No GPU, paid model service or new selector is used.

## Development results

All 60 molecular fits and2,700 frozen portfolio cells completed. Independent
local recalculation reproduced every integer H/D result. At the predeclared 10%
reading example, MVS-A top-ranked achieved H=75.13 and D=45.37, whereas ranked group
round-robin achieved H=65.13 and D=65.13: -10.00 hits and +19.77 groups, descriptively
-13.31% and +43.57%. Fingerprint-group coverage changed44.30->56.57. Equal
campaign weighting and five conditional seeds were retained; this is not a
population interval or a new-method comparison. All 18 arms, all budgets and
campaign effects are available in [the results/evidence package](../03_research/LR_CF1_RESULTS_20261109.md).

At every assigned budget, the available group count exceeded B. Thus round-robin
used its first pass only and D=H in all 900 such cells by construction. The
coverage improvement and hit loss demonstrate an already-classical tradeoff;
they do not establish a novel selector. No new model selection, threshold tuning
or training followed confirmation exposure. Recommendation: NO_GO for a
quota-only method claim; separately review any distinct mechanism before funding
another training study. Final16 remains sealed.

Measured whole-cgroup CPU at result for60 molecular fits was 16,408.400s;
this excludes other scientific/setup/return utilities. Conservative retained
allocation, including every failure and the full utility bucket, was
93,088/172,800s. Complete private return of10,655 task files plus seven
export files, independent disk reread and exact owned cleanup/fresh absence
passed. The public package includes aggregate CSVs and vector figures; raw rows,
private traces and the protected exclusion index are retained locally.


## Limits and publication position

This development feasibility package alone cannot establish a new algorithm or
support an RL-superiority claim. Source-observation selection, binary collapse,
dependent targets, implementation conventions and conflicting SI aliases narrow
interpretation. A new method would need a mechanism distinct from classical
diversification and an owner-approved independently frozen evaluation. Any
additional confirmation data, paid source, commercial use, external validation,
product integration or journal submission requires its own scoped decision.
Raw data, reading PDFs, compound identities and private traces are not part of
the public aggregate package. The offline EN/TH report is an evidence handoff,
not a deployed laboratory system or a business ROI evaluation.
The protected-structure exclusion index also remains private. Consequently, the
public source/aggregate package alone is not a complete external row-level
reproduction bundle. A separately cleared reproducibility plan or independent
panel is needed before a submission can claim public end-to-end reproduction.
