# Proposed research roadmap and bounded long-run options

5 November 2026, Asia/Bangkok. **PROPOSED; NO LONG RUN AUTHORIZED OR STARTED.**
The owner requested the later goals, the achievable autonomous endpoint and
consultation before decisions for which the evidence is insufficient.
This plan preserves existing scientific records and does not open new labels.

## Recommended endpoint

The maximum proposed internal-work endpoint is **Goal 6A: a complete research
and manuscript package ready for the human author's review**. This is conditional
on source access, data readiness, a defensible method and successful validation.
It is not a promise of favorable results, submission readiness with unconfirmed
declarations, journal acceptance or completion within an unmeasured runtime.

The recommended first execution block is **Goals 3–4**, followed by an owner
decision before spending the final-study budget. Goal 2 failed its usefulness
test, and the external data and replacement method are not yet evaluated.
A broader Goals 3–6A block is an alternative if explicitly authorized, with the
same consultation rules and evidence gates below.

## Goal contracts

| Goal | Work | Required completion evidence / next decision |
| --- | --- | --- |
| 3: real data and method decision | Follow the [detailed proposal](GOAL_03_PROPOSAL_20261105.md): source/paper/endpoint/rights, family and structure audits, roles and operating-condition split design; select one stronger method hypothesis. | Dataset card, source/family register, exclusion/overlap report, split/access manifests and method decision. Aim for 12+ evaluable held-out families separate from development; actual counts and dependence must be documented. Owner consultation if required scope or rights cannot be resolved. |
| 4: method and strong controls | Implement the selected model/planner and objective-matched non-RL controls. Test exact cases, privacy and resources, then development/validation only. Examine at most three preregistered candidate configurations, preserving failures and changes between versions. | Executable versioned method, baseline contracts, compute/usage logs, ablations and estimates with uncertainty. Demonstrate an identifiable mechanism and plausible discovery/compute value; do not invent a confirmatory material-effect threshold. Measure canary runtime before proposing a final allocation. Consult owner if competing directions cannot be resolved or none provides a defensible advance. |
| 5: frozen held-out validation | Freeze source/data/roles/methods, contrasts, metrics, operational regimes, analysis and resource allocation before accessing final outcomes. Execute matched campaigns, dependence-aware uncertainty and mechanism ablations. | Complete immutable run/attempt ledger, all failures and exclusions, effects/uncertainty by family/source, decision/runtime tradeoffs, calibration limitations and a reproducible analysis. A separate agent/operator may reexecute a clean environment; disclose same-project automation and do not call it external independent scientific replication. Never retune on final outcomes. |
| 6A: research package for author review | Reconcile claims and literature with executed evidence; assemble English editable manuscript, readable PDF, scientific figures/tables, supplement, code/input instructions, availability statement, AI-use account and cover-letter draft. | Rendered/inspected files, traceable claims, reproducibility bundle tied to immutable source and an author-review checklist. Unconfirmed human declarations remain explicitly pending. Assess current JCAMD fit; request a venue/claim decision if evidence does not support the intended route. No public DOI/archive publication is implied. |
| 6B: actual journal submission | After human review, confirm the exact manuscript, complete author list/order, funding/conflicts/contributions/permissions/originality and any institutional requirements; recheck total cost and publication route. | Explicit authorization for the exact reviewed package and actual submission receipt. No payment or editorial communication is authorized merely by a long run through 6A. |
| 7: response to editorial review | Analyze the journal's actual decision, prepare a point-by-point response and propose justified revisions/additional experiments. | Requires editorial feedback and a new bounded revision contract. No guarantee of the number of rounds, decision timing or acceptance. |

Existing Goals 1–2 remain complete in their recorded scopes. Splitting Goal 6
into 6A/6B clarifies the human-author boundary; it does not change old evidence.

## What successful long-run progress can reach

- **Data or permission missing:** report the exact missing source/file/decision
  during Goal 3 and ask the owner. Continue only work independent of that input.
  Do not claim the desired benchmark is ready or silently reduce its scope.
- **Method gate unresolved:** stop dependent final-study work after Goal 4,
  explain competing options or failed candidates, and ask the owner which
  direction to pursue. Do not relabel a failed method as the desired high-impact
  result or automatically change to a narrow benchmark paper.
