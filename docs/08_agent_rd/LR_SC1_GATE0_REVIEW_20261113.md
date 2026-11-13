# LR-SC1 Gate 0: question, closest work and comparator commitment

Decision: **PASS for bounded data/evaluator admission**, not proof of novelty,
method effectiveness or journal readiness. Review date: 13 November 2026.
No model inference, remote job or test-outcome inspection occurred in this gate.
The original proposal remains byte-identical; this is its authorized gate record.

## Search boundary

Primary-source review covered scientific executable checks, specification
generation, scientific-agent validity and generated-test agents. Queries included
`scientific metamorphic LLM SciCode tests validation`, `SciCode contracts agent
tests scientific`, `scientific test generation metamorphic LLM 2026`,
`CodeMetaAgent metamorphic specifications scientific code`, and
`CodeSpecBench behavioral specification generation scientific`.
Web search snippets were discovery leads only. The decisions below use author
papers or source repositories. This is a targeted review, not a systematic review.

## Closest evidence and limits

| Primary source | What is already covered | Consequence for LR-SC1 |
| --- | --- | --- |
| [Rules to Tools, 2610.00313v1](https://arxiv.org/html/2610.00313), sections 3-4 and appendices C-D | Scientific numerical checks, matched SciCode repair, independent final grading, task-level uncertainty and cost. Its checks are authored/reviewed and qualified by the study team; the contrast supplies prepared implementations rather than automatically discovering checks inside each trajectory. | This is the closest work. Do not claim first scientific-check agent or first matched SciCode check evaluation. Test end-to-end automatic construction without per-test-task human check writing, including its construction cost and mistakes. Retain native sequential generation rather than selected archived failures. |
| [AgentCoder, 2312.13010v3](https://arxiv.org/html/2312.13010), section 3 | Separate programmer/test-designer roles, execution feedback and revision. | B2 must be a real generated-test baseline with a separate design context. AgentCoder-inspired budget adaptation, not a claim to reproduce its original reported scores. |
| [CodeMetaAgent, 2511.18249v1](https://arxiv.org/html/2511.18249), sections 3 and 5 | Specification mutation and metamorphic tests. Test-expansion experiments start from oracle suites. | B2 may generate metamorphic/scientific tests; it is not restricted to weak examples. No native oracle suites may enter either LR-SC1 generation arm. Full mutation/ensemble exploration is a different intervention and is not represented as reproduced. |
| [Teaching Code LLMs to Reason with Intermediate Formal Specifications, 2607.04232v1](https://arxiv.org/html/2607.04232), section III | Executable assertions trained using validated reference executions and behavior-changing mutants. | No novelty claim for executable assertions. LR-SC1 uses fixed base models and public specifications without such test-task reference supervision; no trained-model superiority claim. |
| [CodeSpecBench, 2604.12268](https://arxiv.org/abs/2604.12268) | Execution-based correctness and completeness of behavioral specifications. | Passing a model's own checks is not correctness. Native final grading and false-validation rates are essential. |
| [Structure Before Intelligence, 2610.19507](https://arxiv.org/html/2610.19507) | Scientific release structure, version lineage, validation, containment and recovery. | Existing hashes/release controls are shared infrastructure, not the LR-SC1 contribution. |
| [SciValidityBench, 2610.34767](https://arxiv.org/html/2610.34767), appendix I | Scientific validity and compiled governing state; learned ingestion remains an extension. | No first scientific-validity/compiler claim. This study grades executed generated code, not memory-policy answers. |
| [AgentSpec, 2503.18666](https://arxiv.org/abs/2503.18666) | Structured runtime rules, including LLM-generated rules. | Typed rules alone do not establish novelty or soundness. |
| [AuditCoder source](https://github.com/puppet0x3f/AuditCoder/tree/7617810348f8562db02d8af3b9f5f7a236089c18), README and baseline guide | Contract-annotated responsibility graphs, versioned evidence, scoped repair; the inspected snapshot documents APPS/ClassEval experiments and adapted AgentCoder baselines. | No novelty claim for contract ownership, audit traces or bounded repair. Do not promote a search snippet about a SciCode extension into verified results for this inspected snapshot. |
| [Variable Discovery for Metamorphic Testing of Scientific Software, ICCS 2023](https://www.iccs-meeting.org/archive/iccs2023/papers/140730328.pdf) | Automated scientific-document variable extraction for metamorphic testing. | No claim that extracting scientific constraints with an LLM is new. |
| [MR-Coupler, 2604.10126v2](https://arxiv.org/abs/2604.10126) | LLM-based metamorphic-test generation from source-code coupling and mutation-based validation. | Automatic metamorphic tests are established. The proposed empirical contrast must include competent generated tests. |

## Defensible additional question

The retrieved closest work does not establish the exact combination of: automatic
per-trajectory scientific-contract construction without task-specific author
review; charging construction inside the same inference/execution caps; a strong
generic generated-test control allowed the same scientific information; full
sequential native SciCode generation; and a semantic-check ablation with a second
fixed local model. This is a bounded empirical extension/replication question,
not a claim of an unprecedented algorithm. Larger sample size or another model
alone is not the claimed contribution.

Hypothesis: imposing an explicit, source-grounded scientific-check representation
improves correctly delivered native subproblem outputs over competent generated
Python tests under identical total resource limits. The alternative is that
generic tests suffice, or that incorrect inferred checks consume budget or block
correct solutions. All are legitimate outcomes.

## Comparator and intervention definition before data intake

B2 follows AgentCoder's separate test-designer / programmer / executor pattern.
The designer sees the public specification, background, interface and previous
public substeps, but not the native oracle or the new solver implementation.
It writes executable basic, edge and numerical tests. It may use metamorphic
relations, units, bounds and scientific laws; none are reserved for P. Feedback
supports at most the single revision allowed in the approved plan. There is no
best-of candidate selection or additional free model reviewer.

P uses the same stages and caps, but returns a typed contract: requirement/source
span, applicability condition, probe, executable predicate, tolerance with
rationale, and diagnostics. Deterministic compilation checks completeness and
records unsupported/invalid contracts. Schema acceptance cannot certify scientific
truth. The developer may not manually repair a test-task contract. Both arms use
the same public background, libraries, allowed execution and final grader.

A disables semantic predicates, retaining interface/runtime checks, and reports
the resulting budget use. L and B1 remain as defined in the approved proposal.
The runtime scheduling/order and token allocation are frozen after fixed
development, before held-out generation; no outcomes determine arm membership.

No prepared author-written R2T checks are added as a resource-free comparator:
those introduce task-specific scientific construction/review outside this
automatic public-only question. Consequently LR-SC1 cannot claim to outperform
R2T, AuditCoder, CodeMetaAgent, SpecCoder or any full unreproduced system.
The justified comparative claim is restricted to the implemented matched B2.
If implementing this strong B2 or independent oracle isolation proves infeasible,
the next gate must fail; do not quietly weaken it.

## Gate status and action

- Scientific checks are established prior art: **CONFIRMED**.
- An exact materially equivalent matched study was found: **NOT ESTABLISHED**
  within the stated bounded search, not a proof of absence.
- A specific empirical distinction and implementable comparator are defined:
  **PASS**, subject to technical admission and no outcome-driven revisions.
- Algorithmic novelty, effectiveness and publication readiness: **UNPROVEN**.
- Authorized next action: official SciCode provenance/rights/assets admission.
- No model download or GPU inference until the admission checks justify it.

Gate 0 uses a conservative retained 2 CPU-hour administrative allowance covering
local inspection/control, source review and its records. This is not measured
aggregate CPU and is not reported as a model experiment. No old account is reused.
