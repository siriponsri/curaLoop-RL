---
name: CuraLoop-RL
description: A local scientific workbench with the restraint and traceability of a research operations journal.
colors:
  primary: '#087f72'
  primary-hover: '#066c60'
  midnight: '#16333b'
  muted: '#526653'
  canvas: '#f7f9f8'
  surface: '#ffffff'
  line: '#dce5e1'
  primary-soft: '#e6f3eb'
  primary-soft-ink: '#086851'
  nav-active: '#e3f2eb'
  nav-active-ink: '#076e5e'
  research-soft: '#e4eee8'
  workflow-soft: '#f0f5f0'
  brand-amber: '#b66914'
  amber-ink: '#9a5a10'
  amber-soft: '#fcf3df'
  amber-badge-ink: '#87530e'
  reserved: '#dfb457'
  available: '#d8e5d9'
  focus: '#49a994'
  danger-ink: '#a43834'
  danger-soft: '#fff5f3'
  chart-random: '#687b8a'
  chart-q-learning: '#7958a5'
  chart-bandit: '#227cb3'
typography:
  display:
    fontFamily: CuraThai, sans-serif
    fontSize: clamp(32px, 3.3vw, 49px)
    fontWeight: 650
    lineHeight: 1.22
    letterSpacing: -0.04em
  headline:
    fontFamily: CuraThai, sans-serif
    fontSize: 32px
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: -0.035em
  title:
    fontFamily: CuraThai, sans-serif
    fontSize: 19px
    fontWeight: 650
    lineHeight: 1.4
    letterSpacing: -0.022em
  subheading:
    fontFamily: CuraThai, sans-serif
    fontSize: 15px
    fontWeight: 650
    lineHeight: 1.4
    letterSpacing: normal
  body:
    fontFamily: CuraThai, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: normal
  body-copy:
    fontFamily: CuraThai, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.75
    letterSpacing: normal
  presentation-copy:
    fontFamily: CuraThai, sans-serif
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.85
    letterSpacing: normal
  label:
    fontFamily: CuraThai, sans-serif
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: normal
  annotation:
    fontFamily: CuraThai, sans-serif
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: normal
  table:
    fontFamily: CuraThai, sans-serif
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: normal
  technical:
    fontFamily: ui-monospace, SFMono-Regular, Consolas, CuraThai, monospace
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: -0.015em
  metric:
    fontFamily: CuraThai, sans-serif
    fontSize: 31px
    fontWeight: 550
    lineHeight: 1.4
    letterSpacing: -0.035em
  training-axis:
    fontFamily: CuraThai, sans-serif
    fontSize: 10px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: normal
rounded:
  badge: 5px
  field: 6px
  control: 7px
  navigation: 8px
  compact-card: 11px
  surface: 12px
  dialog: 13px
spacing:
  tight: 5px
  icon-gap: 8px
  compact: 12px
  mobile-gutter: 18px
  section: 20px
  rule: 24px
  surface: 25px
  desktop-gutter: 36px
components:
  button-primary:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.surface}'
    typography: '{typography.label}'
    rounded: '{rounded.control}'
    padding: 11px 17px
  button-primary-hover:
    backgroundColor: '{colors.primary-hover}'
  button-outline:
    backgroundColor: '{colors.surface}'
    textColor: '#3b574b'
    typography: '{typography.label}'
    rounded: '{rounded.control}'
    padding: 11px 17px
  button-secondary:
    backgroundColor: '#e3eee7'
    textColor: '#174b34'
    typography: '{typography.label}'
    rounded: '{rounded.control}'
    padding: 11px 17px
  button-ghost:
    backgroundColor: transparent
    textColor: '#496556'
    typography: '{typography.label}'
    rounded: '{rounded.control}'
    padding: 11px 17px
  button-destructive:
    backgroundColor: '{colors.danger-soft}'
    textColor: '{colors.danger-ink}'
    typography: '{typography.label}'
    rounded: '{rounded.control}'
    padding: 11px 17px
  badge-teal:
    backgroundColor: '{colors.primary-soft}'
    textColor: '{colors.primary-soft-ink}'
    rounded: '{rounded.badge}'
    padding: 3px 7px
  badge-amber:
    backgroundColor: '{colors.amber-soft}'
    textColor: '{colors.amber-badge-ink}'
    rounded: '{rounded.badge}'
    padding: 3px 7px
  surface:
    backgroundColor: '{colors.surface}'
    textColor: '{colors.midnight}'
    rounded: '{rounded.surface}'
    padding: '{spacing.surface}'
  input:
    backgroundColor: '{colors.surface}'
    textColor: '#34533f'
    rounded: '{rounded.field}'
    padding: 9px 11px
    width: 100%
  navigation:
    backgroundColor: transparent
    textColor: '{colors.muted}'
    rounded: '{rounded.navigation}'
    padding: 12px 13px
  navigation-active:
    backgroundColor: '{colors.nav-active}'
    textColor: '{colors.nav-active-ink}'
    rounded: '{rounded.navigation}'
    padding: 12px 13px
  workflow-step:
    backgroundColor: '{colors.workflow-soft}'
    textColor: '{colors.muted}'
    rounded: '{rounded.navigation}'
    padding: 17px 17px
  budget-track:
    backgroundColor: '#ecf2ed'
    rounded: '{rounded.badge}'
    height: 8px
