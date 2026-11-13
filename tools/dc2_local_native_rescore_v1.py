"""Correct upstream tuple decoding on existing outputs; never reruns references."""

import ast
import base64
import json

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write
from dc2_local_native_recover_v3 import invoke
from dc2_local_native_v1 import reserve, settle

SCORER = r"""
import contextlib,importlib.util,json,traceback
from pathlib import Path
from contract import decode_native_result
case=json.loads(Path('/control/case.json').read_text())
try:
    with open('/control/native-log-private.txt','w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        spec=importlib.util.spec_from_file_location('unmodified_native','benchmark/eval_programs/'+case['eval_script_name'])
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        original=module.eval()
        decoded=decode_native_result(original)
    Path('/control/native-detail-private.json').write_text(json.dumps(decoded))
    result={'status':'PASS_NATIVE_INTERFACE_DECODED','native_success':decoded['success'],'return_type':type(original).__name__}
except Exception as e:
    Path('/control/native-error-private.txt').write_text(traceback.format_exc())
    result={'status':'NATIVE_SCORING_ERROR_NOT_SCIENTIFIC_FAILURE','native_success':None,'error_type':type(e).__name__}
Path('/control/score.json').write_text(json.dumps(result))
"""

OUTER = r"""
import json,subprocess,sys
from pathlib import Path
with open('/control/runner.log','wb') as log:
    try:
        p=subprocess.run([sys.executable,'/control/score.py'],stdout=log,stderr=log,timeout=12)
        result=json.loads(Path('/control/score.json').read_text()) if p.returncode==0 else {'status':'SCORER_PROCESS_ERROR','native_success':None}
    except subprocess.TimeoutExpired:
        result={'status':'SCORER_TIMEOUT','native_success':None}
Path('/control/result.json').write_text(json.dumps(result))
"""

REMOTE = r"""
import base64,hashlib,importlib.util,json,os,time
from pathlib import Path
p=json.load(__import__('sys').stdin)
root=Path.home()/'curaloop-tasks/lr-dc2-local-20261113-v1';nroot=root/'native-v1'
spec=importlib.util.spec_from_file_location('owned_io',root/'worker.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.authority()
identity=int(p['case']['instance_id']);assert identity in (2,3,5,16,18,19,22,26,40,41,85)
prior=json.loads((nroot/'control'/f'{identity}-v2'/'qualification-result.json').read_text())
assert prior['reference_exit_code']==0,'Only already-executed valid references can be rescored'
name='curaloop-dc2-local-rescore-20261113-v1'
assert not any('/'+name in r['Names'] for r in m.api('GET','/containers/json?all=1'))
control=nroot/'control'/f'{identity}-scorer-concordance-v1';control.mkdir(exist_ok=False);control.chmod(0o777)
decoder=base64.b64decode(p['decoder_b64'],validate=True);assert hashlib.sha256(decoder).hexdigest()==p['decoder_sha256']
(control/'contract.py').write_bytes(decoder)
(control/'score.py').write_text(p['scorer_source']);(control/'outer.py').write_text(p['outer_source'])
(control/'case.json').write_text(json.dumps(p['case']))
work=nroot/'cases'/f'{identity}-v2';overlay=nroot/'evaluator-mountpoints-v2'/str(identity)
config={'Image':'sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d','Cmd':['python','/control/outer.py'],'WorkingDir':'/work',
 'Labels':{'curaloop.task':'lr-dc2-local-20261113-v1','curaloop.purpose':'native-scorer-concordance'},
 'Env':['PYTHONPATH=/env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1','PYTHONDONTWRITEBYTECODE=1','NVIDIA_VISIBLE_DEVICES=void'],
 'HostConfig':{'NetworkMode':'none','NanoCpus':1000000000,'CpusetCpus':str(sorted(os.sched_getaffinity(0))[-1]),'Memory':2*1024**3,'MemorySwap':2*1024**3,'PidsLimit':64,'ReadonlyRootfs':True,'CapDrop':['ALL'],'SecurityOpt':['no-new-privileges:true'],'Tmpfs':{'/tmp':'rw,size=128m'},
 'Mounts':[{'Type':'bind','Source':str(control),'Target':'/control','ReadOnly':False},
 {'Type':'bind','Source':str(nroot/'env'),'Target':'/env','ReadOnly':True},
 {'Type':'bind','Source':str(work),'Target':'/work','ReadOnly':True},
 {'Type':'bind','Source':str(nroot/'assets/inputs'/str(identity)/'benchmark/datasets'),'Target':'/work/benchmark/datasets','ReadOnly':True},
 {'Type':'bind','Source':str(overlay),'Target':'/work/benchmark/eval_programs','ReadOnly':True},
 {'Type':'bind','Source':str(nroot/'assets/gold-results'),'Target':'/work/benchmark/eval_programs/gold_results','ReadOnly':True}]}}
created=m.api('POST','/containers/create?name='+name,config)
inspected=m.api('GET','/containers/'+name+'/json');h=inspected['HostConfig']
assert h['NetworkMode']=='none' and h['NanoCpus']==1000000000 and h['Memory']==h['MemorySwap']==2*1024**3 and not h.get('DeviceRequests')
(control/'container-admission.json').write_text(json.dumps(inspected))
began=time.time()
try:
    m.api('POST','/containers/'+name+'/start')
    waited=m.api('POST','/containers/'+name+'/wait?condition=not-running',timeout=20)
    assert waited['StatusCode']==0
    result=json.loads((control/'result.json').read_text())
finally:
    current=m.api('GET','/containers/'+name+'/json')
    assert current['Config']['Labels']['curaloop.task']=='lr-dc2-local-20261113-v1'
    if current['State']['Running']:m.api('POST','/containers/'+name+'/stop?t=1',timeout=5)
    final=m.api('GET','/containers/'+name+'/json');assert not final['State']['Running']
    (control/'final-container-state.json').write_text(json.dumps(final))
    m.api('DELETE','/containers/'+name)
result.update(instance_id=identity,wall_seconds=time.time()-began,reference_rerun=False,unmodified_evaluator_sha256=hashlib.sha256((overlay/p['case']['eval_script_name']).read_bytes()).hexdigest())
(control/'concordance-result.json').write_text(json.dumps(result))
print(json.dumps(result))
"""


