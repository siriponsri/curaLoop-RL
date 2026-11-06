# Goal 4R2-A3 population and observation qualification

6 November 2026. **QUALIFICATION COMPLETE; SCIENTIFIC ADVANCEMENT NO_GO.**

A3 established source, protection and transport controls, then found that the
first live observation response used an unsupported native envelope. An additive
offline adapter validated the retained response without another request. It did
not release the stopped intake or establish a paired scientific cohort.

Follow the [execution contract](../06_execution/PLAN_B_EXECUTION_CONTRACT_20261106.md),
[intake contract](../06_execution/GOAL4R2A3_INTAKE_CONTRACT_20261106.md),
[closeout](../06_execution/GOAL4R2A3_CLOSEOUT_20261106.md) and
[versioned evidence](../evidence/goal4r2a3-20261106-v1/README.md).

## Results and limits

| Gate | Evidence | Verdict |
| --- | --- | --- |
| Source scripts and endpoint identities | 60 scripts inspected; 53 exact name/TID/type/unit bindings | PASS within this metadata scope |
| Internal noncommercial use | 95 supported AIDs; 10 quarantined; 47 pairs jointly pass rights and binding | Scoped support; publication, redistribution and commercial data use NOT_CLEARED |
| Protected final identities | All 24 feature-file versions; 4,723 unique structures; 14 groups and 42 proteins | PASS for declared exact-identity protection; no chemical-OOD claim |
| Candidate target metadata | Five pairs, five proteins, four broad annotations, one exposed component | Insufficient for independent twelve-family coverage |
| Structure qualification | 640 sampled SIDs; 589 cleared, 45 ambiguous/missing mappings, 6 protected exclusions | PASS; no replacement |
| First live observation canary | HTTP 200, 16,029 bytes; native envelope rejected by frozen parser | NO_GO preserved; persistent service STOP |
| Offline native-envelope adapter | Existing AID 2097 response only; 16/16 requested SIDs validated | PASS for normalization only; zero additional requests |
| Complete selected readout tuple | 16 numeric cells and 16 missing-TID cells across 16 rows | 0/16 complete tuples; no imputation |
| Paired-stage qualification and scientific pilot | Confirmation stage and expanded observations not requested | NOT_RUN |
| Historical row equivalence, benefit and novelty | No reconstruction certificate or method comparison | NOT_CERTIFIED / NOT_ESTABLISHED |

## Source and intended use

All sixty MF-PCBA scripts at commit `776cb013a5ab9949adfc9c11a212cd7ad7dada7a`
were inspected without executing their download commands or missing-potency floor.
Of 105 AIDs, 95 have supported NIH screening-programme provenance. Fifty-four
pairs have two supported AIDs; 47 jointly pass that gate and endpoint binding.

The reviewer checked 2,638 notice strings, 470 distinct, across those 95 AIDs and
found no explicit internal-use hold. Twelve Burnham AIDs refer to future scoring
publications. Empty notices are not a permission grant. Pinned programme policy
and per-AID review support internal noncommercial computational qualification
only. Publication, raw redistribution and commercial product data use remain
**NOT_CLEARED**. Code/article licences do not establish underlying row rights.

## Protection and target interpretation

The label-free union retains 24 versioned final feature files, 7,277 record
positions and 4,723 unique canonical structures. Its 14 annotation-connected
groups cover 85 registry assays and 42 UniProt proteins. The FS-Mol assay archive
and final outcome arrays were not opened. Byte-pinned RDKit 2026.09.1 retains
stereo, isotope, salt and charge information; this is exact-overlap control.

Twenty-seven UniProt requests returned 1,044 reviewed proteins in release
2026_04. The original zero-admission attempt remains preserved. Cached repairs
validated full RefSeq versions/isoform parents, retained retired IPR050332 as
positive protection, blocked protected-base/exact-version conflicts and rejected
malformed TSV records. No frozen InterPro110 type list, family role or ancestry
was rewritten. No refetch was used.

Five admitted pairs resolve to O95180, P11940, P49840, P49841 and P61088. They
span four cached broad annotations, all within `typed-ancestry-52211aa39e1b3526ca3b`:
a conservative development component linking 87 provisional groups through
typed family/superfamily entries. This dependence/protection unit is not one
homogeneous biological family. Its development exposure prevents fresh
family-transfer validation. Eleven AIDs clear the limited registry; 94 remain
unresolved and quarantined. Pair/accession counts are not independent families.

## Outcome-blind structure selection

Admission and protected-index bytes were pinned before PubChem access. A fixed
hash sample selects at most 128 common **listed** SIDs per pair before CID,
structure or observation access. Membership alone is not measurement evidence.

| Primary / confirmation AIDs | Common listed | Sampled | Cleared | Ambiguous/missing CID | Protected |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2097 / 434954 | 2,198 | 128 | 124 | 3 | 1 |
| 588489 / 602259 | 1,186 | 128 | 118 | 9 | 1 |
| 485273 / 493155 | 1,207 | 128 | 106 | 22 | 0 |
| 2650 / 463203 | 2,175 | 128 | 119 | 7 | 2 |
| 449739 / 489005 | 895 | 128 | 122 | 4 | 2 |
| Total sampled | — | 640 | 589 | 45 | 6 |

Grouped SID/CID mappings must be unambiguous. Complete `SMILES` preserves stereo
and isotopes, unlike connectivity-only SMILES in the
[official PUG specification](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/pug-rest.md).
Excluded structures were not replaced. Native parsing logs and detailed child
errors remain private; public receipts expose safe statuses and aggregates.

## Canary failure and offline repair

The full five-pair population, readouts, source versions and exact SID filters
were frozen before outcomes. The first request used 16 cleared SIDs for AID 2097.
HTTP 200 did not imply scientific success: native `PC_AssaySubmit` failed the
frozen `PC_AssayContainer` envelope check before readout interpretation. The
service STOP remained latched. No second-stage, expanded or bulk request followed.

The pinned NCBI ASN schema defines a container as a sequence of submits. A new
offline adapter wraps the retained submit structurally, verifies exact original
source/receipt/manifest hashes and AID/16-SID filters, then uses the unchanged
row-ID-first validator. It rejects suppression fields and retains original source
SHA. Original source/failure/result bytes and the network ledger remain unchanged.

The offline result validates 16 distinct SIDs and 16 rows from the primary assay.
Its two selected replicate-score TIDs yield 16 numeric cells and 16 missing cells:
**zero complete selected tuples**. This does not justify an alternative endpoint.
The sixteen `CONSISTENT_OBSERVATION` labels are singletons, not replicate-reliability
evidence. Existing comparison can conservatively flag dictionary-order differences;
conflict counts alone are not proof of differing activities.

Missing readouts were not filled; missing rows were not called untested; binary
source outcomes were not substituted for potency. This limited development sample
does not establish that other endpoints or unsampled records are unusable.
Exact historical activity bytes remain **NOT_CERTIFIED**.

## Owner checkpoint

Twenty-nine distinct named engineering checks passed in 32 case executions,
including repeated reconciliation cases. Seven bounded remote workers ran; the
live canary failed as recorded. Engineering success does not establish molecular
performance, a novel decision method or product demand.

Stop at A3 owner review. The next decision concerns a versioned endpoint/provenance
repair and credible broader family coverage, initially using metadata and value-free
missing-TID diagnostics. A revised endpoint, intake or source population needs an
explicit contract; the offline adapter does not release the stopped intake.
Do not spend B's pilot allocation or infer sufficient C potential from these results.
Potential remains unassessed, rather than demonstrated absent. Complete return and
scoped cleanup are tracked separately in the closeout.
