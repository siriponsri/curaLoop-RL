# Implementation and acceptance plan

Base: `b16d2fb9ee56d03fdc6cf0628fc444670a433c43`, fetched from the original remote.
Working branch: `feat/english-durable-poc`. Exact progress is in
[CONTINUATION](docs/CONTINUATION.md); executed results are in
[release verification](docs/RELEASE_VERIFICATION.md).

| Work | Acceptance evidence |
| --- | --- |
| Restore source Git metadata without overwriting files | Root/remote/branch/status and original ancestry |
| Establish baseline on native Windows | Original Python/frontend suites and first-run setup |
| Convert current content to English | Seven routes, Streamlit, docs, legacy-locale regression |
| Durable local state | Pending/completed restart, revision CAS, interruption and corruption tests |
| Repair workflows and recovery UX | Real controls, saved runs/jobs, exports/resume and source-specific results |
| Compatible release tooling | Dependency audits, lint/typecheck, clean production build |
| Browser acceptance | Real localhost at 1440 and 390 px, keyboard/dialog/focus, no overflow |
| Preserve scientific evidence | Byte comparisons of protected resources and historical evidence |
| Deliver | English operator guide, source/build identity, reviewed coherent commits, normal push |

No scientific protocol, reward, seed selection, dataset or trained model changes
are planned. Historical evidence is retained in place. Installation is local to
the project; no machine-level execution-policy or administrator changes.