---

# Design System: CuraLoop-RL

## Overview

**Creative North Star: "The Research Operations Journal"**

CuraLoop-RL is a calm, editorial scientific workbench: white working surfaces sit on a pale mint and stone canvas, with midnight reading text, restrained teal actions and amber qualifications. A stable tool rail and generous section spacing make dense research records approachable without hiding their detail. The original CuraLoop-RL logo and owner-pinned teal, midnight and amber identity remain binding; this is an original shell informed by shadcn references, not a replacement brand.

This document captures the implemented local web system, extracted from frontend/src/styles.css, the shared UI primitives, shell, seven pages and chart components. The confirmed direction lives in docs/WEB_DESIGN_BRIEF.md; final screenshots live in docs/evidence/web-v2/browser. Its visual authority is the working application and actual evidence, not a generated mockup or an invented approval. The final review disposition is SHIP for the reviewed localhost portfolio scope; the review closed four bounded findings and does not establish a fresh audit of every surface.

**Key Characteristics:**
- Publication-like hierarchy within a persistent research tool shell.
- Light mint, stone and white surfaces; teal actions and amber qualifications.
- Offline English typography using the supplied Noto Sans Thai font.
- Live state, recorded evidence and source provenance remain visibly distinct.
- Compact scientific tables and captions retain explicit small-type exceptions.

## Colors

The palette is quiet and botanical rather than clinical blue: teal establishes action, mint and stone organize working space, and amber asks the reader to interpret limitations carefully. The frontmatter is the extracted token source; component-only literals remain in their component entries.

### Primary

Teal `primary` is the action, spent-budget and Greedy-policy color. `primary-hover` deepens the primary button. `primary-soft` and `primary-soft-ink` form teal source/status badges; `nav-active` and `nav-active-ink` identify the current destination. These are distinct implemented treatments, not a single interchangeable tint.

### Secondary

Original `brand-amber` remains the Uncertainty-policy and recorded error-bar accent. The CSS uses darker `amber-ink` for readable amber text and `amber-badge-ink` on `amber-soft` badges. This is an intentional record of the shipped implementation, not a palette replacement. `reserved` marks committed but unsettled simulated budget; `available` marks the uncommitted remainder.

### Tertiary

The multi-policy chart mapping is fixed: Random uses `chart-random`, Greedy uses `primary`, Uncertainty uses `brand-amber`, Q-learning uses `chart-q-learning`, and Contextual bandit uses `chart-bandit`. Keep the corresponding policy names and existing dash patterns beside these colors. `danger-ink` and `danger-soft` are used for destructive controls, not scientific inactivity.

### Neutral

`midnight` is the main reading color; `muted` carries secondary labels, captions and supportive text. `canvas`, `surface` and `line` define the page, white panels and structural borders. `research-soft` is the tonal research inset; `workflow-soft` distinguishes the linked process steps. Focus uses its own visible `focus` accent.

The sidecar's eight-step tonal ramps are synthesized OKLCH preview aids. They are not an additional production palette and do not authorize new semantic shades.

**The Original Identity Rule.** Retain the supplied CuraLoop-RL logo and the pinned teal, midnight and amber identity. Readable amber text may use the darker implemented ink variants.

**The Labelled State Rule.** Pair color with written status, counts, policy labels or line patterns; color alone must not carry a scientific distinction.

## Typography

**Display and Body Font:** CuraThai, the supplied offline variable Noto Sans Thai font, followed by sans-serif. The font file is loaded locally from `/fonts/NotoSansThai.ttf`, covers weights 100–900 and uses swap display.

