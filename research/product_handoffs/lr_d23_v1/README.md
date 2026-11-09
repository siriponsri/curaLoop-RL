# LR-D23 offline product handoff

The package is an aggregate-only evidence adapter input. It does not connect to
the running dashboard or activate a policy. Scientific status is
**INCONCLUSIVE_D2**; D3 was not run. Keep that status visible in EN and TH.

| Artifact | Purpose |
| :--- | :--- |
| [Evidence card](evidence-card-v1.json) | Actual means, source hash, EN/TH decision, limitations |
| [JSON schema](evidence-card.schema.json) | Strict allowed fields; undeclared label payloads rejected |
| [TypeScript type](evidence-card.d.ts) | Adapter-facing structure; no compound-label rows |
| [Product contract](../../../docs/05_product/LR_D23_OFFLINE_HANDOFF_CONTRACT_20261109.md) | Mapping to the four screens and information boundary |
| [Validation](../../../docs/evidence/lr-d23-20261109-v1/product-card-validation-v1.json) | Actual schema/negative-boundary check |

The card's `result.path` is repository-relative. An eventual adapter must verify
its SHA-256 and keep this experiment separate from historical app demos. Random
and legacy RL policies were not evaluated as arms in LR-D23. No assay outcome
visibility can be inferred from the aggregate card.

Before product integration, require an owner-approved phase, actual engine-event
adapter tests, hidden-label API checks, EN/TH UI/interaction review and a bounded
researcher workflow evaluation. No customer ROI, live connector, commercial-data
permission or clinical benefit is established by this package.
