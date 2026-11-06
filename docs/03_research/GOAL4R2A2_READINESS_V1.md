# Goal 4R2-A2: source and benchmark readiness

6 November 2026. **READINESS WORK COMPLETE; ENGINEERING PASS;
SCIENTIFIC PILOT NO_GO.**

The approved metadata-only goal answered two concrete questions: whether the
MF-PCBA publication identities can be observed through an allowed description
endpoint, and whether MolDesignBench directly evaluates the intended R&D
evidence/plan/report workflow. It did not open assay activity or benchmark task/
gold rows. The [execution contract](../06_execution/GOAL4R2A2_EXECUTION_CONTRACT_20261106.md),
[evidence index](../evidence/goal4r2a2-20261106-v1/README.md) and
[closeout](../06_execution/GOAL4R2A2_CLOSEOUT_20261106.md) define scope and delivery.

## Decisions supported by actual evidence

| Question | Result | Meaning |
| --- | --- | --- |
| Can descriptions be retrieved for the fixed 105 AIDs? | PASS: 105/105, no failed request | Description metadata coverage, not compound follow-up coverage |
| Do observed version/revision fields match SI S19? | PASS: 105/105 | Metadata concordance only; historical activity bytes are NOT_CERTIFIED |
| Can publication modification dates be compared? | UNKNOWN: inspected date field absent in 105/105 | Complete AID/version/revision/date tuples remain INDETERMINATE |
| Does the description operation enforce a historical selector? | NOT_VALIDATED: negative control returned current metadata | Do not rely on that selector for historical reconstruction |
| Are scientific endpoints/families/cohort cleared? | NO_GO; eligible count UNKNOWN; zero certified groups | Metadata does not identify row-level observation support or independent families |
| Do ten frozen metadata/compatibility cases execute? | PASS: 10/10 on dr-train | Engineering contract evidence, not scientific or agent performance |
| Is MolDesignBench a direct plan/report benchmark? | NO_GO | Native output is molecule SMILES or `None`; CuraLoop outputs plans/reports |
| Can it serve as an auxiliary design benchmark? | CONDITIONAL_GO | New adapter, rights, exposure/roster, runtime and execution approval required |
| Is commercial use of its dataset cleared? | NOT_CLEARED | Dataset declares CC BY-NC 4.0; code MIT is separate |

## MF-PCBA source and observation register

