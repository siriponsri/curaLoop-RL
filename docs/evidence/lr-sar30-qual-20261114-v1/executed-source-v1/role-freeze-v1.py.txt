"""Freeze metadata roles before inspecting new reference syntax or outcomes."""
from collections import Counter
import hashlib
import json
from tools.sar30_control_v1 import ROOT, PUBLIC, RELEASE, authority, digest, write_new

def main():
    authority()
    census=ROOT/'docs/evidence/lr-sar1-20261114-v1/static-census-v1.json'
    rows=[r for r in json.loads(census.read_text())['catalog'] if not r['exclusion_reasons']]
    assert len(rows)==30
    counts=Counter(r['repository_lineage'] for r in rows)
    domains={r['repository_lineage']:r['domain'] for r in rows}
    salt='SAR30-development-v1'
    ranked=sorted([dict(repository_lineage=k,domain=domains[k],task_count=v,
                        sha256=hashlib.sha256((salt+'\n'+k).encode()).hexdigest())
                   for k,v in counts.items() if v<=2 and domains[k]!='Computational Chemistry'], key=lambda x:x['sha256'])
    chosen=[]; used=set()
    for item in ranked:
        if item['domain'] not in used:
            chosen.append(item['repository_lineage']); used.add(item['domain'])
        if len(chosen)==2: break
    assert len(chosen)==2
    roles=[dict(instance_id=r['instance_id'],repository_lineage=r['repository_lineage'],domain=r['domain'],
                role='development' if r['repository_lineage'] in chosen else 'locked_candidate') for r in rows]
    locked=[r for r in roles if r['role']=='locked_candidate']
    freeze=dict(status='FROZEN_BEFORE_NEW_REFERENCE_SYNTAX_AND_OUTCOMES',release_sha256=digest(RELEASE),
                source_census_sha256=digest(census),salt=salt,hash_input='salt + LF + normalized repository lineage',
                ranking=ranked,selected_development_lineages=chosen,old_development_ids_outside_thirty=[2,3],
                roles=roles,locked_candidates=len(locked),locked_lineages=len({r['repository_lineage'] for r in locked}),
                locked_domains=len({r['domain'] for r in locked}),native_execution='NOT_RUN',agent_execution='NOT_RUN',
                check_rule='Only public instructions/knowledge plus legal input probes. Algorithmic/numerical constraint with observable output; file/shape/schema alone do not qualify.',
                native_rule='Original native predicate; repeated scorer invocations allowed only for conformance, not a second reference fit; missing/invalid output must not pass.',
                retry_rule='One reference attempt/task; no scientific rerun; no outcome-driven environment change')
    write_new(PUBLIC/'role-and-check-freeze-v1.json',freeze)
    print(json.dumps({k:freeze[k] for k in ['status','selected_development_lineages','locked_candidates','locked_lineages','locked_domains']}))

if __name__=='__main__':main()
