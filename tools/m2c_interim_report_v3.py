"""Owner status from fresh process/heartbeat and completion metadata, without effects."""
import ctypes,json
from ctypes import wintypes as w
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-costed-20261108-v2'


def process_alive(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
    kernel.GetExitCodeProcess.argtypes=[w.HANDLE,ctypes.POINTER(w.DWORD)];kernel.CloseHandle.argtypes=[w.HANDLE]
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle:return False
    try:
        code=w.DWORD();return bool(kernel.GetExitCodeProcess(handle,ctypes.byref(code))) and code.value==259
    finally:kernel.CloseHandle(handle)


def main():
    now=datetime.now(timezone.utc);local=now.astimezone(timezone(timedelta(hours=7)))
    ledger=json.loads((TASK/'ledger.json').read_text());pipeline=json.loads((TASK/'pipeline-status.json').read_text())
    resource=json.loads((TASK/'durable-pipeline-resource-v3.json').read_text());alive=process_alive(resource['pid'])
    heartbeat_age=(now-datetime.fromisoformat(resource['heartbeat_utc'])).total_seconds()
    assert alive and heartbeat_age<90,'DO_NOT_REPORT_STALE_RUNNING'
    matrix=json.loads((TASK/'execution-matrix-v1.json').read_text());counts={}
    for handler in('main','ablation','transfer'):
        count=0
        for e in matrix['entries']:
            path=TASK/'jobs'/e['job']/'resource.json'
            if e['handler']==handler and path.exists() and json.loads(path.read_text())['status']=='PASS':count+=1
        counts[handler]=count
    charged=ledger['prior_retained_seconds']+sum(ledger['bucket_reserved_seconds'].values())
    snapshot={'status':'VERIFIED_INTERIM_NOT_M2_COMPLETE','as_of_utc':now.isoformat(),'as_of_thailand':local.isoformat(),
      'controller_process_alive':alive,'controller_pid':resource['pid'],'heartbeat_age_seconds':heartbeat_age,
      'phase':pipeline['step'],'technical_contexts_complete':96,'prefixes_complete':48,'branches_complete':1152,
      'gates_frozen':12,'tuning_complete':576,'control_artifacts_frozen':8,'main_complete':counts['main'],
      'ablation_complete':counts['ablation'],'main_and_ablation_complete':counts['main']+counts['ablation'],
      'main_and_ablation_target':2100,'transfer_complete':counts['transfer'],'transfer_target':288,
      'cumulative_charged_seconds':charged,'cumulative_cap_seconds':172800,'accounting_basis':'full retained reservations, not total measured host CPU',
      'retained_not_dispatched_failed_unit_attempts':6,'scientific_effect_verdict':'NOT_AVAILABLE_INCOMPLETE_PAIRED_MATRIX',
      'final_outcomes_opened':False,'m3_released':False,'deadline_utc':ledger['deadline_utc']}
    target=ROOT/'docs/evidence/m2-costed-20261108-v2/interim-status-20261109.json'
    target.write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
    main_done=counts['main']+counts['ablation'];remaining=2100-main_done
    text=f'''# M2 interim owner report

Verified {local.strftime('%d %B %Y, %H:%M:%S')} Thailand time. **M2 IN PROGRESS; no efficacy verdict.**

The scoped six-assay development study has not completed. No effect estimate or
publication-readiness claim is supported by this interim checkpoint.

| Stage | Completed / planned | Evidence status |
| --- | ---: | --- |
| Synthetic resource contexts | 96 / 96 | PASS |
| Training prefixes | 48 / 48 | PASS |
| Forced continuations | 1,152 / 1,152 | PASS |
| Gate artifacts | 12 | Frozen; 384/384 eligible state/C combinations |
| Baseline tuning | 576 / 576 | PASS; controls frozen in 8 predictor/fold artifacts |
| Main comparison | {counts['main']} / 1,920 | In progress |
| Interleaved RF ablations | {counts['ablation']} / 180 | In progress |
| RF B=16 transfer | {counts['transfer']} / 288 | Pending |
| Full return, analysis, final render review and exact cleanup | Not complete | Pending |

Main plus ablations: **{main_done}/2,100 ({100*main_done/2100:.1f}%)**. Counts are work
units, including correlated branches, not independent biological repetitions.
There are six exposed FS-Mol assays, 1,285 task rows and four annotation components.

## Problems identified and retained

Three calibration units were never sent when the first local coordinator reached
its CPU limit. Three tuning units were never sent when an SSH TCP connection timed
out. Fresh exact job/unit absence preceded identical-context retries. All six
failed attempts and their original reservations remain retained; no favorable
replacement seed or changed method was introduced.

At this owner status request, the previous local controller was absent even though
its initial resource file still said RUNNING. Its last three remote workers had
completed successfully and were inactive. Their real receipts were recovered and
settled, bringing the retained main/ablation total to 210 before resuming. The
precise cause of the local controller's exit is not established. It is not a
molecular-method failure. The unclosed controller's full reservation remains
charged; its unavailable final CPU measurement is not fabricated.

A replacement hidden controller was launched with private durable logs, an exact
PID, a 30-second heartbeat and independent process readback. This report verified
that PID alive and its heartbeat fresh ({heartbeat_age:.1f} seconds old), and
observed further completed units. Remaining work resumes from the original frozen
specification hashes; the completed 210 units are not repeated. No predictor,
planner, endpoint, seed, gate or selected control was changed.

## Resource position

Conservative cumulative charge: **{charged/3600:.3f}/48 CPU-hours**. This includes
retained reservations for interrupted coordinators and newly booked bounded
orchestration; it is not measured total-host consumption. All charges remain
within the existing stage ceilings. The original deadline remains **12 November
2026, 15:17:29 Thailand time**. At most three remote scientific workers and one
local CPU-equivalent/512MiB coordinator remain allowed.

## Research interpretation and remaining work

Technical checks and fitted artifacts have passed their registered gates. The
main paired matrix is incomplete, so there is no defensible complete L-G1/L-T/L-E
effect estimate yet. This checkpoint does not establish incremental discovery,
clinical benefit, laboratory savings, novelty or journal readiness. Final
features/labels/presence and old validation remain closed; M3 is not released.

Remaining scientific work is {remaining} main/ablation units and {288-counts['transfer']}
transfer units. It is followed by complete private return/hash reread, full trace
and budget audit, component-balanced effects and conditional seed intervals,
aggregate figures with final-size/grayscale inspection, exact owned remote
cleanup, English main delivery and the owner decision before M3.

See the [execution record](M2_COSTED_EXECUTION_NOTES_20261108.md) and
[machine-readable interim snapshot](../evidence/m2-costed-20261108-v2/interim-status-20261109.json).
'''
    (ROOT/'docs/06_execution/M2_INTERIM_OWNER_REPORT_20261109.md').write_text(text,encoding='utf-8')
    print(json.dumps(snapshot))


if __name__=='__main__':main()
