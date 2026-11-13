# LR-SC1 owner report: stop at the native evaluator readiness gate

Decision: **NO_GO_NATIVE_EVALUATOR_READINESS**. No agent comparison ran.
The owner authorized progression only through passed gates and required a stop
after failure without repeated experiments. This report preserves that outcome.
Final return/cleanup, resource and main-delivery identities are recorded in
`docs/evidence/lr-sc1-20261113-v1/` and the private account delivery receipt.

## What was completed

- Opened a fresh 128 CPU-hour / 96 allocated GPU-hour account, separate from all
  closed accounts. Start: 13 November 2026, 16:03:03 UTC. Deadline: 27 November
  2026, 16:03:03 UTC / 23:03:03 Bangkok. The failed gate ends research early;
  the unused allowance does not authorize another study.
- Reviewed close work, including Rules to Tools. Gate 0 passed only for a bounded
  empirical extension: automatic scientific-check construction versus competent
  generic generated tests under equal total caps. Algorithmic novelty remains
  unproven. The detailed review is `LR_SC1_GATE0_REVIEW_20261113.md`.
- Received official SciCode data and code, pinned versions, constructed agent-safe
  views and fixed six validation main-problem IDs without model-based selection.
- Received the official numeric file: 1,049,345,865 bytes, SHA256
  `48b0272a88b17dbd29777c217e1b4fb2b019b92e11cc2add847409db9541b890`.
- Verified exact transferred bytes on dr-train. A wall-stop canary passed.
  Qualification used a one-CPU quota, 4 GiB memory, no network, read-only container
  root and unprivileged task ownership. No host permission/configuration changes.
- Executed native reference checks on six selected validation main problems:
  **70, 44, 49, 7, 19, 10**, containing **29 subproblems**.

## Actual results and cause boundaries

| Technical attempt | Native checks passed | Entire main references passed | Remaining failures |
| --- | ---: | ---: | --- |
| Initial adapter | 26/29 | 4/6 | 70.6, 70.8, 10.7 |
| One permitted source-supported repair | 28/29 | 5/6 | 70.8 |

The missing `scicode.compare` package in the first adapter was our implementation
omission. Copying the unchanged upstream comparator corrected 70.6 and 10.7.
Both original outcomes remain retained. These two technical attempts are not
independent samples or agent experiments.

The unchanged native assertion for reference 70.8 still failed. Its program AST
matches the program reconstructed using the official assembly helper. The cause
is unresolved across the reference, numeric target and environment; it is not
proven to be a universal benchmark defect. No third attempt or environment search
was performed.

All **65/65 test main problems** had their expected fixture groups present.
This is asset coverage, not proof of native scoreability. The planned minimum
50-task qualified evaluation cohort was **not established**. Inspected upstream
code also skips 13.6, 62.1 and 76.3 while retaining a full substep denominator;
this was recorded without changing assertions or scoring definitions.

## What did not run

| Item | Status |
| --- | --- |
| Qwen model download | NOT_RUN; zero new model bytes |
| Agent-model inference / GPU allocation | NOT_RUN; zero calls / zero GPU-hours |
| Fixed development agent comparisons | NOT_RUN |
| Frozen evaluation protocol and final matrix | NOT_RUN |
| Up to 520 planned agent episodes | 0 executed |
| Primary effect and uncertainty | NOT_ESTIMABLE, not zero |
| New scientific-contract workbench plugin | NOT_IMPLEMENTED after failed admission |
| User / independent expert / clinical validation | NOT_RUN |
| Public deployment or journal submission | NOT_RUN |

The previously delivered local EN/TH molecular workflow and every historical
positive/negative result remain intact. No mock, prior model case or native
reference check is substituted for a comparative agent outcome. Original
final16, private CF1 rows and hidden outcomes remain closed.

## Manuscript and publication assessment

The editable English technical manuscript is
`docs/07_publication/LR_SC1_SCICODE_ADMISSION_MANUSCRIPT_EN_20261113.md`, with a PDF
and a vector execution-status figure. It reports the actual admission work and
the missing agent evidence. It is an admission report, not a completed efficacy
paper. Empirical Software Engineering submission readiness is **NO_GO**.

The journal scope is relevant to a future completed empirical study. Its regular
subscription option has no APC according to the publisher, but publication cost
does not address the missing results:
https://link.springer.com/journal/10664/how-to-publish-with-us .

## Owner decision after closeout

No further research is activated. If the owner wishes to continue, the next
decision is whether to authorize a narrowly bounded qualification review of the
existing 70.8 reference/target/environment mismatch and upstream denominator
behavior. A new decision must define any changed evaluator/version and a new
resource account before another numerical attempt. Do not silently replace
SciCode, remove the difficult validation case, weaken a tolerance, or spend the
remaining nominal allowance on another method/model search.

The current objective's approved stop branch is fulfilled by evidence return,
honest reporting, exact owned cleanup, preservation checks and main delivery.
The larger comparative research and product-plugin objectives remain unachieved.
