# Goal 4 remote execution record

5 November 2026. The local all-arm canary completed84campaigns. Timing-only
allocation froze8seeds/4workers. Local free physical memory then fell below the
2GiB preflight minimum; no main worker launched locally. Owner-authorized
dr-train preflight passed with over114GiB available RAM, over114GiB disk and
72allowed CPUs, low observed load, and no existing new task root.

New explicitly owned root: `/home/chaw/curaloop-rl/plan-a-20261105-v2`.
Use the existing strict noninteractive IP profile, without key/config changes.
Create an isolated copied-binary environment inside that root, with the frozen
versions; do not borrow or alter another project's environment. Four independent
main workers use only CPUs68–71, one BLAS thread each, low priority,1GiB each,
within the original40CPU-hour stage/48CPU-hour total and fixed wall window.
Environment setup uses one CPU, at most4GiB and bounded sequential subprocesses;
its child CPU is charged. Existing jobs and GPU state remain untouched.

Transfer only a hash-identified closed source/development-input bundle initially.
No final outcomes or full FS-Mol archive are needed by the compute workers.
Check the pinned runtime and constructed tests before main execution. Preserve
the local canary and its timing-only allocation provenance. Validation preparation
waits for the frozen selected M and complete development evidence verification.

Return and verify intermediate completed development artifacts to support that
gate. At completion retain a complete manifest and return task code, private data,
results, environment records and failures locally. Verify every owned file before
deleting the exact task/export roots; verify their absence. A partial stage return
does not authorize final cleanup. Stop/retain remote state if verification fails.
