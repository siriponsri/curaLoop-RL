"""M2 costed permits over the preserved single-process resource enforcement."""
import json
import os
from pathlib import Path
from research.longrun_v1.guard import ResourceGuard


def new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


class CostedGuard(ResourceGuard):
    def _write(self,status):
        self.base=dict(self.base,schema='curaloop.m2_costed.resources.v2',
                       release_utc=self.permit['release_utc'],reservation_seconds=self.permit['reservation_seconds'])
        super()._write(status)

    def kernel_proof(self):
        if os.name=='nt':return {'mechanism':self.child_policy,'affinity':self._windows_affinity(),
                                'memory_bytes':self.ram_limit,'cpu_seconds':self.cpu_limit}
        cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
        value={k:(cg/k).read_text().strip() for k in('cpu.max','memory.max','memory.swap.max')}
        assert value=={'cpu.max':'100000 100000','memory.max':'4294967296','memory.swap.max':'0'}
        return value
