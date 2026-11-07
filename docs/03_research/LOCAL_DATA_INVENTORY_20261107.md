# Local data inventory and readiness for independent Deep Research

Snapshot: **7 November 2026**. Repository base at inspection:
`1c849d38d7c6b07b20c16f38f2ad6f57251558ea`.
This is a local inventory and document handoff, not an R0-QC run, new dataset
qualification, source intake, model experiment or split change.

**Main finding: several real datasets already exist locally. What remains
unqualified is the benchmark for the newer joint evidence/molecular-decision
question.** The older screening/planning data and the newer evidence-sensitive
task have different requirements and must not be described as one readiness state.

## What was checked now

The file-metadata scan covered `research/`, `.local/`, `src/curaloop/resources/`,
`papers/` and the task workspace `C:\Users\User\Documents\ChatGPT\Drug Discovery`.
It listed **22,309 matching data-like/document files, 35,649,199,993 apparent
file bytes (35.65 decimal GB; sum of file lengths, not allocated disk blocks)**, with no scan errors. Dependencies/UI caches and
aliases were skipped. The extension allowlist and excluded directories are
recorded in the [filesystem summary](../evidence/local-data-inventory-20261107-v1/filesystem-summary-v2.json).
These are matching files, not 22,309 datasets or unique experimental records.
The scan did not cover the whole computer, other drives, Downloads or dr-train.

A separate bounded opaque-byte check freshly matched **28 small files / 6,799,216
bytes** against existing manifests: the HIV replay, three Tox21 derivatives and
all 24 FS-Mol revision-A feature files. It did not decode JSON dataset rows,
arrays, labels or archive members. See [small-file integrity](../evidence/local-data-inventory-20261107-v1/small-file-integrity-v1.json).

Large archive sizes/existence were checked now; their hashes below are from
earlier verified receipts, **not a new multi-GB digest pass**. Aggregate row/task
counts are from the cited manifests/cards, not new raw-row counts. No activity
values, per-record numerical-presence flags, final outcomes, raw SQLite tables
or source PDF text were opened. No SSH or scientific HTTP was used.

## Logical inventory

| Asset | Actually available | Readiness for its existing use | Limit for the new research question |
| --- | --- | --- | --- |
| MoleculeNet HIV replay | Verified packaged 1,200-compound subset and provenance manifest | Exposed application/replay data | One assay population; no multi-context reference benchmark or fresh final test |
| NCATS Tox21 | Three raw endpoint exports and three verified 600-row prepared derivatives | Exposed development data, 1,800 task rows | Correlated pathways, cross-endpoint compounds and synthetic operations; not independent new-family replication |
| FS-Mol original | Full `fsmol.tar`, 4.871 GB; source metadata and historical digest | Real source archive present | Original few-shot/potency-relative binary task differs from current Ki/Kd/reference-context task |
| FS-Mol revision-A features | 24 verified feature files; 6/2/16 development/validation/final assays | Prepared under the older feature/readiness contract | Final outcomes reserved; annotation-connected groups are not certified biological families; no new-method result |
| ChEMBL 37 original | Exact 5.764 GB source archive plus two complete private return archives | Raw source preserved, historical full hash/schema proof | Complete source availability does not establish suitable assay panels, construct truth or evidence-action value |
| ChEMBL derived audits | Metadata/context slices, complete old support graphs and frozen candidate manifests | Existing blinded feasibility diagnostics | Latest frame has one nominal development pair, no certified new final tasks or independent reference gold |
| MF-PCBA / PubChem | Main paper + SI PDFs, scripts/metadata, structure qualification and small canary responses | Partial acquisition/readout/provenance research | No complete qualified paired-stage cohort; current/revision equivalence and product data rights remain unresolved |
| Protein/family metadata | ChEMBL mapping, UniProt/InterPro caches and registry v1/v2/v3 | Label-free lineage/protection inputs | Coverage/version/scope incomplete; transitive broad-domain links must not become convenient family counts |
| MolDesignBench | Metadata/card/code assessment only | Candidate lead, not ingested task dataset | Task/gold intake NOT_RUN; noncommercial terms and native tool/output mismatch |
| Methods/literature and workflow cases | Owner papers, masked context projections and authored cached-metadata briefs | Supporting evidence and engineering tests | Not independent molecular reference gold, experimental measurement panels or customer validation |

