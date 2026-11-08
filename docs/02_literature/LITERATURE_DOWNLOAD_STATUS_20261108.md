# Literature reading copies: current download status

8 November 2026. **PARTIAL_DOWNLOAD_COMPLETE**, distinct from reading or reproduction.

The owner identified the existing literature manifest and requested downloads.
The fresh reading room contains **25 of 28 main PDFs**, totaling **107,553,115
bytes and 666 pages**. Every available file was reopened, checked for PDF
structure/page count and title identity, and SHA-256 matched against the existing
register. The original manifest is unchanged. One supplement is also outstanding.

Private entry point on the owner's machine:
`C:\Users\User\Documents\ChatGPT\Drug Discovery\literature\OPEN-READING-ROOM.html`.
PDFs are in its `pdfs` directory. Public Git contains the
[verification receipt](LITERATURE_DOWNLOAD_RECEIPT_20261108.json), not the papers.
Transport logs and interrupted partials are retained privately and are not counted
as available papers. An interrupted initial transfer was resumed with byte ranges;
fresh validation, rather than transport success alone, determined availability.

## Copies still needed

Place a lawful copy in the private reading room's `pdfs` folder using the indicated
filename. A replacement must be version-checked before its status changes. No
purchase, credential request, certificate-check relaxation or access bypass was used.

| ID | Source/version needed | Current obstacle | Target filename |
| --- | --- | --- | --- |
| R03 | [LIT-PCBA](https://doi.org/10.1021/acs.jcim.0c00155), HAL hal-03013622v1 author manuscript, 32 pages including cover; [HAL copy](https://hal.science/hal-03013622v1/file/revised_manuscript_final.pdf) | Windows TLS revocation service was unavailable; checks were retained | `R03_lit_pcba_hal_manuscript.pdf` |
| R05 | [Traversing Chemical Space](https://doi.org/10.26434/chemrxiv-2023-wgl32-v3), ChemRxiv v3, 23 February 2024 | HTTP 403 | `R05_traversing_chemical_space_chemrxiv_v3.pdf` |
| R05_SI | Matching R05 v3 supplementary information, 7 pages; obtain from the preprint record above | No confirmed matching download URL; a different version was not substituted | `R05_SI_traversing_preprint_supplement.pdf` |
| R26 | [BayBE](https://doi.org/10.1039/D5DD00050E), RSC publisher copy, 11 PDF pages including issue cover | HTTP 403 | `R26_baybe_publisher.pdf` |

The RSC indexed PDF states CC BY 3.0, whereas the historical register describes
CC BY 4.0. Keep this as an unresolved license-metadata discrepancy until the
actual publisher copy is checked; do not redistribute based on the older field.

## Reading and positioning

The download itself does not mean 666 pages were read. The
[positioning review](POSITIONING_REVIEW_20261108.md) identifies exactly which
methods, results and versions were inspected. A newly recovered, exact R07 GLARE
PDF enabled a local method/experiment refresh; that strengthened the prior-art
warning against claiming broad RL acquisition as new. No reported result was
independently reproduced, and no M2 or final study was released.

`tools/download_literature_reading_room_v1.py --output <fresh-outside-repository-directory>`
provides a bounded initial download utility for manifest entries with public
sources. It refuses an existing output directory and does not resume this completed
room or automatically resolve the four outstanding sources.