def main():
    authority()
    folder = TASK / "native-scorer-concordance-v1"
    folder.mkdir(exist_ok=False)
    upstream = TASK / "source-concordance-v1/upstream_compute_scores.py"
    tree = ast.parse(upstream.read_text(encoding="utf-8"))
    assert any(
        isinstance(n, ast.Assign)
        and isinstance(n.value, ast.Name)
        and n.value.id == "result"
        and any(
            isinstance(t, ast.Tuple)
            and [getattr(e, "id", None) for e in t.elts] == ["success", "log_info"]
            for t in n.targets
        )
        for n in ast.walk(tree)
    )
    previous = read(PUBLIC / "native-reference-qualification-v3.json")
    rows = read(TASK / "catalog-v1/public-task-and-evaluator-metadata.json")
    decoder = ROOT / "research/local_agent_eval_v1/native_result.py"
    encoded = base64.b64encode(REMOTE.encode()).decode()
    command = "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""
    corrected = []
    for original in previous["results"]:
        identity = original["instance_id"]
        item = dict(original)
        if original.get("reference_exit_code") == 0:
            name = f"native-interface-concordance-{identity:03d}-v1"
            reserve(name, 20)
            row = next(r for r in rows if r["instance_id"] == identity)
            payload = {
                "case": {k: row[k] for k in ("instance_id", "eval_script_name")},
                "decoder_b64": base64.b64encode(decoder.read_bytes()).decode(),
                "decoder_sha256": sha(decoder),
                "scorer_source": SCORER,
                "outer_source": OUTER,
            }
            value = invoke(command, payload, 60)
            assert value["unmodified_evaluator_sha256"] == row["evaluator_sha256"]
            settle(name, value, folder / f"rescore-{identity:03d}.json")
            item.update(
                native_success=value["native_success"],
                native_interface_status=value["status"],
                reference_rerun=False,
                prior_nominal_false_was_unsupported_tuple_not_scientific_failure=True,
            )
        corrected.append(item)
    locked = [
        r for r in corrected if r["role"] == "locked_candidate" and r["native_success"] is True
    ]
    development = [
        r for r in corrected if r["role"] == "development" and r["native_success"] is True
    ]
    groups = sorted({r["lineage_group"] for r in locked})
    passed = bool(development) and len(locked) >= 6 and len(groups) >= 4
    result = {
        "status": "PASS_NATIVE_PILOT_COHORT"
        if passed
        else "DATA_NOT_READY_USE_APPROVED_BOUNDED_FALLBACK",
        "previous_nominal_cohort_result_invalid_due_to_adapter_contract_mismatch": True,
        "source_commit": "c26e151ed601ba109dc4d35e057ff8e73fec469d",
        "source_path": "compute_scores.py",
        "source_blob_sha": "0be3e805d85f0f3477f028e54714cb55c2dac91e",
        "retained_source_sha256": sha(upstream),
        "decoder_sha256": sha(decoder),
        "reference_training_or_execution_repeated": False,
        "development_ids": [r["instance_id"] for r in development],
        "locked_candidate_ids": [r["instance_id"] for r in locked],
        "locked_repository_lineage_groups": groups,
        "minimum_rules_unchanged": previous["minimum_rules_unchanged"],
        "results": corrected,
        "candidate_model_evaluation": "NOT_RUN",
        "matrix_frozen": False,
        "protected_old_outcomes_opened": False,
    }
    write(PUBLIC / "native-reference-qualification-corrected-v1.json", result)
    ledger = read(TASK / "ledger.json")
    ledger["gates"]["native_cohort"] = {
        "decision": "PASS" if passed else "FALLBACK_NATIVE_INFEASIBLE",
        "receipt_sha256": sha(PUBLIC / "native-reference-qualification-corrected-v1.json"),
        "supersedes_invalid_wrapper_result_not_a_changed_native_rule": True,
    }
    save(ledger)
    print(json.dumps({k: v for k, v in result.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
