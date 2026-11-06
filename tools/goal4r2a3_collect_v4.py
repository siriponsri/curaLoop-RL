"""Closed identifier-stage aggregate transfer; raw identifiers remain private."""
from tools.goal4r2a3_collect_v1 import PHASES, main

PHASES['identifiers'] = {
    'identifier-results-v1.json': 'results.json',
    'identifier-resources-v1.json': 'resources.json',
    'identifier-checks-v1.json': 'identifier-checks.json',
    'identifier-attrition-v1.json': 'attrition.json',
}

if __name__ == '__main__':
    main()
