"""Isolated native reference qualification. No model sees scorer or gold mounts."""

import hashlib
import importlib.util
import json
import os
import re
import resource
import shutil
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path, PurePosixPath

TASK = Path.home() / "curaloop-tasks/lr-dc2-local-20261113-v1"
IMAGE = "sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d"
NAME = "curaloop-dc2-local-native-20261113-v1"


def write(path, value):
    path = Path(path)
    with path.open("x") as out:
        json.dump(value, out, indent=2, ensure_ascii=False, allow_nan=False)
        out.write("\n")


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(65536):
            digest.update(block)
    return digest.hexdigest()


def docker_io():
    spec = importlib.util.spec_from_file_location("owned_model_io", TASK / "worker.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.authority()
    return module


def install(payload):
    assert TASK.is_dir() and not TASK.is_symlink()
    assert not (TASK / "native-worker-v1.py").exists()
    assert hashlib.sha256(payload["source"].encode()).hexdigest() == payload["source_sha256"]
    root = TASK / "native-v1"
    root.mkdir(exist_ok=False)
    for name in ("control", "env", "cases"):
        (root / name).mkdir()
    (TASK / "native-worker-v1.py").write_text(payload["source"])
    write(root / "expected-bundle.json", payload["bundle"])
    return {
        "status": "PASS_NATIVE_WORKER_INSTALLED_NO_EXECUTION",
        "source_sha256": payload["source_sha256"],
    }


def receive():
    root = TASK / "native-v1"
    expected = read(root / "expected-bundle.json")
    bundle = TASK / "native-assets-v1.tar.gz"
    assert bundle.stat().st_size == expected["bytes"] and sha(bundle) == expected["sha256"]
    assert not (root / "assets").exists()
    total, manifest = 0, {}
    with tarfile.open(bundle, "r:gz") as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            assert path.parts[0] == "assets" and not path.is_absolute() and ".." not in path.parts
            assert all(":" not in p and "\\" not in p for p in path.parts)
            assert member.isfile() and member.size <= 256 * 1024**2
            total += member.size
            assert total <= 1024**3
            target = root.joinpath(*path.parts)
            assert target.resolve().is_relative_to(root.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with tar.extractfile(member) as src, target.open("xb") as dst:
                while block := src.read(65536):
                    digest.update(block)
                    dst.write(block)
            manifest[member.name] = {"bytes": target.stat().st_size, "sha256": digest.hexdigest()}
    assert manifest == expected["members"]
    write(root / "received-manifest.json", manifest)
    return {
        "status": "PASS_FULL_BUNDLE_REREAD_AND_SEPARATE_ASSETS",
        "files": len(manifest),
        "expanded_bytes": total,
    }


WATCH = """import json,os,time
from pathlib import Path
while True:
    limits=json.loads(Path('/control/limits.json').read_text())
    usage=dict(line.split() for line in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())
    if time.time()>=limits['deadline_epoch'] or int(usage['usage_usec'])/1e6>=limits['cpu_cap_seconds']-3:
        os._exit(124)
    time.sleep(.5)
"""


def create_container(mode, case=None, *, cpu=600, wall=900):
    m = docker_io()
    root = TASK / "native-v1"
    assert mode in ("setup", "reference", "probe", "dependency-repair")
    assert not any("/" + NAME in r["Names"] for r in m.api("GET", "/containers/json?all=1"))
    control = root / "control" / ((mode if case is None else str(case["instance_id"])) + "-v2")
    control.mkdir(exist_ok=False)
    control.chmod(0o777)
    if mode in ("setup", "dependency-repair"):
        (root / "env").chmod(0o777)
    (control / "watch.py").write_text(WATCH)
    deadline = min(
        time.time() + wall,
        datetime.fromisoformat(read(TASK / "release.json")["deadline_utc"]).timestamp(),
    )
    write(control / "limits.json", {"deadline_epoch": deadline, "cpu_cap_seconds": cpu})
    mounts = [
        {"Type": "bind", "Source": str(control), "Target": "/control", "ReadOnly": False},
        {
            "Type": "bind",
            "Source": str(root / "env"),
            "Target": "/env",
            "ReadOnly": mode not in ("setup", "dependency-repair"),
        },
    ]
    if case is not None:
        identity = str(case["instance_id"])
        work = root / "cases" / (identity + "-v2")
        work.mkdir(exist_ok=False)
        work.chmod(0o777)
        (work / "pred_results").mkdir(mode=0o777)
        (work / "pred_results").chmod(0o777)
        original_eval = root / "assets/evaluators" / identity / "benchmark/eval_programs"
        overlay = root / "evaluator-mountpoints-v2" / identity
        overlay.mkdir(parents=True, exist_ok=False)
        (overlay / "gold_results").mkdir()
        for path in original_eval.iterdir():
            if path.is_file():
                shutil.copyfile(path, overlay / path.name)
                assert sha(path) == sha(overlay / path.name)
        mounts.extend(
            [
                {"Type": "bind", "Source": str(work), "Target": "/work", "ReadOnly": False},
                {
                    "Type": "bind",
                    "Source": str(root / "assets/inputs" / identity / "benchmark/datasets"),
                    "Target": "/work/benchmark/datasets",
                    "ReadOnly": True,
                },
                {
                    "Type": "bind",
                    "Source": str(
                        root / "assets/evaluators" / identity / "benchmark/gold_programs"
                    ),
                    "Target": "/work/benchmark/gold_programs",
                    "ReadOnly": True,
                },
                {
                    "Type": "bind",
                    "Source": str(overlay),
                    "Target": "/work/benchmark/eval_programs",
                    "ReadOnly": True,
                },
                {
                    "Type": "bind",
                    "Source": str(root / "assets/gold-results"),
                    "Target": "/work/benchmark/eval_programs/gold_results",
                    "ReadOnly": True,
                },
            ]
        )
    config = {
        "Image": IMAGE,
        "Cmd": ["python", "/control/watch.py"],
        "WorkingDir": "/work" if case else "/tmp",
        "Labels": {
            "curaloop.task": "lr-dc2-local-20261113-v1",
            "curaloop.purpose": "native-" + mode,
        },
        "Env": [
            "PYTHONPATH=/env",
            "OMP_NUM_THREADS=1",
            "OPENBLAS_NUM_THREADS=1",
            "MKL_NUM_THREADS=1",
            "NUMEXPR_NUM_THREADS=1",
            "LOKY_MAX_CPU_COUNT=1",
            "MPLBACKEND=Agg",
            "PYTHONDONTWRITEBYTECODE=1",
            "NVIDIA_VISIBLE_DEVICES=void",
        ],
        "HostConfig": {
            "NetworkMode": "bridge" if mode in ("setup", "dependency-repair") else "none",
            "NanoCpus": 1000000000,
            "CpusetCpus": str(sorted(os.sched_getaffinity(0))[-1]),
            "Memory": 8 * 1024**3,
            "MemorySwap": 8 * 1024**3,
            "PidsLimit": 128,
            "ReadonlyRootfs": True,
            "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges:true"],
            "Tmpfs": {"/tmp": "rw,size=1g"},
            "Mounts": mounts,
            "LogConfig": {"Type": "local", "Config": {"max-size": "5m", "max-file": "2"}},
        },
    }
    created = m.api("POST", "/containers/create?name=" + NAME, config)
    inspected = m.api("GET", "/containers/" + NAME + "/json")
    h = inspected["HostConfig"]
    assert inspected["Image"] == IMAGE and h["Memory"] == h["MemorySwap"] == 8 * 1024**3
    assert h["NanoCpus"] == 1000000000 and h["ReadonlyRootfs"] and not h.get("Privileged")
    assert not h.get("DeviceRequests") and h["NetworkMode"] == (
        "bridge" if mode in ("setup", "dependency-repair") else "none"
    )
    write(
        control / "container-admission.json",
        {"container_id": created["Id"], "host_config": h, "deadline_epoch": deadline},
    )
    m.api("POST", "/containers/" + NAME + "/start")
    return m, control


def finish(m, control):
    value = m.api("GET", "/containers/" + NAME + "/json")
    usage = None
    if value["State"]["Running"]:
        try:
            out, _ = m.execute(NAME, ["cat", "/sys/fs/cgroup/cpu.stat"], timeout=5)
            usage = (
                int(dict(line.split() for line in out.decode().splitlines())["usage_usec"]) / 1e6
            )
        finally:
            m.api("POST", "/containers/" + NAME + "/stop?t=2", timeout=10)
    value = m.api("GET", "/containers/" + NAME + "/json")
    assert not value["State"]["Running"]
    write(control / "final-state.json", {"state": value["State"], "observed_cpu_seconds": usage})
    m.api("DELETE", "/containers/" + NAME)
    return usage


def setup():
    m, control = create_container("setup", cpu=900, wall=1500)
    (control / "constraints.txt").write_text(
        "numpy==1.26.4\npandas==2.2.3\nscipy==1.13.1\nscikit-learn==1.5.2\nrdkit==2024.9.6\n"
    )
    packages = [
        [
            "numpy==1.26.4",
            "pandas==2.2.3",
            "scipy==1.13.1",
            "scikit-learn==1.5.2",
            "rdkit==2024.9.6",
            "openpyxl==3.1.5",
        ],
        ["mastml"],
        ["matminer"],
        ["papyrus-scripts"],
        ["prolif", "MDAnalysis"],
        ["biopsykit"],
    ]
    script = r"""import importlib.metadata,json,os,subprocess,sys,time
from pathlib import Path
groups=json.loads(sys.stdin.read()); results=[]
for i,packages in enumerate(groups):
    with open('/control/pip-'+str(i)+'.log','wb') as log:
        command=[sys.executable,'-m','pip','install','--disable-pip-version-check','--only-binary=:all:','--no-cache-dir','--target=/env','--constraint=/control/constraints.txt','--report=/control/pip-report-'+str(i)+'.json',*packages]
        began=time.time()
        try:
            p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=220)
            results.append({'packages':packages,'exit_code':p.returncode,'wall_seconds':time.time()-began})
        except subprocess.TimeoutExpired:
            results.append({'packages':packages,'exit_code':124,'wall_seconds':time.time()-began})
    size=sum(p.stat().st_size for p in Path('/env').rglob('*') if p.is_file())
    if size>3*1024**3: raise RuntimeError('Dependency directory exceeds scoped disk ceiling')
    if i==0 and results[-1]['exit_code']!=0: break
versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=['/env'])}
Path('/control/setup-result.json').write_text(json.dumps({'status':'SETUP_ATTEMPTED','groups':results,'versions':versions,'environment_bytes':size}))
print(json.dumps({'groups':results,'environment_bytes':size}))
"""
    try:
        (control / "install.py").write_text(script)
        m.execute(
            NAME, ["python", "/control/install.py"], json.dumps(packages).encode(), timeout=1450
        )
        result = read(control / "setup-result.json")
    finally:
        usage = finish(m, control)
    write(
        TASK / "native-v1/setup-receipt.json",
        {
            **result,
            "observed_cpu_seconds": usage,
            "network_only_for_dependency_setup": True,
            "candidate_or_gold_execution": False,
        },
    )
    return {
        "status": "PASS_SETUP_ATTEMPTS_RETAINED",
        "groups": result["groups"],
        "environment_bytes": result["environment_bytes"],
    }


def guard_probe():
    m, control = create_container("probe", cpu=30, wall=15)
    began = time.time()
    try:
        while time.time() - began < 23:
            state = m.api("GET", "/containers/" + NAME + "/json")["State"]
            if not state["Running"]:
                assert state["ExitCode"] == 124
                result = {
                    "status": "PASS_NATIVE_WALL_WATCHDOG_ACTUALLY_TERMINATED",
                    "elapsed_seconds": time.time() - began,
                    "state": state,
                }
                write(control / "probe-result.json", result)
                return result
            time.sleep(0.5)
        raise RuntimeError("Native watchdog did not terminate on time")
    finally:
        finish(m, control)


def qualify(payload):
    case = payload["case"]
    assert case["instance_id"] in (2, 3, 5, 16, 18, 19, 22, 26, 40, 41, 85)
    assert re.fullmatch(r"[A-Za-z0-9_.-]+\.py", case["gold_program_name"])
    assert re.fullmatch(r"[A-Za-z0-9_.-]+\.py", case["eval_script_name"])
    m, control = create_container("reference", case, cpu=620, wall=650)
    script = r"""import importlib.util,json,os,runpy,subprocess,sys,time,traceback
from pathlib import Path
case=json.load(sys.stdin); result={'instance_id':case['instance_id'],'native_success':False}
began=time.time()
with open('/control/reference.log','wb') as out:
    try:
        p=subprocess.run([sys.executable,'benchmark/gold_programs/'+case['gold_program_name']],stdout=out,stderr=subprocess.STDOUT,timeout=600)
        result['reference_exit_code']=p.returncode
    except subprocess.TimeoutExpired:
        result['reference_exit_code']=124
result['reference_wall_seconds']=time.time()-began
if result['reference_exit_code']==0:
    try:
        import contextlib
        with open('/control/native-scorer.log','w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            spec=importlib.util.spec_from_file_location('isolated_native_scorer','benchmark/eval_programs/'+case['eval_script_name'])
            module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            value=module.eval()
        result['native_result_type']=type(value).__name__
        if isinstance(value,(bool,int,float)):
            result['native_success']=bool(value==1)
        elif type(value).__module__.startswith('numpy') and getattr(value,'ndim',None)==0:
            result['native_success']=bool(value==1)
        else:
            result['native_return_not_admitted']=True
    except Exception as e:
        result['scorer_error_type']=type(e).__name__
        Path('/control/scorer-error-private.log').write_text(traceback.format_exc())
else:
    text=Path('/control/reference.log').read_text(errors='replace')
    result['reference_error_type']='Timeout' if result['reference_exit_code']==124 else 'ReferenceProgramFailure'
    # Only dependency names leave the private evaluator; no gold source lines.
    import re
    match=re.search(r"ModuleNotFoundError: No module named '([A-Za-z0-9_.-]+)'",text)
    if match: result['missing_module']=match.group(1)
Path('/control/qualification-result.json').write_text(json.dumps(result))
print(json.dumps(result))
"""
    try:
        (control / "qualify.py").write_text(script)
        m.execute(NAME, ["python", "/control/qualify.py"], json.dumps(case).encode(), timeout=640)
        result = read(control / "qualification-result.json")
    finally:
        usage = finish(m, control)
    result["observed_cpu_seconds"] = usage
    write(control / "final-qualification.json", result)
    return result


def dependency_repair():
    m, control = create_container("dependency-repair", cpu=300, wall=600)
    (control / "constraints.txt").write_text(
        "numpy==1.26.4\npandas==2.2.3\nscipy==1.13.1\nscikit-learn==1.5.2\nrdkit==2024.9.6\n"
    )
    script = r"""import importlib.metadata,json,subprocess,sys,time
from pathlib import Path
base=[sys.executable,'-m','pip','install','--disable-pip-version-check','--no-cache-dir','--target=/env']
groups=[['--no-deps','--only-binary=:all:','mastml','papyrus-scripts','biopsykit'],
        ['--only-binary=:all:','--constraint=/control/constraints.txt','shap==0.46.0','pystow','more-itertools','pingouin','neurokit2','mne'],
        ['--no-deps','mordred==1.2.0']]
results=[]
for i,group in enumerate(groups):
    with open('/control/repair-'+str(i)+'.log','wb') as log:
        began=time.time()
        try:
            p=subprocess.run(base+['--report=/control/repair-report-'+str(i)+'.json']+group,stdout=log,stderr=subprocess.STDOUT,timeout=170)
            results.append({'arguments':group,'exit_code':p.returncode,'wall_seconds':time.time()-began})
        except subprocess.TimeoutExpired:
            results.append({'arguments':group,'exit_code':124,'wall_seconds':time.time()-began})
versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=['/env'])}
Path('/control/repair-result.json').write_text(json.dumps({'status':'ONE_BOUNDED_DEPENDENCY_REPAIR_ATTEMPT','groups':results,'versions':versions}))
print(json.dumps({'groups':results}))
"""
    try:
        (control / "repair.py").write_text(script)
        m.execute(NAME, ["python", "/control/repair.py"], timeout=570)
        result = read(control / "repair-result.json")
    finally:
        usage = finish(m, control)
    write(control / "final-repair.json", {**result, "observed_cpu_seconds": usage})
    return {"status": result["status"], "groups": result["groups"], "observed_cpu_seconds": usage}


if __name__ == "__main__":
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[-3:])
    payload = json.load(sys.stdin)
    action = sys.argv[1]
    if action == "install":
        result = install(payload)
    elif action == "receive":
        result = receive()
    elif action == "setup":
        result = setup()
    elif action == "guard-probe":
        result = guard_probe()
    elif action == "qualify":
        result = qualify(payload)
    elif action == "dependency-repair":
        result = dependency_repair()
    else:
        raise ValueError("Unregistered native operation")
    print(json.dumps(result))
