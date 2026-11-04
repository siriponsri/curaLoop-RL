# Materials and methods: implemented historical pilot

## Dataset and initialization

The pilot uses the frozen `curaloop-hiv-1.0.0` derivative described in the resource manifest. The downloaded DeepChem HIV source contained 41,127 rows; seven invalid SMILES were removed under the documented preparation procedure. A label-blind random sample of 1,200 valid rows was retained. Canonical SMILES, Morgan radius-2 fingerprints with 1,024 bits and nonchiral Murcko scaffold identifiers were derived with RDKit. Historical CA/CM labels were mapped to active and CI to inactive.

Each campaign began with 48 uniformly sampled labelled compounds, selected without inspecting activity. These labels were preexisting sunk information, excluded from new-hit counts and campaign cost. Ten seeds, 0-9, were paired across five independent policies. The candidate pool, initial labels and scenario constraints were common within a seed; results were not shared between policies.

## Predictors and policies

Greedy and margin-based Uncertainty used `StandardScaler -> LogisticRegression`, with liblinear, C=1 and a maximum of 500 iterations. Only initial and subsequently delivered Boolean labels were used for fitting. A one-class observed set caused a labelled Random fallback. Predicted probabilities were uncalibrated. Greedy selected high predicted activity; Uncertainty used proximity to 0.5 as a margin score.

Frozen tabular Q-learning and contextual-bandit controllers selected among Random, Greedy and Uncertainty. Each controller had been trained on 160 synthetic episodes using seeds 10000-10159. The reward was newly delivered active hits minus 0.01 times newly settled assay cost. Their state lookup and explicit unseen-state Greedy fallback were retained during HIV evaluation. No HIV label was used for controller training.

## Scheduler and metrics

The recorded scenario used budget 30, unit assay cost, concurrent capacity 5 and a common delay of two simulated steps, with no jitter or missing outcomes. Accepted requests reserved cost once. Delivered outcomes settled cost once. Only unique newly delivered active results counted as new hits; seed labels, predictions and pending outcomes were excluded. The budget identity was spent plus reserved plus remaining equals total.

The recorded AUC-DB is the left-step integral of cumulative delivered hits against settled cost, carried to the configured budget and normalized by budget times the maximum affordable assay count. It is not AUROC or average precision. The historical comparisons summarize within-assay seed variation and include exploratory paired-bootstrap contrasts against Random.

## Separate predictor audit

A custom whole-scaffold hash split at seed 42 produced 960 training and 240 test molecules, containing 36 and six actives respectively and no shared Murcko scaffold. Scaling and fitting used training rows only. The evaluator's labels and fitted model were never passed to campaign policies. This is not an official MoleculeNet/TDC leaderboard reproduction.

## Evidence preservation

This documentation release reads existing artifacts and does not rerun or alter the pilot. Exact machine-readable settings, metrics and source identities remain in the original evidence folders. Software tests and browser verification are reported separately and do not validate chemical or operational performance.
