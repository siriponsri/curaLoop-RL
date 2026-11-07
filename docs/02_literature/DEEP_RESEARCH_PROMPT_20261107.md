# Independent Deep Research brief for CuraLoop-RL

Act as a critical computational drug-discovery methods reviewer, scientific
data curator and R&D product researcher. I need one evidence-backed research
direction and dataset/benchmark plan that is scientifically substantial,
practical on CPU and relevant to a future agentic R&D plugin. Challenge our
assumptions rather than confirming the current plan. A defensible NO-GO or
explicitly justified pivot is more useful than an impressive-sounding proposal
without usable data.

Use web Deep Research, primary papers, official dataset repositories/release
records, supplements, documentation and official journal pages. State your
research date. Independently verify every paper title, author, year, DOI,
preprint/journal version and correction; citations in our existing documents
are leads, not guaranteed facts. Label abstract-only, full-methods-inspected,
metadata-only and inaccessible sources separately. Do not invent citations,
dataset access, sample counts, measured overlaps, reviewer availability or results.

## Project and objective

The project is CuraLoop-RL: https://github.com/siriponsri/curaLoop-RL .
It has a retrospective screening application, an EN/TH Molecular Studio UI,
a cached evidence/readiness workspace and local typed/MCP interfaces. The
desired business workflow is to search papers and molecular databases, prepare
a reviewable R&D plan, and return a cited report to team tools. Live autonomous
R&D efficacy, external-team delivery, customer value and scientific novelty
are not established by the existing product prototype.

The proposed research question is: **Under a limited measurement/evidence
budget, when should a system resolve shared assay-context evidence, measure a
supported compound/assay cell, recommend compounds, or abstain? Does this improve
reference-endpoint molecular decisions beyond strong alternatives using the
same predictor and complete available metadata?**

We want a substantive contribution, not novelty from adding an LLM, RL label,
retrieval, a graph, more tasks or an attractive interface. You may recommend
retaining, narrowing or replacing this hypothesis, but distinguish each material
scope change and explain what the owner must decide before execution.

## Local inventory you must account for

The attached `LOCAL_DATA_INVENTORY_20261107.md` is a local audit dated 7 November 2026,
based on repo checkpoint `1c849d38d7c6b07b20c16f38f2ad6f57251558ea`.
It separates current file/size checks, fresh small-file hash matches and historical
archive/processing receipts. Its local paths are not public download URLs.
Private `.local/` and raw datasets are ignored by Git; do not assume you can
access them or infer absence because GitHub lacks them. If the attachment is
unavailable, use the following summary and explicitly identify that limitation.

1. **MoleculeNet HIV:** a verified 1,200-compound local replay subset; its manifest
   records 41,127 source rows. Binary historical assay activity, structures and
   fingerprints exist; cost/time are simulated. This is exposed application/
   development data, not a fresh final or multi-context benchmark.
2. **NCATS Tox21:** three raw training-endpoint exports, AhR/PPAR-gamma/p53,
   and three verified 600-row derivatives. The 1,800 task rows overlap chemically
   and are development-exposed. They are pathway/assay outcomes, not therapeutic
   hits or three independent cross-family evaluation populations.
3. **FS-Mol:** full 4,871,086,080-byte `fsmol.tar` present, previously hash-verified.
   The pinned default manifest has 5,135 tasks versus 5,120 reported in the paper;
   retain that discrepancy. A custom prepared cohort has 24 verified label-free
   feature files: 6 development, 2 validation and 16 reserved-final assays, grouped
   4/2/12 by conservative annotation-connected components. There are 6,630 structure
   rows; final features are not final outcome permission. Old development and
   validation assays were used in earlier experiments; final outcomes remain
   reserved. FS-Mol's assay-relative potency-derived binary labels and ChEMBL 27
   provenance differ from continuous Ki/Kd reference-context tasks. Later
   ChEMBL 37/UniProt/InterPro annotations need version-aware reconciliation.
