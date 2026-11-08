<h1 align="center">Screening decisions you can audit.</h1>

<p align="center">
  A local research workbench for sequential pharmaceutical screening.<br>
  Choose candidates. Wait for feedback. Compare policies. Preserve the evidence.
</p>

<p align="center">
  <a href="docs/manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf"><strong>English user manual (PDF)</strong></a> &nbsp;·&nbsp;
  <a href="docs/evidence/four-screen-dashboard-20261108-v1/README.md">EN/TH screen gallery</a> &nbsp;·&nbsp;
  <a href="#quick-start">Quick start</a> &nbsp;·&nbsp;
  <a href="#architecture">Architecture</a> &nbsp;·&nbsp;
  <a href="START_HERE.md">Research programme</a> &nbsp;·&nbsp;
  <a href="docs/EVALUATION.md">Scientific evaluation</a>
</p>

<p align="center"><strong>Research POC</strong> &nbsp; / &nbsp; Local CPU &nbsp; / &nbsp; Windows first &nbsp; / &nbsp; Offline after installation &nbsp; / &nbsp; MIT code</p>

---

CuraLoop-RL explores a practical research question: **with a budget for 30 assays
in a library of 1,200 historical compounds, which candidates should be tested
first?** The workbench connects selection policies to delayed feedback, explicit
resource accounting and an inspectable public event ledger.

It includes a frozen MoleculeNet HIV replay dataset, clearly labelled synthetic
fixtures, five selection policies and independent matched comparisons. The
scientific engine runs in Python; the interface presents its actual state.

![Actual CuraLoop-RL Discovery Overview with historical assay data](docs/evidence/four-screen-dashboard-20261108-v1/01-overview-desktop-en.png)

*Captured from the running English application. This is a retrospective research
simulator; historical assay labels are distinct from simulated cost and timing.*

## The screening loop

![The auditable screening loop](docs/diagrams/screening-loop.png)

Accepted requests reserve budget once. Outcomes become visible only when their
configured simulated delay has elapsed. Only newly delivered active outcomes
count as hits; seed labels, pending predictions and missing outcomes are excluded.

The ledger makes decisions inspectable. SQLite preserves public snapshots and
revisions, while portable single-run JSON supports validated recovery elsewhere.

[Editable diagram](docs/diagrams/screening-loop.html) · [SVG](docs/diagrams/screening-loop.svg) · [Persistence and recovery](docs/PERSISTENCE.md)

## Inside the workbench

| Workspace | What you can do |
| --- | --- |
| **Discovery Overview** | Read actual compound, budget, delivered-assay and hit counts; inspect public chemistry and discovery curves. |
| **Digital Twin Simulation Lab** | Use the explicitly labeled Retrospective Simulator; inspect selection, queue, delivery and model-data stages. |
| **Benchmark Arena** | Compare Random, Greedy, active-learning and RL implementations; distinguish single-seed efficiency from recorded ten-seed variation and fallback. |
| **Compound Explorer** | Search a structure table or grid; inspect public descriptors, outcome visibility and selection history. |
| **Scenario builder** | Configure dataset, seed, policy, budget, capacity, delay, jitter and missingness. |
| **Research evidence** | Inspect provenance and limitations; export, resume and recover saved campaigns or revisions. |
| **Guided presentation** | Explain the screening loop in 5-7 minutes using the same live campaign. |
| **C Workspace** | Trace cached declared fields to their original sources, review readiness and export local files in EN/TH. |

## Research and R&D pilot programme

**Current direction: a method paper using existing datasets, with a useful R&D plugin.**
The [method design](docs/03_research/METHOD_FIRST_DESIGN_20261108.md) includes
an executable small predictive-scenario rollout reference and constructed checks.
Its [closest-work review](docs/02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md)
records strong prior-art overlap. The [LR-M12 M1 investigation](docs/03_research/LR_M12_M1_RESULTS_20261108.md)
executed a small exposed-data predictor adapter, 17 constructed checks and 36
planning timing calls. It ended **NO-GO for the method transition**; novelty and
molecular benefit remain unestablished. Conditional M2 was not run.

