"""The single allowed source-supported technical repair: include native comparator."""
import json
import subprocess
from tools.sc1_control_v1 import ACCOUNT, ROOT, write_new
from tools.sc1_native_transport_v1 import SSH, REMOTE, reserve, settle


def main():
    old = ROOT / "tools/sc1_native_inside_v1.py"
    new = ROOT / "tools/sc1_native_inside_v2.py"
    source = old.read_text(encoding="utf-8")
    anchor = '    (package / "parse.py").write_text(adapted)\n'
    if source.count(anchor) != 1 or new.exists():
        raise RuntimeError("Unexpected repair source or existing attempt")
    replacement = anchor + '    import shutil\n    shutil.copytree(root / "code/src/scicode/compare", package.parent / "compare")\n'
    source = source.replace(anchor, replacement).replace('sys.argv[1] == "qualify"', 'sys.argv[1] == "qualify-v2"')
    new.write_text(source, encoding="utf-8", newline="\n")
    controller = (ROOT / "tools/sc1_remote_native_v1.py").read_text(encoding="utf-8")
    controller = controller.replace('{"setup", "probe", "qualify"}', '{"qualify-v2"}').replace('TASK / "inside.py"', 'TASK / "inside-v2.py"')
    host = ROOT / "tools/sc1_remote_native_v2.py"
    with host.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(controller)
    reserve("native-qualify-remote-v2", 3920)
    for path, destination in ((new, "inside-v2.py"), (host, "remote-v2.py")):
        p = subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", str(path), f"100.77.149.83:{REMOTE}/{destination}"], capture_output=True, text=True, timeout=45)
        if p.returncode:
            raise RuntimeError("Repair source transfer failed: " + p.stderr[-1000:])
    decision = {"status": "ONE_SOURCE_SUPPORTED_TECHNICAL_REPAIR", "cause": "The fixture-loader adapter omitted upstream scicode.compare, needed by native tests 70.6 and 10.7",
                "changes": ["Copy exact upstream scicode.compare package into evaluator-only support"],
                "native_assertions_changed": False, "references_changed": False, "targets_changed": False,
                "failed_assertion_70_8_preserved": True, "same_six_validation_main_problems": True,
                "new_model_calls": 0, "further_environment_repairs_allowed": 0}
    write_new(ACCOUNT / "native-repair-decision-v2.json", decision)
    p = subprocess.run(SSH + [f"python3 {REMOTE}/remote-v2.py qualify-v2"], input=json.dumps({"cpu": 3900, "wall": 4000}), capture_output=True, text=True, encoding="utf-8", timeout=4060)
    if p.returncode:
        raise RuntimeError("Repair qualification transport failed: " + p.stderr[-1500:])
    result = json.loads(p.stdout)
    settle("native-qualify-remote-v2", result)
    print(json.dumps(result))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
