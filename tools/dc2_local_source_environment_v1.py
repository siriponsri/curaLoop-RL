"""One source-concordant environment batch; no new tasks or successful-reference refits."""

import ast
import base64
import json

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, save, sha, write
from dc2_local_native_recover_v3 import invoke
from dc2_local_native_v1 import reserve, settle

REMOTE = r'''
import base64,hashlib,json,os,shutil,sys
from pathlib import Path
p=json.load(sys.stdin);task=Path.home()/'curaloop-tasks/lr-dc2-local-20261113-v1'
raw=(task/'native-worker-v2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()==p['worker_sha256']
source=raw.decode()
for a,b in [('root = TASK / "native-v1"','root = TASK / "native-source-env-v1"'),('cpu=620','cpu=120'),('wall=650','wall=140'),('timeout=600','timeout=110'),('timeout=640','timeout=135'),('value=module.eval()',"from contract import decode_native_result; value=decode_native_result(module.eval())['success']")]:
    assert a in source,a;source=source.replace(a,b)
compile(source,'source-environment-adapter-v1.py','exec')
namespace={'__name__':'source_environment_adapter'};exec(compile(source,'source-environment-adapter-v1.py','exec'),namespace)
m=namespace['docker_io']();original_api=m.api
def api(method,path,body=None,timeout=30):
    if method=='POST' and path.startswith('/containers/create'):
        body['HostConfig']['Mounts'].append({'Type':'bind','Source':str(task/'native-v1/env'),'Target':'/env-base','ReadOnly':True})
        body['Env']=[v.replace('PYTHONPATH=/env','PYTHONPATH=/env:/env-base') for v in body['Env']]
    return original_api(method,path,body,timeout)
m.api=api;namespace['docker_io']=lambda:m
root=task/'native-source-env-v1'
if p['action']=='setup':
    assert not root.exists();root.mkdir();(root/'control').mkdir();(root/'env').mkdir();(root/'cases').mkdir()
    (root/'source-environment-adapter-v1.py').write_text(source)
    shutil.copytree(task/'native-v1/assets',root/'assets',copy_function=os.link)
    m,control=namespace['create_container']('setup',cpu=180,wall=300)
    setup=r"""import importlib.metadata,json,subprocess,sys,time
from pathlib import Path
packages=['pandas==1.5.3','rdkit==2023.9.5','matplotlib==3.7.5','pymatgen==2024.5.1','nilspodlib','imucal','pathos==0.3.2','multiprocess==0.70.16','dill==0.3.8','pox==0.3.4','ppft==1.7.6.8']
with open('/control/source-compatibility-pip.log','wb') as log:
    p=subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--no-cache-dir','--no-deps','--only-binary=:all:','--target=/env','--report=/control/source-compatibility-pip-report.json',*packages],stdout=log,stderr=subprocess.STDOUT,timeout=260)
versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=['/env'])}
Path('/control/setup-result.json').write_text(json.dumps({'exit_code':p.returncode,'versions':versions,'requested_packages':packages}))
"""
    (control/'setup.py').write_text(setup)
    try:
        m.execute(namespace['NAME'],['python','/control/setup.py'],timeout=280)
        result=json.loads((control/'setup-result.json').read_text())
    finally:namespace['finish'](m,control)
    result.update(status='SOURCE_BOUNDS_COMPATIBILITY_SETUP_ATTEMPT',new_tasks=False,new_models=False,old_environment_modified=False)
else:
    assert p['action']=='qualify'
    case=p['case'];assert case['instance_id'] in (2,22,26,85)
    prior=json.loads((task/'native-v1/control'/f"{case['instance_id']}-v2"/'qualification-result.json').read_text())
    assert prior['reference_exit_code']!=0,'Never refit a successful original reference'
    base_create=namespace['create_container']
    def create(*args,**kwargs):
        m,control=base_create(*args,**kwargs)
        decoder=base64.b64decode(p['decoder_b64'],validate=True);assert hashlib.sha256(decoder).hexdigest()==p['decoder_sha256']
        (control/'contract.py').write_bytes(decoder)
        return m,control
    namespace['create_container']=create
    result=namespace['qualify']({'case':case})
    result.update(status='SOURCE_CONCORDANT_REFERENCE_ATTEMPT',source_bounded_cpu_seconds=120,prior_failed_environment_only=True)
print(json.dumps(result))
'''


