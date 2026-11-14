"""AST and archive-member qualification. Never execute or display gold source."""
import ast
import json
import zipfile
from pathlib import PurePosixPath
import pyarrow.parquet as pq
from tools.sar30_control_v1 import ROOT, ACCOUNT, PUBLIC, authority, digest, write_new

# Written from public annotation before reference syntax/outcomes. These are
# proposed checks, not implemented or validated checkers and not native oracles.
CHECKS = {
5:'Random-forest model class and prediction invariance to held-out row reordering; no target-label score.',
12:'Train/test separation and reversal of ranking when affinity direction is reversed on a public synthetic probe.',
13:'No train/test overlap in fitted preprocessing; predictions follow reordered SMILES inputs.',
15:'Training-only fitting and prediction permutation equivariance on legal input probes.',
16:'Independently check PAINS/Brenk rejection and maximum Morgan Tanimoto <0.5 against public actives.',
18:'Verify public DILI label mapping and three training configurations; exclude test rows from fitting/search.',
19:'Verify public DILI label mapping and SVM class/configuration; exclude test rows from fitting/search.',
21:'Check projected distance units for 5.5 km buffer and area-ratio recomputation on small synthetic geometry.',
22:'Recompute quality, target class, Ki/KD and organism filters from supplied public input metadata.',
26:'Exactly first ten trajectory frames; interactions consistent with explicit ligand/protein selections on public probe.',
29:'Event grouping and rate/amplitude calculation on supplied or synthetic ECG/RSP/EDA event signals.',
34:'Recompute time-domain HRV from a known synthetic RR sequence; verify train-free signal processing.',
35:'Respiratory-rate units and time-domain RRV on a known synthetic breathing sequence.',
37:'Baseline/onset percentage identity from a public heart-rate probe; exact baseline/window semantics need public documentation.',
40:'Random-forest class and public configuration memberships; no held-out rows in hyperparameter search.',
41:'KNN class, training-only normalization and public configuration memberships.',
44:'Sleep onset <= wake onset and duration consistency; physiological correctness not certified by this partial invariant.',
45:'Public PSS reverse-scoring and total/subscale arithmetic on synthetic questionnaire answers.',
53:'NOT_AVAILABLE: public prompt lacks the category-to-score mapping required to assert a scientific reclassification oracle.',
58:'Public model/rule aggregation count conservation and tie handling from a synthetic prediction table.',
60:'Recompute declared accuracies/improvements against supplied MFA answers on a public small probe.',
67:'NOT_AVAILABLE: exact pattern-similarity definition is not fixed by the public instruction; schema alone is insufficient.',
71:'Training-only normalization, linearity and test-output permutation equivariance on public synthetic EEG.',
72:'Public EEG2EEG architecture and training-only normalization; no native target correlation exposed.',
85:'Recompute public mean/std/skew/kurtosis/argmax definitions and condition associations on synthetic saliva data.',
87:'Recompute degree-two polynomial least-squares fit by public year on a synthetic temperature series.',
90:'Nonnegative factor values and reconstruction residual against supplied X; no native tolerance copied.',
92:'Recompute all six explicitly specified formulas from input factors; no hidden gold values.',
101:'Declared MODNet layer/activation/150-feature configuration and train-only preprocessing.',
102:'Declared MODNet layer/activation/300-feature configuration and train-only preprocessing.'}

def cname(n):
    if isinstance(n,ast.Name):return n.id
    if isinstance(n,ast.Attribute):return cname(n.value)+'.'+n.attr
    return '<expression>'

def scan(raw):
    tree=ast.parse(raw.decode('utf-8-sig'))
    imports=set(); calls=set(); reads=[]; urls=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):imports.update(x.name.split('.')[0] for x in n.names)
        if isinstance(n,ast.ImportFrom) and n.module:imports.add(n.module.split('.')[0])
        if isinstance(n,ast.Call):
            name=cname(n.func); calls.add(name)
            if any(t in name.lower() for t in ('read_','load','open','unpickle')):
                if n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str):
                    reads.append(n.args[0].value)
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith(('http://','https://')):
            # URL is recorded privately, never its downloaded contents.
            urls.append(n.value)
    return dict(imports=sorted(imports),calls=sorted(calls),literal_read_paths=sorted(set(reads)),url_literals=sorted(set(urls)))

