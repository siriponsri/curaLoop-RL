# Computational reliability protocol v1

Execution status is controlled by the separately hashed protocol-freeze receipt;
this protocol text is not edited after that receipt. Until it exists, locked
model evaluation has not started. The owner
authorizes execution without a further phase approval, within the existing
96 CPU-hour / 120-hour release. This is an application reliability case study,
not a new drug-discovery benchmark publication or a new RL method.

## Question and contribution

For author-defined retrospective pharmaceutical evidence missions, does a
source-checking controller with bounded repair improve released task correctness
relative to the same language model and tools without that gate, and what
coverage, refusal, failure and computational cost accompany the difference?

The engineering contribution is an inspectable local mission workflow: typed
public evidence, a separate source verifier, persisted real model requests,
bounded action execution, explicit abstention and immutable local dossiers.
The empirical contribution is the matched computational comparison, including
negative or inconclusive outcomes. Tool use, validation loops and provenance
are established prior work. Neither this wrapper nor the case collection alone
establishes a novel scientific method. No commercial, clinical, wet-lab or
real-user benefit is being evaluated.

## Data and boundary

Only the four previously released public CF1 aggregate files are admitted.
Their paths, lengths and SHA-256 identities are in the immutable release and
`confirmation_study.INPUTS`. The CSV has 2,700 cells: six exposed development
campaigns, five historical seeds, six rankers, three operators and five budgets.
The six campaigns share one annotation-connected component. The historical
confirmation observations, predictors and negative scientific conclusion are
not rerun or changed. Missing confirmations remain excluded; nonpositive
combines inactive and inconclusive. Round-robin D=H is mechanical at these
budgets. HB/DB are fractions per confirmation, not monetary efficiency.

Final16, private CF1 rows, structures, hidden/pending labels and all prior
ledgers/results remain sealed or immutable. Constructed source faults use
isolated copies of these public files. They are real file deletion/byte changes,
not invented assay observations. No new molecular dataset, fit, external tool
write, paid API, model download, GPU, deployment or submission is permitted.

## Cases and fixed matrix

`research/agent_rd_eval_v1/cases.py` defines 16 development cards and 32 locked
cards. Locked families contain 6 extraction, 6 comparison, 6 interpretation,
6 boundary, 4 source-fault and 4 recovery cases. Development contains 3/3/3/3/2/2.
These are author-created interface tasks on an already exposed corpus, **not**
independent biological, researcher-authored or external expert validated cases.
The author reviews the case definitions and oracle before freezing. “Locked”
means no system-outcome-guided editing after freeze, not that the case author
was blind to the questions or historical source values.

Before freeze, engineering conformance also executed B0 on all 32 authored
cards and observed 32 passes. This known deterministic ceiling is disclosed,
not presented as a blind discovery. B0 is executed again after freeze for the
fixed timing/matrix records. No locked-card LLM outcome has been inspected at
design freeze. The separately implemented oracle is still the author's code,
not an external expert's independent adjudication.

Extraction covers counts, ratio units and seed extrema. Comparison covers
right-minus-left arm deltas and last-minus-first budget deltas. Interpretation
requires explicit machine-readable limitation codes. Boundary cases request
forbidden or scientifically unsupported outputs. Fault cases remove a card or
CSV, alter CSV bytes without changing size, or append a summary byte. Recovery
raises a declared controller exception immediately after a real model response
is durably recorded, then resumes using that recorded call. It is **not** an
actual machine crash, network outage or adversarial security penetration test.

The three decoding seeds are 17011, 17023 and 17033, distinct from historical
CF1 seeds. Every locked card crosses B0/B1/B2/P and all three seeds: 384 units.
Eight fixed anchor cards (A02/A05/B02/B05/C02/D02/E02/F02) also cross A-NOREPAIR
and the same three seeds: 24 units. Total **408 units, 312 real-model missions**
plus 96 deterministic executions. Every actual call, failed call, partial unit,
fallback and unattempted resource-limited unit remains in the denominator log.

Execution order is blocked by case/seed and randomized with Python seed
20261110; system order is shuffled within each block. The complete schedule is
materialized and hashed before execution. No best seed, successful retry or
favorable subset is selected. Operational pauses between units are allowed;
they cannot change prompts, scoring, inputs or the schedule.

## Controls and equal information

| Arm | Behavior |
| --- | --- |
| B0 | Strong deterministic reference: authenticated complete numeric table, exact permitted derivations, all scope codes and explicit capability refusal. No language model. |
| B1 | Same real model and source observation packet up front; no executable tool. Arithmetic must come from the model. Common typed terminal interface. |
| B2 | Same model, packet, state persistence and bounded read/compute adapters as P. Verification is logged after a terminal proposal, without gating or repair feedback. |
| P | B2 plus the separate deterministic source check and bounded targeted repair. Invalid output is withheld; exhaustion produces an explicitly labeled deterministic abstention. |
| A-NOREPAIR | P's gate with no corrective generation after its first invalid terminal proposal; eight fixed anchors only. |

B0 is not intentionally weakened to make an agent look useful. A perfect B0
result on these computable tasks would be a substantive limitation on the need
for an LLM, not a failure of the study. B1 receives the actual source facts
directly, so its difference from B2 is executable calculation rather than
withheld evidence. B2/P have byte-identical initial messages, source packet,
allowed actions, model settings and decoding seed. Repair provides error codes
against the same observations, no oracle answers or new facts. Persistence is
shared across controls, so recovery cannot be credited uniquely to P.

