# Research specifications

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
The registry currently contains only the known HIV regression resource. New
assay ingestion, analog audits, acquisition baselines and the multi-target runner
remain unimplemented. The declarative study config below is still not executable
by the existing application CLI.

`configs/development_protocol.json` is a declarative development design, not an input supported by the current CLI. `manifests/protocol_freeze.json` intentionally records that final tasks, primary contrast and material effect have not been frozen. Null fields are unresolved scientific decisions, not missing experiment results.

Implement a versioned runner and validate these contracts before executing them. Existing CLI/configs remain unchanged. Use the detailed protocol under `docs/03_research/`. Put future run outputs under an excluded run directory and publish selected rights-compatible artifacts with immutable identities.

## Draft 1.1 additions

The full-text review adds source release/AID/phenotype mapping, explicit initialization regimes, frozen/retrained and nearest-hit controls, metric-definition identities and separate compute reporting. Read `docs/03_research/BASELINE_SPECIFICATION.md` before implementation. The configurations and schema remain declarative; they do not install an importer, new scheduler or backend integration.