**Label/Mono Font:** Technical identifiers use the documented technical stack, retaining the bundled font after Latin monospace faces for complete offline glyph coverage.

**Character:** One bundled family carries English editorial headlines and dense operational detail. Dark text, restrained negative tracking in large Latin headings and generous paragraph leading supply the hierarchy; there is no separate decorative display face.

### Hierarchy

| Token | Implemented use and exceptions |
| --- | --- |
| `display` | Overview headline. Responsive overrides use 37 px at ≤1250, 43 px at ≤1020, 36 px with 1.3 leading at ≤760, and 51 px at ≥1600. The range is not a monotonic fluid scale. |
| `headline` | General page h1. Page-heading overrides are 29 px at ≤1020 and 28 px at ≤760. |
| `title` / `subheading` | Section hierarchy. Mobile section titles use 17 px; individual form and queue headings use their existing 15–18 px variants. |
| `body` / `body-copy` | Root text and ordinary paragraph leading. Supporting workbench prose often uses 12–13 px; hero copy uses 1.85 leading and a 57ch measure. |
| `presentation-copy` | Spacious guided narration, reducing to 14 px at ≤1250; mobile uses 1.9 leading. Presentation chapter titles are 37 px desktop and 31 px at narrower widths, weight 550. |
| `label` | Default action labels. Navigation is 13 px/500, with active weight 650. |
| `annotation` | Footnotes, source badges, provenance lists, field notes, timeline text, chart notes and many mobile labels. Badge weight is 550 and leading 1.3; caption leading varies by component. |
| `table` | Scientific tables use tabular numerals, weight 500 headers and 1.8 leading for wrapping explanations. |
| `technical` | Hashes and identifiers; compact contexts reduce to 11 px. |
| `metric` | KPI totals with tabular numerals. Mobile totals are 29 px; labels and units remain smaller. |
| `training-axis` | Existing checkpoint-return tick labels. This 10 px exception is specific to the small training charts. |

Small text is an honest density exception: this implementation uses 11 px footnotes, scientific tables and many secondary labels, plus 10 px training-axis ticks. It does not promise a universal 16 px floor. Preserve the existing contrast, explanatory line height, zoom behavior and contained table scrolling; do not spread these exceptions to major narrative copy. Font sizes follow the CSS's explicit pixel values and a 14 px root rather than an invented geometric type scale.

**The Offline Type Rule.** Keep the licensed bundled font in body and technical fallback stacks. Verify English wrapping, dense identifiers and accessible labels on desktop and mobile after layout changes.

## Layout

The desktop shell has a fixed white tool rail (244 px) and a corresponding main offset, a quiet top bar (76 px), a flexible main column and a naturally scrolling document. The main content is centered within a maximum width of 1500 px; its default padding is 34 px vertically at the top, 36 px horizontally and 44 px at the bottom. This is a tool-and-document system, not a universal grid of equal cards.

The spacing tokens catalogue recurring values, not a strict eight-point scale. Panels normally use the surface inset; related controls use compact gaps; section boundaries and editorial blocks use larger breathing room. Retain observed spacing where scientific density requires it.

| CSS condition | Actual behavior |
| --- | --- |
| ≥1600 px | Horizontal content padding becomes 46 px; overview specimen and headline receive more room. |
| ≤1250 px | Rail becomes 219 px, horizontal content padding 25 px, panels 21 px and lab board one column. |
| ≤1020 px | Rail becomes 205 px; content padding is 27 px × 21 px. Overview/scenario/evidence and presentation layouts stack; the overview specimen hides; the compound grid becomes two columns. Chapter navigation becomes a horizontally scrolling row. |
| ≤760 px | Rail hides and its offset clears. Navigation opens in the Radix dialog; top bar becomes 64 px and main padding becomes 23 px 18 px 32 px. KPI/workflow blocks use two columns. Panels use 20 px 17 px. Compounds remain two columns. |

Body minimum width is 320 px. Desktop compound cards use three columns; forms use two columns where implemented. Wide scientific tables and the capped event timeline scroll inside named, focusable regions; they must not widen the page. Hashes wrap anywhere, explanation cells wrap naturally and table values retain their alignment. The content footer wraps when required.

