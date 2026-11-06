# Working-interface redesign: reference review

The owner rejected the opened competitor interfaces as visual templates. This
review informs workflow choices only. It does not establish superior usability,
customer adoption, scientific performance or business value for CuraLoop-RL.

## Public references and limits

| Product | Official reference | Useful workflow pattern | CuraLoop-RL decision |
| --- | --- | --- | --- |
| Benchling | [Account navigation](https://help.benchling.com/hc/en-us/articles/9684267691021-Navigate-your-Benchling-account) | Stable project and record navigation | Keep a fixed, labeled sidebar and current record context; remove promotional copy. |
| Dotmatics Luma | [Product overview](https://www.dotmatics.com/luma) | Review records and analytical outputs together | Put the campaign record beside a candidate inspector; use a numerical ledger rather than a wall of KPI cards. |
| Causaly | [Agentic research](https://www.causaly.com/products/agentic-research) | Inspect citations alongside research outputs | Keep source locators, hashes and readiness gaps accessible from each metadata claim. Do not imply a live autonomous agent was evaluated. |
| Schrödinger LiveDesign | [Product overview](https://www.schrodinger.com/platform/products/livedesign/) | Connect records, plots and decisions | Connect actual candidate tables, delivered outcomes and policy comparisons. Preserve discrete event curves. |

Only public product/help pages were reviewed. No authenticated tenant, paid
account or competitor workflow was tested. Two public vendor images (Benchling
navigation and Luma summary) were actually viewed. They remain private references,
not CuraLoop-RL assets or a visual-quality target. Other observations describe
public documentation and vendor positioning, not independently measured capability.

## Design basis

Use [Oil UI](https://github.com/oil-oil/oil-ui) for working-screen iteration and
independent visual/UX review. Apply the owner's later
[no-slop-ui](https://github.com/LeoStehlik/no-slop-ui) constraints when generic
motion or decorative suggestions conflict. Keep the established CuraLoop-RL
palette, CuraThai font, accessibility and scientific requirements.

- Lead with the current record and one next action, not a dashboard slogan.
- Use structure, whitespace, restrained borders and readable text.
- Remove nested cards, decorative gradients, fake activity, hover movement and
  unrelated marketing language.
- Show pending, delivered and missing outcomes as distinct real states.
- Translate interface labels and controls into EN/TH. Keep source statements,
  identifiers, scientific values and original diagnostics intact.
- Use 100–200 ms opacity/color transitions in the application, with reduced-motion
  support. Keep [HyperFrames](https://github.com/heygen-com/hyperframes) in the
  approved walkthrough/prototype deliverable.

The intended distinction is a quieter interface where the next decision and its
supporting evidence are easy to inspect. This is a design hypothesis. Runtime,
visual and UX acceptance must be recorded against actual rebuilt pages.

## Current verification boundary

At this preparation checkpoint, new React/C Workspace code exists but production
build, browser acceptance, refreshed manual and HyperFrames render are pending.
The first remote process-tree canary failed closed because cpuset was not
delegated to the user manager. Its payload was not released; descendants were
confirmed absent. The owner has been asked whether an aggregate one-core CPU
quota with inherited starting affinity is acceptable. No privilege/configuration
change or unbounded build fallback was performed.