## 1. MoleculeNet HIV

Local files: `src/curaloop/resources/hiv_manifest.json` and
`src/curaloop/resources/hiv_replay_v1.json.gz` (**103,010 bytes**, freshly
hash-matched). The manifest records source 41,127 rows, seven invalid SMILES
removed, 41,120 valid unique source rows and an outcome-blind 1,200-row sample.
The original full HIV CSV was not independently identified as a standalone
source in this scan; do not mistake `hiv-benchmark/benchmark.csv.gz` run output
for that source. An old reproduction checkout also holds a duplicate replay.

Declared schema/semantics: canonical isomeric SMILES, Morgan radius-2/1,024-bit
features, Murcko scaffold and historical binary assay activity. Cost/delay are
synthetic scenario assumptions. This is a custom replay subset, not an official
MoleculeNet/TDC split reproduction or evidence of therapeutic efficacy.
Source paper identity: MoleculeNet, DOI `10.1039/C7SC02664A`.
The manifest records a CC BY 4.0 source notice via TDC; this audit does not
renew license or commercial-use clearance.

## 2. NCATS Tox21 development data

Local root: `research/raw_data/ncats-development-20261104/`.
Raw exports are `ahr.smiles` (472,354 bytes), `pparg.smiles` (455,392 bytes),
and `p53.smiles` (494,124 bytes), with receipts. Prepared files are
`prepared-v1/ahr.json`, `pparg.json`, `p53.json`; all three freshly hash-match.

| Endpoint | Source identity | Recorded raw rows | Prepared task rows |
| --- | --- | ---: | ---: |
| AhR | AID 743122, NCATS 2014 training | 8,169 | 600 |
| PPAR-gamma | AID 743140, NCATS 2014 training | 8,184 | 600 |
| p53 | AID 720552, NCATS 2014 training | 8,634 | 600 |

The 1,800 prepared task rows are **not 1,800 independent unique molecules**.
Prior preparation records canonical overlaps of 52/52/36 across endpoint pairs.
All three endpoints and pools are development-exposed, never fresh final tests.
The source binary labels are pathway/assay activity; simulated costs/time and
the custom discovery metric are separate. Paper identity:
`10.3389/fenvs.2015.00085`; source-row counts differ from the paper's training
sample count and remain documented. Existing local-use rights review does not
automatically grant every proposed downstream commercial data use.
Evidence: [task registry](../../research/manifests/ncats_development_tasks_v1.json)
and [Goal 2 protocol](GOAL_02_REAL_DATA_PROTOCOL_V1.md).

## 3. FS-Mol source and prepared features

Source path: `research/raw_data/external-benchmarks/fs-mol-0.1/fsmol.tar`.
Current size **4,871,086,080 bytes**. Historical verified SHA256:
`528a9c4e8d74c4287acda79536eecbf91418d6d0ac2c55918b270d78c2333ebc`.
The file is an uncompressed tar, not tar.gz. Source record:
`10.6084/m9.figshare.16941100.v1`; associated paper: Stanley et al., NeurIPS
Datasets and Benchmarks 2021. The earlier official download returned 403 and the
owner supplied the file; no retry or member read occurred in this audit.

The pinned default manifest has **5,135 tasks** (4,938 train / 40 validation /
157 test), whereas the paper reports 5,120. The 21,930 additional physical
training files are outside the pinned default population. These counts are
historical source/manifest findings, not a fresh tar enumeration.

Prepared path: `.../feature-cohort-v2/`. The scan found **24 `.features.json`
files**, all freshly hash-matched to the revision-A result. The folder has
29 matching files including metadata/receipts. The first, smaller v1 remains
for failure history; it is not an additional independent cohort.

| Custom role | Annotation-connected groups | Assays | Structure rows | Unique structures, from card |
| --- | ---: | ---: | ---: | ---: |
| Development | 4 | 6 | 1,285 | 1,107 |
| Validation | 2 | 2 | 330 | 330 |
| Final, outcomes reserved | 12 | 16 | 5,015 | 4,416 |

