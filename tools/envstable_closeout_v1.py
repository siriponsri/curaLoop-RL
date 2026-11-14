"""Evidence-based engineering closeout; no manuscript or scientific inference."""
import ast,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.envstable_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,digest,authority,write_new
if __name__=='__main__':
 r,l=authority('analysis_return');assert json.loads((PUBLIC/'fresh-absence-v1.json').read_text())['status']=='PASS_FRESH_SSH_ABSENCE'
 pins={n:digest(ROOT/n)==h for n,h in r['preservation_pins'].items()};assert all(pins.values());write_new(PUBLIC/'preservation-audit-v1.json',dict(status='PASS',count=len(pins),files=pins))
 before=(ACCOUNT/'project-memory-before.md').read_bytes();memory=ROOT/'docs/00_project/ENGINEERING_MEMORY.md';assert memory.read_bytes().startswith(before)
 cycle=json.loads((PUBLIC/'engineering-cycle3.json').read_text());cold=json.loads((PUBLIC/'offline-reconstruction-cold-starts-v1.json').read_text());native=json.loads((PUBLIC/'native-development-canaries-v1.json').read_text());ret=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text())
 checks=[]
 for p in sorted((ROOT/'tools').glob('envstable_*.py')):
  source=p.read_bytes();tree=ast.parse(source,filename=str(p));compile(source,str(p),'exec');embedded=[]
  for n in tree.body:
   if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in {'INSTALL','LOCK','AUDIT','LIBRARIES','SUPERVISOR','PROGRAM','VERIFY','DELETE','REMOTE','ABSENCE'}:
    val=ast.literal_eval(n.value);compile(val,str(p)+':'+n.targets[0].id,'exec');embedded.append(n.targets[0].id)
  checks.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p),syntax='PASS',embedded_programs=embedded))
 write_new(PUBLIC/'source-syntax-and-identity-v1.json',dict(status='PASS',files=checks,scope='Syntax and embedded-source integrity, not a runtime-suite claim'))
 status='ENVIRONMENT_READY' if cycle['all_pass'] and cold['all_pass'] and native['all_pass'] else 'RUNTIME_ARTIFACT_PASS_NATIVE_ACCEPTANCE_FAILED'
 rows=[]
 for c in native['cases']:
  rows.append(f"| {c['case_id']} | {c['reference']['state']['ExitCode']} | {c['score']} | {c['status']} | {c['reference']['resources']['aggregate_cpu_seconds']:.3f} |")
 report=f'''# ENV-STABLE-LR final owner report

Decision: **{status}**. This closes the authorized engineering work order.
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
- Offline copied installed artifact: {cold['reconstruction']['files']:,} files,
  {cold['reconstruction']['regular_bytes']:,} regular bytes; every copied regular
  file independently reread: PASS. No network/installer during reconstruction.
- Complete content lock SHA-256: `{cold['reconstruction']['lock_sha256']}`.
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
{chr(10).join(rows)}

Complete native receipts are in `native-development-canaries-v1.json`; unchanged
development program logs and outputs are retained privately in the full return.
Scores measure the native development predicates, not an agent contribution.
A cap or numerical predicate failure must not be relabeled a missing dependency.

## Resources, preservation and delivery

`resource-accounting-v1.json` and `closed-ledger-v1.json` retain every booked
ceiling, including failed/unmetered administration. Measured local process CPU,
remote host-controller CPU and container aggregate CPU are separate components;
whole-host consumption is **NOT_ESTABLISHED**. Booked ceilings are not actual
usage. Allocated GPU is zero. Dependency receive was
{cycle['dependency_receive_bytes']:,} measured container network bytes, under
20 GiB; root-owned pip-cache warning means no blanket wheel-cache claim is made.

All {len(pins)} frozen preservation pins pass. Old ledgers, negative results,
final16, private CF1 rows and old hidden outcomes remain unchanged/closed.
Only the four admitted development references were executed. No locked reference
was opened or run. Dataset maintenance retained canonical sources and removed
only owner-approved duplicate copies; see the separate cleanup report.

Full return: {ret['regular_files']:,} regular files, {ret['symlinks']:,} symlinks,
{ret['directories']:,} directories, {ret['regular_bytes']:,} apparent regular bytes.
All content and metadata were checked locally, then independently reread remotely
before exact owned-root/export/stopped-container removal. Fresh SSH absence
passed. Identical file bytes are stored once in the transfer archive with checked
earlier-member aliases; the verifier does not extract/follow returned links.
Shared images, models, services and other projects were preserved.

Full private delivery: `.local/env-stable-lr-20261114-v1/remote-return-v1/`.
Archive SHA-256: `{ret['bundle_sha256']}`.
Manifest SHA-256: `{ret['manifest_sha256']}`.
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
'''
 path=ROOT/'docs/08_agent_rd/ENV_STABLE_LR_FINAL_OWNER_REPORT_20261114.md';path.write_text(report,encoding='utf-8',newline='\n')
 addition=f'''\n## EM-20261114-08: substantive checks and exact engineering closeout\n\nType: observed ENV-STABLE-LR engineering evidence, not agent efficacy.\n\nRoot imports missed DeepPurpose's descriptastorus dependency. Real module/Morgan\nworkloads found it. The pinned 2.8.0 wheel was added in a separate addon; existing\nprofiles were preserved. Test fixtures also needed Papyrus `Quality` and ProLIF\nMapping/UserDict semantics. Correct fixture contracts rather than misclassify\nthese as package failures. All13 workloads and26 cold checks passed after offline\nbyte reconstruction. Keep installed-artifact reproduction distinct from fresh\nresolver recreation. Frozen native outcome: {status}; see the final owner report\nfor all four scores/errors, without rerun or source/scoring edits.\n\nA missing generated file failed locally before remote dispatch. Preflight every\nsource before booking/dispatched state, and inspect dispatch receipts before\nrecovering. Never reset failed bookings. Shell quoting is not JSON escaping;\nprefer script files for edits. Root-owned pip cache refused a user-owned parent;\ndo not claim cache completeness from a configured cache path.\n\nFull returned artifact was independently verified before exact owned cleanup;\ncanonical datasets and all protected scientific bytes remain. No actor, locked\nnative run or manuscript was performed. Future research needs owner review.\n'''
 with memory.open('a',encoding='utf-8',newline='\n') as f:f.write(addition)
 agents=ROOT/'AGENTS.md';s=agents.read_text(encoding='utf-8');header=f'''# Current closeout: ENV-STABLE-LR\n\nThe authorized engineering work order completed as {status}. Read\ndocs/08_agent_rd/ENV_STABLE_LR_FINAL_OWNER_REPORT_20261114.md and\ndocs/evidence/env-stable-lr-20261114-v1/delivery-audit-v1.json.\nThirteen workloads, offline content reconstruction and26 cold checks passed.\nFour unchanged development canaries ran once each; retain all native outcomes.\nNo locked reference/actor comparison/manuscript ran; ESE/JSS readiness is not\nestablished. Full return/local+remote reread/exact cleanup/fresh absence passed.\nPreserve all old pins, ledgers, final16/private CF1/hidden outcomes. No automatic\nnew science/qualification/migration. Scoped main push authorized at closeout.\nLower release records remain history and do not reopen accounts.\n\n''';agents.write_text(header+s,encoding='utf-8',newline='\n')
 write_new(PUBLIC/'README.md.json',dict(report=path.relative_to(ROOT).as_posix(),readiness=status,claims='Engineering only; no actor/scientific comparison',raw_return='Ignored local account remote-return-v1'))
 print(json.dumps(dict(status='PASS_CLOSEOUT_DOCUMENTS_AND_PRESERVATION',readiness=status,pins=len(pins),report=str(path))))
