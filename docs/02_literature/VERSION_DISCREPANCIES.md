# Version and interpretation discrepancy register

All entries describe inspected material as of 4 November 2026. “Unresolved” means that this package does not claim to have checked the required downstream data/code or associated publication. A discrepancy in wording is not automatically an error in the underlying experiment.

| ID | Inspected evidence | Resolution / required check | Status |
| --- | --- | --- | --- |
| V01 | R03 HAL cover names Célien Jacquemard; first package expanded a different given name | Correct active citations and preserve original pre-refresh archive | CORRECTED |
| V02 | R05 supplied filename resembles the journal title; PDF cover identifies ChemRxiv v3, 23 February 2024 | Cite inspected preprint DOI; retain journal DOI separately; compare version of record before attributing final-published details | VERSION_IDENTIFIED; JOURNAL_COMPARISON_NOT_RUN |
| V03 | R05 main PDF p. 4 and R03 PDF p. 15 describe VDR antagonism; R05_SI p. 2 calls VDR hits agonists | Verify AID/release and source-code label mapping before task import; do not invert labels from captions | UNRESOLVED_IMPORT_GATE |
| V04 | R05 Eq. 8 (PDF p. 12) explicitly minimizes its mutual-information score | Inspect exact source code/commit and formula direction before reproduction; do not silently replace with maximum BALD or call it a proven typo | UNRESOLVED_REPRODUCTION_GATE |
| V05 | R05 reports six comparison arms but five acquisition functions in Methods | Frozen-model exploitation shares the exploitation selector but changes retraining; describe selector and update schedule separately | INTERPRETATION_RECORDED |
| V06 | R03 EF1% uses constant 1% false-positive rate; other sources use ranked/acquired fractions | Give metrics distinct names, units and denominators | DEFINITIONS_SEPARATED |
| V07 | R05 batch sensitivity tests 16/32/64 only on ALDH1; shaded bands are SEM across ten runs | Do not infer equivalence, optimal batch size or task-population confidence from these plots | SCOPE_RECORDED |
| V08 | BayBE article identifies code version 0.12.2 and a paper analysis snapshot | Pin that snapshot for reproduction; pin and test a chosen release separately for integration | VERSION_RECORDED; INTEGRATION_NOT_RUN |
| V09 | LIT-PCBA provider table says PKM2 inhibitors; primary AID 1631 description says activators of human muscle isoform 2 pyruvate kinase | Inspect exact prepared release and activity mapping; do not invert labels | UNRESOLVED_IMPORT_GATE |
| V10 | Provider PPARG inhibitor shorthand versus AID 743094 PPAR-gamma signaling agonists | This is an erratum to earlier project inhibitor shorthand, not evidence of inverted data; exposed PPARG family remains development only | SOURCE_DISCREPANCY_RECORDED; IMPORT_GATE_OPEN |
| V11 | Provider TP53 inhibitor shorthand versus AID 651631 p53 signaling agonists | Preserve earlier frozen artifacts and qualify interpretation; exposed p53 remains development only | SOURCE_DISCREPANCY_RECORDED; IMPORT_GATE_OPEN |
| V12 | GBA AID 2101 includes both inhibitor/activator directions and N370S; IDH1 602179 is mutant; mTORC1 493208 uses MEF Tsc2-/-, p53-/- cells | Preserve mutation, species/cell context and pathway rather than direct-binding claims; audit dependence | CONTEXT_RECORDED; IMPORT_GATE_OPEN |
| V13 | AID 504327 title GCN5L2 has target KAT2A; ALDH 1030 specifies ALDH1A1, 995 ERK pathway and 492947 beta-arrestin bias | Alias/isoform/pathway distinctions do not create independent families | CONTEXT_RECORDED |
| V14 | AID 720551 title KCHN2 3.1 versus target KCNH2; AID 624291 integrin phenotype versus glycoprotein hormone alpha-chain target | Do not repair names or assign roles without exact endpoint adjudication; 624291 feature audit also stopped at cap | UNRESOLVED_IMPORT_GATE |
| V15 | Selected primary metadata includes rat IMPase/TrxR1, parasite phosphoglycerate kinase and mouse IL-2; TGF-beta title targets Smad3 | Keep nonhuman scopes separate and pathway semantics explicit | CONTEXT_RECORDED; NO_FINAL_ROLE |

Evidence supporting each row is paraphrased in [the full-text amendment](FULL_TEXT_REVIEW_ADDENDUM.md). A future resolution must add the date, exact file/commit, inspection result and consequences for the protocol. Do not delete an unresolved entry merely because an implementation has been written.

Rows V09-V15 were added from the 4 November
[primary metadata/feature audit](../03_research/CANDIDATE_ASSAY_AUDIT_V1.md), whose
request receipts pin live response bytes, AID versions/revisions and times.
They qualify earlier wording without rewriting frozen protocols or outcomes.
