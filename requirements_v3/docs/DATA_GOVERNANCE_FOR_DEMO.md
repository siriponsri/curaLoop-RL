# Personal repo boundaries — data, IP, branding, security

## Default rule

Use only deliberately created synthetic fixtures or datasets with documented public access, permitted use and redistribution terms. A project shown **inside** a company is not automatically a company project, and it is not automatically authorized to use company information. Organizational IP/side-project policies and employment agreements may apply; the owner should check those before publishing or sharing. No legal determination is made by this pack.

## Excluded by default

- Nonpublic GPO data, assay results, SOPs, formulations, procurement records, production logs, LIMS extracts, employee/patient data, equipment screenshots, network topology, credentials or internal URLs.
- Logos, official seals, graphic identities or text that creates an impression of organizational endorsement.
- Unreviewed papers or software libraries with uncertain redistribution rights; do not bundle their PDF binaries or source code by assumption.
- Any material where the origin of the values cannot be traced to a public dataset or a clearly synthetic generator.

## Provenance tags

- `SYNTHETIC_ONLY`: generated fixture with seeded fake truth, including costs/delays.
- `HISTORICAL_PUBLIC_DATA`: original historical, accessible assay labels with manifest and license/terms.
- `SYNTHETIC_SCENARIO_OVERLAY`: **display label only** for `data_origin=HISTORICAL_PUBLIC_DATA` with `scenario_origin=SYNTHETIC_ASSUMPTION`. Keep both dimensions separate in event/manifest schemas.
- `AUTHORISED_PRIVATE_DATA`: future-only mode after documented permission; excluded from the public personal repo, screenshots and exports by default.

## Before pushing to a public GitHub repository

1. Check the repo's license and third-party notices. Do not assume a dataset license equals a software code license.
2. Inspect `.gitignore`, Git history, artifacts, logs and images for secrets, identifiers and proprietary materials.
3. Keep dataset downloader and provenance manifests; do not commit redistributed data unless licensing explicitly permits it.
4. Review README and screenshots for claims of organizational approval and unsupported clinical/drug claims.
5. Confirm that the chosen GitHub account and destination are personal and owner-approved.
6. Keep hosting optional; local demo or recorded video is sufficient. No cloud paid service is required.

## Working with real data later

Real experimental data require a designated data controller, access permissions, suitable data agreement, assay/endpoint definition, expert validation and separation of duties. A regulatory or GMP-impacting workflow additionally requires organization-specific change control, validation and IT security requirements. None of these are represented as completed.
