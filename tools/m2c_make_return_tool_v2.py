"""Derive the reviewed full-return workflow for this owned task; preserve old tool."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'tools/m2p_return_v1.py').read_text()
source=source.replace('m2-cpu-profile-20261108-v1','m2-costed-20261108-v2').replace('curaloop.m2_profile.','curaloop.m2_costed.')
source=source.replace('curaloop-m2p-20261108-v1-','curaloop-m2c-20261108-v1-').replace('curaloop-m2p-return','curaloop-m2c-return').replace('curaloop-m2p-exact','curaloop-m2c-exact')
source=source.replace('2026-11-08T17:05:46+00:00','2026-11-12T08:17:29+00:00')
source=source.replace('len(rows)<10000','len(rows)<100000').replace("sum(r['bytes'] for r in rows)<1024**3","sum(r['bytes'] for r in rows)<4*1024**3")
source=source.replace('512*1024**2','1024**3').replace('4*1024**2','16*1024**2')
source=source.replace('from research.m2_profile_v1.guard import ProfileGuard','from research.m2_costed_v2.guard import CostedGuard').replace('guard = ProfileGuard(','guard = CostedGuard(')
target=ROOT/'tools/m2c_return_v2.py'
with target.open('x',encoding='utf-8',newline='\n') as f:f.write(source)
compile(source,str(target),'exec')
print('Created current-task complete-return tool; previous tool unchanged.')
