"""Authenticated offline dependencies and data-free, frozen profile code only."""
import io
import json
import sys
import tarfile
from pathlib import Path
from research.m2_profile_v1.guard import ProfileGuard,new

ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT/'.local/m2-cpu-profile-20261108-v1'


def sha(path):
    import hashlib
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def build():
    old=ROOT/'.local/m2-selective-compute-20261108-v1/remote-return'
    verified=json.loads((old/'verified-v1.json').read_text())
    manifest=old/'export/manifest.json'
    assert sha(manifest)==verified['manifest_sha256']
    source=json.loads(manifest.read_text())['files'];files=[]
    for row in source:
        if not row['path'].startswith('vendor/'):continue
        if '/tests/' in row['path'] or row['path'].startswith('vendor/sklearn/datasets/'):continue
        path=old/'files'/row['path']
        assert path.is_file() and not path.is_symlink() and sha(path)==row['sha256']
        files.append((path,row['path'],row['sha256']))
    paths=['research/__init__.py','research/longrun_v1/__init__.py','research/longrun_v1/guard.py',
           'research/m2_v1/__init__.py','research/m2_v1/models.py']
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'research/m2_profile_v1').glob('*.py')]
    assert sha(ROOT/'research/m2_v1/models.py')=='7a7403e5906dc0b74883f9d2eb35b50a438f13273d82cd2c9ddb25430ba722dc'
    pins={p:sha(ROOT/p) for p in paths}
    files += [(ROOT/p,'code/'+p,pins[p]) for p in paths]
    manifest={'schema':'curaloop.m2_profile.transport.v1','biological_inputs_included':False,
              'files':[{'path':name,'bytes':p.stat().st_size,'sha256':pin} for p,name,pin in files]}
    archive=TASK/'transport-profile-v1.tar.gz'
    with tarfile.open(archive,'x:gz',compresslevel=1) as tf:
        for path,name,_ in files:tf.add(path,arcname=name,recursive=False)
        data=(json.dumps(manifest,indent=2)+'\n').encode();info=tarfile.TarInfo('transport-manifest.json')
        info.size=len(data);info.mode=0o600;tf.addfile(info,io.BytesIO(data))
    new(TASK/'transport-manifest.json',manifest)
    result={'status':'PASS_SYNTHETIC_ONLY_PROFILE_BUNDLE','file_count':len(files),
            'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'code_pins':pins,
            'biological_inputs_included':False,'frozen_original_predictor_planner':True}
    new(TASK/'bundle-result.json',result);return result


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());job=TASK/'jobs'/permit['attempt']
    assert permit['schema']=='curaloop.m2_profile.permit.v1' and permit['host']=='local'
    guard=ProfileGuard(job/'resource.json',permit)
    try:
        result=build();new(job/'result.json',result);guard.finish('PASS')
        print(json.dumps({k:v for k,v in result.items() if k!='code_pins'}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]});guard.finish('FAIL');raise


if __name__=='__main__':main()
