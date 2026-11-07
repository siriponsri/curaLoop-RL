"""Copy small outcome-free derivations for ongoing review, not full-return proof."""
import argparse,base64,hashlib,json
from r0dqr_core_v1 import PRIVATE,REMOTE,save,now
from r0dqr_rpc_v1 import ssh
from r0dqr_transport_guard_v1 import TransportGuard

SETS={'inventory':['jobs/inventory-v1/taxonomy-inventory.json','jobs/prepare-v1/schema-columns.json'],
      'nominal':['jobs/nominal-v1/frame-frozen.json','jobs/nominal-v1/candidates-frozen.json','jobs/nominal-v1/pooling-diagnostics.json'],
      'context':['jobs/context-v1/development-packet.json','jobs/context-v1/source-intent-frozen.json']}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('set',choices=SETS);args=parser.parse_args()
    guard=TransportGuard('small-return-'+args.set+'-v1',cpu_seconds=30,wall=60,memory_mib=512)
    try:
        code='''import json,base64,hashlib;from pathlib import Path
root=Path(__ROOT__);rows=[]
for rel in __FILES__:
 p=root/rel;assert p.is_file() and not p.is_symlink() and p.stat().st_size<24*1024**2
 raw=p.read_bytes();rows.append({'path':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()})
print(json.dumps({'files':rows}))'''.replace('__ROOT__',repr(REMOTE)).replace('__FILES__',repr(SETS[args.set]))
        result=ssh(code);pins=[]
        for row in result['files']:
            raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
            target=PRIVATE/'small-return'/row['path'];assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);pins.append(row)
        save(PRIVATE/('small-return-'+args.set+'-v1.json'),{'status':'PASS_SMALL_DERIVATION_TRANSPORT_NOT_COMPLETE_RETURN','files':pins,'utc':now()})
        print(json.dumps({'status':'PASS_SMALL_DERIVATION_TRANSPORT_NOT_COMPLETE_RETURN','set':args.set,'files':len(pins)}))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS')
