# Owner decision after R0-DQ

**PROPOSAL ONLY. No new phase, clock, root or processing is released.**
Read the [actual R0-DQ results](../03_research/R0DQ_QUALIFICATION_RESULTS_20261107.md).
Two candidates have real 128-compound panels, but both are development cases in
one broad, exposed split unit. There are no validation/final groups, source
methods or independent references. This is not an R1 or journal GO.

## A. Recommended: R0-DQ-R, metadata and task-unit feasibility

Proposed fresh ceiling: **4 additional CPU-hours / 48 elapsed hours / at most
two combined workers**, one dr-train worker at one CPU-equivalent/4GiB and one
local worker at one CPU/1GiB maximum. The clock begins only after explicit owner
release. Existing reservations and closed phases remain unchanged. This is a
ceiling for review, not an estimate of actual time or a promised successful
cohort. A source/return budget of2CPU-hours, metadata1hour, source-method
feasibility0.5hour and utilities0.5hour is proposed.

The owner would explicitly approve two design investigations:

1. **Broader, reviewable family coverage.** Inventory target/classification
   metadata from the already pinned ChEMBL37 DB. The observed release catalog
   has11,055 SINGLE PROTEIN entries; inventory metadata only. Prepare a taxonomy
   crosswalk and identify where inherited coverage or transitive merging prevents
   defensible biological units. ChEMBL class labels are not automatically
   evolutionary families. Do not split or rename groups merely to reach12final
   units. Domain review must precede any claim of certified families.
2. **Source-verified procedure groups as a proposed reference unit.** Assess
   whether multiple assays can be shown to measure the same reference procedure,
   instead of requiring128compounds inside one database assay instance. This is
   a material task-unit proposal. It is not authorized by the old R0-DQ grant.

Pooling would require explicit agreement on target accession/organism,
variant/construct, endpoint type, measurement procedure and relevant conditions
including tracer/cell/readout. A common target, paper, ASSAY_GROUP or endpoint
alone is insufficient. Null variant fields are not wild type. Unknown procedure
equivalence prevents pooling; contradictory evidence is retained. No value
correlation, favorable potency or downstream performance may justify pooling.
Ki and Kd remain separate, with IC50 auxiliary only. Keep128/64/32floors.

### Bounded proposed work

- Reuse the locally returned, verified archive/DB bytes. Zero new bulk HTTP
  downloads; no mirror, release switch or stopped-source retry. A new remote
  root would require fresh admission under the same checked SSH identity and
  aggregate one-core quota. Never recreate the closed R0-DQ root.
- Catalog inventory may cover the11,055target metadata entries. The new task
  feasibility frame would be capped at200targets,4,000assays,120candidate
  bundles,2million outcome-free support rows and100,000canonical molecule IDs.
  Incomplete graphs remain unknown. These are new proposed bounds, not current
  execution permission.
- No numerical activity values, nonmissingness flags, ranks, pChEMBL, model
  training or final outcomes. Support counts use IDs/type/relation/unit only;
  numerical qualification would require a later owner decision.
- Preserve all historical protected identities, exposed canonical structures,
  actual target/source lineage and old task roles. A new taxonomy label must
  not clear a protected or exposed lineage. Unknown mapping blocks final use.
- Inspect at most12primary source documents for development feasibility, with
  at most24abstract-free access metadata and12masked-methods attempts,
  128MiBnonbulk cap,2MiBmetadata/8MiBmethods-file caps, one request at a time
  and no retries. Reuse successful cached access metadata for the current four
  documents. No purchase, paid API or bypass of access controls.
- The same complete private return, streamed local reread and exact scoped
  cleanup are required. Proposed remote64GiB/local28GiBtask caps and16GiBreturn
  ceiling remain; recheck actual disk/RAM admission before work.

### Proposed decision gates

| Gate | What would support another qualification proposal |
| --- | --- |
| D1 taxonomy | Traceable crosswalk, explicit unknowns and a defensible granularity proposal; no claimed independent certification by the parent |
| D2 protection | All historical identities/roles and exposure joins retained; unresolved proposed final lineage quarantined |
| D3 nominal task scale | Candidate36bundles in18conservative units with4/2/12role targets and128/64/32ID support after canonical pruning; still no numerical qualification |
| D4 evidence relevance | At least4development candidate pairs with accessible source methods spanning at least2units; at least2traceable candidate decision-relevant facts beyond complete metadata, for domain review |
| D5 integrity | No numerical values or final outcomes opened; complete failure ledger, return/reread and scoped absence |

If counts or source relevance remain insufficient, end with REVISE/STOP and
owner options after this one bounded round. No automatic resampling, lowered
floors, endpoint expansion, R1 or model campaign. If the taxonomy/procedure
equivalence cannot be established within the proposed scope, consult the owner
before changing the research population or claims. Unused budget is not an
automatic next-phase grant.

The intended output is an owner-reviewable taxonomy/task-unit feasibility packet
and, if supported, a concrete new numerical-qualification proposal. It is not a
publication-ready benchmark. Independent domain/source adjudication remains
required before research claims.

## B. Adjudicate the current two diagnostics first

Proposed fresh ceiling: **1 CPU-hour / 8 elapsed hours / one local worker up to
one CPU/1GiB**. No SSH or new data records. If the owner already has lawful
access, provide the four existing papers for methods-only projection and
assay/reference mapping. No purchase is requested.

Optional owner-file directory, created only on release:
`research/raw_data/external-benchmarks/chembl-37-taskfirst/owner-methods/`.
Use the ChEMBL document IDs as filenames; the DOI table is in the result report.
The work could clarify constructs/procedures in these two cases. It would not
repair the absent validation/final groups or satisfy the broad benchmark target.
Independent reference review and any further work still need owner decisions.

## C. Pause with the current evidence

Retain the full private return and public readout; no new compute/intake. The
existing product and research claims remain bounded by their actual evidence.

**Recommendation: A**, because the current failure is chiefly population/coverage
and task construction. The four-paper review is useful for two diagnostics but
cannot alone establish the intended study scale. The owner chooses the next
package; approval of this report does not release either proposed budget.
