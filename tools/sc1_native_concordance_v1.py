"""Static concordance against the official gold/prompt assembly; no test rerun."""
import ast
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path
from tools.sc1_control_v1 import ACCOUNT, ROOT, write_new
from tools.sc1_native_transport_v1 import SSH


def main():
    root = ROOT / "research/raw_data/external-benchmarks/scicode-2024"
    code = root / "upstream-code"
    evaluator = ast.parse((code / "eval/inspect_ai/scicode.py").read_text())
    model = ast.parse((code / "src/scicode/gen/models.py").read_text())
    definitions = [node for node in evaluator.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in {"ScicodePromptingAssistant", "generate_gold_response"}]
    definitions += [node for node in model.body if isinstance(node, ast.FunctionDef) and node.name == "extract_python_script"]
    namespace = {"Path": Path, "re": re, "DEFAULT_PROMPT_TEMPLATE": (code / "eval/data/background_comment_template.txt").read_text()}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), "verified_upstream_assembly", "exec"), namespace)
    target = ACCOUNT / "gold-concordance-v1"
    target.mkdir(exist_ok=False)
    helper = namespace["ScicodePromptingAssistant"](target / "generated", target / "prompts", True)
    rows = [json.loads(line) for line in (root / "upstream-hf/problems_dev.jsonl").read_text().splitlines()]
    row = next(r for r in rows if r["problem_id"] == "70")
    for idx in range(len(row["sub_steps"])):
        _, previous = helper.prepare_final_prompt_with_steps(row, idx + 1, len(row["sub_steps"]), save=False)
        response = namespace["generate_gold_response"](row, idx + 1)
        helper.register_previous_response(row, response, previous, idx + 1)
    program = '''import json
from pathlib import Path
p=Path('/home/chaw/curaloop-tasks/lr-sc1-20261113-v1/control/qualify-v2')
print(json.dumps({'candidate_script':(p/'gold-70.8.py').read_text(),'stderr':(p/'gold-70.8.stderr.txt').read_text()}))
'''
    encoded = base64.b64encode(program.encode()).decode()
    p = subprocess.run(SSH + ["python3 -c \"import base64;exec(base64.b64decode('" + encoded + "'))\""], capture_output=True, text=True, timeout=40)
    if p.returncode:
        raise RuntimeError("Read-only concordance transport failed")
    raw = json.loads(p.stdout)
    write_new(target / "remote-program-and-error.json", raw)
    actual = raw["candidate_script"].rsplit("\nfrom scicode.parse.parse import process_hdf5_to_tuple\n", 1)[0]
    expected = (target / "generated/with_background/70.8.py").read_text()
    expected_ast = ast.dump(ast.parse(expected), include_attributes=False)
    actual_ast = ast.dump(ast.parse(actual), include_attributes=False)
    result = {"status": "PASS_STATIC_NATIVE_ASSEMBLY_CONCORDANCE" if actual_ast == expected_ast else "FAIL_ADAPTER_CONCORDANCE",
              "case": "70.8", "official_saved_gold_program_ast_sha256": hashlib.sha256(expected_ast.encode()).hexdigest(),
              "admission_program_ast_sha256": hashlib.sha256(actual_ast.encode()).hexdigest(),
              "native_gold_assembly_ast_identical": actual_ast == expected_ast,
              "retained_v2_failure": "AssertionError" if "AssertionError" in raw["stderr"] else raw["stderr"][-300:],
              "test_reruns": 0, "new_model_calls": 0, "test_outcomes_accessed": False,
              "causal_limit": "Reference/native-target/environment mismatch remains unresolved; this is not proof of a universally defective dataset"}
    write_new(target / "concordance.json", result)
    write_new(ROOT / "docs/evidence/lr-sc1-20261113-v1/native-assembly-concordance-v1.json", result)
    print(json.dumps(result))
    if actual_ast != expected_ast:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
