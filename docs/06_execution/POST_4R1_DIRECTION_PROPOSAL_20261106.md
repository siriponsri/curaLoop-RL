# After 4R1: an evidence-to-experiment research and product direction

6 November 2026, Bangkok. **PROPOSAL; NEW EXECUTION NOT_AUTHORIZED.**

## Recommendation and basis

Develop an agent that turns a molecular R&D question into an evidence-linked,
feasible confirmation plan and an inspectable report. The research hypothesis
is that handling evidence identity, measurement status and conflicting endpoints
explicitly can improve scientific decisions under a limited budget. This is a
hypothesis to challenge, not an established novelty or benefit claim.

The [4R1 diagnosis](../03_research/GOAL4R1_RESULTS_V1.md) supports retaining GP
as a useful development baseline. It does not justify another rescue trial for
the present acquisition thesis. Keep its source/results and reserved final panel
unchanged. Starting main for this proposal is `5d688c877439142a5874fcee7f8a034459c3c43c`.

The intended demonstration accepts a target question, retrieves permitted source
evidence, flags incompatible assay definitions, proposes what to measure next,
replays an authorized benchmark through a trusted engine, updates the plan after
new measurements, and produces a source-linked report for a team workspace.
Physical laboratory execution and universal connectivity are later possibilities,
not proposed prototype capabilities.

## Options and tradeoffs

| Direction | Strength | Main limitation | Recommendation |
| --- | --- | --- | --- |
| P1 product prototype first | Fast route to a usable evidence/report workflow and later user feedback | A connector or literature agent alone is a weak new molecular-method contribution | Viable if near-term product usefulness becomes the priority |
| New acquisition model first | Direct continuation of scientific algorithm work | Current evidence does not establish a useful mechanism; another model may only repeat the same failure | Defer until a distinct question and suitable observations are established |
| Evidence-to-experiment programme | Connects a scientifically testable decision problem with the selected R&D workflow | Requires valid confirmation data, an explicit difference from prior work, and a separate workflow evaluation | Recommended, beginning with the bounded feasibility prototype below |

## What the contribution would have to demonstrate

The scientific comparison should hold the chemical predictor and resource model
fixed while testing whether the proposed treatment of evidence changes worthwhile
measurement decisions. Candidate actions are acquiring permitted background
evidence, ordering a primary measurement, ordering confirmation, or reporting
that a decision is unsupported. A specific decision principle must be selected
before development campaign outcomes are inspected. A catalogue of agent tools
does not supply that principle.

Potential primary endpoint: new source-confirmed positives under a fixed declared
budget. It must be defined from the actual source phenotype and observed outcomes.
Selectivity is a possible later extension only if matched counter-assay evidence
exists. Real assay cost/time savings require actual cost/time evidence; assumed
operational values remain simulation parameters.

Planned controls include a cheap fixed confirmation rule, a strong statistical
policy with the same predictor, and an appropriate published multifidelity
search method if its observation/objective contract can be matched. Agent
workflow comparison uses the same model with ordinary search. Removing the
evidence layer or fixing the decision policy should test the claimed mechanism.
These comparisons are proposed, not implemented or run.

Scientific utility, evidence correctness and workflow utility are separate
outcomes. A well-written report cannot count as an experimentally confirmed hit;
a better predictor cannot establish agent orchestration value.

## Primary-source refresh and remaining overlap

This is a focused update on 6 November, not an exhaustive novelty review.
alphaXiv discovery supplied leads; primary text/records support the statements
below. Recent arXiv sources remain preprints.

