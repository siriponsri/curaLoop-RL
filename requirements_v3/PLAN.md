# PLAN — Portfolio-first, evidence-driven

This plan is **goal-based, not calendar-based**. Build the smallest product a reviewer can really use before expanding algorithmic complexity.

## P0 — Personal repo and environment

**Deliver:** locally initialized Git repo under owner control, Python package, pinned dependencies, MIT or owner-chosen compatible code license, gitignore, Windows instructions, a fixture and basic CI/tests. Commit baseline. Avoid committing data with uncertain redistribution rights.

**Accept:** clean local install on CPU; one test suite succeeds; no paid APIs, GPU, GPO systems, cloud or credentials needed.

## P1 — Demonstrable interactive product (first GPO-appropriate showcase)

**Deliver:** Streamlit dashboard with four core pages/tabs: Overview, Scenario Setup, Screening Run, Compare & Export; accessible labels, clear research disclaimers, visible synthetic-data indicators; small deterministic replay and valid budget accounting; at least random, greedy and uncertainty policies. Save screenshot(s) only from an actual running UI.

**Accept:** user can complete the full 5–7 minute demo offline and export a report; UI and results agree; no broken buttons/placeholder charts; usable Windows commands.

## P2 — Reproducible pharmaceutical data benchmark

**Deliver:** official LIT-PCBA target loader after provenance/license review, RDKit validation, assay definition, source identifiers, deduplication, input fingerprinting, error messages and a controlled small-data demo; additional diversity and budget-aware baselines.

**Accept:** a documented real dataset can be acquired and replayed without oracle leakage; dashboard clearly distinguishes historical public assay results from synthetic scenarios; no public redistribution of restricted data.

## P3 — Adaptive decision policy, then RL

**Deliver:** contextual-bandit/meta-strategy controller choosing among valid acquisition strategies; fair comparison to the best tuned non-RL baselines. Add optional Gymnasium / PPO only if reproducible tests and a specific research hypothesis justify complexity.

**Accept:** same initial labels, assay budget, seed definitions, observation delay and predictor resources across methods; training/testing leakage guarded; `RL_TRAINED` only if actually trained. Show negative results honestly.

## P4 — Digital-twin-ready scenarios

**Deliver:** user-editable synthetic cost, batch size, turnaround time, noise, missingness and policy constraints; event timeline; prediction-versus-revealed outcomes dashboard; scenario cards and versioned manifest.

**Accept:** each scenario is explicitly labeled `SYNTHETIC_ASSUMPTION` unless grounded in an authorized measured reference. Still call the project a simulator, not a live twin. Document mismatch and limits.

## P5 — Portfolio finish and presentation

**Deliver:** clean bilingual README, annotated architecture diagram, substantive recorded/screenshotted demo from real app, 5–7 minute Thai presentation storyline, benchmark table with source flags, issue board, known limitations, release/tag and stable Codex handoff.

**Accept:** a third party can clone, run demo, understand value, reproduce a result and distinguish achieved results from hypotheses. Owner reviews repo visibility and licensing before public sharing.

## P6 — Optional later (not first showcase blockers)

- Real, authorized assay CSV import with strong schema validation; expert review and quality controls.
- Digital shadow/twin maturity assessment only with ongoing physical process data and independent prospective validation.
- Formal research paper, multi-target generalization, advanced RL, API + multiuser UI, external hosting.

## Work vs Codex

**GPT Work:** P0 + executable P1 with tests; leave exact commit and `HANDOFF_TO_CODEX.md` in repository; may do P2 if time and source terms allow.

**Codex:** complete P2, improve P1 QA, add P3/P4 based on evidence, then P5 release material. Avoid costly rewrites. Each merge should strengthen demonstrability or scientific trust.

## Owner decisions reserved

Public/private GitHub repository, publication or external data sharing, licensing where nontrivial, any internal GPO material/branding, paid APIs/GPU and claims about organizational adoption. Routine dependency choices, code refactors and offline benchmarks do not need separate approval.
