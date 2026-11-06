"""Closed offline native-submit aggregate transfer; source rows stay private."""
from tools.goal4r2a3_collect_v1 import PHASES, main

PHASES['offline-submit'] = {
    'offline-submit-results-v1.json': 'results.json',
    'offline-submit-resources-v1.json': 'resources.json',
    'offline-submit-checks-v1.json': 'submit-checks.json',
    'offline-submit-aggregate-v1.json': 'observation-aggregate.json',
}

if __name__ == '__main__':
    main()
