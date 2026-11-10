# A0: targeted agent-reliability literature review

Author-conducted targeted review, not systematic/scoping review, native author
reproduction or novelty certification. The attached starter's bibliographic
claims were treated as leads and checked against primary sources. No external
expert review is claimed. Search date: 10 November 2026.

| Primary source | Actual read depth | Consequence for this project |
| --- | --- | --- |
| [ChemCrow, Nature Machine Intelligence 2024](https://www.nature.com/articles/s42256-024-00832-8), DOI 10.1038/s42256-024-00832-8 | Publisher abstract and evaluation/Fig4 text | Chemistry tools and agents are established. Human and LLM judgments can disagree; a fluent explanation is not a reliable numeric oracle. No reproduction or transfer of their reported effects |
| [Coscientist, Nature 2023](https://www.nature.com/articles/s41586-023-06792-0), DOI 10.1038/s41586-023-06792-0 | Selected publisher architecture/method excerpts | Orchestrated tools, web/documentation and experimental planning predate CuraLoop. We have no autonomous physical laboratory or arbitrary code-execution claim |
| [Paper2Agent, Nature 2026](https://www.nature.com/articles/s41586-026-11044-y), DOI 10.1038/s41586-026-11044-y | Publisher-indexed Overview, tool validation and large-scale evaluation sections; initial direct fetch hit identity redirect | Validated locked tools, provenance, out-of-scope rejection and adversarial drift already overlap the proposal. An MCP wrapper plus validation is not a new method |
| [ScienceAgentBench, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/f12b4df26344f3be803c06b555252efe-Abstract-Conference.html) | Official abstract; physical pp1-3 formulation, p5 program-evaluation rubric, p28 error analysis | Execution is distinct from task success; costs and semantically wrong executable outputs matter. Its expert-validated multi-publication coding tasks differ from our author-defined typed cases. Its figure grading also uses a model judge; ours uses no model judge and does not reproduce its benchmark |
| [Tooling or Not Tooling?, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.424/), DOI 10.18653/v1/2025.findings-naacl.424 | Official abstract/identity; physical pp2-3 methods, pp11-13 evaluation format and tool-leakage discussion | Tool benefit depends on task and tool design. Strong base and non-LLM controls and input-format errors matter. External tool training exposure can be uncertain; our closed source oracle measures copying/arithmetic/scope on exposed data, not unseen chemical prediction |
| [CF2 prior source review](../02_literature/CF2_CLOSEST_WORK_20261110.md) | Existing preserved source-located record | Coverage/feedback novelty remains NO_GO. The new agent study does not revive or relabel that claim |

Additional located leads, **not yet fully reviewed**: BioDiscoveryAgent ICLR2025,
MLR-Bench NeurIPS2025, SCI-AGENT-EXAM arXiv2610.32441, and the verification-loop
decomposition preprint arXiv2607.17044. Preprints are not peer-reviewed evidence.
The initial broad web search also returned commentary; only primary sources
support the table above. Full read depth and searches must be updated before the
final manuscript; inaccessible methods are recorded rather than invented.

## Provisional contribution, three sentences

We implement an auditable localhost pharmaceutical evidence workbench whose
single-controller agent uses existing authenticated retrospective aggregates
and releases only typed, source-checkable claims or explicit abstentions.
We evaluate the incremental reliability and cost of a deterministic claim gate
using the same model, information, tools and generation limits as simpler
controls, reporting proposals separately from released results and fallback.
The contribution is a bounded application and controlled computational study,
conditional on actual results; it is not the first scientific agent, a new RL
selector, a biological discovery result or a claim of general agent superiority.

Strongest counterexample: validated tools and denial behavior already exist in
Paper2Agent, while a deterministic pipeline may solve these structured tasks
more reliably and cheaply. If that happens, the manuscript must state that the
LLM added cost/interaction rather than demonstrate a new scientific advantage.
If source/tool availability differs between arms, that comparison is explicitly
labelled and cannot establish the primary verifier effect.

## Feasible comparison without reproducing expensive prior agents

Use strong deterministic B0, evidence-supplied LLM-only B1, the same LLM with
identical typed tools B2, guarded P and an isolated no-repair ablation. B2 already
serves as the verifier-off control; this clarification precedes locked execution.
Do not call these implementations native ChemCrow/Paper2Agent reproductions.
No expert/LLM judge supplies the primary score. Existing source CSV arithmetic
and documented scope rules supply a separate deterministic oracle. Full agent
traces, failed calls and all-attempt costs are necessary evidence.

Editorial readiness remains conditional. The method/software case must stand
on its actual specificity and results; an incomplete or narrow result can be
delivered as a complete negative/inconclusive report without promising that a
particular journal will accept it. A Thai scoping review would require a separate
review protocol and is not a translation of this empirical manuscript.
