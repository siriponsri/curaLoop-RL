# Molecular Studio frontend acceptance

Final implementation: source-v8. Actual screenshots/acceptance: browser-v7.
Review history and deviations are preserved in the
[checkpoint report](../../06_execution/FRONTEND_CHECKPOINT_20261106.md).

| Packet | Meaning |
| --- | --- |
| [Build results](build-source-v8/results.json) | Typecheck/lint/21tests/production build; [effective inputs](build-source-v8/effective-build-inputs.json) include the actual generated lock |
| [Browser result](browser-final-v7/browser-result.json) |16 positive axe audits,23 captures,3 fresh asynchronous/recovery/comparison paths |
| [C checks](workspace-checks-v4.json) |13 checks,5 real cached metadata dispositions,11 actual OS stdio responses |
| [Reviews](INDEPENDENT_REVIEWS.md) | Independent screenshot scores7→8/10 and fresh functional UX walkthrough |
| [Final motion](motion-final-v3/results.json) | Software-rendered20sec film; [process observation](motion-final-v3/render-processes.json), decoded frames and render logs |
| [Artifact identities](delivery-artifact-pins-v1.json) | Rebuilt dist, additive view, screenshots, film, manual and editable composition bytes |
| [Retained accounting](terminal-accounting-v4.json) |18.75 cumulative CPU-hours reserved; all39 jobs terminal, no reset |
| [Complete return](complete-return-verified-v2.json) | Every owned regular file locally reread and hash-verified; symlinks recorded separately |
| [Scoped cleanup](scoped-delete-v2.json) / [fresh absence](fresh-absence-v2.json) | Deletion only after complete return and a second local reread |

All failed process attempts and reconciliations remain alongside these final
results. Generic process PASS means supervision/payload exit succeeded; it does
not establish CPU-only compliance for the earlier HyperFrames auto-GPU attempt.
See the explicit resource deviation in the checkpoint report. Only motion-v3 is
the delivered final film. No new scientific-source call or final-outcome access
was released. Scientific readiness remains NOT_READY.

Full private return:
`.local/lrbc-ui-20261106-v1/remote-return/full-v1/`.
`ui-full-return-manifest-v2.json` maps the final original Linux paths to numbered
objects in the base full-v1/files and additive full-v2/files folders, retaining mode/directory/symlink identity without Windows case/name
collisions. Archives and the exact manifest are retained privately. Three
pre-existing OS-Python links are references only; host software is not deleted.
