# CURALOOP-RL — MASTER PROMPT FOR GPT WORK
## Upgrade the existing research starter into a beautiful, fully functional localhost pharmaceutical R&D web application

You are a senior full-stack engineer, scientific-software architect, frontend designer, accessibility reviewer, and QA auditor. Deliver a *real working source-code revision* to the provided CuraLoop-RL project. Do not deliver only design files, mockups, static HTML screenshots, documents, or a new unrelated template repository.

### 0. Input and identity

The attached `CuraLoopRL_Full(1).zip` was produced by GPT Work and contains `CuraLoopRL-history.bundle`, `curaloop-rl/`, source code, research data, a Streamlit dashboard, tests, and handoff evidence. Restore the *actual Git history* from the bundle using the ZIP-level Windows instructions and verify its HEAD against `SOURCE_COMMIT.txt` / `RELEASE.json`. Read `AGENTS.md`, `HANDOFF_TO_CODEX.md`, `README.md`, `docs/BRAND.md`, `docs/AUDIT_REPORT.md`, `docs/ARCHITECTURE.md`, and `docs/EVALUATION.md`.

This is an **independent personal portfolio**, possibly shown to researchers at the Government Pharmaceutical Organization (GPO) in Thailand. It is **not** an official GPO system, clinical tool, operational Digital Twin, validated decision system, or organizational deployment. Never use GPO logos, internal documents, private datasets, credentials, or implied endorsement.

**First verify existing tests and working app.** The previous handoff reported 79 passing Python tests on Linux; independently run and record what is true in your environment. Never describe old test evidence as your own execution.

### 1. Deliverable / primary outcome

Replace the **primary demo UI** with a polished React + TypeScript + Vite application, using Tailwind CSS and shadcn/ui, Recharts for truthful scientific charts, and optional `@xyflow/react` for the retrospective simulation flow. Connect it to the *existing working* Python `curaloop` domain/simulator/policy/evaluation code through a local FastAPI service.

Keep the original Streamlit application available as a working fallback under `app/streamlit_app.py`; do not break it or overwrite the scientific engine.

Architecture target:

```text
frontend/ (Vite + React + TypeScript + Tailwind + shadcn)
        | HTTP localhost, typed API client
        v
api/ (FastAPI: schema validation, run sessions, exports)
        | call existing service/domain
        v
src/curaloop/ (unchanged scientific logic except documented bug fixes)
        | historical HIV + synthetic fixtures + trained controllers
```

Dev mode: frontend on `http://localhost:5173`, API on `http://127.0.0.1:8000`, strict local proxy/CORS. Demo/release mode: build React static assets and have FastAPI serve them from `http://127.0.0.1:8000` so the owner opens only *one address*. Bind exclusively to loopback by default, never `0.0.0.0`.

Provide `Start-CuraLoop-Web.cmd` for Windows without administrator rights and `scripts/start_local.ps1` if helpful. First-time installation may require Python and Node.js; subsequent demo runs must not require internet or paid APIs. Do not auto-install global executables or alter execution policy; verify prerequisites and provide comprehensible instructions. Build and bundle frontend static assets into the release artifact.

### 2. Open-source visual references; adapt selectively

Review the following real repos and their current license files, compatible dependencies, and security implications *before copying any code*. Prefer using official component packages and design patterns over forking a whole application:

- https://github.com/shadcn-ui/ui (MIT; component foundations)
- https://github.com/shadcndashboard/shadcndashboard (MIT, React + Vite dashboard shell/layout ideas; project README requests attribution; avoid importing fake data/auth/blog/CRM modules)
- https://github.com/tremorlabs/tremor (Apache-2.0; charts/dashboard design patterns if useful)
- https://github.com/xyflow/xyflow (MIT React Flow; an optional process flow)
- https://github.com/recharts/recharts (MIT; scientific charts)

Do not copy proprietary/pro-tier templates or assets. Retain required copyright and attribution in `THIRD_PARTY_NOTICES.md` and any attribution requested by source maintainers. Avoid chart libraries with unexpected commercial or redistribution license terms. Record exact repositories, commits/versions, licenses, and files actually adapted. If a template is too complex, build an original application shell using shadcn/ui instead.

### 3. Design language

