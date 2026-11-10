# CF2 critical source comparison

10 November 2026, Asia/Bangkok. Single-implementer targeted review, not a
systematic review, independent scientific assessment or novelty certificate.
Scope: the two owner-approved CF2 mechanism hypotheses. No molecular data,
private CF1 rows, new activity records, model fitting or final16 access.

## Source matrix and actual read depth

| Source | Exact inspected location / access | Established overlap | Important difference or limit |
| :--- | :--- | :--- | :--- |
| [Nguyen and Garnett, AISTATS 2023, diverse active search](https://proceedings.mlr.press/v206/nguyen23d.html) | Publisher PDF physical pp2-5, sections 2-3, equations 2-12; physical pp18-19, appendix F/G. New local PDF authenticated and targeted text inspected | Multiclass diminishing-return discovery, Bayesian feedback decisions, a submodular batch approximation and explicit treatment of conditional label dependence as a computational challenge | Its practical approximation uses a mean-field/Jensen construction. This leaves approximation questions, not an established CuraLoop contribution. The unbounded-utility hardness statement is not automatically inherited by a capped coverage utility |
| [Golovin and Krause, adaptive submodularity](https://arxiv.org/abs/1003.3967) | Local 60-page article, targeted physical pp6-8, section 3 and definitions 1-3; PDF text and matching online passages inspected | Pointwise submodularity survives expectation for a fixed joint law; adaptive conditional marginals need a separate diminishing-return condition | Arbitrary outcome correlation does not grant adaptive-greedy guarantees. No theorem is transferred to a fitted molecular model or source-selection process |
| [Nguyen, Modiri and Garnett, ICML 2021, multifidelity active search](https://proceedings.mlr.press/v139/nguyen21f.html) | Publisher PDF physical pp1-4, sections 2-3; targeted source text inspected | A cheap noisy oracle and expensive faithful oracle, posterior feedback, budget awareness and nonmyopic search are established | The source's timing/oracle-access contract differs from an already screened, selectively confirmed primary-hit universe. This is not an interchangeable reproduction or automatic matched baseline |
| [Jiang et al., NeurIPS 2018, batch active search](https://papers.nips.cc/paper_files/paper/2018/hash/a7aeed74714116f3b292a982238f83d2-Abstract.html) | Primary publisher PDF indexed introduction/problem and abstract read online. A separate local PDF request timed out; no local full-text or native reproduction claim | Batch feedback, cumulative positive discovery and computational approximations are established | Partial read depth; this source alone does not resolve the exact confirmation/group utility |
| [Johnson et al., 2007, HTS variability and active chemotypes](https://pubmed.ncbi.nlm.nih.gov/17272827/) | PubMed author abstract/identity; DOI 10.1177/1087057106297826. Publisher full-text request timed out | Primary-hit cluster sampling, screening variability and follow-up chemotype identification were already studied with simulation and replicate information | Abstract-only lead. No reconstruction of its detailed algorithm, numerical findings or exact overlap is claimed; full paper would be needed before reproducing it |
| [Jansen et al., JCIM 2019, biased complement diversity](https://doi.org/10.1021/acs.jcim.9b00048) | Indexed primary publisher Workflow Design/Conclusion and supporting-workflow excerpts; direct live fetch 403 | Quality-biased per-cluster selection, a core/complement design and MaxMin diversity form established practical hit-finding workflows | Indexed sections only, not end-to-end article/SI verification or a native KNIME reproduction. No exact published effect is imported into CuraLoop |
| [Maus et al., MOCOBO, arXiv 2501.19342v4](https://arxiv.org/abs/2501.19342v4) | Canonical v4 identity and online PDF physical pp1-5, sections 3.1-3.2 and equations 2-7 | Set-valued coverage optimization, expected coverage improvement and a batch extension have existing methods | Its continuous/multi-objective response coverage differs from binary positive structure-group coverage. It is adjacent work, not evidence that the two algorithms or data contracts are identical |
| [MolPAL, existing R04](https://arxiv.org/abs/2012.07127) | Owner reading room, pinned R04 PDF; selected physical pp2-4, especially p3 equation 1 | Pool-based molecular search and a top-k computational objective | These inspected pages concern docking/top-k framing, not measured primary-to-confirmation chemotype recovery. Do not call the whole PDF newly read |
| [Asynchronous local penalisation, existing R10](https://proceedings.mlr.press/v97/alvi19a.html) | Owner reading room, pinned R10 PDF; physical p2 preliminaries/equation 5 and start of p3 | Batch dependence, pending observations and uncertainty marginalization are established selection issues | Best-function BO and its assumptions differ from the binary confirmation objective; no inherited method guarantee |
| [Batch local penalisation, existing R11](https://arxiv.org/abs/1505.08052) | Owner reading room, pinned R11 PDF; physical p2 sections 1.1-1.2/equations 2-3 and start of p3 | Joint batch uncertainty and a cheaper diversity-promoting approximation predate CF2 | Lipschitz function optimization is not the same endpoint, observation support or binary oracle model |

The existing room is
`C:\Users\User\Documents\ChatGPT\Drug Discovery\literature\pdfs`.
Its three reused PDFs match the original literature manifest. New reading copies
and extraction text remain in the ignored LR-CF2P reading folder; they are not
redistributed in Git. Three new PDF downloads succeeded, totaling 1,960,842
bytes; the batch-active-search download failure is retained. Downloaded,
extracted, selectively read and independently reproduced are different states.

## Consequence for the two mechanisms

**H1: primary-to-confirmation error plus within-group dependence.** Different
joint outcome laws can change a useful batch while preserving every marginal
probability. That makes an information/model question worth specifying. It does
not create a new expected-coverage objective or prove that CF1 contains usable
joint signal. A fixed realization's group coverage is a union-coverage function;
averaging it preserves static submodularity without requiring independence.
The product-probability formula needs independence, not the coverage objective.

**H2: confirmation-feedback adaptation.** The known group of a compound and its
unknown binary confirmation can be represented as a nonpositive class or a
group-specific positive class. Capped group reward then recovers positive-group
coverage. Feedback and budget-aware selection still require an actual
conditional model and measurable incremental value; relabeling this as agentic
or reinforcement learning does not supply either.

These are our reductions/interpretations, not assertions that all cited papers
implement the same practical algorithm. No exact fast dependence-aware method
with identified information support was established by this review. The
[single design decision](../03_research/CF2_DESIGN_DECISION_20261110.md) therefore
rejects the two generic mechanisms as sufficient new-method claims. It does
not prove that every more specific research idea is impossible.

## Journal relevance

The current official [JCAMD aims and scope](https://link.springer.com/journal/10822/aims-and-scope)
prioritizes experimental validation and allows appropriate retrospective
validation for novel methods or innovative computational strategies. It does
not require a new mathematical theorem in every paper. Our concern is the lack
of a demonstrated distinct strategy and independent supporting evidence, not a
self-imposed demand for theoretical novelty or p < 0.05. No new fee assertion,
paid route or submission is made here.

Review limits: targeted searches, selected full-text sections, one reviewer,
abstract/indexed-only sources explicitly marked, no author-code execution or
unreviewed empirical claims. Access gaps do not become negative findings.
