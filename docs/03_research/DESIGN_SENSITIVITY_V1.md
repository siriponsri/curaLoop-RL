# Estimation design and resource sensitivity v1

4 November 2026. **Hypothetical design simulation, not final-study results.**
The owner selected 12+ biological families, additional CPU resources in
principle, and reporting effects with uncertainty **without a confirmatory
material-effect threshold**. No numeric final CPU cap was supplied. The
0.5/1/2-hit margins and 2/8/24-hour scenarios below are sensitivity inputs only,
not owner-selected criteria or execution approvals.

## What the development evidence can support

The exposed similarity-penalty paired differences were AhR [0,-2,0],
PPAR-gamma [0,0,0], p53 [0,0,0]. The equal-endpoint mean was -0.222 hits;
leave-one-endpoint-out means were 0, -0.333 and -0.333. The Gaussian pair had
all-zero hit differences. These are three correlated endpoints from one source
panel. Seeds do not turn them into independent targets; between-source variance
cannot be estimated. No population CI, equivalence conclusion or zero-variance
prior is assigned. Positive and unfavorable histories remain retained.

## Reproducible hypothetical model

The [config](../../research/configs/design_sensitivity_v1.json) and
[complete CSV](../evidence/design-preparation-20261104-v1/simulation/all-sensitivity.csv)
cover 216 design/variance/distribution cells, 10,000 replicates each, five
effects per cell and 1,080 reported rows. Fixed seed 20261104. Actual runtime
was 12.61 seconds wall / 7.80 seconds process CPU, one numerical thread.
No new candidate outcomes were inputs. Three variance profiles were assumed,
not fitted to the pilot:

| Profile | Family SD | Task-within-family SD | Paired-repeat SD |
| --- | ---: | ---: | ---: |
| Optimistic | 0.25 | 0.50 | 1.00 |
| Middle | 0.75 | 0.75 | 2.00 |
| Adverse | 1.50 | 1.00 | 3.00 |

All units are additional delivered hits in a paired contrast. Simulate
`D_fts = delta + F_f + T_ft + e_fts`, average repeats within task, then tasks
within family, with equal family weights. Family offsets are Gaussian or
variance-matched t4; other errors Gaussian. The residual mean is generated
analytically. For K families, q tasks/family and m paired repeats/task,
`Var(mean) = sigma_F^2/K + sigma_T^2/(K*q) + sigma_e^2/(K*q*m)`.
The paired error is a difference distribution, so no extra independent-arm
factor of two is added. More seeds cannot remove family variance.

Use family df K-1 for t intervals. Record two-sided 95% coverage/halfwidth,
one-sided alpha=.05 rejection of zero, Monte Carlo SE and lower-bound sensitivity
to each hypothetical margin. Gaussian 95% coverage across the grid was
0.9428-0.9548. This is a continuous, unbounded difference approximation, not a
calibrated hit-count/prevalence model or a guarantee of actual coverage/power.
Shared source libraries, chemical clusters and biological dependencies may
invalidate the hypothetical independent-family assumption.

## Precision under the owner's broader direction

The table reports **median halfwidth of a two-sided 95% interval**, one task per
family, Gaussian family offsets. It is neither an observed effect nor a
meaningful-effect criterion.

| Families | Paired repeats/task | Optimistic halfwidth | Middle halfwidth | Adverse halfwidth |
| ---: | ---: | ---: | ---: | ---: |
| 8 | 10 | 0.509 | 0.983 | 1.622 |
| 12 | 10 | 0.394 | 0.761 | 1.251 |
| 12 | 20 | 0.371 | 0.710 | 1.181 |
| 16 | 20 | 0.314 | 0.599 | 1.000 |

Under the middle assumptions, doubling repeats from 10 to 20 at 12 families
reduces median halfwidth by only about 0.051 hits. Adding four families at 20
repeats reduces it by about 0.111 hits. Prefer breadth once rights, assay meaning
and dependence have been resolved. These numbers do not justify relabeling
related endpoints as independent families to reach a target count.

For scale only, the hypothetical chance of a one-sided lower bound above zero
when the true effect is +1 hit is 0.663 (8 families/10 repeats), 0.884
(12/20), and 0.952 (16/20) in the middle Gaussian profile. It is only 0.518 for
12/20 under the adverse profile. Middle heavy-t4 family offsets at 12/20 give
approximately 0.883. These are appendix sensitivities, not a confirmatory power
claim. At a true effect equal to a +1-hit margin, the probability of establishing
**more than** that margin is about alpha, not the probability of detecting +1
against zero. No margin is selected from these calculations or pilot outcomes.

