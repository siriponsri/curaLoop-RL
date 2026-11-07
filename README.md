<h1 align="center">Screening decisions you can audit.</h1>

<p align="center">
  A local research workbench for sequential pharmaceutical screening.<br>
  Choose candidates. Wait for feedback. Compare policies. Preserve the evidence.
</p>

<p align="center">
  <a href="docs/manual/CuraLoop-RL-Molecular-Studio-Manual-EN-v2.pdf"><strong>English user manual (PDF)</strong></a> &nbsp;·&nbsp;
  <a href="docs/media/molecular-studio-walkthrough.mp4">20-second walkthrough</a> &nbsp;·&nbsp;
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

![Actual CuraLoop-RL workbench with historical assay data](docs/evidence/ui-modern-bilingual-20261106-v1/browser-final-v7/01-overview-en.png)

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
| **Molecular Studio / Overview** | Inspect an eligible historical structure, page candidates, zoom and read the actual campaign record. |
| **Compound explorer** | Search, filter, sort and inspect public descriptors and genuine historical molecular structures. |
| **Scenario builder** | Configure dataset, seed, policy, budget, capacity, delay, jitter and missingness. |
| **Simulation lab** | Select batches, advance time, finish, replay or reset; inspect outcomes, explanations and the budget ledger. |
| **Benchmark arena** | Execute matched independent policies, inspect actual fallback usage and reopen saved comparisons. |
| **Research evidence** | Inspect provenance and limitations; export, resume and recover saved campaigns or revisions. |
| **Guided presentation** | Explain the screening loop in 5-7 minutes using the same live campaign. |
| **C Workspace** | Trace cached declared fields to their original sources, review readiness and export local files in EN/TH. |

## Research and R&D pilot programme

The **Molecular Studio frontend checkpoint is complete**. Both the screening application and C Workspace now offer EN/TH,
Graphite x Copper styling, responsive source inspection and reduced motion.

Latest research: [R0-DQ ChEMBL37 qualification](docs/03_research/R0DQ_QUALIFICATION_RESULTS_20261107.md)
found two candidates with panels of 128 compounds, both in one development
split unit. The proposed benchmark of 36 tasks in 18 groups and source/reference truth
remain unqualified; the readout is **PILOT_ONLY_REVISE**. These are private
research artifacts pending review, separate from the application's documented
replay datasets. The owner decides the next phase.
[Evidence](docs/evidence/chembl-taskfirst-dq-20261107-v1/README.md) ·
[Next decision](docs/06_execution/R0DQ_OWNER_DECISION_20261107.md)

[Checkpoint and limits](docs/06_execution/FRONTEND_CHECKPOINT_20261106.md) ·
[English manual,12pages](docs/manual/CuraLoop-RL-Molecular-Studio-Manual-EN-v2.pdf) ·
[Walkthrough](docs/media/molecular-studio-walkthrough.mp4) ·
[Acceptance evidence](docs/evidence/ui-modern-bilingual-20261106-v1/README.md)

![The source-linked C Workspace](docs/evidence/ui-modern-bilingual-20261106-v1/browser-final-v7/08-workspace-en.png)

The additive [C Workspace HTML](docs/05_product/metadata-workspace-v2/workspace.html)
opens from a local checkout or downloaded export. GitHub displays its source;
download/open it to use the interactive view. Field selection follows the
original source locator. Local export does not deliver to an external team tool.
The [frozen v1 core guide](docs/05_product/METADATA_PORTFOLIO_GUIDE_V1.md) remains
available; the new view preserves its report identity and original artifact bytes.

The [LR-BC core checkpoint](docs/06_execution/LRBC_CORE_CLOSEOUT_20261106.md)
delivers four typed metadata tools, cited readiness/gap reports, portable local
exports and a tested MCP stdio surface. Two ten-case C acceptance runs, four
native pipe checks and an eleven-response engineering client/server path passed.
[Core guide](docs/05_product/METADATA_PORTFOLIO_GUIDE_V1.md) ·
[C evidence](docs/evidence/lrbc-c-20261106-v1/README.md).

Research remains **NOT_READY**. Historical LR-BC R1 stopped on the third source request after
HTTP504; full molecular qualification and the pilot were NOT_RUN. The real-metadata
functional comparison tied12/12 versus12/12 using shared decision code, supporting
the [narrow product continuation](docs/06_execution/B_POTENTIAL_DECISION_LRBC_20261106.md)
without a superiority or live-agent claim. All B/C owned remote files returned
and were reread before exact cleanup. The pre-UI charge was9.5CPU-hours; the completed frontend continuation retains
18.75CPU-hours cumulatively, including every failed attempt and utility reserve. Final outcomes and all source STOPs remain preserved.

Earlier completed goal: [A3 population/observation qualification](docs/03_research/GOAL4R2A3_QUALIFICATION_V1.md).
Its original canary NO_GO, offline repair and
[verified closeout](docs/06_execution/GOAL4R2A3_CLOSEOUT_20261106.md) remain unchanged.

