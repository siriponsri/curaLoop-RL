# AgentRD solo project: final owner report

Prepared 11 November 2026. This report closes the computational and localhost
delivery scope authorized on 10 November, including an unfavorable result.
It does not claim a validated commercial product or a competitive journal paper.
Final account settlement and main-delivery identities are separate receipts in
the [evidence directory](../evidence/agent-rd-20261110-v1/README.md).

## Delivered outcome

| Workstream | Actual outcome | Evidence |
| --- | --- | --- |
| A0 reconciliation and research design | Reused the existing repository and admitted aggregates; froze tasks, sources, prompts, scoring, controls and model before locked calls | [Source/reuse](A0_SOURCE_AND_REUSE_20261110.md), [protocol](COMPUTATIONAL_PROTOCOL_V1.md), [freeze](../evidence/agent-rd-20261110-v1/protocol-freeze-v1.json) |
| Necessary A1/A2 product | Working EN/TH Mission Control, durable actual model/tool events, deterministic comparisons and five-budget sweep, source checks, explicit abstentions and local dossier export | [57 backend and 32 frontend checks plus served acceptance](../evidence/agent-rd-20261110-v1/product-scope-checks-v1.json) |
| Real computational evaluation | All 408 frozen units completed, including 312 actual model missions and 436 provider responses; no replacement trials | [Analysis](../evidence/agent-rd-20261110-v1/analysis-v1/analysis.json), [all dispositions](../evidence/agent-rd-20261110-v1/locked-progress-v1.json) |
| Reproduction | Read-only replay agrees with frozen scoring/analysis; all 96 initial B2/P inputs match; same-machine fresh-output figure reproduction passes | [Score replay](../evidence/agent-rd-20261110-v1/reproducibility-replay-v1.json), [figure reproduction](../evidence/agent-rd-20261110-v1/offline-figure-reproduction-v2.json), [instructions](REPRODUCIBILITY_V1.md) |
| Manuscript and operator documentation | Full English computational report, seven tables, three figures; eight-page English screenshot guide; every final PDF page visually inspected | [Manuscript PDF](../07_publication/CuraLoop-AgentRD-Computational-Report-EN-v2.pdf), [editable text](../07_publication/CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V2.md), [guide PDF](../manual/CuraLoop-AgentRD-Guide-EN-v2.pdf) |
| Remote stewardship | Returned and reread all 477 owned files, matched actual provider receipts, then removed only the owned container/root/archive; fresh absence check passed | [Complete return](../evidence/agent-rd-20261110-v1/complete-remote-return-v1.json), [cleanup](../evidence/agent-rd-20261110-v1/owned-remote-cleanup-v1.json), [absence](../evidence/agent-rd-20261110-v1/fresh-remote-absence-v1.json) |

The handoff's A0-only, mock-first and separate phase-approval instructions were
superseded by the owner's continuous solo instruction. The original handoff
remains unchanged. Its later simulator-writing mission, live source expansion,
external team delivery and separate Thai review were not prerequisites of the
released read-only implementation. They were not silently treated as completed.

## Research question and controls

The falsifiable question was whether source-checked release and bounded repair
improve task completion over the same LLM and tools without that gate. The
comparison used one existing Typhoon 2.1 Gemma3 12B Q4_K_M model, CPU-only, the
same typed source packet and fixed caps. B2 and P had identical initial messages,
schema, seeds, tool access and output allowance; only the studied gating/repair
condition differed. B1 had no executable tools. B0 was a strong deterministic
reference, not an intentionally weak baseline.

The 32 locked cards are author-created interface tasks using already exposed
CF1 public aggregates, with three within-card decoding seeds. Sixteen separate
development cards supported implementation. These are not 32 independent
biological tasks, an unseen external scientific benchmark or an independent
expert assessment. The deterministic reference's 32/32 pre-freeze conformance
ceiling was known and disclosed. An author-written direct-CSV oracle was kept
separate from the production verifier; it is not independent human validation.

## Actual results

