# Research benchmarks and provenance

This English operator reference restates the preserved source records. It does
not claim a new benchmark execution or certify CuraLoop-RL's biological utility.

| Benchmark | Primary source | Release status |
| --- | --- | --- |
| MoleculeNet HIV / NCI DTP | Wu et al., Chemical Science 2018, DOI [10.1039/C7SC02664A](https://doi.org/10.1039/C7SC02664A) | Frozen 1,200-molecule replay derivative with genuine structures/fingerprints |
| TDC HTS HIV | [Task and license documentation](https://tdcommons.ai/single_pred_tasks/hts/#hiv) | CC BY 4.0 source declaration recorded with attribution and transformations |
| LIT-PCBA | Tran-Nguyen et al., JCIM 2020, DOI [10.1021/acs.jcim.0c00155](https://doi.org/10.1021/acs.jcim.0c00155) | Research option only; raw redistribution rights remain unestablished |
| Tox21 | MoleculeNet / [TDC toxicity tasks](https://tdcommons.ai/single_pred_tasks/tox/) | Not included; file-level rights and missing-endpoint handling require review |

## Preserved HIV preparation record

The DeepChem mirror source has 41,127 rows and SHA256
`9ffa7fe57dc86c342627ee1d5255e937e2ab812393c73c4d16c697022f6e1d22`.
Seven invalid SMILES were excluded, leaving 41,120 valid rows. Canonical duplicate
and conflicting-label checks found none under the documented rules. Sampling
used `random.Random(20261103).sample` without activity stratification to select
1,200 rows. These counts describe that exact downloaded file, not a paper's
different count. The original TDC Dataverse request returned HTTP 403; the
DeepChem mirror was actually downloaded. Those historical access records remain
unchanged.

Morgan radius-2 fingerprints (1,024 bits) and Murcko scaffolds derive from genuine
structures, without activity as a feature. Source identifiers are original
zero-based CSV rows, not invented NSC numbers. NCI CA and CM are positive; CI is
negative under MoleculeNet's assay semantics. This is not clinical efficacy.

HIV initial seed labels are sampled uniformly without consulting labels and may
contain a single class. Synthetic seeds use a disclosed oracle intervention for
stratification. Seeds are preexisting sunk cost, common across matched policies
and excluded from new hits. Cost, capacity, delay and missingness remain simulated.

## Distinct evaluation questions

Sequential replay shares the pool, initial labels, feature/classifier contract,
budget, delay and capacity across fresh independent policies. Ten paired seeds
(0–9) compare five policies, retaining all public events. Initialization
variability within one assay is not ten independent biological replications.

The separate predictor audit uses a custom whole-scaffold hash split with seed
42: 960 train / 240 test, 36 / 6 actives and no shared scaffold. Train-only scaling
and logistic fitting yielded weak AUROC about 0.5563 and AP about 0.03266. It is
not the official MoleculeNet/TDC leaderboard split. Evaluator labels/models never
enter policy observations. See [evaluation](EVALUATION.md) for the exact protocol.

Q-learning and contextual bandit each trained on 160 synthetic episodes, seeds
10000–10159. Frozen checkpoints retain actual returns, values, counts and hashes.
Recorded HIV evaluation used Greedy fallback for 300/300 requests per learned
controller. Equality with Greedy does not demonstrate successful learned transfer.
No new training, reward tuning, seed cherry-picking or benchmark overwrite is part
of the English/persistence release.

## Future data ingestion boundary

For any future LIT-PCBA work, retain per-target active/inactive semantics,
release/hash, PubChem AID/SID and endpoints. Check canonical collisions and label
conflicts, distinguish target-family transfer from within-target replay and
scaffold evaluation, and establish redistribution permission before bundling raw
files. No such new dataset is included now. Code, dataset and paper licenses are
distinct; see [third-party notices](../THIRD_PARTY_NOTICES.md).