Create a visually distinctive **scientific decision-support workbench**, not a generic enterprise admin portal and not a neon/cyberpunk biotech fantasy. Reuse the existing original CuraLoop-RL logo and brand palette (`docs/BRAND.md`: teal `#087F72`, midnight `#16333B`, amber `#B66914`); extend it with restrained mint, white/off-white, stone neutrals, and accessible chart colors. Professional, editorial layout, balanced whitespace, high-contrast headings, layered but restrained cards, careful micro-interactions, smooth but useful transitions. Rich visual information must reflect actual application state.

Desktop-first for presentations at 1440px wide, and fully responsive at 390px mobile. Support Thai and English clearly, using a Thai-capable font (the project bundles licensed NotoSansThai), not mixed-font glyph clipping. Provide intentional empty states, loading states, error states, data disclaimers, keyboard focus states, color-independent chart legends, and reduced-motion support.

**Do not stop at cosmetic design:** every navigation item, form, chart, export, button, timeline, filter and simulated lab control must actually work, or be clearly labelled as planned and omitted from release UI.

### 4. Required functional pages

1. **Overview — Discovery Mission.** A compelling question: 'With a screening budget of 30 assays among 1,200 historical compounds, which should we test first?' Show real dataset provenance, a 4-step research workflow, live scenario KPIs and a short call to action. Keep historically measured assay labels distinct from simulated budget/delay/cost assumptions. Do not imply clinical efficacy.
2. **Compound Explorer.** Search/filter/sort a public candidate pool by compound ID, known public descriptors, and request/result status. Offer optional genuine 2D molecule images rendered from the available canonical SMILES via RDKit if the dependency is available. Labels for *unselected* compounds must never be exposed. No virtual compound image placeholders presented as real structures.
3. **Scenario Builder.** Select historical HIV vs synthetic scenario, random seed, budget units, batch size, delay steps, jitter, missingness, and policy. Validate input using the existing `Scenario` rules and show readable assumptions; don't call synthetic cost units USD/THB.
4. **Simulation Lab / Digital Twin Readiness.** React Flow (optional) for Pool -> Select -> Queue -> Simulated Assay -> Deliver Result -> Update. Node statuses must be driven by real events. Functional actions: start run, select batch, advance step, finish, replay, reset. Show pending and delivered separately, meaningful action explanations, an event timeline, remaining/reserved/spent budget, actual delivered outcomes only. Prominently label this as **Retrospective Screening Simulator — Not a Validated Digital Twin**.
5. **Benchmark Arena.** Matched-policy comparisons (Random, Greedy, Uncertainty; Q-learning and Contextual Bandit when valid) using actual independent runs, same seed labels, budget, features and conditions. Display confirmed new hits vs budget spent, uncertainty/variability when available, event-derived metrics, provenance, descriptive results and fallback counts. Specifically disclose that reported learned-controller historical comparisons invoked a Greedy fallback; never claim RL superiority or transfer without evidence. Avoid a curated demonstration seed chosen only for attractive results.
6. **Research Evidence & Limitations.** Scientific model/data provenance, source links, software version/SHA, synthetic-vs-historical labels, known evaluation weaknesses, limitations, 79-test historical claim with clear verification status, and access to JSON/CSV downloads. State 'personal portfolio; not official GPO'.
7. **Guided Presentation.** An optional 5-7 minute walkthrough using real interactions and a deterministic preconfigured scenario with honest output, readable to pharmaceutical and non-ML audiences. Do not generate fake success metrics or fabricate screenshots.

Do not show a page with no purpose; combine pages if it improves presentation and technical simplicity.

### 5. Backend API and correctness

Reuse public `RunService`, `compare`, data models and existing export utilities; don't reimplement selection, model inference, budget accounting or event semantics in JavaScript.

Suggested typed API endpoints, subject to adaptation to existing contracts:

- `GET /api/v1/health` and `GET /api/v1/meta`
- `GET /api/v1/datasets` and `GET /api/v1/policies`
- `POST /api/v1/runs` (create one session with scenario+policy)
- `GET /api/v1/runs/{run_id}` (public observation and event-derived aggregates only)
- `POST /api/v1/runs/{run_id}/select` (invoke actual `next_batch()`)
- `POST /api/v1/runs/{run_id}/advance` (invoke actual `advance()`)
- `POST /api/v1/runs/{run_id}/finish`
- `POST /api/v1/comparisons` (actual matched comparisons)
- `GET /api/v1/runs/{run_id}/export?format=json|csv` (use actual export code)

