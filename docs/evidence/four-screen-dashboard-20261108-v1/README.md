# Four-screen dashboard: actual browser evidence

8 November 2026. Screens captured from the actual local React application and
Python engine, using a separate disposable QA database. No template scores or
sample customers. The selected historical HIV campaign's zero new hits are
preserved. All costs and delays are simulated assumptions.

| Screen | Desktop EN | Desktop TH | Mobile EN | Mobile TH |
| --- | --- | --- | --- | --- |
| Discovery Overview | [View](01-overview-en.png) | [View](01-overview-th.png) | [View](01-overview-mobile-en.png) | [View](01-overview-mobile-th.png) |
| Digital Twin Simulation Lab | [View](02-lab-en.png) | [View](02-lab-th.png) | [View](02-lab-mobile-en.png) | [View](02-lab-mobile-th.png) |
| Benchmark Arena | [View](03-arena-en.png) | [View](03-arena-th.png) | [View](03-arena-mobile-en.png) | [View](03-arena-mobile-th.png) |
| Compound Explorer | [View](04-explorer-en.png) | [View](04-explorer-th.png) | [View](04-explorer-mobile-en.png) | [View](04-explorer-mobile-th.png) |

Desktop viewport: 1440 x 1000; mobile: 390 x 844. Full-page captures are linked
above. `*-desktop-*.png` and `*-viewport-*.png` retain the visible first viewport.
Captures wait for real page content, chart loading and molecular images to settle.
Earlier private timing captures that still showed loading are superseded.

- [Actual engine/browser sequence](engine-browser-check.json): stage inspection
  leaves revision unchanged; selection creates pending requests without hits;
  pending candidate labels are null; two advances deliver results; a real
  four-policy comparison completes; EN/TH preserves the campaign; no page errors.
- [Final read-only captures](capture-check.json): both locales and widths without
  page-level overflow or uncaught JavaScript errors.
- [Delivery receipt](delivery-check.json): frontend source fingerprint, public
  metrics, actual comparison policy reports and manual hash. This validates
  product wiring, not scientific superiority or M2 readiness.
- [English operator guide](../../manual/CuraLoop-RL-Dashboard-Guide-EN-v3.pdf).

Independent UX and visual reviewers used isolated contexts. Their findings and
fixes are recorded in the [checkpoint](../../05_product/FOUR_SCREEN_DASHBOARD_CHECKPOINT_20261108.md).
This is not a representative usability study, accessibility certification, live
laboratory validation or cross-target model evaluation.
