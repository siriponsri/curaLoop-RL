"""Reverify retained offline dependencies and extract the already pinned archive."""
import hashlib,json,os,shutil,sqlite3,sys,tarfile,time
from pathlib import Path,PurePosixPath

p=Path(sys.argv[1]);root=p.parents[1];started=time.monotonic()
def save(name,data):
    target=p/name;tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');tmp.replace(target)
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()
def safe_member(member):
    rel=PurePosixPath(member.name)
    assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in member.name
    assert member.isdir() or member.isfile(),'Special archive entry denied'
    return rel
try:
    assert shutil.disk_usage(root).free>48*1024**3
    manifest=json.loads((p/'vendor-manifest.json').read_text())
    assert digest(root/'vendor-inputs-v1.tar.gz')==manifest['archive_sha256']
    for row in manifest['files']:
        target=root/row['path']
        assert target.is_file() and not target.is_symlink() and target.stat().st_size==row['bytes']
        assert digest(target)==row['sha256']
    extra=root/'additional-exposure-v1.json';pin=json.loads((p/'additional-exposure-pin.json').read_text())
    assert extra.stat().st_size==pin['bytes'] and digest(extra)==pin['sha256']
    assert (root/'inputs/additional-exposure-v1.json').read_bytes()==extra.read_bytes()
    sys.path.insert(0,str(root/'vendor'))
    import importlib
    importlib.invalidate_caches()
    from rdkit import Chem,rdBase
    import numpy
    assert rdBase.rdkitVersion=='2026.09.1'
    assert Chem.MolToSmiles(Chem.MolFromSmiles('C(C)O'),canonical=True,isomericSmiles=True)=='CCO'
    save('progress.json',{'status':'PASS_OFFLINE_ENVIRONMENT','rdkit':rdBase.rdkitVersion,'numpy':numpy.__version__})
    source=root/'source/chembl_37_sqlite.tar.gz'
    proof=json.loads((root/'jobs/download-archive-v1/result.json').read_text())
    assert proof['status']=='PASS_ARCHIVE_DIGEST'
    # Receipt and pinned digest already establish the compressed source. Rehash
    # here binds extraction to those identical bytes, without reading any values.
    assert digest(source)=='33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281'
    entries=[];database=None;other=0
    with tarfile.open(source,'r|gz') as tar:
        for member in tar:
            rel=safe_member(member);entries.append({'path':member.name,'bytes':member.size,'kind':'directory' if member.isdir() else 'regular'})
            assert len(entries)<=100
            if member.isdir():continue
            if rel.suffix in {'.db','.sqlite','.sqlite3'}:
                assert database is None and 0<member.size<=32*1024**3
                target=root/'source/chembl_37.db.part';assert not target.exists();h=hashlib.sha256();written=0
                with tar.extractfile(member) as src,target.open('xb') as dst:
                    for chunk in iter(lambda:src.read(1024**2),b''):
                        dst.write(chunk);h.update(chunk);written+=len(chunk)
                        if written%(256*1024**2)==0:
                            assert shutil.disk_usage(root).free>16*1024**3
                            save('progress.json',{'status':'UNPACKING_PRIVATE_SQLITE','bytes':written,'expected_bytes':member.size,'outcomes_emitted':False})
                    dst.flush();os.fsync(dst.fileno())
                assert written==member.size
                with target.open('rb') as f:assert f.read(16)==b'SQLite format 3\x00'
                target.replace(root/'source/chembl_37.db');database={'member':member.name,'bytes':written,'sha256':h.hexdigest()}
            else:
                other+=member.size;assert other<=16*1024**2
                target=root/'source/archive-metadata'/Path(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,1024**2)
    assert database
    conn=sqlite3.connect('file:'+str(root/'source/chembl_37.db')+'?mode=ro&immutable=1',uri=True)
    from r0dq_projection_v1 import protect_metadata_connection
    protect_metadata_connection(conn)
    tables={row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required={'activities','assays','target_dictionary','target_components','component_sequences','docs','compound_structures','molecule_dictionary'}
    assert required<=tables
    schema={name:[{'column':r[1],'type':r[2]} for r in conn.execute('PRAGMA table_info('+name+')')] for name in sorted(required|({'assay_parameters','variant_sequences'}&tables))}
    save('schema-columns.json',schema)
    save('result.json',{'status':'PASS_VERIFIED_EXTRACTION_AND_SCHEMA','database':database,'archive_entries':entries,
        'rdkit_version':rdBase.rdkitVersion,'numpy_version':numpy.__version__,'sqlite_runtime':sqlite3.sqlite_version,
        'source_value_queries':0,'numeric_outcomes_emitted':False,'wall_seconds':time.monotonic()-started})
except Exception as exc:
    import traceback
    save('result.json',{'status':'FAIL_EXTRACTION_OR_SCHEMA','error_type':type(exc).__name__,
        'error_frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)],
        'numeric_outcomes_emitted':False})
    raise SystemExit(1)