## Resource envelope, not an allocation

Runtime inputs are the 162 completed fresh-reproduction/Gaussian development
attempts: median 1.91537 seconds, p95 2.30524 seconds. They used 600-compound
pools on the local host. Forecasts multiply per-attempt wall time by run count
and an assumed 1.2 overhead. They are serial CPU-equivalent planning hours;
future remote CPU time, parallel elapsed time, larger pools and new methods
have not been measured. Separate 5/15-second stress cases are assumptions.

| Proposed scope | Runs: 4 methods x 2 conditions | Measured-median forecast | Measured-p95 forecast | Unmeasured 5s stress | Unmeasured 15s stress |
| --- | ---: | ---: | ---: | ---: | ---: |
| 12 families x 1 task x 20 paired repeats | 1,920 | 1.226 h | 1.475 h | 3.200 h | 9.600 h |
| 16 families x 1 task x 20 paired repeats | 2,560 | 1.634 h | 1.967 h | 4.267 h | 12.800 h |

Nine methods multiply these figures by 9/4: the 12-family 15s stress case is
21.6 hours; the 16-family case is 28.8 hours. Validation, preprocessing and
failed attempts require explicit accounting beyond a final-only run catalogue.
Do not treat a hypothetical 24-hour row as an approved cap or a paid allowance.
No electricity, laboratory savings, labor cost or commercial importance is
estimated. Complete [resource sensitivity](../evidence/design-preparation-20261104-v1/simulation/resource-sensitivity.csv)
retains every option, not only affordable/favorable rows.

## Concrete next design proposal

Use the [candidate audit](CANDIDATE_ASSAY_AUDIT_V1.md) to seek a human-annotated
12-family estimation set plus separate validation groups, with all source,
endpoint and whole-pool overlap gates closed first. The 23 selected panel
assays span 20 metadata planning groups, but 3 feature audits were excluded at
the payload cap. The 20 completed/reused feature audits span 17 groups, of which
14 are human-annotated and 13 remain after quarantining mixed-endpoint CYP2C9.
A 12+2 proposal therefore also needs an adjudicated group from the earlier
census (for example ERK pathway) or further source work. Grouping, source
dependence or eligibility attrition can reduce the count. No final-ready task
or frozen role exists. HIV/AhR/PPAR-gamma/p53 remain development/regression only.

Before opening outcomes, freeze the exact population, family weighting,
primary matched contrast, endpoint H(T), timing conditions, repeat distribution,
validation/final IDs, exclusions, analysis/interval procedure, multiplicity
handling, failure rules, compute cap and stop policy. If outcomes are needed to
establish task eligibility, design an authorized curator/aggregate gate first;
do not let final performance guide inclusion. Preserve uniform zero-hit starts.
Report estimates and intervals; describe any zero test as exploratory and never
interpret a nonsignificant result as equivalence or absence of useful effects.

## Remote host and authorization

The initial alias `dr-train` resolved to default user `user` and authentication
failed. Read-only config review did not confirm `chaw` for that alias, so no
username override or config change was made. The owner then supplied the
existing IP profile `100.77.149.83`, which local effective configuration and
known_hosts confirmed. One noninteractive strict-host-key test with the existing
identity and `IdentitiesOnly=yes` returned hostname `dr-train` successfully.
See the [receipt](../evidence/design-preparation-20261104-v1/dr-train-ip-profile-test.json).
Private key contents were not read/displayed, no keys created and no config
changed. Use this existing IP profile; do not assume the hostname is an alias.

No remote compute job was launched. CPU allocation, active-job/conflict checks
and the shared OS GPU lock remain NOT_RUN; inspect them at any future launch.
Authentication success is not a reservation or compute measurement. No GPU,
paid service, outreach, push, deployment or external publication occurred.

Source/config hashes, versions, array digests, Monte Carlo inputs and measured
development contrasts are in the [simulation receipt](../evidence/design-preparation-20261104-v1/simulation/simulation-receipt.json).
All review is by the same implementer. Application/browser suites were not rerun
for this separate preparatory work; exact targeted verification is retained in
the [verification receipt](../evidence/design-preparation-20261104-v1/verification.json).