Total: **24 assays / 6,630 structure rows**, not a new cross-assay context
benchmark. Hashing final feature bytes did not load final labels. Original
source train/valid/test roles are provenance, not the custom CuraLoop roles.
Never infer authorization from an upstream split name.

The six development and two validation assays were used in the older Goal 4
experiments; their previous validation label does not make them fresh for the
new hypothesis. The later 4R1 diagnosis used only the six exposed development
assays. Reserved final outcomes remained closed in those studies.

The registry accepted 2,884 of 5,135 source tasks into 139 transitive annotation
components; its largest development component joins 87 broad names. The selected
12 final groups are **not 12 independently certified evolutionary families**.
Features are canonical isomeric SMILES, nonchiral Morgan radius-2/1,024-bit fingerprints and
Murcko scaffolds. Exact-role overlap was removed under the old contract, but
63 development/final scaffolds were shared and high fingerprint similarities
remain; there is no chemical-OOD claim.

FS-Mol uses assay-relative potency-derived binary labels, with a deliberately
balanced positive ratio. They are not sparse therapeutic hit calls, and not
continuous Ki/Kd reference values. ChEMBL 27 source provenance was mapped using
later ChEMBL 37/UniProt 2026_04/InterPro 110.0 metadata; historical annotation
equivalence is not automatically certified. Figshare CC BY 4.0 and repository
dataset CC BY-SA 3.0 notices differ; preserve both pending intended-use review.
Evidence: [latest dataset card](FSMOL_DATASET_CARD_V2.md),
[feature result](../evidence/plan-a-20261105-v1/feature-cohort-v2-result.json),
[archive receipt](../evidence/fs-mol-receipt-20261105-v1/archive-verification.json).

## 4. ChEMBL 37: complete source, incomplete new benchmark

The source archive exists at
`.local/chembl-taskfirst-dqr-20261107-v1/source/chembl_37_sqlite.tar.gz`,
**5,764,252,857 bytes**, with historical SHA256
`33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281`.
The source DB was verified remotely as **30,480,314,368 bytes**, SHA256
`4be13df3b68e25dcd0bff44bf094033b5aebe98f415acdc8c1cdf380e0c15142`.
It is retained inside complete returned archives, not expanded locally.

| Local complete return | Current bytes | Historical complete-return SHA256 |
| --- | ---: | --- |
| `.local/chembl-taskfirst-dq-20261107-v1/remote-return/full-task-v1.tar.gz` | 11,070,386,037 | `981b4ff3d1c0180c70a7b21e11ecef3a24ad2b98011673097b6df0db7e87cefc` |
| `.local/chembl-taskfirst-dqr-20261107-v1/remote-return/full-task-v1.tar.gz` | 11,071,998,021 | `ed1d27411f280fba174ad2cd06fd44207cb5a7359a7eecd6ee82d3495534d38a` |

These include the **same source DB/archive** plus different code/derivations;
they are two physical preservation packages, not independent datasets.
The source DB byte count cannot be added to local expanded storage as if a
second local DB existed. Total raw activity rows were not counted in this audit.

| Existing audit | Scope already recorded | What it establishes |
| --- | --- | --- |
| Initial R0/R0-R/A1 | 50 assays in readiness; 12 frozen context cases; 10 admitted projections / 86 records / 80 molecules | Small metadata/reference-feasibility slice; no independent gold or decision gain; same-target ghrelin subset has one molecule |
| R0-DQ | 8 targets / 121 complete assays / 8,231 topology rows / 5,549 source molecule IDs | Two 128-compound support candidates in one development unit; source/construct truth unqualified |
| R0-DQ-R | 11,055-target inventory; 200 targets / 1,254 complete assays / 16,862 topology rows / 12,873 source molecule IDs | One nominal development pair; no new numeric validity/presence query or qualified final task |

These overlap and must not be summed as independent populations. ChEMBL fields
such as accession/organism, assay context, endpoint type/unit/relation, document
DOI and molecule identity support qualification. Their existence alone does
not prove comparability, numerical completeness or useful information gain.

