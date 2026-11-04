# Reproducibility and release contract

## Required run identity

Record experiment/protocol IDs; Git commit plus dirty-file digest; environment lock hash; dataset and split hashes; predictor/controller identities; RNG seeds; operational generator version; policy configuration; initial labels; event ledger; interruption state; and metric implementation version. Seed, software version and dataset name alone are insufficient.

Store a public artifact whenever its data rights allow. If a source cannot be redistributed, provide a lawful retrieval route, transformation code and checksums. Describe the missing availability explicitly. Customer-private data cannot silently substitute for an open benchmark while the manuscript claims full reproducibility.

## Execution pattern

Use a resumable runner with a deterministic immutable run key. Write a run manifest before execution, append events safely and finalize an explicit completion marker only after metrics reconcile. A partial directory is not a complete result. Resume a compatible checkpoint or mark an interrupted run; do not repeat expensive actions invisibly.

Keep model fitting and policy execution deterministic where feasible and record thread counts and library versions. If hardware or parallelism introduces nondeterminism, quantify it and preserve the environment. Match training and inference budgets across methods or disclose the differences.

## Figure generation

Each figure references a machine-readable data table, a script and a completed run set. Figure labels state task population, seeds, simulated time/cost assumptions and what an uncertainty band represents. No synthetic illustration is presented as an empirical curve. Preserve a zero-hit trajectory rather than changing its seed for a better story.

## Independent reproduction

Have a fresh environment recreate at least one end-to-end task and every table/figure aggregation. A solo author may perform this clean-room execution, clearly labelling who ran it. An external reproduction is stronger evidence only when a real independent person performed it. Record failures and dependency changes rather than editing the original log.

Archive a tagged release and immutable experiment materials with an appropriate archival service after owner approval. A repository URL is not an assigned DOI. Citation metadata in this package therefore contains a repository URL and no fabricated DOI or ORCID. External submission and archival upload are not performed by creating this package.

## Full-text and comparator version trace

Link each reproduced comparator to the exact inspected paper version, source commit, dataset hashes, initialization and metric conventions. R05 here is ChemRxiv v3; BayBE's article identifies manuscript code 0.12.2 and separate code/analysis Zenodo snapshots. A current integration may choose another pinned release, but must record that difference. Preserve unresolved questions in the version-discrepancy register until exact-code/data inspection resolves them.
