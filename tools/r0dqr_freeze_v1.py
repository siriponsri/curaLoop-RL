"""Freeze predeclared rules and test privacy boundaries on synthetic records."""
import ast,json,sqlite3,sys
from pathlib import Path
from r0dqr_core_v1 import ROOT,PRIVATE,LocalGuard,save,sha,archive_code
from r0dqr_projection_v1 import protect_metadata_connection
from r0dqr_context_projection_v1 import fixtures,project_methods,project_text
sys.path.insert(0,str(ROOT))
from research.taskfirst_dqr_v1.rules import RULES

if __name__=='__main__':
    guard=LocalGuard('rules-and-privacy-fixtures-v1',cpu_seconds=30,wall=60)
    try:
        db=sqlite3.connect(':memory:')
        db.executescript('CREATE TABLE activities(activity_id,assay_id,molregno,standard_type,standard_units,standard_relation,doc_id,standard_value,pchembl_value,activity_comment);INSERT INTO activities VALUES(1,2,3,"Ki","nM","=",4,12345,99,"hidden");')
        protect_metadata_connection(db)
        assert db.execute('SELECT COUNT(*),standard_type FROM activities').fetchone()==(1,'Ki')
        denied=[]
        for query in ['SELECT standard_value FROM activities','SELECT standard_value IS NOT NULL FROM activities','SELECT pchembl_value FROM activities','SELECT activity_comment FROM activities','UPDATE activities SET activity_id=2','ATTACH DATABASE ":memory:" AS x','CREATE TABLE x(a)','SELECT random()','PRAGMA journal_mode=WAL']:
            try:db.execute(query).fetchall()
            except sqlite3.DatabaseError:denied.append(query)
            else:raise AssertionError('Unsafe query accepted')
        assert 'PresenceValidator' not in (ROOT/'tools/r0dqr_projection_v1.py').read_text()
        context=fixtures()
        xml=b'<article><front><article-meta><article-id pub-id-type="doi">10.test/own</article-id></article-meta></front><back><article-id pub-id-type="doi">10.test/cited</article-id></back></article>'
        assert project_methods(xml)['article_dois']==['10.test/own']
        assert project_text('Ki was undetectable.')['text'] is None
        for file in list((ROOT/'tools').glob('r0dqr*.py'))+list((ROOT/'research/taskfirst_dqr_v1').glob('*.py')):
            ast.parse(file.read_text(encoding='utf-8'));archive_code(file)
        target=PRIVATE/'frame-rules-v1.json';assert not target.exists();save(target,RULES)
        save(PRIVATE/'privacy-fixtures-v1.json',{'status':'PASS_SYNTHETIC_BOUNDARY_FIXTURES','denied_queries':denied,
            'context':context,'own_doi_only':True,'rules_sha256':sha(target),'real_source_values_queried':0,
            'synthetic_fixtures_are_not_source_validation':True})
        print(json.dumps({'status':'PASS_SYNTHETIC_BOUNDARY_FIXTURES','rules_sha256':sha(target)}))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
