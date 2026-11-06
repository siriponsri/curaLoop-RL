# Molecular Studio and additive C Workspace

The screening app and C Workspace share the approved graphite, ivory and copper
visual language. Use EN/TH to change interface language without changing the
campaign or the original source values.

Start the main application with `Start-CuraLoop-Web.cmd` after the documented
installation. The committed `frontend/dist` contains the tested production build.
The main app's existing API/security/storage contracts are unchanged. The
checkpoint's special loopback `/workspace` mount was an isolated QA harness;
it is not a newly installed production route.

For C Workspace, open `docs/05_product/metadata-workspace-v2/workspace.html` from
a local checkout, or open `view-v2/workspace.html` in a new v2 tool export. The
view embeds its presentation assets and metadata. No live source or language
service is called. Original report, plan and preview files remain adjacent.
GitHub displays HTML source; download the folder or clone before opening it.

The v1 metadata/MCP tools remain available. To select the additive export wrapper,
use the same registered private source root and registry as the v1 guide:

```powershell
python -m curaloop_rd.mcp_v2 --source-root <registered-source-root> --registry <registry-json> --workspace <new-local-workspace> --font frontend/public/fonts/NotoSansThai.ttf
```

The paths in angle brackets must be the owner's actual registered local paths;
this example does not create rights, obtain source data or register a live client.
The font must retain its adjacent OFL.txt. The four typed tools and pinned stdio
transport are unchanged. Successful `local_export` adds a `workspace_v2` receipt.
It does not send a message or upload files to a team system.

Re-export validates the original v1 export, derives the expected view again,
and requires exact manifest, file inventory, size and hash agreement. A modified
view, coordinated copied-file/manifest tampering, extra file or symlinked view is
rejected. Preserve an altered folder as evidence and export to a fresh workspace
when investigating; do not patch the manifest to make verification pass.

The source ledger distinguishes absent, explicit null and present raw metadata.
Raw unit/type codes remain unconverted. “Not released” means molecular research
has not been qualified by this metadata report. It is not a clinical, commercial
or experimental approval.

[English manual](../manual/CuraLoop-RL-Molecular-Studio-Manual-EN-v2.pdf) ·
[Actual walkthrough](../media/molecular-studio-walkthrough.mp4) ·
[Acceptance and limits](../06_execution/FRONTEND_CHECKPOINT_20261106.md)
