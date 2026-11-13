# Actual local-workflow results

Author engineering acceptance only. External agent comparison: **NOT_RUN**. Primary effect: **NOT_ESTIMABLE**.

Frozen model cases: **6/6**. Actual deterministic conformance: **3/3**. Product provider attempts: **12**; generated tokens: **332**. No mock responses, automatic deterministic fallback or outcome-driven repeated cases.

| Frozen case | State | Selected | Calls | Generated tokens | Observed wall (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| molecular_weight_max-en | COMPLETED | 2 | 2 | 56 | 74.781 |
| molecular_weight_max-th | COMPLETED | 2 | 2 | 56 | 7.500 |
| logp_max-en | COMPLETED | 2 | 2 | 56 | 7.547 |
| logp_max-th | COMPLETED | 2 | 2 | 56 | 7.859 |
| tpsa_max-en | COMPLETED | 1 | 2 | 54 | 8.047 |
| tpsa_max-th | COMPLETED | 1 | 2 | 54 | 9.266 |

Case wall time covers queue/model/tool/validation polling, in a fixed sequential order, with a cold first model request and later warm requests. It is not a controlled EN-versus-TH or method timing comparison. Cases are author-selected paired translations; no population confidence interval is justified. Generated-token totals exclude prompt tokens and the separate seven-token technical canary. Conservative resource reservations are not measured compute use.

Native admission: one development reference, six evaluation candidates, three evaluation repository groups against a minimum of four. This fails readiness; it is not an agent method failure result. All proposed research controls and ablations remain NOT_RUN.
