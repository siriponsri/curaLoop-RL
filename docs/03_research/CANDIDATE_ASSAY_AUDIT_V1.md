# Candidate assay audit v1

4 November 2026. **Preparatory metadata/feature work; zero final-ready tasks.**
The owner selected expansion to 12+ families and effect estimation with
uncertainty, without a confirmatory material-effect threshold. No final outcome
file was fetched, no final role assigned, and no final evaluation executed.
All biological grouping and rights review is by the same implementer.

## What was inspected

| Discovery route | Preserved result | Interpretation |
| --- | --- | --- |
| Official NCATS training index, excluding the three exposed endpoints | 9 source AIDs; all feature audits completed | Strong shared-library overlap; within-panel candidates only |
| All 15 LIT-PCBA provider source AIDs | 15 source AIDs; all feature audits completed | Raw PubChem sources, not the prepared LIT-PCBA release |
| Fixed 16-gene expansion, first 128 AIDs/gene and bounded HTS membership checks | Only HSP90AA1 AID 1789 qualified for feature audit | The other 15 are search-limit failures, not absence of suitable assays |
| Pinned official DeepChem PCBA identifier list | All 128 AID descriptions inspected; 23 representatives selected before new feature retrieval | New metadata-guided breadth proposal; not a DeepChem dataset reproduction |

The gene search's early IDs were dominated by literature/non-HTS entries. Its
negative results, 92 requests and limits remain intact. The new panel route
addresses discovery recall through a separate, source-derived HTS census. It
does not revise the old search or select assays using favorable outcomes.
Of the gene-search requests, 69 succeeded and 23 all-CID membership attempts
returned HTTP 404/PUGREST.NotFound. Some AIDs recur across different gene
queries; the log retains those repeated membership lookups rather than calling
them 23 unique failures. Failed HTTP bodies were not cached/hash-verified.
They are retained request errors, not 401/403 access denials or outcome evidence.

The PCBA list is pinned to DeepChem commit
`b1ef4e590d9cdc41a3d6d547ad338c052a75c6e4`. Only the literal `PCBA_TASKS` list
was parsed using Python AST; the remote module was never imported/executed and
its labeled CSV was never downloaded. The software LICENSE is not an assay-data
license. The 23-AID [selection](../../research/configs/hts_feature_selection_v1.json)
was committed at `612309a` before feature retrieval. It contains 20 conservative
planning groups: four chromatin assays deliberately share a group. These are
manual functional groupings, not 20 certified independent biological families.

Four selected assays have rat/parasite/mouse target metadata (1457, 588453,
602233, 652025), so they remain outside a human-only core. The remaining 19
assays span 16 proposed groups before further endpoint/independence review.
CYP2C9 AID 883 mixes inhibition/substrate language; AID 624291 has conflicting
title/target annotation. The actual bounded feature phase completed 17 new
audits and reused 3 earlier audits; its last 3 structure samples (588855,
624291, 652025) were not fetched because the payload cap had been reached.
The all-CID membership response for 588855 was received before the cap check
prevented its SMILES request. All three
failures remain in the denominator, with no retry or cap increase. Thus 20
feature-audited panel assays span 17 planning groups, including 3 nonhuman
groups. Excluding nonhuman groups leaves 14 human-annotated groups; excluding
mixed-endpoint CYP2C9 leaves 13. A 12-final plus 2-validation proposal would need
additional adjudicated groups from the earlier census, such as the ERK pathway,
or further metadata work. No such roles are reserved. Dependence merging can
reduce the count further. Planning groups are not certified independent trials.

## Exposure and exact response identity

Only assay descriptions, unfiltered all-CID membership and compound isomeric
SMILES were requested from PubChem. Gene queries added unfiltered AID lists;
the panel added batch descriptions. URL and response-schema guards reject
outcome operations/sections, active-only membership and unexpected fields.
The offline checker verifies every saved response's URL, byte count, SHA256 and
schema. It does not infer scientific independence or a data license.

Each description retains AID version/revision, depositor identity and target
metadata. Request receipts pin exact live bytes and retrieval times; these are
not an atomic historical release. The original 24-assay audit used 72 requests,
68,561,093 received bytes, 289.68 seconds wall and 68.11 seconds process CPU.
The gene expansion used 92 requests, 14,174,968 bytes, 234.97 seconds wall and
20.45 seconds CPU. The panel used 42 successful requests including its 7
identifier/description requests, receiving 98,619,670 bytes. The pre-query 96 MB
cap is explicitly soft by one response; that final response brought the total
over the cap, preventing the last three planned audits. Feature-phase runtime
was 229.87 seconds wall / 64.83 seconds process CPU. No HTTP response failed.
Cap exclusions and chemical-toolkit warnings are separate retained events.

Published aggregate class totals on the LIT-PCBA landing page were already
visible in literature/source discovery. That exposure is explicitly retained;
the totals were not inputs to selection, variance profiles or threshold choice.
No compound outcome values were requested or evaluated. Seeing metadata and
structures is itself an exposure that future split manifests must retain.

PubChem's category definitions inactive=1/active=2 differ from the NCATS
training CSV's inactive=0/active=1. Definitions do not prove that every source
member has a usable binary label. Inconclusive, unspecified, conflicting and
missing values need explicit future ingestion rules; none are silently mapped.

## Chemical overlap is a gate, not a clearance certificate

For each audited assay, at most 200 unfiltered CIDs were selected by fixed
SHA256 ranking without outcomes. RDKit canonical isomeric SMILES retain salts,
tautomers and stereochemistry. Exact matches and nearest radius-2/1,024-bit
nonchiral Morgan Tanimoto >=0.8 were compared against 7,484 unique previously
retrieved NCATS structures, 1,663 unique structures in the three development
subsets, and 1,200 bundled HIV structures. Activity columns were not used.
Standalone-hydrogen RDKit warnings occurred; this preparation does not claim
zero warnings. They are separate from HTTP failures or hidden outcomes.

