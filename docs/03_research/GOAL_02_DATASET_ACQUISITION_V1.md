# Paper-backed external benchmark acquisition

Read-only dataset research, 4 November 2026, with an acquisition update on
5 November. Dataset selection is based on source, endpoint and transfer design,
not unseen acquisition scores. The owner has now supplied the FS-Mol archive;
no archive member or external assay label has been opened or assigned a
CuraLoop evaluation role.

## Ready development source: Tox21

The [challenge paper](https://doi.org/10.3389/fenvs.2015.00085) and
[official training files](https://tripod.nih.gov/tox21/challenge/data.jsp)
support the three exposed development derivatives used in the
[Goal 2 protocol](GOAL_02_REAL_DATA_PROTOCOL_V1.md). Hashes, preprocessing,
row-count discrepancies and limitations are explicit there. These are real
historical experimental labels with simulated operations, not new experiments.

## FS-Mol: owner archive received and byte-verified

5 November update: **PASS**, the owner-supplied archive matches the expected
size and MD5. The [receipt](../evidence/fs-mol-receipt-20261105-v1/README.md)
records the full-file SHA256 and verification output. Goal 3 has not started;
archive extraction, label inspection and task-role assignment remain unperformed.

Use the [official version 1 record](https://figshare.com/articles/dataset/FSMol_Dataset/16941100),
DOI 10.6084/m9.figshare.16941100.v1, accompanying
[Stanley et al., NeurIPS Datasets and Benchmarks 2021](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html).
The [official metadata](https://api.figshare.com/v2/articles/16941100) identifies:

| Field | Verified source value |
| --- | --- |
| File ID / format |31345321 / uncompressed tar, application/x-tar |
| Filename |fsmol.tar, not tar.gz |
| Size |4,871,086,080 bytes |
| Published MD5 |0ad8f73db6bb8415b023538d514138dc |
| Local SHA256 |`528a9c4e8d74c4287acda79536eecbf91418d6d0ac2c55918b270d78c2333ebc` |
| Direct official URL |https://figshare.com/ndownloader/files/31345321 |
| Automated file acquisition |BLOCKED: HTTP403; no bypass or alternate mirror attempted |

Place the archive at:

`C:\Users\User\Desktop\myProject\curaloop-rl\research\raw_data\external-benchmarks\fs-mol-0.1\fsmol.tar`

The owner placed the archive at this ignored destination. The existing
`tools/verify_fsmol_archive_v1.py` completed size/MD5/SHA256 verification without
opening archive members. The raw archive is retained. Unknown tar root/layout
remains UNKNOWN until an authorized inspection; byte verification does not
close the data-rights, phenotype, overlap or split gates below.

Official repository pin: `92aa95daba3f43863227e65be85a07b4a2ee754f`.
[README](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/README.md),
[task manifest](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/datasets/fsmol-0.1.json),
[license](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/LICENSE).
Read-only manifest review found 4,938 train, 40 validation and 157 test tasks:
5,135 distinct assay IDs and no cross-role ID overlap. The paper states 5,120 total: this discrepancy is
unresolved, not silently corrected. Source roles do not automatically become
CuraLoop roles; overlap with development structures/families must be audited.

Figshare labels the archive CC BY 4.0; the repository assigns datasets/ CC BY-SA 3.0
with upstream ChEMBL 27 provenance. MIT applies to the remaining source code.
Both data notices must be preserved; a uniform redistribution grant is not
resolved by choosing the more permissive badge. Keep raw/derived assays outside
public Git while the release-specific attribution/redistribution review closes.

FS-Mol uses IC50/EC50 measurements with constrained assay-median binary labels,
retaining 30–70% positive ratios; large HTS assays are excluded. A positive means
above the dataset's assay-relative activity criterion, not a sparse confirmed
screening hit or therapeutic efficacy. Its protein-target-separated test split
allows compound overlap: the paper reports 27,520 test compounds, 15,732 unseen in train/
validation. Assay IDs and tasks are not counts of independent biological families.
Use as a transfer/potency-threshold complement, not a replacement label for HTS.

## Other real benchmark candidates

| Dataset and supporting paper | Readiness / reason not ingested |
| --- | --- |
| [LIT-PCBA, Tran-Nguyen etal., JCIM2020](https://doi.org/10.1021/acs.jcim.0c00155); [official15-target resource](https://drugdesign.unistra.fr/LIT-PCBA/) | Stronger sparse-screening complement; active.smi/inactive.smi and train/validation files documented, but explicit prepared-file reuse grant/release archive identity unverified; provider endpoints and original benchmark ascertainment require review. No label download. |
| [MoleculeNet, Wu etal., Chemical Science2018](https://doi.org/10.1039/C7SC02664A), MUV17 /PCBA128 | Official DeepChem loaders point to muv.csv.gz /pcba.csv.gz, but release-specific assay grants, outcome/missingness semantics and overlap remain open. Software MIT does not grant all data rights. No label download. |

## JCAMD impact assessment

Inference: a method that improves useful assay prioritization across molecular
families and operational shifts, with strong non-RL baselines and realistic
retrospective validation, aligns with the
[journal scope](https://link.springer.com/journal/10822/aims-and-scope).
The journal prioritizes experimental validation and allows proper retrospective
validation for novel methods/innovative computational strategies. Merely adding
more task IDs, relabelling potency positives as hits, or improving one exposed
toxicology panel does not establish that contribution. Preserve source-derived
endpoint meaning and pursue a rights-cleared sparse-screening complement later.
No submission, outreach, payment or acceptance is implied.