Historical v0.2 captures cover Chromium/Linux at 1440 px and 390 px. Current English-only Windows evidence is recorded separately in docs/RELEASE_VERIFICATION.md. Legacy Thai browser storage does not change the document language or interface. Resume, replay, loading and recovery feedback use English. Physical-device and other-browser checks require their own evidence.

## Elevation & Depth

Most depth comes from white surfaces, soft mint insets and fine borders. Standard working panels have no resting shadow. Shadows are small and functional on the primary action, selected language control and hovered compound; the transient busy indicator and dialog sit above the workspace. No gradients or glass effects are part of the current system.

### Shadow Vocabulary

| Role | Exact implemented shadow | Use |
| --- | --- | --- |
| Primary action | `0 2px 5px #065c4f12` | Default teal button. |
| Language selection | `0 1px 3px #183a2414` | Selected EN/TH segment. |
| Compound hover | `0 7px 22px #223d2710` | Interactive compound card only. |
| Busy indicator | `0 8px 28px #123b3026` | Fixed local-engine status. |
| Modal | `0 24px 90px #0b251d38` | Dialog above the translucent `#132e2580` scrim. |

**The Flat Surface Rule.** Working surfaces rest on borders and tonal layering. Use the existing small action and hover shadows; reserve the large shadow for a modal.

## Shapes

Corners are modest and differentiated by role: badges, fields, buttons, navigation, compact cards, standard panels and dialogs use the frontmatter's observed radii. White panels and compound cards retain thin borders. Status dots and chapter numerals use circles; color legend markers are small rounded squares. KPI strips and molecular cards clip their content within the container; chart surfaces allow overflow for axis labels.

The Tailwind theme also declares `--radius-lg: 0.875rem`, but the visible class-based components use the explicit pixel radii captured here. Do not silently normalize their corners to that separate theme value. The supplied logo's geometry is an identity asset, not a shape to redraw.

## Components

### Buttons

Restrained, compact and legible. The shared Button exposes default, secondary, outline, ghost and destructive variants, plus default/small/icon sizes. Its normal minimum height is 40 px; small is 33 px, and the icon variant declares a 36 px square while inheriting the base 40 px minimum height. Do not claim every control already meets a 44 px target.

Default actions use the primary token pair. Outline actions use white, a fine stone border and green-gray ink, shifting to a pale mint hover; secondary is a subdued green fill; ghost is transparent until hover; destructive is pale red with a red border. Normal padding is held in the component tokens; small actions use 7 px 12 px. Mobile action padding and labels follow the existing page-specific overrides.

Background, shadow and transform transitions are 160 ms with the CSS default easing. Pressed enabled buttons move down 1 px; disabled controls use 0.45 opacity and a not-allowed cursor. General keyboard focus is a 3 px visible outline offset by 3 px. Do not infer a special secondary/destructive hover treatment absent from the source.

### Badges and Source Labels

Badges are compact rounded rectangles with a thin border, 23 px minimum height and explicit text. Teal identifies the historical public-data source or ordinary settled state in its context; amber identifies synthetic fixtures and qualifications. The shared source badge follows the active campaign's manifest rather than a hardcoded page default. Observed active and observed inactive may share a teal badge: the written label, not teal alone, carries that distinction. Pending and missing outcomes remain separately named.

### Cards / Containers

Ordinary surfaces are white, bordered and flat, with responsive insets. The tonal research note is a purposeful inset, not a template for every card. Compound cards use their compact radius, an actual public structure when available, a descriptor fallback when not, and a subtle hover border/shadow. Image content is contained rather than cropped; synthetic descriptors must not acquire fabricated molecular structures.

### Inputs / Fields

Native labelled input/select controls use a white field, 1 px `#d4dfd7` stroke, the field radius and 41 px minimum height. Text is 12 px, with the documented component padding. Hover changes the stroke to `#9ab8a3`; focus uses a 2 px `#b1d5c3` outline and `#4c9173` border. Mobile fields use 42 px minimum height. Validation is an explicit nearby alert/message; no unsupported field-error variant is invented here. Native checkboxes retain teal accent and selected policy cards add a pale green fill and stronger border.

### Navigation and Dialogs

Navigation is a stable vertical list with Lucide line icons and written labels. Its default item minimum height is 45 px; active uses the documented tint/ink and increased weight, while hover is a lighter green surface. The language switch uses explicit EN/TH buttons with `aria-pressed`; it is separate from the page navigation.

