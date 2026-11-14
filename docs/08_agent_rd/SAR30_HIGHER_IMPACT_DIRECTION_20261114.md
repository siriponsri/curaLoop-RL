# Higher-impact direction after SAR30 qualification

Date: 14 November 2026. Status: **RECOMMENDATION_ONLY — NOT_RELEASED_FOR_EXECUTION**.
This is a research and product decision document, not a manuscript. The current
qualification account does not authorize another dataset, model, comparison or
scientific rerun. ESE remains primary and JSS backup.

## Recommendation

Study **when reusable scientific actions and executable verification complement
each other, and when deterministic automation already provides the benefit**.
Build the corresponding product as a bounded, auditable scientific-execution
plugin. The potential contribution is a controlled empirical explanation of
reliability and cost, rather than a claim that adding a checker creates a new
kind of agent.

The visible product could accept a public research task, select a typed action,
execute its real Python workflow, show the resulting artifact with exact
code/data/environment identities, diagnose an applicable check failure, and
attempt one budgeted repair or report that completion is unverified. It should
make failed execution as inspectable as successful execution. A pharmaceutical
workflow is the application example; clinical benefit and customer value remain
outside the computational claim.

**Novelty is not established.** Packaging published mechanisms together is not
itself a new research result. A positive effect, a statistically precise result
and publication cannot be promised. The current failed environment preparation
does not provide an agent-performance result supporting this direction.

## Why the former question needs strengthening

The earlier P-versus-T comparison asks whether supplying an executable checker
helps beyond its written public definition. That is legitimate, but prepared
checking is already close to published work and task-dependent effects can be
small. Reliability gains can also come from preimplemented scientific actions,
extra information, additional model calls or unequal preparation. A better
study must separate those mechanisms and include preparation in the cost.

The new qualification adds three practical warnings:

1. Import/install success is a different endpoint from native scientific success.
   The selected installation recipe encountered ENOSPC before any reference was
   run; its 4 GiB temporary mount is a likely, not per-mount-confirmed, bottleneck.
2. Repository labels are insufficient independence guarantees: two nominally
   separate repositories contain exactly identical scientific input files.
3. A small, concentrated cohort cannot establish a general small improvement.
   More seeds or difficulty variants do not create more independent papers.

## Closest work and what it rules out

These are source-based summaries, not replications performed by CuraLoop.

