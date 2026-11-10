# Source checking, task completion and cost in a local pharmaceutical evidence agent

Manuscript core written while the locked experiment is running. This file
contains the introduction, methods and interpretive limits, not empirical
results or a publication-readiness verdict. The final manuscript must insert
the audited locked analysis and retain unfavorable or incomplete outcomes.

## Author

Siripon Srihangpiboon

King Mongkut's Institute of Technology Ladkrabang

Correspondence: srihangpiboon.siri@gmail.com

ORCID: 0009-0001-0611-5568

Affiliation and contact details were supplied by the owner. Funding, competing
interests and final author approval require the author's confirmation before
submission; no declaration is inferred from the software's resource ledger.

## Introduction

Language-model agents can place computational chemistry tools behind a natural
language interface. ChemCrow integrates chemistry tools and reports expert
assessment; Coscientist coordinates computational tools and laboratory
automation [1,2]. These systems establish tool-mediated chemical workflows as
prior work. Paper2Agent further turns research outputs into executable agents,
including validation and repair of exposed tools [3]. A wrapper, a validation
loop or a provenance record is therefore insufficient to establish a new
scientific method.

Reliability also depends on what is measured. ChemAgent's comparative study
shows that tool augmentation need not outperform the underlying language model
across chemistry tasks [4]. ScienceAgentBench separates execution from
scientific task completion [5]. In a structured evidence application, an answer
may contain only source-correct numbers yet omit requested quantities, omit
essential limitations or answer a request that should have been refused. A
numerical source check cannot by itself establish that the user's task has
been completed.

We study that distinction in CuraLoop-RL, a local pharmaceutical research
workbench. The evaluated agent reads previously released retrospective
confirmation-selection aggregates, performs bounded calculations and releases
typed claims or abstentions. The research question is whether a deterministic
source gate with bounded corrective generation improves released task
correctness relative to an otherwise matched model with the same tools, and
what refusal, coverage, failure and computational cost accompany the difference.
The contribution is an inspectable implementation and a controlled application
case study. It is neither a new RL selector nor a claim of general autonomous
scientific discovery. The case collection is an evaluation instrument for this
software, not a proposed standalone benchmark publication.

## Methods

### Study scope and provenance

The study uses four already released public CF1 aggregate files. Their full
paths, byte lengths and SHA-256 identities are pinned in the protocol release.
The principal CSV contains 2,700 historical portfolio cells: six development
campaigns, five historical seeds, six rankers, three portfolio operators and
five confirmation budgets. The upstream source is the processed AIC_Finder
repository at commit `04c58e85188e724ec5ff44cbed2e7b960f6f3df3`, associated
with the published MVS-A study [6]. Our prior CF1 reconstruction and its source
concordance qualifications remain unchanged. This is not a new reproduction
of the original raw assays or every result in that article.

H denotes historical confirmed-positive observations; D denotes positive fixed
structure groups; B denotes confirmation observations. HB and DB are fractions
per confirmation, not laboratory expenditure or monetary efficiency. Missing
confirmation remains excluded. The nonpositive class mixes inactive and
inconclusive observations. The six campaigns share one annotation-connected
component; the five historical seeds are conditional repetitions. At the
studied budgets, round-robin D=H is a mechanical property. Neither groups nor
seeds supply independent biological replicates.

No final16 record, private CF1 compound row, molecular structure or hidden or
pending assay outcome is accessible through the evaluated tools. Earlier
datasets, ledger bytes, frozen results and negative findings are preserved.
Source-fault cases operate on isolated copies of the admitted public files,
without modifying the historical originals. No new molecular fit, laboratory
experiment or user study is part of this work.

### Workbench and agent controller

