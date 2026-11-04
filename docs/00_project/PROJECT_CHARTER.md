# Project charter

## Problem and users

A screening team has a candidate pool, a limited experimental budget and incomplete knowledge of activity. Experiments consume capacity and return at different times. A useful planning tool must make a defensible next-batch choice, keep pending work distinct from measured evidence and expose enough provenance to explain the decision later.

The first research user is the owner, acting as an independent investigator. The proposed product user is an R&D scientist or screening informatician; the proposed buyer is the person who controls a small evaluation budget. These roles are hypotheses until documented customer discovery identifies actual people and workflows.

## Workstreams and shared evidence

The research workstream produces protocols, runs, statistical analysis and a manuscript. The product workstream produces stable data contracts, installation, recoverable campaigns and usable reports. The business workstream tests a workflow problem, procurement fit and willingness to pay. All three use a common provenance contract. A commercial presentation may summarize research evidence but cannot expand its scientific scope.

## What remains public

Public code, documentation, benchmark configurations, rights-compatible data descriptions, nonconfidential run artifacts and the manuscript belong in the repository. Customer libraries, account records, interview details and confidential timestamps belong outside public Git. No such private data is present in this package.

## Resource discipline

Start with fingerprints and classical predictors on CPU. Measure inference/training overhead so any adaptive gain can be assessed against implementation cost. Add GPU-heavy models only if a controlled pilot identifies a scientific reason and resources are authorized. Use single-process deterministic smoke scenarios for scheduler correctness before long runs. Resume runs by immutable IDs and never reinterpret interrupted jobs as successful.

## Responsibility

The owner makes the final research and business decisions and reviews AI-assisted artifacts. AI assistance may help with literature extraction, code and drafting, but responsibility for source verification, dataset permissions, experimental integrity and final claims remains with the human author. Affiliations, ORCID, funding and conflicts must be supplied accurately at submission time, not inferred from employment or conversation history.