def main():
    authority()
    freeze_path=PUBLIC/'role-and-check-freeze-v1.json'
    freeze=json.loads(freeze_path.read_text()); roles={r['instance_id']:r for r in freeze['roles']}
    write_new(PUBLIC/'public-check-specification-v1.json',dict(status='DECLARED_BEFORE_NEW_NATIVE_OUTCOMES',
        role_freeze_sha256=digest(freeze_path),definitions=CHECKS,implementation='NOT_RUN',
        conformance='NOT_RUN',coverage_is_provisional=True,hidden_targets_used=False))
    annotation=ROOT/'.local/lr-dc2-20261111-v1/dataset-intake-v1/verified.parquet'
    assert digest(annotation)=='c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147'
    cols=['instance_id','domain','github_name','task_inst','domain_knowledge','dataset_folder_tree','gold_program_name','eval_script_name','output_fname','src_file_or_path']
    rows=[r for r in pq.read_table(annotation,columns=cols).to_pylist() if r['instance_id'] in roles]
    assert len(rows)==30
    write_new(ACCOUNT/'public-task-metadata-v1.json',rows)
    archive=ROOT/'research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip'
    assert digest(archive)=='46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610'
    private=[]; public=[]
    with zipfile.ZipFile(archive) as z:
        infos={i.filename:i for i in z.infolist()}
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in infos)
        for r in rows:
            i=r['instance_id']; tree=r['dataset_folder_tree']; folder=tree.splitlines()[0].removeprefix('|-- ').strip().rstrip('/')
            prefix='benchmark/datasets/'+folder+'/'
            members=[n for n in infos if n.startswith(prefix) and not infos[n].is_dir()]
            gold='benchmark/gold_programs/'+r['gold_program_name']; ev='benchmark/eval_programs/'+r['eval_script_name']
            assert gold in infos and ev in infos
            s=scan(z.read(gold,pwd=b'scienceagentbench')); e=scan(z.read(ev,pwd=b'scienceagentbench'))
            literal_missing=[]
            for value in s['literal_read_paths']:
                p=value.removeprefix('./')
                if p.startswith('benchmark/datasets/') and p not in infos:
                    literal_missing.append(p)
            network=[c for c in s['calls'] if any(v in c.lower() for v in ('download','http','urlopen','urlretrieve','from_pretrained','fetch_'))]
            row=dict(**roles[i],dataset_prefix=prefix,input_members=len(members),input_declared_bytes=sum(infos[n].file_size for n in members),
                     reference_sha256=hashlib_sha(z.read(gold,pwd=b'scienceagentbench')),
                     evaluator_sha256=hashlib_sha(z.read(ev,pwd=b'scienceagentbench')),
                     reference_imports=s['imports'],evaluator_imports=e['imports'],
                     reference_network_call_flags=network,reference_literal_missing_archive_paths=literal_missing,
                     reference_url_literal_count=len(s['url_literals']),public_scientific_check_candidate=not CHECKS[i].startswith('NOT_AVAILABLE'),
                     rights_status='PENDING_SOURCE_SPECIFIC_REVIEW',transitive_helper_review='PENDING',
                     native_reference_execution='NOT_RUN',native_scoring='NOT_RUN',reason='STATIC_REVIEW_IN_PROGRESS')
            public.append(row); private.append(dict(instance_id=i,reference_syntax=s,evaluator_syntax=e,
                                                     dataset_members={n:infos[n].file_size for n in members}))
    write_new(ACCOUNT/'reference-syntax-private-v1.json',private)
    write_new(PUBLIC/'static-input-and-dependency-audit-v1.json',dict(status='AST_AND_MEMBER_AUDIT_NOT_NATIVE_QUALIFICATION',
        role_freeze_sha256=digest(freeze_path),all_thirty_retained=True,reference_source_displayed=False,
        reference_programs_executed=False,expected_values_displayed=False,rows=public))
    print(json.dumps(public,indent=2))

def hashlib_sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()

if __name__=='__main__':main()
