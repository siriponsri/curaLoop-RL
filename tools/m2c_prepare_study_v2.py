"""Fresh guarded six-pool admission, immutable study matrix, scoped label projection."""
import base64,hashlib,json,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.m2_costed_v2.guard import CostedGuard,new
from research.m2_v1.admission import admit
TASK=ROOT/'.local/m2-costed-20261108-v2';REMOTE='/home/chaw/curaloop-tasks/m2-costed-20261108-v2'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def build_matrix(admission):
    caps=json.loads((TASK/'technical-admission-result.json').read_text())['caps'];entries=[]
    pools=admission['pools'];configurations={'Gk':[2,4,8],'T':[[2,.02],[4,.05],[8,.10]]}
    def add(handler,key,args,cpu=None):
        index=len(entries);cpu=69+int.from_bytes(hashlib.sha256(key.encode()).digest()[:2],'big')%3 if cpu is None else cpu
        name=f'{handler}-{index:04d}';entries.append({'job':name,'handler':handler,'cpu':cpu,'arguments':args});return name,cpu
    for predictor in('rf','neighbor'):
        for task in sorted(pools):
            for n0 in(0,16):
                for policy,seed in [('G1',101),('MIX',211)]:
                    costs=caps[f'{predictor}:{n0}:32']['operation_cost_priors']
                    args={'task_id':task,'predictor':predictor,'n0':n0,'budget':32,'seed':seed,'policy':policy,'cap':15.,
                      'cost_priors':costs,'training':True,'save_snapshots':True}
                    prefix,cpu=add('prefix',f'prefix:{predictor}:{task}:{n0}:{policy}',args)
                    for snapshot in(0,8,16,24):
                        for regime in('cheap','high'):
                            for operation in('REUSE','UPDATE','PLAN'):
                                value=dict(args,save_snapshots=False,policy='G1',prefix_job=prefix,snapshot=snapshot,
                                  regime=regime,cap=caps[f'{predictor}:{n0}:32'][regime],forced=operation)
                                add('branch',prefix,value,cpu)
    # All matrix ordering and CPU pairing are fixed without opening labels.
    for handler,seeds,bs,arms in [('tuning',[301,401],[32],['Gk','T']),
         ('main',[1009,2027,3041,4051,5059],[32],['R','G1','Gk','U','P','T','E','L']),
         ('ablation',[1009,2027,3041,4051,5059],[32],['no_history','no_UPDATE','no_PLAN']),
         ('transfer',[1009,2027,3041],[16],['G1','T','E','L'])]:
        for predictor in (('rf','neighbor') if handler in('tuning','main') else ('rf',)):
            for task in sorted(pools):
                for n0 in(0,16):
                    for b in bs:
                        for regime in (('cheap',) if handler=='ablation' else ('cheap','high')):
                            for seed in seeds:
                                # Reuse exact CPU of main context for paired RF ablations.
                                key=f'eval:{predictor}:{task}:{n0}:{b}:{regime}:{seed}'
                                for arm in arms:
                                    for configuration in (range(3) if handler=='tuning' else [None]):
                                        c=caps[f'{predictor}:{n0}:{b}']
                                        value={'task_id':task,'predictor':predictor,'n0':n0,'budget':b,'seed':seed,
                                          'policy':'L' if handler=='ablation' else arm,'regime':regime,'cap':c[regime],
                                          'cost_priors':c['operation_cost_priors'],'training':handler=='tuning'}
                                        if configuration is not None:value.update(configuration=configuration,parameter=configurations[arm][configuration])
                                        if handler=='ablation':value['variant']=arm
                                        add(handler,key,value)
    for entry in entries:
        task=entry['arguments']['task_id'];entry['arguments']['input_path']='inputs/development/'+task+'.json'
    counts={h:sum(e['handler']==h for e in entries) for h in ('prefix','branch','tuning','main','ablation','transfer')}
    assert counts=={'prefix':48,'branch':1152,'tuning':576,'main':1920,'ablation':180,'transfer':288}
    entries.sort(key=lambda e:(['prefix','branch','tuning','main','ablation','transfer'].index(e['handler']),hashlib.sha256(('order:'+e['job']).encode()).digest()))
    return {'schema':'curaloop.m2_costed.matrix.v2','entries':entries,'counts':counts,
       'components':sorted({p['group'] for p in pools.values()}),'labels_opened_during_matrix_definition':False,
       'paired_context_same_initial_cpu':True,'policy_order':'SHA256(order:job) within stage',
       'seed_recipe':'int.from_bytes(SHA256(m2:task:seed)[:4],big) modulo 2147483647'}


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());job=TASK/'jobs'/permit['attempt'];guard=CostedGuard(job/'resource.json',permit)
    try:
        assert permit['handler']=='prepare_development' and permit['host']=='local'
        assert json.loads((TASK/'ledger.json').read_text())['technical_admission']=='PASS'
        checks=json.loads((TASK/'jobs/engine-checks-02/result.json').read_text());assert checks['status']=='PASS_CONSTRUCTED_ENGINE_CHECKS'
        result=admit(TASK);assert result['status']=='PASS_OUTCOME_BLIND_ADMISSION'
        admission=json.loads((TASK/'admission/features-and-mask-private.json').read_text())
        matrix=build_matrix(admission);new(TASK/'matrix-definition-v1.json',matrix)
        code=json.loads((TASK/'code-stage-02.json').read_text())
        new(TASK/'implementation-freeze-v1.json',{'status':'FROZEN_BEFORE_FIRST_DEVELOPMENT_LABEL_DECODE',
          'code_directory':code['code_directory'],'code_pins':code['code_pins'],'matrix_sha256':sha(TASK/'matrix-definition-v1.json'),
          'source_predictor_unchanged':True,'synthetic_checks_sha256':sha(TASK/'jobs/engine-checks-02/result.json'),
          'cpu_reserve':'min(0.05,max(0.002,0.01*C)); no cap rounding; scientific prep and inference charged',
          'gate_weighting':'equal annotation-component totals, weights normalized to mean one; training-only standardization',
          'final_outcomes_opened':False,'development_labels_decoded':False})
        # Decode only the freshly authenticated six allowed files, after all gates.
        files=[]
        for tid,pool in admission['pools'].items():
            source=ROOT/pool['source_input'];assert sha(source)==pool['input_sha256'] and not source.is_symlink()
            data=json.loads(source.read_text());assert data['task_id']==tid and data['role']=='development' and data['family_id']==pool['group']
            features={r['candidate_id']:r for r in pool['records']};assert set(features)=={r['candidate_id'] for r in data['records']}
            for record in data['records']:
                assert type(record['active'])is bool and record['morgan_on_bits']==features[record['candidate_id']]['morgan_on_bits']
            data.update(component=pool['group'],training_candidate_ids=pool['training_candidate_ids'])
            path=TASK/'inputs/development'/f'{tid}.json';new(path,data)
            files.append({'path':str(path.relative_to(TASK)).replace('\\','/'),'sha256':sha(path),'bytes':path.stat().st_size,
                           'source_sha256':pool['input_sha256'],'task_id':tid,'component':pool['group'],'rows':len(data['records'])})
        for e in matrix['entries']:e['arguments']['input_sha256']=next(f['sha256'] for f in files if f['task_id']==e['arguments']['task_id'])
        new(TASK/'execution-matrix-v1.json',matrix);new(TASK/'development-projection-manifest.json',{'files':files,'final_outcomes_opened':False})
        ledger=json.loads((TASK/'ledger.json').read_text());assert ledger['development_labels_decoded']is False
        ledger['development_labels_decoded']=True;ledger['development_projection_sha256']=sha(TASK/'development-projection-manifest.json')
        tmp=TASK/'ledger.next.json';tmp.write_text(json.dumps(ledger,indent=2)+'\n');os.replace(tmp,TASK/'ledger.json')
        new(job/'result.json',{'status':'PASS_AUTHENTICATED_DEVELOPMENT_PREPARATION','assays':6,'rows':sum(f['rows'] for f in files),'counts':matrix['counts'],'final_outcomes_opened':False})
        guard.finish('PASS');print(json.dumps({'status':'PASS_AUTHENTICATED_DEVELOPMENT_PREPARATION','counts':matrix['counts']}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:300]});guard.finish('FAIL');raise


if __name__=='__main__':main()