def main():
    authority()
    folder = TASK / "source-environment-concordance-v1"
    folder.mkdir(exist_ok=False)
    upstream = TASK / "source-concordance-v1/upstream_run_eval.py"
    source = upstream.read_text(encoding="utf-8")
    assert all(
        s in source
        for s in ("pandas<=1.5.3", "rdkit<=2023.09.5", "matplotlib<3.8.0", "pymatgen<=2024.5.1")
    )
    ast.parse(REMOTE)
    targets = [2, 22, 26, 85]
    plan = {
        "status": "FINAL_SINGLE_SOURCE_ENVIRONMENT_COMPATIBILITY_BATCH_BEFORE_AGENT_EVALUATION",
        "source_commit": "c26e151ed601ba109dc4d35e057ff8e73fec469d",
        "source_file": "run_eval.py",
        "upstream_source_sha256": sha(upstream),
        "target_ids": targets,
        "setup_cpu_seconds": 180,
        "per_reference_cpu_seconds": 120,
        "local_control_cpu_seconds": 60,
        "all_successful_original_references_preserved_not_refitted": True,
        "native_rules_data_task_roles_and_minimum_groups_unchanged": True,
        "further_environment_search_or_reference_retries": False,
    }
    write(PUBLIC / "source-environment-concordance-plan-v1.json", plan)
    previous = read(PUBLIC / "native-reference-qualification-corrected-v1.json")
    worker = ROOT / "tools/dc2_local_native_worker_v2.py"
    decoder = ROOT / "research/local_agent_eval_v1/native_result.py"
    encoded = base64.b64encode(REMOTE.encode()).decode()
    command = "python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""
    reserve("source-environment-compatibility-setup-v1", 180)
    setup = invoke(command, {"action": "setup", "worker_sha256": sha(worker)}, 350)
    settle("source-environment-compatibility-setup-v1", setup, folder / "setup.json")
    write(PUBLIC / "source-environment-setup-v1.json", setup)
    rows = read(TASK / "catalog-v1/public-task-and-evaluator-metadata.json")
    results = []
    for old in previous["results"]:
        identity = old["instance_id"]
        if identity not in targets or setup["exit_code"] != 0:
            results.append(old)
            continue
        name = f"source-environment-reference-{identity:03d}-v1"
        reserve(name, 120)
        row = next(r for r in rows if r["instance_id"] == identity)
        payload = {
            "action": "qualify",
            "worker_sha256": sha(worker),
            "case": {k: row[k] for k in ("instance_id", "gold_program_name", "eval_script_name")},
            "decoder_b64": base64.b64encode(decoder.read_bytes()).decode(),
            "decoder_sha256": sha(decoder),
        }
        result = invoke(command, payload, 200)
        result.update(role=old["role"], lineage_group=old["lineage_group"], prior_attempt=old)
        settle(name, result, folder / f"reference-{identity:03d}.json")
        results.append(result)
        print(
            json.dumps(
                {
                    "source_concordant_reference": identity,
                    "native_success": result["native_success"],
                    "reference_exit_code": result.get("reference_exit_code"),
                    "missing_module": result.get("missing_module"),
                }
            ),
            flush=True,
        )
    locked = [r for r in results if r["role"] == "locked_candidate" and r["native_success"] is True]
    development = [r for r in results if r["role"] == "development" and r["native_success"] is True]
    groups = sorted({r["lineage_group"] for r in locked})
    passed = bool(development) and len(locked) >= 6 and len(groups) >= 4
    receipt = {
        "status": "PASS_NATIVE_PILOT_COHORT"
        if passed
        else "DATA_NOT_READY_APPROVED_FALLBACK_FINAL_ADMISSION",
        "development_ids": [r["instance_id"] for r in development],
        "locked_candidate_ids": [r["instance_id"] for r in locked],
        "locked_repository_lineage_groups": groups,
        "minimum_rules_unchanged": previous["minimum_rules_unchanged"],
        "results": results,
        "successful_original_reference_fits_repeated": False,
        "failed_reference_source_compatibility_attempts": len(targets)
        if setup["exit_code"] == 0
        else 0,
        "candidate_model_evaluation": "NOT_RUN",
        "matrix_frozen": False,
        "further_environment_or_reference_retries": False,
    }
    write(PUBLIC / "native-admission-final-v1.json", receipt)
    ledger = read(TASK / "ledger.json")
    ledger["gates"]["native_cohort"] = {
        "decision": "PASS" if passed else "FALLBACK_NATIVE_INFEASIBLE_FINAL",
        "receipt_sha256": sha(PUBLIC / "native-admission-final-v1.json"),
    }
    save(ledger)
    print(json.dumps({k: v for k, v in receipt.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
