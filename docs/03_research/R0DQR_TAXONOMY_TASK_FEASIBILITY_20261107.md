# R0-DQ-R: taxonomy coverage and procedure-unit feasibility

**Scientific verdict: REVISE. No R1, model comparison or journal GO.**
This is one bounded outcome-free investigation of the existing ChEMBL37
archive. The [approved contract](../06_execution/R0DQR_EXECUTION_CONTRACT_20261107.md)
keeps numerical activities and value-presence flags closed. Completion and
resource/return evidence are recorded in the phase summary linked below.

## What this round established

| Observation | Result | Meaning |
| --- | ---: | --- |
| SINGLE PROTEIN target inventory | 11,055 | Full observed release catalog inventoried as metadata |
| Single-component targets without an unambiguous inherited family mapping | 10,008 / 11,052 | Three further targets have missing/multiple components; none of these unknowns establishes a new final family |
| Targets admitted for metadata feasibility | 10,763 | Protection, homologue and taxon gates applied; this is not benchmark eligibility |
| ChEMBL classification nodes | 905 | Functional classification metadata, not independently certified evolutionary families |
| Diagnostic sampling strata | 15 | Fixed second node from root; no granularity chosen by task yield |
| Frozen targets / assays | 200 / 1,254 | One bounded frame, without post-failure refill |
| Complete topology rows / molecule IDs | 16,862 / 12,873 | IDs, type, relation and unit only; all 1,254 assay graphs complete |
| Source molecule IDs matching protected identities / unresolved source IDs | 17 / 3 | Excluded or quarantined before nominal support construction; not a count of unique protected structures |
| Nominal candidate bundles | 1 | A 128-compound panel with 115 shared auxiliary compounds; numerical validity unqueried |
| Accepted source-verified multi-assay reference pools | 0 | Same-source/context resemblance did not establish procedure equivalence |
| Newly certified biological families / final tasks | 0 / 0 | The broad benchmark remains unqualified |

Evidence: [taxonomy and nominal tasks](../evidence/chembl-taskfirst-dqr-20261107-v1/taxonomy-and-task-feasibility-v1.json),
[selected target crosswalk](../evidence/chembl-taskfirst-dqr-20261107-v1/selected-target-crosswalk-v1.json),
[phase summary](../evidence/chembl-taskfirst-dqr-20261107-v1/phase-summary-v1.json).
All counts are frame-specific unless explicitly described as catalog inventory.

## Why the old family coverage collapsed

The inherited registry has 259 provisional broad labels. Its recorded bridge
graph contains six `family` edges and 79 `homologous_superfamily` edges.
Using all recorded types yields 139 connected components, with 87 broad labels
in the largest component. The same graph restricted to `family` edges has
254 components and a largest component of two labels. These are reproducible
connectivity diagnostics, not alternative certified family counts.

This explains how shared domain/superfamily ancestry can connect otherwise
different annotations transitively. It does not establish that removing those
edges produces independent biological families. The existing 87-label exposed
component, protected identities and historical roles remain intact. It was not
split to create new final groups. See the [granularity diagnostic](../evidence/chembl-taskfirst-dqr-20261107-v1/taxonomy-granularity-diagnostic-v1.json).

The proposed scientific rule for review is to distinguish three concepts:
curated target family, domain architecture/homology caution, and historical
exposure/source grouping. A domain reviewer must decide the family boundary
and evaluate cross-family leakage before any new split. ChEMBL functional
labels can organize that review; they cannot certify the claim by themselves.
Unknown mapping remains quarantined for final use.

The final append-only exposure audit also found **four shared-source components
with mixed frame-role labels**. Thirty-five selected assays share an already
exposed document; all 35 are development metadata. The incidental planning ID
CHEMBL8809 was previously resolved as a molecule, but its canonical aliases were
not present in the returned identity derivations; it has zero exact source-ID
matches in the current frame. That absence does not certify absence of aliases.
The frozen metadata worker retains old inputs/role labels but does not yet
propagate every old-document, planning-identity and shared-source join into a
certified split. **D2 therefore remains REVISE**, and all proposed final uses
are withheld. No frame refill, candidate replacement or new source query was
made to repair this after the result. The single nominal candidate remains
development-only. See the [exposure/quarantine audit](../evidence/chembl-taskfirst-dqr-20261107-v1/exposure-quarantine-audit-v1.json).

## Nominal support and the sampling limitation

The outcome-free assay catalog had 6,780 metadata-eligible targets with at least one
nominal endpoint assay. The fixed balanced draw selected roughly 13–14 targets
per functional stratum, including only 11 targets with the declared priority
condition of a nominal 128-ID Ki/Kd assay and at least two paper-linked assays.
After the fixed 20-assay/target DOI-balanced selection, seven selected assays
had a nominal reference count of at least 128 before canonical pruning.