The paper-backed source remains Buterez et al., JCIM 2023,
[DOI 10.1021/acs.jcim.2c01569](https://doi.org/10.1021/acs.jcim.2c01569).
The previously audited 47-page owner-supplied SI identifies sixty stage pairs
in Table S2 and 105 distinct AID version/revision/date tuples in S19. The source
repository inspected at commit `776cb013a5ab9949adfc9c11a212cd7ad7dada7a` remains
distinct from an exact paper-experiment snapshot.
[Prior SI audit](../evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json),
[official source repository](https://github.com/davidbuterez/mf-pcba/tree/776cb013a5ab9949adfc9c11a212cd7ad7dada7a).

Actual retrieval used the existing PubChem skill client, with only GET
`/assay/aid/{aid}/description/JSON`. A successful initial AID 873 probe was reused;
104 additional current descriptions and two selector controls followed. There
were **107 requests total**, no automatic denial/rate-limit retries and no
full-record fallback. The roster job used 8.812219154 measured CPU-seconds and
211.443808 wall-seconds on one CPU; these are metadata acquisition measurements,
not molecular-policy timing.

The [request receipts](../evidence/goal4r2a2-20261106-v1/request-receipts-v1.json)
retain endpoint, options, UTC, HTTP status, response size and SHA256. Saved raw
responses are HTTP-decoded text encoded as UTF-8, rather than original wire-byte
captures. Full descriptions/protocol text remain in private complete retention.
The [derived register](../evidence/goal4r2a2-20261106-v1/readiness-audit-v1.json)
links each published tuple to its observed fields, pointers, provider/source ID,
target IDs and response hash. The [readout register](../evidence/goal4r2a2-20261106-v1/readout-definitions-v1.csv)
contains factual column definitions; it has no SID, compound or activity rows.

Observed metadata includes eleven provider names and **3,287 readout definitions**.
Target lists are present for 95 AIDs and absent for ten. These counts do not
establish unique targets, biological families or useful scientific endpoints.
All 105 readout-definition fields are present. Unit fields are present in 1,945
definitions and absent in 1,342. Raw codes 5, 10, 14, 15 and 254 are retained
without decoding or assuming potency units; zero, absent and null remain distinct.
No scientific endpoint was selected from a name or count alone.

| Provider name as observed | Distinct AIDs |
| --- | ---: |
| Broad Institute | 62 |
| Burnham Center for Chemical Genomics | 12 |
| Emory University Molecular Libraries Screening Center | 2 |
| ICCB-Longwood/NSRB Screening Facility, Harvard Medical School | 2 |
| Johns Hopkins Ion Channel Center | 10 |
| PCMD | 2 |
| SRMLSC | 3 |
| Southern Research Institute | 3 |
| Southern Research Specialized Biocontainment Screening Center | 5 |
| The Scripps Research Institute Molecular Screening Center | 2 |
| Vanderbilt Screening Center for GPCRs, Ion Channels and Transporters | 2 |

These are source/depositor names, not certified distinct institutions or licence
scopes. The provider register explicitly leaves source-specific terms URLs and
analysis/adaptation/redistribution/commercial permissions unresolved. Article
CC BY 4.0 and code MIT do not automatically clear contributed assay data.
PubChem's policy allows public access while warning that contributed material
may be copyrighted and users remain responsible for restrictions.
[Official submission policy](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/data-submission-policy.md).

### Historical-selector control

For AID 873, current metadata reports version 1, revision 13. Both
`?version=1.13` and deliberately invalid `?version=999999.999999` returned
HTTP 200, the same 1/13 fields and byte-identical saved response text, SHA256
`6a650785d737d7e860d74ebb17a23fd4639f1a380896c8a68bcfe10d73e40d13`.
Thus the negative control fails to establish selector enforcement for this
description operation. This does not establish that every PubChem operation
ignores versions, or that historical retrieval is impossible.

Official REST documentation illustrates old-version retrieval for a full-record
operation, which may contain experimental rows and was outside A2. SOAP
description metadata has optional version/revision/LastDataChange fields but no
documented historical input selector. `LastDataChange` concerns data changes for
tested SIDs; it must not be equated with the SI modification date, HTTP headers
or retrieval UTC. The normalized field was absent here; no substitute date was
invented. [REST specification](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/pug-rest.md),
[SOAP reference](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/pug-soap-reference.md).

All 105 current version/revision pairs matching SI is encouraging identity
evidence. It does not close the reconstruction differences: source-code default
SD median versus paper mean; structure-processing conventions; activity-sorted
deduplication; separate-AID missing-potency flooring versus same-AID filtering;
and the absence of a general exact/censored/untested observation contract.
AC50 labels are assay-specific, rather than a universal biological endpoint.
[PubChem glossary](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/glossary.md).

## Proposed observation/population protocol

This is a justified candidate protocol, **not a frozen cohort or approved pilot**.

1. Bind each pair to an inspected source artifact and explicit readout/TID,
   endpoint direction, units and qualifier semantics. Decide exact historical
   reconstruction versus a named current-source reconstruction before comparisons.
2. Keep primary-tested, follow-up-performed, exact measured, censored/qualitative,
   inconclusive/invalid and never-followed-up states distinct. Retain selection
   provenance, replicates, deduplication and exclusions. A default potency floor
   cannot stand in for a missing experimental response.
3. For a conditional retrospective replay, define the population as compounds
   with prespecified eligible, observable follow-up support. Every permitted
   confirmation action must have a justified delivered observation. Report
   attrition and the conditional estimand: confirmed-hit discovery **within this
   selected historical population**, with any simulated cost/time stated as such.
4. Do not claim full-primary-library policy value from that subset. Unperformed
   confirmations have unidentified outcomes without additional justified coverage/
   selection assumptions or new experimental evidence. Censor-aware analysis
   requires its own endpoint and estimator decision.
5. Resolve provider rights, protected final-panel exclusion, exact structure
   overlap and target/family mapping before outcome use. Maintain the twelve-plus
   biological-group ambition; report the number actually qualified. Metadata
   counts and source names cannot substitute for that gate.
6. Freeze exposure, group roles, estimand, comparator, observation masks and
   budgets before development selection or validation. Earlier exposed FS-Mol
   validation groups stay exposed; original final outcomes remain reserved.

Current result: **full-library confirmation oracle NO_GO; conditional-cohort
membership and eligible group count UNKNOWN; scientific pilot NO_GO.** Zero
certified groups is a clearance count, not a statement that no biological groups
exist in the source. No observation population or scientific readout was frozen.

## Engineering checks and benchmark assessment

The ten cases were frozen before implementation, SHA256
`c1fca7585e0b49070678cfe41ebf6e490c24816f044d38be1299a46d3d471892`.
They cover strict bounded JSON, wrong IDs/duplicate rosters, observed version
comparison, absent/null/zero, source/unit uncertainty, rejection of data-bearing
payloads, source/rights/runtime blockers, exposure quarantine, manifest binding
and synthetic metric concordance. All ten actual META IDs executed and passed
on dr-train Python 3.12.3. [Check log](../evidence/goal4r2a2-20261106-v1/contract-checks-v1.log),
[results](../evidence/goal4r2a2-20261106-v1/contract-results-v1.json).

Read-only review identified five issues before validation: missing readouts
collapsed to zero, overflowing JSON numbers, inferred rather than executed case
IDs, unresolved split flags accepted as truthy, and unbound reused probe bytes.
All were corrected before the tested source freeze; selector denial/schema stop
handling was also checked. There were no post-test changes to the frozen worker,
contracts, jobs, cases or benchmark manifest.

The [MolDesignBench assessment](GOAL4R2A2_BENCHMARK_COMPATIBILITY_V1.md) documents
pinned sources, output mismatch, data restrictions, runtime requirements and an
important Feasibility F1 discrepancy between card and scorer. A prospective
grouped split quarantines exposed/unresolved examples, but no concrete roster
exists. Native benchmark evaluation, model/provider trials and live plugin
connections remain NOT_RUN. No task/gold rows were opened; the external schema
tool's unsuccessful internal preview attempt is disclosed separately.

## Next owner decision

The useful next research gate is **4R2-A3: historical observation qualification**,
proposed at eight CPU-hours / twelve elapsed hours / maximum two CPU workers on
dr-train, with no model campaigns. First resolve intended-use/provider rights
and exact source-operation boundaries. Only after those gates, inspect a bounded
development-only activity sample with explicit observation states, protected-panel
exclusion and an attrition report. Determine whether a conditional confirmation
study has an identifiable endpoint and enough eligible independent groups.
Stop and report NO_GO if it does not; do not silently substitute a full-library
oracle or relax the twelve-group research ambition. Data/row intake and this new
budget require owner approval and a detailed pre-intake contract.

A separate P1 integration goal can make the paper/database-to-report workflow
automatic, with a bounded model/provider evaluation and read-only live sources.
That is a product-engineering step, not evidence of a novel molecular method.
MolDesignBench should be auxiliary only if native molecular design becomes an
explicit product/research objective; it is currently unsuitable as the primary
workflow benchmark and should not be bundled into a commercial product dataset.

For the journal target, dataset compatibility and audit infrastructure strengthen
reproducibility but do not yet establish a publishable method contribution.
The next scientific claim must be supported by a matched decision-value study
with measured outcomes and uncertainty. No submission, payment, prospective
laboratory benefit or broader Goal4 advancement is claimed by A2.
