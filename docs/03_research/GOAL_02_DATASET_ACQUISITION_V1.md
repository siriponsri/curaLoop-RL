# Paper-backed external benchmark acquisition

Read-only dataset research, 4 November 2026. Dataset selection is based on
source, endpoint and transfer design, not unseen acquisition scores. No
external assay rows were downloaded or assigned CuraLoop evaluation roles.

## Ready development source: Tox21

The [challenge paper](https://doi.org/10.3389/fenvs.2015.00085) and
[official training files](https://tripod.nih.gov/tox21/challenge/data.jsp)
support the three exposed development derivatives used in the
[Goal2 protocol](GOAL_02_REAL_DATA_PROTOCOL_V1.md). Hashes, preprocessing,
row-count discrepancies and limitations are explicit there. These are real
historical experimental labels with simulated operations, not new experiments.

## FS-Mol: owner download requested

Use the [official version1 record](https://figshare.com/articles/dataset/FSMol_Dataset/16941100),
DOI10.6084/m9.figshare.16941100.v1, accompanying
[Stanley etal., NeurIPS Datasets and Benchmarks2021](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html).
The [official metadata](https://api.figshare.com/v2/articles/16941100) identifies:

| Field | Verified source value |
| --- | --- |
| File ID / format |31345321 / uncompressed tar, application/x-tar |
| Filename |fsmol.tar, not tar.gz |
| Size |4,871,086,080 bytes |
| Published MD5 |0ad8f73db6bb8415b023538d514138dc |
| Local SHA256 |UNKNOWN; calculate from received bytes |
| Direct official URL |https://figshare.com/ndownloader/files/31345321 |
| Automated file acquisition |BLOCKED: HTTP403; no bypass or alternate mirror attempted |

Place the archive at:

`C:\Users\User\Desktop\myProject\curaloop-rl\research\raw_data\external-benchmarks\fs-mol-0.1\fsmol.tar`

This ignored destination is prepared. An async owner request supplies the
source, size and path. Do not extract or inspect labels merely because a file
arrives: first verify size/MD5, compute SHA256 and retain the raw archive.
`tools/verify_fsmol_archive_v1.py` performs only byte-level verification, without
opening archive members. Unknown tar root/layout remains UNKNOWN until inspected.

Official repository pin92aa95daba3f43863227e65be85a07b4a2ee754f:
[README](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/README.md),
[task manifest](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/datasets/fsmol-0.1.json),
[license](https://raw.githubusercontent.com/microsoft/FS-Mol/92aa95daba3f43863227e65be85a07b4a2ee754f/LICENSE).
Read-only manifest review found4938train/40valid/157test,5135 distinct assay IDs
and no cross-role ID overlap. The paper states5120 total: this discrepancy is
unresolved, not silently corrected. Source roles do not automatically become
CuraLoop roles; overlap with development structures/families must be audited.

Figshare labels the archive CC BY4.0; the repository assigns datasets/ CC BY-SA3.0
with upstream ChEMBL27 provenance. MIT applies to the remaining source code.
Both data notices must be preserved; a uniform redistribution grant is not
resolved by choosing the more permissive badge. Keep raw/derived assays outside
public Git while the release-specific attribution/redistribution review closes.

FS-Mol uses IC50/EC50 measurements with constrained assay-median binary labels,
retaining30–70% positive ratios; large HTS assays are excluded. A positive means
above the dataset's assay-relative activity criterion, not a sparse confirmed
screening hit or therapeutic efficacy. Its protein-target-separated test split
allows compound overlap: paper totals27520test compounds,15732unseen in train/
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
