# R0-R reference review packet

Historical S1-only checkpoint. The current packet is
[version 2](R0R_REFERENCE_REVIEW_V2_20261107.md), incorporating all three
owner-supplied articles. The earlier source counts below are point-in-time facts.

Date: 7 November 2026. Status: **PENDING_OWNER_REVIEW; NOT INDEPENDENT GOLD**.
No numerical activity values or protected final outcomes are included.

## Source note S1

Source: [DOI 10.1021/jm900186m](https://doi.org/10.1021/jm900186m),
[public article](https://pmc.ncbi.nlm.nih.gov/articles/PMC2708097/),
Experimental Section. A trusted parser isolated methods, excluded tables and
result sections, masked numerals and withheld the unmasked article from agent
context. This is a conservative extraction, not an assurance of perfect semantic
separation. Numeric masking can remove necessary protocol distinctions.

Draft interpretation: the methods describe ligand-competition measurements for
individual PKC isozymes, with Ki derived from displacement measurements. They
mention alternative lipid preparations. The retained passage does not uniquely
assign one preparation to each sampled ChEMBL assay. This supports a draft
biochemical-binding context, while the assay-specific preparation stays
UNRESOLVED. This interpretation is awaiting review; it establishes no activity,
transfer performance or benefit of adaptive evidence gathering.

## Two source-supported candidates

| Case | Source metadata | Draft context status | Owner review |
| --- | --- | --- | --- |
| CHEMBL1000240 | CHEMBL3582; binding; Ki/nM; four projected record IDs | Assay-specific lipid preparation UNRESOLVED; see S1 | PENDING |
| CHEMBL1000241 | CHEMBL299; binding; Ki/nM; four projected record IDs | Assay-specific lipid preparation UNRESOLVED; see S1 | PENDING |

The two cases share four molecule IDs. These are linked record identities, not
proof of nonmissing numeric outcomes. Their targets differ. Under this round's
same-target eligibility rule, unqualified pooling of this pair is already
ineligible from typed metadata. This is an exploratory adequacy control examined
after source retrieval, not a prespecified policy result. Added context must not
be mislabeled as a demonstrated decision improvement.

Please review: (1) whether S1 accurately reflects the source method, (2) whether
there is a source location that maps either case to a particular preparation,
and (3) whether UNRESOLVED should remain. AGREED / REVISE / UNRESOLVED are all
valid outcomes. Record source locations and reasoning for revisions; do not
infer numeric activity or assign a missing condition from a typical protocol.
An owner review does not by itself establish independent domain-expert gold.

## Full frozen case register

The [case candidates](../evidence/r0r-chembl-20261107-v1/reference-candidates-v1.json)
retain all twelve cases, including both rejected projections. Two cases have
methods for draft review; the other ten have no admitted methods reference yet.
No failed case was replaced. Source availability must not select the scientific
population after outcomes. This is a development/reference feasibility slice,
not an untouched final set or a twelve-family benchmark.

Remaining sources are listed in
[the owner download request](R0R_OWNER_METHODS_REQUEST_20261107.md).
No next phase is released by this packet. Further source intake and review must
stay inside the unchanged R0-R resource window or receive a new owner release.
