# LR-CF1 independent source-use and baseline review

**Preparation completed while the owner's source-name decision is pending.**
No campaign intake, source correction, molecular model fit or outcome analysis
is released by this note. It supplements the
[source-concordance decision](../06_execution/LR_CF1_SOURCE_CONCORDANCE_DECISION_20261109.md).

## Scoped source-use assessment

The reviewed universe is16 assay-description records associated with the8
provisional cached-target matches. Ten descriptions were retrieved from the
official description-only endpoint; six came from the authenticated A3 return.
These are not16 newly admitted campaigns. All records carry programme category1
(MLSCN) or2(MLPCN), with five named screening-centre providers. Their222 notice
strings were reviewed for rights/publication restrictions. Two strings state that
details of a scoring system will be published elsewhere; neither states a ban on
research reanalysis. No explicit rights restriction was identified in the reviewed
notices. Absence of a restriction alone is not the use rationale.

Positive source evidence is as follows:

- The NIH [MLSCN data-release provision](https://grants.nih.gov/grants/guide/rfa-files/RFA-RM-04-017.html)
  makes released data available for research redisplay/reanalysis while requiring
  source attribution and respect for producers' publication interests.
- The NIH [MLPCN provision G2](https://grants.nih.gov/grants/guide/rfa-files/RFA-RM-08-005.html)
  likewise supports research reanalysis of released data, with producer-publication
  expectations. The [later programme announcement](https://grants.nih.gov/grants/guide/pa-files/PAR-09-129.html)
  describes adaptation in biological research and source acknowledgment.
- [NCBI's molecular-data policy](https://www.ncbi.nlm.nih.gov/home/about/policies/)
  places no NCBI restriction on molecular data use, while retaining the distinction
  between access and third-party intellectual-property rights. It does not transfer
  all submitter rights to a user.
- The [published2024 study](https://doi.org/10.1021/acscentsci.3c01517) explicitly
  links the released processed datasets and reproduction code. The pinned
  repository retains an MIT notice for its software. Article/code licenses are
  not treated here as a blanket license for every underlying datum or compound.

**Review judgment:** these sources support bounded noncommercial methodological
reanalysis of the released processed resource and preparation of derived aggregate
reports with attribution. This is a scoped research-use assessment, not a transfer
of intellectual-property rights, commercial-data clearance, raw-data redistribution
authorization or approval to submit a journal article. It applies only to the
reviewed source records if their campaign/role/observation identities are admitted.
Use upstream links and source hashes in public reproduction instructions; keep
raw data, source text and detailed private returns outside public Git.

The older A3 INTERNAL_RESEARCH_USE/NOT_CLEARED dispositions and all its source
STOPs remain unchanged. They assessed another raw-intake qualification purpose.
This note records the positive evidence for the narrower released-resource
reanalysis now proposed; it does not retroactively certify A3 or extend to
unreviewed AIDs, industrial data or other archives. Final campaign admission still
requires the explicit source-concordance choice and all other LR-CF1 gates.

The direct NIH HTML downloads returned403; their official text was available
through web retrieval. The private receipts retain these failures. No missing
download was substituted by an unverified mirror or represented as a successful
HTTP fetch. The NCBI policy response is retained locally.

## MVS-A implementation concordance

The owner-supplied SI, SHA256
`adf8716fb2559aeb0ac1248d4f42c72b1466babced2e102b1cee69b9558e43b1`,
was inspected on pp3–4 and11–12. The equation on p4 was visually checked to avoid
losing its square-root sign during text extraction. It is a sum of clipped square
roots of squared gradient plus a weighted squared Hessian. The stated weight is
an L1 norm of tree leaf outputs. The implementation's default-string branch
provides regularization1.0 and feature fraction0.95; SI specifies100 boosting
iterations and1024-bit radius2 ECFP. Low MVS-A importance ranks toward positives;
high primary activity Score ranks toward positives.

The [pinned author code](https://github.com/dahvida/AIC_Finder/blob/04c58e85188e724ec5ff44cbed2e7b960f6f3df3/Scripts/MVS_A.py)
has implementation conventions that a reproduction must retain explicitly:

| Convention | Constructed observation | Consequence |
| :--- | :--- | :--- |
| Leaf-weight loop | Given maximum zero-based leaf index2, it visits indices0/1 and not2 | Do not silently replace the source's loop with a full-leaf norm |
| Prediction checkpoints | A three-tree fixture requests iteration counts0/1/2 | In pinned LightGBM3.1.1,0 requests all iterations; it does not mean an empty model |
| Custom parameter branch | An ordinary dict instance does not initialize `params`; the string `default` does | Do not assume a custom resource dict is accepted by that source branch |
| Score calculation | Synthetic-array gradient/Hessian, clipping and boundary calculations match the source equation operations | This is arithmetic conformance only, not a molecular reproduction |

The iteration meaning is verified in the official
[LightGBM v3.1.1 source](https://github.com/microsoft/LightGBM/blob/v3.1.1/python-package/lightgbm/basic.py),
retained locally with SHA256
`6e3179b1a9884cecf90e4db733eb82b57284ae90131f07110ade63bd6e370e35`.
The author source remains unchanged with SHA256
`d68898ba92b417739f066278b82e5293a162ed91e6f0fcc61f1a740860f2c52c`.

[The constructed probes](../evidence/lr-cf1-20261109-v1/source-behavior-review-v2.json)
execute the author class methods with synthetic arrays and a deterministic fake
model. They do not import/train a real LightGBM model, test compiled-runtime
compatibility or measure an effect on ranking quality. The first helper stopped
because its exact-text assertion did not strip documentation backticks; that
failure/source snapshot and full180-second envelope are retained. A separate
180-second technical repair reused the exact downloaded dependency source and
completed the probes. There was no molecular retry or alternate ranking choice.

If option A is approved, the mandatory baseline should be identified as a
reproduction of the pinned author implementation, including these conventions,
with an explicit compatibility/resource concordance. A source-code reproduction
cannot be presented as proof that every mathematical convention, raw assay or
published figure has been independently reconstructed. The proposed option A
already uses that qualified claim boundary. No corrected MVS-A variant is
implemented, added to the matrix or authorized here.

## Remaining boundary

This work removes avoidable uncertainty about source-use evidence and implementation
behavior while preserving the required owner decision. It does not resolve the
13/17 campaign-name conflict, processed-file identity, confirmation support,
compound exclusions, experiment blocks, actual environment compatibility or
resource feasibility. All scientific baseline fits and portfolio cells remain
NOT_RUN. The original budget/deadline and protected final16 boundary remain intact.
