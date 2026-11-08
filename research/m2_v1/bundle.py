"""Fresh authenticated offline numerical stack and synthetic-only calibration code."""
import io
import json
import sys
import tarfile
from pathlib import Path

from research.m2_v1.admission import M2Guard, ROOT, new, sha


def build(task):
    source=ROOT/'.local/goal4r1-20261105-v1/remote-return/full-v1'
    manifest=source/'manifest.json'
    assert sha(manifest)=='15ebe921421336e0c1179f851bd929efddc0e5e0d5b69519706d70568b2b0f95'
    records=json.loads(manifest.read_text())['files']
    marker='.venv/lib/python3.12/site-packages/'
    wanted={'numpy','numpy.libs','numpy-2.3.5.dist-info','scipy','scipy.libs','scipy-1.17.0.dist-info',
            'sklearn','scikit_learn.libs','scikit_learn-1.8.0.dist-info','joblib','joblib-1.5.3.dist-info',
            'threadpoolctl.py','threadpoolctl-3.6.0.dist-info'}
    files=[]
    for r in records:
        if not r['path'].startswith(marker): continue
        relative=r['path'][len(marker):]
        if relative.split('/')[0] not in wanted or '__pycache__' in relative or relative.endswith('.pyc'):continue
        path=source/'files'/r['path']
        assert path.is_file() and not path.is_symlink() and path.stat().st_size==r['bytes']
        assert sha(path)==r['sha256'],'OFFLINE_DEPENDENCY_HASH_MISMATCH'
        files.append((path,'vendor/'+relative,r['sha256']))
    assert files and sum(p.stat().st_size for p,_,_ in files)<1024**3
    paths=['research/__init__.py','research/longrun_v1/__init__.py','research/longrun_v1/guard.py']
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'research/m2_v1').glob('*.py')]
    for name in paths:
        path=ROOT/name;files.append((path,'code/'+name,sha(path)))
    manifest={'schema':'curaloop.m2.transport.v1','biological_inputs_included':False,
              'files':[{'path':name,'bytes':p.stat().st_size,'sha256':pin} for p,name,pin in files]}
    archive=task/'transport-synthetic-v1.tar.gz'
    with tarfile.open(archive,'x:gz',compresslevel=1) as tf:
        for path,name,_ in files:tf.add(path,arcname=name,recursive=False)
        data=(json.dumps(manifest,indent=2)+'\n').encode()
        info=tarfile.TarInfo('transport-manifest.json');info.size=len(data);info.mode=0o600
        tf.addfile(info,io.BytesIO(data))
    new(task/'transport-manifest.json',manifest)
    result={'status':'PASS_AUTHENTICATED_SYNTHETIC_ONLY_BUNDLE','files':len(files),
            'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),
            'source_bytes':sum(p.stat().st_size for p,_,_ in files),
            'biological_inputs_included':False,'code_pins':{n:sha(ROOT/n) for n in paths}}
    new(task/'bundle-result.json',result)
    return result


def main():
    permit=json.loads(Path(sys.argv[1]).read_text())
    assert permit['host']=='local' and permit['schema']=='curaloop.m2.permit.v1'
    task=ROOT/'.local/m2-selective-compute-20261108-v1';job=task/'jobs'/permit['attempt']
    guard=M2Guard(job/'resource.json',permit)
    try:
        result=build(task);new(job/'result.json',result);guard.finish('PASS')
        print(json.dumps({k:v for k,v in result.items() if k!='code_pins'}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:240]})
        guard.finish('FAIL');raise


if __name__=='__main__':main()
