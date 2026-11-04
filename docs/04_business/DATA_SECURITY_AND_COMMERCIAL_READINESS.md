# Data handling and commercial readiness

## Current deployment boundary

The current application is single-owner, loopback-only and designed for a local workstation. SQLite snapshots contain public campaign records; hidden historical truth remains in the backend resource. Browser-origin checks and process separation support this architecture but do not provide enterprise identity, encryption policy, access review or customer tenant isolation.

A commercial pilot should therefore begin with a controlled local evaluation. Before accepting proprietary inputs, agree who can access the machine, where backups live, what is exported and who may view results. Audit logs may contain molecular identifiers or structures and can themselves be confidential. A claim that the database stores only “public snapshots” describes the software boundary, not the confidentiality status of a future customer's data.

## Proposed intake controls

Validate structure formats, size limits, finite numerical features, allowed endpoint values and identifier uniqueness. Reject executable uploads and unsafe serialization. Keep raw inputs immutable, separate derived features from truth and record transformations. Do not send structures or assay labels to external APIs without specific permission. The present POC has no operational LLM workflow, so there is no reason to introduce a model API into a customer-data path by default.

## Readiness levels

| Level | Intended activity | Evidence needed |
| --- | --- | --- |
| L0 | Public-data demonstration | Working local release and transparent limitations |
| L1 | Controlled historical customer pilot | Agreed data schedule, supported environment, scoped adapter and tested backup/export |
| L2 | Repeated team use | User/access design, maintenance, support, failure handling and security review |
| L3 | Operational or regulated integration | Customer-specific intended-use assessment and required validation programme |

The current package documents L0 and a proposed L1 path. It does not certify any readiness level. Do not bind the existing service to a public interface to imply L2 readiness.

## Rights and dependencies

The core code retains MIT terms. Third-party software, data, paper PDFs and generated artwork have separate notices. Inspect the exact versions and rights before redistributing a customer bundle. Downloaded reading copies are outside the public repository payload. Source citation is necessary but does not by itself grant every redistribution or commercial-use right.

## Actual-claim discipline

Do not assert regulatory approval, medical-device classification, GMP readiness or organizational endorsement without a relevant factual basis. Any future intended-use change needs customer-specific review. This document defines a product evidence boundary rather than a jurisdiction-specific legal or regulatory opinion.

## Local backend and paper provenance

A local open-source acquisition adapter is not permission to transmit molecular libraries to a remote service. Record dependency versions, source licenses, data flow and the fields passed to the backend. Keep supplied reading PDFs outside the customer/public source payload unless the particular distribution and attribution have been reviewed. Publication of a paper and licensing of its underlying assay data are separate questions.
