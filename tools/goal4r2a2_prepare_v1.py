"""Prepare the fixed A2 metadata request plan and unchanged skill client."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = Path('C:/Users/User/.codex/plugins/cache/openai-curated-remote/life-science-research/1.0.3/skills/pubchem-pug-skill/scripts/rest_request.py')


def main():
    local = ROOT / '.local/goal4r2a2-20261106-v1'
    private = local / 'private-tools'
    private.mkdir(parents=True, exist_ok=True)
    data = CLIENT.read_bytes()
    with (private / 'pubchem_rest_request.py').open('xb') as handle:
        handle.write(data)
    si = json.loads((ROOT / 'docs/evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json').read_text())
    ids = sorted({row['aid'] for row in si['versions']}, key=int)
    assert len(ids) == 105
    plan = {'status': 'FROZEN_METADATA_REQUEST_PLAN', 'base_url': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug',
            'allowed_aids': ids, 'probe_aid': '873', 'operation': 'description/JSON',
            'response_format': 'text', 'raw_semantics': 'HTTP-decoded text saved as UTF-8, not wire-byte capture',
            'maximum_current_description_requests': 105, 'maximum_selector_control_requests': 2,
            'maximum_response_bytes': 2 * 1024**2, 'per_request_timeout_seconds': 10,
            'minimum_interval_seconds': 1.1, 'stop_roster_on_denial_or_rate_limit': True,
            'skill_client_sha256': hashlib.sha256(data).hexdigest(),
            'skill_client_bytes': len(data), 'skill_client_copied_unchanged': True,
            'full_record_or_activity_fallback': False, 'scientific_campaigns': 0}
    target = ROOT / 'research/configs/goal4r2a2_requests_v1.json'
    with target.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(plan, handle, indent=2)
        handle.write('\n')
    print(json.dumps({k: v for k, v in plan.items() if k != 'allowed_aids'}, indent=2))


if __name__ == '__main__':
    main()
