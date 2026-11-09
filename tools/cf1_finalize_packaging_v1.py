"""Preserve executed controllers before import-only publication cleanup."""
# ruff: noqa: E402

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start


def without_imports(text):
    tree = ast.parse(text)
    tree.body = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
    return ast.dump(tree, include_attributes=False)


def main():
    names = ["tools/cf1_remote_v1.py", "tools/cf1_science_v1.py"]
    original, pins = {}, {}
    for name in names:
        path = ROOT / name
        original[name] = path.read_text(encoding="utf-8")
        target = TASK / "packaging-history" / path.name
        target.parent.mkdir(exist_ok=True)
        with target.open("xb") as file:
            file.write(path.read_bytes())
        pins[name] = {"executed_source_sha256": sha(target)}
    lint = subprocess.run(["rtk", "proxy", "ruff", "check", "--fix", *names], capture_output=True, text=True, timeout=60)
    assert lint.returncode == 0, lint.stdout
    for name in names:
        assert without_imports(original[name]) == without_imports((ROOT / name).read_text(encoding="utf-8"))
        pins[name]["packaged_source_sha256"] = sha(ROOT / name)
    for name, expected in read(TASK / "code-pins-science-v2.json").items():
        assert sha(ROOT / name) == expected
    new(PUBLIC / "controller-packaging-polish-v1.json", {"status": "PASS_IMPORT_ONLY_PACKAGING_WITH_EXECUTED_SNAPSHOT",
        "changes": "unused imports and import ordering only", "non_import_AST_unchanged": True,
        "all_scientific_worker_pins_unchanged": True, "executed_sources_preserved_privately": True, "files": pins})
    # Failed quality attempts remain intact; repaired checks get fresh names.
    source = (ROOT / "tools/cf1_english_polish_v1.py").read_text(encoding="utf-8")
    source = source.replace("def polish(text):", "def polish_prose(text):")
    wrapper = '''def polish(text):
    parts = re.split(r"(\\]\\([^)]*\\)|```[\\s\\S]*?```|`[^`]*`)", text)
    return "".join(part if part.startswith(("](", "`")) else polish_prose(part) for part in parts)


'''
    assert "def main():" in source
    source = source.replace("def main():", wrapper + "def main():", 1)
    source = source.replace("english-polish-v1.json", "english-polish-v2.json").replace("english-document-polish-v1", "english-document-polish-v2")
    with (ROOT / "tools/cf1_english_polish_v2.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(source)
    audit = (ROOT / "tools/cf1_audit_v1.py").read_text(encoding="utf-8")
    audit = audit.replace("final-audit-v1", "final-audit-v2").replace("final-lint-v1", "final-lint-v2").replace("closure-audit-v1", "closure-audit-v2")
    with (ROOT / "tools/cf1_audit_v2.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(audit)
    print("PASS executed controllers preserved; non-import AST and worker pins unchanged; fresh quality checks prepared")


if __name__ == "__main__":
    guard = start("controller-packaging-polish-v1", 120, 300, bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("controller-packaging-polish-v1", guard, "PASS_IMPORT_ONLY_PACKAGING")
    except BaseException:
        finish("controller-packaging-polish-v1", guard, "FAIL")
        raise