| Condition | Successful tasks | Success rate | Actual model calls | Recorded tokens | Known model CPU-hours |
| --- | ---: | ---: | ---: | ---: | ---: |
| B0: deterministic | 96/96 | 100.0% | 0 | 0 | 0.000 |
| B1: LLM-only | 60/96 | 62.5% | 118 | 95,447 | 10.753 |
| B2: LLM + tools | 67/96 | 69.8% | 144 | 126,726 | 12.764 |
| P: guarded agent | 67/96 | 69.8% | 144 | 126,726 | 13.222 |
| A-NOREPAIR: fixed eight-anchor subset only | 24/24 | 100.0% | 30 | 23,040 | 2.159 |

The primary P minus B2 effect was **0.00 percentage points**, with conditional
exploratory case-bootstrap interval **[0.00, 0.00]**. Every paired case-average
difference was zero, and all 96 seed/card B2/P output sequences were identical.
This degenerate interval describes this observed task set. It does not prove
equivalence on external tasks or that verification is generally useless.
The matched P anchor subset was also 24/24 with 30 calls; the ablation is not a
full-matrix result or evidence that removing repair improves performance.

The unchanged-verifier trace audit found **zero invalid terminal proposals in
both B2 and P (0/78 each)**. The numerical/source repair branch therefore had
no naturally occurring invalid proposal to repair in P. This is a limitation
of identifying that mechanism's benefit, not evidence of broad gate efficacy.
The same audit found 15 invalid B1 terminal proposals among 85, including 27
wrong numerical fields and three missing development-scope codes.
See the [mechanism audit](../evidence/agent-rd-20261110-v1/mechanism-audit-v1.json).

Correct numbers did not ensure task success. P and B2 each had 0/206 released
numeric errors, but 19/66 overrefusals and 18 deterministic abstention fallbacks.
P still failed 13 of 78 tasks whose released source check was valid. B1 had
27/178 numeric errors. Malformed responses were 33/118 for B1 and 48/144 for
both B2 and P. Output lengths and stop reasons are retained; matching cap-hit
and malformed counts do not establish that the cap caused those failures.

The 436 successful research provider responses recorded 371,939 tokens and
38.898 known model CPU-hours. All 312 planned model missions received actual
provider responses. This is model cost for the locked matrix, not total project
CPU. There were no locked provider/execution failures, but earlier development
failures and controller interruptions are retained separately. No paid API was
used. Latency comparisons are descriptive on fixed execution order and cached
CPU inference, not a causal efficiency or laboratory cost-saving estimate.

## Product acceptance and current use

Run `Start-CuraLoop-Web.cmd` and open `http://127.0.0.1:8000/agent`.
Use the existing [Windows instructions](../../START_WINDOWS.md). Opening the
page does not start model computation or create a simulator campaign.

Three reproducible demonstrations remain usable without a model worker:

1. **Open recorded model example** explicitly imports the genuine original
   two-call model mission, preserving its timestamp, sources, response and
   costs. It is labeled recorded evidence, never new inference.
2. **Deterministic mode** performs actual admitted-aggregate comparisons and
   a five-budget sweep. Served acceptance checked 129 source-derived values
   against the separate direct-CSV oracle.
3. A designated unsupported request produces a persisted **controller
   abstention**, zero model calls and an exportable local dossier in EN/TH.

Current served checks covered desktop/mobile layouts, bilingual labels,
immutable five-file exports, actual API restart without regeneration, empty
legacy simulator-run state and no external browser requests/page errors.
They are developer self-checks, not a representative user or security study.
The scope preflight recognizes designated cases; it is not a general intent
classifier. Actual data protection comes from the closed source/tool boundary.

The current service was also exercised with the real model before cleanup.
Mission `98661213-dcd5-4f9d-830e-4ce6b5629dc4` made three actual calls and two
tool calls, recorded 3,605 tokens and 2,354.363377 model CPU seconds, and survived
restart without regeneration. Its technical lifecycle passed, **but the
permitted comparison task failed: terminal state ABSTAINED**. This failure is
retained [with its actual receipt](../evidence/agent-rd-20261110-v1/product-current-model-acceptance-v1.json)
and was not replaced by another favorable trial. The earlier successful model
example and this later failed task are both visible.

The newer API policy/replay service is outside the frozen P research condition.
Its controller denials cannot replace the frozen model failures or support a
new comparative research claim. Historical screening/Confirmation/C Workspace
interfaces remain available; the agent does not order assays or mutate them.

