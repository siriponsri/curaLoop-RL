# AgentRD continuation: one consolidated resource/model decision

Status: **PROPOSED_NEW_RESOURCE_ACCOUNT; NO MODEL INFERENCE STARTED**.
10 November 2026, Asia/Bangkok. Source main is
`3fa17f09fc90b89dc4cc98668d86afb17d81552d`, clean at intake. The owner now
authorizes A0 -> necessary A1/A2 -> evaluation -> analysis/manuscript continuously;
the attached pack's A0-only, mock-first and per-phase approval wording is
superseded. Old budgets stay closed. No manuscript submission is authorized.

## Verified runtime inventory

Read-only SSH succeeds as the existing `chaw` profile on dr-train. The machine
reports 72 logical CPUs and about 126 GiB physical RAM. Its host PATH lacks an
Ollama binary, but two existing container services respond to model-metadata
requests on loopback 11434/11435. Neither reported a loaded model at inspection.
Available models include:

| Model | Exact digest | Existing bytes |
| --- | --- | --- |
| `hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M` | `ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b` | 7,300,583,628 |
| `hf.co/unsloth/medgemma-27b-text-it-GGUF:Q4_K_M` | `5370d71cef17b08981562112095859458982cd3e3ffa4a254f956fdb076a1aa0` | 16,546,406,453 |

The 12B model is the proposed existing-resource choice. The 27B model is not
needed. These are inventory facts, not an inference-speed, tool-use or accuracy
PASS. Docker is already available to this account. Existing services and their
configuration are preserved. An isolated task-owned container would use the
existing image and model mount read-only, no GPU, no published port and no
privileged mode. Image identity, CPU/memory/swap enforcement and offline loading
must pass admission before any evaluation. No new model download is proposed.

Local inspection found no installed Ollama/llama.cpp service or language-model
weights in the ordinary Ollama, LM Studio and Hugging Face model locations.
No OpenRouter key was present in the current process environment; no key or
other project's credentials were read.

## Option A: existing dr-train model, zero API spend (recommended)

Fresh ceiling **96 CPU-hours / 120 elapsed hours**, max **4 combined CPU cores**:
local one CPU / aggregate 1 GiB for engineering; one isolated remote model job
up to three CPU equivalents / 12 GiB / swap0. Numerical/library threads are
bounded. GPU and paid APIs stay disabled. The clock starts on this resource
approval, never by reopening a closed account. Retain failed reservations and
record measured CPU separately. No new system permissions or global installs.

Bucket upper bounds: admission 2 CPUh, implementation/verification 12,
development/model feasibility 10, locked evaluation 56, analysis/manuscript 8,
return/cleanup/delivery 4, technical retry reserve 4. No silent borrowing.

Start with a bounded real-model format/latency calibration on development-only
inputs. Predeclare task scope and prompts before it; use only development
outcomes for at most two prompt revisions. Freeze all code/prompts/source pins,
gold/scoring and task IDs before locked evaluation. Do not switch to a bigger
model or an API if the local model fails. Keep failures and finish the software
and candid negative/incomplete experimental report within this account.

## Option B: OpenRouter plus dr-train engineering, faster remote inference

Fresh ceiling **16 CPU-hours / 72 elapsed hours**, max four CPU cores, same
local one / remote up to three engineering limits (remote 4 GiB / swap0).
Proposed fixed model `qwen/qwen3.5-flash-02-23`, one provider selected before
freeze, provider/model fallback disabled, explicit request/token/price caps.
Authorize **at most USD5 total API usage**, including development, failed calls,
repairs and evaluation. No automatic credit purchase or top-up. A dedicated
key must be supplied through the local environment, never in chat or Git.

The live catalogue and official model page checked at intake list input
USD0.065 / output USD0.26 per million tokens. Availability/pricing can change;
recheck and enforce the ceiling before calls. A conservative 8M input + 2M
output token allowance would be about USD1.04 at those listed token prices,
not a guaranteed bill. Set maximum 1,500 provider requests, disable paid
fallbacks and fail closed if actual usage/pricing cannot be accounted.
Only allowlisted public aggregate evidence and task questions may leave the
machine. No private rows, hidden gold, sealed outcomes, secrets or local paths
are sent. No third-party search/code-execution plugin is enabled.

Sources: [official model/pricing](https://openrouter.ai/qwen/qwen3.5-flash-02-23),
[provider pinning](https://openrouter.ai/docs/guides/routing/provider-selection).
Free routers are not the recommended primary experiment because endpoint/model
changes and rate limits complicate matched reproducibility. No OpenRouter
inference has occurred.

## Shared complete project scope

Deliver the localhost EN/TH workbench, bounded single-controller real-LLM
missions, typed tools, independent-from-generator deterministic claim checks,
durable receipts/recovery, truthful local dossiers, computational results,
failure/cost analysis, figures/tables, a complete English manuscript and a
publication-readiness assessment. Independent expert/user validation is not
claimed or required for this computational study.

Initial costed suite: **48 author-defined cases: 16 development + 32 locked**,
covering extraction, paired comparison/budget sweep, scope/uncertainty,
unsupported/forbidden requests, actual isolated-source integrity/availability
faults, and interruption/recovery. Counts are feasibility choices, not power
calculations or biological replication. Every locked case has three predeclared
decoding repetitions. No selection of a best repetition.

Controls: B0 strong deterministic pipeline; B1 same model with the evidence
snapshot supplied upfront and no tool execution; B2 same model and same typed
tools without the independent report gate; P guarded controller; A-VERIFY the
same controller without the claim gate in the isolated evaluation harness.
B2 vs P is primary; the rest are secondary. Match source information, task
specification, model/decoding settings, call/output ceilings and retry policy.
The verifier cannot inject evaluator gold or give P extra source facts.
Measure both raw model proposals and released outputs, fallback and abstention,
so a deterministic repair cannot masquerade as LLM reasoning success.

Primary: exact task success across all locked attempts; report paired effects
and uncertainty descriptively, with no minimum effect or significance threshold
invented from pilot results. Also measure unsupported claims/coverage, source
fidelity, appropriate refusal/over-refusal, blocked attempts versus actual leaks,
recovery, and all-attempt resource costs. Gold is independently calculated from
the admitted public CSV and source rules, outside the model runtime. Constructed
faults are labelled as such; all agent outputs must come from actual inference.

A2 is limited to five-budget comparison and pinned local literature/source
metadata necessary for these missions. No new molecular datasets, simulation
creation/advance, arbitrary browsing, external writes or wet-lab action. The
original final16, private CF1 rows, hidden outcomes, frozen results and ledgers
stay sealed and unchanged. Fourteen prior closed ledgers (the preceding thirteen
plus CF2P) are protected in the new account.

This single resource choice covers continuous gated work through the manuscript.
Technical/safety gates still apply; a negative comparison does not stop honest
analysis/manuscript. A privacy failure stops affected execution for repair, not
for access to protected data. No external researcher, customer or wet lab is a
prerequisite. Normal main commit/push remains covered by standing owner authority;
public application deployment and journal submission remain excluded.

During the pending choice, continue source/literature reconciliation, protocol,
schemas and additive implementation that requires no model call or costly run.
Do not describe an unrun model comparison as a result.
