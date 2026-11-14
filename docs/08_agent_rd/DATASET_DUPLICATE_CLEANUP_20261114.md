# Authorized duplicate dataset cleanup

Completed 14 November 2026, after explicit owner authorization to remove unused
dataset copies. Status: **PASS_AUTHORIZED_DUPLICATE_CLEANUP**.

Removed 216 files, **2,774,958,031 apparent bytes (2.5844 GiB)**:

| Removed path relative to repository | Bytes | Retained recovery source |
| --- | ---: | --- |
| .local/lr-sc1-20261113-v1/remote-return-v1/files/assets/test_data.h5 | 1,049,345,865 | research/raw_data/external-benchmarks/scicode-2024/evaluator-private/test_data.h5 |
| .local/lr-sara-20261114-v1/native-assets-v1/tree | 1,725,612,166 | .local/lr-sara-20261114-v1/native-assets-v1/native-assets.tar.gz and private-member-manifest.json |

The first was an unused exact byte duplicate from the retired SciCode study.
The second was the 215-file expanded tree, not the original ScienceAgentBench
dataset. The selected tree can be recreated before future development canaries.
No unique dataset or canonical archive was deleted. Apparent bytes do not
guarantee the same change in physically allocated disk space.

All targets/ancestors were checked as exact absolute paths inside the intended
repository, with no reparse points. Canonical archives/files and every expanded
member were rehashed before native PowerShell literal-path deletion. Both target
paths were freshly absent afterward; canonical hashes, all 230 prior preservation
pins and the closed LR1 ledger remained unchanged. Labels/HDF5 datasets were not
parsed. No research account was reopened or scientific execution started.

Retained: ChEMBL/FS-Mol/AIC holdings, final16, private CF1 rows, unique raw data,
closed ledgers, result/source snapshots, original return manifests and receipts.
Large retired holdings still require verified cold backup before local removal.

Two pre-deletion administrative failures were recorded: using a provider-only
type property while walking .NET ancestors, and missing Get-FileHash in the
legacy shell. Both stopped before removal. The corrected type check and known
bundled PowerShell 7 completed the intended script without changing permissions.

Historical checks that require a removed path need the recorded restoration
before replay. Their frozen delivery receipts remain historical evidence and
were not rewritten to pretend the copies are still present.

- [Post-delete receipt and restore map](../evidence/dataset-cleanup-20261114-v1/cleanup-receipt.json)
- [Pre-delete validation](../evidence/dataset-cleanup-20261114-v1/pre-delete-verification.json)
- [Executed cleanup source](../evidence/dataset-cleanup-20261114-v1/executed-cleanup.ps1.txt)
- [Retained pre-delete errors](../evidence/dataset-cleanup-20261114-v1/pre-delete-administration-errors.json)
- [Project engineering memory](../00_project/ENGINEERING_MEMORY.md)
