"""Closed observation-canary status transfer, including failed source attempts."""
from tools.goal4r2a3_collect_v1 import PHASES, main

PHASES['canary'] = {
    'canary-results-v1.json': 'results.json',
    'canary-resources-v1.json': 'resources.json',
    'observation-checks-v1.json': 'observation-checks.json',
}

if __name__ == '__main__':
    main()