The workbench adds a bilingual EN/TH mission page and API to the existing
localhost React/FastAPI application. EN/TH describes interface and dossier
localization; the locked questions are English, so no comparative Thai-language
agent-performance result is claimed. A closed mission specification selects a
campaign, ordered methods and budgets. It cannot supply arbitrary paths,
providers, code or external write actions. A trusted controller authenticates
and reads the source packet before generation. This preflight read is not a
tool autonomously selected by the language model. The model can request one
fixed calculation adapter while useful, then answer or abstain in a typed JSON
interface. The tools cannot change the screening simulator or write to a team
or laboratory service.

A separate verifier compares released numeric claims with authenticated source
values and permitted derivations. It checks source identity and declared
limitations but does not decide whether a natural language request has been
fully answered. Actual requests are durably recorded before inference. Mission
state, tool receipts, proposals, repair feedback, failures and costs are retained
in an atomic revisioned store. An explicitly requested local dossier contains
EN/TH HTML reports, structured values, the trace and a file-hash manifest.
Application-level immutability prevents silent replacement through the normal
workflow; it is not an external signature or trusted timestamp.

### Matched controls

B0 is a strong deterministic reference: the complete authenticated table,
permitted exact derivations, all true scope codes and a capability refusal
filter. It uses no language model. B1 receives the same public observations
directly but has no executable calculation action. B2 uses the same model,
information, typed actions, state persistence and read/compute adapters as P;
its terminal proposal is checked for logging without gating or scientific
correction feedback. P adds the deterministic source gate and bounded targeted
repair. A-NOREPAIR retains the gate but stops after its first invalid terminal
proposal on eight fixed anchor cases.

B2 and P have byte-identical initial observations, instructions, model
settings, action schema and decoding seed. A correction contains error codes
against the same observations, not gold answers or additional facts. A common
malformed-JSON recovery rule applies across model arms. Every model arm has at
most three calls and 256 generated tokens per call; tool-enabled arms have at
most two tool receipts, including the trusted preflight read. The last call
must terminate. Exhaustion is retained as deterministic abstention fallback,
not automatically scored as successful research.

The primary B2/P comparison isolates the implemented gate and its associated
repair under this shared controller. It does not identify the separate causal
effect of each internal component. B1's common tool-oriented instruction and
terminal-only action interface constrain its secondary comparison. These
controls are not native reproductions of ChemCrow, Coscientist or Paper2Agent.

### Cases, development and freeze

There are 16 development and 32 locked author-created interface cards. Locked
families contain six extraction, six comparison, six interpretation, six
boundary, four source-fault and four recovery tasks. Interpretation is scored
through explicit limitation codes, not open-ended narrative quality.
Source-fault cases delete or alter actual public-copy files. Recovery introduces
a declared controller exception immediately after a real model response has
been durably recorded and then resumes that exact call. It does not simulate
every property of a real machine crash or network outage.

Each locked card crosses B0/B1/B2/P and decoding seeds 17011, 17023 and 17033,
giving 384 units. Eight preselected anchors also cross A-NOREPAIR and the same
seeds, giving 24 additional units. The total is 408 planned units, including
312 real-model missions. The fixed schedule randomizes system order within
case/seed blocks using Python seed 20261110. Historical CF1 seeds are distinct
from these decoding seeds.

Two unsuccessful development canaries and two common prompt/interface repairs
preceded freeze. The third canary completed a source-correct answer. A separate
six-mission development probe retained a refusal failure: the model returned
permitted aggregate values instead of abstaining. No protected data was read.
The protocol did not tune that failure away. B0 had already passed all 32
authored cards in pre-freeze engineering conformance, a disclosed known ceiling
rather than a blind discovery. The card author also knew the exposed source
values. Locked means no outcome-guided changes after freeze; it does not mean
externally authored, biologically held-out or independently validated tasks.

The protocol, cards, schedule, oracle, scorer, production prompts/controller
and model transport were frozen through 27 SHA-256 pins, with freeze identity
`5b70e5f1454e9062441b3e292a50fab45f9aebe73ed7994971c6a88de2ad4c8e`.
The exact bytes were committed and pushed as `064bd3d` before the first locked
model call. Documentation, figures and descriptive reporting tools may be added
later without changing those scientific pins. Every planned unit, attempt,
partial failure, fallback and unattempted resource-limited unit is retained.

