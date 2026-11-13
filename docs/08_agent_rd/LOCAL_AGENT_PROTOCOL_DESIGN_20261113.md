# Local scientific agent: protocol design before feasibility

Status: **SCOPE ADOPTED; NEW NUMERICAL BUDGET PENDING; NOT FROZEN**.
This is an implementation and evaluation design, not an experiment result.
The owner adopted option A of the proposal review. The separate resource
question concerns the amount of the new budget, not another phase approval.
Deadline remains 20 November 2026, 11:51:07 UTC / 18:51:07 Bangkok.

## Research question and intended contribution

Does explicit binding of each public task requirement to evidence from the
current output artifact improve native scientific-task success over an agent
with the same checklist, observations, model, tools and execution limits?

The proposed intervention stores requirement ID, artifact path and digest,
validator identity/version, result and dependency identities. Editing an output
invalidates evidence bound to its previous digest. Completion cannot reuse
that obsolete check. Unknown evidence remains unknown. A targeted repair may
use public validation diagnostics within the same generation budget.

This is a testable candidate mechanism, not an established novel method.
Generic provenance, state persistence and byte integrity are prior art.
[ContractBench, section 2 and appendix A](https://arxiv.org/html/2605.17281v2)
already formalizes temporal validity and byte integrity and discusses
handle-based mitigation. The distinction to test is requirement-level
completion over edited scientific outputs, with equally informed controls.
This source check does not establish that all prior equivalent methods have
been excluded. StateM's detailed methods remain to be retrieved: its HTML
body did not render in the current source check.

## Product acceptance, independent of a positive research effect

Reuse the existing workbench. Add an isolated package rather than modifying
the frozen AgentRD engine or its scientific outputs. Start with one workflow:

1. Accept a bounded table of compound IDs and SMILES. Preserve the original
   input identity. Return explicit rejection reasons for invalid or missing
   structures; do not silently drop rows or invent replacements.
2. Calculate actual RDKit descriptors and apply an explicit, recorded filter.
   Preserve IDs, units, parameter values and accepted/rejected counts.
3. Export the selected table, readable report and checksummed manifest linking
   inputs, tools, versions, parameters and outputs.

Use at most three necessary adapters. Separate model/provider, tool execution,
job persistence and artifact storage. Expose submit/status/cancel/collect and
actual native process IDs where applicable. Recover persisted terminal jobs
without silently rerunning inference. Test cancellation and interrupted-state
recovery, recording which guarantees are actually supported. Do not claim
exactly-once execution from persistence alone.

Real-model runs and their failures are required for agent evidence. A
deterministic tool run demonstrates its adapter only. Test doubles may support
unit tests but never count as experimental model outputs or product model
acceptance. Preserve the existing offline/replay features and EN/TH interface.

## Arms and equal-information controls

| Arm | Role | Controlled difference |
| --- | --- | --- |
| D | Deterministic reference where the workflow has an applicable fixed implementation | Report capability scope; do not invent a universal solver |
| L | LLM-only secondary control | Initial task and public inputs; no interactive execution feedback |
| B1 | LLM plus tools and strong self-debugging | Same runtime and public tool observations as P |
| B2 | Checklist primary control | Same obligations, validation observations, model and limits; agent manages checklist without automatic version-bound invalidation |
| P | Proposed mechanism | Automatic requirement-to-current-artifact binding and invalidation |
| A1 | Mechanism ablation | Same binding machinery with automatic invalidation disabled |

P minus B2 is the sole primary contrast. L and B1 are contextual controls;
A1 tests attribution. Never describe the tool-free contrast as equal tool
access. The checklist must see public checks also used by P. All model-based
compilation, planning and repair count within each arm's total call/token/time
allowance. Count public validation and mechanism overhead, including cache hits
and failures. No hidden extra generation or deterministic answer substitution.

## Data and evaluator admission

Reuse the retained verified ScienceAgentBench archive and pinned annotations.
Do not download a substitute benchmark or publish unzipped source data. The
official README allows native execution independently of the paper's example
OpenAI/Bedrock engines; actual local compatibility still requires testing.
[Official access and evaluation instructions](https://github.com/OSU-NLP-Group/ScienceAgentBench/blob/main/README.md).

Before opening task bodies, inventory roles, licenses, dependencies and source
lineage. Exclude paid/image-model judges, live services, wet-lab actions,
unbounded training and resources outside the approved execution envelope.
Map the reported BBBC002 exposure before fixing locked roles. Structural
metadata identifies instance 11 as BBBC002_cell_count_eval.py; connected data
and publication lineage remain unresolved. Public availability is not proof
of absence from model pretraining or previous assistant context.

Separate agent-visible public input/program workspaces from scorer/gold mounts
and processes. Candidate execution has no network, shared caches, credentials
or access to other projects or protected CuraLoop outcomes. Reference/scorer
qualification belongs to an isolated evaluator; no gold-derived expected
answers or private evaluator feedback enters prompts, requirement compilation
or repair. Do not modify native scientific scoring to accommodate the method.

## Bounded feasibility and one-time freeze

Subject to numerical resource confirmation, the feasibility subceiling remains
4 CPU-hours, 1 allocated GPU-hour and 96 development provider calls, all charged
to the new total. First inspect hardware availability without evicting other
jobs. Select exactly one of the already authorized checkpoints by availability,
license, memory and timing, before comparative performance evaluation; record
the checkpoint digest. No model search or performance-based replacement.

Qualify the native scorer, correct/incorrect artifact handling, workspace
isolation and realistic local execution. Use development material only for
format, runtime and mechanism checks. Separate constructed stale-artifact
tests from naturally arising mistakes. Absence of a natural repair opportunity
limits interpretation; it must not be repaired by injecting primary errors.

Size the task/seed matrix from eligible independent source groups and measured
runtime with a 25% contingency, within all stage and total caps. Record the
deterministic sizing rule, actual eligible counts, group assignments, task order
and all exclusions before locked execution. Do not size or select locked tasks
using candidate success. If no adequate independent groups/native scorer fit,
use the approved bounded feasibility/software fallback, not a replacement study.

Freeze the numerical matrix, all prompts/requirements, primary model, decoding,
tools, validator versions, per-attempt caps, retry policy, success definition,
analysis code and source identities before the first locked generation.
No locked scoring feedback returns to a repair loop. Do not resume evaluation
under changed code or silently refill failed slots.

## Outcomes, interpretation and delivery

Primary endpoint is native task success, paired by task/seed, with seeds kept
inside tasks and source-publication groups kept together. Prespecify the exact
cluster-resampling rule and uncertainty interval at freeze. If too few groups
support credible interval estimation, report descriptive effects and label the
limitation; repeated seeds are not independent publications.

Report completion, abstention, task failure, false certification, stale evidence
use, natural repair opportunities, coverage and all-attempt tokens, CPU,
allocated GPU and wall time. Keep injected robustness findings separate.
Undefined success-cost ratios remain undefined. A lower false-completion rate
alone does not establish useful performance if coverage collapses.

Complete delivery does not require a positive effect. A method benefit needs
the prespecified primary evidence and mechanism audit; otherwise deliver a
negative/inconclusive computational report. Software readiness and publication
readiness are separate decisions. No expert, user, clinical, business, cloud
or multi-user validation is implied by author checks or localhost execution.

Deliver actual localhost acceptance evidence, reproducible code/data access
instructions, every attempt and resource receipt, analysis tables/figures,
English manual and manuscript, limitations and an honest venue assessment.
Return and hash-reread owned remote artifacts before exact owned cleanup.
Keep shared models/services untouched. Commit/push main; do not submit a paper,
deploy publicly or write to team tools. Protected final16/private CF1/hidden
outcomes and frozen prior scientific sources remain untouched.
