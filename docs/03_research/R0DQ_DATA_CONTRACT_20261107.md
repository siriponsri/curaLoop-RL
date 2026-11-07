# R0-DQ data and role contract

This is the implementation contract for the owner-released
[R0-DQ qualification](../06_execution/R0DQ_EXECUTION_CONTRACT_20261107.md).
It preserves the task-first design and does not authorize a study or modify a
historical benchmark. The parent is the producer; the owner is the next phase
approver. Source and derived files are versioned private research artifacts.

## Records and freezes

| Artifact | Unit and stable key | Contents | Consumer boundary |
| --- | --- | --- | --- |
| `frame-frozen.json` | Assay identified by release + integer assay ID and ChEMBL ID | Bounded target, source, role and catalog-count metadata | Frozen before values or source-method interpretations |
| `topology-outcome-free.json` | Release + activity ID | Assay/compound/document IDs, endpoint type, original unit and relation | No numerical values or value-derived flags |
| `candidates-frozen-before-values.json` | Salted bundle ID | One reference assay/type and 1-3 different auxiliary assay IDs/types | At most 120; no replacement outside this frame after validation |
| `numeric-query-allowlist.json` | Activity ID | Only frozen-candidate IDs passing target, assay, structure and role gates | Fixed presence validator; no arbitrary query interface |
| `restricted-support-booleans.json` | Activity ID | Exact positive finite support boolean | Neither magnitude, rank, class nor pChEMBL |
| `cohort-support-frozen.json` | Bundle ID | Post-pruning panel of 128 canonical identity hashes, chosen activity IDs and support counts | Candidate support, pending construct/context/reference review |
| `development-packet.json` | Development assay ID | Projected descriptions, variants, parameters and source IDs | No final-source interpretation; omissions are explicit |

SHA-256 binds each freeze to its predecessor and executed code snapshots.
These hashes establish byte identity, not independent scientific review.
Output files are append/version based. Failed runs and their reservations are
retained; a repair must have a distinct job name and remaining approved budget.

## Units, identity and missingness

Primary reference types are Ki and Kd, kept separate. IC50 is auxiliary only.
Concentration units M, mM, uM, micro-M, nM, pM and fM have fixed molar factors.
Only exact `=` relations with finite positive values qualify. A rejected row
is not an inactive compound; absent, censored and unrecognized-unit rows remain
distinct in the outcome-free topology. No activity threshold or utility is
calculated in this phase.

Canonical identity uses RDKit `2026.09.1`, canonical isomeric SMILES, with no
salt, charge, isotope or tautomer normalization. A canonical hash identifies
that exact representation; it does not establish chemical novelty. Replicate
edges use the lowest admissible activity ID, never the most favorable value.

Historical protected identities are excluded before value queries. Known
previously exposed structures cannot enter a new final role. Between new roles,
exact identities are assigned with fixed priority final, validation, development;
all support floors apply after this pruning. Unknown structure/family mapping
is quarantined. A null variant field does not establish wild type.

## Lineage and context completeness

The predeclared, authenticated family registry maps exact UniProt accessions.
Ambiguous/unmapped accessions are quarantined. Normalized DOI and nonempty,
nonzero assay-group links merge candidate family/source units transitively;
historical development/validation exposure forces a connected unit development.
This is a conservative split mechanism inside the bounded frame, not certified
evolutionary or statistical independence across all ChEMBL records.

Descriptions and article methods pass a conservative projector. Procedural
identifiers and narrowly recognized input conditions can be retained; other
numbers are masked and result statements/tables/figures are omitted. Parameter
values are projected only for explicitly recognized procedural input types.
Unsupported parameter semantics and omissions remain visible as limitations.
Neither a projector omission nor an unknown variant can be advertised as
natural decision uncertainty. Complete metadata and source mapping need review
before any candidate context fact is credited as an incremental contribution.

The host and qualifier are trusted processes. Private source SQLite bytes
contain plaintext outcomes at rest; the process contract is not cryptographic
isolation from the machine owner. No raw source or full masked passage enters
public Git. Database attribution and source-paper rights remain separate;
commercial redistribution clearance is not established by this audit.

## Compatibility and recovery

| Existing consumer/artifact | Compatibility |
| --- | --- |
| Historical FS-Mol/Tox21/MF-PCBA manifests, roles, ledgers and final outcomes | Unchanged; no migration |
| Existing application or C Workspace | No dataset activation or new result claim |
| A future reference-review tool | May consume candidate IDs and provenance after owner approval; cannot call support candidates gold |
| A future model/planner | No numerical outcomes or utility released in R0-DQ |

If a cap truncates an assay, its graph is incomplete and it cannot qualify from
the prefix. If source access stops, retain the failure and do not retry or use a
mirror. If transport/reread fails, preserve remote originals. Rollback consists
of leaving historical consumers unchanged and retaining the failed new snapshot,
not resetting clocks, deleting failures or silently sampling a new population.

Every current remote regular task file, including source archive and database,
must be returned in a private archive. Every entry is stream-hashed locally
without expanding the large DB, before exact scoped cleanup and a fresh absence
check. Resource receipts and full return hashes accompany the phase readout.

The owner reviews the achieved G1-G5 result before any next phase. Independent
family certification, source/reference adjudication and model evaluation remain
separate required work. Constructed fixtures test implementation behavior only.
