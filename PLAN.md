# Implementation / evidence map

แผนแบบตรวจหลักฐานเป็นเป้าหมาย ไม่ใช้ deadline หรือ future extension มาทดแทน component ที่ต้องส่งมอบ

| Goal | Implementation | Evidence |
|---|---|---|
| Local installable application | src package + Streamlit + pinned dependencies + Windows launcher | wheel build / isolated environment / AppTest |
| Correct retrospective engine | private TruthStore, immutable events, reservation/settlement, capacity/delay/missingness | simulator + stress + leakage tests |
| Real assay dataset | 1200 real HIV molecules from 41127-row source, RDKit validation, hashes, attribution | hiv_manifest + preparation script + source/rights evidence |
| Reproducible comparison | fresh independent runs, common seed labels/budget/features | baseline + controller comparisons / JSON and CSV |
| Actual adaptive training | tabular Q-learning and contextual bandit, 160 episodes each; Gymnasium API | checkpoint values/counts/returns/hash + environment/training tests |
| Honest external evaluation | 10 paired HIV seeds / 5 policies; separate scaffold predictor audit | benchmark files + summary + limitations |
| Complete user workflow | four views, run controls, compare, export, resume, Learning/Benchmark Lab | AppTest / actual Chromium screenshots + downloads |
| Reviewable transfer | Git commits, source ZIP, bundle, HANDOFF_TO_CODEX | exact commit identity + clean status + archive CRC |

Measured limitations are research outcomes: uncalibrated logistic probabilities, sparse positives, controller unseen-state fallback and weak held-out performance cannot be repaired by changing labels, cherry-picking seeds or relabeling a simulator as a validated twin. LIT-PCBA/Tox21 rights and cross-target prospective validation remain external research needs, explicitly outside achieved evidence.
