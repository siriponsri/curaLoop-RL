# CuraLoop engineering memory

Scope: CuraLoop-RL only. Owner explicitly requested recording engineering errors
as project memory on 14 November 2026. Reverify current state before reuse.
These records describe evidence and approved boundaries; they do not reopen
closed research accounts or authorize new experiments.

## EM-20261114-01: preparation must finish before runtime starts

Type: confirmed source-order defect plus a causal hypothesis.
Sources: tools/saralr1_acceptance_program_v1.py;
docs/evidence/lr-sara-lr1-20261114-v1/engineering-acceptance-v1.json;
docs/evidence/lr-sara-lr1-20261114-v1/post-failure-static-observation-v1.json.

The acceptance Python process started with absolute LD_LIBRARY_PATH directories
that did not yet exist, created/extracted the library tree in that process, then
called ctypes.CDLL. libXrender loading failed on libX11.so.6 even though later
inspection found that file, its target and the declared environment. Static ELF
inspection found the expected x86-64 dependency chain without RPATH/RUNPATH.

The glibc loader can cache nonexistent absolute search directories. This is the
leading source-supported explanation, not runtime-confirmed causality for that
specific image: exact glibc build/LD_DEBUG/A-B controls were not captured.
Do not convert this hypothesis into a confirmed cause in future reports.

Prevention: complete and hash a prepared environment first; start a separate
fresh worker with its search path set before exec; mount completed dependencies
read-only. Prove the loader explanation using controlled startup conditions,
not repeated downloads or same-process environment edits.

## EM-20261114-02: package metadata and Python API compatibility

Type: confirmed implementation defects.
Sources: tools/sara_correction_worker_v1.py;
docs/evidence/lr-sara-20261114-v1/terminal-technical-stop-v1.json.

dpkg-deb -x attempted to restore owner/time/mode on an ordinary-user-owned bind
root under dropped capabilities and failed. SETUP also called hashlib.file_digest
under Python 3.10; that API starts with Python 3.11. The latter setup line was not
reached in that run. Do not claim its traceback was observed there.

Prevention: validated content-only extraction to owned staging, no bind-root
metadata restoration; streaming SHA-256 on the retained interpreter; run actual
interpreter/ownership integration tests before research admission.

## EM-20261114-03: orchestration is part of the deliverable

Type: confirmed implementation defects.
Source: docs/evidence/lr-sara-lr1-20261114-v1/engineering-administration-incidents-v1.json.

The bootstrap omitted the leases parent before Docker creation. A first-start
continuation then omitted shutil from its result-reporting namespace. Inspecting
the same completed job recovered its result; tests were not rerun. The acceptance
program only emitted its result at the end, leaving partial step results absent.

Prevention: preflight all required directories/imports; use importable workers
rather than string-cut program tails; exercise launcher success/failure/timeout
and collection paths; persist per-step events and a final receipt even on error.

## EM-20261114-04: engineering debugging and scientific retries differ

Type: process correction and owner preference.

Prior finite research releases stopped at the first failed harness gate, before
an environment artifact was established. This sequencing repeatedly terminated
research budgets without evaluating agents. Do not present those stops as null
agent effects or intrinsic benchmark failure.

The owner now approved the proposed engineering budget (16 CPU-hours, two
allocated GPU-hours, 72 elapsed hours) and prompt correction of errors within
that scope. Keep corrections in one engineering work order, recording failed
candidates and resources. Proposed limit: three engineering correction cycles,
with final clean reconstruction/runtime acceptance before scientific canaries.
Native algorithms/scoring and locked roles remain protected. No new paid API,
model/data, permission or scope expansion is implied. A long-goal proposal was
requested; budget approval alone is not a completed environment or study result.

## EM-20261114-05: safe Windows cleanup preflight

Type: confirmed local administrative issues, corrected before deletion.
Source: maintenance cleanup script and receipt under
docs/evidence/dataset-cleanup-20261114-v1.

FileInfo/DirectoryInfo ancestors obtained through .Parent are not guaranteed to
retain PowerShell provider PSIsContainer properties; test the .NET DirectoryInfo
type when walking ancestors. The legacy powershell.exe session did not expose
Get-FileHash; use the known bundled PowerShell 7 runtime and preflight required
commands. Both failures occurred before any removal. No old ledger was edited.

Delete only checked absolute literal paths, reject reparse points and validate
canonical hashes before removal. Keep a restore map and recheck canonical files,
fresh absence and preservation pins afterward. Never use broad deletion of .local.

## EM-20261114-06: authorized dataset duplicate cleanup

