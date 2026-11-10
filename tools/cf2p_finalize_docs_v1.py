"""Write current navigation and truthful review receipts for the owner checkpoint."""

from cf2p_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write


def main():
    current = """**Current: LR-CF2P complete; owner checkpoint before another phase.**
CF2-Design is **NO_GO_THIS_MECHANISM** after two formulations and 12 constructed
cases. P-CF1 is **PASS_INTERNAL_INTEGRATION**: actual main-app EN/TH comparison,
strict aggregate API, additive local C Workspace tools, filtered exports,
70 served-build views and a six-page English PDF addendum. No molecular fit,
private CF1 row or final16 was opened. Journal readiness is **NOT_READY**.

Read the [owner checkpoint](docs/06_execution/LR_CF2P_OWNER_CHECKPOINT_20261110.md),
[full phase status](docs/06_execution/PROJECT_PHASE_STATUS_20261110.md),
[integration guide](docs/05_product/CF1_INTEGRATION_GUIDE_20261110.md) and
[acceptance/closure evidence](docs/evidence/lr-cf2p-20261110-v1/README.md).
The current design decision and internal integration close F1 and F4 of the
eight-package roadmap. Six conditional packages remain; none starts automatically.
Next actor: owner reviews product-workflow evaluation or a different specific
research direction. A benchmark-publication pivot is not the selected fallback.

"""
    for name in ("START_HERE.md", "GOAL.md", "PLAN.md"):
        path = ROOT / name
        old = path.read_text(encoding="utf-8")
        title = old.splitlines()[0]
        history = old[old.index("## Historical checkpoints"):]
        path.write_text(title + "\n\n" + current + history, encoding="utf-8", newline="\n")
    path = ROOT / "HANDOFF.md"
    old = path.read_text(encoding="utf-8")
    history = old[old.index("## Completed LR-CF1 checkpoint"):]
    path.write_text("# Handoff: LR-CF2P owner checkpoint\n\n" + current + """## Exact continuation boundary

Working checkout: `C:\\Users\\User\\Desktop\\myProject\\curaloop-rl`, branch main.
Fresh local namespace: `.local/lr-cf2p-20261110-v1`. Release base is
`ebf5c5be06e8b2a84c50d9d2f83e6d06f6558b60`. The enclosing main delivery commit
identifies this checkpoint; verify HEAD, origin/main and the final owner report
before continuing. Finish only pending delivery if any; do not relaunch completed
bookings, recreate deleted old roots, reuse an old budget or run another design loop.

Original release `2026-11-09T22:54:26+00:00`, deadline
`2026-11-10T08:54:26+00:00` (15:54:26 Bangkok). Fresh maximum 8 CPU-hours,
10 elapsed hours, max two combined workers; the actual work succeeded locally
on one CPU / aggregate 1 GiB. No remote task/upload/export was created. Read-only
SSH absence is recorded; new remote return/deletion is not applicable. Prior CF1
private return and exact deletion remain intact. Closed budget and preservation
receipts are in the current evidence index; all failed reservations are retained.

Key current files: shared adapter `src/curaloop_rd/confirmation_study.py`, API
`api/main.py`, main page `frontend/src/pages/Confirmation.tsx`, local tools
`confirmation_workspace_v3.py` / `confirmation_mcp_v3.py`, and tests
`tests/test_confirmation_study.py` / `frontend/src/confirmation.test.tsx`.
Current build/browser v5 are final. Manual uses actual v4 Confirmation captures
with unchanged page component/layout; final navigation additionally allows the
explicit empty-state Scenario builder. All 22 Python/API and 26 frontend checks
pass; browser verifies all 70 numerical views. Old full manual v3 is preserved.

Public evidence contains versioned failures as well as passes. Browser v1's port
was rejected by the original origin policy; v3 caught Thai SVG-label overflow.
The first PDF had one clipped heading; generation v2 and visual review supersede
it. Initial lint findings were unused/import-format issues, repaired within scope.
Do not remove failed charges or describe these as failed scientific fits.
There were no new fits in this phase. Existing FastAPI TestClient emits one
dependency deprecation warning; the regression tests pass.

Research disposition: one ticket, NO_GO for two generic mechanisms, not all
confirmation research. Expected coverage and Bayesian feedback have close prior
work; current aggregates cannot identify the proposed joint/adaptive signal.
No independent scientific or user reviewer was invented. All six CF1 campaigns
stay exposed development in one annotation-connected component. Final16,
historical scientific pins/STOPs and inactive conditional96h grant stay closed.
No paid/GPU/live external writes/deployment/submission occurred.

Acceptance gaps: representative-researcher workflow evaluation, chosen live
connector, commercial-data basis, deployment/customer pilot, distinct molecular
method, independent confirmation population, complete journal manuscript and
submission authority. Recommended next discussion is F5 protocol design, not an
automatic F2 training cycle. Owner chooses the next scope and fresh budget.

## Historical CF1 handoff

The material below is preserved at its earlier checkpoint; its old future-task
wording does not supersede the current P-CF1 integration above.

""" + history, encoding="utf-8", newline="\n")
    path = ROOT / "docs/06_execution/PROJECT_PHASE_STATUS_20261110.md"
    text = path.read_text(encoding="utf-8")
    start, end = text.index("Date:"), text.index("## How to read the status")
    text = text[:start] + """Date: 10 November 2026, Asia/Bangkok. Updated after executing the owner-approved
LR-CF2P proposal based on `ebf5c5b`. Status: **COMPLETE_FOR_OWNER_REVIEW**.
CF2-Design is NO_GO_THIS_MECHANISM; P-CF1 is PASS_INTERNAL_INTEGRATION.
[Current owner checkpoint](LR_CF2P_OWNER_CHECKPOINT_20261110.md).

""" + text[end:]
    text = text.replace("The records linked below were inspected in this planning turn; their historical\ntests were not rerun.", "Historical tests below were not rerun wholesale. Current CF2P engineering\nacceptance is separately executed and linked in the current checkpoint.")
    text = text.replace("current manual v3 and actual browser evidence delivered; CF1 not integrated", "manual v3 and actual browser evidence delivered; later P-CF1 integration below")
    text = text.replace("OFFLINE_HANDOFF_COMPLETE; runtime adapter NOT_RUN; complete submission manuscript and independent evaluation NOT_READY", "OFFLINE_HANDOFF_COMPLETE; subsequent runtime adapter completed in P-CF1; manuscript and independent evaluation NOT_READY")
    text = text.replace("## Remaining roadmap: eight work packages, two proposed now", "## Roadmap: two packages closed here, six conditional packages remain")
    text = text.replace("Only\nCF2-Design and P-CF1 have been selected for the next proposal. All later packages\nare conditional; a defensible NO_GO may end the current method-paper line.", "CF2-Design and P-CF1 were released and completed. All later packages are\nconditional; the current design NO_GO does not release a method-development run.")
    text = text.replace("OWNER_DIRECTION_SELECTED; EXECUTION_NOT_RELEASED | Source-located comparison, falsification examples, GO_FOR_OWNER_PROTOCOL_REVIEW / NO_GO_THIS_MECHANISM / INSUFFICIENT_EVIDENCE", "COMPLETE / NO_GO_THIS_MECHANISM | Two generic formulations, 12 exact constructed cases, source-located review and one final design ticket; no fit or final access")
    text = text.replace("OWNER_DIRECTION_SELECTED; EXECUTION_NOT_RELEASED | Real API/UI/export, all arms/budgets, EN/TH, provenance, privacy, regression evidence and actual manual/screenshots", "COMPLETE / PASS_INTERNAL_INTEGRATION | Actual API/UI/local C tools/export, all 70 EN/TH views, strict provenance, privacy/regressions, screenshots and English PDF; no user/market validation")
    text = text.replace("**The proposed ten-hour LR-CF2P closes F1 and F4 investigations/delivery, plus\none joint owner checkpoint: two of these eight remaining packages.**", "**The executed LR-CF2P closes F1 and F4 plus the joint owner checkpoint:\ntwo of the previously remaining eight packages.**")
    pos = text.index("## Next decision")
    text = text[:pos] + """## Next decision

Read [the actual owner checkpoint](LR_CF2P_OWNER_CHECKPOINT_20261110.md) and
[source-located CF2 decision](../03_research/CF2_DESIGN_DECISION_20261110.md).
Recommended next discussion is F5 product workflow evaluation: representative
research tasks/users, one proposed destination and comparison with ordinary
tools, with an owner-reviewed protocol before any live writes or new grant.
The method-paper line needs a distinct specific strategy and suitable evidence;
the current NO_GO is not permission to repeat training/design automatically.
The six remaining packages are conditional destinations, not mandatory reruns.
The owner chooses the next scope; no old unused allowance or final16 access is
released. The original proposal/config remain immutable creation-time records.
"""
    path.write_text(text, encoding="utf-8", newline="\n")
    path = ROOT / "docs/00_project/CLAIM_LEDGER.md"
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write("""
## CF2 design and P-CF1 integration, 10 November 2026

| ID | Claim | Evidence status | Evidence and limit |
| --- | --- | --- | --- |
| CF2P-R1 | Two generic probability/dependence or feedback coverage formulations supply a new method | NO_GO_THIS_MECHANISM | [Design decision](../03_research/CF2_DESIGN_DECISION_20261110.md), closest-work locations and 12 constructed cases. No fitted joint model, identifiable adaptive evidence, new selector or final access. Not a proof that every specific alternative is impossible. |
| CF2P-P1 | Main app and additive local C tools expose the authenticated CF1 study | PASS_INTERNAL_INTEGRATION | [Integration guide](../05_product/CF1_INTEGRATION_GUIDE_20261110.md), 70 actual served-build EN/TH views, 22 Python/API and 26 frontend tests, native stdio, atomic local exports, screenshots and six-page English PDF. No live connector or representative-user study. |
| CF2P-P2 | Product integration establishes laboratory/business value or journal readiness | NOT_ESTABLISHED | All six source campaigns remain exposed development; structural-group coverage is a proxy. No prospective assay, customer, independent method evaluation or submission. |
| CF2P-A1 | This goal preserves earlier evidence and closes within fresh limits | CHECK_CLOSURE_RECEIPTS | [Audit/budget](../evidence/lr-cf2p-20261110-v1/README.md): 13 old ledgers, 66 merged scientific pins, five inputs and prior C/manual bytes. Local-only compute; read-only SSH, no remote files created or deleted. |
""")
    intake = read(TASK / "reading/intake.json")
    downloaded = [r for r in intake if "sha256" in r]
    for row in downloaded:
        assert sha(TASK / "reading" / (row["id"] + ".pdf")) == row["sha256"]
    write(PUBLIC / "reading-receipt-v1.json", {
        "status": "TARGETED_PRIMARY_REVIEW_COMPLETE_WITH_ACCESS_LIMITS", "reviewer": "parent self-review",
        "literature_lookup_tool_calls_recorded": 9, "lookup_cap": 24,
        "new_local_primary_pdfs": downloaded, "successful_pdf_bytes": sum(r["bytes"] for r in downloaded),
        "all_new_reading_bytes": sum(p.stat().st_size for p in (TASK / "reading").iterdir() if p.is_file()),
        "original_intake_statuses_are_creation_time_not_final_read_depth": True,
        "read_depth": "Selected source sections/definitions, not end-to-end reading or native author reproduction",
        "source_locations_and_access_limits": "docs/02_literature/CF2_CLOSEST_WORK_20261110.md",
        "existing_room_identity_receipt": "existing-reading-identity-v1.json",
        "failed_local_downloads": [r for r in intake if "error" in r],
        "abstract_only": ["Johnson2007"], "indexed_sections_only": ["batch_as2018", "BCD2019"],
        "online_selected_pdf_sections": ["MOCOBO arXiv v4"], "molecular_labels_accessed": False,
        "independent_review": False, "pdfs_redistributed_in_git": False}, True)
    unchanged = {str(i): sha(TASK / f"manual-v4-render/page-{i}.png") == sha(TASK / f"manual-v4-render-r2/page-{i}.png") for i in range(1, 6)}
    assert all(unchanged.values())
    write(PUBLIC / "visual-review-v1.json", {
        "status": "PASS_PARENT_RENDERED_SELF_REVIEW", "independent_reviewer": False,
        "pdf": "docs/manual/CuraLoop-RL-Confirmation-Evidence-Guide-EN-v4.pdf", "sha256": sha(ROOT / "docs/manual/CuraLoop-RL-Confirmation-Evidence-Guide-EN-v4.pdf"),
        "pages_reviewed": [1, 2, 3, 4, 5, 6], "final_pages_1_to_5_render_byte_identical_to_viewed_first_render": unchanged,
        "page6_repaired_and_final_render_viewed": True, "issue_found": "Original page 6 heading clipped at right edge",
        "repair": "Shortened heading with measured width assertion; body and all other page renders unchanged",
        "checks": ["No final title/body/footer overlap or clipped text", "Readable chart and selected metrics at printed page size", "Actual app/export screenshots correctly described", "Thai mobile chart labels inside SVG", "Grayscale operator shapes and selected outline remain distinguishable", "Scope, seed ranges and provenance preserved"],
        "ui_views_reviewed": ["screens-v4/02-tradeoff-en.png", "screens-v4/06b-tradeoff-mobile-th.png", "screens-v4/09-c-workspace-th.png"],
        "grayscale_capture_private": ".local/lr-cf2p-20261110-v1/chart-grayscale-v4.png",
        "visual_spec": "visual-spec-v1.json", "score_or_independent_certification_claim": False}, True)
    print("PASS current navigation, claim boundaries and reading/render review receipts")


if __name__ == "__main__":
    main()
