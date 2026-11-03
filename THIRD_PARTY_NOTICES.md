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

Noto Sans Thai, Google/Noto contributors, is redistributed under the SIL Open Font License 1.1. Original font and copyright/license notice are in `assets/fonts/NotoSansThai.ttf` and `assets/fonts/OFL.txt`. Source: https://github.com/google/fonts/tree/main/ofl/notosansthai . The font is embedded locally for offline typography. The current interface is English; historical captures and the original licensed asset remain unchanged.


## Local web UI v0.2 references and attribution

Reviewed public repository source/license files on 2026-11-03 before implementation. The app shell is original, informed by the dashboard reference; no complete CRM/auth/template project or proprietary component was imported. Full fetched license texts and pinned commits are retained in `docs/evidence/web-v2/licenses/`.

| Source | Reviewed commit | License | Actual use |
| --- | --- | --- | --- |
| shadcn-ui/ui | `4aaea19d9cff3e0908e12a8c1d504b8c5ec34610` | MIT | `apps/v4/registry/new-york-v4/ui/button.tsx` composition adapted in `frontend/src/components/ui/button.tsx`; custom CSS and local Radix Dialog/Badge composition |
| shadcndashboard/shadcndashboard | `386235c3199168fa743db593d7acf014a40f1ca1` | MIT | Dashboard shell/navigation design reference only; no source modules copied. Requested attribution: [shadcndashboard](https://shadcndashboard.dev/), also linked in the app footer |
| tremorlabs/tremor | `ca4d588f47820ff3d514d37fa4ee08a4222dec11` | Apache-2.0 | Reviewed only; no copied code or package |
| xyflow/xyflow | `1bc405cd113618c17fd181b931a9fe573bec9fee` | MIT | Reviewed only; no React Flow dependency. Workflow is original state-driven React links |
| recharts/recharts | `8b7111daedc43ddcffc407153178126009cfc24e` | MIT | Official npm Recharts 3.10.1; original chart definitions over real reports |

The exact installed dependency versions are locked in `frontend/package-lock.json`. React 19.3.1, Radix primitives, Vite, Tailwind, Lucide, Recharts and their bundled dependencies retain upstream licenses. Full runtime dependency notices are collected in `frontend/THIRD_PARTY_LICENSES.txt`; the package/version/license inventory is under the evidence licenses directory. FastAPI, Uvicorn and RDKit are locally installed Python dependencies, not copied third-party application source. Existing MIT project code, data CC BY attribution, original logo and Noto font terms remain separate.

Copies: `frontend/SHADCN-LICENSE.txt`, `DASHBOARD-LICENSE.txt`, `RECHARTS-LICENSE.txt`, `public/fonts/OFL.txt`. The existing PNG logo and font are reused unchanged, with no new company marks or generated scientific structures.

Dependency check: `npm audit --omit=dev --json` reported zero production advisories at audit time. Full audit reported 11 moderate development-tool advisories involving minimatch/ESLint; no incompatible automatic downgrade/override was applied. This is a point-in-time dependency scan, not a security certification. ESLint 9 support migration and the build-size warning are recorded technical debt.


## Local POC v0.3 dependency verification

The original v0.2 dependency scan above is historical. Current release audit
results are in `docs/RELEASE_VERIFICATION.md` and `docs/evidence/poc-v0.3/`.
Pillow was updated from 12.3.0 to 13.0.0, which satisfies Streamlit/RDKit requirements
and resolves the entries reported by the locked Python audit. See the upstream
[Pillow advisory](https://github.com/advisories/GHSA-78g4-xqwv-q3g8).

Frontend development tooling uses compatible ESLint 10/TypeScript ESLint packages
with a narrowly pinned patched minimatch 11.0.1 override. Upstream ESLint's current
dependency range still selected the affected major; the override is an actual
dependency replacement, not an audit suppression. Real lint/typecheck/unit/build
checks verify this project's usage. See the [minimatch advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249)
and [ESLint migration notes](https://eslint.org/docs/latest/use/migrate-to-10.0.0).
Original license/copyright texts and runtime assets are preserved.