Validate types, bounds, state transitions and response contracts. Keep run sessions isolated, deterministic, restart behavior documented and error surfaces readable. Restrict CORS to local development origins. No API may expose `TruthStore`, full hidden label data, future outcomes, or disallowed internal imports. Do not return the full original dataset records with `active` labels. Publishing a public historical dataset does not excuse leaking private oracle state into the selection UI.

**Known metadata issue to audit/fix:** existing `RunService.report()` contains a dataset `source` string hardcoded as `Original in-process synthetic generator; no external data.` while historical HIV replay is supported. Correct provenance attribution per dataset type without altering assay semantics; add a regression test to catch it. Preserve source hashes and manifests.

### 6. Acceptance tests — mandatory

1. Rerun all existing Python tests, retaining or improving the previous 79 test cases; no regression in deterministic replay, leakage prevention, budget, delays, export and metrics.
2. Add FastAPI contract tests: health, datasets, run creation, selection, advance, finish, compare, JSON/CSV exports, invalid inputs, concurrent/session separation, and hidden-label nonexposure.
3. Add frontend tests for routing, forms, validation, API errors, screen states and data labels. Verify `npm run build`, TypeScript check and lint in actual execution.
4. Run **real Playwright browser smoke tests** on the working local app. Capture at least Overview, Scenario, Simulation before and after result delivery, Benchmark, Evidence, and mobile viewport. Test on desktop ~1440x900 and mobile ~390x844; no horizontal overflow, clipping, Thai font rendering problems or inert buttons.
5. Compare a fixed API-run JSON report with the preexisting CLI/Streamlit engine's result under identical parameters. Verify reproducible metrics and no extra labels returned.
6. Log actual commands and pass/fail/skip. Never report tests as passed unless executed. The original 79 pass are historical evidence until retested.
7. Provide one-click localhost run in production mode with built frontend assets. Confirm browser content is served at `http://127.0.0.1:8000` in your execution environment; if not possible, mark NOT_RUN and provide Windows verification instructions.
8. Do not silently expand dependencies into cloud platforms, mandatory external databases, auth services, subscriptions, paid model APIs or unnecessary GPU workloads.

### 7. Work priorities and stop conditions

A. **Audit the original repo** and create a checkpoint commit on a dedicated local branch (`feat/local-web-ui`).
B. Implement the local FastAPI adapter and contract tests before UI integration.
C. Build a coherent high-quality design system and functional pages, wiring each to real API data.
D. Make a packaged local release and Windows launcher; preserve Streamlit as fallback.
E. Run the full QA suite + real browser review, fix visual/functional defects and document residual risks.
F. Update `README.md`, `START_WINDOWS_TH.md`, `THIRD_PARTY_NOTICES.md`, `docs/ARCHITECTURE.md`, and `HANDOFF_TO_CODEX.md`.

Favor an elegant, working subset over a huge incomplete template. If capacity is limited, finish Overview, Scenario Builder, Simulation Lab, Benchmark Arena, and Evidence first, with operational backend and tests; add compound explorer/presentation only when core passes.

### 8. Owner permissions and handoff

You may fetch public repositories and allowed dependencies for local build, provided that you check licenses and do not expose owner data. You may create local Git commits. **Do not push to GitHub, deploy, publicize, change sharing permissions, access organizational systems, use paid services or purchase anything without explicit owner authorization.**

Deliver:

- A real revised repo source ZIP preserving `.git` history via a valid Git bundle if ZIP packaging strips `.git`.
- An executable one-click Windows localhost launcher and offline-ready built frontend assets.
- An updated `HANDOFF_TO_CODEX.md` including exact current SHA, working branch, test evidence, current screenshots, technical debt, security/scientific limitations, and three prioritized next tasks.
- A brief Thai operator guide: extract -> setup -> double-click -> open localhost, plus manual CLI fallback.

**Definition of Done:** A solo owner on Windows can start CuraLoop-RL locally, see a premium-quality responsive scientific web app, run a real historical/synthetic screening campaign, follow the event timeline, compare actual policies, export event-derived results and audit limitations — without losing or falsifying the original research engine.

Do the work now: inspect, implement, run, visually audit, fix, commit, and package. Do not stop at a plan or at static mockups.
