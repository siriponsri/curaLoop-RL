# R0 ChEMBL readiness results and phase decision

Date: 7 November 2026. Execution base:
0de9df4a6b772dcbb90ed291cb4c5d4d9fa1e4bf.
**R0 bounded readout complete. Scientific advance: REVISE; no next phase released.**
This is not a passed molecular benchmark or an established new method.

## Owner decisions and scope

The owner authorized completing the bounded R0 phase work. After the historical
release directory was inspected, the owner explicitly selected ChEMBL 37 for the
candidate instead of 35. Caps and final-outcome protections were unchanged.
Current-release snapshots are labeled 37; 35 files remain source-access evidence.
No full database, activity endpoint, benchmark question/gold file, full article/SI,
training, SSH processing, GPU, paid service or external team write was used.

Execution followed [the contract](../06_execution/R0_CHEMBL_EXECUTION_CONTRACT_20261107.md)
and [the outcome-blind sampling freeze](../06_execution/R0_METADATA_SAMPLING_FREEZE_20261107.md).
Final aggregate evidence is [the v4 summary](../evidence/r0-chembl-20261107-v1/metadata-summary-v4.json).

## What actually passed

| Check | Observed result | Scope |
| --- | --- | --- |
| Version/access | Official 37 README/schema/license retrieved; API status before and after remained ChEMBL_37 with identical status payloads | Local response bytes pinned; not an atomic full-release archive snapshot |
| Metadata retrieval | 50 assays: 25 binding, 25 functional | Deterministic convenience sample, not representative of ChEMBL |
| Document linkage | 12 document records, 12 DOIs; every sampled assay's referenced document returned | Metadata only; full-text access/reference truth not tested |
| Target linkage | 22 single-protein targets and 22 target components | High assignment confidence was a sampling restriction, not a truth certificate |
| Classification closure | 18 initially referenced nodes; 38 including ancestors; every observed parent resolved | 82 target/component/classification records total, within 100; not 38 biological families |
| Identity freeze | 50 IDs frozen before descriptions; no failed/quarantined replacement | Sample remains metadata-exposed for future design |
| Structural checks | Fixed-ID joins, projected fields, version/status, hashes and budgets checked | No observed outcome support or molecular-overlap certification |

The 50 assays span 12 paper/target-connected components with sizes
20, 8, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1. These are dependence units under that graph,
not 12 verified biological families. The classification ancestry contains five
level-1 categories: enzyme, ion channel, membrane receptor, other membrane protein
and transcription factor. Those broad categories are also not certified families.
The owner's 12+ independent-family ambition remains unqualified.

## Metadata findings and their limits

All 50 descriptions, organism fields and target relationships were present.
Cell type was null in 26/50, tissue in 43/50 and subcellular fraction in 47/50.
A null may mean not applicable or unreported; these counts are not a defect rate
and do not establish that a source clarification would change a molecular decision.

The simple predeclared pattern audit found no IC50/EC50/Ki/KD markers in these
descriptions. This is not absence of such measurements. Readout types/units and
observed support require fields outside the admitted assay metadata; activity
records were not accessed. Therefore the main endpoint cannot be frozen from
this result. Parser-positive synthetic checks passed, but the patterns do not
cover every spelling or semantic expression.

Four descriptions were quarantined by conservative quantitative-outcome/condition
patterns. They could contain protocol concentrations rather than results; no
manual reference label was assigned. Raw passages were not emitted to the agent.
Unflagged text is not certified outcome-free. Public evidence exports IDs,
structural metadata, dispositions and aggregates; full raw response bodies remain
private. Public exposure/pretraining contamination cannot be certified absent.

The document years are 1989-2009. This follows the early-ID convenience frame;
the sample cannot support claims about current-literature coverage, temporal
generalization or ChEMBL-wide uncertainty rates. No authors' original activity
results were inspected to select a promising task.

## Method and publication assessment

[The formalization](R0_METHOD_FORMALIZATION_20261107.md) specifies shared context,
supported measurement actions, evidence observations and separate resource
constraints. It also identifies overlap with decision-region learning and
multifidelity search. A source graph, a typed report and value of information
do not establish a new algorithm. A technical approximation with incremental
decision value remains to be demonstrated.

There is a strong falsifier: if all relevant evidence can be obtained upfront
at no constrained cost, an optimal upfront-informed policy can simulate any
adaptive policy and ignore unused information. Universal adaptive superiority
cannot follow from that setting. A real evidence-resolution cost or access
constraint must be established, not created by artificially hiding free metadata.

Acting as a skeptical reviewer: source integrity and inspectable engineering
have improved; scientific novelty, reference truth, observable panel support,
family independence and planning benefit remain unsupported. This is sufficient
to justify a bounded reference-feasibility revision, not a JCAMD-ready method
paper or an efficacy claim for an autonomous R&D agent. A product-only or
benchmark-only pivot would require an explicit owner decision.

