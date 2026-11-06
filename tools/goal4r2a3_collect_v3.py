"""Read-only closed aggregate transfer for the second metadata reconciliation."""

from tools.goal4r2a3_collect_v1 import PHASES, main

PHASES['reconcile2'] = {
    'reconciliation-results-v2.json': 'results.json',
    'reconciliation-resources-v2.json': 'resources.json',
    'reconciliation-checks-v2.json': 'reconciliation-checks-v2.json',
    'family-overlay-v3.json': 'family-overlay.json',
    'pair-metadata-gates-v3.json': 'pair-metadata-gates.json',
}

if __name__ == '__main__':
    main()