The owner approved the [M2 contribution direction](docs/03_research/M2_CONTRIBUTION_PROPOSAL_20261108.md):
learn when to reuse a predictor, update it or invoke nonmyopic planning. The
[detailed experiment plan](docs/06_execution/M2_EXPERIMENT_PLAN_20261108.md) proposes
six existing FS-Mol development pools, two predictors and eight matched arms,
with a fresh 48 CPU-hour / 96-hour grant. **Execution awaits owner approval**;
the failed M1 verdict, closed budgets and final-outcome protections remain intact.

The earlier baseline-relative rollout remains isolated historical research code.
The approved selective-computation direction is not yet implemented or evaluated,
and is not a production policy. Toy checks do not establish drug discovery,
real-world safety, speedup or publication readiness.

Read [GOAL](GOAL.md), [PLAN](PLAN.md), [START_HERE](START_HERE.md) and
[constructed evidence](docs/evidence/method-first-20261108-v1/README.md).
The [data inventory](docs/03_research/LOCAL_DATA_INVENTORY_20261107.md) remains
available. QP32/QC500 and benchmark-publication fallbacks are deferred. The LR-M12
release is closed after verified full return and exact remote cleanup; final
outcomes remain closed. See the [owner checkpoint](docs/06_execution/LR_M12_OWNER_CHECKPOINT_20261108.md)
before a new mechanism or phase.

