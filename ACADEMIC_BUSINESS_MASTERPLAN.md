# CuraLoop-RL: academic and business master plan

> **Current planning override, 8 November 2026:** use the [method-first design](docs/03_research/METHOD_FIRST_DESIGN_20261108.md). The older question/roadmap below is historical. Preserve frozen
> scientific evidence and safeguards; it does not release QP/QC, a benchmark-
> publication fallback, new data/compute or final outcomes.

**Prepared:** 4 November 2026, Asia/Bangkok. **Source checkpoint:** `2d287a170b39b0c07d02631ca027c2ba535c0df9`. **Owner choices:** public-data-first computational research; R&D-team pilot as the initial business route; solo starting point; English active repository documentation.

## 1. The outcome to pursue

Build a reproducible study of molecular screening decisions under operational constraints, then test whether the resulting workflow solves a problem for R&D teams. The research and business programmes share code and provenance but require different evidence. A paper needs a question, credible comparisons and supported conclusions. A sale needs a buyer, an agreed deliverable and a commercial commitment. Neither follows automatically from a polished application.

The existing POC is a useful base. It has a real local interface, private delayed outcomes, explicit budget accounting, independent comparisons and recoverable evidence. It currently supports a frozen historical HIV task and synthetic fixtures. It uses Logistic Regression and fixed acquisition strategies, plus frozen synthetic-trained tabular controllers. There is no LLM-driven scientific workflow in the application.

## 2. What the evidence currently supports

The preserved pilot contains 50 campaigns: five policies across ten paired seeds. With 48 preexisting labels and 30 new assays, recorded mean new active hits were 0.7 for Random, 3.8 for Greedy and 0.9 for Uncertainty. Both learned controllers also scored 3.8 while invoking Greedy fallback for all 300 requests each. The separate scaffold-disjoint predictor audit recorded AUROC 0.5563 and AP 0.03266. These are exploratory historical results on one custom subset.

The documentation release does not change those results or execute a new scientific study. It prepares the research and commercial next steps, preserves code/resources/evidence and provides a working manuscript that states exactly what is known. Prior Windows/Python/frontend/browser reports remain dated software evidence. Current package checks are reported separately.

## 3. A defensible paper question

Ask: **When does accounting for pending experiments improve delivered hit discovery under a fixed simulated deadline and limited assay capacity?** This question has a measurable endpoint and a plausible operational mechanism. It can yield useful positive, negative or regime-dependent findings.

Broad novelty is already occupied. Model-guided molecular screening, learned acquisition, asynchronous Bayesian optimization and modular scientific workflows all have prior art. The review compares MolPAL, GLARE, ALF, PAL, BoTorch, BayBE, SimDMTA and foundational delayed-feedback methods. The contribution must be a specific controlled result and reusable evaluation, with any learned-controller benefit established empirically.

A timing feature is not enough by itself. Equal costs and a common delay without a deadline may leave the selected compounds unchanged. The development pilot must first test that invariance and demonstrate a small heterogeneous-duration case where available information and capacity create a real decision tradeoff. This resolves whether the simulator can answer the intended question.

## 4. The scientific design

Use public assay tasks with clear active/inactive semantics and inspected structure identities. Existing HIV remains the regression fixture. LIT-PCBA and TDC HTS are candidate sources; no new task collection is installed by this package. Audit source versions, file-level use terms, invalid structures, duplicates, conflicting labels, analog overlap and endpoint compatibility before freezing the registry.

Separate controller-development, validation and final-test tasks at the target/family level. Keep campaign initialization separate from an independent predictor audit. Use uniform seed selection and retain one-class initial sets. A repeated seed is not a new biological target. If only a narrow task population is feasible, state that boundary instead of using more seeds to imply generality.

Compare policies under the same pool, initial labels, predictor and operational realization. Include Random, retrained and frozen-model Greedy, nearest-delivered-hit similarity, diversity, meaningful uncertainty, a simple exploration mixture and an asynchronous method matched to multi-hit retrieval. Choose the strong fixed policy on development data. A numerical backend can be reused when it preserves the policy information boundary. A new controller is an optional additional method, not a prerequisite for a useful benchmark.