| Source and access | Relevant established work | Consequence |
| --- | --- | --- |
| [MF-PCBA, JCIM 2023](https://pubs.acs.org/doi/10.1021/acs.jcim.2c01569), DOI 10.1021/acs.jcim.2c01569; primary indexed methods and [official source repository](https://github.com/davidbuterez/mf-pcba). Direct PMC access later challenged. | Sixty primary/confirmatory dataset pairs; the release distinguishes measured confirmation values from default-filled values. | A candidate source, not a cleared campaign benchmark. Preserve measurement/default/censoring distinctions and selective follow-up. Sixty datasets do not mean sixty independent families. |
| [Nonmyopic Multifidelity Active Search, ICML 2021](https://proceedings.mlr.press/v139/nguyen21f.html); primary abstract refreshed, targeted full-text review retained in the prior packet. | Budget-aware search using cheap and expensive feedback already exists. | Multifidelity, confirmation or lookahead alone is insufficient novelty. |
| [MolDesignBench, v1, 23 September 2026](https://arxiv.org/html/2609.27349v1); targeted abstract, benchmark and evaluation sections. | Scenario-based molecular design evaluates constraints, tool reasoning and infeasibility detection. | An agent that checks chemical constraints is not an untouched contribution. It is a potential adjacent benchmark, not confirmation-assay ground truth. |
| [Autonomous Science Bench, v1, October 2026](https://arxiv.org/html/2610.18449v1); targeted campaign, backend and limitations sections. | Budgeted experimental agents, trusted measurement records and discovery/learning gates are already proposed and evaluated with replay/twin backends. | A trusted replay ledger is useful infrastructure, not sufficient research novelty. Public-data contamination and surrogate limitations still matter. |
| [LLM sequential decision making under uncertainty in biochemical domains, v1, September 2026](https://arxiv.org/html/2609.33061v1); targeted results/methods. | Studies prior knowledge, tool access and sequential choices against statistical references; aggregate results do not establish uniform agent superiority. | Keep a strong statistical control and matched model comparisons. Do not assume replacing a planner with an LLM repairs acquisition. |

The earlier [related-work packet](../02_literature/REDESIGN_DEEP_REVIEW_20261105.md)
also covers ChemCrow, Coscientist and PaperQA2. The unresolved distinction is the
specific decision method and its valid molecular evaluation, not the existence
of a chemistry agent or a report connector.

## Data feasibility before a scientific pilot

MF-PCBA is a lead to audit, not a substitute automatically approved for FS-Mol.
The next step must establish source versions/rights, target and endpoint
identity, candidate overlap, measured confirmation masks and the follow-up
mechanism before outcome-based selection. Missing or default-filled values are
not automatically experimental negatives. A replay restricted to measured pairs
estimates performance in that selected population, not the full screened library.

Do not assume that unmeasured confirmation values can be queried from a historical
table. If valid policy comparison is not identifiable, return a NO_GO/options
report; do not silently invent an oracle or change the population. A prospective
study or a different source would be a separate owner decision.

Retain the ambition of 12 or more verified biological groups for a later broad
study, subject to actual eligibility and independence evidence. Report achieved
counts. Do not borrow the old FS-Mol component counts for a new dataset or shrink
the target silently. Preserve the existing reserved final panel and block its
outcomes from external-source retrieval. Retrieval controls do not certify that
an LLM has never seen public data during pretraining.

## Proposed next goal: 4R2-A feasibility prototype

Proposed new cap: **4 cumulative CPU-hours / 12 elapsed hours / maximum two CPU
workers**, with processing/tests on dr-train. This is a planning estimate, not
authorization or a guarantee of completion. Record a new window and fresh owned
remote root after approval; return and verify all task files before cleanup.

| Deliverable | Acceptance evidence |
| --- | --- |
| Source-backed problem and novelty decision | Compare the candidate method with the closest papers; state a concrete difference or NO_GO, with unresolved claims retained |
| Candidate-data feasibility register | Paper/version/rights, endpoint and missingness semantics, overlap/exposure rules and achieved eligible counts; no final outcomes or bulk activity-table intake |
| Runnable offline workflow prototype | Fixed source snapshots/fixtures through evidence records, plan validation and local Markdown/JSON report bundles; twelve prespecified success/failure contract cases |
| Inspectable next-study design | One primary question, observation contract, essential controls, exposure/split plan and a measured pilot resource estimate when available |

Freeze the twelve engineering cases before implementation: six ordinary workflow
cases and six failures, covering source unavailability, incompatible endpoints,
reserved evidence, stale revisions, interrupted work and duplicate delivery.
Success includes correctly stopping an unsupported workflow. Deterministic replay
tests demonstrate engineering behavior only; they do not establish live retrieval,
autonomous model performance or scientific benefit.

This small offline prototype is a newly proposed subset of the
[P1 direction](../04_business/AGENTIC_RD_PLUGIN_PROPOSAL_V1.md), not all of P1.
MCP/client integration, live source evaluation and actual destination delivery
remain subsequent integration tasks. First delivery stays local/preview-only.
There is no scientific campaign, new model/API purchase, final-label release,
live team-tool write, customer contact or journal submission in 4R2-A.

If source access or metadata counts cannot be obtained, report the exact source
and target path for owner help. If data or novelty fails, preserve the prototype
and explain the options before changing the scientific design. A feasibility
goal may complete with a documented NO_GO; it does not pass the research gate.

## Subsequent goals, each requiring its own decision

| Stage | Result sought | Budget posture |
| --- | --- | --- |
| 4R2-B: scientific pilot | Implement one approved decision principle and test it against matched controls on eligible development data | Initial proposal: 8 CPU-hours / 12 elapsed hours / maximum four workers; revise from 4R2-A measurements before approval |
| P1 integration | Connect the tested local tools to a verified AI client, permitted live sources and one previewed team destination; compare workflow quality with ordinary search | Existing P1 starting proposal: 4 CPU-hours / 12 elapsed hours / maximum two workers; model/tool quotas require a separate check |
| New broad study | Freeze the new task/split/exposure design and evaluate independent groups with uncertainty and essential ablations | Estimate after pilot; no automatic return to the previous 48 CPU-hour allowance |
| Paper package and R&D pilot | Assemble evidence-supported molecular-method claims, and separately test analyst review effort/reuse with an authorized team | Human declarations, customer access, venue, fees and real delivery authority remain separate decisions |

The existing [Goal 5 route](GOAL_TRACKER.md) must be reconciled with the new
design before execution; the old reserved panel is not automatically suitable.
Goal names and this table confer no execution authority.

## Journal and business assessment

The current [JCAMD scope](https://link.springer.com/journal/10822/aims-and-scope)
allows appropriate retrospective validation for novel computational strategies
and prioritizes experimental validation. Our assessment: a molecular decision
advance with valid measured outcomes is a more plausible match than generic
agent integration alone. Acceptance and novelty are not established; retain
the existing venue decision until the actual contribution can be assessed.

For business, test whether an R&D team values fewer unsupported decisions,
reproducible study handoffs and less review effort. These are proposed benefits.
Measure them in a later authorized pilot; neither an offline demo nor paper
acceptance establishes demand, savings or willingness to pay.

## Current evidence and next actor

**READY_FOR_OWNER_REVIEW.** This turn inspected the clean main checkpoint,
existing results/plugin plan and primary literature. It prepared this proposal;
it did not launch a new study, access final outcomes, connect to dr-train,
purchase a service or write to a team tool. The owner can approve only 4R2-A,
choose product-first P1, or request a different research question. No downstream
stage starts automatically.
