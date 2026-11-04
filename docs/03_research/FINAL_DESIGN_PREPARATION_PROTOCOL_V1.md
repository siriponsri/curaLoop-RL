# Outcome-sealed candidate and design preparation v1

Prepared 4 November 2026 after the exposed development studies. This is not a
final protocol freeze or authorization to execute a final study. Subsequent
owner direction selects 12+ families and effect estimation with uncertainty,
without a confirmatory material-effect threshold. Population/roles, primary
contrast, interval procedure and numeric final resource allocation still need
freezing. No threshold will be chosen from the null development outcomes.

## Source census and exposure boundary

Audit the nine remaining entries of the official NCATS Tox21 training index and
all 15 source AIDs listed by the LIT-PCBA provider, in a fixed source-derived
census. Do not select by published hit rate, model performance or expected gain.
HIV and the already seen AhR/PPAR-gamma/p53 resources stay regression/development
only. Related PPARG and TP53 endpoints cannot silently become independent final
target families; VDR phenotype remains unresolved. No final role is assigned by
this preparation.

Use only official PubChem PUG REST assay **description**, unfiltered `cids_type=all`
membership, and compound **IsomericSMILES** property operations. The URL guard
rejects full records, concise/dose-response/summary results, active/inactive
membership filters, unknown parameters/origins and credentials. The response
guard rejects unexpected assay data sections or outcome fields. Do not request
or evaluate compound outcome values. Label definitions are metadata: PubChem
inactive(1)/active(2) is distinct from NCATS training CSV inactive(0)/active(1).
Other categories must remain quarantined until an explicit ingestion rule exists.

The LIT-PCBA landing page includes published class totals visible during the
prior literature review and current source discovery. Record that exposure;
do not characterize these source summaries as unseen, copy them into power
inputs, or use them for candidate selection. No reserved final compound outcome
file exists or is unsealed in this package. Metadata/structure exposure itself
must be retained in any future split/selection history.

## Rights, identity and structural audit

Pin each exact received response by URL, time, bytes, SHA256 and metadata AID
version/revision/depositor record. An accessible URL or a generic PubChem listing
is not a file-level license. NCATS provider public-domain evidence supports its
stated data scope; prepared LIT-PCBA rights, individual depositor terms and
structure-source reuse require explicit closure before a final data ingest.
ChEMBL has provider CC BY-SA 3.0 terms, but the attempted release LICENSE
download timed out here; no version/file-level grant is inferred from that.
Keep raw metadata/features outside Git. Never disable TLS verification or bypass
an access denial. Record failures and stop the origin after 401/403.

Select at most 200 CIDs per assay by fixed SHA256 rank of version/seed/AID/CID,
without outcomes. Canonicalize public isomeric SMILES in RDKit, retaining salts,
tautomers and stereochemistry. Compare exact canonical structures and radius-2 /
1,024-bit nonchiral Morgan nearest Tanimoto >=0.8 with (a) all previously fetched
NCATS raw structures, (b) the three 600-compound subsets, and (c) bundled HIV.
Do not inspect activity columns for overlap. This is a feature-audit sample,
not the final 600-compound pool or proof that all rows have usable binary labels.
Provisional target/functional groupings are explicitly manual planning aids,
not an independent biological-family certification.

The bounded audit allows 120 requests, 480 seconds between-query wall checks,
8 MB per response and 96 MB received before the next query (soft by one
response), one sequential process and 0.55s minimum inter-request delay. All
errors/caps remain visible. No paid service, GPU or outreach is permitted.

## Hypothetical precision/power/resource sensitivity

`research/configs/design_sensitivity_v1.json` contains **multiple hypothetical**
effects (0, .25, .5, 1, 2 additional hits), material margins (.5, 1, 2), resource
budgets (2/8/24 serial CPU hours), family counts 3/4/6/8/12/16, one/two tasks per
family and 3/10/20 paired repeats. No primary threshold is selected. Three
variance profiles are assumptions, not estimates fitted to the small pilot.

Simulate paired differences `D_fts = delta + F_f + T_ft + e_fts`, equal family
weights, with separate family/task/paired-seed SD. Family offsets are Gaussian
or variance-matched heavy-tail t4; task/residual terms Gaussian. The Gaussian
mean of q*m residuals is generated analytically, preserving the hierarchy.
The design variance is `sigma_F^2/K + sigma_T^2/(K*q) + sigma_e^2/(K*q*m)`;
more seeds cannot eliminate family variance. Use family df K-1 for the t-based
interval. Report simulated one-sided rejection of zero, two-sided 95% coverage/
halfwidth, Monte Carlo SE, and probabilities that the lower bound exceeds each
hypothetical material margin. Boundary power at true effect=margin is not power
to establish a gain beyond that margin.

Use 10,000 replicates per design/profile/distribution, deterministic RNG, and
retain every scenario. This is a continuous-difference approximation, not a
calibrated count/prevalence model or assurance of real-world power. The three
correlated pilot endpoints and single source panel cannot identify a population
variance, especially when all GP paired differences are zero. Keep raw pilot
contrasts/leave-one-endpoint-out sensitivity separate from the hypothetical grid.
No equivalence claim follows from non-significance or a zero sample SD.

Project serial runtime from recorded 600-compound campaigns and explicitly
unmeasured 5s/15s stress assumptions, with a declared 1.2 overhead factor. Compare
4/9 methods x two timing conditions; these are options, not a frozen final
catalogue. Do not infer electricity, labor, commercial importance or paid cost.
Simulation run-wall cap is 120 seconds, one numerical thread. Final outcome
execution, controller transfer, publication, push and deployment remain outside
this preparatory package. All review is by the same implementer unless an
external reviewer is actually recorded.

## Subsequent bounded expansion and owner direction

The fixed 16-gene expansion and separately pinned 128-AID HTS census are retained
as new discovery histories. The gene search found one feature candidate and
retained 23 HTTP 404 membership attempts. The HTS selection was committed at
`612309a` before new features: 23 selections, 17 new/3 reused feature audits,
3 exclusions after the pre-query 96 MB payload cap (soft by one response).
There was no outcome-based selection, cap increase or retry of that panel.
Source/code/config pins, exact request histories and semantic/rights gates are
in the [candidate report](CANDIDATE_ASSAY_AUDIT_V1.md).

The owner authorized additional CPU in principle and existing dr-train SSH
access, not a paid allocation or final outcome execution. After an alias/user
mismatch, the owner supplied the existing IP profile `100.77.149.83`. Read-only
effective config/known-host review confirmed User chaw and its existing identity;
one strict noninteractive test returned dr-train. No configuration/key changes,
private-key contents or remote compute jobs were involved. Resource availability
and conflicts remain to be checked at launch. See [design options](DESIGN_SENSITIVITY_V1.md).