4. **ChEMBL 37:** the full 5,764,252,857-byte SQLite source archive exists. The
   30,480,314,368-byte DB is preserved inside two complete local return archives;
   these duplicate the same source and are not independent datasets. The most
   recent metadata inventory covered 11,055 SINGLE PROTEIN targets. A fixed
   200-target/1,254-assay frame had 16,862 outcome-free topology rows and 12,873 source
   molecule IDs. It produced one nominal development pair with a 128-member
   reference panel and 115 shared auxiliary compounds. Numerical validity was not
   checked in that round. The pair is FcRn CHEMBL5966/P55899, Kd reference
   CHEMBL956457 and IC50 auxiliary CHEMBL956456, source DOI
   `10.1016/j.bmc.2008.05.004`. Construct/family/reference truth remains unreviewed;
   available metadata already distinguishes SPR / pH 6 and IgG-binding ELISA.
   Prior separate qualification found two Ki development diagnostics in one
   exposed component, not additional independent qualified final tasks.
5. **MF-PCBA / PubChem:** main paper and SI PDFs exist, DOI
   `10.1021/acs.jcim.2c01569`. We have scripts/metadata for 60 definitions/105 AIDs,
   readout/provider/version assessments, sampled structure mappings and small
   canary payloads, not a full qualified paired-stage measurement dataset.
   Forty-seven pairs passing scoped source/readout review are not 47 complete
   datasets. The latest 16-row primary/confirmation canary still had zero complete
   selected primary tuples and four exact confirmation tuples; intake stopped
   at its third request with 504. Unrequested pairs remain unknown. Historical
   revision equivalence, defaults/censoring and commercial row-use rights are
   unresolved. An earlier parser-envelope problem was repaired offline; that
   repair did not establish scientific data suitability.
6. **Supporting assets:** pinned protein/family/protection caches; three owner
   main methods PDFs plus two supplements and an older masked web-methods source;
   literature ledgers; partial ChEMBL context projections; authored workflow cases.
   These are not independent reference gold. MolDesignBench is card/code/metadata
   only, with task/gold intake NOT_RUN and recorded noncommercial/tool-compatibility
   concerns. LAB-Bench, Papyrus, LIT-PCBA, MUV and full PCBA are investigated leads,
   not confirmed qualified local payloads. Verify all of their actual merits.

We are not starting from zero data or zero prior experiments. Older FS-Mol
challenges ran thousands of repeated campaigns on small exposed assay sets.
The prior screening implementation was 32.2% slower in a matched timing check;
a stronger Tanimoto-GP/Greedy predictor explained much of later improvement,
while incremental event-planner value was not established. No learned RL
controller was evaluated in those challenges. Repeated campaigns are not new
biological samples. Do not propose the same old computational-advantage story
without addressing this counterevidence.

## Current design choices are hypotheses, not universal requirements

The current proposal keeps reference Ki/Kd separate, IC50 auxiliary, 128 canonical
reference compounds, 64 shared in the auxiliary union and 32 per auxiliary context.
It targets 36 bundles in 18 isolation units, with 4 development/2 validation/12 final
units. These numbers are project design choices, **not a proven power calculation,
journal mandate or qualified dataset**. Critically assess whether they are
justified. Propose better designs prospectively with reasons; never tune them
to favorable activity results or silently lower them to declare success.

The old family registry has 139 annotation-connected components, including an
87-label exposed development component. A family-edge-only diagnostic yields
254 components; neither count certifies evolutionary independence. Historical
protected identities, exposed lineages and custom final roles must remain
unchanged. The protection union includes 4,723 canonical structures, 14 components
and 42 proteins. Do not clear old exposure by renaming a family or using an
upstream train/test label. Four old DOI/group-ID graph components mix role labels;
source-key namespace and CHEMBL8809 canonical aliases need reconciliation.