### Model and computational environment

The existing Typhoon 2.1 Gemma3 12B GGUF model runs through Ollama 0.12.6 on
dr-train. Its historical local tag is
`hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M`; the pinned digest is
`ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b`.
Q4_K_M is recorded from the tag; the runtime's parsed quantization field was
unknown. The original upstream URL now redirects to the Typhoon namespace [7];
that metadata check is not evidence of a newly downloaded binary identity.

Temperature is 0.2, context length 4,096, model threads three and GPU layers
zero. The owned container has no network or published ports, uses a read-only
existing model cache and enforces a three-core CPU quota on cores 69/70/71.
Its memory limit is 11.5 GiB with no swap; the host-control allowance is
0.5 GiB. Completed calls check zero GPU VRAM. Local orchestration and document
helpers share one one-core/1 GiB Windows Job, keeping the combined maximum at
four CPU cores. No paid inference, new model download or shared-service
configuration change occurs.

The fresh overall authorization is 96 CPU-hours and 120 elapsed hours, starting
10 November 2026 at 11:10 UTC and ending 15 November 2026 at 11:10 UTC.
The locked remote phase has a 201,600 CPU-second ceiling. The original clock
and per-stage caps are not reset. Before each unit, the controller requires
3,000 CPU seconds and 15 minutes of deadline headroom; an in-cgroup watchdog
also enforces the hard limit. Reservations, observed model CPU, local-controller
CPU and unknown failed-call cost are reported separately. Costs depend on this
hardware, execution order and prompt caching, and do not measure laboratory
savings, energy use or user productivity.

### Oracle, scoring and analysis

An author-written oracle reads the pinned CSV directly using code separate
from the production adapter and source verifier. It averages campaigns within
each historical seed, then the five seed values. Ratios are averaged as ratios.
Source operands are rounded to three decimals before deltas; comparisons use
absolute tolerance 0.0005000001. Gold quantities and required-key/scope lists
are never provided to the model or remote container. A separate implementation
is a useful conformance check, not independent expert adjudication.

Task success requires the expected terminal action, every requested numeric
key and required scope code, correct source identity for answers and no released
wrong or unsupported numeric claim. Abstention cases require an accepted empty-
claim refusal. Extra correct permitted values are allowed equally for all arms.
A source-check PASS, process exit or executable response alone is insufficient.
We retain raw and released numeric error rates, malformed responses, required-
field coverage, source citations, appropriate abstention, overrefusal, fallback,
execution failure, recovery and observed calls/tokens/CPU/wall time. A numeric
error rate with no numeric claims is NA. Unknown failed-call cost is not zero.

The primary estimand is P minus B2 task success in percentage points, averaging
the three decoding seeds within each of 32 cards, then weighting cards equally.
All-planned and attempted-unit denominators are both shown. If the full matrix
is incomplete, the primary comparison is inconclusive; a partial favorable
table does not establish superiority. When complete, an exploratory paired
case bootstrap uses 10,000 draws, seed 20261110 and sorted positions 250 and
9,750, one-based. The interval is conditional on the authored cases, corpus
and one model, not a biological or real-user population confidence interval.
There is no primary p-value, new significance threshold or post-hoc success
gate. Seed differences and the eight matched ablation anchors are descriptive.

## Interpretive limits

The study can measure fidelity to a narrow, machine-checkable evidence contract.
It cannot establish unrestricted scientific reasoning, hypothesis quality,
prospective compound discovery or the value of a general research assistant.
Typed questions and a complete deterministic table may favor B0. Its known
pre-freeze conformance ceiling is a substantive limit on the need for an LLM
in these tasks, not a reason to weaken that reference.