The research model worker is deliberately retired after full return. Model
mode is not an always-on service. Fresh inference requires a newly authorized
operator session and transport namespace/setup; setting a session environment
variable alone is insufficient. Do not recreate the deleted research root or
reopen this account. Offline deterministic use and recorded evidence need no
such session. This is a bounded localhost prototype, not a general autonomous
pharmaceutical research product.

## Integrity, failures and resources

Fourteen old ledger identities, 66 old scientific pins and 27 new frozen
scientific pins are protected by exact hash checks. Older NO_GO/inconclusive
studies, unsuccessful model canaries, the refusal failure, interrupted controller
logs and unsuccessful first-edition visual reviews remain intact. New editions
fix figure label association, headings and table layout without changing scores
or coordinates. Final16, private CF1 rows and hidden outcomes were not opened.

One controller stopped after 52 units on a pre-unit SSH banner error. Another
controller disappeared after 197 units, with an unknown cause and a stale
resource record. Both failed reservations remain charged. An already completed
response was reconciled by exact request ID, without regeneration. That one
unit's wall measurement covers only its final controller segment; its original
model CPU/tokens remain intact. The recovery suite is a controlled persisted
response interruption, not universal machine-crash recovery validation.

The original allowance was 96 CPU-hours / 120 elapsed hours, at most four CPU
cores combined; no GPU or new model download. T0 was 10 November 11:10 UTC and
the unchanged deadline was 15 November 11:10 UTC. Model/test jobs have bounded
resource receipts. All remote code/data/evidence returned before exact owned
cleanup; reused model caches and other services were preserved.

The final retained allocation is recorded in `account-closure-v1.json` and
`settled-account-identity-v1.json`. Reservations include failures and unused
allowance; they are not measured usage and were not refunded or reset.
Interactive administrative/authoring CPU was not separately metered. An
additional 1,800-second control allowance was retained within the original
technical bucket; this is not measured consumption or retroactive hard-cap
enforcement. No precise total-project measured CPU claim is made.

## Manuscript and publication assessment

The delivered English report contains actual methods, matched controls,
results, conditional uncertainty, costs, failure analysis, limitations,
reproduction instructions and references. All 11 final pages and eight guide
pages were inspected after rendering. Color/grayscale figures and their final
paper insertions were checked. These are author reviews only.

**Assessment: complete computational negative/inconclusive report; not yet
established as a competitive JCAMD original-method submission.** The observed
gate adds no task advantage, its invalid-candidate repair branch was not
exercised, the deterministic ceiling was known, and one exposed aggregate
corpus/model with typed authored tasks does not establish a distinct molecular
design advance. A software/reproducibility contribution is possible to assess,
but code release alone is not an acceptance claim. The solo project is not held
open waiting for a wet lab, customer or external expert.

The [publication scope/fee notes](PUBLICATION_SCOPE_AND_MODEL_NOTES_20261110.md)
record official publisher checks dated 10 November: JCAMD's subscription route
had no APC and can fit the owner's US$300 ceiling; the listed open-access option
exceeded it. Financial fit does not establish scientific fit. No journal was
contacted and no manuscript was submitted. Future submission requires current
venue checks and the owner's approval, not automatic use of this report.

## Work not run and remaining owner decisions

**NOT_RUN:** another model or paid provider, new molecular training, final16
evaluation, private compound recommendations, live paper/database intake,
team/lab tool writes, public deployment, multi-user production qualification,
independent expert validation, real-user/business evaluation, a systematic
literature review/second Thai manuscript, and journal submission. These do not
masquerade as passed goals in this delivery.

The owner can now review the report and choose whether to archive the negative
study, assess a suitable software/report venue, or propose a separate study with
tasks that genuinely exercise invalid proposals and semantic completeness.
No such study starts automatically. Before any submission, confirm funding,
conflicts of interest, author contribution/AI-assistance text, author approval
and current venue requirements. The supplied author identity is included;
unconfirmed declarations have not been invented or signed.

No additional download, model, paid service or permission is needed to inspect
this completed package. Further live model operation or broader product scope
requires a separate owner decision and fresh resource setup.