Type: completed owner-authorized storage maintenance.
Receipt: docs/evidence/dataset-cleanup-20261114-v1/cleanup-receipt.json.

Removed only 216 duplicate/rebuildable files, 2,774,958,031 apparent bytes:

- .local/lr-sc1-20261113-v1/remote-return-v1/files/assets/test_data.h5
  (1,049,345,865 bytes), retaining the canonical evaluator-private SciCode file.
- .local/lr-sara-20261114-v1/native-assets-v1/tree (215 files,
  1,725,612,166 bytes), retaining native-assets.tar.gz and its member manifest.

Both canonical hashes and all 230 prior preservation pins passed before/after.
Restore these exact historical paths from the recorded canonical sources before
running old scripts that require them. Earlier return verification receipts
describe their historical delivery; intentional later duplicate deletion does
not rewrite them. Do not claim the removed expanded paths still exist.

ChEMBL, FS-Mol, CF1 private data, unique raw archives, final16, source/result
snapshots, manifests and closed ledgers were retained. Future cold archival of
unique holdings requires a verified destination and restore map.

## EM-20261114-07: loader startup mechanism now has matched runtime controls

Type: controlled engineering evidence, ENV-STABLE-LR (not agent efficacy).
Source: docs/evidence/env-stable-lr-20261114-v1/loader-controls-v1.json and
the captured LD_DEBUG logs in the owned return.

Same retained image, seven identical Debian payloads, Python 3.10.22/glibc 2.41,
AT_SECURE=0 and the same in-container LD_LIBRARY_PATH:
A (directory absent at startup; late prepare/load in same process) reproduced
the libX11.so.6 failure; B (prepare first, fresh consumer) passed; C (directory
present at startup before late extraction) passed. Both libgomp and libXrender
loaded under B/C. This supports directory-startup state as the causal trigger in
the retained setup and the glibc missing-directory-cache explanation. This
supersedes the hypothesis-only status in EM-20261114-01 for this tested setup;
the original record and frozen failed reports remain unchanged.

Papyrus's owned writable HOME/PYSTOW cache subsequently passed fresh imports.
ProLIF then exposed another dependency, libXext.so.6, in RDKit Draw. Loader
control success is not full RDKit/ProLIF readiness. Audit the complete selected
ELF closure and substantive imports/workloads, rather than fixing only the first
missing SONAME or claiming package-root imports prove runtime readiness.
Further profile repairs stay within the single approved engineering work order.

## EM-20261114-08: substantive checks and exact engineering closeout

Type: observed ENV-STABLE-LR engineering evidence, not agent efficacy.

Root imports missed DeepPurpose's descriptastorus dependency. Real module/Morgan
workloads found it. The pinned 2.8.0 wheel was added in a separate addon; existing
profiles were preserved. Test fixtures also needed Papyrus `Quality` and ProLIF
Mapping/UserDict semantics. Correct fixture contracts rather than misclassify
these as package failures. All13 workloads and26 cold checks passed after offline
byte reconstruction. Keep installed-artifact reproduction distinct from fresh
resolver recreation. Frozen native outcome: RUNTIME_ARTIFACT_PASS_NATIVE_ACCEPTANCE_FAILED; see the final owner report
for all four scores/errors, without rerun or source/scoring edits.

A missing generated file failed locally before remote dispatch. Preflight every
source before booking/dispatched state, and inspect dispatch receipts before
recovering. Never reset failed bookings. Shell quoting is not JSON escaping;
prefer script files for edits. Root-owned pip cache refused a user-owned parent;
do not claim cache completeness from a configured cache path.

Full returned artifact was independently verified before exact owned cleanup;
canonical datasets and all protected scientific bytes remain. No actor, locked
native run or manuscript was performed. Future research needs owner review.

## EM-20261114-09: freeze resource estimates after capacity preflight

The native per-attempt CPU cap was an engineering allocation, not the benchmark requirement. Full-training throughput was not calibrated before freezing that cap. Preserve actual cap stops as capacity-limited/inconclusive; do not classify them as dependency failure or native score zero. Do not silently increase caps after observing outcomes or replay a scientific attempt. Future releases must justify allocation before freeze, while reusing the verified installed artifact and successful existing native evidence.

## EM-20261114-10: Git whitespace checks must preserve frozen receipts

Frozen Windows JSON receipts used CRLF and were correctly kept with -text.
Git's whitespace check initially flagged those line endings. Add a narrowly
scoped cr-at-eol attribute rather than normalize pinned receipt bytes. Write the
new attributes file with explicit LF bytes; a default Windows text writer can
otherwise introduce the same issue into that policy file. Failed delivery
preflights were administrative, before commit/push; no scientific job reran.
