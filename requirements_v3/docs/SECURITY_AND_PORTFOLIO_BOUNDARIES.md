# Security, Organizational Boundaries and Sharing Checklist

**Scope:** personal independent code portfolio to be shown to pharmaceutical R&D professionals. Mentioning a possible GPO audience does not imply organizational ownership, sponsorship, approval or permission to publish internal information. Review local employment/IP/conflict policies independently.

## Restricted by default

No real internal assay files, proprietary formulae, batch records, GMP SOPs, LIMS/ERP logs, business pricing, product portfolios derived from confidential records, personal data, hospital/clinical results, company logos or seals, internal APIs, access tokens, work email lists, internal URLs, network diagrams, or screenshots from company systems.

## App boundaries

- UI accepts only synthetic source data at first. Later CSV loader must reject files that are too large, unknown fields, executable objects, invalid encodings, path traversal, absolute/traversal export paths and unexpected MIME/extension combinations.
- No `pickle.loads` or untrusted serialized model loading; trusted model artifacts only, with checksum and owner provenance.
- Local run data and event logs may expose assay labels: when historical public dataset is used, follow source terms; prevent hidden-truth export until assays have been revealed in that specific run.
- Log only model configuration/IDs, not secrets, full environment variables or employee file paths. Prefer relative paths and `.env` in `.gitignore`.
- Do not publish GitHub repo or demo URL automatically. Confirm target, account, visibility, licenses, screenshot/data content and user approval. Make local Git commits without remote push.

## Licensing notes

Code license: MIT is reasonable for independently authored original code, subject to the owner's review; it cannot assign rights in third-party software, source paper PDFs, datasets or copied figures. Third-party full-text PDFs need article-specific redistribution license and attribution. The packaged bibliography is not evidence of copyright clearance. Public dataset access does not necessarily permit bundling or commercial reuse.

## Honest institutional narrative

Suggested wording: *'Independent personal prototype demonstrating AI-assisted screening decisions using synthetic and public research data; not affiliated with, validated by, or deployed in the Government Pharmaceutical Organization.'* Avoid GPO in the repo title, badges, logos and URLs unless permission is explicit.

## Release review

Before first external sharing: owner reviews `git log --stat`, staged files, `.gitignore`, secrets scan, dependency license list, dataset attribution, article citations, exported figures, screenshots, claims about cost and status of Digital Twin/RL. If any company policy conflicts, keep demo local/private and seek appropriate authorization; this pack does not provide legal advice.