The primary endpoint is new historical active labels delivered by deadline T. Secondary endpoints include the area under the discovery-time curve, discovery against accepted expenditure, active scaffold coverage, failure/fallback share and compute cost. Missingness mechanisms, cancellations and completion exactly at T need explicit definitions. Pending commitments remain visible at the deadline even when their results arrive later.

Use paired task-level effects and uncertainty that respects independent families/tasks and repeated seeds. Estimate pilot variance and runtime before choosing final repeats and a material-effect threshold. Freeze the final design before seeing final-test outcomes. Keep all valid seeds, failures, unfavorable conditions and protocol amendments. Do not tune the final test toward an RL success story.

## 5. A practical sequence for a solo investigator

First preserve the current application and evidence, then implement the smallest data/scheduler/baseline slice. Validate hidden-label privacy, event order and accounting on enumerated toy cases. Next execute 3-5 development tasks under a small operational grid. Use that pilot to discover defects, assess endpoint scarcity and measure compute.

Only then decide whether a learned controller has a sensible state/action/reward design and a feasible training population. If it always falls back or chooses the same actions, diagnose that before scaling. If a fixed policy remains competitive, preserve the result. Expand to the frozen multi-target study only when the scientific question is identifiable and its comparisons are fair.

The proposed larger grid and resource formulas are planning examples. They are not completed experiments or approved paid compute. Start CPU-first and ask for a specific resource decision only when measured runtime shows why it is needed.

## 6. Paper structure and release

`docs/01_paper/` follows the manuscript sequence: title/abstract, introduction, related work, implemented methods, proposed study, historical results, discussion, limitations, conclusion and declarations. `MANUSCRIPT.md` assembles the chapter content for review. The critical literature review, 28-source register, extraction matrix, evidence notes and BibTeX are under `docs/02_literature/`.

New study outcomes remain NOT_RUN. Complete final figures, supplements and a fresh-environment reproduction after experiments. Confirm author spelling, affiliation, contact, funding, conflicts and AI assistance before submission. No DOI, ORCID, customer or affiliation is invented. Choose the venue after the contribution is clear; Journal of Cheminformatics and SoftwareX are scope candidates, while JOSS has current public-history and demonstrated-use requirements that make it a longer-term option for a new project.

Version 2 contains 28 identified main-source PDFs plus one R05 supplement: 29 reading copies and 731 physical PDF pages. R03, R05 and R26 were supplied by the owner after the first release. R05 is ChemRxiv v3, not a verified reading of its associated journal version. Reading copies are outside the public repository payload. That separation lets the owner access requested papers without blindly publishing third-party PDFs with the project. The public register preserves canonical links, versions and checksums.

## 7. The first commercial offer

The initial offer is an **R&D screening-planning pilot**: install locally, map permitted historical data, fix a replay protocol, compare strategies and deliver an auditable report plus operator handover. The buyer evaluates decision relevance and reproducibility. Actual assay savings or improved biological outcomes require their own evidence.

The first target user is a scientist or informatics lead with a real batch-selection problem. The buyer is the person able to fund a scoped evaluation. These roles and the problem frequency are hypotheses until discovery confirms them. Start with a public-data demo so the conversation does not depend on receiving proprietary libraries.

The MIT code remains public. Possible paid work includes installation, adapters, analysis, training and support. An exclusive software-license proposition is not assumed. A recurring plan becomes reasonable only when the customer has repeated work and a continuing support need. Assess whether an integration with an established optimizer is a better solution than expanding an independent platform.

## 8. Business experiments and economics

Ask about a recent actual campaign: how the next batch was chosen, which results were pending, what tools were used, who approved experiments and what made the decision difficult. Separate observed behavior from enthusiasm about AI. Seek a real next commitment, not a compliment. Customer contact is an external action and was not performed here.

The pilot offer defines inputs, deliverables and acceptance. The draft statement of work identifies scope, data ownership, outputs, support and exit conditions that a customer agreement must settle. Customer-specific records remain outside public Git. No customer names, organizational logos or testimonials are included.

