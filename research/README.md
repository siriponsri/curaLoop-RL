# Research specifications

Latest preparatory work: [candidate metadata/feature audit](../docs/03_research/CANDIDATE_ASSAY_AUDIT_V1.md)
and [hierarchical estimation/resource sensitivity](../docs/03_research/DESIGN_SENSITIVITY_V1.md).
Code is isolated under `research/preparation_v1/`. It does not ingest final
compound outcomes or assign final roles. Run the offline integrity check with
`python -m tools.check_design_preparation_v1`; preserve immutable network/simulation
packets rather than rerunning them in place. The owner selected 12+ families and
estimation without a confirmatory material-effect threshold; numeric CPU cap,
source/phenotype closure, independence and final task allocation remain open.

Latest executable evidence: [fresh-venv reproduction](../docs/03_research/NCATS_REPRODUCTION_V1.md)
matches all 108 original scientific traces, and the separately frozen
[Gaussian amendment](../docs/03_research/NCATS_GAUSSIAN_RESULTS_V1.md) executed 54
new development runs using the existing sklearn backend. Original source/data/
run artifacts stay unchanged. The final study and learned transfer remain open.

## Current executable foundation

The local Reviewed v2 continuation adds an **integer-time reference**, a small
local registry validator and constructed diagnostics. These live under
`research/`, are not installed by the application package and do not replace the
original engine, UI, models or historical results.

```powershell
python -m research.task_registry --output outputs/research/registry.json
python -m research.toy_validation --output outputs/research/toys.json
python -m research.legacy_regression --output outputs/research/legacy-smoke.json
```

Run from the repository root using its existing development environment
(`jsonschema` is already a development dependency). The last command executes
three independent two-assay historical regression campaigns, not a new study.
All output locations above are ignored by Git. Selected current evidence is
preserved separately in `docs/evidence/reviewed-v2-integration-20261104/`.

Read [the reference contract](../docs/03_research/INTEGER_REFERENCE.md) and
[foundation checkpoint](../docs/06_execution/FOUNDATION_CHECKPOINT.md).
The original registry contains the known HIV regression resource. The separate
`manifests/ncats_development_tasks_v1.json` now identifies three public NCATS
development endpoints, with exact raw/cohort hashes and overlap/attrition audits.
Six fixed controls and the bounded runner completed 108 runs; see
[the development result](../docs/03_research/NCATS_DEVELOPMENT_RESULTS_V1.md) and
[its frozen protocol](../docs/03_research/NCATS_DEVELOPMENT_PROTOCOL_V1.md).
Raw/full derived pools remain ignored, while public run evidence is versioned.
The original declarative study config remains unsupported by the application CLI.

`configs/development_protocol.json` is a declarative development design, not an input supported by the current CLI. `manifests/protocol_freeze.json` intentionally records that final tasks, primary contrast and material effect have not been frozen. Null fields are unresolved scientific decisions, not missing experiment results.

The versioned development runner is implemented; it does not complete the final
study or install new application inputs. Use the detailed protocol under
`docs/03_research/`. Future substantive changes need new experiment identities.

## Draft 1.1 additions

The full-text review adds source release/AID/phenotype mapping, explicit
initialization regimes, frozen/retrained and nearest-hit controls, metric
identities and separate compute reporting. Read
`docs/03_research/BASELINE_SPECIFICATION.md` before implementation. The original
configs remain declarative. The separate NCATS runner has its own executable
frozen config; no asynchronous backend integration or learned transfer is
implemented by this pilot.
