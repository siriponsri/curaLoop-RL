# UI process-tree CPU envelope: owner amendment

The owner explicitly approved an aggregate CPU quota equivalent to one core per
UI build/test/render job, with a singleton starting affinity, after the first
canary found no delegated cpuset controller. This supersedes the UI amendment's
requirement for a hard singleton cpuset only. It does not change scientific
guards, the four-worker combined ceiling, C's clock or budget.

Required before payload release: kernel `cpu.max=100000 100000`, aggregate
`memory.max=4294967296`, `memory.swap.max=0`, starting affinity on the leased CPU,
nice19, bounded tasks and an absolute-deadline-clamped runtime no greater than
840seconds, followed by a five-second control-group shutdown grace. Child
processes may change affinity; the hard aggregate quota remains one CPU. Do not
claim a hard cpuset lock or simultaneous physical-core isolation.

Keep all previous reservations. The failed first canary retains900CPU-seconds;
it released no payload and left no descendants. After the additive utility
amendment and that canary, cumulative conservative charge is10.25CPU-hours.
Actual first-canary aggregate usage was0.019877seconds, not the retained charge.
The next900-second attempt brings the conservative charge to10.5CPU-hours.

No sudo, delegation, SSH, system-manager or machine configuration changes are
authorized or needed. Verify the user service, its identity and kernel limits.
Missing quota/memory/terminal evidence remains a blocker; do not weaken them.
All UI task-owned code/data/dependencies/logs must return and be reread before
exact task/export cleanup. Earlier closed B/C roots remain closed.