The four-screen dashboard uses the [shadcn Dashboard](https://ui.shadcn.com/blocks/dashboard)
as a design reference, reusing the existing app and real Python engine. It supports
EN/TH, Graphite x Copper styling, public 2D chemistry and reduced motion. Read the
[frontend checkpoint](docs/05_product/FOUR_SCREEN_DASHBOARD_CHECKPOINT_20261108.md)
for actual checks and limits. The C Workspace exposes
cached declared metadata and local reports; live autonomous R&D efficacy,
external-team delivery and customer value are unvalidated.

[English manual](docs/manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf) ·
[Previous Molecular Studio walkthrough](docs/media/molecular-studio-walkthrough.mp4) ·
[C Workspace HTML](docs/05_product/metadata-workspace-v2/workspace.html) ·
[Core guide](docs/05_product/METADATA_PORTFOLIO_GUIDE_V1.md)

The [literature positioning review](docs/02_literature/POSITIONING_REVIEW_20261108.md)
and [current download status](docs/02_literature/LITERATURE_DOWNLOAD_STATUS_20261108.md)
separate papers actually inspected from 25 newly verified private reading copies.

Historical negative results remain visible: [Goal4](docs/03_research/GOAL4_RESULTS_V1.md)
found slower screening in its matched check, and [4R1](docs/03_research/GOAL4R1_RESULTS_V1.md)
did not establish incremental planner value beyond the stronger predictor.
Old final outcomes and all closed ledgers/source STOPs remain preserved.
The [working manuscript](docs/01_paper/MANUSCRIPT.md) is a design draft with
separately retained historical studies; no submission or acceptance is claimed.

## Quick start

**Windows:** install 64-bit Python 3.12, open the project folder and double-click
**`Start-CuraLoop-Web.cmd`**. First use creates `.venv` and installs the locked
dependencies; subsequent use runs from local assets. The bundled frontend needs
no Node.js installation.

Open **http://127.0.0.1:8000** and keep the launcher terminal open. Stop with Ctrl+C.
No administrator access, execution-policy change, API key or cloud account is
required. Python 3.11 is also supported by configuration; the executed Windows
verification used Python 3.12.10.

```powershell
# From the source folder:
.\Setup-CuraLoop-Web.cmd
.\Start-CuraLoop-Web.cmd
```

**Start with the illustrated guide:** [Download the English user manual](docs/manual/CuraLoop-RL-User-Manual-EN.pdf).
Its 20 pages include real program screenshots, linked contents, a worked campaign,
policy comparison, export/import, saved revisions and recovery instructions.

For platform commands and troubleshooting, see the [Windows operator guide](START_WINDOWS.md).
Linux/macOS can use the same locked Python dependencies and
`python scripts/start_web.py --no-browser` inside a virtual environment.
The English Streamlit fallback is available through `Start-CuraLoop.cmd` on port 8501.

## Architecture

![CuraLoop-RL architecture and public/private boundaries](docs/diagrams/architecture.png)

The React/TypeScript frontend calls a loopback FastAPI adapter. `RunService` and
the existing Python engine own selection, simulated time, accounting and export.
Built-in policies receive public observations in a separate process. Unrevealed
assay labels stay in the private backend.

SQLite stores public snapshots, revisions and comparison records. Restart
reconstructs accepted state through the existing reconciliation logic; unfinished
comparison jobs are marked interrupted and never silently repeated. Run one
active server with one Uvicorn worker.

[Architecture reference](docs/ARCHITECTURE.md) · [Editable diagram](docs/diagrams/architecture.html) · [SVG](docs/diagrams/architecture.svg)

## Scientific scope

| Evidence | Interpretation |
| --- | --- |
| Historical HIV replay | Genuine retrospective assay labels and structures; a custom 1,200-molecule derivative, not an official leaderboard reproduction. |
| Budget, delay, capacity and missingness | Explicit simulated operational assumptions, not measured laboratory costs or turnaround times. |
| Random, Greedy and Uncertainty | Implemented selection baselines; model probabilities are uncalibrated and uncertainty is a margin heuristic. |
| Q-learning and contextual bandit | Frozen controllers trained on synthetic tasks. Actual learned-request and fallback counts are exposed. |
| Recorded historical benchmark | Both learned controllers used **Greedy fallback for 300/300 requests each**. Matching Greedy does not establish learned RL transfer. |

The default seed may produce zero new hits. That result is retained. Recorded
benchmarks are labelled separately from newly executed comparisons. No dataset,
label semantics, trained checkpoint, reward or evaluation protocol was changed
for the interface, persistence or documentation work.

This independent personal project does not establish clinical efficacy, GMP
suitability, real laboratory savings or an operational Digital Twin. It is not
an official GPO system. See [evaluation and limitations](docs/EVALUATION.md) and
[dataset provenance](docs/RESEARCH_BENCHMARKS.md) for the full research boundary.

## Verification

Executed Windows verification includes **136 Python tests and 18 frontend
tests**, a production build, real desktop/mobile browser workflows, delayed
visibility, budget accounting, restart recovery, exports and validated resume.
The detailed reports distinguish current execution from preserved historical
evidence and list all unrun checks.

- [POC release verification](docs/RELEASE_VERIFICATION.md)
- [README, branding and manual verification](docs/README_MANUAL_VERIFICATION.md)
- [Current screenshots and capture records](docs/evidence/readme-manual-v1/)

## Development

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src app api scripts tests
.\.venv\Scripts\python.exe scripts\start_web.py --check
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Use a Node version compatible with `frontend/package.json` for frontend work.
Vite development uses port 5173; production serves the committed build at port
8000. Rebuild `frontend/dist` after UI changes and restart to refresh build
identity. Documentation tooling is optional and separate from application runtime.

## Documentation and attribution

| Resource | Purpose |
| --- | --- |
| [English user manual (PDF)](docs/manual/CuraLoop-RL-User-Manual-EN.pdf) | Illustrated operation, evidence and recovery. |
| [Windows operator guide](START_WINDOWS.md) | Installation, launchers, backup and troubleshooting. |
| [Persistence reference](docs/PERSISTENCE.md) | Storage schema, atomic actions, interruption and corruption recovery. |
| [Research benchmarks](docs/RESEARCH_BENCHMARKS.md) | Data preparation, source records and evaluation context. |
| [Change log](CHANGELOG.md) | Release changes. |
| [Engineering handoff](HANDOFF_TO_CODEX.md) | Verified checkpoints and continuation boundaries. |

Code is [MIT licensed](LICENSE). The HIV derivative has separate CC BY 4.0
attribution to NCI DTP, MoleculeNet, DeepChem and TDC. Fonts and software retain
their upstream notices. New brand artwork is AI-assisted; the original logo and
historical screenshots remain preserved. See [third-party notices](THIRD_PARTY_NOTICES.md)
and [brand provenance](docs/BRAND.md).
