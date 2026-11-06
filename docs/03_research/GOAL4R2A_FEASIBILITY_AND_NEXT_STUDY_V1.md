# Goal 4R2-A feasibility and next-study specification

6 November 2026. **OFFLINE ENGINEERING PASS; SCIENTIFIC ADVANCEMENT NO_GO.**

The [approved contract](../06_execution/GOAL4R2A_EXECUTION_CONTRACT_20261106.md)
asks for a feasibility prototype and a source-backed research decision, not a
scientific campaign. The twelve frozen workflow cases and eight added boundary
checks passed on dr-train. This does not establish autonomous-agent quality,
live integration, molecular discovery gains or a new method.

## Engineering result and implemented boundary

The new `curaloop_rd` package is independent of the application and frozen
research engines. It exposes offline catalogue search/source inspection, typed
plan construction/validation, local report bundles and preview receipts. A
SQLite store enforces run identity, expected revisions and durable workflow
stages. Complete temporary files are published atomically; interrupted partials
remain for inspection and do not block resume. Exact preview retries return
one content-checked receipt. Report, stored-plan and receipt tampering is rejected.

The public demonstration uses a fixed synthetic catalogue, including measured,
censored, default-filled, missing, untested, predicted and metadata-only status
examples. It contains no compound measurements. It records illustrative proposed
cost, no executed assay cost, null confirmed hits and `delivered=false`.
Reserved-role and registered synthetic-alias checks precede payload inspection.
These are fixture gates, not a complete registry of the real reserved panel.
There is no external-source adapter through which that panel could be retrieved.

All twelve engineering cases were fixed before implementation. A read-only
review identified partial-write recovery, stored-identity and exact-retry defects;
they were repaired before the first remote check. First execution passed all
20 checks. Tests cover this prototype only; application/frontend/browser suites
and live-source/LLM/MCP evaluations were not rerun.

See [case results](../evidence/goal4r2a-20261106-v1/case-results-v1.json),
[runtime identities](../evidence/goal4r2a-20261106-v1/source-freeze-v1.json),
[metadata projection](../evidence/goal4r2a-20261106-v1/metadata-audit-v1.json),
and the [synthetic report](../evidence/goal4r2a-20261106-v1/demo-report.md).

## Candidate data: what the audit actually established

The [metadata register](../../research/manifests/goal4r2a_mfpcba_metadata_v1.json)
pins official source commit `776cb013a5ab9949adfc9c11a212cd7ad7dada7a`.
Sixty retrieval-script names project to 54 distinct primary and 60 distinct
confirmatory AIDs; nine definitions use the same AID for both stages. The
projection was independently checked on dr-train. The subsequently supplied
47-page SI corroborates all 60 stage pairs in Table S2 and specifies version,
revision and last-modification date for all 105 distinct AIDs in Table S19
(PDF pages 46–47). Every script body was not independently parsed. Dataset
definitions are not independent biological families.

The [supplementary metadata audit](../evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json)
records every published version tuple. Earlier pending-SI fields in the frozen
candidate register remain historical; this supplement closes the publication-
metadata access gate. It does not establish that newly retrieved assay rows
match those historical versions.

| Gate | Outcome |
| --- | --- |
| Primary publication/source identity | Identified: Buterez et al., JCIM 2023, DOI 10.1021/acs.jcim.2c01569; pinned source code |
| Publication-specific assay revisions | PASS metadata: SI Table S19 covers all 105 AIDs; historical row reconstruction NOT_RUN. The first supplied PDF was a 12-page primary article; the separate SI was then supplied and inspected |
| Article/software licences | Source reports article CC BY 4.0 and software MIT; underlying provider-row redistribution NOT_CERTIFIED |
| Uniform exact/default/censor status across all datasets | NOT_ESTABLISHED; notebook paths handle same-AID and separate-AID datasets differently |
| Biological grouping and independence | UNKNOWN; zero groups certified by this audit, not zero biological diversity |
| Eligible scientific datasets | UNKNOWN; zero datasets cleared by this audit |
| Compound coverage/overlap and reserved-panel exclusion | NOT_RUN; no activity-table or compound-row intake |
| Unrestricted primary-library confirmation oracle | NO_GO from currently established observations |
| Actual assay time/cost or therapeutic selectivity | NOT_ESTABLISHED |

Pinned retrieval code defaults to median primary aggregation where the paper
reports mean; current retrieval also uses live unversioned endpoints and a
different molecular field. A contemporary download is not automatically a
paper-exact reconstruction. Same-AID default handling and separate-AID numerical
missingness flags do not supply a universal physical measurement-status schema.

