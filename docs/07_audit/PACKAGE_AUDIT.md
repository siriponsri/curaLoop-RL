# Package audit — reviewed version 2

> Preparation record supplied with the overlay. Its 511 raw-byte and 29-PDF
> checks describe that package-building environment. Current Windows integration
> results and the explicitly different checkout-byte scope are recorded in
> [LOCAL_INTEGRATION.md](LOCAL_INTEGRATION.md). The full/private PDF package has
> not been downloaded or rechecked in this continuation.

Source checkpoint: `2d287a170b39b0c07d02631ca027c2ba535c0df9`. Documentation/literature cutoff: 4 November 2026. [Current package validation](package_validation.json) records the computed checks rather than relying on a claimed file count.

## Verified scope

All 511 protected application/resource/evidence files retain their original SHA256 values. Twenty-seven pre-refresh documents and catalogue files remain archived byte-for-byte. Version 2 retains the original application, dataset fixtures, trained tables, frontend build and historical results. No new scientific study is inferred from documentation changes.

The active literature register identifies 28 main PDFs and one supplied R05 supplement: 29 reading copies, 731 physical pages. Every copy was reopened, its page count and SHA256 matched, and source identity checked. The three newly supplied main files and supplement were inspected in substantive sections, with selected visual checks of 15 pages. R05 is ChemRxiv v3, not a verified reading of the associated journal text. The first release's access gaps and receipts are retained as history, not current limitations.

The document review checks source-version claims, manuscript assembly, metric/initialization definitions, baseline requirements, implementation states, business evidence boundaries and active cross-references. The [document matrix](documentation_review_matrix.csv) distinguishes revised documents from those checked for impact. This is a single AI-assisted review, not independent peer review or a guarantee of publication acceptance.

## Receipts

- [Package validation](package_validation.json): protected/snapshot hashes, active Markdown links, reference/BibTeX identities, consistent catalogues, configuration status, economics and manuscript assembly.
- [PDF validation](pdf_validation.json): actual hashes/page counts and source-identity checks for all 29 reading files.
- [Apply-helper checks](apply_helper_tests.json): Linux execution against an isolated source clone, including wrong-origin rejection, no-write dry run, copy/backup integrity, applied-checkout validation, CRLF-aware Git whitespace checking of all new/modified files and dirty-tree rejection.
- [Version-2 review changes](REVIEW_CHANGELOG.md): evidence-to-document impact and remaining work.

Earlier version-1 receipts are under `archive/package_v1/`; they retain their historical scope and counts. The package-level `documentation_changes.json` is regenerated relative to the original source checkpoint. The apply test records the exact manifest it exercised; later receipt-only additions may have a separate manifest identity.

The original archived catalogue CSV retains CRLF bytes. Default Git whitespace checking flags those carriage returns when the archive is newly staged. The apply guide uses a per-command `cr-at-eol` allowance and checks all other whitespace rules, without rewriting the original snapshot or changing global settings.

## NOT_RUN

New multi-target experiments, new controller training, comparator reproduction, local backend integration, customer validation, paid pilots, journal submission, archival DOI creation, remote Git push and deployment were not performed. Application Python/frontend/browser suites were not rerun for this documentation-only revision. Their previous reports remain historical. The optional PowerShell helper was statically reviewed; native Windows application remains NOT_RUN.

## Recheck

Run `python tools/check_research_package.py` in the public payload or applied checkout. In the complete package, it additionally verifies reading-room hashes if that folder is present. No paper PDF is added to the public repository. Keep the full ZIP/reading room outside Git and inspect a normal diff before the owner's push.
