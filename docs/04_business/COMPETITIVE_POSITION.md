# Competitive position and build-versus-integrate decision

This is a capability review of primary papers and project documentation, not a market-share or pricing survey. “Not assessed” means the available evidence was insufficient; it does not mean a competitor lacks the capability. Do not convert this table into unsupported sales claims.

| Tool / method | Publicly documented focus | Relationship to CuraLoop |
| --- | --- | --- |
| MolPAL (R04) | Model-guided pool screening | Strong acquisition and scaling reference |
| GLARE (R07) | RL-based molecular selection | Direct learned-selection prior art |
| ALF (R08, preprint) | Modular offline/online acquisition loop | Potential integration host and software comparator |
| PAL (R09) | Concurrent active-learning components | Existing asynchronous infrastructure reference |
| BoTorch (R16) | Probabilistic acquisition and optimization | Candidate numerical backend, not a feature to reimplement casually |
| BayBE (R26; paper snapshot 0.12.2) | Practical BO, historical backtesting, chemical/custom encodings, asynchronous/partial-measurement support, serialization, transfer and stopping | Direct workflow alternative and integration candidate; case-study savings are not CuraLoop outcomes |
| SimDMTA (R27) | Query strategies in simulated DMTA | Close study-design comparator |
| CuraLoop current POC | Local historical replay with public event accounting | Narrow existing implementation, limited biological evidence |

## Integration tests before product expansion

Test whether a thin adapter can submit public candidate features and revealed labels to an existing acquisition backend while retaining CuraLoop's oracle boundary and ledger. A successful integration may improve the product and provide a fair baseline. Record package versions, license obligations and operational assumptions. An integration remains future work until code and tests exist.

Use a concrete build-versus-integrate decision: which customer-specific gap remains after using an established framework? A local event ledger or UI alone may not justify another independent platform. A reproducible set of operational stress tests and an installation/reporting workflow may be useful if it saves actual analyst effort, which must be measured in a pilot.

## Evidence gaps

Commercial support terms, current enterprise prices, customer counts, service guarantees and procurement eligibility were not researched or verified. Do not invent them. The first market assessment should obtain real quotations or published terms when needed and distinguish vendor statements from observed customer behavior.

## Defensible selling language

Use “local evaluation workbench,” “matched historical replay,” and “documented assumptions.” Avoid “first RL screening platform,” “guaranteed discovery,” “validated laboratory savings,” “GMP-ready” and “approved by GPO.” Such statements exceed the evidence. Competition is addressed by a specific workflow and credible results, not a claim that no alternatives exist.

## Evidence added from the BayBE publisher article

The full text confirms that workflow usability and historical backtesting are established offerings. Its selected reaction and encoding examples do not establish a market-wide savings rate, a competitor's current pricing or this project's customer ROI. Distinguish a paper's feature evidence from a test of an installed release.

Use an integration-first feasibility gate: choose a pinned local backend; compare objective/observation contracts; test a small public-data replay; and measure implementation effort versus a native alternative. Record whether capacity, pending information, cost settlement and report provenance remain in CuraLoop or the backend. If the existing framework already meets the buyer's need, scope installation, adaptation or evaluation support rather than promising a unique platform.
