"""Deterministic support-only selection; no numerical outcomes accepted."""
import hashlib
from itertools import combinations
from collections import defaultdict
from .rules import RULES


def rank(value):return hashlib.sha256((RULES['salt']+'|'+str(value)).encode()).hexdigest()


def known_family_map(registry):
    grouped=defaultdict(set);roles=defaultdict(set)
    for row in registry['assays']:
        grouped[row['uniprot_accession']].add(row['family_id'])
        roles[row['family_id']].add(row['role'])
    return ({k:next(iter(v)) for k,v in grouped.items() if len(v)==1},
            {k:next(iter(v)) for k,v in roles.items() if len(v)==1},
            sorted(k for k,v in grouped.items() if len(v)!=1))


def source_components(assays,forced_development_families):
    families={a['family_id'] for a in assays};parent={f:f for f in families}
    def find(x):
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    docs=defaultdict(set)
    for row in assays:
        doi=str(row.get('doi') or '').strip().lower().removeprefix('https://doi.org/').removeprefix('http://doi.org/')
        docs[('publication',doi or row['doc_id'])].add(row['family_id'])
        group=row.get('assay_group')
        if group not in (None,'',0,'0'):
            docs[('assay_group',str(group))].add(row['family_id'])
    for grouped in docs.values():
        ordered=sorted(grouped)
        for family in ordered[1:]:
            a,b=find(ordered[0]),find(family)
            if a!=b:parent[max(a,b)]=min(a,b)
    members=defaultdict(set)
    for family in families:members[find(family)].add(family)
    mapping={};components=[]
    for values in members.values():
        identity='|'.join(sorted(values));cid='family-source-'+rank(identity)[:20]
        bucket=int(rank('role|'+identity)[:8],16)%10
        forced=bool(values&set(forced_development_families))
        role='development' if forced or bucket<3 else 'validation' if bucket<5 else 'final'
        component={'component_id':cid,'family_ids':sorted(values),'role':role,
                   'forced_development_by_exposure':forced,'biological_certification':'NOT_RUN'}
        components.append(component)
        for family in values:mapping[family]=component
    return mapping,sorted(components,key=lambda c:rank(c['component_id']))


def auxiliary_choice(reference_molecules,auxiliary_sets):
    ref=set(reference_molecules)
    if len(ref)<128:return None
    eligible={key:set(values)&ref for key,values in auxiliary_sets.items() if len(set(values)&ref)>=32}
    ordered=sorted(eligible,key=lambda key:(-len(eligible[key]),rank(key)))[:8]
    for number in range(1,min(3,len(ordered))+1):
        good=[]
        for keys in combinations(ordered,number):
            union=set().union(*(eligible[k] for k in keys))
            if len(union)>=64:good.append((keys,len(union)))
        if good:return min(good,key=lambda item:(-item[1],rank('|'.join(map(str,item[0])))))[0]
    return None


def panel(reference_molecules,fixed_auxiliary_sets):
    ref=set(reference_molecules)
    if len(ref)<128 or not 1<=len(fixed_auxiliary_sets)<=3:return None
    shared={key:set(values)&ref for key,values in fixed_auxiliary_sets.items()}
    if any(len(v)<32 for v in shared.values()):return None
    union=set().union(*shared.values())
    if len(union)<64:return None
    selected=set()
    for key in sorted(shared,key=rank):
        need=max(0,32-len(selected&shared[key]))
        selected.update(sorted(shared[key]-selected,key=rank)[:need])
    selected.update(sorted(union-selected,key=rank)[:max(0,64-len(selected&union))])
    selected.update(sorted(ref-selected,key=rank)[:128-len(selected)])
    assert len(selected)==128 and len(selected&union)>=64
    assert all(len(selected&v)>=32 for v in shared.values())
    return sorted(selected,key=rank)


def molecule_role_owners(assay_molecules,assay_roles,exposed_canonical):
    priority={'development':0,'validation':1,'final':2};owners={}
    for assay,values in assay_molecules.items():
        role=assay_roles[assay]
        for molecule in values:
            if molecule in exposed_canonical and role=='final':continue
            if priority[role]>priority.get(owners.get(molecule),-1):owners[molecule]=role
    return owners
