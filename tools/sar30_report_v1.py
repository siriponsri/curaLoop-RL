"""Derive the owner report from retained attempts, without new scientific runs."""
import csv,io,json,sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.sar30_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,authority,digest,write_new

def main():
    r,l=authority();assert l['status']=='ACTIVE_CLOSEOUT_FAILED_ENVIRONMENT'
    env=json.loads((PUBLIC/'remote-environment-result.json').read_text())
    rows=json.loads((PUBLIC/'static-input-and-dependency-audit-v1.json').read_text())['rows']
    stop=json.loads((PUBLIC/'qualification-stop-v1.json').read_text())
    returned=json.loads((PUBLIC/'owned-return-verification-v1.json').read_text())
    cleaned=json.loads((PUBLIC/'remote-cleanup-v1.json').read_text())
    rights=json.loads((PUBLIC/'rights-and-shared-input-audit-v1.json').read_text())
    freeze=json.loads((PUBLIC/'role-and-check-freeze-v1.json').read_text())
    assert cleaned['root_absent'] and cleaned['exports_absent'] and all(cleaned['owned_container_absence'].values())
    status={};details={}
    for group in env:
        if group['install_exit_code']!=0:
            for i in group['ids']:status[i]='FAIL_INSTALL';details[i]='ENOSPC in frozen preparation; no reference attempt'
        else:
            for case in group['imports']:
                i=case['instance_id'];results=case.get('results') or []
                ok=case.get('exit_code')==0 and bool(results) and all(x['pass'] for x in results)
                status[i]='PASS_ROOT_IMPORTS_ONLY' if ok else 'FAIL_ROOT_IMPORT'
                details[i]='Root imports only; reference execution and native scorer conformance NOT_RUN' if ok else '; '.join(x['module']+': '+x.get('error_type','unknown') for x in results if not x['pass'])
    final=[]
    for row in rows:
        i=row['instance_id'];lineage=row['repository_lineage']
        cluster='shared-nvc-cogsci-inputs' if lineage in ('nriesterer/syllogistic-nvc','brand-d/cogsci-jnmf') else lineage
        final.append(dict(instance_id=i,role=row['role'],domain=row['domain'],repository_lineage=lineage,dependence_cluster=cluster,
            rights='ADMITTED_DECLARED_LOCAL_RESEARCH',input_members=row['input_members'],
            input_declared_bytes=row['input_declared_bytes'],environment_status=status.get(i,'NOT_RUN_AFTER_GATE_STOP'),
            reason=details.get(i,'Stopped when three locked environment failures made the approved 24-task floor impossible under this recipe'),
            native_reference_execution='NOT_RUN',native_score=None,grader_conformance='NOT_RUN',
            public_check_definition_candidate=row['public_scientific_check_candidate'],public_check_implementation='NOT_RUN',agent_execution='NOT_RUN'))
    write_new(PUBLIC/'per-task-qualification-v1.json',final)
    fields=list(final[0]);s=io.StringIO(newline='');writer=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(final)
    (PUBLIC/'per-task-qualification-v1.csv').write_text(s.getvalue(),encoding='utf-8',newline='\n')
    locked=[x for x in final if x['role']=='locked_candidate']
    optimistic=[x for x in locked if not x['environment_status'].startswith('FAIL')]
    assert len(locked)==26 and len(optimistic)==23 and len(final)==30
    summary=dict(status='NO_GO_FIXED_ENVIRONMENT_QUALIFICATION',all_candidates=30,development_candidates=4,locked_candidates=26,
        root_import_status_counts=dict(Counter(x['environment_status'] for x in final)),
        locked_status_counts=dict(Counter(x['environment_status'] for x in locked)),
        locked_optimistic_upper_bound=len(optimistic),locked_minimum=24,
        optimistic_dependence_clusters=len({x['dependence_cluster'] for x in optimistic}),cluster_minimum=12,
        new_native_reference_attempts=0,new_native_scorer_calls=0,agent_model_calls=0,gpu_allocated_seconds=0,
        native_valid_locked_tasks='NOT_ESTABLISHED_NO_REFERENCE_ATTEMPTS',agent_effect='NOT_ESTIMABLE',
        native_grader_conformance='NOT_RUN',full_comparison='NOT_RUN',manuscript='NOT_WRITTEN',
        source_specific_rights_scope='Benchmark declaration and rasterio license; not independent ownership certification',
        exact_shared_input_links=len(rights['cross_repository_identical_noncode_input_files']),
        complete_independence_certification=False,return_files=returned['files'],return_bytes=returned['bytes'],remote_cleanup='PASS')
    write_new(PUBLIC/'qualification-summary-v1.json',summary)
    cpu=sum(x['cpu_seconds'] for x in l['reservations'])
    measured_local=sum(x.get('measured_cpu_seconds',0) for x in l['reservations'])
    table='\n'.join(f"| {x['instance_id']} | {x['role']} | {x['environment_status']} | {x['reason']} |" for x in final)
    report=f'''# LR-SAR30-Q: qualification results and owner checkpoint

Date: 14 November 2026. Decision: **NO_GO_FIXED_ENVIRONMENT_QUALIFICATION**.
The owner-approved qualification round has stopped. No full agent experiment or
new manuscript was run/written. This is an engineering-feasibility outcome,
not a negative agent-performance result and not proof the benchmark is invalid.

## What actually happened

The retained 30 candidates were all inventoried. The metadata-only hash split
quarantined DeepPurpose (12/13) and EEG2EEG (71/72) before new reference syntax
or outcomes. Existing development IDs 2/3 remain development outside this set.
This left 26 locked candidates, 14 repository labels and four domains.

The archive/annotation identities were rehashed. Input member names and declared
sizes were checked for all 30; this was not a full input extraction/CRC audit.
Reference/evaluator syntax was processed privately for imports and file paths;
their bodies and expected values were not displayed to the author/model. Public
checking candidates were specified before this processing and before any native
outcome. They are definitions, **not implemented or validated checkers**.

A fresh isolated Python 3.10.22 environment worker ran on dr-train with one CPU
equivalent, 8 GiB RAM, no GPU, read-only container root, owned writable mounts,
and a 4 GiB temporary filesystem. Two actual termination probes passed (CPU and
wall deadline). One fixed preparation/import batch then ran. Base packages and
seven locked tasks passed root imports. Three other locked tasks failed this
preflight. Under the frozen rule, at most 23 locked tasks could remain, below
24, so the worker stopped before reference execution. Remaining work was not
continued merely to consume the budget.

| Outcome | All 30 | Locked 26 |
| --- | ---: | ---: |
| Root imports passed, not native-qualified | 7 | 7 |
| Installation failed | 3 | 1 |
| Root import failed | 2 | 2 |
| Not run after gate stop | 18 | 16 |
| Native reference programs attempted | 0 | 0 |
| Native scorer/conformance calls | 0 | 0 |
| Agent calls / GPU allocation | 0 / 0 | 0 / 0 |

## The blockers, including limitations of our harness

| Task(s) | Observed evidence | Supported interpretation |
| --- | --- | --- |
| 12/13, development | DeepPurpose installation ended with `OSError: [Errno 28] No space left on device` | The selected temporary-storage recipe did not support this installation; not a scientific program failure |
| 15, locked | Chemprop installation ended with the same ENOSPC error | The 4 GiB temporary filesystem chosen for this worker was too restrictive for its install attempt; a preparer limitation |
| 22, locked | `papyrus_scripts` root import returned `OSError` | Import failed under this recipe; the exception message/traceback was not captured by the current adapter, so its exact cause remains unresolved |
| 26, locked | `prolif` root import returned `ImportError`, while MDAnalysis imported | Package installation success did not establish import readiness; exact cause is unresolved because the adapter retained only exception type |

The minimal image, storage layout and fixed dependency recipe were implementation
choices. They are not an exact reproduction of every upstream container layer.
The upstream Docker recipe installs system libraries as well as Python packages.
We must not reclassify these failures as evidence that an upstream scientific
reference is wrong or that the 30 tasks are intrinsically unusable.

The error adapter's incomplete exception recording is a further observability
defect. Successful root imports likewise do not exercise submodule imports,
neural training, system-library paths, data loading or native grading. No new
environment repair or scientific rerun was made after the failed gate. A future
technical correction would require its own explicit bounded owner release.

Old reference passes/failures remain historical in the earlier planning CSV.
They were neither erased nor promoted to fresh qualification results. No old
ledger, frozen score, final16, private CF1 row or protected outcome was reopened.

## Dependence, rights and checking coverage

The shared-input audit found two exact SHA256 matches linking
`nriesterer/syllogistic-nvc` and `brand-d/cogsci-jnmf`. Their Matching/MMT input
files connect the two repository labels; future uncertainty analysis must group
them conservatively. Thus the initial 14 locked repository labels provide at
most 13 such connected clusters. Removing the three distinct failed locked
lineages leaves an optimistic upper bound of **10 clusters**, below the planned
12. This is not an exhaustive paper/shared-subject ancestry audit.

The benchmark publisher declares CC-BY-4.0 for most tasks and original terms for
rasterio task 53. The retained rasterio source notice permits use under its BSD-
style conditions. Local research use was admitted on those declarations with
attribution and no unpacked/raw redistribution. This is not independent legal
ownership certification for every upstream data source.

Twenty-eight public check definitions were proposed (24 of the 26 locked
candidates). Tasks 53 and 67 lack a sufficiently fixed public scientific
definition in the inspected prompt for the proposed checker. Even the 28 are
only **candidate applicability**, not conformance-validated scientific check
coverage. Grader repeatability, invalid-artifact rejection, runtime transitive
API freedom and scientific-check conformance are **NOT_RUN** after the gate stop.

## Per-task accounting

Every native/agent result in this table is NOT_RUN. Environment states must not
be read as agent correctness. Machine-readable versions accompany the report.

| ID | Prospective role | Environment state | Reason |
| --- | --- | --- | --- |
{table}

## Resources and preservation

Fresh limits were 16 CPU-hours and two allocated GPU-hours, at most four combined
CPU equivalents/one GPU, with T0 **2026-11-14 03:23:02 UTC** and deadline
**2026-11-16 03:23:02 UTC** (16 November 10:23:02 Bangkok). The remote worker
started at 03:32:57 UTC and finished at 03:43:24 UTC on 14 November. Scientific
work stopped there; return, diagnosis and reporting followed.

At report generation, retained CPU reservations were {cpu:,} seconds
({cpu/3600:.6f} hours), with zero allocated GPU time. The final closed resource
audit, including report/delivery reservations, supersedes this interim subtotal.
The environment container measured 265.233740 CPU seconds; its two termination
probes measured 5.954473 seconds combined. The export process measured 71.482526
seconds; cleanup host control measured 15.970937 seconds. These are measured
components, **not aggregate whole-host consumption**. Retained reservations also
cover unmetered administration and failures; unused allowance is not reusable.
Network receive for the setup container was 7,617,673,202 bytes, below 30 GiB.
No actor checkpoint or scientific dataset was downloaded; package distributions
included neural-runtime dependencies. No GPU was allocated.

All **50,120 persistent owned files / 2,679,279,800 bytes** were returned in a
private 1,176,881,350-byte archive. Every member was rehashed against the remote
manifest on local disk, then the remote tree was independently reread before
exact cleanup. The owned task root, two export files and four named owned
containers are absent. Shared images, model stores, services and other projects
were not removed or changed. Returned dependencies remain local/private.

The release carries 109 prior/source preservation pins. Final closeout verifies
them again. Administrative incidents are retained: the unconfigured hostname
alias initially selected the wrong SSH user; the verified IP profile worked;
one metadata transformer encountered a null PyPI field and was completed using
the retained response without another HTTP fetch; a direct monitor launcher was
corrected to module invocation. No reference or agent experiment was repeated.
The original failed worker snapshot and reservation remain visible.

## Publication and contribution decision

**Not ready for ESE or JSS on the proposed agent-reliability claim.** There are
no new native scientific outcomes or comparative agent runs, so superiority,
equivalence, cost effectiveness and the P-minus-T effect are NOT_ESTIMABLE.
This qualification report alone is not a complete empirical agent paper. It is
not made publishable by relabeling implementation failures as novel findings.

Read [the higher-impact direction](SAR30_HIGHER_IMPACT_DIRECTION_20261114.md).
It recommends separating scientific-action reuse from executable diagnostic
feedback, with strong matched controls and full preparation costs. Existing
papers already cover prepared checks, paper-to-tool conversion and unreliable
tool feedback; novelty remains to be established. CORE-Bench is a source-
readiness candidate, not an automatically admitted replacement or a claim that
270 variants are 270 independent papers. Its capsules/models/evaluator were not
downloaded or run in this goal. A prospective LR-SAV1 envelope is explicitly
unapproved and cannot spend this closed qualification account.

## Owner checkpoint and remaining work

The owner receives the complete failed-gate result **before** any full comparison
or manuscript. Decide whether to authorize one specific infrastructure correction,
consider the action-by-verification study and its separate source-readiness plan,
or retain this report and stop that research branch. No decision is inferred
from elapsed time or an unused resource balance.

Not run: reference execution; native numerical validity; scorer conformance;
scientific-check implementation; agent development/comparison; effect/uncertainty
analysis from agent outcomes; new product-plugin implementation; CORE-Bench
intake; new manuscript. No independent expert validation, customer impact,
wet-lab efficacy or commercial readiness is claimed.

## Evidence entrypoints

- [Qualification summary](../evidence/lr-sar30-qual-20261114-v1/qualification-summary-v1.json)
- [All 30 task rows](../evidence/lr-sar30-qual-20261114-v1/per-task-qualification-v1.csv)
- [Pre-outcome roles and rule](../evidence/lr-sar30-qual-20261114-v1/role-and-check-freeze-v1.json)
- [Environment plan](../evidence/lr-sar30-qual-20261114-v1/environment-plan-v1.json)
- [Actual environment/import results](../evidence/lr-sar30-qual-20261114-v1/remote-environment-result.json)
- [Stop receipt](../evidence/lr-sar30-qual-20261114-v1/qualification-stop-v1.json)
- [Rights and shared-input evidence](../evidence/lr-sar30-qual-20261114-v1/rights-and-shared-input-audit-v1.json)
- [Return verification](../evidence/lr-sar30-qual-20261114-v1/owned-return-verification-v1.json)
- [Exact cleanup](../evidence/lr-sar30-qual-20261114-v1/remote-cleanup-v1.json)
- [Final delivery audit](../evidence/lr-sar30-qual-20261114-v1/delivery-audit-v1.json)

Private retained bundle:
`.local/lr-sar30-qual-20261114-v1/remote-return-v1/owned-return.tar.gz`.
Its SHA256 is `4351f5c2675fc5580f163d9a5c19fb4e1dd49ae0f512aedb511ef919c00e8ca3`.
It is deliberately excluded from Git. Source/evidence is delivered on main;
the actual final commit/push receipt is recorded only after Git verification.
'''
    target=ROOT/'docs/08_agent_rd/LR_SAR30_QUALIFICATION_OWNER_REPORT_20261114.md'
    assert not target.exists();target.write_text(report,encoding='utf-8',newline='\n')
    readme='''# SAR30 qualification evidence

Status: NO_GO_FIXED_ENVIRONMENT_QUALIFICATION. Start with
[the owner report](../../08_agent_rd/LR_SAR30_QUALIFICATION_OWNER_REPORT_20261114.md)
and `qualification-summary-v1.json`. Seven root-import passes are not seven
native passes. All new reference/scorer/agent executions are NOT_RUN.

All 30 rows remain in the accounting. Role/check and environment plans precede
native outcomes. This is a failure of the selected preparation recipe, with
an undersized temporary filesystem and insufficient import-error diagnostics;
it is not proof that the benchmark or the agent is scientifically invalid.

Small control receipts are public; the exact dependency/code return and raw
logs are retained privately under `.local`. No unpacked benchmark input,
gold program, target value, credential or model checkpoint is published here.
Final delivery audit records budget/preservation/return/cleanup and source
identities. It is an implementer-produced audit, not independent expert review.
'''
    (PUBLIC/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    print(json.dumps(summary))

if __name__=='__main__':main()