The latest proposed next census is 3 CPU-hours/24 hours, max two combined workers,
metadata/ID/structure only, up to 500 targets/12,000 assays. It is NOT_APPROVED and
does not authorize values or final outcomes. Treat it as a proposal to critique,
not an instruction to execute or an assumption that it will solve the problem.

## Research tasks

### 1. Test novelty adversarially

Identify the closest decision-region determination, value-of-information,
Bayesian experimental design, multifidelity active search, assay matching,
assay-context modeling/curation and scientific-agent work. Include seminal
methods and work through your actual research date. For each, state exactly
what is established, which part of our proposal it already covers, and what
computational or empirical distinction remains. Verify the existing leads
Javdani et al. (2014), Nguyen et al. (2021), AssayMatch, PCAM and ChEMBL assay-annotation
work rather than treating their cached descriptions as authoritative.

If the proposed policy is a direct instance of standard decision-region/VOI
machinery, say so. Recommend one technically defensible contribution, or state
that a benchmark/curation/product contribution is more credible and requires
an explicit change of research objective. Do not invent a theorem or gap.

### 2. Find actual usable data, not merely dataset names

Evaluate our existing sources first, then a short list of stronger alternatives.
For each serious candidate provide the primary paper, official version/release,
download/location, format/size, schema/unit of observation, endpoint semantics,
protein/organism/construct identifiers, source/methods traceability, actual
measurement-state distinctions, licensing and CPU feasibility.

The key question is whether the same compounds have **genuinely measured,
interpretable support across a reference and auxiliary contexts**, with enough
alternatives to support a molecular choice. Distinguish observed overlap from
common listed IDs, paper-reported counts, imputed/default labels and unknowns.
Do not infer per-context overlap from millions of global rows. If you cannot
verify overlap without a later data audit, give the exact minimal metadata-only
check needed and label the count UNKNOWN. Assess selective follow-up/MNAR,
censoring, duplicates, assay aggregation, stereo/canonicalization and whether
live API responses reproduce the publication's snapshot.

For MF-PCBA specifically investigate lawful fixed/author-released measurement
artifacts, SI/revision binding, single-dose versus dose-response semantics,
mean/median and missing-value floor behavior. A live retrieval script is not
a frozen dataset. For ChEMBL assess whether source/construct/procedure grouping
is verifiable and whether complete metadata already resolves the purported
paper-only uncertainty. For FS-Mol assess reuse for a better question without
pretending binary assay-relative labels are continuous potency or rare hits.

### 3. Design credible grouping and reference truth

Recommend biologically meaningful family granularity, with versioned primary
annotation evidence and a clear distinction between family, shared domain,
homology warning, source-connected isolation unit and taxon/construct context.
Review DOI/assay-group/deposition namespace and chemical/source dependence.
Specify how unknowns and conflicts are handled without relabeling protected data.

Determine what truly needs human domain adjudication. Two independent qualified
reviewers are a current proposal, not a journal rule already established.
Consider structured/experimentally defined reference designs that reduce manual
burden. Explain their validity and residual ambiguity. AI agreement and database
flags alone cannot be called independent gold.

Natural uncertainty must remain after complete permitted metadata. Do not create
it by hiding a known cell line, mutation, unit or cached fact. Show how a source
fact can change a supported decision, then explain how the later experiment
would test utility. Retain clear, ambiguous, contradictory and inaccessible
cases; do not select final cases because paper reading helped them.

### 4. Recommend one best empirical plan

Select one best-supported research/data plan and at most two fallback routes
with explicit triggers. Define population, task/reference unit, sampling,
exclusions, observed-support masks, splits, exposure handling, primary molecular
endpoint, baselines, uncertainty, failure criteria and smallest useful pilot.
Separate facts already verified from assumptions needing local qualification.

