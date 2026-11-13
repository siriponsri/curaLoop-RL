# Current-artifact evidence checks in a local molecular workflow: a bounded feasibility report

**Draft technical report, not submitted.** Siripon Srihangpiboon, King Mongkut's
Institute of Technology Ladkrabang. Contact: srihangpiboon.siri@gmail.com.
ORCID: 0009-0001-0611-5568. Authorship, affiliation, funding, competing interests
and AI-assistance disclosures require author confirmation before submission.

## Abstract

Scientific workflow agents need evidence that remains valid after input or output
files change. We implemented an inspectable local CSV-to-RDKit filtering and report
workflow with requirement-to-artifact identities, explicit invalidation and durable
execution records. An intended comparison against an equally informed checklist
was conditional on native external benchmark readiness. In a bounded examination
of eleven metadata-selected ScienceAgentBench tasks, one development reference
and six evaluation candidates qualified, but those evaluation candidates covered
only three repository lineages against a prespecified minimum of four. The gate
therefore failed and no comparative agent matrix or locked generations ran. The
primary method effect is not estimable. We report the admission failures, a
scorer-interface correction and the resulting software implementation separately
from the scientific hypothesis. Actual local-model software acceptance and its
associated costs are recorded in the accompanying versioned acceptance table.
These author-selected cases do not replace an external benchmark or establish
method superiority, independent validation, clinical utility or user benefit.

## 1. Question and position

The intended question is whether binding an explicit scientific requirement to
the identities of the artifacts that support it reduces stale-evidence completion
errors compared with an equally informed checklist, under matched model, tool and
resource limits. A changed dependency should invalidate the associated status;
an unchecked requirement must remain unknown. This is a testable mechanism
hypothesis, not a demonstrated contribution in the present report.

ContractBench evaluates temporal validity and byte integrity in tool observations
[2]. StateM studies durable execution states and checked transitions [3]. These
works make generic state tracking, contracts, hashes and recovery insufficient as
standalone novelty claims. Our narrow candidate distinction is dependency-bound
completion evidence for mutable scientific files. We have not established that
distinction empirically against these or matched controls. Their reported scores
are not reproduced here and cannot be transferred to this workflow.

ScienceAgentBench supplies publication-derived scientific programming tasks and
execution-based assessment [1]. We attempted a limited native programmatic
qualification in the retained verified snapshot, rather than equating a successful
model reply with task completion. RDKit supplies the molecular representations,
descriptors and drawings used in the delivered tool [4].

## 2. Methods

### 2.1 Authority, preservation and resource accounting

The owner authorized a fresh 96 CPU-hour and 24 allocated GPU-hour release,
maximum four combined CPU cores and one GPU worker, ending 20 November 2026 at
11:51:07 UTC. Earlier retained 0.675 CPU-hours remain separate. The admission
sub-budget was four CPU-hours, one GPU-hour and at most 96 development provider
attempts. Conservative reservations are retained after failures; they are not
reported as measured CPU consumption. Local guarded work uses one CPU core and
an aggregate memory ceiling no greater than the authorized 2 GiB. The owned
remote model container uses two CPU equivalents and a single designated GPU.
Administrative/control work includes an upfront retained allowance and is not
fully individually metered. No paid API, model search or public deployment was used.

Historical ledgers, frozen results and source identities remain preserved. Old
final16, private CF1 rows and hidden outcomes were not opened. Rights and
source/exposure records accompany the new snapshot; task input, reference and
gold/scorer files are separated. Public task snippets and prior exposure are
recorded rather than claiming universal contamination freedom. Model pretraining
exposure is unknown.

### 2.2 Native readiness rule