| Primary source | Relevant evidence | Implication for our claim |
| --- | --- | --- |
| [Rules to Tools, 2610.00313](https://arxiv.org/abs/2610.00313) | Matched public definitions and prepared executable checks; task-dependent SciCode results, a larger shared-definition cohort tied, and source-through-Python matched the dedicated tool aggregate | Do not claim executable scientific checks, a dedicated tool command or generic checker advantage as novel. Include a source-through-Python control or document why it is the same treatment implementation. |
| [Paper2Agent, author manuscript](https://github.com/jmiao24/Paper2Agent/blob/main/skills/paper2agent/paper2agent-paper/references/paper.md) | Turns paper code/workflows into tested callable resources; evaluates tool packages and downstream use | Paper-to-plugin construction and tested scientific actions are prior art. Separate implementation reuse from verification and include preparation cost. |
| [GAV, 2610.30292](https://arxiv.org/abs/2610.30292) | PDE experiments use generated problem/reference pairs, numerical feedback and guided development; reports substantial error reductions | Scientific feedback and iterative numerical improvement are established mechanisms. Its PDE reference construction does not automatically transfer to drug-screening or general research repositories. |
| [When Tools Lie, 2610.08097](https://arxiv.org/abs/2610.08097) | Controlled tool corruption on 31 mathematical problems; mandatory checking helped, while optional designs had unequal checking rates | Tool availability and actual verification policy must be measured separately. A generic corrupted-tool demonstration would duplicate a closely related question. |
| [ResearchEnvBench, 2603.06739](https://arxiv.org/abs/2603.06739) | Distinguishes dependency integrity, CPU execution, accelerator alignment, real entrypoints and unsupported readiness claims | A successful installation is not execution evidence; a setup benchmark or “evidence attached” feature alone is not a new contribution. |
| [Does Failure Feedback Direct Agent Self-Modification?, 2610.14662](https://arxiv.org/abs/2610.14662) | Controlled feedback comparisons show model dependence and distinguish target repair from held-out generalization | Count regressions and transfer failures. Improvement after selecting a repaired candidate does not prove feedback caused general improvement. |

The four October 2026 papers above are treated as preprints here; repository or
PDF conference wording is not independent confirmation of acceptance. The R2T,
GAV, corrupted-tool and ResearchEnvBench full texts were inspected through
alphaXiv in this qualification/reporting work. The source discovery results also
identified further harness/reproducibility work; those titles are leads rather
than evidence of a completed exhaustive novelty review.

## Falsifiable experimental question

Under the same model, public scientific requirements, initial data access and
total execution/model budget, what changes native correctness and cost:
reusable scientific actions, executable diagnostic feedback, or their interaction?

| | Ordinary public checking specification | Prepared executable diagnostic checks |
| --- | --- | --- |
| Ordinary code/filesystem tools | G: fixed strong self-debugging control | V: executable-verification treatment |
| Prepared scientific actions | A: action-reuse treatment | AV: combined treatment |

All four receive the same public scientific facts and normal tool permissions.
The prepared implementation is an explicit treatment, not concealed extra
knowledge. Controls can implement checks and reuse repository code within the
same budget. A source-through-Python control must have the actual implementation
when testing the benefit of a special invocation interface; otherwise that
comparison confounds interface and implementation. Measure actual tool/check
use and task-specific preparation, not merely nominal access.

Additional contextual controls should include an unchanged deterministic Python
workflow and LLM-only generation. A reference program is an evaluator sanity
check, not an autonomous deterministic solver. A developer-configured workflow
must disclose its task-specific configuration and preparation cost. LLM-only
cannot be described as equal-tool access when execution is intentionally absent;
it is contextual, while the four matched tool arms support causal comparisons.

Predeclare one primary paired contrast and the interpretation of the factorial
interaction. Do not promote a noisy secondary interaction into the main finding
after looking at outcomes. A defensible option is AV-versus-A as primary and
the action-by-verification interaction as secondary unless prospective precision
analysis supports an interaction-focused study.

Report native completion, continuous scientific error where the upstream
endpoint supports it, task-level wins/losses/ties, previously successful cases
broken by repair, check coverage/use, unsupported completion claims, fallback,
timeouts, preparation and execution CPU/GPU/model cost. Use paper/shared-data
clusters and task-averaged seeds. Missing outcomes stay in the denominator under
a frozen missingness rule. Zero effect and uncertainty are valid results.

## Dataset direction, without creating our own benchmark

**CORE-Bench is the preferred source-readiness candidate to investigate, not an
admitted replacement.** Its [paper](https://arxiv.org/abs/2409.11363) describes
270 tasks based on 90 papers in computer science, social science and medicine.
The three difficulty variants share paper origins; they are not 270 independent
studies. The [official repository](https://github.com/siegelz/core-bench) now
recommends the Holistic Agent Leaderboard harness and says its old harness is
not actively maintained. This needs version and evaluator verification before
any execution proposal can be regarded as ready.

Its attraction is paper-level computational reproduction with existing upstream
tasks and scoring, rather than another custom benchmark publication. It does
not guarantee CPU/GPU suitability, lawful access to every capsule, numerical
scoreability without a paid judge, compatibility with a small local model, or
enough eligible held-out papers. None of its capsules, target answers, model
weights or native environments was downloaded or executed in SAR30-Q.

A prospective intake must verify source revision, existing development/test
roles, capsule/data licenses, evaluator/transitive calls, language/vision needs,
hardware/network requirements and real reference readiness. Prefer existing
official roles and one difficulty level per paper. Inventory all candidates and
publish an exclusion rule before results; do not select easy papers by score.
Do not choose a new numerical floor just to match whatever count happens to be
available. Freeze a precision-based population decision before locked evaluation.

[SWE-bench Verified](https://www.swebench.com/SWE-bench/) is a documented SE
alternative with 500 engineer-confirmed issues and a Docker harness, but its
issue-resolution endpoint does not establish scientific or pharmaceutical
validity. It is not silently adopted here. Existing author exposure to
`astropy__astropy-12907` and `astropy__astropy-13033` remains recorded in the
previous proposal. A future selection must preserve those exposure exclusions.

## Proposed single staged long goal: LR-SAV1

**Planning ceiling only: 96 fresh CPU-hours + 48 allocated GPU-hours / seven
elapsed days, at most four combined CPUs and one GPU. Not authorized by the
SAR30 qualification release.** It would require a separate owner choice and a
final source/resource plan, including any capsule/model download limits.

| Milestone | Planning CPU h | GPU h | Progression requirement |
| --- | ---: | ---: | --- |
| Source, rights, evaluator and native feasibility | 12 | 2 | Existing benchmark; upstream-compatible isolated environment; useful native endpoint, full failure traces and no paid/live scoring dependency |
| Development and protocol freeze | 20 | 6 | One fixed model; equal-information controls; technical canaries; checker conformance; prospective precision and cost projection |
| Frozen comparison | 44 | 32 | Fixed cohort, arms, seeds and budgets; measured projection with 25% contingency fits the total; every attempt recorded |
| Analysis, plugin demonstration, return and owner report | 20 | 8 | Native outcomes, failure/regression analysis, reproducible evidence and explicit limitations; results before manuscript |
| Total | 96 | 48 | No automatic model/dataset search or failed-gate retry loop |

This envelope is not an estimate measured on CORE-Bench. If native feasibility,
eligible paper coverage or projected costs fail, stop and report that exact
condition. Do not open a replacement benchmark under the same release. A single
fixed model and fixed development budget are sufficient for the first study;
generality across model families would remain limited. Any model download,
capsule rights, disk ceiling and offline runtime policy must be included in the
one owner release before intake, rather than obtained piecemeal during runs.

Technical progression must not require a positive agent effect. Publication
readiness needs a nonduplicative question, a qualified population, fair controls,
enough precision for the intended claim, authentic model runs and complete costs.
If those pass and the effect is null/negative, finish the analysis without
changing the hypothesis. Manuscript writing still waits for the owner's results
review. The present records are **not sufficient for an ESE/JSS research paper**.

## Immediate owner decision

Review the SAR30 results first. There are two distinct matters:

- The current technical failure: installation storage exhaustion under a 4 GiB
  temporary-filesystem recipe and incompletely diagnosed import failures. Fixing
  that infrastructure would need
  an explicit bounded technical release; it is not evidence that the scientific
  idea failed, nor a reason to claim the benchmark is invalid.
- The contribution decision: whether the action-by-verification study above is
  worth source-readiness work on CORE-Bench. That choice is motivated by the
  scientific question and source diversity, not by trying to hide SAR30 failures.

No new research phase, model download, full comparison or manuscript starts
automatically from this recommendation. No independent expert validation,
customer pilot, clinical benefit, business revenue or superiority is claimed.
