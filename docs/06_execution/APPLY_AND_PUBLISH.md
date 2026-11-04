# Apply the package to the existing repository

## Choose the checkout

Use the folder containing `.git` whose `origin` is `siriponsri/curaLoop-RL`. The folder name alone, such as `curaloop-rl` or `curaloop-rl-git`, does not determine which is correct. Inspect `git rev-parse --show-toplevel`, `git remote get-url origin` and `git status --short`. Keep owner changes safe before applying anything.

The package's `Apply-Documentation.py` checks the origin, a clean working tree and the expected base commit. It backs up existing changed files outside the repository and copies only the listed documentation/support changes. It never deletes the checkout, modifies `.git`, commits or pushes. If main has advanced, integrate the documented diff against the new head rather than bypassing the check blindly.

## Apply and inspect

From the extracted package root, use the installed Python (no PowerShell execution-policy change is needed):

```powershell
py -3.12 .\Apply-Documentation.py --repository 'C:\path\to\your\actual\clone'
```

The path above is an instruction argument to replace with the verified checkout, not a claim about the owner's current filesystem. Add `--dry-run` to check before copying. An optional `Apply-Documentation.ps1` alternative is also supplied. The script requires a clone matching the source checkpoint. It prints the backup location and changed-file count. Inspect the diff, read `START_HERE.md`, and run the included documentation validator using the project's Python environment. Use the CRLF-aware whitespace check below because the byte-preserved original catalogue in the archive retains its original line endings.

## Normal main update

After review, use the normal repository workflow:

```powershell
git status --short
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check
git add README.md GOAL.md PLAN.md PRODUCT.md DESIGN.md START_WINDOWS.md THIRD_PARTY_NOTICES.md HANDOFF_TO_CODEX.md AGENTS.md START_HERE.md ACADEMIC_BUSINESS_MASTERPLAN.md CONTRIBUTING.md SECURITY.md CHANGELOG.md .gitignore docs papers prompts research tools
git diff --cached --stat
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check
git commit -m "docs: define academic study and R&D pilot programme"
git push origin main
```

Run these only from the verified main checkout after checking the staged diff. The package does not execute them. A normal push updates files while preserving Git ancestry. Do not use `--force`, replace `.git`, or publish private reading-room PDFs. If a push is rejected because remote main advanced, fetch and integrate the new commits, resolve conflicts and validate the resulting state before pushing normally.

The `cr-at-eol` option applies to that command only; it does not change global Git settings or normalize the archive. It accepts carriage returns at CRLF line endings while retaining the other whitespace checks. The staged check covers newly added files as well as replacements.

## Package boundaries

`repository/` is the public-ready payload. `reading_room_private/` contains requested public reading copies and is outside that payload. The full ZIP itself is not a file to commit to the repository. The smaller documentation overlay contains only the changed files and apply support, making it the preferred update route. Historical requirements, raw evidence, original screenshots, model resources and application files remain preserved.

## Updating an already applied v1

The v2 overlay remains a diff against the original inspected source checkpoint. If v1 is already applied, retain and commit/review that work, then merge the v2 document changes with Git/Codex. The apply helper intentionally rejects a dirty tree or a different base; do not discard owner work or bypass those checks just to make the script run. Review `docs/07_audit/REVIEW_CHANGELOG.md` for the evidence-driven changes.
