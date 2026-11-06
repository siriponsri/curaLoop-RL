# Approved design: Molecular Studio, Graphite x Copper

The owner chose direction A from three actual first-screen composition studies,
then rejected the green/cyan/teal theme and approved the revised design for
continued implementation. This supersedes the earlier light teal direction.
Keep both the main screening app and C Workspace, EN/TH, in scope.

## Visual intent

A scientific object is the focal point. Keep a large, authentic molecular view
beside its record, outcome-visibility boundary and next action. C Workspace uses
the actual declared endpoint and linked evidence as its focal object; metadata
that contains no molecular structure must not acquire an invented molecule.
Use a graphite navigation rail, an ivory working canvas, white object surface,
precise warm borders and deep copper actions. Keep one primary action per screen.

The current [official GPO website](https://www.gpo.or.th/) was visually inspected
on6November2026 and uses teal (computed navigation color RGB0,169,157).
Graphite x Copper is this project's proposed pharmaceutical R&D palette, not an
official GPO CI palette. The owner's explicit exclusion of teal takes priority.
Keep the independent-project identity and existing provenance limitations.

| Role | Value |
| --- | --- |
| Canvas | `#F6F4EF` |
| Object surface | `#FFFFFF` |
| Secondary surface | `#FCFBF8` |
| Graphite text / navigation | `#28282B` |
| Muted text | `#6A6661` |
| Decorative border | `#D9D5CF` |
| Primary action / focus | `#A6492D` |
| Primary hover | `#883B25` |
| Selected soft surface | `#F4E5DC` |
| Decorative accent | `#C97245` |

Calculated contrast: white/action5.81:1, graphite/ivory13.37:1,
muted/ivory5.18:1 and action/selected-soft4.73:1. Decorative borders alone are
not sufficient control boundaries; use stronger neutral control borders/focus.
These pair calculations do not establish whole-application accessibility.

## Behavior and motion

- Navigate the actual eligible public candidate pool without changing a campaign.
- Zoom/reset only the displayed structure; preserve standard RDKit atom colors.
- Display the original CuraLoop logo in monochrome through scoped CSS, retaining
  its original file and geometry. Never apply a global image color filter.
- Connect selected metadata fields to their actual source locators and hashes.
- Preserve pending/missing/delivered distinctions, source IDs, scientific values,
  cached-data limits, session/revision identity and private outcomes.
- Use purposeful object/inspector feedback and scoped GSAP/CSS transitions;
  disable nonessential motion under reduced motion. Do not animate scientific
  values or discrete evidence curves. HyperFrames remains a separate walkthrough.

The direction studies are static composition previews, not connected operations
or tested motion. The approved design still requires actual implementation,
fresh builds, tests, visual/UX review, EN/TH browser checks, manual/PDF refresh and
remote full-return verification/cleanup before final main delivery.
