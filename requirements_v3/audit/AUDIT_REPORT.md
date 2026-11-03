# Independent Audit Report — CuraLoop-RL Portfolio Pack v2 → v3

**Audit date:** 2026-11-03. **Scope:** examine previous on-disk v2 ZIP and specification files, static tests and available reference links. **Intended decision:** whether the owner can safely hand the v3 specification ZIP to GPT Work and then Codex for an independent personal pharmaceutical R&D portfolio. This is **NOT** a software security certification, full scientific literature systematic review, or proof that an app already exists.

## A. Reproducible inspection of v2

- v2 archive exists at `/mnt/data/CuraLoop-RL_Personal_Portfolio_GPO_Audience_Handoff_v2.zip`, size 67,094 bytes; contains **36 entries**. ZIP CRC scan / Python `ZipFile.testzip()` returned `None` (no detected CRC error).
- Entries include `GOAL.md`, `PLAN.md`, `README.md`, dashboard/product documentation, two agent prompts, two scenario YAMLs, scripts and **25-item paper manifest**.
- No `.pdf` member exists in v2; `PACK_STATUS.json` explicitly says **0 original article PDFs**. Earlier user-visible download failure is real as reported by the owner; local ZIP CRC success does **not** establish browser attachment delivery.
- `python -m unittest discover -s scripts -p 'test_*.py' -v` executed **3 passing tests** for the PDF fetcher helper, not for an app. `fetch_oa_papers.py --dry-run` listed 20 candidates but downloaded 0; it did not confirm licenses, retractions or actual PDF contents.
- Network access from the file-building container failed for NCBI, EBI and LIT-PCBA (DNS/connection failures). Therefore zero article PDFs can responsibly be included or asserted downloaded in v3.
- There is no runnable application, no real RL model or Digital Twin and no experimental benchmark evidence inside v2. Correct classification: *specification/handoff pack*.

## B. Findings, severity, evidence and corrective action

| ID | Risk | Severity | Evidence in v2 / gap | Required correction (v3 instruction) | Closure |
|---|---|---|---|---|---|
| F01 | Delivery confusion | HIGH | User cannot download previous link; archive valid locally, delivery path not confirmed | New shorter exact file path; ZIP CRC + checksum + standalone prompt; do not claim browser success | New path generated; user must confirm download |
| F02 | Misreadiness | HIGH | v2 contains instructions but no runnable repo, despite portfolio goal | Prompts demand working demo + executable tests + local commits, real evidence | Spec corrected; implementation pending |
| F03 | Article PDFs absent | HIGH | 25 references, 0 PDFs; downloader dry-run is not network test | Explicit inventory, rights-aware local-only downloader, no fabricated attachments | Disclosure closed; acquisition pending |
| F04 | Literature verification overclaim | MEDIUM | 25 titles listed but not all checked against publisher metadata | Paper audit labels `SOURCE-CHECKED` vs `CATALOGUED-UNVERIFIED`; investigate before citing publicly | Partial; remaining must be checked |
| F05 | Digital Twin overclaim | HIGH | Simulator has no physical lab counterpart, real-time update or prospective validation | Strict maturity ladder and permitted terminology in UI | Spec corrected; operational validation unavailable |
| F06 | RL novelty overclaim | HIGH | GLARE 2025 already RL policy for VS; SimDMTA 2026 DMTA simulator; MF-BO 2025 cost-aware methods | Prior-art matrix, falsifiable hypothesis, no `first`/`novel` without experiments | Spec corrected; novelty unproved |
| F07 | Hidden-label leakage | CRITICAL | Oracle interface described but not demonstrated/tested | Process-level oracle isolation in benchmark, fake-policy leakage tests, prohibit hidden `y` in observation/dataframe | Test requirement defined; implementation pending |
| F08 | RL same-pool memorization | CRITICAL | Repeated replay episodes can expose all labels for a target | Use disjoint train/val/test target families for learned policy; do not claim generalization from same pool | Protocol defined; implementation pending |
| F09 | Cold-start ambiguity | HIGH | Greedy/uncertainty require seeded labels; no initial seed budget contract in prompts | Fix shared initial labeled set, label balance, source, budget accounting or explicitly sunk historical cost | Contract added; implementation pending |
| F10 | Unequal policy comparisons | HIGH | Policies might receive different seeds, models or query costs | Matched initial labels, budget, oracle, compute and tuning regime; multi-seed paired evaluation | Contract added; implementation pending |
| F11 | Cost, delay, fidelity confusion | HIGH | Future synthetic overlays could be presented as real GPO assay parameters | Per-metric provenance flags and UI labelling `SIMULATED COST/TIME` | Contract added; implementation pending |
| F12 | Synthetic truth confused with public assay | HIGH | Synthetic fixtures and historical replay both supported | Two-field provenance: `data_origin` = `SYNTHETIC_ONLY` or `HISTORICAL_PUBLIC_DATA`; `scenario_origin` = `SYNTHETIC_ASSUMPTION` or measured; IDs | Contract added; implementation pending |
| F13 | Third-party rights unknown | HIGH | Source-paper PDF rights and LIT-PCBA dataset reuse terms not verified for redistribution | Link only by default; manual per-source licensing gate; no raw data PDFs committed | Policy defined; external decision pending |
| F14 | Organizational IP / logo risk | HIGH | Personal work to be presented inside GPO may be mistaken as GPO product | Personal independent disclaimer, no GPO seals/data/logos/claim of endorsement, review side-project obligations | Documentation corrected; owner review remains |
| F15 | Downloader safety claims too broad | MEDIUM | 3 tests only check helper behavior; retraction/identity/full license checks not proven | Mark utility `BEST_EFFORT/NOT_FULLY_AUDITED`; additional manual checks required for redistribution | Disclosure closed; internet integration pending |
| F16 | Design vs functioning UI confusion | HIGH | Four-view UX design exists without evidence of actual screens | Work must launch app, capture actual outputs, confirm all buttons and export | Acceptance contract added; implementation pending |
| F17 | Windows / package reproducibility | MEDIUM | Tool/env pin and clean-room installation unverified | Python 3.11 CPU setup, PowerShell, dependency lock, smoke tests, run manifest, no paid API | Acceptance contract added; implementation pending |
| F18 | Silent failure / fabricated evidence | HIGH | Future agent may generate metrics or test statuses from templates | `DONE/TESTED/PLANNED/NOT_RUN/BLOCKED` report; no fake plots, no screenshots from mocks | Instructions corrected; implementation pending |
| F19 | Unbounded solo-project scope | HIGH | RL/twin/synthesis/future clinical ambitions too big for first release | Goal gates P0-P5, working demo first, optional features explicitly excluded | Spec corrected |
| F20 | Security threat model absent from prompt | MEDIUM | File uploads/paths/credentials could leak via logs/repo | Require no secrets, path validation, max file size, no arbitrary pickle loading, dependency review | Threat and acceptance docs added |
| F21 | Non-ML audience comprehension | MEDIUM | Strong technical detail but little assurance that user sees uncertainty and provenance | Thai storyboard, 4 pages, 'what it means' text, clear zero/failed-case states | UX spec strengthened |
| F22 | Reproducing paper benchmark results | MEDIUM | Current references lack data/version/source recording in runs | Hashes and frozen configs, policy/reward definitions, bootstrap paired intervals | Protocol strengthened |