At mobile width the same destinations are presented inside the existing Radix dialog. The dialog is centered, at most 560 px wide, uses `calc(100vw - 32px)`, caps height at 90vh and scrolls internally. It retains the actual close control, title/description, keyboard focus behavior and focus return. Do not turn the current modal into an undocumented slide-in drawer.

### Scientific Charts and Tables

Live discovery and queue series are discrete `stepAfter` traces with chart animation disabled. The discovery chart uses a labelled policy legend, fixed policy colors and dash patterns for later series. These counts change only with actual events. The checkpoint-return trace currently uses `monotone` interpolation at 1.4 px, without dots or animation; it is an existing training-record display exception, not authority to smooth discrete delivered-hit curves.

Recorded horizontal benchmark bars use teal with original amber error bars. Their uncertainty is seed SD; the lower display bound is clipped to zero by `min(mean, SD)`, while the full exact SD remains in the benchmark table. Retain the visible zero-clipping explanation and do not relabel this quantity as a confidence interval. Axis titles, chart group labels and the adjacent scientific table support interpretation; some chart/tooltips and auxiliary labels remain English.

Tables are compact, tabular, row-divided records with a tinted header and a very quiet hover. Non-wrapping value cells coexist with wrapping explanation cells. The table scroll region and event timeline are keyboard focusable and use their own teal outline; do not remove this access when adding columns.

### Live Workflow and Budget Ledger

The linked workflow shows candidate pool → policy selection → result queue → delivered results using real counts, icons, labels and a pending-state tint. At mobile width it becomes a two-by-two arrangement rather than a horizontal page overflow. A completion check reflects the actual finished run.

The budget ledger is an 8 px clipped track with separate spent, reserved and available labels and actual values. Its widths reflect real simulation state. Current CSS has no explicit width transition: the direction brief's intended deliberate width motion has not been implemented as a separate effect. Do not claim it has. Existing motion is limited to the documented 160 ms component transitions and a 900 ms linear loading spinner. The reduced-motion media query disables all animation and transitions and restores automatic scroll behavior.

### Feedback and Evidence Context

Loading, empty, error, notice, busy, resume and disabled states retain their actual messages and semantics. Keep the active manifest's historical/synthetic source adjacent to the work, and keep a separately labelled recorded v0.1 benchmark distinct from the active campaign. Provenance lists expose the current Git revision, working-tree status, engine source hash and exact frontend build hash; do not substitute a branch name, old screenshot identifier or vague current-version claim for that record.

The accompanying finish review and browser record identify frontend build `2b8c8ea049a3fb1f61f0e9e9647cda81a28d01af2f3debc09ca33fed26aa3fc6` served from the actual built Vite assets by FastAPI at `http://127.0.0.1:8000`. This is a historical review identity, not an instruction to freeze future live metadata. The review records 28 final PNGs and 18 axe route/state checks; these are recorded evidence, not tests rerun for this documentation pass.

## Do's and Don'ts

### Do:

- Do reuse the supplied logo, local CuraThai font and the documented token roles.
- Do preserve readable English wrapping, visible keyboard focus and contained, keyboard-scrollable scientific tables.
- Do show source origin beside the active work and label separately recorded HIV results as recorded evidence.
- Do keep predicted, pending, observed active, observed inactive and missing outcomes explicit in text.
- Do use step-after live discovery and queue traces, labelled policy colors and the benchmark table for exact seed SD.
- Do keep compact captions and scientific tables intentional, with enough line height and space to wrap explanations.
- Do preserve real zero, unfavorable and fallback results, and visible loading, error, empty and disabled states.
- Do disable existing animation and transitions for prefers-reduced-motion.

### Don't:

- Don't replace the pinned identity with a new logo, palette, stock biotech fantasy or invented molecular imagery.
- Don't turn a pending request or predicted positive into a confirmed discovery, or collapse missing into inactive.
- Don't present the recorded v0.1 benchmark or synthetic training trace as a new run, useful RL transfer or a clinical result.
- Don't omit the zero-clipped SD display disclosure or relabel seed SD as a confidence interval.
- Don't add chart animation, celebratory success effects or artificial completion percentages.
- Don't hide provenance or limitations to simplify a composition, and don't create page-level horizontal overflow.
- Don't claim complete localization, all controls at 44 px, a universal 16 px minimum or a universal eight-point spacing scale; those are not the implemented system.
- Don't claim Windows, Safari, physical-device, manual screen-reader or measured performance validation from the recorded Chromium/Linux localhost review.
