"""Replace stale current-status text while preserving prior scientific records."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, now, read, sha, start


def write(name, text):
    (ROOT / name).write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def main():
    assert read(PUBLIC / "interpretation-v1.json")["method_claim_disposition"] == "NO_GO_QUOTA_ONLY_METHOD_CLAIM"
    assert read(PUBLIC / "fresh-absence-v1.json")["status"] == "PASS_FRESH_EXACT_ABSENCE"
    current = """**Current: LR-CF1 study complete; owner review before a new phase.**
Six admitted published-source campaigns,1,333,191 retained primary observations,
6,896 observation-supported confirmations,60 molecular fits and2,700 portfolio
cells completed. All30 real MVS-A score checks and independent local H/D recount
passed. Complete private return/reread and exact owned remote cleanup passed.

The [results](docs/03_research/LR_CF1_RESULTS_20261109.md) confirm a classical
hit/coverage tradeoff. **NO_GO for a quota-only new-method claim; journal readiness
is not established.** The [EN/TH offline report](research/product_handoffs/lr_cf1_v1/report.html)
and [English paper insert](docs/07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md)
preserve the actual evidence. Final16 remains sealed; no novel selector or live
integration was activated. Read the [owner checkpoint](docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md)
and [evidence index](docs/evidence/lr-cf1-20261109-v1/README.md).

CF2-Design and P-CF1 are alternative proposals requiring a new owner decision.
No unused LR-CF1 allowance or old conditional grant releases another phase.
"""
    for name, marker in (("START_HERE.md", "**Current: LR-D23 complete"), ("GOAL.md", "**LR-D23 complete"), ("PLAN.md", "**LR-D23 complete")):
        path = ROOT / name
        before = path.read_text(encoding="utf-8")
        assert marker in before
        history = before[before.index(marker):]
        title = before.splitlines()[0]
        write(name, title + "\n\n" + current + "\n## Historical checkpoints\n\nThe states below describe their original checkpoints, not current permissions.\n\n" + history)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    begin, end = readme.index("**Current research checkpoint:**"), readme.index("**9 November 2026:**")
    readme = readme[:begin] + """**Current research checkpoint:** [LR-CF1 is complete](docs/03_research/LR_CF1_RESULTS_20261109.md).
Six published-source development campaigns,60 molecular fits and2,700 fixed
portfolio cells passed, including independent H/D recalculation and complete
private return/exact remote cleanup. Classical group diversification increases
coverage while losing hits; a quota alone does not establish a new method.
Final16 remains sealed and journal readiness is not established. Open the
[EN/TH offline evidence report](research/product_handoffs/lr_cf1_v1/README.md),
[English paper insert](docs/07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md)
and [owner checkpoint](docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md).
Future method/product proposals require a new owner decision.

""" + readme[end:]
    begin, end = readme.index("**Contribution revision proposed:**"), readme.index("**M2 complete / INCONCLUSIVE")
    readme = readme[:begin] + """**Contribution direction evaluated:** the owner-approved
[confirmation-portfolio question](docs/03_research/CONFIRMATION_PORTFOLIO_CONTRIBUTION_PROPOSAL_20261109.md)
now has real baseline evidence. LR-CF1 closes data/endpoint feasibility and
baseline opportunity; **NO_GO for a quota-only method claim**. A distinct
mechanism and independent evaluation remain unresolved. The original proposal's
disabled configuration records its creation time, not the later released study.

""" + readme[end:]
    write("README.md", readme)
    old_handoff = (ROOT / "HANDOFF.md").read_text(encoding="utf-8")
    with (TASK / "handoff-before-final-refresh-v1.md").open("x", encoding="utf-8", newline="\n") as file:
        file.write(old_handoff)
    write("HANDOFF.md", """# Handoff: LR-CF1 complete, owner checkpoint

The authorized LR-CF1 scientific work, independent result verification, full
private return/reread, exact remote cleanup and offline delivery preparation
are complete. Do not relaunch any completed booking or recreate its remote root.
Finish any remaining final audit/main delivery step only; a new research or
product phase needs the owner's next decision.

## Result and entry points

- [Full results](docs/03_research/LR_CF1_RESULTS_20261109.md):6 campaigns,
  1,333,191 retained primary rows,6,896 supported confirmations,60 molecular
  fits,2,700 cells.30 MVS-A original-code score checks and independent local
  recount PASS. All18 arms, five budgets and conditional seed variation retained.
- [Owner checkpoint](docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md):
  NO_GO_QUOTA_ONLY_METHOD_CLAIM. Classical round-robin accounts for the observed
  tradeoff. In all900 such cells D=H by construction: assigned budgets use only
  the first one-per-group pass. No novel selector or independent final test.
- [EN/TH offline report](research/product_handoffs/lr_cf1_v1/README.md):70 views
  browser checked, strict aggregate card/schema and actual screenshots.
