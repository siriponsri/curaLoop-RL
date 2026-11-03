# Third-party notices

## Historical HIV benchmark data (separate from MIT code)

Attribution: NCI Developmental Therapeutics Program (DTP) AIDS Antiviral Screen; Zhenqin Wu et al., *MoleculeNet: a benchmark for molecular machine learning*, Chemical Science 9 (2018), 513–530, DOI https://doi.org/10.1039/C7SC02664A; DeepChem contributors; Therapeutics Data Commons (TDC), Kexin Huang et al., NeurIPS Datasets & Benchmarks 2021.

Dataset license recorded as **Creative Commons Attribution 4.0 International**, based on the explicit HIV dataset license statement at https://tdcommons.ai/single_pred_tasks/hts/#hiv, accessed 2026-11-03. License: https://creativecommons.org/licenses/by/4.0/ . The license allows sharing and adaptation with attribution and an indication of changes; it does not imply endorsement. This records the source's license declaration, not a legal certification of all upstream rights.

Source downloaded from https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/HIV.csv . Original public screening data context: https://wiki.nci.nih.gov/spaces/NCIDTPdata/pages/158204006/AIDS+Antiviral+Screen+Data . Source SHA256 and preprocessing evidence are in `src/curaloop/resources/hiv_manifest.json`.

Changes: invalid structures excluded (7); canonical duplicate and conflicting-label checks; label-blind deterministic 1,200-record subset; canonical isomeric SMILES, Morgan 1024-bit radius-2 fingerprints and Murcko scaffolds calculated with RDKit. CA and CM remain positive and CI negative as defined by MoleculeNet. Original full raw CSV is not included. Source identifiers in this derivative are original zero-based CSV row indices, **not invented NSC numbers**.

Source benchmark paper license and dataset license are distinct. No paper PDF is distributed here. The reference pack's unverified literature entries are preserved as references and are not newly certified by this implementation.

## Software

NumPy, pandas, scikit-learn, Streamlit, Altair, Gymnasium, pytest and optional RDKit retain their respective upstream licenses. They are installed as dependencies and not copied into source archives.

## Logo

`assets/curaloop-logo.png` is an original AI-assisted logo generated for this project using the built-in image-generation tool on 2026-11-03. It is a raster PNG with transparency, not an SVG or trademark clearance. Its generation prompt and use are documented in `docs/BRAND.md`; no GPO identity, emblem or endorsement is used.

## Thai font

Noto Sans Thai, Google/Noto contributors, is redistributed under the SIL Open Font License 1.1. Original font and copyright/license notice are in `assets/fonts/NotoSansThai.ttf` and `assets/fonts/OFL.txt`. Source: https://github.com/google/fonts/tree/main/ofl/notosansthai . The font is embedded locally so Thai labels render without an external font server.
