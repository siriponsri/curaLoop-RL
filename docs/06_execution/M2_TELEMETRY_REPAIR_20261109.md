# M2 Windows telemetry repair

During the fixed development matrix, a Windows reader briefly prevented atomic
replacement of the parent controller's heartbeat file. The heartbeat thread
exited. The parent process and remote molecular jobs continued; the child's
independent heartbeat and Windows Job accounting remained available. A stale
`RUNNING` receipt is not evidence of fresh accounting.

The writer now retries brief file contention and records prolonged telemetry
contention without terminating its CPU/deadline watchdog. The live readback uses
Windows read/write/delete sharing so it does not prevent atomic replacement.
Already-running Python objects retain their original implementation; the change
does not revive the existing parent's thread. Its process, advancing append-only
log, healthy child guard and absolute wall limit are checked separately.

Two constructed checks using actual Windows reader locks passed:

- A brief lock was released and the writer completed its replacement.
- A prolonged lock returned an explicit unsuccessful telemetry write without
  raising, then a final write succeeded after release.

See the [check receipt](../evidence/m2-costed-20261108-v2/telemetry-io-checks-v4.json).
The accounting fixture is constructed: these checks establish metadata behavior,
not resource-enforcement or molecular performance. No labels or scientific units
were read or run by the checks. The frozen scientific source, cohort, parameters,
caps, seeds, comparisons and decision criteria are unchanged.
