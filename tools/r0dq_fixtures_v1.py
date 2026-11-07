"""Meaningful constructed privacy/support fixtures before source intake."""
import json
import sqlite3
from r0dq_core_v1 import LocalGuard,PRIVATE,ROOT,save,archive_code
from r0dq_projection_v1 import PresenceValidator,protect_metadata_connection


def run(output_name='projection-fixtures-v1.json'):
    connection=sqlite3.connect(':memory:')
    connection.executescript('CREATE TABLE activities(activity_id INTEGER,assay_id INTEGER,molregno INTEGER,standard_type TEXT,standard_relation TEXT,standard_units TEXT,standard_value,doc_id INTEGER,pchembl_value,activity_comment TEXT);')
    connection.executemany('INSERT INTO activities VALUES(?,?,?,?,?,?,?,?,?,?)',[
        (1,10,20,'Ki','=','nM',12.345,30,1,'SENTINEL_NOT_EXPORT'),
        (2,10,21,'Ki','=','nM',None,30,None,None),
        (3,10,22,'Ki','>','nM',99.876,30,None,None),
        (4,10,23,'Ki','=','%',3.14,30,None,None),
        (5,10,24,'Kd','=','nM',-4.56,30,None,None),
        (6,10,25,'Kd','=','nM','nan',30,None,None)])
    connection.executescript('CREATE TABLE unrelated_outcomes(secret_value); INSERT INTO unrelated_outcomes VALUES(777);')
    connection.commit()
    clone=sqlite3.connect(':memory:');connection.backup(clone)
    protect_metadata_connection(clone)
    checks={}
    assert clone.execute('SELECT activity_id,molregno FROM activities').fetchall()
    checks['outcome_free_projection_allowed']=True
    try:clone.execute('SELECT secret_value FROM unrelated_outcomes').fetchall()
    except sqlite3.DatabaseError:checks['metadata_default_denies_other_outcome_tables']=True
    else:raise AssertionError('Unknown table admitted')
    for column in ['standard_value','pchembl_value','activity_comment']:
        try:clone.execute('SELECT '+column+' FROM activities').fetchall()
        except sqlite3.DatabaseError:checks['metadata_denies_'+column]=True
        else:raise AssertionError('Forbidden metadata column admitted')
    validator=PresenceValidator(connection,{1,2,3,4,5,6})
    output=validator.check([1,2,3,4,5,6])
    assert [r['exact_positive_finite_support'] for r in output]==[True,False,False,False,False,False]
    assert all(set(row)=={'activity_id','exact_positive_finite_support'} for row in output)
    assert '12.345' not in json.dumps(output) and 'SENTINEL_NOT_EXPORT' not in json.dumps(output)
    checks['present_missing_censor_unit_sign_nonfinite_distinguished']=True
    queries=[];connection.set_trace_callback(queries.append)
    try:validator.check([999])
    except PermissionError:pass
    else:raise AssertionError('Protected/unfrozen ID admitted')
    assert queries==[]
    checks['unfrozen_id_rejected_before_query']=True
    try:clone.execute('UPDATE activities SET standard_value=0')
    except sqlite3.DatabaseError:checks['metadata_cannot_write']=True
    else:raise AssertionError('Metadata connection can change source')
    result={'status':'PASS_CONSTRUCTED_CONTRACT_FIXTURES','checks':checks,'passed':len(checks),
            'real_database_validated':False,'scientific_gold':False}
    assert not (PRIVATE/output_name).exists()
    save(PRIVATE/output_name,result)
    archive_code(ROOT/'tools/r0dq_projection_v1.py')
    print(json.dumps(result))


if __name__=='__main__':
    guard=LocalGuard('projection-fixtures-v1',cpu_seconds=60,memory_mib=256)
    try:run()
    except Exception as exc:
        guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