Earlier completed goal: [Goal 4R2-A2 readiness](docs/03_research/GOAL4R2A2_READINESS_V1.md)
retrieved descriptions for all 105 MF-PCBA AIDs, with version/revision metadata
matching the publication, and passed ten engineering contract checks on dr-train.
Historical activity equivalence and scientific cohort eligibility remain open.
The [MolDesignBench assessment](docs/03_research/GOAL4R2A2_BENCHMARK_COMPATIBILITY_V1.md)
finds an output mismatch with the current plan/report workflow and a
noncommercial dataset restriction. Full return and scoped remote cleanup are
[verified](docs/06_execution/GOAL4R2A2_CLOSEOUT_20261106.md). Scientific pilot
advancement remains NO_GO; live integration and benchmark evaluation remain unrun.

Earlier: [Goal 4R2-A](docs/03_research/GOAL4R2A_FEASIBILITY_AND_NEXT_STUDY_V1.md)
delivers an [offline evidence-to-plan/report prototype](docs/05_product/OFFLINE_RD_WORKFLOW_V1.md)
with 20 passing engineering checks. MF-PCBA publication metadata now covers
60 stage pairs and 105 AID version tuples. Scientific cohort eligibility and a
novel method remain unestablished. The [verified closeout](docs/06_execution/GOAL4R2A_CLOSEOUT_20261106.md)
and [proposed dataset/benchmark expansion](docs/06_execution/GOAL4R2A_EXPANSION_PROPOSAL_20261106.md)
separate completed work from the next decision. Live agent/MCP/team integration
has not been evaluated.

Earlier: [Goal 4R1 results](docs/03_research/GOAL4R1_RESULTS_V1.md) separate
predictor gains from planning gains. The direct Tanimoto GP improves familiar-
condition Greedy discovery on the development panel; incremental planning value
remains unestablished. The bounded challenge and verified remote cleanup are
[complete](docs/06_execution/GOAL4R1_CLOSEOUT_20261105.md). Final outcomes stay reserved.

The reviewed [predictor/decision-value proposal](docs/03_research/GOAL4R_METHOD_PREDICTOR_PROPOSAL_V1.md)
led to the completed 4R1 diagnosis above. An
[agentic R&D plugin](docs/04_business/AGENTIC_RD_PLUGIN_PROPOSAL_V1.md)
for live paper/database search and team delivery remains proposed; its offline
subset is described above. The
[related-work review](docs/02_literature/REDESIGN_DEEP_REVIEW_20261105.md)
records prior art and open questions. Live plugin integration and broader
method benefits remain unvalidated.

Earlier: [Plan A, Goals 3–4](docs/06_execution/PLAN_A_CLOSEOUT_20261105.md)
completed a paper-backed FS-Mol cohort and a frozen development/validation challenge.
The candidate screening method was slower in matched timing checks; broader
discovery benefit remains unestablished. Read the [results and limits](docs/03_research/GOAL4_RESULTS_V1.md).
Final outcomes remain reserved for a later decision.

Earlier: [Goal 2 real-data planning challenge](docs/03_research/GOAL_02_RESULTS_V1.md)
completed **180 Tox21 development runs on dr-train**. The new bound preserved
rollout decisions but increased policy computation; nearest-hit found more
assay actives on this panel. This is an implemented prototype with a retained
negative result, not an established new method. See the
[paper-backed dataset and FS-Mol download record](docs/03_research/GOAL_02_DATASET_ACQUISITION_V1.md).

Reviewed v2 adds a [master plan](ACADEMIC_BUSINESS_MASTERPLAN.md),
[literature review](docs/02_literature/CRITICAL_REVIEW.md),
[proposed study protocol](docs/03_research/PROTOCOL.md) and
[R&D pilot offer](docs/04_business/PILOT_OFFER.md).
The research asks when pending work, capacity and a simulated deadline change
delivered-hit discovery. Multi-target performance, controller transfer and
customer value require new evidence; the current HIV pilot remains historical.

Read [START_HERE](START_HERE.md) for the document order and
[the documentation map](docs/README.md) for the complete programme.
The versioned research reference remains separate from the application engine;
new research configuration files are not inputs to the existing UI or CLI.

The local [NCATS development pilot](docs/03_research/NCATS_DEVELOPMENT_RESULTS_V1.md)
now records **108 completed runs** across AhR, PPAR-gamma and p53, with six fixed
controls and three seeds. Pending-penalty selection added no deadline hits in
this bounded pilot and lost two hits in one paired run. These are correlated
development endpoints, not untouched final tests or therapeutic-efficacy evidence.

A [fresh-environment reproduction](docs/03_research/NCATS_REPRODUCTION_V1.md)
matched all 108 scientific traces. A separate frozen
[54-run Gaussian comparator](docs/03_research/NCATS_GAUSSIAN_RESULTS_V1.md)
also found no extra deadline hits from pending conditioning in this allocation.

The latest [candidate audit](docs/03_research/CANDIDATE_ASSAY_AUDIT_V1.md) and
[design sensitivity report](docs/03_research/DESIGN_SENSITIVITY_V1.md) prepare a
broader 12+ family estimation study. They retain metadata/feature audits,
failures and hypothetical uncertainty/resource scenarios. Final task rights,
endpoint mappings and roles remain open; no final compound outcomes were read.

The English [working manuscript](docs/01_paper/MANUSCRIPT.md) now includes the
measured development evidence. A source-checked
[journal shortlist](docs/01_paper/JOURNAL_TARGETS_20261104.md) and
[submission review package](docs/01_paper/submission/README.md) respect the
owner's US$300 publication-fee limit. The manuscript is awaiting author,
scientific and venue review; no journal submission or acceptance is claimed.

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
