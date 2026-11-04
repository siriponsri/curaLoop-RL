"""Fresh offline-installed venv + local clone reproduction of the frozen pilot.

Requires seven named wheels in the ignored wheelhouse; never touches original
run/data artifacts. This is same-implementer, same-host environment reproduction.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "d57838d41b30d956c7fd72ac502c1765653fd087"
WORK = ROOT / ".local/repro-ncats-20261104-v1"
PACKET = ROOT / "docs/evidence/ncats-reproduction-20261104-v1"
PINS = {
    "numpy": "2.3.5",
    "scipy": "1.17.0",
    "scikit-learn": "1.8.0",
    "rdkit": "2026.9.1",
    "threadpoolctl": "3.6.0",
    "joblib": "1.5.3",
    "pillow": "13.0.0",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    if PACKET.exists() or (WORK / "env").exists() or (WORK / "checkout").exists():
        raise ValueError("Preserve existing attempts; use a new version instead of overwriting.")
    if shutil.disk_usage(ROOT).free < 3_000_000_000:
        raise ValueError("Need 3 GB free for bounded isolated environment setup.")
    PACKET.mkdir(parents=True)
    (PACKET / "logs").mkdir()
    (PACKET / ".gitattributes").write_text(
        "runs/*.json -text\n*.json whitespace=trailing-space,space-before-tab,cr-at-eol\n"
        "*.txt whitespace=trailing-space,space-before-tab,cr-at-eol\n",
        encoding="utf-8",
        newline="\n",
    )
    state = {
        "status": "RUNNING",
        "source_commit": BASE,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "commands": [],
        "scope": "SAME_HOST_FRESH_VENV_AND_CLONE; not independent scientific review",
        "run_wall_cap_seconds": 300,
        "gpu_jobs": 0,
        "paid_compute_calls": 0,
    }
    save(PACKET / "attempt.json", state)

    def command(name, args, cwd, timeout):
        print("START " + name, flush=True)
        start = time.perf_counter()
        proc = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, timeout=timeout)
        (PACKET / "logs" / (name + ".txt")).write_bytes(proc.stdout + proc.stderr)
        state["commands"].append(
            {
                "name": name,
                "argv": list(map(str, args)),
                "cwd": str(cwd),
                "exit_code": proc.returncode,
                "wall_seconds": time.perf_counter() - start,
            }
        )
        save(PACKET / "attempt.json", state)
        if proc.returncode:
            raise RuntimeError(name + " failed; retained full log")
        print("PASS " + name, flush=True)

    try:
        wheels = sorted((WORK / "wheelhouse").glob("*.whl"))
        if len(wheels) != len(PINS):
            raise ValueError("Expected exactly seven source-version wheels.")
        save(
            PACKET / "wheel-manifest.json",
            {w.name: {"bytes": w.stat().st_size, "sha256": sha(w.read_bytes())} for w in wheels},
        )
        (PACKET / "requirements.txt").write_text(
            "\n".join(k + "==" + v for k, v in PINS.items()) + "\n"
        )
        command("create-venv", [sys.executable, "-m", "venv", WORK / "env"], ROOT, 180)
        py = WORK / "env/Scripts/python.exe"
        command(
            "offline-install",
            [
                py,
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                "--find-links",
                WORK / "wheelhouse",
                "-r",
                PACKET / "requirements.txt",
            ],
            ROOT,
            180,
        )
        command("pip-check", [py, "-m", "pip", "check"], ROOT, 30)
        command(
            "clone",
            ["git", "clone", "--local", "--no-hardlinks", "--no-checkout", ROOT, WORK / "checkout"],
            ROOT,
            60,
        )
        checkout = WORK / "checkout"
        command("checkout", ["git", "checkout", "--detach", BASE], checkout, 30)
        env_code = (
            "import sys,json,site; from importlib.metadata import version,distribution; names="
            + repr(tuple(PINS))
            + "; print(json.dumps({'prefix':sys.prefix,'base_prefix':sys.base_prefix,'python':sys.version,'sys_path':sys.path,'site_packages':site.getsitepackages(),'packages':{n:{'version':version(n),'location':str(distribution(n).locate_file(''))} for n in names}},indent=2))"
        )
        command("environment", [py, "-I", "-c", env_code], checkout, 30)
        env = json.loads((PACKET / "logs/environment.txt").read_text())
        assert all(
            v["version"] == PINS[k] and Path(v["location"]).is_relative_to(WORK / "env")
            for k, v in env["packages"].items()
        )
        assert "include-system-site-packages = false" in (WORK / "env/pyvenv.cfg").read_text()
        cfg_path = checkout / "research/configs/ncats_development_v1.json"
        cfg = json.loads(cfg_path.read_text())
        raw = checkout / "research/raw_data/ncats-development-20261104"
        raw.mkdir(parents=True)
        for assay, expected in cfg["raw_source_sha256"].items():
            source = ROOT / "research/raw_data/ncats-development-20261104" / (assay + ".smiles")
            assert sha(source.read_bytes()) == expected
            shutil.copy2(source, raw / source.name)
        command("prepare-cohorts", [py, "-m", "research.development.prepare_cohort"], checkout, 60)
        assert all(
            sha((raw / "prepared-v1" / (a + ".json")).read_bytes()) == expected
            for a, expected in cfg["cohort_sha256"].items()
        )
        runs = checkout / "research/runs/ncats-reproduction-20261104-v1"
        args = [
            py,
            "-m",
            "research.development.runner",
            "--config",
            cfg_path,
            "--output",
            runs,
            "--phase",
        ]
        command("canary", args + ["canary"], checkout, 120)
        ledger = json.loads((runs / "ledger.json").read_text())
        assert len(ledger["attempts"]) == 18 and all(
            v["status"] == "COMPLETE" for v in ledger["attempts"].values()
        )
        if ledger["wall_seconds"] * 6 > 300:
            raise RuntimeError(
                "Canary projection exceeds the frozen 300s reproduction cap; retain partial runs"
            )
        command("remaining-grid", args + ["all"], checkout, 340)
        ledger = json.loads((runs / "ledger.json").read_text())
        assert len(ledger["attempts"]) == 108
        original = ROOT / "docs/evidence/ncats-development-20261104-v1/runs"
        rows = []
        for run_id, entry in sorted(ledger["attempts"].items()):
            data = (runs / (run_id + ".json")).read_bytes()
            assert sha(data) == entry["sha256"]
            a, b = json.loads((original / (run_id + ".json")).read_text()), json.loads(data)
            keys = (
                "status",
                "identity",
                "initial_ids",
                "initial_active_count",
                "schedule_sha256",
                "metrics",
                "decisions",
                "decision_grid",
                "snapshot",
                "warnings",
                "restoration_verified",
            )
            equal = {k: a.get(k) == b.get(k) for k in keys}
            selector_keys = [k for k in a["selector"] if not k.endswith("wall_seconds")]
            equal["selector_non_timing"] = all(
                a["selector"][k] == b["selector"][k] for k in selector_keys
            )
            rows.append(
                {
                    "run_id": run_id,
                    "checks": equal,
                    "scientific_exact_match": all(equal.values()),
                    "original_sha256": sha((original / (run_id + ".json")).read_bytes()),
                    "fresh_sha256": sha(data),
                }
            )
        assert all(r["scientific_exact_match"] for r in rows), (
            "Scientific result/trace mismatch; retain all differences"
        )
        state["comparison"] = {
            "status": "PASS",
            "exact_scientific_runs": 108,
            "allowed_differences": [
                "execution environment/commit metadata",
                "CPU/wall timing fields",
                "file hashes containing those fields",
            ],
            "runs": rows,
        }
        state["resources"] = {
            k: ledger[k] for k in ("wall_seconds", "cpu_seconds", "peak_runner_working_set_bytes")
        }
        state["status"] = "PASS"
    except Exception as error:
        state["status"] = "FAILED"
        state["error"] = type(error).__name__ + ": " + str(error)
        raise
    finally:
        candidate = WORK / "checkout/research/runs/ncats-reproduction-20261104-v1"
        if candidate.exists():
            (PACKET / "runs").mkdir(exist_ok=True)
            for path in candidate.glob("*.json"):
                shutil.copy2(path, PACKET / "runs" / path.name)
        state["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        save(PACKET / "attempt.json", state)
        print("REPRODUCTION " + state["status"], flush=True)


if __name__ == "__main__":
    main()
