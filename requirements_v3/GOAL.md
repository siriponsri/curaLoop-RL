# GOAL — Personal Pharmaceutical R&D Portfolio

## Primary goal

Build and personally own a polished, reproducible open-source-ready **Pharmaceutical Discovery Workbench** that can be demonstrated in **5–7 minutes** to a non-specialist pharmaceutical R&D audience, including potential audiences inside GPO. It is a personal independent project, **not** an affiliated or approved GPO tool. The deliverable is a real Git repository with functional application code, not a slideshow or abstract research proposal.

## Business/user problem

A scientist with limited experimental capacity must choose candidate compounds from a larger screening library. How can a decision-support simulator compare different selection policies under matched constraints (number of assays, simulated cost, delayed feedback) and explain which policy is best in which scenario?

## Portfolio proof points

1. **Product ownership:** README, clear scope, demo workflow, screenshots, issues, change log and maintainable architecture.
2. **Pharmaceutical relevance:** compound and assay concepts accurately described, synthetic/public data provenance visible, no misleading medicinal claims.
3. **ML engineering:** descriptors/fingerprints and robust predictor plus fair non-RL acquisition policies.
4. **Sequential decision-making:** recorded budget ledger, delayed result queue, reproducible closed-loop simulation, event logs, uncertainty and appropriate RL/bandit extension.
5. **UX & demonstration:** clean Thai/English-capable dashboard with clear controls, explainers, comparison curves, report export and failure/limitation states.
6. **Reproducibility:** CPU/Windows installation, deterministic seeds, tests, tracked experiment configurations and honest result labeling.

## Audience acceptance: first showcase

A reviewer unfamiliar with RL should be able to understand in under 2 minutes: what library is being screened, what the algorithm is choosing, how assay results are revealed, how spending is limited, and why outcomes differ between policies.

A reviewer familiar with ML should be able to inspect the repo, reproduce a demo run, verify hidden-label isolation and challenge comparisons without encountering marketing claims or inaccessible infrastructure.

## Domain and safety scope

- Initial application: **prioritize compounds for in-silico retrospective assay screening** only.
- No drug synthesis protocols, wet lab execution, real patient decisions, human clinical treatment, claimed drug efficacy, or automated GMP operational action.
- **Digital Twin readiness** is an architectural direction. The baseline is not a connected or validated Digital Twin.
- No internal data, code, documents, product formulas, credentials, names of internal staff, restricted brand assets or sensitive GPO work artifacts in the personal Git repo.
- No public deployment, repo sharing or external push without owner-authorized target and visibility. Publish screenshots only after checking all data and attribution.
- The GPO name may be mentioned only as **presentation audience/context**, never as owner/sponsor/endorser; logo is excluded absent written permission.

## Engineering targets (demonstrable, not artificial claims)

- `make demo` or documented equivalent: succeeds on CPU with a local synthetic fixture without internet or API key.
- Web app starts and completes one sequential run; user can change budget and seed and compare at least three independently implemented policies.
- Each run shows selected compound IDs, actual revealed labels in its own scope, remaining budget, cumulative hits, provenance and policy name.
- Test suite covers budget overspending, duplicate charging/hits, deterministic replay, pending-feedback visibility, truth leakage, invalid actions, unsupported target and corrupted input.
- One exportable run report and at least one visual comparison chart; explicit synthetic/public source indicators.
- Where RL is shown, it is a real trained/evaluated policy with algorithm/training data/seed explained. Otherwise show the RL capability as `PLANNED`, never a fabricated result.

## Success is not publication

A useful portfolio can be complete even if RL underperforms strong active-learning baselines or no journal paper results. A later research contribution would require external benchmarks, independent comparisons and uncertainty intervals. It must not block the first product demonstration.