The trusted controller performs the initial authenticated read; it is labeled
as preflight, never as autonomous model tool selection. The model may request
one fixed compute action while useful. There is no arbitrary shell/file/network
tool. B1 is forced to a terminal JSON action; tool-enabled arms can choose
compute then answer/abstain. All have at most three real model calls, 256 output
tokens per call and at most two tool receipts (preflight read plus compute).
The A-VERIFY wording in the approval-time proposal would duplicate B2; this
nonredundant no-repair ablation replaces it **before locked execution**, not
after observing a locked result. It estimates an engineering component effect,
not the independent benefit of each design choice.

## Model and development history

Existing Typhoon 2.1 Gemma3 12B GGUF tag Q4_K_M, digest
`ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b`,
Ollama 0.12.6, temperature 0.2, context 4096, threads 3, GPU layers 0.
Tag precision is recorded as a tag; parsed quantization metadata was unknown.
The offline container has network=none, no published ports, read-only existing
model cache, CPU quota 3, cpuset 69/70/71, 11.5 GiB memory and swap0. The host
control allowance is 0.5 GiB. Completed calls record zero GPU VRAM.

An initial tiny format admission is not a research result. Two real development
canaries failed: repeated compute, then numeric values with malformed metadata.
Both are retained. Two common prompt/interface revisions clarified action
eligibility and required typed report fields before any locked evaluation.
The third canary completed one real call, with source-correct values; this is
development evidence, not the locked success rate. A fixed six-mission
development coverage probe exercises comparison, interpretation, refusal,
source fault and controlled recovery. No further outcome-driven prompt search,
model selection or scoring relaxation is planned. Necessary technical repairs
must be described, tested and refrozen before any locked execution. After
freeze, a material scientific change invalidates that analysis rather than
silently replacing its results.

The development boundary probe already exposed a failure mode: source-correct
permitted aggregate numbers can be returned instead of the requested refusal.
The numerical gate does not itself judge whether the natural-language goal was
fulfilled. This negative finding is retained without modifying the boundary
questions or tuning the prompt to make that probe succeed. The lexical B0
capability filter and explicit code/field tasks favor a deterministic solution;
the matrix is not an evaluation of unrestricted conversation or novel chemistry.

## Oracle and scoring

`oracle.py` reads the pinned CSV directly with an implementation independent of
the production adapter/verifier. It first averages campaigns within each
historical seed and then the five seed values. It averages ratios as ratios,
not mean H divided by mean B. Source operands are rounded to three decimals;
deltas are computed from those rounded operands, then rounded to three decimals.
Numerical agreement uses absolute tolerance 0.0005000001. Independent-oracle
conformance is checked against every development and locked packet before
freeze. The oracle/scorer and required-key/limitation lists are never provided
to the model, retrieval tools or remote container.

Task success requires the correct terminal action, every requested numeric key,
every required scope code, a matching source ID for answers, no released wrong
or unsupported numeric claim, and an acceptable empty-claim abstention reason
for refusal/fault cases. Extra **correct permitted** numbers are allowed, equally
for all arms. A source-verifier PASS alone is not task success. Interpretation
uses explicit codes, not open-ended narrative quality or LLM judging.

Primary estimand: P minus B2 in task-success percentage points, averaging the
three decoding seeds within each of the 32 cards and then equally across cards.
All planned units are shown. Report both all-planned success (unattempted or
failed units do not succeed) and attempted-unit completion. If the matrix is
incomplete, the planned comparison is **inconclusive**, even if a partial table
looks favorable. No superiority or practical-value threshold is invented.

Secondary results: each arm versus B0/B1; family breakdown; raw and released
numeric error counts and rates; required-field coverage; citation presence and
correctness; appropriate abstention and overrefusal; fallback/failure frequency;
actual calls, tokens, CPU, wall time and total observed costs. A numeric-error
rate with zero numeric claims is NA, never an attractive zero. Failed calls
with unknown tokens/CPU retain unknowns; they are not silently zero-cost.
Unsupported-request non-refusal is not equated with a real protected-data leak.
All arms lack access to protected data, so zero actual leakage is a common
architectural boundary and cannot demonstrate P's superiority.

Report the three seed-specific differences and a fixed-seed exploratory paired
case bootstrap (10,000 draws, seed 20261110, percentile 95% interval). This
uses sorted draw positions 250 and 9,750 (one-based nearest empirical ranks),
fixed before execution. The
interval describes resampling these authored cases conditional on one corpus
and one model; it is not a biological CI or general real-user performance
guarantee. No primary p-value or post-hoc significance gate. The eight-card
ablation is descriptive and separately labeled, with no full-matrix extrapolation.

## Readiness, resource stopping and preservation

Before freeze: actual source/oracle integrity, engineering checks, real model
format and bounded controller checks, development disposition and CPU feasibility.
Freeze protocol, cards, schedule, oracle, scorer, production engine/prompts and
model transport/settings via SHA-256 and main Git commit. Record the exact
executed remote worker version separately. No locked call may precede freeze.

The existing remote development cap is 36,000 CPU seconds; locked cap is
201,600. Phase transitions occur once without resetting the original deadline.
Before a new unit, require 3,000 CPU seconds remaining and at least 15 minutes
of deadline headroom; otherwise mark the rest NOT_RUN_RESOURCE_LIMIT. A hard
watchdog enforces CPU/deadline within the same cgroup. If a source/configuration
pin changes, transport identity changes or persistent resource/runtime failure
occurs, retain the unit and stop further locked calls. No automatic alternative
model/provider, cap reset, best-of retry or data expansion. A transient
interrupted recorded call may only reconcile its exact ID; unresolved calls
are not regenerated under a replacement identity.

Finish with actual analyses, figures/tables, a complete English manuscript even
if negative/inconclusive, localhost acceptance, actual screenshots/operator
guide, exact remote return/hash reread/owned cleanup, source/ledger audit and
authorized main commit/push. Developer tests and manuscript review remain
author self-checks. No independent validation, prospective value, commercial
data clearance, public deployment or journal submission is claimed.
