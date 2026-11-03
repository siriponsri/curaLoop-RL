# Packaging & Release Validation — v3

**Version:** Audited handoff v3, 2026-11-03. Static checks are about this ZIP and its machine-readable specifications; **not** about code which GPT Work will create afterwards.

## Checks performed

- Previous v2 ZIP: 36 entries, 67,094 bytes, CRC `ZipFile.testzip() == None` — structurally intact.
- Previous v2 downloader helper: 3 tests passed; 20 OA manifest candidates listed by dry-run; **no real article downloaded or license verified by dry-run**.
- v3 downloader helper and bundle validator: **10 tests PASS** (3 downloader-helper tests + 7 archive/structure tests); command `python -m unittest discover -s scripts -p 'test_*.py' -v`. These are pack tests, **not application tests**.
- JSON parser and Draft202012 schema structural checks for all `*.json` and `*.schema.json`.
- YAML parser checks for two scenario examples.
- Archive safety: no `..`, absolute or backslash entry; ZIP member content hashes equal source tree files; CRC check; no third-party PDF binaries.
- `papers_manifest.json`: 25 unique IDs, all URLs HTTPS, **7 source metadata checks** and **18 not independently verified in this pass**. No assertion of article PDF rights.
- Run `python scripts/validate_handoff_pack.py . --zip <full-path-to-new-ZIP>` from the extracted root. Exact archive SHA256 is recorded in **companion `.sha256` file outside ZIP** (hash cannot be embedded recursively).

## Limitations / open gates

- Actual browser download success is determined by the user/client; a verified local sandbox path is not proof of success on every device.
- No network PDF fetch, no full systematic literature audit and no rights clearance performed for 25 papers.
- No runnable app was built within this handoff; new app tests are `NOT_RUN` until Work builds it.
- No real dataset ingestion/chemical predictive validity or statistical result exists.
- No real RL trained; no prospective assays, physical Digital Twin synchronization, GPO endorsement, GMP validation or ROI evidence.
- Repository ownership, public visibility, third-party licenses and internal organizational policy remain owner decisions.

## Release decision

**GO for giving specifications to GPT Work** if all structural checks pass. **NO-GO for claiming a working drug discovery platform, trained RL, live Digital Twin, paper PDFs included, organizational endorsement or external regulatory validation.**
