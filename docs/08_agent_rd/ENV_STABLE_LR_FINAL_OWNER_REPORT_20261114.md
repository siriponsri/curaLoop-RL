# ENV-STABLE-LR final owner report

Decision: **RUNTIME_ARTIFACT_PASS_NATIVE_ACCEPTANCE_FAILED**. This closes the authorized engineering work order.
Agent efficacy, matched scientific comparison and ESE/JSS publication readiness remain **NOT_ESTABLISHED**.

## Approved scope and actual work

Fresh budget: 16 CPU-hours, two allocated GPU-hours, 72 elapsed hours from
14 November 2026 21:35:05 to 17 November 2026 21:35:05 Bangkok. Maximum four CPU
equivalents/one GPU; actual workers were sequential, each with one CPU-equivalent
quota and a selected initial core. No GPU was allocated. The owner authorized
continuous correction inside three recorded engineering cycles, followed by four
unchanged development canaries once each. No actor, locked reference, manuscript,
paid API, new scientific input/model/base image or host permission change ran.

## Confirmed root cause and fixes

Matched A/B/C tests used the same retained image, Python 3.10.22, glibc 2.41,
AT_SECURE=0, seven Debian payloads and in-container LD_LIBRARY_PATH. A, where the
library directory was absent at process startup and prepared later in that same
process, reproduced missing libX11; B, separate preparation then fresh Python,
passed; C, directory existing before startup then late extraction, passed.
This supports directory startup state and glibc's missing-directory caching in
the tested environment. It is not a universal statement about every loader.
Real aggregate CPU-stop and wall-stop probes passed.

Cycle 1 completed all selected ordinary package installations/restored complete
verified older profiles. Imports then identified missing Xext and expat.
Cycle 2 audited actual ELF dependencies, added libXext.so.6 and libexpat.so.1
without replacing base ABI packages, and passed imports across all 13 profiles.
Initial substantive workloads passed 10/13. Two failures were our fixture bugs:
Papyrus uses `Quality`, and ProLIF returns a Mapping/UserDict rather than dict.
The third found DeepPurpose's undeclared-in-root-import descriptastorus need.
Cycle 3 retained originals, corrected those fixture assumptions and installed
only descriptastorus 2.8.0 into a new addon, checking the official wheel SHA.
All 13 substantive workloads then passed.

A local PowerShell quoting error prevented generation of a workload file before
dispatch. The controller had reserved resources before checking that source
existed. It was recovered with a new controller after proving remote dispatch
had not happened; the original reservation and failed local receipt were kept.
There was no fourth remote engineering cycle and no scientific replay.

## Reproduction and acceptance evidence

- 13/13 root-import profiles covering fixed-30 task metadata: PASS.
- 13/13 substantive library workloads: PASS. These explicit synthetic engineering
  fixtures are not substitute benchmark/agent results.
- Offline copied installed artifact: 228,737 files,
  22,980,099,567 regular bytes; every copied regular
  file independently reread: PASS. No network/installer during reconstruction.
- Complete content lock SHA-256: `5ace608c826864c25d842e940decbfc687481d4e0977565a4f4ea5bccd64f951`.
- Two fresh worker/cache sets, 13 profiles each: 26/26 PASS.
- The package-version manifest and full content lock are in the private returned
  `leases/offline-reconstruct-v1/` directory. This is reproduction of an installed
  artifact on the pinned base, not a demonstrated fresh online resolver rebuild.

Four development references/scorers retained their exact original bytes and
criteria. All used CPU, no network; reference containers had no evaluator gold
mount. Graders received output read-only separately. `eval()` tuple first element
was validated as the score; tuple truthiness was never used. No failed scientific
attempt was replayed. The frozen per-reference cap was 2,100 aggregate CPU seconds
and 2,400 wall seconds, with 90 CPU/150 wall seconds for each grader.

| Development task | Reference exit | Native score | Outcome | Reference CPU seconds |
|---|---:|---:|---|---:|
| 12 | 124 | None | FAIL_REFERENCE_RUNTIME | 2097.239 |
| 13 | 0 | 1 | PASS_NATIVE_CANARY | 76.506 |
| 71 | 0 | 1 | PASS_NATIVE_CANARY | 168.892 |
| 72 | 0 | 0 | FAIL_NATIVE_PREDICATE_OR_GRADER | 514.259 |

Complete native receipts are in `native-development-canaries-v1.json`; unchanged
development program logs and outputs are retained privately in the full return.
Scores measure the native development predicates, not an agent contribution.
A cap or numerical predicate failure must not be relabeled a missing dependency.