Hold predictor/features/updates and cache access fixed when comparing policies.
Include strong metadata-only and upfront-evidence controls, fixed/random evidence
schedules, appropriate adapted decision-region/multifidelity methods, and cheap
strong acquisition baselines. Report the common feasible resource frontier.
An optimal zero-cost full-context policy can emulate an adaptive one; do not
manufacture an advantage by denying free information. Separate evidence actions,
CPU, analyst time and experimental costs. Do not invent their exchange rates.
Missing experimental cells cannot become faithful oracle observations.

The owner has not set a minimum meaningful effect. Plan effect/uncertainty
reporting and explain precision limits without treating seeds/tasks as new
independent families or selecting a success threshold from old pilot results.
Explain which failure would stop the hypothesis and which would only show an
access, sampling, annotation or implementation limitation.

### 5. Connect the research to a useful R&D product

Specify a realistic first plugin workflow: paper/molecule evidence lookup,
reviewable next-action plan and cited report/export. Separate implemented cached
metadata tools from proposed live agent behavior. Compare against the same model
using ordinary tools; define factual correctness, source fidelity, abstention,
workflow effort and integration outcomes independently of molecular-policy utility.
Identify relevant competitors from primary product documentation. Do not infer
customer demand, time savings or business ROI without evidence. No messages,
team writes, wet-lab orders, purchases or deployment are authorized.

### 6. Assess publication and practical constraints

JCAMD via subscription is our historical target, with a maximum publication
budget of USD 300. Verify current official scope, publication routes and any
mandatory charges; do not promise eligibility, acceptance, waivers or zero cost.
Recommend another journal only if its scientific fit is better, with primary
evidence and a clear contribution tradeoff. Dataset terms, article access,
research use, redistribution and commercial reuse must be assessed separately.

Assume CPU-first development, at most 4 combined CPU workers across local and
dr-train only under a later explicit grant. GPU, paid APIs/models/cloud compute
and paid papers are not authorized. Give realistic staged resource estimates,
labeling estimates versus measured/published figures. Do not run local/SSH jobs
or request credentials. Do not fetch project assay rows, reserved labels or gold,
rerun blocked bioactivity endpoints, or bulk-download multi-GB data. You may
inspect primary papers, official metadata and documented lawful release locations.
If access is blocked, report it and give the owner an exact official URL,
filename, expected size/checksum if published, and a proposed destination under
`research/raw_data/external-benchmarks/<dataset-release>/`. Do not bypass access
controls or imply that the destination/file already exists.

## Required output

Start with a concise **Thai owner explanation**: what is ready, what blocks us,
what should change, and one recommended next decision. Supply an **English
technical report** suitable for repository documentation, containing:

1. A corrected asset/readiness map, distinguishing local payload, metadata-only
   lead, exposed development, protected final and independently qualified data.
2. A closest-work/novelty matrix with primary citations and inspected scope.
3. A dataset feasibility matrix, exact release/access/terms evidence, verified
   support versus unknown overlap, and reasons for rejecting tempting candidates.
4. One recommended contribution statement plus a concrete protocol and its
   strongest falsification/control tests; two fallback routes maximum.
5. A staged qualification/experiment/product plan with dependencies, CPU/storage/
   source budgets, pass/fail/unknown gates and explicit owner decisions.
6. A reviewer-style publication assessment: strongest objection, missing evidence,
   current NO-GO/conditional-GO reasoning and what would materially change it.
7. A copyable handback for Codex listing exact next checks, required files,
   proposed download paths and permissions still missing. Do not claim code,
   datasets, certificates, interviews or experiments have been produced when
   you have only proposed them.

Attach primary URLs/DOIs next to the claims they support, note access dates and
version/correction mismatches, and keep an explicit uncertainty/contradiction
register. If the joint evidence/molecular-decision thesis is not currently
supportable, say that plainly and recommend the smallest evidence-backed owner
decision. Do not force a "wow factor" by changing endpoint meaning, hiding a
strong control, counting correlated groups as independent, or inventing results.
