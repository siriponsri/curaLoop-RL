"""Constructed transport checks: prevent replay after ambiguous remote completion."""
import json,subprocess
from pathlib import Path
from unittest.mock import patch
from tools import m2c_batch_v2 as transport


def checks(task):
    fixture=Path(task)/'transport-check-fixtures';fixture.mkdir(exist_ok=False)
    (fixture/'ssh-profile.json').write_text(json.dumps({'selected_profile':'SYNTHETIC_NO_NETWORK'}))
    results=[];source='print("{}")'
    success=subprocess.CompletedProcess([],0,b'{}',b'')
    timeout=subprocess.CompletedProcess([],255,b'',b'ssh: connect to host example port 22: Connection timed out\r\n')
    auth=subprocess.CompletedProcess([],255,b'',b'Permission denied (publickey).')
    partial=subprocess.CompletedProcess([],255,b'{"started":',b'ssh: connect to host example port 22: Connection timed out')
    def check(name,replies,expected_calls,should_succeed):
        calls=[]
        def fake(*args,**kwargs):
            calls.append((args,kwargs));return replies[len(calls)-1]
        with patch.object(transport,'TASK',fixture),patch.object(transport.subprocess,'run',fake):
            succeeded=False
            try:assert transport.ssh_script(source)=={};succeeded=True
            except AssertionError:pass
        assert succeeded==should_succeed and len(calls)==expected_calls,name
        assert all(c[1]['input']==source.encode() for c in calls)
        results.append({'name':name,'status':'PASS','mock_connections':len(calls)})
    check('successful-connection-dispatched-once',[success],1,True)
    check('proven-tcp-timeout-retries-identical-undispatched-payload',[timeout,success],2,True)
    check('authentication-failure-is-not-retried',[auth],1,False)
    check('partial-output-or-ambiguous-completion-is-never-retried',[partial],1,False)
    check('tcp-retries-stop-after-three-connect-attempts',[timeout,timeout,timeout],3,False)
    result={'status':'PASS_CONSTRUCTED_TRANSPORT_CHECKS','checks':results,'network_calls_made':0,'scientific_units_run':0}
    with (Path(task)/'transport-constructed-checks-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    return result