## Resources, preservation and delivery

`resource-accounting-v1.json` and `closed-ledger-v1.json` retain every booked
ceiling, including failed/unmetered administration. Measured local process CPU,
remote host-controller CPU and container aggregate CPU are separate components;
whole-host consumption is **NOT_ESTABLISHED**. Booked ceilings are not actual
usage. Retained booked ceilings total **14.083333 CPU-hours (50,700 seconds)**, under
the 16-hour owner ceiling; these are not measured usage. Allocated GPU is zero.
Dependency receive was
10,920,370,369 measured container network bytes, under
20 GiB; root-owned pip-cache warning means no blanket wheel-cache claim is made.

All 279 frozen preservation pins pass. Old ledgers, negative results,
final16, private CF1 rows and old hidden outcomes remain unchanged/closed.
Only the four admitted development references were executed. No locked reference
was opened or run. Dataset maintenance retained canonical sources and removed
only owner-approved duplicate copies; see the separate cleanup report.

Full return: 459,446 regular files, 56 symlinks,
54,588 directories, 49,081,826,811 apparent regular bytes.
All content and metadata were checked locally, then independently reread remotely
before exact owned-root/export/stopped-container removal. Fresh SSH absence
passed. Identical file bytes are stored once in the transfer archive with checked
earlier-member aliases; the verifier does not extract/follow returned links.
Shared images, models, services and other projects were preserved.

Full private delivery: `.local/env-stable-lr-20261114-v1/remote-return-v1/`.
Archive SHA-256: `d93a22c7b523fc3c97d93f42ba9f5658633238884b8b3a0008557a6f2e55e1cb`.
Manifest SHA-256: `6330e7c92ffd586b694fbd398e265f16c9cc1c5ae7fc3e92aaeb5c6178e24ac5`.
The public evidence folder contains summaries, the protocol, executed-source
identities, loader controls, failed candidates, reconstruction and native receipts,
resource account, preservation checks and exact cleanup. Raw inputs/dependency
trees/full return remain ignored locally, outside public Git.

## Limits and owner decision

The environment has stronger runtime evidence than prior import-only attempts.
Only four native development tasks were attempted; the other 26 fixed candidates
have not been natively qualified. Package work is not evidence of benchmark-wide
scientific feasibility or reliable agent behavior. Engineering fixtures have
neither independent expert validation nor user/wet-lab value validation.

No actor comparison, final study, effect estimate or manuscript was run. ESE/JSS
readiness is not established. Review these results before authorizing any new
scientific phase; do not restart qualification or migrate to CORE automatically.
No new research goal is activated by this report. Commit/push main is authorized;
the exact verified pushed SHA is recorded in the delivery message/private Git receipt.

## Exact native outcome interpretation

- **Task 12, incomplete:** CPU safeguard stopped the reference at 2,097.239 CPU seconds (exit 124). Training had entered epoch 3 of 10. No final output or grader score is available. This is a capacity-limited result, not a native score of zero.
- **Task 13, PASS:** the unchanged reference and grader completed. Native score 1; both data and functional correctness checks passed.
- **Task 71, PASS:** the unchanged reference and grader completed. Spearman correlation 0.606264 exceeded the unchanged 0.60 threshold; native score 1.
- **Task 72, FAIL_NATIVE_PREDICATE:** the reference and grader both completed successfully as programs. Spearman correlation 0.081978 was below the unchanged 0.73 threshold; native score 0. The cause of this numerical discrepancy is unresolved; this single run does not establish whether source, version, hardware or another factor explains it.

The 2,100-second per-reference CPU allocation was our engineering budget choice, not a published benchmark requirement. It was frozen before native attempts but was not supported by full-training capacity calibration. A cap failure therefore identifies an allocation limitation in this run; it does not prove the unchanged source could not finish under the overall owner budget or different permitted hardware. The reference was not replayed or truncated to produce a passing answer.

The returned transfer archive was stream-verified without extraction. Complete restoration from that transfer archive on a second host was NOT_RUN. The demonstrated offline reconstruction was a byte copy of the installed artifact on the retained base, followed by two new worker/cache sets. Preserve this distinction. When restoring a transfer archive, use its manifest, validate relative paths, do not follow returned symlinks, and copy checked earlier-member aliases as separate files when metadata differs. Shared base image remains on dr-train; cross-host image provisioning was not tested.
