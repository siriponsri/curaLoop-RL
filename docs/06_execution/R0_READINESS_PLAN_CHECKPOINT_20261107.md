# R0 readiness-plan checkpoint

Date: 7 November 2026. Base main:
66e6387fa17d7e2f8e4d7e97613c2f974f982d06.
Status: PLAN_READY_FOR_REVIEW. Owner-approved direction: ChEMBL primary.

## Delivered

- [Readiness plan](../03_research/R0_CHEMBL_DATA_READINESS_PLAN_20261107.md):
  ordered source/schema/sample/context/readout steps, proposed bounded resources,
  canonical fields, rejection/missingness/duplicate rules, exposure controls,
  decision gates and the owner handoff.
- [Structured plan](../../research/manifests/r0_chembl_readiness_plan_20261107_v1.json):
  authority versus proposed bounds, zero scientific intake, fixed-release rules
  and explicit unknowns.
- Updated AGENTS.md, HANDOFF.md and the contribution decision table. Original
  source manifest and earlier scientific artifacts remain unchanged.

## Verification

| Check | Result |
| --- | --- |
| Structured JSON parsing, required local manifest targets | PASS |
| Relative links in plan and updated proposal | PASS; four checked targets |
| Direction, source and phase/outcome boundary consistency | PASS within fourteen structural consistency checks |
| Proposed limits and unstarted execution clock | PASS as document/manifest declarations; no run admitted |
| Git whitespace check | PASS; exit 0 |
| Official source documentation | PASS for bounded review of downloads, FAQ, assay definitions and service docs |
| Release-35 archive/schema/metadata source pin | NOT_RUN; no new source intake |
| Assay/document sample, independent adjudication and cohort readiness | NOT_RUN |
| Independent review | NOT_RUN; parent prepared and checked serially |

Commands: `rtk proxy python .local/r0-readiness-plan-audit.py` returned exit 0,
PASS, four links and 14/14 consistency checks. `rtk git diff --check` returned
exit 0. These checks validate the planning artifacts, not the scientific data.

One read-only discovery search used unsupported Windows wildcard path arguments;
it returned an rg path error and was corrected with directory/glob discovery.
It was not counted as evidence of artifact absence. Exact label-free protection
paths/hashes remain a mandatory prerequisite for later execution, not a verified
result of this plan.

No activity/gold/final intake, training, SSH processing, source retry, paid
service, team write or phase transition occurred. New resource numbers are
proposed, not a reset of old budgets or an execution grant. Next action is review
of the concrete plan and release of bounded M0-M3 execution if chosen. A later
metadata pass can support another R0 qualification decision; it cannot authorize
the next phase.
