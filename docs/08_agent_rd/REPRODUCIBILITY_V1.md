# Reproducing the AgentRD computational report

There are three different operations: inspect retained real evidence, replay
its deterministic scoring/analysis, or run fresh model inference. Only the
last consumes a new model session. Replaying a receipt is never described as
new inference. No private CF1 row, final16 record or hidden outcome is needed.

## Exact historical execution

The source/protocol freeze was committed and pushed as `064bd3d` before any
locked model call. Its SHA-256 is
`5b70e5f1454e9062441b3e292a50fab45f9aebe73ed7994971c6a88de2ad4c8e`.
It pins 27 code/input/protocol files. Later commits add actual receipts, author
documentation, figures and analysis/reporting helpers while retaining those
bytes. The manifest identifies the exact executed remote `worker-v2.py`; the
later formatted local worker source is a separate identity. Do not assume they
are byte-identical. The private full-return audit verifies both versions.

On Windows, preserve the committed bytes when cloning:

```powershell
rtk proxy git -c core.autocrlf=false clone https://github.com/siriponsri/curaLoop-RL.git
```

The historical Python interpreter was 3.12.10. The observed version receipt is
`docs/evidence/agent-rd-20261110-v1/python-environment-observed-v1.json`.
It was recorded during execution, not a whole-environment pre-run byte seal.
Install the repository's declared Python dependencies into a separate local
environment using the repository setup instructions. No model is needed for
the following read-only replay. Commands assume the repository root and its
configured `.venv`; the module form keeps the repository on Python's path:

```powershell
rtk proxy .venv/Scripts/python.exe -m tools.agent_rd_verify_results_v1
```

The replay requires the final actual analysis to exist. During an active study
it intentionally fails rather than inventing missing results. After delivery,
it verifies the freeze, every public unit envelope, the separately implemented
frozen score, all planned denominators and the prespecified analysis. It also
compares the actual initial B2/P messages, schema, seed and output cap wherever
both initial responses exist. It makes no model, SSH, HTTP or paid call. Its
default mode does not overwrite any evidence or emit a new receipt.

The historical one-time analysis builder uses exclusive output paths. Do not
delete its output to rerun it. Use the read-only verifier to check identical
results. A new analysis with different definitions needs a separately labeled
version and must preserve the original result. Do not edit a pin, rerun the
one-time freezer or normalize old ledgers merely to make a check pass.

## Evidence structure

| Artifact | Meaning |
| --- | --- |
| `protocol-freeze-v1.json` | The pre-call source and design identities. |
| `locked-results-v1/<unit>.json` | Actual attempted-unit state, frozen score, timing and cost. |
| `locked-results-v1/<unit>-trace.json` | Original model requests/responses, tool receipts and revisioned state. |
| `locked-progress-v1.json` | Final disposition of all 408 planned units, including unattempted work. |
| `analysis-v1/analysis.json` | Prespecified aggregation and conditional primary interval. |
| `descriptive-v1/all-planned-units.csv` | Descriptive per-unit coverage, refusal, malformed-output and cost fields. |
| `descriptive-v1/matched-ablation-anchors.csv` | P and A-NOREPAIR on the same eight anchors only. |
| `result-figures-v1/` | Actual-data SVG/300dpi PNG figures, linked to exact analysis hashes. |
| `example-mission-v1.json` and `example-dossier-v1/` | One actual pre-freeze UI acceptance mission; not a locked observation. |
| `complete-remote-return-v1.json` | Full private return/file-reread and matching provider-file audit. |
| `owned-remote-cleanup-v1.json` and `fresh-remote-absence-v1.json` | Exact owned removal after successful return. |

Paths in this table are relative to
`docs/evidence/agent-rd-20261110-v1/`. A listed final artifact is not a claim
that it already exists during active execution. The evidence index and final
closeout identify what was actually completed. Private returned operational
archives remain outside public Git; all public study inputs, unit traces and
analysis needed for the read-only replay are included.

## Localhost use after research-worker cleanup

Start the existing Windows web launcher following README. The screening,
Confirmation evidence, C Workspace and Agent RD pages remain available. In
Agent RD, deterministic mode uses actual admitted public aggregates without a
model. Recorded local missions are read without regenerating responses. The
exact published real-model example also opens as the retained EN/TH HTML
dossier from the evidence index and README; a clean checkout does not silently
import a private development mission store.

Model mode requires a currently authorized operator session. The research
container and task root are deliberately removed after complete return, and
the new account is closed. Reopening the completed study's ledger, recreating
its deleted root or borrowing another project's session is prohibited. A future
live model session needs fresh owner authorization and operator configuration
through `CURALOOP_AGENT_SESSION`, using the same bounded provider contract.
There is no paid-provider fallback or claim that the retired research worker
is an always-on product service.

## Fresh model replication is a new run

The full planned matrix is 408 units, including 312 model missions. This is not
a one-command invitation to reuse the closed research allowance. A new run must
have a fresh task namespace, resource ledger, model identity, source/version
receipt and schedule disposition, while retaining the historical outputs.
Model sampling, CPU hardware, constrained JSON generation, cache state and
runtime versions may change outcomes or latency despite the same seed. The
historical tag is Typhoon 2.1 Gemma3 12B Q4_K_M; the exact digest, Ollama0.12.6
and CPU-only settings are in the frozen protocol. Existing weights are not
redistributed and their license is separate from MIT code.

The fixed source-gate study does not require new molecular data or prospective
outcomes. A broader agent, new tools/model, unrestricted reasoning tasks or
changes to scoring would be a different study, not a silent repair of this one.
