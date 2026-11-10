"""Read-only local/remote runtime admission; no remote task root creation."""

import base64
import json
import shutil
import subprocess

from cf2p_admin_v1 import PUBLIC, ROOT, TASK, read, write


def main():
    release = read(TASK / "release.json")
    local = {"python": shutil.which("python"), "node": shutil.which("node"), "npm": shutil.which("npm"),
             "existing_frontend_dependencies": (ROOT / "frontend/node_modules").is_dir(),
             "local_python_environment": (ROOT / ".venv/Scripts/python.exe").is_file(),
             "disk_free": shutil.disk_usage(ROOT).free, "deadline_utc": release["deadline_utc"]}
    for label, command in [("node_version", ["rtk", "proxy", "node", "--version"]),
                           ("python_packages", [str(ROOT / ".venv/Scripts/python.exe"), "-c",
                            "import fastapi,pydantic,pytest;print(fastapi.__version__,pydantic.__version__)"])]:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        local[label] = {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    write(TASK / "local-preflight-attempt-v2.json", local, True)
    assert local["existing_frontend_dependencies"] and local["local_python_environment"]
    assert local["node_version"]["exit_code"] == local["python_packages"]["exit_code"] == 0
    write(PUBLIC / "local-preflight-v1.json", {"status": "PASS_LOCAL_RUNTIME", **local}, True)
    config = subprocess.run(["rtk", "proxy", "ssh", "-G", "100.77.149.83"], capture_output=True, text=True, timeout=20)
    fields = dict(line.split(maxsplit=1) for line in config.stdout.splitlines() if len(line.split(maxsplit=1)) == 2)
    assert config.returncode == 0 and fields.get("user") == "chaw" and fields.get("hostname") == "100.77.149.83"
    assert "id_ed25519_dr_train" in config.stdout
    code = '''import json,os,pwd,resource,shutil,signal,subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,5));signal.alarm(20)
allowed=sorted(os.sched_getaffinity(0));cpu=allowed[-1];os.sched_setaffinity(0,{cpu})
roots=[Path.home()/'curaloop-tasks'/n for n in ['lr-cf2p-20261110-v1','lr-cf2p-20261110-v1-export-v1','lr-cf1-20261109-v1','lr-cf1-20261109-v1-export-v1']]
mem=next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
print(json.dumps({'user':pwd.getpwuid(os.getuid()).pw_name,'hostname':os.uname().nodename,'initial_cpu':cpu,'roots_absent':all(not p.exists() and not p.is_symlink() for p in roots),'memory_available':mem,'disk_free':shutil.disk_usage(Path.home()).free,'node':shutil.which('node'),'npm':shutil.which('npm'),'systemd_run':shutil.which('systemd-run'),'task_root_created':False,'compute_admitted':False}))
'''
    encoded = base64.b64encode(code.encode()).decode()
    command = 'python3 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
    result = subprocess.run(["rtk", "proxy", "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                             "-o", "ConnectTimeout=15", "100.77.149.83", command], capture_output=True, text=True, timeout=35)
    write(TASK / "ssh-readonly-response-v1.json", {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, True)
    if result.returncode:
        write(PUBLIC / "remote-preflight-v1.json", {"status": "UNAVAILABLE_LOCAL_WORK_CONTINUES", "error": result.stderr,
              "task_root_created": False, "private_key_read": False, "configuration_changed": False}, True)
    else:
        value = json.loads(result.stdout)
        assert value["user"] == "chaw" and value["hostname"] == "dr-train" and value["roots_absent"]
        write(PUBLIC / "remote-preflight-v1.json", {"status": "PASS_READ_ONLY_NOT_COMPUTE_ADMISSION", **value}, True)
    print("PASS local runtime and recorded optional remote read-only status")


if __name__ == "__main__":
    main()
