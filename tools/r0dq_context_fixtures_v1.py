"""Bounded pre-source procedural projection checks."""
import ast,json
from r0dq_core_v1 import LocalGuard,PRIVATE,ROOT,save,archive_code
from r0dq_context_projection_v1 import fixtures,project_text

if __name__=='__main__':
    guard=LocalGuard('context-fixtures-v1',cpu_seconds=30,wall=120,memory_mib=256)
    try:
        result=fixtures()
        mixed=project_text('After incubation, binding was 12 nM. COS-7 cells were incubated for 30 min at 37 C.')
        assert '12 nM' not in mixed['text'] and 'COS-7' in mixed['text'] and '30 min' in mixed['text']
        for path in list((ROOT/'tools').glob('r0dq_*.py'))+list((ROOT/'research/taskfirst_dq_v1').glob('*.py')):
            ast.parse(path.read_text(encoding='utf-8'));archive_code(path)
        result.update(additional_mixed_sentence_check=True,all_phase_python_syntax_valid=True)
        save(PRIVATE/'context-fixtures-v1.json',result);print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
