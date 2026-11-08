"""Fresh LR-M12 permits over the preserved platform resource guard."""

import json
import os
from pathlib import Path

from research.longrun_v1.guard import ResourceGuard


class M12Guard(ResourceGuard):
    def _write(self, status):
        self.base = dict(self.base, schema='curaloop.lr_m12.resources.v1',
                         release_utc='2026-11-08T05:10:46Z',
                         conservative_reservation_seconds=self.permit['reservation_seconds'])
        super()._write(status)

    def kernel_proof(self):
        if os.name == 'nt':
            return {'mechanism': self.child_policy, 'affinity': self._windows_affinity(),
                    'memory_bytes': self.ram_limit, 'process_cpu_seconds': self.cpu_limit}
        line = next(s for s in Path('/proc/self/cgroup').read_text().splitlines()
                    if s.startswith('0::'))
        cgroup = Path('/sys/fs/cgroup' + line.split('::', 1)[1])
        quota, period = (cgroup / 'cpu.max').read_text().split()
        memory = (cgroup / 'memory.max').read_text().strip()
        swap = (cgroup / 'memory.swap.max').read_text().strip()
        if (quota == 'max' or int(quota) / int(period) > 1 or memory == 'max'
                or int(memory) > self.ram_limit or swap != '0'):
            raise RuntimeError('LR_M12_KERNEL_LIMIT_PROOF_FAILED')
        return {'mechanism': 'CGROUP_V2_AGGREGATE_CPU_MEMORY_SWAP',
                'cgroup': str(cgroup), 'cpu_max': [int(quota), int(period)],
                'memory_max': int(memory), 'memory_swap_max': 0,
                'starting_affinity': sorted(os.sched_getaffinity(0))}


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())