The required states are exact measured potency, tested-but-censored/qualitative
confirmation, and no confirmation follow-up. Keep relation, concentration, unit,
endpoint and protocol information. A dataset-minimum replacement does not justify
a potency threshold, measured inactivity or a physical censor inequality.

Historical selective confirmation creates an additional missingness problem:
some possible actions have no observed outcome. A model's prediction does not
make such an action experimentally queryable. Restricting to a fully observed
historical confirmation cohort can support a prespecified conditional-population
replay, not a claim about the entire primary library. That population choice
requires a new design decision rather than a silent convenience filter.

## Novelty decision

**NO_GO on a novel molecular-method claim at present.** The engineering package
is useful infrastructure, but neither its typed checks nor its trusted output
ledger establishes the required research contribution.

[Multifidelity active search](https://proceedings.mlr.press/v139/nguyen21f.html)
already allocates budgets across cheaper and more expensive feedback.
[MolDesignBench v1](https://arxiv.org/html/2609.27349v1) evaluates constraints and
infeasibility, and [Autonomous Science Bench v1](https://arxiv.org/html/2610.18449v1)
uses experimental campaigns and authoritative measurement records. A new agent,
confirmation stage or replay ledger alone does not distinguish the method.

Read-only scientific review suggested the following candidate question:

> Can selectively resolving assay-level evidence improve confirmation decisions,
> after charging for evidence acquisition, compared with resolving all permitted
> metadata upfront and using a strong multifidelity policy?

The proposed uncertain variable concerns endpoint compatibility or source
interpretation shared across compounds. A permitted metadata query may resolve
that uncertainty; a confirmation query reveals an available measured compound
outcome. A candidate decision rule would compare the estimated effect on the
remaining confirmation plan against evidence-acquisition opportunity cost.
Generic value-of-information reasoning already covers this pattern. No distinct
algorithm, valid case population or superiority has been established here.

## Conditional next-study design, not an execution protocol

| Element | Requirement before a scientific pilot |
| --- | --- |
| Primary question | One frozen evidence-resolution decision principle, explicitly different from closest work, or stop the method claim |
| Outcome | Source-confirmed positives under a declared budget; phenotype/qualifiers and observable population fixed before activity inspection |
| Observation contract | Each action returns an actually recorded permitted observation; unmeasured confirmations are not invented. A simulated-oracle study would require a separately labelled question |
| Controls | Typed validator plus cheap fixed rule; same predictor plus objective-matched MF search; resolve-all-metadata-upfront control; fixed retrieval/confirmation policy with the same evidence |
| Reference | Perfect compatible metadata without outcome information, to test whether evidence resolution offers any remaining value |
| Agent comparison | Same model with ordinary search and the same tools/quotas; separate from the scientific-policy comparison |
| Resource accounting | Charge retrieval and measurement operations; keep assumed laboratory costs/time separate from measured CPU and actual operational evidence |
| Exposure/split | New task/source and compound-overlap manifests; do not reuse exposed validation as untouched. Existing final outcomes remain reserved |
| Population breadth | Aim at 12 or more verified biological groups if genuinely eligible; report actual counts and consult before changing design |
| Mechanism test | Remove adaptive evidence resolution while holding predictor, population, observations and budget fixed |
| Interpretation | Report task/group estimates and uncertainty; no material-effect confirmation threshold is inferred from this prototype |

If relevant metadata is cheap and available upfront, that control may remove the
entire proposed mechanism. If confirmation observations do not identify policy
value, do not run a larger benchmark to conceal the problem. Stop or seek an
explicit different data/population design.

No molecular model fit, assay campaign, scientific dataset/benchmark expansion, new outcome release,
LLM evaluation or method-comparator reproduction ran in 4R2-A. The worker that
performed the 20 checks, metadata projection and demo recorded roughly 0.20
CPU-seconds, but that number cannot estimate molecular pilot runtime. A scientific
resource estimate remains NOT_MEASURED; the earlier
8 CPU-hour pilot suggestion is a provisional ceiling to reconsider after data
and method gates, not a certified allocation or new authorization.

## Next decision

Consider the [dataset/benchmark expansion proposal](../06_execution/GOAL4R2A_EXPANSION_PROPOSAL_20261106.md)
to resolve source identity and observation support before a scientific pilot.
P1 integration and external workflow evaluation remain separately useful product
steps. Neither product usefulness nor the possibility of a journal route changes
the present NO_GO on a novel molecular-method claim.
