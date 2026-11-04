# FS-Mol archive receipt

5 November 2026, Asia/Bangkok. The owner supplied the requested official archive
after the earlier automated download returned HTTP 403. This receipt completes
byte-level acquisition follow-up; it does not start Goal 3.

**PASS:** the received file is 4,871,086,080 bytes and its MD5 matches the pinned
release value. SHA256 was calculated from the full received byte stream:

`528a9c4e8d74c4287acda79536eecbf91418d6d0ac2c55918b270d78c2333ebc`

| Item | Value |
| --- | --- |
| Official record | [FSMol Dataset v1](https://figshare.com/articles/dataset/FSMol_Dataset/16941100), DOI 10.6084/m9.figshare.16941100.v1 |
| File | `fsmol.tar`, provider file ID 31345321 |
| Expected and observed MD5 | `0ad8f73db6bb8415b023538d514138dc` |
| Verification | [Machine-readable result](archive-verification.json) |
| Local archive | `research/raw_data/external-benchmarks/fs-mol-0.1/fsmol.tar` |
| Base main | `e76b8371f9b6007951d6b1f43f7b91b42b008647` |

The existing `tools/verify_fsmol_archive_v1.py` checked file size, streamed MD5
and SHA256, and returned exit code 0. No archive member was opened, extracted
or parsed; no assay labels were inspected or assigned evaluation roles. The
archive remains ignored and outside public Git. Earlier missing-file and HTTP
403 records remain intact as historical evidence.

See [dataset provenance and paper](../../03_research/GOAL_02_DATASET_ACQUISITION_V1.md).
Release-license notices, endpoint meaning, manifest/paper count discrepancy,
structural overlap and independent-family/split review remain pending. Byte
identity alone does not clear these scientific data-readiness gates. No new
campaign, model fitting, SSH job or journal action was performed in this follow-up.
