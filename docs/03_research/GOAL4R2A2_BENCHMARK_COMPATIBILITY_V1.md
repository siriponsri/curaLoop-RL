# MolDesignBench compatibility and exposure decision

6 November 2026. Goal 4R2-A2 source review, without task/gold intake or execution.

**NO_GO as a direct benchmark of CuraLoop's current evidence-to-plan/report
workflow. CONDITIONAL_GO as a future auxiliary molecular-design evaluation.
Commercial reuse of the benchmark data is NOT_CLEARED.**

The [readiness manifest](../../research/manifests/goal4r2a2_benchmark_readiness_v1.json)
freezes inspected source identities and prospective rules. These are readiness
findings, not agent scores, molecular discovery results or novelty certification.

## What the benchmark measures

The native output is a molecule represented by SMILES, or explicit `None` for
refusal. The evaluator checks molecular property and fragment constraints.
CuraLoop's implemented offline workflow returns typed evidence, plans and report
bundles. Native evaluation therefore needs a new molecule-generation component
and a frozen adapter. Evaluating only extracted constraints or using fixture
responses would be an adapted test, rather than reproduction of the native
tool-assisted setting. [Paper v1](https://arxiv.org/html/2609.27349v1),
[pinned evaluation guide](https://github.com/KU-AGI/MolDesignBench/blob/69b0dc5571202e03e8867efa898899781fb7d74a/docs/evaluation.md).

RDKit descriptors are computed molecular properties. ADMET-AI outputs are model
predictions. Neither constitutes a new measured assay outcome. This benchmark
does not identify confirmation-policy value, real laboratory savings, selectivity,
or performance across twelve biological groups.

## Pinned sources and rights

| Artifact | Identity and interpretation |
| --- | --- |
| Official code | Commit `69b0dc5571202e03e8867efa898899781fb7d74a`, 7 October 2026; tree `72ab86a7b1d59e02e0560c14b0e566af049b10d2` |
| Dataset repository | `LG-AI-Research/MolDesignBench`; commit `34f8dc0ac2ae77870952d06471f836d2bd9e7c3e` |
| Dataset card | Blob `a4a2dec0d27826ead3054ae8e88442f03208b617` |
| JSONL file metadata only | Blob `21e64a39ab105d29d0b5558ea28ac53959343947`; 4,149,306 bytes; file contents unopened |
| Evaluator | `evaluate/evaluate_benchmark.py`, blob `30bf591c8027535c9147735b6e9d3a335f448986` |

These are Git object identifiers, not SHA256 values. The inspected code commit
is not certified as the exact paper-experiment snapshot. Connected metadata
reports one `default` configuration and one `test` split with 2,000 rows. The
card/paper report 1,000 generation and 1,000 optimization tasks, each containing
900 feasible and 100 infeasible cases. Counts were not independently checked
against task rows. Metadata fields are `id`, `task_type`, `question`, `answer`
and `meta_info`. [Pinned dataset card](https://huggingface.co/datasets/LG-AI-Research/MolDesignBench/blob/34f8dc0ac2ae77870952d06471f836d2bd9e7c3e/README.md).

| Asset | Inspected terms | Consequence |
| --- | --- | --- |
| Main code | MIT | Retain copyright and licence notices |
| Bundled ADMET-AI/Chemprop copies | Separate MIT notices | Retain each notice; this does not clear every weight/service/data asset |
| Benchmark questions and answers | CC BY-NC 4.0 | Noncommercial research scope must be respected; commercial data reuse is NOT_CLEARED |
| Creation-model terms | Card invokes Anthropic model Terms of Use; exact terms version unresolved | Additional rights gate before intake/use |
| MOSES-derived data, weights and hosted tools | Separate provenance/terms | Review exact assets if a future adapter uses them |

Code licensing does not override dataset restrictions. No payment, permission
request or provider contact occurred. [Code licence](https://github.com/KU-AGI/MolDesignBench/blob/69b0dc5571202e03e8867efa898899781fb7d74a/LICENSE),
[dataset card](https://huggingface.co/datasets/LG-AI-Research/MolDesignBench/blob/34f8dc0ac2ae77870952d06471f836d2bd9e7c3e/README.md),
[CC BY-NC terms](https://creativecommons.org/licenses/by-nc/4.0/).

## Metric discrepancy register

| Metric/boundary | Pinned implementation and required reporting |
| --- | --- |
| Success | All constraints met for feasible cases; explicit `None` for infeasible cases |
| Fragment constraints | Exact counts for generation; minimum required counts for optimization |
| MCD | Percentile-normalized constraint distance among feasible cases with valid SMILES; pin the population and normalization |
| Feasibility F1/MCC | Pinned code classifies non-`None` attempt versus refusal, independently of molecular quality |
| Card Feasibility F1 | Describes feasible true positives as fully solved; differs from the pinned code |
| Validity/CSR | Pin exact denominators and treatment of invalid, missing and refused outputs before running |
| Refusal parsing | Empty or malformed output is not a successful `None` refusal |

The frozen synthetic contract example produces F1 **0.8 under the code's attempt
definition** and **0.5 under the card's fully-solved definition**. These hand-built
arrays are a diagnostic of differing definitions, not benchmark performance.
Native generation success must be reported separately from willingness to attempt.
[Pinned scorer](https://github.com/KU-AGI/MolDesignBench/blob/69b0dc5571202e03e8867efa898899781fb7d74a/evaluate/evaluate_benchmark.py).

## Runtime and a legitimate future comparison

The documented environment uses Python 3.11, Java 17, RDKit 2025.03.6, NumPy
1.26.4, PyTorch and patched local ADMET-AI/Chemprop. Scoring requires no LLM or
MolMIM call but still requires chemistry/ADMET dependencies; CPU time is
NOT_MEASURED. Native generation exposes seventeen tools; two require NVIDIA
MolMIM NIM, GPU containers and NGC access. Full native compatibility on the
approved CPU-only host is NOT_ESTABLISHED. No dependency installation or model
weight download was performed. [Installation](https://github.com/KU-AGI/MolDesignBench/blob/69b0dc5571202e03e8867efa898899781fb7d74a/docs/installation.md),
[MolMIM requirements](https://github.com/KU-AGI/MolDesignBench/blob/69b0dc5571202e03e8867efa898899781fb7d74a/docs/molmim_setup.md).

A later paired comparison should hold the model, chemistry backend, tools,
sampling settings, compatible prompts and resource budgets fixed. Compare an
ordinary search/tool agent with a CuraLoop-assisted agent using native molecule/
refusal scoring, while measuring evidence and report correctness separately.
Provider account/quota, token ceiling, timeout, retry limit and cost settlement
need explicit authorization. Upstream defaults of twenty rounds, four workers
and unlimited failed-instance retries are not approved here. Removing tools
requires a named adapted setting and corresponding limits on comparisons.

## Exposure and prospective split

No benchmark JSONL task/question, reference answer, feasibility-label row or
reference molecule was returned to the team. Generic card examples involving
logP and pyridine counts, the BaseTool ethanol example and `analysis.py` SMILES/
property examples were inspected. Actual matching task IDs/template groups
remain UNKNOWN. The connected HF structure tool unexpectedly attempted an
internal schema preview and timed out; no row content was returned. Its internal
row access is NOT_CERTIFIED. Schema was subsequently obtained through metadata-only
`/info`. Public/model-pretraining exposure is also NOT_CERTIFIED.

There is no official development split. The prospective rule hashes a resolved
provenance/template group with salt `CuraLoop-4R2-A2-20261106-v1`, modulo 100:
below 20 development, below 40 validation, otherwise internal evaluation.
Exposed or unresolved groups are quarantined. Exact matching, duplicate/template
grouping, balance, attrition and cross-group dependence need an authorized index
before any roster freeze. Hash fractions do not guarantee exact role quotas or
independence. Concrete roster: **NOT_FROZEN**; no task data were read to create it.

Gold stays scorer-only. Because questions and answers share a source file, any
future intake needs physical separation and access checks before generation.
PythonShell, arbitrary files and live retrieval cannot be allowed to expose that
file to the agent. The ten A2 checks test prospective schema boundaries, not a
deployed agent sandbox or a proven contamination-free test.

## Disposition

- **GO:** source/adapter planning and engineering contract checks.
- **CONDITIONAL_GO:** noncommercial auxiliary molecular-design evaluation after
  rights, output adapter, exposure/index, runtime and bounded-run gates close.
- **NO_GO:** native evaluation of the current plan/report output, commercial
  dataset integration, full native CPU compatibility claims, or scientific/business
  benefit claims from this readiness review.

ASB remains deferred. Goal 4R2-A2 does not start P1, model evaluation or journal
submission. See the [A2 readiness report](GOAL4R2A2_READINESS_V1.md) and
[execution contract](../06_execution/GOAL4R2A2_EXECUTION_CONTRACT_20261106.md).