The retained verified archive has SHA-256
`46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
Annotations came from verified revision
`9c6e96c9e74572e979b0930ee735041cef528cb7`; the upstream evaluator/environment
source was captured at commit `c26e151ed601ba109dc4d35e057ff8e73fec469d`.
These identities do not imply reproduction of every paper result or of the entire
upstream harness. CodeBERT and paid rubric/image evaluation were not used.

Metadata screening nominated development IDs 2 and 3, and evaluation candidates
5, 16, 18, 19, 22, 26, 40, 41 and 85. The minimum was one qualified development
task, six qualified evaluation candidates and four repository-lineage groups among
qualified evaluation candidates. Repository lineage is a proxy, not a certificate
of publication-level independence. Selection preceded reference-body processing;
it is not a random sample of the benchmark. No native comparative matrix was
frozen because this prerequisite was not satisfied.

Reference programs and predicates ran in evaluator-only containers. No reference
or gold body was fed to the candidate model. Initial mount and byte-transport
failures were repaired transparently. A dependency-only repair and one final
source-supported compatibility batch were bounded in advance; the final batch
ran only the four references that had failed, without refitting successful ones.
We stopped after that batch rather than relaxing the cohort rule or searching
for a substitute benchmark.

### 2.3 Scorer correction

The initial adapter expected a scalar result, whereas upstream `eval()` returns
`(success, log_info)` [5]. Consequently its earlier nominal false values are
unsupported adapter flags, not scientific task failures. We added a strict tuple
decoder and rescored retained successful outputs without rerunning their reference
fits. Original reports remain present. The final admission receipt carries the
corrected interpretation; stale fields retained from the earlier report must be
read together with `native_interface_status`. This implementation error belongs
to the current work, not to the upstream benchmark.

### 2.4 Local software and model boundary

The delivered workflow accepts bounded CSV input, computes molecular weight,
LogP, TPSA, HBD and HBA using RDKit and applies three inclusive upper limits.
Rejected records retain reasons. It exports actual descriptors, selections,
reports, evidence and a hash manifest. It does not perform molecular
standardization, assay prediction, synthesis or clinical assessment.

Each requirement records supporting artifact hashes and a validator source
version. Changes or missing dependencies make that requirement unknown. Current
checks cover row accounting, numeric selection consistency and descriptor units;
they are not a complete independent scientific oracle. Durable SQLite revisions
record attempts, cancellation, failures and explicit resume. Exports are refused
after current identity checks fail. The local hash chain is not an external
signature or protection against a fully privileged operator replacing every file.

The fixed primary checkpoint is Typhoon 2.1 Gemma3 12B Q4_K_M, using its existing
cache and recorded model digest. In product mode it only proposes typed numeric
limits and a local export acknowledgement. It cannot upload arbitrary code or
choose new tools. Constrained JSON simplifies the task and does not establish
general-purpose autonomous scientific reasoning. Every actual provider attempt,
raw response, fallback status, generated-token count and resource lease is retained.

### 2.5 Analysis scope

Author engineering cases were frozen before their product model responses. They
cover three threshold requests in English and Thai, with exact parameter and
selected-ID checks, plus actual deterministic tool conformance. Each model case
has one attempt; failures are retained. No case-directed model tuning or response
replacement is allowed. These paired translations are related cases, not six
independent scientific samples. We report per-case observations without a
population confidence interval, significance test or claims of equivalence.

The intended equal-information checklist, LLM-only, self-debugging, applicable
deterministic research controls and invalidation ablation were **NOT_RUN**.
No effect estimate or interval can be computed for that unrun comparison. In
particular, an absent estimate must not be encoded as a zero effect.

## 3. Results

### 3.1 Native admission did not pass

The final receipt qualifies development ID 3 and evaluation IDs 5, 16, 18, 19,
40 and 41. Evaluation candidates represent `psa-lab/predicting-activity-by-machine-learning`,
`felixjwong/antibioticsai` and `anikaliu/CAMDA-DILI`: three groups, below four.
IDs 2, 22, 26 and 85 remained nonqualifying under the final bounded environment.
Missing `mdf_forge` and `fau_colors` and other compatibility failures are retained.
This is a bounded environment/reference-readiness result; it neither disproves
the proposed mechanism nor demonstrates that ScienceAgentBench is invalid.

Figure 1 and the machine-readable admission table report counts and individual
reference status. Their numerators are qualified references, not agent successes.
No locked candidate agent program was generated and no method ranking was measured.

### 3.2 Software and actual model acceptance

See the accompanying versioned actual-run acceptance table and software-check
receipt. Component checks exercise actual RDKit subprocesses, evidence invalidation,
export tampering, revision conflicts, cancellation and recovery. Browser captures
come from the served application with real tool output. These developer checks
are software evidence, not independent expert review, customer validation or a
substitute external research cohort. Model-case failures, if present, remain in
the numerator/denominator and are not repaired into success.

## 4. Limitations and interpretation

External readiness failed before the primary experiment, leaving the central
research question unanswered. The small metadata-selected subset, adapted wrapper,
dependency bounds, source-lineage proxy and known exposure prevent broader benchmark
claims. Seven qualified references do not justify lowering a prespecified diversity
rule after seeing readiness results. Conversely, the failure does not imply the
full benchmark cannot be run with a separately designed environment.

The product case set is small, author-selected and simple; both roles are strongly
constrained. Correct JSON, a completed execution and file consistency do not prove
the natural-language scientific request was fully answered. A validator can be
internally consistent and scientifically wrong. Single-case timing includes hardware
and service variability and is not a controlled speed comparison. Research quotas
apply to guarded research sessions, not automatically to a user-started server.

No independent evaluator, external user study, wet laboratory, prospective assay,
clinical study, business pilot, broad connector ecosystem or demonstrated economic
benefit is included. Existing negative research results are retained separately;
the new software does not overwrite them or convert them into positive findings.

## 5. Publication readiness

**Not ready for a claim of a superior agent method or a validated pharmaceutical
research platform.** The honest deliverable is a feasibility/software technical
report with reproducible implementation and negative admission evidence. A
scientific methods article would need an admitted, independently justified cohort,
frozen matched controls, actual model trajectories and uncertainty analyses under
a newly reviewed scope. That work is not silently initiated here. A software venue
would additionally judge distinctiveness, documentation, sustained software quality
and fit; this report does not guarantee acceptance. No manuscript has been sent.

## Reproducibility and availability

Source, public aggregate receipts and author-example molecule inputs are in the
repository. Raw external benchmark archives, reference/gold bodies, private job
stores and full returned environments remain local and excluded from Git.
Reacquire third-party data from its official source under the applicable licenses;
the code license is not a blanket license for all benchmark content. The new
account's README distinguishes public receipts, private exact source snapshots,
historical invalid reports and final interpretations. Future reproduction requires
the pinned checkpoint and an explicitly configured bounded model backend; the
ordinary deterministic local workflow does not need SSH or a model.

## References

1. Chen Z et al. ScienceAgentBench: Toward Rigorous Assessment of Language Agents
   for Data-Driven Scientific Discovery. ICLR 2025; arXiv:2410.05080v3.
   https://arxiv.org/abs/2410.05080v3
2. Wang J et al. ContractBench: Can LLM Agents Preserve Observation Contracts?
   arXiv:2605.17281v2, 2026. https://arxiv.org/abs/2605.17281v2
3. Qin Z et al. StateM: Reaching 95.3% Raw Accuracy, or a $15 Frontier Run, on
   Terminal-Bench 2.1 via Harness Scaling. arXiv:2608.15089, 2026.
   https://arxiv.org/abs/2608.15089
4. RDKit. Getting Started in Python. Official documentation, accessed 13 November
   2026. https://www.rdkit.org/docs/GettingStartedInPython.html
5. OSU-NLP-Group. ScienceAgentBench, `compute_scores.py` and `run_eval.py`, commit
   c26e151ed601ba109dc4d35e057ff8e73fec469d.
   https://github.com/OSU-NLP-Group/ScienceAgentBench/tree/c26e151ed601ba109dc4d35e057ff8e73fec469d