The short output and call caps are part of the tested system. Truncation,
malformed output, repeated computation and fallback must remain visible beside
numerical error. A numerical verifier may prevent wrong claims yet fail to
detect a missing requested field, missing interpretation code or inappropriate
answer. Withholding all claims would not constitute useful performance; task
success, coverage and overrefusal must therefore be read together.

All arms lack a private-data adapter. Zero observed protected-data leakage is
a common architectural boundary, not evidence that P has superior refusal or
security. A request-contract failure involving only permitted aggregates must
not be relabeled as an actual leak. The controlled recovery probe does not
validate arbitrary outage recovery or adversarial security.

The case author, software developer and evaluator are part of one solo project.
Component tests, visual review, the separate CSV oracle and manuscript checks
are author self-checks. No independent expert, researcher, customer, usability
or wet-lab validation is claimed or required to complete this computational
report. A retrospective application case may still be worth reporting, but its
scope and novelty must be judged against its actual evidence rather than a
promised discovery benefit.

## Reproducibility and availability

The final package must include the frozen protocol/cards/oracle/schedule,
public input identities, immutable actual unit receipts and traces, all planned
dispositions, audited analysis, standalone figure sources and an English
operator guide. The code and reports are in the public CuraLoop-RL repository.
Private reading-room papers and original private compound data are excluded.
Existing model weights are not redistributed. Code's MIT license does not
license weights or underlying datasets, and no general commercial-use clearance
is claimed.

The localhost acceptance record includes an actual UI-to-API-to-model mission,
an explicit five-file dossier export, server restart without regeneration and
EN/TH/mobile self-checks. Recorded results and deterministic mode remain
available after the bounded research worker is removed. A later live-model
session requires a fresh authorized operator configuration; the closed research
ledger must never be reopened. There is no production deployment, live team
connector, always-on inference promise or manuscript submission.

## References

1. Bran AM et al. Augmenting large language models with chemistry tools.
   Nature Machine Intelligence 6, 525-535 (2024).
   https://doi.org/10.1038/s42256-024-00832-8
2. Boiko DA, MacKnight R, Kline B, Gomes G. Autonomous chemical research with
   large language models. Nature 624, 570-578 (2023).
   https://doi.org/10.1038/s41586-023-06792-0
3. Reimagining research papers as interactive and reliable AI agents.
   Nature (2026). https://doi.org/10.1038/s41586-026-11044-y
4. Yu B et al. Tooling or Not Tooling? The Impact of Tools on Language Agents
   for Chemistry Problem Solving. Findings of NAACL 2025, 7635-7655.
   https://doi.org/10.18653/v1/2025.findings-naacl.424
5. ScienceAgentBench: Toward Rigorous Assessment of Language Agents for
   Data-Driven Scientific Discovery. ICLR (2025).
   https://proceedings.iclr.cc/paper_files/paper/2025/hash/f12b4df26344f3be803c06b555252efe-Abstract-Conference.html
6. Boldini et al. Machine Learning Assisted Hit Prioritization for High
   Throughput Screening in Drug Discovery. ACS Central Science 10, 823-832
   (2024). https://doi.org/10.1021/acscentsci.3c01517
7. Typhoon 2.1 Gemma3 12B GGUF model card.
   https://huggingface.co/typhoon-ai/typhoon2.1-gemma3-12b-gguf

Primary-source read depths and access limitations are recorded in
`docs/08_agent_rd/A0_CLOSEST_WORK_20261110.md`. References are not a systematic
review, and the implementations here do not reproduce the referenced agents.

## Writing-assistance disclosure for the final author to review

The project used an AI coding/research assistant to develop software, inspect
sources, prepare figures and draft this manuscript. The empirical agent outputs
are separately identified Typhoon model calls and are not replaced by text
generated by the coding assistant. The human author remains responsible for
the final content and declarations. No completed human verification, signature
or submission is asserted by this draft disclosure.
