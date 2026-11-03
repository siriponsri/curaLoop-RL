# Prior art, novelty risks and positioning

## Key finding: RL-guided screening is not new

1. **GLARE (Chen et al., NeurIPS 2025):** reinforced active learning for large-scale virtual screening; formulates molecular selection as an MDP and uses GRPO. https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html . A GLARE-titled public repository exists, but its authorship/official-code status must be verified separately before citing code or copying it; do not assert that a specific GitHub URL is the official source without checking. Do not claim that bringing RL/MDP to screening or balancing diversity and relevance is original.
2. **SimDMTA / Query Matters (Williams et al., 2026):** a simulator of the Design-Make-Test-Analyze cycle comparing selection strategies using docking scores as proxies. DOI: https://doi.org/10.1021/acs.jcim.5c02504 ; source https://github.com/HuwJWilliams/SimDMTA . Do not claim a closed-loop virtual screening simulator is new.
3. **Multi-fidelity Bayesian optimization (McDonald et al., 2025):** selects experiments according to measurement fidelity and cost and reports a prospective automated platform. https://pmc.ncbi.nlm.nih.gov/articles/PMC11869128/ . Do not claim cost/fidelity-aware experiment selection itself is new.
4. **Sample-efficient RL with active learning (2024):** combines RL and AL in molecular design. https://pmc.ncbi.nlm.nih.gov/articles/PMC10935729/ . A strong warning against novelty based only on concatenating the words RL and active learning.
5. **Digital twin requirements:** National Academies (2024), https://www.ncbi.nlm.nih.gov/books/NBK605502/ ; An & Cockrell (2022), https://pmc.ncbi.nlm.nih.gov/articles/PMC9351294/ . A replay simulator is not automatically a real digital twin.
6. **LIT-PCBA source paper (2020):** DOI https://doi.org/10.1021/acs.jcim.0c00155 . Newness cannot rest on using this existing benchmark.

## Defensible candidate contributions (hypotheses, not claims)

- **A carefully characterized screening-process twin fidelity ladder:** distinguish reproducible retrospective replay from calibrated measured feedback and real-world operational synchronization, with explicit VVUQ.
- **Systematic robustness benchmark:** compare strong RL and non-RL policies under controlled, traceable scenario perturbations combining finite assay budgets, delayed feedback, missing outcomes, proxy disagreement and target/scaffold shift; characterize where decision quality breaks down.
- **Meta-policy generalization study:** policy trained only on disjoint targets versus baseline tuned on validation targets; quantify whether adaptive policy behavior transfers rather than memorizing the same retrospective label pool.
- **Cost/latency-aware decision control with uncertainty:** evaluate whether calibrated uncertainty and dynamically changing capacity improve discovery *at identical total costs*, with useful failure analysis.
- **Auditable open architecture:** clear labels, provenance, event streams and ability to integrate future real assay feedback. Useful engineering but only a research contribution if supported by empirical comparative results.

## The most promising research title after evidence exists

"When Does Adaptive Policy Learning Help? A Reproducible Study of Cost, Delay, and Shift in Retrospective Drug-Screening Workflows"

Avoid "First digital twin for drug discovery" and "Revolutionary RL discovers cures". A methodological empirical study may be more defensible than promising an unprecedented architecture.

## Competitor checklist

| Work | Core contribution | Must differentiate |
|---|---|---|
| GLARE 2025 | RL selection policy in virtual screening | target-disjoint transfer, delays, simulator fidelity, strong comparisons |
| SimDMTA 2026 | closed-loop strategy screening simulation | measured-label replay, budget queue, detailed sim-to-real limitations |
| MF-BO 2025 | choose assay fidelity under cost | avoid simulated fidelity masquerading as measured paired assay |
| RL-AL 2024 | sample-efficient RL + AL | task is acquisition policy under constraints, not molecule generation |
| TDC and LIT-PCBA | existing data + benchmarks | data curation, traceable splits and fair method comparison |

## Falsifiable claims

C1: The proposed meta-policy improves confirmed hit discovery at fixed budget on at least one preregistered held-out regime with robust intervals. **Reject C1** if improvement disappears after fair tuning or at target-level bootstrap.

C2: Its benefit is concentrated in delayed/noisy/shifted regimes. **Reject C2** if performance is flat or worsens; report negative results.

C3: Twin-like scenario models predict future policy rankings. **Reject C3** when predictions fail against external measured settings or if no external validations exist; mark C3 *NOT_TESTED*, never *PASSED*.
