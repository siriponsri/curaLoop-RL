"""Write source-grounded CF1 results, reviewer position and owner checkpoint."""
# ruff: noqa: E402

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, now, read, sha, start

RANKERS = ("random", "primary_score", "mvsa", "gbm", "rf", "nearest_primary")
OPERATORS = ("top_ranked", "cluster_round_robin", "classical_max_min")
NAMES = {"random": "Random", "primary_score": "Primary Score", "mvsa": "MVS-A", "gbm": "GBM", "rf": "RF", "nearest_primary": "Nearest primary hit"}
OPNAMES = {"top_ranked": "Top-ranked", "cluster_round_robin": "Group round-robin", "classical_max_min": "Classical max-min"}


def document(name, body):
    path = ROOT / name
    with path.open("x", encoding="utf-8", newline="\n") as file:
        file.write(body.rstrip() + "\n")


def main():
    data = read(PUBLIC / "results-summary-v1.json")
    assert data["status"] == "PASS_INDEPENDENT_AGGREGATE_RECALCULATION"
    assert read(PUBLIC / "fresh-absence-v1.json")["status"] == "PASS_FRESH_EXACT_ABSENCE"
    rows, campaigns = data["equal_campaign_summary"], data["campaigns"]
    index = {(r["budget_percent"], r["ranker"], r["operator"]): r for r in rows}
    top, rr = index[(10, "mvsa", "top_ranked")], index[(10, "mvsa", "cluster_round_robin")]
    dh = rr["confirmed_positives_mean"] - top["confirmed_positives_mean"]
    dd = rr["positive_structure_groups_mean"] - top["positive_structure_groups_mean"]
    dfp = rr["positive_fingerprint_groups_mean"] - top["positive_fingerprint_groups_mean"]
    with (PUBLIC / "portfolio-cells-v1.csv").open(newline="") as file:
        cells = list(csv.DictReader(file))
    quota = [r for r in cells if r["operator"] == "cluster_round_robin"]
    assert len(quota) == 900 and all(r["confirmed_positives"] == r["positive_structure_groups"] for r in quota)
    assert all(max(r["budgets"]) < r["murcko_or_fallback_groups"] for r in campaigns)
    value = {"status": "TRADEOFF_CONFIRMED_NOVEL_SELECTOR_POTENTIAL_UNPROVEN",
        "method_claim_disposition": "NO_GO_QUOTA_ONLY_METHOD_CLAIM", "publication_ready": False,
        "source_summary_sha256": sha(PUBLIC / "results-summary-v1.json"),
        "predeclared_reading_example_budget_percent": 10,
        "mvsa_group_round_robin_minus_top": {"mean_hit_difference": dh, "mean_group_difference": dd,
            "mean_fingerprint_group_difference": dfp, "hit_relative_change_percent": 100 * dh / top["confirmed_positives_mean"],
            "group_relative_change_percent": 100 * dd / top["positive_structure_groups_mean"]},
        "all_900_round_robin_cells_have_D_equal_H_by_construction": True,
        "no_second_group_pass_at_assigned_budgets": True, "owner_review_before_new_method": True}
    new(PUBLIC / "interpretation-v1.json", value)
    cohort_rows = []
    for c in campaigns:
        budgets = ", ".join(map(str, c["budgets"]))
        cohort_rows.append(f"| {c['campaign']} | {c['retained_primary_rows']:,} | {c['universe_size']:,} | {c['source_confirmed_positive_count']:,} | {c['source_positive_structure_groups']:,} | {budgets} |")
    cohort = "\n".join(cohort_rows)
    table = []
    for ranker in RANKERS:
        for operator in OPERATORS:
            r = index[(10, ranker, operator)]
            table.append(f"| {NAMES[ranker]} | {OPNAMES[operator]} | {r['confirmed_positives_mean']:.2f} [{r['confirmed_positives_min']:.2f}, {r['confirmed_positives_max']:.2f}] | {r['positive_structure_groups_mean']:.2f} [{r['positive_structure_groups_min']:.2f}, {r['positive_structure_groups_max']:.2f}] | {r['positive_fingerprint_groups_mean']:.2f} |")
    budget_rows = []
    for b in (1, 2, 5, 10, 20):
        a, z = index[(b, "mvsa", "top_ranked")], index[(b, "mvsa", "cluster_round_robin")]
        budget_rows.append(f"| {b}% | {a['confirmed_positives_mean']:.2f} | {a['positive_structure_groups_mean']:.2f} | {z['confirmed_positives_mean']:.2f} | {z['positive_structure_groups_mean']:.2f} | {z['confirmed_positives_mean']-a['confirmed_positives_mean']:+.2f} | {z['positive_structure_groups_mean']-a['positive_structure_groups_mean']:+.2f} |")
    fit_seconds = sum(read(p)["whole_cgroup_cpu_seconds_at_result"] for pattern in ("first-seed-*/result.json", "matrix-fit-*/result.json") for p in (TASK / "jobs").glob(pattern))
    returned = read(TASK / "remote-return/verified-v1.json")
    ledger = read(TASK / "ledger.json")
    retained = sum(ledger["retained_seconds"].values())
    result = f"""# LR-CF1: real-source confirmation portfolios

**Data/endpoint feasibility and baseline opportunity are complete.** All 60
molecular fits and 2,700 fixed comparison cells passed. Independent local
recalculation matches every H/D cell. The result confirms a hit/coverage tradeoff
already attainable with classical controls. **NO_GO for a quota-only new-method
claim; novel-selector potential remains unproven.** This is not an independent
final study or a submission-ready paper.

## What was actually run

Six whole AIC_Finder campaigns were selected by numeric AID before outcomes from
snapshot `04c58e85188e724ec5ff44cbed2e7b960f6f3df3`. Source intake was 77,576,150
bytes and 1,341,881 assay-specific primary rows. After protected exact-structure,
invalid/duplicate exclusions, 1,333,191 primary rows and 6,896 observed primary-hit
confirmations remained. These are observations, not unique cross-assay molecules.
All six campaigns are now exposed development data.

| Primary/confirmation AID | Retained primary rows | Supported U | Source positives in U | Positive groups in U | Actual B at 1/2/5/10/20% |
| :--- | ---: | ---: | ---: | ---: | :--- |
{cohort}

There are four provider blocks and one historical annotation-connected component,
not six certified independent biological families. Source 0 combines inactive
and inconclusive; missing confirmation is excluded, never imputed. The source
totals are 3,050 positive assay-specific observations and 2,436 within-campaign
positive groups. Their sums do not identify globally unique molecules/groups.

Thirty MVS-A and thirty RF models use primary labels only. GBM probabilities
reuse MVS-A's model. Random, Primary Score and nearest-primary controls add no
fit. All six rankers receive top-ranked, group round-robin and classical max-min
at five fixed budgets and five seeds. All 18 nominal arms, redundant controls
and unfavorable cells remain in the [complete CSV](../evidence/lr-cf1-20261109-v1/portfolio-cells-v1.csv).
Original author score/checkpoint/leaf-loop conventions and core package versions
are retained; all 30 real MVS-A score recalculations pass the declared tolerance.

## Descriptive result at the predeclared 10% reading example

Every campaign has equal weight. H is source-positive hits; D is positive Murcko/
acyclic-fallback groups. Brackets are the observed range across five conditional
seeds, **not biological-population confidence intervals**. D(FP) uses the frozen
fingerprint grouping. Actual confirmation counts are 164/119/22/89/178/120.

| Ranker | Operator | Mean H [seed range] | Mean D [seed range] | Mean D(FP) |
| :--- | :--- | ---: | ---: | ---: |
{chr(10).join(table)}

For the predeclared MVS-A anchor, round-robin changes mean H from
{top['confirmed_positives_mean']:.2f} to {rr['confirmed_positives_mean']:.2f}
({dh:+.2f}; {value['mvsa_group_round_robin_minus_top']['hit_relative_change_percent']:+.2f}%)
and mean D from {top['positive_structure_groups_mean']:.2f} to
{rr['positive_structure_groups_mean']:.2f} ({dd:+.2f};
{value['mvsa_group_round_robin_minus_top']['group_relative_change_percent']:+.2f}%).
The fingerprint sensitivity also increases, from
{top['positive_fingerprint_groups_mean']:.2f} to {rr['positive_fingerprint_groups_mean']:.2f},
but the magnitude depends on the group definition. These are descriptive
development effects, without a post-result meaningful-effect threshold.

## All five budgets, same MVS-A anchor

| Nominal budget | Top H | Top D | Round-robin H | Round-robin D | H difference | D difference |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(budget_rows)}

The direction is consistent here: more confirmed groups, fewer confirmed
compounds. Ranker ordering varies with budget and metric; there is no universal
best-model claim. Paired campaign/seed contrasts and all provider summaries are
available in the evidence index, including unfavorable effects.

![All rankers: hit recovery](../evidence/lr-cf1-20261109-v1/figures/hits-budget-curves-v2.png)

![All rankers: positive structural coverage](../evidence/lr-cf1-20261109-v1/figures/groups-budget-curves-v2.png)

## Why this is not a new method result

Every assigned B is smaller than the available number of structure groups.
Consequently, round-robin takes only its first pass: one candidate per group.
All 900 round-robin cells therefore have D=H by construction. This is a property
of the operator and budget range, not two independent empirical successes.
Learned primary rankers combined with that classical quota account for the
observed tradeoff. Max-min alone often loses relevance; beating it alone would
not establish novelty. MVS-A's paper already discusses diversity and hybrid
selection, so the next claim cannot be merely ranking plus a scaffold quota.

**Recommendation:** do not fund a new selector on this quota-only contribution.
The problem is measurable; a distinct mechanism that improves on the strongest
shared diversified controls has not been established. A different mechanism
would require its own literature/identifiability review, frozen design and owner
approval. No novel selector or RL controller was trained in LR-CF1.

## Resource and return evidence

The retained upper allocation is {retained:,}/172,800 CPU seconds
({retained/3600:.3f}/48 hours), including the full 43,200-second utility bucket
and every failed attempt. This is not measured total CPU. Measured whole-cgroup
CPU at result for the 60 molecular fits is {fit_seconds:,.3f} seconds
({fit_seconds/3600:.3f} hours); setup, features, selection and utilities are
separate. The closure audit gives handler-level measurements and their scope.
The original deadline was never reset.

All {returned['file_count']:,} task files ({returned['total_bytes']:,} bytes) and
seven export files returned locally, were SHA-256 checked and independently
reread before exact task/export cleanup. The archive is {returned['archive_bytes']:,}
bytes. Combined owned regular files plus archive are 6,210,049,777 bytes, below
8GiB. Fresh exact remote absence passed. Raw data, environments, models and
private traces remain in `.local/lr-cf1-20261109-v1/remote-return/`, outside Git.

## Resolved technical issues and remaining scientific limits

- SI/repository codenames conflict in 13/17 pairs. The owner approved numeric AID
  plus repository provenance; aliases remain recorded. This is qualified
  processed-repository reproduction, not raw-assay/all-paper-table equivalence.
- Four stored CSV indices contain legitimate gaps. The initial dense-index
  assumption failed; append-only repairs retained every eligible original row.
- A conservative storage forecast stopped before remaining fits. Measured opaque
  gzip sizing showed the unchanged matrix and complete return fit the8GiB cap.
- Concurrent worker rendering leaked a bootstrap type flag into a metadata-only
  stage. A terminal/target-absence check and fresh serial stage repaired it,
  without refits, changed cells or premature confirmation analysis.
- Visual QA caught first-render shared-axis clipping at20%; v2 restores all
  endpoints with unchanged data. The first render/source remain private history.
- The six development campaigns are exposed, dependence remains, and the
  historical observation process limits whole-library interpretation. Final16
  remains sealed and is not automatically a matching confirmation test panel.
- Raw records and the protected exclusion index remain private. The public code
  and aggregates are not a complete external row-level reproduction bundle.

## Product and journal position

The [EN/TH offline evidence report](../../research/product_handoffs/lr_cf1_v1/report.html)
and strict card are complete; 70 language/campaign/budget views were browser
checked. This is separate from the live engine and contains no individual assay
rows. It provides a useful internal evidence/decision artifact, without a
customer workflow, commercial-data clearance or ROI evaluation.

The [English paper insert](../07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md)
is a methods/results draft. As a reviewer, I would request a distinct method,
stronger independent evaluation and a cleared reproduction plan before a
method-first journal submission. The current package does not establish novel
algorithmic contribution, independent biological generalization or publication
readiness. No benchmark-paper pivot or journal submission is initiated.

Read the [owner checkpoint](../06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md)
and [next-method disposition](LR_CF1_NEXT_METHOD_DISPOSITION_20261109.md) before
any new training, source intake or evaluation phase.
"""
    document("docs/03_research/LR_CF1_RESULTS_20261109.md", result)
    document("docs/03_research/LR_CF1_NEXT_METHOD_DISPOSITION_20261109.md", """# LR-CF1 next-method disposition

**NO_GO_QUOTA_ONLY_METHOD_CLAIM. No new method is released.**

The fixed controls demonstrate a real H/D tradeoff. At these budgets, ranked
group round-robin is a one-per-group quota; all900 cells satisfy D=H mechanically.
That is useful baseline evidence and already aligns with the published diversity
discussion. It is insufficient to call a new selector novel. There is no basis
to escalate directly to another large training run or claim journal readiness.

One possible question for a separately approved critical design review is whether
primary-to-confirmation error and within-group outcome dependence provide useful
decision information beyond fixed ranks, a group quota and classical expected-
coverage optimization. A learned confirmatory probability, weighted coverage
objective or constrained greedy solver alone is not presumed new. Active search,
probabilistic coverage and group-aware optimization must be checked as prior work.
This is an unverified hypothesis, not an implemented algorithm or a promise of
advantage. The current results do not prove that this mechanism is needed.

If the owner retains a method-first journal objective, propose one bounded
**CF2-Design** review: 2 CPU-hours /24 elapsed hours /local1CPU/1GiB, at most two
mechanism hypotheses and one final design ticket. Use existing source/aggregate
evidence, constructed examples and primary literature only; no new dataset rows,
extra activity/final outcomes, molecular fits, SSH science, paid service or GPU.
Deliver a novelty comparison against ranked quotas, expected coverage and active
search; an identifiable information contract; mandatory strong controls; a
separately costed evaluation design; and a decisive GO/NO_GO recommendation.
If no distinct defensible mechanism remains after that single review, recommend
ending this algorithm line rather than adding another review/training cycle.
No automatic training or independent evaluation follows that proposed review.

An alternative product-first proposal is an internal **P-CF1** adapter pilot:
4 CPU-hours /48 elapsed hours /max2 workers, local1 plus optional dr-train1.
It would connect aggregate evidence to an explicitly separate local research
view, preserve EN/TH and source hashes, test visibility boundaries and capture
the actual interface. No raw CF1 compound import, live laboratory/team write,
commercial-data claim, paid API, GPU or journal action. Research novelty would
remain unestablished; product usefulness would need its own bounded workflow
evaluation. This is proposed, not implemented or owner-released.

Both choices are new accounts, not use of LR-CF1's unused ceiling. The owner must
choose the objective before either starts. All six confirmation campaigns are
now exposed development data. A later independent confirmation panel needs
separate source/role/support admission; the old final16 grant stays inactive.
""")
    document("docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md", f"""# LR-CF1 owner checkpoint

**Complete:** data/endpoint feasibility and baseline/portfolio opportunity.
**Research recommendation:** NO_GO for a quota-only new-method claim.

The study used6 admitted campaigns,1,333,191 retained primary observations,
6,896 observed primary-hit confirmations,60 molecular fits and2,700 fixed cells.
All30 real MVS-A score checks and independent H/D recalculation passed. No
new selector, final16 access, live integration or submission occurred.

At the predeclared10% reading example, MVS-A group round-robin changes mean
hits75.13->65.13 and positive groups45.37->65.13. It gives more coverage while
losing hits. Fixed classical controls already explain this tradeoff; a quota
alone is not the requested publishable method contribution. All18 arms and all
five budgets, ranges and unfavorable campaign effects are retained in the
[full results](../03_research/LR_CF1_RESULTS_20261109.md).

The [EN/TH report](../../research/product_handoffs/lr_cf1_v1/report.html) is an
offline artifact, not integration with the live product. The
[English paper insert](../07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md)
is a draft. Reviewer position: data/baseline feasibility PASS; methodological
novelty NOT_ESTABLISHED; independent confirmation evaluation NOT_RUN; public
row-level reproduction NOT_READY; journal submission NOT_READY.

All10,655 task files and seven export files were returned/reread before exact
remote cleanup and fresh absence. Conservative retained allocation is
{retained:,}/172,800 CPU seconds, including full utility reserves. All old
ledgers/scientific pins remain subject to the final preservation audit. No
unused allowance activates a future phase. Main delivery is authorized.

## Decision needed before the next phase

Recommended if a method-first journal remains the priority: **CF2-Design**, one
critical design review,2 CPU-hours/24h/local1CPU/1GiB, maximum2 hypotheses and
one final GO/NO_GO design ticket. No new rows, outcomes or molecular training.
The review must distinguish a mechanism from ranked quotas, learned-probability
coverage and established active search. If it cannot, end this algorithm line.

Alternative: **P-CF1**, an internal aggregate adapter/product pilot,
4 CPU-hours/48h/max2 workers (local1+optionaldr-train1). No raw compound import,
live team/lab writes, paid service, GPU or journal submission. A product benefit
requires separate workflow evaluation and does not establish algorithm novelty.

The [detailed disposition](../03_research/LR_CF1_NEXT_METHOD_DISPOSITION_20261109.md)
specifies both proposals. Neither is released. The owner can also stop here and
retain the evidence. No new goal starts automatically.
""")
    paper = ROOT / "docs/07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md"
    text = paper.read_text(encoding="utf-8")
    pending = "**Pending evaluator completion and independent aggregate audit.** A constructed\ntest, source metadata admission or successful feature job is not an efficacy\nresult. Replace this paragraph only with verified aggregate evidence."
    assert pending in text
    text = text.replace(pending, f"""All60 molecular fits and2,700 frozen portfolio cells completed. Independent
local recalculation reproduced every integer H/D result. At the predeclared10%
reading example, MVS-A top-ranked achieved H75.13 and D45.37, whereas ranked group
round-robin achieved H65.13 and D65.13: -10.00 hits and +19.77 groups, descriptively
-13.31% and +43.57%. Fingerprint-group coverage changed44.30->56.57. Equal
campaign weighting and five conditional seeds were retained; this is not a
population interval or a new-method comparison. All18 arms, all budgets and
campaign effects are available in [the results/evidence package](../03_research/LR_CF1_RESULTS_20261109.md).

At every assigned budget, the available group count exceeded B. Thus round-robin
used its first pass only and D=H in all900 such cells by construction. The
coverage improvement and hit loss demonstrate an already-classical tradeoff;
they do not establish a novel selector. No new model selection, threshold tuning
or training followed confirmation exposure. Recommendation: NO_GO for a
quota-only method claim; separately review any distinct mechanism before funding
another training study. Final16 remains sealed.

Measured whole-cgroup CPU at result for60 molecular fits was {fit_seconds:,.3f}s;
this excludes other scientific/setup/return utilities. Conservative retained
allocation, including every failure and the full utility bucket, was
{retained:,}/172,800s. Complete private return of10,655 task files plus seven
export files, independent disk reread and exact owned cleanup/fresh absence
passed. The public package includes aggregate CSVs and vector figures; raw rows,
private traces and the protected exclusion index are retained locally.
""")
    paper.write_text(text, encoding="utf-8", newline="\n")
    handoff = ROOT / "research/product_handoffs/lr_cf1_v1"
    document("research/product_handoffs/lr_cf1_v1/README.md", """# LR-CF1 offline confirmation evidence

Open [report.html](report.html) locally in a browser. The self-contained report
switches EN/TH and covers7 campaign views (six individually plus equal-weight
summary), five budgets and all18 arms. On a small screen, scroll the result table
horizontally. The10% default is a descriptive reading example, not a primary
endpoint selected for performance. The report does not activate a live policy.

- [Evidence card](evidence-card-v1.json), including actual source totals and scope.
- [Strict JSON schema](evidence-card.schema.json); private-field injections fail.
- [All2,700 aggregate cells](../../../docs/evidence/lr-cf1-20261109-v1/portfolio-cells-v1.csv).
- [Study results](../../../docs/03_research/LR_CF1_RESULTS_20261109.md).
- [Screen mapping/contract](../../../docs/05_product/LR_CF1_OFFLINE_HANDOFF_CONTRACT_20261109.md).
- [Browser and visual QA](../../../docs/evidence/lr-cf1-20261109-v1/delivery-qa-v1.json).

FEASIBILITY_COMPLETE means this baseline study completed. It does not establish
a new algorithm, independent final evaluation, commercial-data rights or journal
readiness. All six campaigns are exposed development data. Missing confirmation
is outside U; source0 includes inactive/inconclusive. H=D for round-robin at these
budgets is a one-per-group operator property. Seed ranges are conditional, not
biological-population intervals. Individual structures/labels are absent.
""")
    assert handoff.exists()
    screenshots = ["offline-report-" + name + "-v1.png" for name in ("desktop-en", "desktop-th", "mobile-th")]
    new(PUBLIC / "delivery-qa-v1.json", {"status": "PASS_OFFLINE_REPORT_AND_FINAL_FIGURE_QA", "utc": now().isoformat(),
        "browser": {"engine": "Playwright Chromium", "language_campaign_budget_views": 70, "arms_per_view": 18,
            "missing_or_NaN_cells": 0, "desktop_viewport": [1440,1080], "mobile_viewport": [390,844],
            "mobile_document_overflow": False, "mobile_table_internal_scroll": True,
            "csv_http_status": 200, "csv_rows_excluding_header": 2700, "private_route_test_status": 404,
            "application_javascript_errors_observed": 0,
            "console_http_404_notes": "favicon not provided; deliberately blocked private route. Both distinct from application JS failures.",
            "file_protocol_blocked_by_tool": True, "fallback": "Temporary allowlisted loopback aggregate preview, now closed",
            "full_screen_reader_and_other_browsers": "NOT_RUN"},
        "screenshots": {n: sha(PUBLIC / n) for n in screenshots},
        "figures": {"current_version": 2, "forms": "six ranker facets, three common operators, fixed-budget curves",
            "final_dimensions_mm": [178,145], "minimum_text_pt": 8,
            "final_size_color_and_grayscale_inspected": True, "all_20_percent_endpoints_visible": True,
            "v1_shared_axis_clipping_caught_and_preserved_privately": True,
            "data_changed_in_visual_correction": False,
            "references": ["OAI-VIS-013", "OAI-VIS-011", "OAI-VIS-080", "OAI-VIS-082", "OAI-VIS-008"],
            "formats": ["SVG", "PDF", "PNG"], "palette": "owner-preferred burgundy plus neutral line/marker encodings"},
        "actual_live_product_integration": False})
    new(PUBLIC / "documentation-delivery-v1.json", {"status": "PASS_SOURCE_GROUNDED_DOCUMENT_GENERATION",
        "utc": now().isoformat(), "results_sha256": sha(ROOT / "docs/03_research/LR_CF1_RESULTS_20261109.md"),
        "paper_insert_sha256": sha(paper), "interpretation": value["method_claim_disposition"]})
    print(json.dumps({"status": "PASS_RESULTS_OWNER_PAPER_PRODUCT_DOCUMENTS", "fit_cpu_seconds": fit_seconds,
        "retained_seconds": retained, "interpretation": value["method_claim_disposition"]}, indent=2))


if __name__ == "__main__":
    guard = start("source-grounded-closeout-documents-v1", 180, 600, bucket="utilities_return_handoff_delivery")
    try:
        main()
        finish("source-grounded-closeout-documents-v1", guard, "PASS_SOURCE_GROUNDED_DOCUMENTS")
    except BaseException:
        finish("source-grounded-closeout-documents-v1", guard, "FAIL")
        raise
