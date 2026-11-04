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

Evidence supporting each row is paraphrased in [the full-text amendment](FULL_TEXT_REVIEW_ADDENDUM.md). A future resolution must add the date, exact file/commit, inspection result and consequences for the protocol. Do not delete an unresolved entry merely because an implementation has been written.
