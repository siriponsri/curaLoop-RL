"""Bounded readback of explicitly named owned task files."""
import json,sys
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.lrbc_ui_control_v1 import ssh,REMOTE
names=sys.argv[1:]
assert names and all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n for n in names)
result=ssh('''
import json
from pathlib import Path
root=Path(__ROOT__)
print(json.dumps({name:(root/name).read_text()[-10000:] if (root/name).is_file() else 'ABSENT' for name in __NAMES__}))
'''.replace('__ROOT__',repr(REMOTE)).replace('__NAMES__',repr(names)))
for name,value in result.items():print(name+'\n'+value)