For the nine remaining NCATS source AIDs, 166-172 of each 200-structure sample
exactly matched previously retrieved NCATS material, and 175-183 had a nearest
similarity >=0.8. Raw ESR agonist/antagonist, PPARG and TP53 source samples were
similarly exposed: exact matches 162/174/171/182 and near matches
178/185/181/187 respectively. They cannot silently become independent transfer
tests. Other LIT source samples had 0-4 exact and 0-7 near NCATS matches, but
zero in a 200-compound sample does not clear a full candidate pool.

See the [24-assay table](../evidence/design-preparation-20261104-v1/candidate-summary.csv)
and [panel feature table](../evidence/hts-panel-preparation-20261104-v1/selected-feature-summary.csv)
for all denominators and unfavorable overlaps. Three earlier feature audits
(1030, 504327, 602179) are explicitly reused in the panel, not presented as new
independent samples. Before final roles, audit whole feature pools against all
exposed structures and across proposed validation/final groups, define a
structure/similarity exclusion rule in advance and retain its attrition.

## Endpoint and family discrepancies

| Source AID | Inspected primary metadata | Consequence |
| --- | --- | --- |
| 1631, PKM2 | Activators; provider table says inhibitors | Quarantine direction until exact prepared-file mapping is checked |
| 743094, PPARG | Agonists of PPAR-gamma signaling; provider table inhibitor shorthand | Correct interpretation of earlier project shorthand by this erratum; exposed family remains development only |
| 651631, TP53 | Agonists of p53 signaling; provider table inhibitor shorthand | Same erratum; exposed p53 family remains development only |
| 2101, GBA | Inhibitors and activators of N370S mutant glucocerebrosidase | Preserve mutation and dual-direction scope |
| 602179, IDH1 | Mutant IDH1 | Do not describe as general wild-type IDH1 inhibition |
| 493208, mTORC1 | Pathway screen in MEF Tsc2-/-, p53-/- cells | Not direct binding; p53 context needs dependence review |
| 995 / 492947 / 1030 | ERK pathway / beta-arrestin-biased ADRB2 / ALDH1A1 isoform | Keep pathway, signaling bias and isoform specificity |
| 504327 | GCN5L2, target KAT2A | Alias, not an additional biological family |
| 504847 | VDR inhibitors | Earlier agonist/antagonist source conflict remains open |
| 720551 | Title KCHN2 3.1; target KCNH2 | Preserve both strings; resolve naming before import |
| 624291 | Integrin phenotype title; glycoprotein-hormone alpha-chain target | Identity/context conflict, quarantined |
| 588855 / 652025 | TGF-beta title with Smad3 / IL-2 with mouse target | Pathway/species scope must remain explicit |

These are discrepancies requiring exact source/code/label adjudication, not
proof of a publisher typo or authority to invert labels. Earlier frozen
development protocols/results are preserved; this report qualifies their
LIT-PCBA inhibitor shorthand. See the [discrepancy register](../02_literature/VERSION_DISCREPANCIES.md).

## Access and rights

The [NCATS challenge index](https://tripod.nih.gov/tox21/challenge/data.jsp)
identifies training resources and CSV label definitions. A
[provider presentation](https://ntp.niehs.nih.gov/sites/default/files/iccvam/meetings/iccvam-forum-2020/ppt/13-ncats-simeonov-508.pdf)
supports public-domain Tox21 data within its stated scope. It does not license
every NCGC assay or every contributed structure file.
The [PubChem source policy](https://pubchem.ncbi.nlm.nih.gov/docs/data-sources)
requires contributor-specific attention. The NCGC source page presented
reCAPTCHA; it was not bypassed. Official allowed data API responses are recorded
separately; no source-page license was inferred from them.

The [LIT-PCBA provider](https://drugdesign.unistra.fr/LIT-PCBA/) prepared-file
grant was not verified. A local TLS verification failure was retained without
disabling verification. ChEMBL's
[provider FAQ](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/general-questions)
states CC BY-SA 3.0, but the attempted exact release LICENSE request timed out;
no ChEMBL assay data were ingested. DeepChem's software terms do not close any
raw assay-data grant. Public accessibility alone is insufficient.

Raw responses/features remain ignored outside public Git; the committed packet
contains source facts, hashes and derived audits. Before outcome ingestion or
redistribution, record the exact file/release, applicable grant and attribution,
endpoint mapping, population/split rules and allowed use. **Final-ready count is
zero because these gates remain open**, even though metadata/feature discovery
now reaches the owner's broader scope.

## Reproducibility and next dependency

The [preparation protocol](FINAL_DESIGN_PREPARATION_PROTOCOL_V1.md),
[initial packet](../evidence/design-preparation-20261104-v1/),
[gene-search packet](../evidence/design-expansion-20261104-v1/) and
[panel packet](../evidence/hts-panel-preparation-20261104-v1/) retain successful
and negative histories. Use `python -m tools.check_design_preparation_v1` for
offline integrity checks; do not rerun immutable network audits in place.
Tests are software boundary evidence, not independent rights or biology review.
The earlier human HSP90AA1 AID 1789 feature candidate adds a separate proposed
chaperone group (1/200 exact and near NCATS matches), and the ERK pathway is
another candidate from the first census. Neither is independent/eligible merely
because it supplies an additional group. Next close source/endpoint/whole-pool dependence gates before role assignment;
then freeze an estimation protocol and a concrete CPU allocation. No final
outcomes are authorized by this preparatory package.
