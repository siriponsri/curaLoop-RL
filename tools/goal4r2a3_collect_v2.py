"""Versioned metadata-repair aggregate allowlist; unchanged v1 collector."""

from tools.goal4r2a3_collect_v1 import PHASES, main

PHASES['reconcile'] = {
    'reconciliation-results-v1.json': 'results.json',
    'reconciliation-resources-v1.json': 'resources.json',
    'reconciliation-checks-v1.json': 'reconciliation-checks.json',
    'family-overlay-v2.json': 'family-overlay.json',
    'pair-metadata-gates-v2.json': 'pair-metadata-gates.json',
}

if __name__ == '__main__':
    main()
