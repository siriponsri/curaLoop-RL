> Documentation update, 4 November 2026: [current programme](07_audit/PACKAGE_AUDIT.md) and [documentation map](README.md). The detailed record below is retained from the inspected POC checkpoint. New research and commercial capabilities are specifications until implemented; prior test counts are historical execution, not new checks.

# README, branding and English manual verification

Date: 2026-11-04 (Asia/Bangkok). Base: `19134d597c4e1f232864d21a920a06c0693cf737`.

Material content: `344d0e37ad78677202bc7afc9f809d3558aecbdd`. Normal main push
and live remote readback confirmed this checkpoint. The following receipt commit
adds source/build/asset digests in `evidence/readme-manual-v1/refresh-identity.json`
and updates the root runtime marker; original release records remain historical.

## Delivered

- A professional English README with an overview, genuine application preview,
  workflow/architecture diagrams, quick start, scientific scope and documentation.
- New versioned CuraLoop-RL PNG artwork: a transparent application wordmark and
  opaque light-paper README header, readable in both README color themes.
- Two source-grounded diagrams, each with self-contained editable HTML, SVG and
  high-resolution PNG: architecture and the screening loop.
- A 20-page illustrated English PDF manual linked from the README. It includes
  19 bookmarks, 25 internal/external links, real screenshots, installation,
  campaign operation, policy comparisons, export/resume and revision recovery.
- Reproducible diagram, capture and manual-builder scripts. Optional PDF
  dependencies stay separate from application dependencies.

## Actual checks

| Check | Result |
| --- | --- |
| Locked Windows Python suite | 136 PASS, 0 FAIL/SKIP, 1 inherited Starlette/httpx warning; 431.70s |
| Frontend tests | 18 PASS, 0 FAIL/SKIP |
| TypeScript/Vite production build | PASS; lazy route/chart chunks, no size warning |
| ESLint and Ruff | PASS |
| Actual Chromium application workflow | PASS; 31 loaded full-page captures plus 37 manual-oriented views |
| Desktop/mobile | 1440x1000 / 390x844; zero page overflow or JavaScript errors |
| Automated accessibility | 18 route/state audits, zero violations |
| Offline request boundary | Zero external requests; app assets/fonts/structures loaded locally |
| Campaign correctness | Actual pending restart, delayed reveal, budget, active/inactive/missing, replay/reset and independent matched comparisons |
| Evidence portability | Five actual reports and 335 CSV events parsed; invalid import rejected; saved campaign/revision recovery passed |
| Diagrams | Skill self-check PASS; offline Chromium rendering, all text bounds and local mobile scrolling PASS |
| PDF structure | 20 pages, 19 bookmarks, 25 links; extractable English text; no out-of-bounds text |
| PDF visual inspection | All 20 pages rendered; contact sheet and full-size representative pages inspected; no clipping/overlap/missing glyphs found |
| README | Relative targets and light/dark/mobile local Markdown rendering checked separately in readme-validation.json |
| Original research assets | 191-file fixed-base byte preservation checked separately in preservation.json; engine/API and old v0.3 evidence remain unchanged |
| Fresh Windows checkout | PASS; all 191 protected files, nine released visual/PDF assets, frontend build and API byte digests match; not a second runtime execution |

Raw records and captures are under `docs/evidence/readme-manual-v1/`.
`manual-manifest.json` identifies the actual screenshot build:
`24f563fcb7e07d9d6284d5f4af60d0aa807031056bc4843cb97d44d4c0355805`.

The owner's production service already occupied port 8000. It was not stopped or
mutated. An isolated API process with temporary SQLite state served the actual
built frontend on approved loopback origin `http://127.0.0.1:5173` for capture.
The production launcher/address remains `http://127.0.0.1:8000`. An existing app
process needs a normal restart to refresh the cached build identity after a rebuild.

The first capture attempt on port 8000 stopped without touching that service. The
first isolated run hit a five-second replay-readiness timeout while the engine
was busy under concurrent CPU tests. Its packet is retained as `browser-round1`.
The complete workflow was rerun with a 30-second default readiness deadline and
passed; no application failure was skipped. Poppler emitted missing optional
Symbol/ArialUnicode display-alias messages, but inspected output has no missing
glyphs or layout defect. The PDF uses standard Latin fonts and actual images.

## Tooling and provenance

Diagram Design skill: project-local adaptation in `docs/design/diagram-style.md`,
using existing project colors and disclosed offline system-font fallback. The
installed skill and global style/profile configuration were not changed.
Its SVG export helper and offline self-check were used. Browser/PDF renders
provide the static PNGs; no generated UI mockup is presented as a screenshot.

Built-in image generation produced the versioned brand artwork. The original logo
and all earlier screenshots remain untouched. Prompts/asset roles are recorded in
`assets/branding/PROVENANCE.md`. Image-generation previews that failed edge quality
were not released or referenced by the project.

The PDF uses the bundled local ReportLab 4.4.9 runtime, pypdf 6.10.0 and Poppler.
App screenshots and diagram rasterization use project-local Playwright 1.64.1.
Local README preview uses CommonMark/table rendering with GitHub-like CSS; it
does not claim equivalence with GitHub's production renderer.

## Rebuild

```powershell
python scripts/build_readme_diagrams.py
python scripts/render_readme_diagrams.py
# Optional PDF dependencies:
python -m pip install -r requirements-docs.txt
# Capture to a NEW evidence directory for subsequent verification:
python scripts/web_browser_smoke.py --manual --port 5173 --output outputs/manual-capture
# build_user_manual.py defaults to the committed readme-manual-v1 capture packet.
python scripts/build_user_manual.py
```

SVG sources are already included; regeneration used the Diagram Design skill's
`scripts/export_svg.py --system-fonts`. Keep earlier captured evidence intact.
The PDF builder accepts only a passing capture packet and embeds those real PNGs.

## Scope

No scientific protocol, label, dataset, trained model, API state transition or
recorded benchmark changed. Only documentation, branding asset references and
verification/authoring utilities changed. The earlier POC release report remains
a historical release identity; this documentation refresh has its own evidence.
Native CMD restart and a new Streamlit browser capture were not repeated in this
round; the Python suite includes the eight fallback AppTests. Earlier executed
Windows launcher/fallback evidence remains preserved. Clinical/prospective,
other-engine, physical-device and manual-screenreader validation is not implied.
