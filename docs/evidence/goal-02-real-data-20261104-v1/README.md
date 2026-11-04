# Goal 2 evidence packet

Read [the result report](../../03_research/GOAL_02_RESULTS_V1.md) and
[protocol](../../03_research/GOAL_02_REAL_DATA_PROTOCOL_V1.md) first.
Implementation/correctness passed; the candidate computational advantage failed.

| Evidence | Scope |
| --- | --- |
| [Frozen configuration](../../../research/configs/goal_02_real_data_v1.json) | Source and real development-cohort SHA256 identities,180-run allocation |
| [Input transfer](input-transfer.json) / [preflight](remote-preflight.txt) | Minimal owner-authorized SSH package, live host resources |
| [Canary](canary/analysis.json) / [review](independent-review.json) |10 included runs, explicit continuation gate |
| [Final analysis](final/analysis.json) / [metrics](final/metrics.csv) |180 completed runs and all methods/conditions |
| [Paired effects](final/paired-effects.csv) | Task/seed differences, including negative results |
| [Run ledger](final/run-ledger.json) |180 run hashes and180 corresponding attempt hashes |
| [Final independent review](final-independent-review.json) |360 raw hashes, event/CSV fields, bound/effect/timing and source/journal claim audit |
| [Mechanism audit](mechanism-audit.json) |458 bound checks, pruning, WAIT/partial use and compute ratios |
| [Receipts](remaining-receipt.json) / [result transfer](result-transfer.json) | Exact frozen runtime/environment, measured resources and archive SHA256 |
| [Local smoke disclosure](local-smoke-disclosure.json) | Unfrozen local integration check with missing raw trace; separate from formal180 |
| [Preservation](preservation.json) |191 protected application files |
| [Historical development hashes](historical-development-preservation.json) |162 earlier run files unchanged; post-hoc diagnostics only |
| [Package validation](package-validation.json) |511 protected source files,27 archive originals and local links at that checkpoint |
| [Research tests](research-tests.xml) / [baseline tests](development-baseline-tests.xml) |88+19=107 passing targeted tests |
| [FS-Mol receipt](fs-mol-acquisition.json) |Owner download not yet present; no archive-member/label inspection |

Full runs remain ignored at `.local/goal2-real-data-20261104-v1/final/output`
in the checkout and `/home/chaw/curaloop-rl/goal2-20261104-v1/output` on dr-train.
No failed formal runs were discarded; the durable attempt markers block silent
replay after a killed run. Public metrics exclude initial/pending labels.

The small [source archive](execution-source.zip) contains frozen implementation
and config bytes without assay records. The repository's MIT notice applies to
this source. Source line endings must match its hashes; prepared cohort bytes
must match the configuration. Reproduction needs the original permitted NCATS
files/preparation or the owner's retained pinned cohorts. No independent
reproduction is claimed.

New experiment identities and output folders are mandatory for future runs.
Do not rerun the immutable goal driver into these existing outputs or overwrite
older evidence. The package checker's static `not_run` list describes its own
scope; this goal's execution/push statuses are recorded in separate receipts.
