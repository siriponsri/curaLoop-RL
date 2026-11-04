# CuraLoop-RL diagram style

Project-local adaptation of the Diagram Design skill. Source: `DESIGN.md` and
the established application palette. No installed skill or global profile is edited.

| Role | Value |
| --- | --- |
| Paper | `#F7F9F8` |
| Surface | `#FFFFFF` |
| Ink | `#16333B` |
| Muted / soft | `#526653` |
| Accent | `#087F72` |
| Accent tint | `#E6F3EB` |
| Rule | `#DCE5E1` |
| Link | `#176C83` |
| Caution | `#9A5A10` |

Typography uses the installed system stack `Segoe UI, Arial, sans-serif` and
`Consolas, monospace` for technical labels. This is an explicit offline fallback
for the application's bundled CuraThai font; no external font request is made.
The existing local palette and brand authority select this project skin instead
of the skill's unrelated default palette. No saved-profile or global mutation.

Outputs: editable self-contained HTML sources plus SVG/PNG assets for the README
and English PDF manual. Architecture: 6 nodes, 5 permitted-call connections,
1120x792 print layout, mixed technical/research audience. Screening loop: 6
stations and one public ledger hub; bounded repeat, delayed visibility and
event-derived accounting. No animation or inferred infrastructure.

Source mapping: `api/main.py`, `api/storage.py`, `src/curaloop/service.py`,
`engine.py`, `policies.py`, `_oracle.py` and `docs/ARCHITECTURE.md`.
