# Dataset, Oracle Isolation & Leakage Playbook

## Phase I: synthetic fixture is for engineering validation, NOT pharmaceutical evidence

Make a deterministic fixed synthetic dataset (e.g. 240 candidate IDs, 12 numeric features and 0/1 artificial outcome) with a recorded generator seed. It must be obvious these are *fictional labels* and a *toy data distribution*; no invented SMILES are necessary for the first smoke test. If SMILES displayed, use an RDKit-validated set of public/example structures and independently synthetic labels, with explicit source and appropriate licenses. Synthetic signal should be learnable but not trivially encoded as an exposed label column.

**Controlled hidden truth:** `TruthStore[candidate_id] -> label` lives only in the simulator's private environment/oracle. The public observation can include `candidate_id`, allowed features, metadata, *previously delivered* labelled results, queued IDs, budget and simulation time. Avoid passing a whole `pandas.DataFrame` with labels to a policy and merely asking it not to look.

**Cold start:** greedy/uncertainty need a predictor trained on *initial visible seed labels*. Construct one common initial seed set, e.g., 12 observations with both positive and negative classes in the synthetic demo. Record how it was selected and whether its cost is part of budget or is a common historic sunk cost. For public benchmarks, do **not cherry-pick** seed labels to ensure positives without reporting the oracle intervention. If only one class exists, document a valid fallback (e.g., uniform ranking) and label the method accordingly. Never silently reveal labels to warm-start a model.

**Policy separation contract:** `policy.propose(observation) -> selected IDs` cannot import the private oracle, perform disk reads of original labels, use API calls or inspect `run_manifest` hidden fields. A stronger benchmark uses the policy in a restricted process that has only observation JSON. Tests intentionally plant a fake hidden label / row order to catch implicit leakage.

## Phase II: actual public data

Preferred benchmark entry point: **LIT-PCBA** official source https://drugdesign.unistra.fr/LIT-PCBA/index.htm (15 target sets). Counts and packaging depend on the official dataset version/download and should be recorded from a downloaded release, not hardcoded from external summaries. **The data license/redistribution terms are not conclusively verified in this pack.** Before download/public sharing, read its site terms and citation, and keep raw files out of Git (`data/raw/` ignored).

- Preserve source page, dataset filename/version, access timestamp, sha256, target/assay ID, positive/negative definition and record identifiers.
- Parse SMILES with RDKit; reject invalid structures, salts/mixtures per documented rules. Record canonicalization and tautomer/stereochemical handling as versioned settings. Avoid mixing labels after collapsing duplicate canonical SMILES; report conflicts.
- Deduplicate within assay and cross-split for unique molecules; avoid leakage via identical InChIKey or close analogs when the evaluation purports to be scaffold-disjoint.
- Build **within-target** replay campaigns with genuinely hidden labels. For a *learned policy* trained across episodes, use **disjoint target families** for train/validation/test when making transfer claims. Don't present random scaffold split as strict target-level generalization.
- Keep TDC as a later optional loader: TDC's generic split defaults to random and offers scaffold splitting; benchmark-specific splits may be fixed. Select splits explicitly and record exact policy. https://tdcommons.ai/functions/data_split/
- Assay outcomes from different biological experiments are **not interchangeable**. A binary classification label is assay-specific; do not equate activity to potency, efficacy, ADMET or regulatory suitability.

## Three isolated information channels

1. `PUBLIC_FEATURES`: candidate identifiers, pre-assay known descriptors/fingerprints, chemistry metadata and non-private restrictions.
2. `REVEALED_RESULTS`: previous delivered assay labels with timestamps and policy-visible costs.
3. `PRIVATE_TRUTH`: full historical labels and counterfactual results retained by simulator only; never serialized into observations, model inputs or UI exports before reveal.

## Fair comparison protocol

Every comparator starts with the **same candidate pool**, **same common initial labeled set**, **same available features**, **same budget**, **same round length and capacity**, **same cost assumptions**, and **same label reveal timing**. Predictor type and training schedule should be matched, or the asymmetry explicitly declared. Tune baseline hyperparameters on a validation regime rather than leaving RL tuned and baselines weak. At least 10 common random seeds for engineering experiments; for scientific conclusions decide sample size and confidence method before analysis.

**Primary metric:** cumulative *delivered* active assay labels found at fixed spent cost; include AUC of hits vs cost. Secondary: time to k hits, hit recall where total positives are known, diversity of selected molecules, mean outcome delay, invalid actions and wall-clock compute. Show paired effect sizes with intervals. No claim of superiority from a single curated run.

## Defense tests

- Policy cannot import/access `TruthStore`; offer a test policy that attempts to read `label` and fails.
- Row-order shuffling or replacing private truth should not change first action before any label reveal (given fixed public observations).
- A delayed label changes policy state **only after** due event.
- Duplicate candidate requests fail or are idempotent consistently; never charge or count a label twice.
- Every accepted request has a unique ID and budget reservation; after restart, ledger reconciliation reconstructs spent/reserved/remaining exactly.
- Export redacts unrevealed labels and private truth. Replay with same seed/config/dataset hash is bitwise/eventwise deterministic where platform permits; document tolerated floating point differences.
- Train/test target exclusion checked programmatically before claiming meta-policy generalization.

## License and sharing

Code under an owner's chosen compatible license does **not** license third-party datasets or paper PDFs. The documentation links papers; the ZIP does not contain original articles. Commercial/organizational presentation also does not imply a reuse right. Store PDF notes/links in the repository, keep actual copies local unless redistribution is clearly permitted and attributed.
