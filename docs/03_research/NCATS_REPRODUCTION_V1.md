# Frozen NCATS pilot: fresh-environment reproduction

Date: 4 November 2026. **PASS: 108/108 exact scientific artifact comparisons**.
Same implementer and Windows host; fresh virtual environment and separate local
Git clone. This is environment reproducibility evidence, not independent
scientific review, another biological replication, or a final evaluation.

The clone checked out `d57838d41b30d956c7fd72ac502c1765653fd087` detached. It
regenerated all three 600-compound cohorts from locally transported raw source
bytes with the original source hashes, using the original preparation code and
frozen config. All three regenerated cohort SHA256 values matched exactly.
No original prepared file, experiment ledger or output was overwritten.

The new venv has `include-system-site-packages=false`. Seven exact-version wheels
were obtained using pip's local HTTP cache and installed **offline**, with no
dependencies inherited from the project's venv: NumPy 2.3.5, SciPy 1.17.0,
scikit-learn 1.8.0, RDKit 2026.9.1, threadpoolctl 3.6.0, joblib 1.5.3 and Pillow
13.0.0. `pip check` passed. Recorded distribution paths all lie within the new
venv. The base Python 3.12.10 interpreter and host OS are shared; this is not a
new machine/container or independent upstream wheel audit. No other project's
cached application wheel was used.

The included 18-run canary consumed 36.0240 cumulative run-wall seconds, projecting
216.1442 seconds for the complete grid, within the unchanged 300-second cap.
All 108 fresh runs then completed without failure and matched original warnings
(zero), statuses, initial IDs/counts, schedule hashes, metrics, public snapshots,
decision grids, chosen scores/probabilities and non-timing selector counters.
CPU/wall timing and environment/commit metadata were compared separately. Their
different raw file hashes are expected and recorded rather than discarded.

Fresh cumulative run-wall time was **213.9307 seconds**, CPU **195.0156 seconds**,
peak runner process working set **180,887,552 bytes** (172.51 MiB). Setup/driver
time is separate: creating the venv took 15.847 seconds, offline installation
90.321 seconds, and the cohort-preparation command 21.925 seconds. These times
are not laboratory turnaround or prospective savings. No GPU or paid API was used.

The [evidence packet](../evidence/ncats-reproduction-20261104-v1/) contains every
fresh raw public run/ledger, all command arguments/exit codes and stdout/stderr
logs, exact wheel identities, environment/distribution paths and all 108
pairwise scientific/raw-file comparisons in
[attempt.json](../evidence/ncats-reproduction-20261104-v1/attempt.json).
The [driver](../../tools/reproduce_ncats_v1.py) refuses to overwrite existing
attempts. Setup, run or comparison failures are retained; this attempt had none.
The scientific code is pinned by the detached clone/frozen execution identity.
The orchestration driver's own start-time source hash was not captured; it was
subsequently formatted and its generated attribute-file newline corrected.
Those authoring changes did not change the cloned scientific execution code.
The ignored `.local/repro-ncats-20261104-v1/` retains wheels, the fresh venv,
isolated checkout and raw/prepared data outside Git.

The original null/unfavorable [pilot finding](NCATS_DEVELOPMENT_RESULTS_V1.md)
is unchanged. These 108 reruns are reproductions of existing development
campaigns, not 108 additional seeds or evidence for a population-level benefit.