## Gate readout

| R0 gate | Decision | Reason |
| --- | --- | --- |
| Fixed source and basic schema/access | PASS for sampled 37 metadata | README/license/schema, projected joins and version checks available |
| Terms/provenance for this metadata slice | PASS, scoped | Database CC BY-SA 3.0 notice/license recorded; no raw articles or commercial property calculations used |
| Natural, adjudicable decision-changing uncertainty | NOT_RUN / not established | Nulls and regex flags are not a reference standard |
| Endpoint and measured-panel support | NOT_RUN | Zero activity intake; no complete observed panel can be asserted |
| Protected identity / final cohort admission | NOT_RUN | Existing exclusions retained; no new scientific cohort admitted or final outcomes opened |
| 12+ independent families | NOT_ESTABLISHED | Dependency/classification audit is not evolutionary validation |
| Method distinction and same-predictor value | REVISE / NOT_RUN | Generic formulation overlaps prior work; no policy experiment authorized |
| Next phase | NOT_RELEASED | Owner decision required |

This phase's authorized work concludes with **REVISE_BEFORE_NEXT_PHASE**. The
readout is complete; scientific success criteria did not all pass. No score,
simulated result or administrative status substitutes for the missing evidence.

## One recommended continuation: R0-R reference feasibility

Before enlarging the benchmark or training a model, establish whether real
source verification changes a decision on a small fixed development subset.
Use the existing metadata-exposed sample; do not present it as untouched final.

Proposed new contract, not released: choose up to 12 assays from the fixed 50,
across distinct source documents where feasible, using a predeclared balanced
B/F hash rule. Admit at most 20 outcome-free readout-type/unit/molecule-ID
projections per selected assay (240 total), at most 240 outcome-free molecular
identity records for protection checks, and up to 12 legally accessible,
result-masked methods extracts. These are bounded support samples, not complete
assay coverage; no result-driven replacement. Numerical
activity values, gold labels and old final outcomes remain excluded. First apply
the existing label-free protected identity/lineage checks; uncertain matches are
excluded, not imputed. Accessing activity-record projections and paper methods
is a material extension beyond the closed zero-activity metadata contract.

For each fixed case, record the pre-evidence ambiguity, admissible source,
resolved/unresolved reference and whether a supported decision could change.
Have references reviewed separately from case construction; an appropriate
reviewer must be designated rather than treating the author's own labels as
independent truth. Count all cases, unresolved results and ties. Record actual
technical or reviewer burden separately; no invented lab costs or success quota.

Suggested ceiling: one local CPU, 1 GiB, 1 CPU-hour including utilities, 8 elapsed
hours; 48 source attempts, 32 MiB decoded, no paid model/GPU/training/team write.
These are proposed fresh resources; the current ledger remains closed at its
retained charge. Stop if access, reference adjudication or support cannot be
established. A negative finding can end the adaptive-evidence thesis. A positive
finding would justify designing a new, broader family-separated cohort and a
controlled development experiment with upfront resolution as a required baseline.

Next actor: owner reviews this REVISE decision and chooses whether to release
R0-R, request a different contribution or stop this direction. P1/R1 is not
automatically authorized.

## Accounting and artifacts

24 source attempts: 23 metadata responses and one retained client-side STOP.
531,683 decoded body bytes. Conservative charge: 1740/1800 seconds (29/30 minutes),
comprising 24 retained 60-second worker reservations plus 300 utility seconds.
This is not measured CPU use or a reset of historical LR-BC accounting.
27 receipts sum to 2.078125 measured process-CPU seconds over their measured
segments; imports, setup and unmeasured utilities are not included in that sum.
The conservative charge is the budget figure.

The stopped ChEMBL-35 LICENSE request returned HTTP 200 without Content-Type.
The first client rejected it before reading its body. This was a client
format-assumption failure, not provider denial. The attempt/charge/STOP remain;
that URL was not retried. Independently listed text metadata accepts an absent
type only with a fixed filename, bounds and UTF-8/nonbinary validation; the
separate owner-approved 37 source was then used. Exact source revisions were
retained, including three reconstructed source snapshots accepted only after
matching the hashes in their actual execution receipts. No result was rebuilt.

The final local reread covered 76 private files / 737,121 bytes before any later
delivery receipts. Raw metadata and executed code snapshots remain in
`.local/r0-chembl-20261107-v1/`. See [the artifact index](../evidence/r0-chembl-20261107-v1/private-artifact-index-v1.json).
No remote work occurred, so remote return/cleanup is NOT_APPLICABLE.
Independent scientific review is NOT_RUN; the reviewer assessment above is a
clearly labeled self-assessment, not another person's endorsement.
