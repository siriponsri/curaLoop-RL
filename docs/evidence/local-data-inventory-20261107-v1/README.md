# Local data inventory and Deep Research handoff

This owner-requested metadata/document audit does not release R0-QC, a new
research budget, dataset processing, source intake or final outcomes.

- [Readable data inventory](../../03_research/LOCAL_DATA_INVENTORY_20261107.md)
- [Copy-ready Deep Research prompt](../../02_literature/DEEP_RESEARCH_PROMPT_20261107.md)
- [Filesystem summary v2](filesystem-summary-v2.json): declared roots, matching
  file metadata, apparent byte lengths and excluded directories. V1 remains
  as the original snapshot; its `matching_physical_bytes` key was a legacy
  name for summed file lengths, not measured disk allocation.
- [Fresh small-file integrity](small-file-integrity-v1.json): 28 opaque file
  digests against existing manifests; no dataset row/array/label decoding.
- [Existing evidence source pins](evidence-source-pins-v1.json): cards, manifests
  and aggregate reports consulted; not new web/source verification.
- [Handoff validation v2](handoff-validation-v2.json): limits, old ledger hashes,
  current source-file sizes, document links and helper syntax.

Validation v1 is retained as the pre-editorial checkpoint. V2 updates the
document/helper digests after prose and navigation edits; scientific source
counts, digest results, protected roles and closed ledgers are unchanged.

The complete matching filename/stat index is retained privately at
`.local/data-inventory-20261107-v1/file-metadata-v1.json`; it contains no file
contents. Large archives were not reopened or rehashed. Their quoted digest
verification is historical and explicitly separate from current file-size checks.
Private raw payloads, final features, source PDFs and label arrays are not
published here. Source/return duplicates, code/configs and prior run outputs
are not independent measurement datasets.