Illustrative unit economics show why delivery effort matters. The example base case assumes a USD 3,000 fee, 40 delivery hours at USD 50/hour, USD 75 infrastructure and USD 250 support/other allowance. Contribution is USD 675, or 22.5%, before overhead and tax. The stress case is loss-making. These figures are internal hypotheses, not a quote, market price or revenue forecast.

Measure analyst effort, installation/reproduction success, decisions changed, repeated use and actual commercial commitments in pilots. Treat simulated assay reductions as scenario results. Do not multiply hypothetical extra hits by the speculative value of a successful drug. Market sizing remains bottom-up until account counts, buying rates and prices are sourced.

## 9. Product boundary and data handling

The existing release is a single-owner local workbench. New multi-task ingestion, deadline scheduling, asynchronous policies and customer adapters are specifications. Public hosting, multi-user identity, instrument integration and regulated use require additional design and evidence. A local origin check is not an enterprise security system.

For a customer-data pilot define permitted fields, access, processing location, backup, exports and retention. Structures and event logs may be confidential. Do not send them to external model APIs without permission. Code, dependencies, datasets, papers and customer outputs have distinct rights; citation alone does not resolve every reuse question.

## 10. Repository application and ownership

Use the existing clone whose `.git` and origin point to `siriponsri/curaLoop-RL`. Apply the documentation overlay only after checking owner changes and the base checkpoint. The supplied Python apply helper backs up affected files, checks the expected base and copies the listed changes. It never deletes the clone, rewrites history, commits or pushes.

Review the diff and use a normal main commit/push when ready. Do not force-push or copy the entire enclosing reading-room package into Git. The complete source payload is provided for convenience, while the smaller overlay is the preferred update path. If the remote has advanced, integrate the documents against the newer source instead of overwriting new runtime work.

## 11. Milestone acceptance

| Milestone | Evidence needed |
| --- | --- |
| Research question locked | Nearest-work comparison, endpoint and protocol |
| Data trustworthy | Versioned sources, terms, identity/analog audit and task roles |
| Simulator suitable | Enumeration, invariance and heterogeneous-duration checks |
| Baselines credible | Matched predictors/information/resources and public action traces |
| Study complete | All final runs, failures, task-level uncertainty and ablations |
| Paper reviewable | Reproducible figures, precise claims, supplements and declarations |
| Pilot credible | Buyer problem, feasible data, agreed acceptance and measured effort |
| Business repeatable | Actual continued use/commitment and sustainable delivery economics |

## 12. The next concrete action

Apply and review the documentation package, then give Codex `prompts/CODEX_RESEARCH_BUSINESS.md` in the verified existing checkout. Its first task is ENG-01 through ENG-05: protect the baseline and establish whether the proposed operational tradeoff is testable. Continue toward evidence, not a predetermined model ranking or an inflated sales claim.

## Full-text review decisions — version 2

The additional review changes the design in four places. First, LIT-PCBA's target ascertainment, source release and phenotype mapping become explicit data gates. Second, the primary uniform start keeps zero-active runs, while a known-hit sensitivity acknowledges the different regime used in R05. Third, no-retrain and similarity controls, exact enrichment definitions and predictor-update timing become mandatory reporting. Fourth, BayBE's documented backtesting/asynchronous capabilities favor a local integration feasibility study and a narrower service proposition.

Read [the full-text amendment](docs/02_literature/FULL_TEXT_REVIEW_ADDENDUM.md), [version questions](docs/02_literature/VERSION_DISCREPANCIES.md), [metric concordance](docs/02_literature/METRIC_AND_INITIALIZATION_CONCORDANCE.md) and [baseline specification](docs/03_research/BASELINE_SPECIFICATION.md). VDR's conflicting description and the preprint's MI direction are unresolved data/code questions; they are recorded without guessing corrections. New-study results, controller transfer, real savings, customers and payments remain unvalidated. Existing application and historical evidence bytes remain unchanged.
