# English documentation and manuscript reconciliation audit

Date: 4 November 2026, Asia/Bangkok. Starting repository commit:
`52c349ab24c653b043fa5401c923d330d7ec3d9e`.

**Status: PASS for the staged-document checks below; final integrated review and
human author approval remain separate.** The documentation subagent inspected
the repository read-only and wrote 14 replacement drafts in its exclusive
staging directory. The parent integrates repository edits. No experiment,
submission, merge, push or deployment was performed by this subagent.

## Scope and language screen

The tracked-document inventory covered 243 UTF-8-readable `.md`, `.rst`, `.txt`,
`.html`, `.svg` and `.tex` candidates: 115 active files, 30 archive files and
98 protected/source/evidence files. There were no decoding failures. A Unicode
screen for Thai, Cyrillic, Arabic, CJK, Japanese and Korean found one hit in an
active file: the source-conversation link label in `docs/REVIEWED_V2_INTAKE.md`.
The staged replacement uses an English label and preserves the original URL.
All 14 staged replacements have zero hits under the same screen.

The screen is an auditable detection method, not proof of language identity for
every Latin-script sentence. Manuscript passages were edited/reviewed in English.
Latin-script author names, source titles, exact identifiers, Greek mathematical
symbols and original URLs are not silently anglicized. Binary PDFs/images were
not reauthored or independently re-rendered by this documentation task; the
existing English screenshot manual and visual-release evidence remain intact.

The other 138 script hits occur in six frozen legacy/source files:

| Retained original | Script-hit lines | Treatment |
| --- | ---: | --- |
| `docs/archive/README_v0.1.md` | 36 | Historical source, unchanged; current README and English manual provide the active entrypoint |
| `requirements_v3/docs/DEMO_STORYBOARD_TH.md` | 20 | Protected source requirements, unchanged |
| `requirements_v3/docs/PORTFOLIO_BRIEF_TH_EN.md` | 7 | Protected bilingual source requirements, unchanged |
| `requirements_v3/docs/PRESENTATION_7_MIN_TH.md` | 14 | Protected source requirements, unchanged |
| `requirements_v3/docs/SOLO_LEARNING_PATH_TH.md` | 35 | Protected source requirements, unchanged |
| `requirements_v3/docs/UX_BLUEPRINT_TH.md` | 26 | Protected source requirements, unchanged |

These are explicit archival exceptions, not English translations or active
instructions. Changing them would alter protected historical evidence. Current
reader-facing operation is documented in the English README, Windows guide,
architecture documents, screenshot manual and public demo/evidence sheet. The
audit does not claim that every preserved source record is English.

## Manuscript corrections

The previous manuscript said that all new multi-target/deadline comparisons
were unexecuted. That was stale after the NCATS development continuation.
The staged chapters now distinguish these evidence layers:

| Layer | Actual evidence | Wording boundary |
| --- | --- | --- |
| Historical HIV pilot | Preserved 1,200-compound replay and complete Greedy fallback for both synthetic-trained controllers | No learned-transfer claim |
| NCATS fixed-control development | 108 completed runs, six methods, three correlated endpoints, three seeds, two timing conditions | Eight heterogeneous ties and one loss for the pending penalty; not a final independent-family test |
| Fresh-environment reproduction | All 108 scientific comparisons match in a separate checkout/new venv | Same host/implementer, not new biological repetitions or independent scientific review |
| Gaussian development amendment | 54 completed runs; all nine heterogeneous pending/blind hit pairs tie, five histories change | Approximate binary Gaussian regression; no equivalence, calibration or inherited regret guarantee |
| Candidate preparation | Outcome-sealed metadata/features, preserved search errors and cap exclusions | Provisional groups, no final-ready task or assigned final role |
| Hierarchical sensitivity | 1,080 hypothetical effect rows and 288 resource rows | Assumed precision/resource scenarios, not observed final power or effects |
| Future final study | Rights, endpoints, whole-pool dependence, roles and analysis/resource freeze remain open | NOT_FROZEN / NOT_RUN |

The methods explicitly separate research modules from the production UI/CLI.
Both original HIV numerical tables are retained exactly. The abstract,
introduction, related-work bridge, methods, proposed-final-study chapter,
results, discussion, limitations, conclusion, declarations, figure/table map,
paper README and assembled manuscript agree on the development/final boundary.

The owner supplied the name Siripon Srihangpiboon, King Mongkut's Institute of
Technology Ladkrabang, contact email and ORCID on 4 November. The declarations
identify these as owner-provided details and do not invent institutional
endorsement, funding, competing-interest answers or completed human approval.
The owner-selected journal fee ceiling is USD 300. Venue assessment and actual
submission are handled separately from this documentation audit.

## Executed verification

The documentation agent executed a staged-document verifier on 4 November:

- **PASS:** all 14 source/replacement hashes match the draft manifest.
- **PASS:** all ten transformed numbered chapters occur in `MANUSCRIPT.md`.
- **PASS:** the two historical HIV tables are unchanged.
- **PASS:** all 54 cells in the added logistic/Gaussian mean tables match the
  preserved CSV values at the reported two-decimal precision.
- **PASS:** original paired counts (8 ties/1 loss), seven changed heterogeneous
  histories, Gaussian nine ties/five changed histories and both common-delay
  controls (9/9 exact) match source CSVs.
- **PASS:** the fresh-environment receipt reports PASS; the simulation contains
  1,080 effect rows and 288 resource rows, and the two quoted median halfwidths
  (0.710 and 0.599) match the specified hypothetical scenarios.
- **PASS:** all 60 local links in staged replacements resolve against repository
  targets; no new external link availability or journal-policy verification is
  claimed by this check.
- **PASS:** the staged script screen finds no non-Latin-script prose hits.

Receipts are `language-scan.json`, `replacement-manifest.json` and
`staged-verification.json` in the English agent's staging directory. The parent
should retain them in the delivery evidence packet and rerun integrated links,
claim checks and protected-byte checks after applying all agents' work.

## Remaining review

An independent reviewer must assess the integrated manuscript rather than this
agent approving its own changes. No source scientific code, raw outcome file,
model, frozen result or application behavior was changed. No application,
frontend, browser or new campaign tests were run by this agent. Exact data
rights, final-family independence, prospective value, journal acceptance and
human authorship/declaration approval are not established by documentation
verification.
