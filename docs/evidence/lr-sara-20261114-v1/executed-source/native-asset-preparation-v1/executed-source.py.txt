"""Select only authorized cohort members and preserve unchanged evaluator bytes."""
import ast,fnmatch,json,stat,subprocess,tarfile,zipfile
from pathlib import PurePosixPath
import pyarrow.parquet as pq
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,authority,digest,write_new

def patterns(tree):
    bindings={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name):bindings[target.id]=node.value
    def symbolic(node,seen=frozenset()):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):return node.value
        if isinstance(node,ast.Name) and node.id in bindings and node.id not in seen:return symbolic(bindings[node.id],seen|{node.id})
        if isinstance(node,ast.JoinedStr):return ''.join(symbolic(x,seen) if not isinstance(x,ast.FormattedValue) else symbolic(x.value,seen) for x in node.values)
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Div)):
            return symbolic(node.left,seen)+('/' if isinstance(node.op,ast.Div) else '')+symbolic(node.right,seen)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='format':return symbolic(node.func.value,seen)
        if isinstance(node,ast.Call) and ast.unparse(node.func) in ('os.path.join','Path','pathlib.Path'):
            return '/'.join(symbolic(x,seen) for x in node.args)
        return '*'
    result=set()
    for node in ast.walk(tree):
        value=symbolic(node) if isinstance(node,(ast.Constant,ast.JoinedStr,ast.BinOp,ast.Call)) else None
        if value:
            value=value.removeprefix('./')
            if value.startswith('benchmark/eval_programs/gold_results/') and not value.endswith('/'):
                import re
                result.add(re.sub(r'\{[^}]*\}','*',value))
    return sorted(result)

def main():
    r,l=authority('technical')
    folder=ACCOUNT/'native-assets-v1';folder.mkdir(exist_ok=False);tree_root=folder/'tree';tree_root.mkdir()
    roles=json.loads((ROOT/r['role_freeze_source']).read_text())['roles'];ids={x['instance_id']:x for x in roles}
    annotation=ROOT/'.local/lr-dc2-20261111-v1/dataset-intake-v1/verified.parquet'
    assert digest(annotation)=='c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147'
    columns=['instance_id','domain','github_name','task_inst','domain_knowledge','dataset_folder_tree','gold_program_name','eval_script_name','output_fname','src_file_or_path']
    rows=[x for x in pq.read_table(annotation,columns=columns).to_pylist() if x['instance_id'] in ids]
    assert len(rows)==30
    archive=ROOT/'research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip'
    assert digest(archive)=='46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610'
    selected=set();cases=[]
    with zipfile.ZipFile(archive) as z:
        index={x.filename:x for x in z.infolist()}
        for row in rows:
            i=row['instance_id'];prefix='benchmark/datasets/'+row['dataset_folder_tree'].splitlines()[0].removeprefix('|-- ').strip().rstrip('/')+'/'
            inputs=[n for n in index if n.startswith(prefix) and not index[n].is_dir()]
            ref='benchmark/gold_programs/'+row['gold_program_name'];ev='benchmark/eval_programs/'+row['eval_script_name']
            eval_tree=ast.parse(z.read(ev,pwd=b'scienceagentbench').decode('utf-8-sig'))
            pats=patterns(eval_tree);gold=sorted({n for n in index for pat in pats if fnmatch.fnmatchcase(n,pat) and not index[n].is_dir()})
            # Reject a generic directory-wide target request instead of opening
            # unrelated hidden benchmark results under a broad wildcard.
            assert all(pat!='benchmark/eval_programs/gold_results/*' for pat in pats)
            assert len(gold)<=24
            members=inputs+[ref,ev]+gold
            for name in members:
                item=index[name];path=PurePosixPath(name)
                assert not path.is_absolute() and '..' not in path.parts and not stat.S_ISLNK(item.external_attr>>16)
                assert all(':' not in v and '\\' not in v for v in path.parts) and item.file_size<=1024**3
            selected.update(members)
            cases.append(dict(**ids[i],dataset_prefix=prefix,input_members=inputs,gold_program_name=row['gold_program_name'],
                              eval_script_name=row['eval_script_name'],output_fname=row['output_fname'],evaluator_gold_members=gold,
                              private_target_path_patterns=pats,public_task_metadata=row))
        expected_bytes=sum(index[n].file_size for n in selected);assert expected_bytes<=8*1024**3
        selection=folder/'member-selection.txt';selection.write_text('\n'.join(sorted(selected))+'\n',encoding='utf-8',newline='\n')
        command=['tar','-x','--passphrase','scienceagentbench','-f',str(archive),'-C',str(tree_root),'-T',str(selection)]
        p=subprocess.run(command,capture_output=True,text=True,timeout=1800)
        write_new(folder/'extraction-receipt.json',dict(exit_code=p.returncode,stderr=p.stderr,command_kind='Local libarchive selective extraction; no reference/scorer execution'))
        assert p.returncode==0,p.stderr[-1000:]
        manifest={}
        for name in sorted(selected):
            path=tree_root.joinpath(*PurePosixPath(name).parts)
            assert path.is_file() and path.stat().st_size==index[name].file_size
            manifest[name]=dict(bytes=path.stat().st_size,sha256=digest(path))
    write_new(folder/'private-member-manifest.json',manifest);write_new(folder/'private-cases.json',cases)
    bundle=folder/'native-assets.tar.gz'
    with tarfile.open(bundle,'w:gz',compresslevel=1) as tar:
        for name in sorted(manifest):tar.add(tree_root.joinpath(*PurePosixPath(name).parts),arcname=name,recursive=False)
    receipt=dict(status='PASS_COHORT_ONLY_INPUT_REFERENCE_EVALUATOR_ASSETS',cases=len(cases),files=len(manifest),
        expanded_bytes=expected_bytes,bundle_bytes=bundle.stat().st_size,bundle_sha256=digest(bundle),
        private_manifest_sha256=digest(folder/'private-member-manifest.json'),
        reference_programs_executed=0,native_scorer_calls=0,gold_bodies_or_targets_displayed=False,
        protected_old_outcomes_accessed=False)
    write_new(PUBLIC/'native-asset-preparation-v1.json',receipt);print(json.dumps(receipt))

if __name__=='__main__':main()