The latest nominal pair is FcRn **CHEMBL5966/P55899**, Kd reference
CHEMBL956457/552585 and IC50 auxiliary CHEMBL956456/552584. It has 149 nominal
reference canonical identities, a 128-member panel and 115 shared compounds.
Family/construct/reference truth remain unreviewed; numerical validity was not
queried. Its primary source is CHEMBL1150419,
DOI `10.1016/j.bmc.2008.05.004`; previous access checks found no confirmed OA route,
not universal unavailability. Complete metadata already distinguishes SPR / pH 6
from IgG-binding ELISA. No paper-only decision-changing fact was established.

The old two Ki diagnostics involve A3/H3 targets and four primary source DOIs:
`10.1016/j.bmc.2009.05.038`, `10.1016/j.bmcl.2011.07.006`,
`10.1021/jm049662f`, `10.1016/j.bmcl.2010.04.045`. Their checked access metadata
did not supply methods bodies. Do not add them to the new one as three
independent qualified tasks.

Current lineage limits: 10,008 of 11,052 single-component targets lack an
unambiguous inherited mapping, plus three unresolved-component targets.
Four old DOI/group-ID components mix frame-role labels over 85 targets
(78 development, 6 final, 1 validation); source-key namespace also needs review.
CHEMBL8809 canonical alias reconciliation remains pending. No final use is cleared.
Evidence: [R0-DQ](R0DQ_QUALIFICATION_RESULTS_20261107.md),
[R0-DQ-R](R0DQR_TAXONOMY_TASK_FEASIBILITY_20261107.md),
[exposure audit](../evidence/chembl-taskfirst-dqr-20261107-v1/exposure-quarantine-audit-v1.json).

## 5. MF-PCBA and the limited PubChem payloads

Physical source PDFs exist:
`research/raw_data/external-benchmarks/mf-pcba-2023/metadata/ci2c01569.pdf`
(3,271,821 bytes) and `ci2c01569_si_001.pdf` (4,674,245 bytes).
Paper identity: `10.1021/acs.jcim.2c01569`. The SI has already supported a historical
version/revision metadata audit. This inventory did not reread PDF contents.

The initial manifest identified 60 script definitions/105 distinct AIDs; later
work inspected the scripts, 3,287 readout definitions, target/provider metadata,
53 readout bindings and 47 pairs jointly passing scoped source/binding review.
These counts describe metadata/permissions, **not 47 qualified measured pairs**.
Ninety-five AIDs had scoped internal-use support; publication, redistribution
and commercial row use remain NOT_CLEARED in project records.

Five development candidate pairs supplied 640 sampled common-listed SIDs, 589
cleared structures, 45 ambiguous/missing mappings and 6 protected exclusions.
Listed membership is not evidence of an actually measured cell. The early
16-row primary canary had zero complete selected tuples. The later LR-BC R1
canary validated 16 primary and 16 confirmation rows, still zero complete primary
tuples and four exact confirmation tuples; the third request returned 504 and
intake stopped. Full paired-stage qualification and scientific fitting were
NOT_RUN. Unrequested pairs are unknown, not unusable.

The retained responses exist inside private source/return packages. Do not
mistake retrieval-script zips, library bundles or the SI for a full frozen
MF-PCBA measurement release. Relevant open issues include live-versus-published
revision equivalence, mean/median aggregation, structure/stereo handling,
unmeasured/censored/default-floor semantics and historical follow-up selection.
Evidence: [A3 qualification](GOAL4R2A3_QUALIFICATION_V1.md),
[latest B decision](../06_execution/B_POTENTIAL_DECISION_LRBC_20261106.md),
[initial metadata manifest](../../research/manifests/goal4r2a_mfpcba_metadata_v1.json).

## 6. Annotation, methods and workflow support assets

- `research/raw_data/external-benchmarks/fs-mol-0.1/` contains family registry
  v1/v2/v3, 220 matching ChEMBL mapping-cache files and multiple UniProt/InterPro
  cache/attempt directories. File presence can include failed-request receipts;
  it is not a full curated proteome or proof every accession is covered.
- Protected-final provenance includes 24 versioned feature files, 7,277 record
  positions, 4,723 unique canonical structures, 14 annotation-connected groups and
  42 proteins under the existing protection union. These are a protection index,
  not additional experimental samples or identical counts to the current FS-Mol
  selected final subset. Keep all existing restrictions.
