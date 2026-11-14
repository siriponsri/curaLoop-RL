"""Bounded public source snapshots and shared-input metadata audit."""
import hashlib,json,urllib.request,zipfile,sys
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import PurePosixPath
from tools.sar30_control_v1 import ROOT, ACCOUNT, PUBLIC, authority, digest, write_new

URLS={
 'benchmark-readme':'https://raw.githubusercontent.com/OSU-NLP-Group/ScienceAgentBench/c26e151ed601ba109dc4d35e057ff8e73fec469d/README.md',
 'benchmark-code-license':'https://raw.githubusercontent.com/OSU-NLP-Group/ScienceAgentBench/c26e151ed601ba109dc4d35e057ff8e73fec469d/LICENSE',
 'rasterio-license':'https://raw.githubusercontent.com/rasterio/rasterio/main/LICENSE.txt',
 'admet-ai-1.3.1-metadata':'https://pypi.org/pypi/admet-ai/1.3.1/json'}

def main():
    authority();sources=[]
    for name,url in (URLS.items() if '--complete-retained' not in sys.argv else []):
        try:
            with urllib.request.urlopen(url,timeout=25) as response:
                raw=response.read(262145);assert len(raw)<=262144
                status=response.status
            path=ACCOUNT/'public-source-snapshots'/f'{name}.txt';path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as f:f.write(raw)
            sources.append(dict(name=name,url=url,status=status,bytes=len(raw),sha256=digest(path),retrieved_utc=datetime.now(timezone.utc).isoformat()))
        except Exception as e:sources.append(dict(name=name,url=url,status='UNAVAILABLE',error_type=type(e).__name__))
    readme=(ACCOUNT/'public-source-snapshots/benchmark-readme.txt').read_text()
    assert 'Creative Commons Attribution 4.0' in readme and 'Instance ID: 32, 46, 53, 54, 84' in readme
    license_text=(ACCOUNT/'public-source-snapshots/rasterio-license.txt').read_text()
    assert 'Redistribution and use in source and binary forms' in license_text
    rows=json.loads((PUBLIC/'static-input-and-dependency-audit-v1.json').read_text())['rows']
    meta=ACCOUNT/'public-source-snapshots/admet-ai-1.3.1-metadata.txt'
    chemprop=[x for x in (json.loads(meta.read_text())['info'].get('requires_dist') or []) if x.lower().startswith('chemprop')] if meta.exists() else []
    if '--complete-retained' in sys.argv:
        sources=[dict(name=name,url=url,bytes=(ACCOUNT/'public-source-snapshots'/f'{name}.txt').stat().st_size,
            sha256=digest(ACCOUNT/'public-source-snapshots'/f'{name}.txt'),retrieval='RETAINED_INITIAL_FETCH_NO_SECOND_REQUEST')
            for name,url in URLS.items() if (ACCOUNT/'public-source-snapshots'/f'{name}.txt').exists()]
    rights=[dict(instance_id=r['instance_id'],use_status='ADMITTED_LOCAL_RESEARCH_SOURCE_DECLARATION',
                 benchmark_task_license='Original rasterio BSD-style terms' if r['instance_id']==53 else 'CC-BY-4.0 per benchmark declaration',
                 attribution_repository=r['repository_lineage'],raw_redistribution=False,
                 limitation='Benchmark publisher declaration and retained source notice; not an independent ownership audit or permission for all underlying third-party data redistribution') for r in rows]
    matches=defaultdict(list)
    archive=ROOT/'research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip'
    prefixes={r['dataset_prefix']:r['repository_lineage'] for r in rows}
    shared=[]
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            repo=next((repo for prefix,repo in prefixes.items() if info.filename.startswith(prefix)),None)
            if repo and not info.is_dir() and info.file_size>1024 and PurePosixPath(info.filename).suffix.lower() not in ('.py','.md','.txt'):
                matches[(info.file_size,info.CRC)].append((info.filename,repo))
        for key,items in matches.items():
            if len({repo for _,repo in items})>1:
                hashes=defaultdict(list)
                for name,repo in items:
                    h=hashlib.sha256(z.read(name,pwd=b'scienceagentbench')).hexdigest();hashes[h].append((name,repo))
                for h,items2 in hashes.items():
                    if len({repo for _,repo in items2})>1:shared.append(dict(sha256=h,members=[dict(path=n,repository_lineage=r) for n,r in items2]))
    report=dict(status='PASS_DECLARED_LOCAL_USE_AND_EXACT_INPUT_AUDIT',sources=sources,rights=rights,
                admet_ai_1_3_1_chemprop_requirements=chemprop,
                old_admet_metadata_dependency_identity='NOT_VERIFIED_NULL_REQUIRES_DIST' if not chemprop else 'DECLARED',
                cross_repository_identical_noncode_input_files=shared,
                all_paper_or_semantic_dataset_links_resolved=False,
                dependence_limitation='Exact-byte overlap audit cannot exclude shared subjects, studies, preprocessing derivatives or cross-paper ancestry; repository lineage is a minimum grouping, not independence certification',
                native_qualification='NOT_RUN')
    write_new(PUBLIC/'rights-and-shared-input-audit-v1.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('rights','sources')}))

if __name__=='__main__':main()
