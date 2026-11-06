"""Cited cached-source UI checks and actual v2 OS-stdio export roundtrip."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch

def execute(root, output):
    root, output = Path(root), Path(output)
    sys.path.insert(0, str(root/'src'))
    from curaloop_rd.portfolio_v2 import Portfolio
    from curaloop_rd.workspace_v2 import render_workspace
    from curaloop_rd.contracts_v2 import digest
    output.mkdir(exist_ok=False)
    font=root/'font/NotoSansThai.ttf'
    app=Portfolio(root,root/'inputs/workflow-registry.json',output/'workspace',font)
    checks=[]
    def rejected(call):
        try:call()
        except ValueError:return
        raise AssertionError('Expected explicit rejection')
    brief={'report_id':'studio-endpoint','question':'Inspect the declared IC50 endpoint and unit.',
           'kind':'endpoint','source_ids':['D1259375'],'tid':2}
    try:
        drafted=app.call('draft_metadata_plan',brief)
        assert drafted['report']['report_sha256']=='706eb54e7417a31d161f333ef88b7ca752b1c1c20c6bae146fd48f071e16e50f'
        params={'report_id':brief['report_id'],'report_sha256':drafted['report']['report_sha256']}
        exported=app.call('local_export',params)
        assert app.call('local_export',params)==exported
        folder=Path(exported['local_folder']);view=Path(exported['workspace_v2']['local_folder'])
        for name,value in exported['manifest']['files'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==value
        assert (view/'report.json').read_bytes()==(folder/'report.json').read_bytes()
        checks.append('UI_C01_ORIGINAL_REPORT_AND_V1_EXPORT_UNCHANGED')
        for row in exported['workspace_v2']['manifest']['files']:
            assert hashlib.sha256((view/row['path']).read_bytes()).hexdigest()==row['sha256']
        assert exported['workspace_v2']['external_delivery'] is False
        checks.append('UI_C02_IDEMPOTENT_BILINGUAL_EXPORT_HASHES')
        briefs=[dict(brief,report_id='absent-endpoint',tid=3),
          {'report_id':'historical','question':'Check historical identity.','kind':'historical','source_ids':['R873_PUBLISHED','R873_INVALID','D873_PUBLISHED','D873_INVALID']},
          {'report_id':'identity','question':'Check compound identity.','kind':'identity','source_ids':['D2097','UNIPROT014']},
          {'report_id':'rights','question':'Check intended-use rights.','kind':'rights','source_ids':['NLM_POLICY']},
          {'report_id':'unavailable','question':'Check required source availability.','kind':'unavailable','source_ids':['SOURCE_ATTEMPTS']}]
        dispositions={drafted['report']['disposition']}
        for item in briefs:
            result=app.call('draft_metadata_plan',item)
            value=app.call('local_export',{'report_id':item['report_id'],'report_sha256':result['report']['report_sha256']})
            dispositions.add(result['report']['disposition'])
            assert result['readiness_plan']['molecular_experiments_released'] is False
            assert value['workspace_v2']['manifest']['report_sha256']==result['report']['report_sha256']
        assert dispositions=={'METADATA_REPORT','BLOCKED_ENDPOINT_UNRESOLVED','BLOCKED_HISTORICAL_IDENTITY','BLOCKED_RIGHTS_UNRESOLVED','BLOCKED_REQUIRED_SOURCE'}
        checks.append('UI_C03_ALL_FIVE_REAL_CACHED_SOURCE_DISPOSITIONS')
        evil='<script>alert("UI_ESCAPE_FIXTURE")</script> __ROWS__'
        safety=app.call('draft_metadata_plan',dict(brief,report_id='ui-escape-fixture',question=evil))
        escaped=app.call('local_export',{'report_id':'ui-escape-fixture','report_sha256':safety['report']['report_sha256']})
        text=(Path(escaped['workspace_v2']['local_folder'])/'workspace.html').read_text()
        assert evil not in text and '&lt;script&gt;' in text and '__ROWS__' in text
        checks.append('UI_C04_USER_TEXT_ESCAPED_WITHOUT_RECURSIVE_TEMPLATE_EXPANSION')
        copied=output/'tampered-copy';copied.mkdir()
        for name in ['report.json','report.md','preview.json','readiness-plan.json']:shutil.copyfile(folder/name,copied/name)
        tampered=json.loads((copied/'report.json').read_text());tampered['claims'][0]['value']=999
        (copied/'report.json').write_text(json.dumps(tampered))
        rejected(lambda:render_workspace(copied,output/'rejected-tamper',font))
        assert not (output/'rejected-tamper').exists()
        checks.append('UI_C05_REPORT_TAMPER_REJECTED_BEFORE_OUTPUT')
        # Labelled synthetic UI safety fixture; never presented as a provider claim.
        unsafe=output/'unsafe-link-fixture';unsafe.mkdir()
        for name in ['report.json','report.md','preview.json','readiness-plan.json']:shutil.copyfile(folder/name,unsafe/name)
        body=copy.deepcopy(drafted['report']);body['source_ledger']['D1259375']['citation']['url']='javascript:alert(1)'
        body['report_sha256']=digest({k:v for k,v in body.items() if k!='report_sha256'})
        (unsafe/'report.json').write_text(json.dumps(body))
        for name in ['preview.json','readiness-plan.json']:
            value=json.loads((unsafe/name).read_text());value['report_sha256']=body['report_sha256'];(unsafe/name).write_text(json.dumps(value))
        render_workspace(unsafe,output/'safe-link-view',font)
        html=(output/'safe-link-view/workspace.html').read_text()
        assert 'href="javascript:' not in html and 'javascript:alert(1)' in html
        checks.append('UI_C06_UNSAFE_CITATION_SCHEME_IS_TEXT_NOT_LINK')
        with patch.object(Path,'read_bytes',side_effect=AssertionError('Unapproved source read')):
            rejected(lambda:app.call('evidence_inspect',{'source_id':'alias_final_reserved'}))
        checks.append('UI_C07_UNKNOWN_SOURCE_REJECTED_BEFORE_PAYLOAD_ACCESS')
        js=(root/'src/curaloop_rd/resources/workspace_v2.js').read_text()
        assert 'textContent' in js and 'innerHTML' not in js and 'fetch(' not in js
        assert 'prefers-reduced-motion' in (root/'src/curaloop_rd/resources/workspace_v2.css').read_text()
        checks.append('UI_C08_LOCAL_SELECTION_REDUCED_MOTION_AND_NO_LIVE_FETCH')
        messages=[{'jsonrpc':'2.0','id':0,'method':'tools/list'},
          {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'studio-engineering-client','version':'1'}}},
          {'jsonrpc':'2.0','method':'notifications/initialized'},
          {'jsonrpc':'2.0','id':2,'method':'tools/list'},
          {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'evidence_search','arguments':{'query':'1259375'}}},
          {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'evidence_inspect','arguments':{'source_id':'D1259375'}}},
          {'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'draft_metadata_plan','arguments':brief}},
          {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'local_export','arguments':params}},
          {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'local_export','arguments':params}},
          {'jsonrpc':'2.0','id':8,'method':'tools/call','params':{'name':'evidence_inspect','arguments':{'source_id':'alias_final_reserved'}}}]
        raw=''.join(json.dumps(m)+'\n' for m in messages)+'{invalid\n'+json.dumps({'jsonrpc':'2.0','id':9,'method':'ping'})+'\n'
        env=os.environ.copy();env['PYTHONPATH']=str(root/'src')
        result=subprocess.run([sys.executable,'-B','-m','curaloop_rd.mcp_v2','--source-root',str(root),'--registry',str(root/'inputs/workflow-registry.json'),'--workspace',str(output/'stdio-workspace'),'--font',str(font)],input=raw,text=True,capture_output=True,timeout=30,env=env)
        (output/'stdio-input-private.jsonl').write_text(raw)
        (output/'stdio-output-private.jsonl').write_text(result.stdout)
        (output/'stdio-error-private.txt').write_text(result.stderr)
        assert result.returncode==0
        responses=[json.loads(line) for line in result.stdout.splitlines()]
        assert len(responses)==11
        byid={r['id']:r for r in responses}
        assert byid[0]['error']['message']=='INITIALIZATION_REQUIRED'
        assert len(byid[2]['result']['tools'])==4
        assert byid[6]['result']==byid[7]['result']
        assert byid[6]['result']['structuredContent']['workspace_v2']['manifest']['report_sha256']==drafted['report']['report_sha256']
        assert byid[8]['result']['isError'] is True and byid[None]['error']['message']=='PARSE_ERROR'
        checks.append('UI_C09_ACTUAL_OS_STDIO_ELEVEN_RESPONSES_AND_STABLE_EXPORT')
        changed=view/'workspace.html';changed.write_text(changed.read_text()+'\n<!--altered-->')
        rejected(lambda:app.call('local_export',params))
        checks.append('UI_C10_MODIFIED_VIEW_REJECTED_ON_REEXPORT')
        # A view's editable manifest is not an independent trust anchor.
        # Restore the exact original view before each coordinated-tamper fixture.
        shutil.rmtree(view);render_workspace(folder,view,font)
        original_manifest=(view/'handoff-manifest.json').read_bytes()
        for filename in ['report.json','report.md','preview.json','readiness-plan.json','workspace.html']:
            p=view/filename;original=p.read_bytes();p.write_bytes(original+b'\n ')
            forged=json.loads(original_manifest)
            for row in forged['files']:
                if row['path']==filename:row.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            (view/'handoff-manifest.json').write_text(json.dumps(forged))
            rejected(lambda:app.call('local_export',params))
            p.write_bytes(original);(view/'handoff-manifest.json').write_bytes(original_manifest)
        checks.append('UI_C11_COORDINATED_FILE_AND_MANIFEST_TAMPER_REJECTED')
        (view/'unexpected.txt').write_text('Synthetic extra-file fixture')
        rejected(lambda:app.call('local_export',params));(view/'unexpected.txt').unlink()
        checks.append('UI_C12_UNEXPECTED_VIEW_INVENTORY_REJECTED')
        moved=view.with_name('view-v2-symlink-fixture');view.rename(moved);view.symlink_to(moved,target_is_directory=True)
        rejected(lambda:app.call('local_export',params));view.unlink();moved.rename(view)
        assert app.call('local_export',params)==exported
        checks.append('UI_C13_SYMLINK_VIEW_REJECTED_AND_ORIGINAL_REEXPORT_STABLE')
        return {'status':'PASS','checks':checks,'count':len(checks),'actual_os_stdio_responses':11,
                'real_cached_source_dispositions':sorted(dispositions),'synthetic_ui_safety_fixtures_labelled':True,
                'report_sha256':drafted['report']['report_sha256'],'new_scientific_source_calls':0,
                'molecular_replay':'UNMET','live_agent_evaluation':'NOT_RUN'}
    finally:app.close()

if __name__=='__main__':
    root=Path(sys.argv[1]);out=Path(sys.argv[2]);result=execute(root,out)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