- [English paper insert](docs/07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md)
  and [next-method disposition](docs/03_research/LR_CF1_NEXT_METHOD_DISPOSITION_20261109.md).
  No benchmark-paper pivot, journal submission or live integration was started.
- [Evidence index](docs/evidence/lr-cf1-20261109-v1/README.md), including return,
  cleanup, analysis, plots and QA. Final closure audit/budget records are stored
  alongside these artifacts after their actual checks pass.

## Authority, accounting and exposure

Original release9November2026 14:10:48.561842Z; original deadline13November
14:10:48.561842Z. Owner source choice A explicitly resumed the same account;
no clock reset. Owner approved AID/pinned-repository provenance with13/17 SI
alias conflicts retained. Snapshot04c58e85188e724ec5ff44cbed2e7b960f6f3df3.

Retained upper allocation93,088/172,800 CPU seconds, including the full43,200
utility bucket and every failed attempt. It is not measured total CPU.
Scientific models used dr-train up to3 single-core-equivalent workers, each4GiB,
swap0, initial69/70/71 and numerical threads1; local lightweight work CPU0/1GiB.
All six current confirmation campaigns are now **exposed development data**.
No final16 feature, label or performance-presence payload was opened. Old
MF-PCBA/ChEMBL STOPs, old ledgers, protocols, results and conditional96h stay closed.

## Exact private return and deletion

Private root:
`C:\\Users\\User\\Desktop\\myProject\\curaloop-rl\\.local\\lr-cf1-20261109-v1`.
Complete returned files: `remote-return/files/`; original export and manifest:
`remote-return/export/`; proof: `remote-return/verified-v1.json`.

10,655 task files,5,130,006,634 bytes, plus all seven export files returned and
independently reread. Archive1,080,043,143 bytes,
SHA25631bbb0584c5c8785abe7f5a7bf05ee3fb666dc68b2eb62cead480adb5415ad5e.
ManifestSHA2567e849c21012d095ea5d2bbea6162ead4343608f0c4ee7b5a86e1e3eb62649056.
Combined task regular files+archive6,210,049,777 bytes, below8GiB.

Only `/home/chaw/curaloop-tasks/lr-cf1-20261109-v1` and its exact
`-export-v1` sibling were deleted, after complete local verification and2,700-cell
recount. Fresh absence PASS for both. Do not recreate either root. No remote
source/data/model work remains to resume; all relevant tool sessions terminated.

## Technical history and reproducibility

Original failures remain: blocked SI aliases (owner resolved A), four invalid
dense-index assumptions (append-only row-preserving repair), initial dependency
distribution/bootstrap transport, storage forecast and metadata factory stage.
All60 scientific fits passed without retries. Metadata retry reused exact passed
checks in a fresh serial process; concurrent rendered() calls otherwise mutate a
shared bootstrap flag. Any future orchestration must isolate/serialize that
factory. Do not silently rewrite executed source to hide the failure.

Scientific code-v2, author code, feature/rank/cell manifests and source versions
are frozen. First-seed models are reused, not extra observations. Visual-onlyv2
fixed shared-axis clipping with unchanged data;v1 is private history. Raw records,
model files, environments, protected exclusion identities, reading PDFs and
private traces stay outside Git. Public source/aggregates alone are not a full
external row-level reproduction bundle.

## Remaining closure and next actor

If not yet done: run the prepared closure audit, retain its PASS and final closed
budget record, validate local references/whitespace/private boundaries, then
normal main commit/push (already authorized). Do not mark goal complete until
those required steps actually pass. Main's enclosing delivery commit identifies
the shipped version; avoid a self-referential precomputed commit SHA.

After delivery, the next actor is the owner. CF2-Design (2CPUh/24h/local1) and
P-CF1 (4CPUh/48h/max2) are alternatives only, not released goals. No new source,
selector, independent evaluation, final16, paid/GPU, actual team/lab write,
deployment or submission follows automatically. Preserve12 old ledger pins,
58 old scientific pins and17 LR-D23 source pins; the closure audit verifies them.
""")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    title, rest = agents.split("\n", 1)
    write("AGENTS.md", title + "\n\n" + """## LR-CF1 complete; owner checkpoint before any new phase

Read docs/03_research/LR_CF1_RESULTS_20261109.md,
docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md and HANDOFF.md. All60
molecular fits and2,700 cells PASS; independent recount/full private return and
exact owned cleanup/fresh absence PASS. NO_GO_QUOTA_ONLY_METHOD_CLAIM; a new
selector's novelty/potential is not established. All six current confirmations
are exposed development; final16 remains sealed. No new selector, actual
integration, paid/GPU, live team write/deploy or submission was performed.

