# R0-R source-linked reference review, version 2

Date: 7 November 2026. **PENDING_OWNER_REVIEW; NOT INDEPENDENT GOLD**.
This packet supersedes the earlier S1-only packet. The owner limited new intake
to three supplied main articles and two related supplements. Three purchase-only
documents remain unavailable; no substitution or further download is requested.
All twelve original cases remain in the denominator. No numerical activity
values or protected final outcomes are included.

## Source notes and exact review locations

| Note | Document and source | Location | Parent draft | Still unresolved |
| --- | --- | --- | --- | --- |
| S1 | CHEMBL1138492; [10.1021/jm900186m](https://doi.org/10.1021/jm900186m); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2708097/) | Experimental Section; prior masked XML | PKC ligand-competition methods, with Ki derived from displacement and alternative lipid preparations | Preparation for each frozen assay |
| S2 | CHEMBL1140224; [10.1021/jm801063n](https://doi.org/10.1021/jm801063n) | Physical PDF page 10, Experimental Section | Perforin-related lysis/cytotoxicity procedures in several systems | Which procedure belongs to CHEMBL1000319; do not infer affinity from B metadata |
| S3 | CHEMBL1140235; [10.1021/jm800965b](https://doi.org/10.1021/jm800965b) | Physical PDF pages 7-8, Biological Methods / Cell Culture / Antiproliferative Assay | Radioligand binding and a distinct MTT cell-growth procedure coexist | Exact case-to-procedure mapping; numeral masking obscures receptor suffixes/cell identifiers |
| S4 | CHEMBL1156448; [10.1074/jbc.M609796200](https://doi.org/10.1074/jbc.M609796200) | Physical PDF page 3, Experimental Procedures | Receptor constructs, transfection, phosphatidylinositol turnover, SRE reporter and competition binding | Exact construct/pathway/procedure for each case; shared target does not establish compatibility |

Locations use physical PDF pages, not printed journal pagination. These concise
paraphrases are based on masked procedures. They do not incorporate table/figure
results, complete original papers, activity values or later author inferences.
No exact method mapping has been independently adjudicated. Supplements were
title-matched but quarantined by the methods extractor, and support none of the
draft judgments below. See [processing details](R0R_OWNER_SUBSET_RESULTS_20261107.md).

## All twelve frozen cases

| Case | Target | Admitted metadata records | Typed readout/unit | Document note | Reference disposition |
| --- | --- | ---: | --- | --- | --- |
| CHEMBL1000140 | CHEMBL4153 | 0 | Projection rejected | S3 | Document context only; projection STOP retained; mapping UNRESOLVED |
| CHEMBL1001324 | CHEMBL4616 | 0 | Projection rejected | S4 | Document context only; projection STOP retained; mapping UNRESOLVED |
| CHEMBL1000240 | CHEMBL3582 | 4 | Ki/nM | S1 | Assay-specific preparation UNRESOLVED |
| CHEMBL1000649 | CHEMBL233 | 20 | IC50/nM or null unit | Unavailable CHEMBL1136971 | SOURCE_UNAVAILABLE; 17 null units unresolved |
| CHEMBL1000319 | CHEMBL5480 | 6 | Inhibition/% | S2 | Exact lysis procedure/system UNRESOLVED |
| CHEMBL1001155 | CHEMBL3979 | 20 | EC50/nM | Unavailable CHEMBL1141686 | SOURCE_UNAVAILABLE |
| CHEMBL1000360 | CHEMBL5491 | 20 | IC50/nM | Unavailable CHEMBL1156685 | SOURCE_UNAVAILABLE |
| CHEMBL1001334 | CHEMBL4616 | 1 | IC50/nM | S4 | Construct/pathway/procedure UNRESOLVED |
| CHEMBL1000136 | CHEMBL273 | 9 | Ki/nM | S3 | Exact binding-procedure mapping UNRESOLVED |
| CHEMBL1001339 | CHEMBL4616 | 1 | IC50/nM | S4 | Construct/pathway/procedure UNRESOLVED |
| CHEMBL1000241 | CHEMBL299 | 4 | Ki/nM | S1 | Assay-specific preparation UNRESOLVED |
| CHEMBL1001341 | CHEMBL4616 | 1 | IC50/nM | S4 | Construct/pathway/procedure UNRESOLVED |

Records indicate admitted identifiers/readout metadata, not nonmissing numerical
outcomes. The two rejected projections were not retried or replaced. Methods at
document level cover 9/12 cases, 7/10 admitted cases and 26/86 admitted records.
All source-supported rows are PENDING_OWNER_REVIEW. Unavailable rows are not
negative labels. No row currently authorizes pooling or reports a molecular
decision gain. All 17 null-unit records belong to the unavailable S1-independent
document CHEMBL1136971; a unit must not be borrowed from a different paper.

The S1 pair shares four molecule IDs but has different targets. The same-target
eligibility rule already excludes unqualified pooling using typed metadata.
That is an exploratory adequacy control, not proof of source-acquisition value.
For S4, matching target/readout/unit fields are necessary but insufficient:
the construct/pathway mapping remains unresolved. No new comparator result is
created by pointing out that scientific distinction.

## Owner review form

For each source-supported case, record **AGREED**, **REVISE** or **UNRESOLVED**,
the source note and exact methods location, the procedure that maps to the assay
if known, and the reason. UNKNOWN is an acceptable answer. Do not supply a typical
protocol condition as if observed, infer a missing unit from another assay, or
look up numerical activities/final outcomes for this review.

The specific decisions are:

1. Are the document-level source notes faithful to the cited methods?
2. Can a source location link the frozen assay to an exact preparation,
   construct, pathway or biological system within the approved masked scope?
3. Does that resolve compatibility beyond complete typed metadata, or merely
   add context while leaving the operational decision unchanged/unknown?

If the mapping needs unmasked construct identifiers, tables/results, additional
activity records or different documents, flag that requirement for a concrete
scope proposal. This packet does not release those accesses. Owner review is
not automatically independent scientific adjudication; reviewer expertise and
independence must be documented before any gold-reference claim.

R0-R remains **REVISE_PENDING_REFERENCE_REVIEW**. The owner's three-paper subset
is processed, but no P1/R1, model training, journal submission or final evaluation
is released. Source availability is not a scientific success criterion.
