import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_batch_v2 import admin_call
from research.m2_costed_v2.guard import new
TASK=ROOT/'.local/m2-costed-20261108-v2'
path=TASK/'specs/prepare-development.json'
new(path,{'job':'prepare-development','host':'local','handler':'prepare_development','bucket':'engineering_guards',
 'reservation_seconds':120,'wall_seconds':180,'memory_bytes':536870912,'arguments':{}})
print(json.dumps(admin_call('reserve',path)))
