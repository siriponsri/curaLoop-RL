"""Authenticated data-free runtime/code projection for technical admission."""
import hashlib,io,json,sys,tarfile
from pathlib import Path
from research.m2_costed_v2.guard import CostedGuard,new
ROOT=Path(__file__).resolve().parents[2];TASK=ROOT/'.local/m2-costed-20261108-v2'


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def build():
    previous=ROOT/'.local/m2-cpu-profile-20261108-v1/remote-return'
    verified=json.loads((previous/'verified-v1.json').read_text());manifest=previous/'export/manifest.json'
    assert sha(manifest)==verified['manifest_sha256'];files=[]
    for row in json.loads(manifest.read_text())['files']:
        if row['path'].startswith('vendor/'):
            p=previous/'files'/row['path'];assert p.is_file() and not p.is_symlink() and sha(p)==row['sha256']
            files.append((p,row['path'],row['sha256']))
    names=['research/__init__.py','research/longrun_v1/__init__.py','research/longrun_v1/guard.py',
           'research/m2_v1/__init__.py','research/m2_v1/models.py',
           'research/m2_profile_v1/__init__.py','research/m2_profile_v1/guard.py','research/m2_profile_v1/worker.py']
    names += [p.relative_to(ROOT).as_posix() for p in (ROOT/'research/m2_costed_v2').glob('*.py')]
    pins={n:sha(ROOT/n) for n in names}
    assert pins['research/m2_v1/models.py']=='7a7403e5906dc0b74883f9d2eb35b50a438f13273d82cd2c9ddb25430ba722dc'
    files += [(ROOT/n,'code/'+n,pins[n]) for n in names]
    projected={'schema':'curaloop.m2_costed.transport.v2','biological_inputs_included':False,
               'files':[{'path':n,'bytes':p.stat().st_size,'sha256':s} for p,n,s in files]}
    archive=TASK/'transport-technical-v1.tar.gz'
    with tarfile.open(archive,'x:gz',compresslevel=1) as tf:
        for p,n,_ in files:tf.add(p,arcname=n,recursive=False)
        data=(json.dumps(projected,indent=2)+'\n').encode();info=tarfile.TarInfo('transport-manifest.json');info.size=len(data)
        tf.addfile(info,io.BytesIO(data))
    new(TASK/'transport-manifest.json',projected)
    result={'status':'PASS_DATA_FREE_TECHNICAL_BUNDLE','archive_bytes':archive.stat().st_size,
            'archive_sha256':sha(archive),'code_pins':pins,'biological_inputs_included':False}
    new(TASK/'bundle-result.json',result);return result


def main():
    permit=json.loads(Path(sys.argv[1]).read_text());job=TASK/'jobs'/permit['attempt'];guard=CostedGuard(job/'resource.json',permit)
    try:
        result=build();new(job/'result.json',result);guard.finish('PASS');print(json.dumps({k:v for k,v in result.items() if k!='code_pins'}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]});guard.finish('FAIL');raise


if __name__=='__main__':main()