- **Data and method gates pass:** under explicit expanded authorization,
  proceed through the frozen Goal 5 and assemble Goal 6A. Report unfavorable
  final outcomes faithfully; discuss any change of claim/venue with the owner.
- **Author review / editorial process:** 6B and 7 depend on owner declarations,
  authorization and external events. An internal long run cannot certify those
  facts or guarantee publication.

The ambitious research target is a useful decision method that transfers across
biological families and operational shifts. More data rows, an RL label, WAIT
support, a valid generic bound or polished documents do not establish it.
Historical assay labels and synthetic operating times/costs remain separate.

## Consultation rule requested by the owner

When evidence is insufficient for a material choice, present the proposed
action, alternatives, evidence, likely impact and recommendation, then ask
before performing dependent work. Concrete triggers include:

- unresolved source rights, endpoint meaning, family mapping or split leakage;
- inability to support the agreed family scope without changing the population;
- competing algorithm directions, or failed candidates requiring a new thesis;
- increasing compute/storage/download allocation or using a paid resource/GPU;
- changing a frozen final protocol, replacing failed final runs or interpreting
  evidence as supporting a materially different paper claim;
- venue changes, human declarations, external publication, communication,
  submission or payment.

Record the pending question and checkpoint. Preserve outputs and continue
independent authorized tasks where useful. Routine implementation fixes and
checks inside a clear approved contract do not require repeated approval.
Uncertain future outcomes are tested by an approved experiment; they are not
permission to make unsupported claims.

## Proposed resource options, not completion estimates

| Option | Endpoint | Resource ceilings |
| --- | --- | --- |
| A, recommended first block | Goals 3–4, then owner review | 48 cumulative CPU-hours: up to 8 for Goal 3 and 40 for Goal 4; at most 4 CPU workers overall, with Goal 3 retaining its 2-worker cap; 24-hour execution window. |
| B, extended conditional block | Goals 3–6A, subject to consultation/gates | 128 cumulative CPU-hours: up to 8/40/80 for Goals 3/4/5; at most 4 CPU workers; 48-hour execution window. Goal 5 allocation must first be justified by Goal 4 canary measurements. |

Both options use existing local/dr-train resources with live allocation/job
checks, no GPU and no additional paid service. Maximum total worker RAM is
16 GiB and additional scratch/output disk 32 GiB; Goal 3 retains its stricter
8 GiB RAM/16 GiB scratch/200 MB metadata-download caps. Do not terminate other
jobs or modify SSH configuration. Dependency changes, if required by Goal 4,
belong in an isolated pinned environment and must preserve the existing POC.

CPU-hours measure process/subprocess compute, not simulated assay time or LLM
tokens. The execution window is elapsed time from block start, including waits;
it is a stopping limit, not a promise that all goals will finish. Goal 6A's
analyses/rendering count within the same global allocation. Stop at the first
applicable cap, preserve the checkpoint and ask about an extension rather than
silently spending more. No numeric final-study runtime is inferred from the
old cheap Tox21 pilot or from the host's logical CPU count.

At most three candidate configurations in Goal 4, not an unbounded search.
Independent data, methods and English/journal reviewers can work in parallel
with the parent as sole repository integrator. Report completed work and open
decisions at each goal checkpoint. A launched remote job is not a completed run;
completion requires logs, exit status, output identity and analysis checks.

## Source and human-author boundary

The [current JCAMD author guide](https://link.springer.com/journal/10822/submission-guidelines),
checked 5 November, requires editable manuscript sources and author/declaration
information. Submission implies co-author/institutional approval and originality/
concurrent-submission conditions; substantive LLM assistance must be accurately
documented with human accountability. The owner's contact/ORCID and USD 300
limit do not certify these declarations.

The [current publication page](https://link.springer.com/journal/10822/how-to-publish-with-us)
states no APC for subscription publication; optional OA exceeds the stated
budget. Route/mandate compatibility and actual mandatory cost must be checked
again for the final package. No acceptance, waiver or funding coverage is assumed.

The current conversation requests a plan only. Choosing a future long-run
option would need explicit execution authorization and the exact budget;
it would supersede the earlier per-goal approval cadence only within that scope.
The owner's instruction to consult on unresolved material choices always applies.