**Critical open gates:** the app has not been built; no article PDFs downloaded; no dataset redistribution rights confirmed; no machine-trained RL results; no operational DT validation; user download not yet confirmed. These are not concealed by a `PASS` on ZIP structure.

## C. Correct scientific framing

- **Problem:** select which compounds to assay first under a limited, simulated budget and delayed feedback.
- **Method:** retrospective screening decision simulator with hidden ground-truth labels, basic baseline policies and optional learned strategy selector after robust evaluation.
- **Closest competitors:** GLARE (reinforced AL for VS, NeurIPS 2025), SimDMTA (DMTA active learning simulator, JCIM 2026), multifidelity Bayesian optimization (ACS Cent Sci 2025). Our positioning is *transparent portfolio workbench + reproducible stress tests*, **not** invention of RL screening or the first twin.
- **Demonstrable value:** explanation of screening decision trade-offs using public/synthetic data.
- **Not validated:** drug efficacy, manufacturing savings, predictive clinical utility, real GMP use, confirmed ROI, prospective lab behavior, live twin.

## D. Recommended minimum acceptance before presentation

1. Fresh Windows CPU installation documented and actually executed.
2. Offline synthetic demo works end-to-end (set scenario → run → reveal only due results → compare 3 real policies → export).
3. 15+ critical simulator tests including no hidden-label access, budget conservation and deterministic replay pass.
4. Charts derive from event logs; seed and scenario configuration appear on screen and exports.
5. Comparator budget, initial labeled seed and cost/latency definitions are disclosed.
6. UI declares *personal prototype*, *synthetic cost/time*, *not an operational digital twin*, *no verified pharmaceutical efficacy*.
7. No unlicensed PDFs/datasets, company data, brand assets, secrets or unapproved pushes.
8. Work hands off git SHA, exact tested commands, screenshots from real app and remaining issues to Codex.

## E. Selected research sources checked during this audit

- GLARE, NeurIPS 2025: https://papers.neurips.cc/paper_files/paper/2025/hash/57ac7ccded0eaaec4ad6f05612289b79-Abstract-Conference.html
- SimDMTA / *Query Matters*, JCIM 2026, DOI 10.1021/acs.jcim.5c02504: https://pmc.ncbi.nlm.nih.gov/articles/PMC13014458/
- *Bayesian Optimization over Multiple Experimental Fidelities*, ACS Cent Sci 2025, DOI 10.1021/acscentsci.4c01991: https://pmc.ncbi.nlm.nih.gov/articles/PMC11869128/
- REINVENT4, J Cheminform 2024, DOI 10.1186/s13321-024-00812-5: https://pmc.ncbi.nlm.nih.gov/articles/PMC10882833/
- LIT-PCBA official set: https://drugdesign.unistra.fr/LIT-PCBA/index.htm ; paper DOI 10.1021/acs.jcim.0c00155: https://pubmed.ncbi.nlm.nih.gov/32282202/
- TDC data splits: https://tdcommons.ai/functions/data_split/
- National Academies *Foundational Research Gaps and Future Directions for Digital Twins* (2024): https://doi.org/10.17226/26894
- NIST definitions and state of the art: https://www.nist.gov/digital-twins/definitions-and-state-art

Citations above support the direction; every article's specific data, code and full-text redistribution rights still require independent checks.