Only one candidate survived the support/overlap rules: target **CHEMBL5966**,
accession **P55899**, reference assay **CHEMBL956457 / 552585 (Kd)** and auxiliary
**CHEMBL956456 / 552584 (IC50)**. The reference has 149 nominal canonical
identities; the fixed panel contains 128, with 115 shared with the auxiliary.
The target has no inherited family mapping and is development feasibility
only, with final mapping explicitly quarantined. This is not a numerically
qualified or independently adjudicated reference task.

The coverage-balanced selection undersamples the large enzyme/receptor strata
relative to their catalog size. Fixed DOI balancing may omit a reference assay
even when a selected target has one elsewhere in its catalog. Consequently,
this result does **not** establish that ChEMBL lacks sufficient tasks. It shows
that this particular bounded sampling/task construction did not meet the
36-bundle/18-unit, 4/2/12-role target. No new selection was run after observing it.
The earlier two R0-DQ candidates remain historical diagnostics, not additional
independent tasks in this new frozen frame.

Three groups shared the projected metadata signature, with only two, three and
four nominal reference identities respectively. None establishes construct or
procedure concordance. Strict complete-context and source-verified pool counts
are zero. Unrestricted pooling by target/type gives 12 reference units with at
least 128 nominal identities; that is an **ineligible upper bound**, without
proven procedure equivalence or auxiliary overlap, not 12 usable tasks/families.

## Source evidence and incremental value

The single candidate uses one frozen primary document, **CHEMBL1150419**,
DOI [10.1016/j.bmc.2008.05.004](https://doi.org/10.1016/j.bmc.2008.05.004).
Two abstract-free access metadata requests completed. Europe PMC returned no
confirmed PMC open-access route, and OpenAlex returned no open-access location.
No article body was retrieved, no source retry or replacement was attempted,
and no paper-only decision-relevant fact or independent reference was established.
These checks do not prove universal unavailability or a requirement to purchase.

Complete admitted assay metadata already names human FcRn, surface plasmon
resonance at pH 6 for the reference, and IgG-binding ELISA for the auxiliary.
Those are procedural metadata, not paper-only findings. Both variant fields
are null and both parameter lists empty. Null does not prove wild type or
complete construct/condition equivalence. Source methods and domain adjudication
remain necessary. The phase cannot test whether reading a paper changes a
molecular decision because no incremental source fact or decision gold exists.

See [source access evidence](../evidence/chembl-taskfirst-dqr-20261107-v1/source-access-readout-v1.json).
The source cap was a maximum, not permission to fill the remaining slots with
unfrozen substitute papers after candidate scarcity became apparent.

## D1–D5 decision

| Gate | Status | Assessment |
| --- | --- | --- |
| D1 taxonomy | REVIEW_REQUIRED | Traceable crosswalk and granularity diagnosis produced; biological rule needs domain adjudication |
| D2 protection | REVISE | Prior inputs/role provenance retained and protected exact matches excluded; four mixed-role shared-source components and one unresolved planning canonical join prevent final split clearance; all final use withheld |
| D3 nominal task scale | FAIL | One development-only nominal bundle; no qualified validation/final cohort or 36/18 scale |
| D4 evidence relevance | NOT_ESTABLISHED | One candidate pair/one unverified unit, zero accessible methods bodies and zero paper-only facts; target was at least four pairs/two units/two facts |
| D5 integrity | PASS | Numerical activity and presence interfaces absent; complete return/reread and scoped absence required for closure |

The study remains **not ready for a confirmatory model comparison or journal
submission**. The current contribution is an auditable data/task feasibility
and failure analysis, alongside the existing product POC. There is no evidence
yet that an evidence-aware planner improves molecular decisions, generalizes
across biological families, saves laboratory cost or delivers clinical value.
Product usability evidence does not fill those scientific gaps.

## Owner decision before further work

Read the [decision options](../06_execution/R0DQR_OWNER_DECISION_20261107.md).
No more intake, relaxed floors, new family split, numerical qualification,
training or R1 follows automatically from unused budget.

## Completion and preservation

All 1,689 remote regular task files (36,549,056,841 uncompressed bytes) were returned and streamed/hash-verified locally before exact owned task/export cleanup and fresh absence. Conservative retained reservations are 12,300 / 14,400 seconds, including 1,800 utilities; these are not measured runtime. The ledger is CLOSED, with no active owned jobs or automatic next phase. See the [phase summary](../evidence/chembl-taskfirst-dqr-20261107-v1/phase-summary-v1.json) and [return proof](../evidence/chembl-taskfirst-dqr-20261107-v1/complete-return-verified-v1.json).