Finish final audit/budget closure/main delivery if still pending, then stop for
owner decision. Do not relaunch completed units or recreate deleted task/export
roots. Retain93,088/172,800 CPU seconds including full utility bucket and failed
attempts; no unused ceiling releases another phase. Original deadline/account
unchanged. CF2-Design and P-CF1 are proposals only. Parent sole writer. Normal
main commit/push at closeout is explicitly authorized. Earlier active/blocked/
release/proposal markers below are historical and do not override this state.
""" + rest)
    write("docs/06_execution/LR_CF1_EXECUTION_STATUS_20261109.md", """# LR-CF1 completion checkpoint

**SCIENTIFIC_AND_RETURN_WORK_COMPLETE / OWNER_CHECKPOINT.**

The owner-approved study closed data/endpoint feasibility and baseline/portfolio
opportunity. Six published-source campaigns,1,333,191 retained primary rows and
6,896 observation-supported confirmations were admitted. All60 primary-only
molecular fits passed; all30 real MVS-A score checks matched original author
code. The frozen2,700 cells completed and every H/D count was independently
recalculated locally. All18 arms and five budgets remain visible.

The [results](../03_research/LR_CF1_RESULTS_20261109.md) confirm the classical
hit/coverage tradeoff. **NO_GO for a quota-only new-method claim.** Novel-selector
potential and independent journal-level evidence remain unproven. No new
selector, final16 access or actual product integration occurred.

## Source and resources

Owner A resolved13/17 conflicting SI/repository aliases using canonical numeric
AID pairs and pinned repository provenance. Snapshot
04c58e85188e724ec5ff44cbed2e7b960f6f3df3; six whole files77,576,150 bytes and
1,341,881 source primary rows authenticated. Four source-provider blocks and one
historical annotation component do not establish independent biological families.
Source0 includes inactive/inconclusive; unobserved confirmation is never imputed.

Original release9November14:10:48.561842Z and deadline13November14:10:48.561842Z
never reset. Conservative retained allocation93,088/172,800 CPU seconds, including
43,200 utility,8,460 admission,37,228 features/baselines,1,080 portfolio and3,120
technical reserve. This upper allocation is not actual total consumption.
Measured model-fit-handler CPU and separate costs appear in the results/audit.

Original-version CPU-only native runtime, lossless feature storage, real kernel
proofs and fixed-core waves passed. Index gaps, initial transport/distribution,
storage forecast and metadata-stage issues were resolved without model/data/
outcome-based substitutions. Failed attempts remain retained. See the
[calibration note](LR_CF1_CALIBRATION_EXECUTION_20261109.md) and evidence index.

## Return and delivery

All10,655 task files and seven export files returned and independently reread.
Task regular files5,130,006,634 bytes; archive1,080,043,143 bytes; total6,210,049,777
bytes below8GiB. After local verification and independent2,700-cell recount,
exact owned task/export deletion and fresh absence passed. No remote science
remains active. Raw records/environment/models/traces remain private locally.

The [EN/TH offline package](../../research/product_handoffs/lr_cf1_v1/README.md)
has70 checked views, strict schema and actual screenshots. The
[English paper insert](../07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md)
is a draft, not a submission. Current public reproduction is limited by withheld
raw records/exclusion identities. Final preservation/budget closure and normal
main delivery are the last bookkeeping checks, documented in the evidence index.

Read the [owner checkpoint](LR_CF1_OWNER_CHECKPOINT_20261109.md) before another
phase. CF2-Design/P-CF1 are proposed alternatives; no unused account or old
conditional grant activates them. Earlier blocked/wait records are creation-time
history in their separate handoff/receipts, not current blockers.
""")
    write("docs/evidence/lr-cf1-20261109-v1/README.md", """# LR-CF1 evidence index

**Complete baseline feasibility; NO_GO for a quota-only new-method claim.**
[Results](../../03_research/LR_CF1_RESULTS_20261109.md) ·
[Owner checkpoint](../../06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md) ·
[EN/TH offline report](../../../research/product_handoffs/lr_cf1_v1/README.md).

## Source, admission and fixed controls

| Evidence | Actual scope |
| :--- | :--- |
| [Owner source choice A](../../../research/manifests/lr_cf1_source_a_owner_20261109_v1.json) | AID/repository provenance; SI alias conflicts retained |
| [SI concordance](si-concordance-v2.json) | Same17 AID pairs;13 conflicting names; source correction not guessed |
| [Metadata admission](metadata-admission-v1.json) | Six whole campaigns chosen by numeric AID before outcomes |
| [Opaque intake](opaque-intake-v1.json) |77,576,150 bytes; Git-blob/SHA authentication |
| [Blinded support](blinded-support-v1.json) | Structure/role exclusions and observation presence before C values |
| [Source feature manifests](feature-manifests-v1.json) | Original fingerprints and fixed groups; no confirmation values |
| [Cost release v2](complete-matrix-cost-release-v2.json) | Full48 remaining fits/2,700 cells inside original limits |
| [Opaque compression calibration](storage-compression-calibration-v1.json) | Measured storage forecast; no label parsing or archive |
| [All-six primary checks](primary-score-validation-v1.json) | Primary Score and common operator integrity |
| [Metadata-stage repair](metadata-stage-repair-v2.json) | Retained failure, terminal/target absence and serial exact retry |
| [Rank manifests](rank-manifests-v1.json) |60 molecular models, primary-only; GBM reuses MVS model |
| [Frozen cell matrix](cell-manifest-v1.json) | Exact2,700 cells frozen before C values |
| [Evaluator release](evaluation-release-v1.json) | After baseline/resource/readiness gates; development only |