- The ChEMBL owner-methods folder contains **three main PDFs plus two related
  supplements**, 5,793,019 bytes total. Main IDs/DOIs are CHEMBL1140224 /
  `10.1021/jm801063n`; CHEMBL1140235 / `10.1021/jm800965b`; CHEMBL1156448 /
  `10.1074/jbc.M609796200`. A separate masked web-methods source,
  `10.1021/jm900186m`, was retained earlier. Supplements are not extra independent
  papers or adjudicated references. Three other documents were deferred by the
  owner without purchase. These old sources do not supply methods for every new
  ChEMBL candidate. [R0-A1](R0A1_FEASIBILITY_RESULTS_20261107.md) records the limits.
- MolDesignBench records describe a 2,000-task source-reported generation/
  optimization benchmark, but native task/gold ingestion is NOT_RUN. Its record
  reports CC BY-NC 4.0, unpinned additional model terms, tool/dependency concerns
  and a native SMILES/None output mismatch. Metadata/card/code review is not a
  downloaded usable benchmark. [Manifest](../../research/manifests/goal4r2a2_benchmark_readiness_v1.json).
- LAB-Bench, Papyrus, LIT-PCBA, MUV and full PCBA appear as investigated leads.
  No qualified local measurement/task payload was established by this inventory.
  A literature mention or data-card example does not prove a local data release.
- Twelve exposed authored workflow briefs in six cached-source groups and C
  acceptance fixtures support software tests. The simple/durable comparison tied
  12/12 vs 12/12 with shared decision code. They are not independent molecular
  reference gold, live-agent superiority or customer-benefit data.
- `.local/curaloop.sqlite3` is application state, not a new scientific source.
  Source model JSONs, run outputs, manifests and vendor/return zips are not
  independent experimental datasets. This audit did not open application DB rows.

There are also substantial **old experimental outputs**, not an absence of
earlier experiments: Goal 4 recorded 6,488 campaign executions plus 64 calibration
diagnostics, and 4R1 recorded 3,176 campaigns. These are repeated runs on the small
exposed assay populations, not thousands of independent datasets. The prior
screening implementation was 32.2% slower in its matched timing check; stronger
Greedy prediction explained much of 4R1's improvement and incremental planner
value was not established. No learned RL controller was evaluated in those
challenges. Deep Research should use this counterevidence when checking novelty.
See [Goal 4](GOAL4_RESULTS_V1.md) and [4R1](GOAL4R1_RESULTS_V1.md).

## Historical records that can look contradictory

The early acquisition document says FS-Mol was only received and not extracted;
the later dataset card records the prepared 24-assay feature cohort. Both are
historical checkpoints; the latter is the relevant preparation state.
The initial MF-PCBA manifest says SI acquisition was blocked; the actual SI PDF
is now present and the later A2/A3 audit used its metadata. Do not overwrite
those frozen early receipts or treat their initial status as current absence.

Counts such as 139 components, 18 selected units, 12 reserved groups, 24 feature files,
4,723 protected structures, 36 proposed bundles and 1 new nominal pair have different
definitions. None should be substituted for another or for independently
certified family count.

## What Deep Research should resolve

1. Which existing source can support a scientifically meaningful, source-grounded
   decision task with adequate measured overlap and trustworthy reference context?
2. Are our proposed 128/64/32 floors, 36/18 scale and 12 final-family ambition justified,
   or are they obstructing a better design? Any change requires a prospective
   owner decision, not selection based on favorable results.
3. Is adaptive evidence acquisition substantively distinct from strong existing
   methods when complete metadata/caching and a fixed predictor are available?
4. Can a defensible alternative reference design reduce manual adjudication,
   without calling AI consensus or database flags independent truth?
5. What is the smallest credible empirical plan for a strong paper and a useful
   R&D plugin, with separate scientific, product and commercial evidence?

Use the [copy-ready Deep Research brief](../02_literature/DEEP_RESEARCH_PROMPT_20261107.md).
Local paths above are owner-machine locators, not public download URLs. Attach
this inventory to the new research chat; ignored/private payloads are not on
GitHub and must not be assumed accessible. No raw datasets or reserved outcomes
need to be uploaded for the first literature/data-feasibility research pass.