## Results and uncertainty

- [All2,700 cells](portfolio-cells-v1.csv).
- [Campaign means/ranges/SD](campaign-summary-v1.csv).
- [Equal-campaign descriptive summaries](equal-campaign-summary-v1.csv).
- [Provider summaries](provider-summary-v1.csv); four providers are not biological independence.
- [Paired seed contrasts](paired-contrasts-v1.csv), including losses.
- [Mean-point frontiers](campaign-mean-frontiers-v1.csv) and [per-seed frontiers](campaign-seed-frontiers-v1.csv).
- [Independent summary](results-summary-v1.json) and [interpretation](interpretation-v1.json).
- Hit curves: [PNG](figures/hits-budget-curves-v2.png), [SVG](figures/hits-budget-curves-v2.svg), [PDF](figures/hits-budget-curves-v2.pdf).
- Group curves: [PNG](figures/groups-budget-curves-v2.png), [SVG](figures/groups-budget-curves-v2.svg), [PDF](figures/groups-budget-curves-v2.pdf).

Five-seed ranges describe conditional algorithm/tie variation, not a biological
population interval. Round-robin D=H in all900 assigned cells is mechanical:
these budgets take one candidate per group. No outcome-selected primary budget,
meaningful-effect margin or model/tuning substitution was introduced.

## Offline report, return and quality

- [Card generation/schema checks](offline-product-validation-v1.json).
- [Completed browser/visual QA](delivery-qa-v1.json):70 views, all18 arms,
  desktop EN/TH and mobile TH; full screen-reader/other-browser review NOT_RUN.
- Screenshots: [EN desktop](offline-report-desktop-en-v1.png), [TH desktop](offline-report-desktop-th-v1.png), [TH mobile](offline-report-mobile-th-v1.png).
- [Complete private return/reread](complete-return-verified-v1.json):10,655 files plus seven export files.
- [Exact owned deletion](scoped-delete-v1.json) and [fresh absence](fresh-absence-v1.json).
- Final `closure-audit-v1.json` and `budget-closeout-v1.json` are produced only
  after the actual preservation/source/role/budget checks pass.

Raw records, compound identities, protected exclusion metadata, reading PDFs,
models/environments, transport permits and private traces stay outside Git.
Source/aggregate publication does not constitute a fully public row-level
reproduction bundle or commercial-data clearance. No new selector or submission.

## Earlier preparation snapshots

The [initial pending card](offline-handoff-v1.json), [source-choice pending card](offline-handoff-v2.json),
[preparation checks](preparation-quality-v3.json), [source probes](source-behavior-review-v2.json)
and [predecision preservation](predecision-checkpoint-v1.json) describe their
creation time. Null metrics there mean unrun then; they do not override the
completed study or reopen earlier blockers/accounts.
""")
    new(PUBLIC / "visual-preflight-v1.json", {"status": "PASS_VECTOR_PREFLIGHT_AND_RENDERED_QA",
        "utc": now().isoformat(), "hits_svg_size_mm": [178,145], "groups_pdf_size_mm": [178,145],
        "svg_detected_font_sizes_pt": [8.0,8.5,8.8,10.2], "embedded_raster_images": 0,
        "warning": "8.00pt boundary warning in SVG preflight; actual final-size labels inspected and legible",
        "rendered_v2_clipping_and_grayscale_check": "PASS", "scientific_values_changed": False})
    new(PUBLIC / "current-document-refresh-v1.json", {"status": "PASS_CURRENT_STATUS_REFRESH",
        "utc": now().isoformat(), "historical_scientific_records_changed": False,
        "previous_handoff_private_sha256": sha(TASK / "handoff-before-final-refresh-v1.md")})
    print("PASS current root documents, execution status, handoff and evidence index refreshed")


if __name__ == "__main__":
    guard = start("current-document-refresh-v1", 180, 600, bucket="utilities_return_handoff_delivery")
    try:
        main()
        finish("current-document-refresh-v1", guard, "PASS_CURRENT_DOCUMENT_REFRESH")
    except BaseException:
        finish("current-document-refresh-v1", guard, "FAIL")
        raise
