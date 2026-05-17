# Copilot Instructions — DJ Tools Web App

## Project Overview
This is a **single-file HTML web application** (`index.html`). It runs as a static site hosted on Azure Static Web Apps with no server-side components, build tools, or dependencies.

## Architecture
- **Single file**: All HTML, CSS, and JavaScript live in `index.html`
- **No frameworks**: Pure vanilla HTML/CSS/JS — no React, Vue, npm, etc.
- **No build step**: The file deploys directly via SWA CLI
- **Static hosting**: Azure Static Web Apps (Free SKU)

## Git & Deployment Workflow
- **GitHub Flow**: Always create a feature branch → PR → merge to `main`
- **Branch naming**: Use prefixes like `feature/`, `fix/`, `docs/`, `chore/`
- **NEVER commit or push to `main` directly**. All work lands on a feature branch and merges via PR only with explicit user approval.
- **State the branch on every git action**: before running `git commit` / `git push`, print the current branch and explicitly confirm it is *not* `main`. Use a guard like:
  ```powershell
  $b = git branch --show-current
  if ($b -eq 'main') { Write-Host "ABORT: on main" -ForegroundColor Red; exit 1 }
  Write-Host "Branch: $b (NOT main)" -ForegroundColor Green
  ```
  Always push with the branch name spelled out: `git push origin <branch>` (never bare `git push` when intent matters).
- **In chat**, lead any commit/push action with a one-liner like *"Pushing to `feature/xxx` (NOT main)"* so the user can intervene before the action runs.
- **CI/CD**: Push to `main` triggers `.github/workflows/deploy.yml` (GitHub-hosted `ubuntu-latest` runner) which deploys `index.html` to Azure Static Web Apps via `@azure/static-web-apps-cli`. The deployment token lives in the `production` GitHub Environment (branch-restricted to `main`).
- **Validation**: `.github/workflows/validate.yml` runs HTML structural checks on PRs touching `*.html`. It uses `pull_request` (not `pull_request_target`), so PRs from forks run with **no secret access**.
- **Pinning**: third-party actions are pinned to commit SHA — update the `# vX.Y.Z` comment beside each `@<sha>` when bumping.
- **OneDrive workaround**: Use `git -c gc.auto=0 push` to avoid gc/OneDrive file-locking conflicts

## Version Numbering
- Format: `v1.X.X-beta`
- Update version in: footer in index.html, any generator metadata, README badge
- Bump version for feature changes, not doc-only changes

## Code Conventions
- Keep everything in the single `index.html` file
- Minimal code comments — only where clarification is needed
- CSS uses custom properties (variables) for theming (light/dark mode)
- JavaScript uses modern ES6+ (const/let, arrow functions, template literals, async/await)
- Three CDN dependencies are permitted and required:
  - **Chart.js** (`cdn.jsdelivr.net/npm/chart.js`) — all chart visualisations
  - **SheetJS** (`cdn.sheetjs.com/xlsx`) — client-side Excel (.xlsx) parsing
  - **JSZip** (`cdnjs.cloudflare.com/ajax/libs/jszip`) — `.rvz` scenario container (real ZIP read/write)
- All three are pinned with SRI hashes
- No other external CDN dependencies should be added without good reason

## Documentation
- `README.md` — Project overview (stays in repo root)
- `docs/SPEC.md` — Full application specification
- `docs/howitworks.md` — Technical deep-dive
- `docs/talktrack.md` — Demo talk track

## Documentation Updates
Any feature added, changed, or removed requires updating these docs before merging:
- `README.md` — Features list, format references, how-to sections
- `docs/SPEC.md` — Full specification
- `docs/howitworks.md` — Technical deep-dive
- `docs/talktrack.md` — Demo talk track (version, recent features)

## Testing
- No automated unit tests — validation is manual + HTML structure validation in CI
- Hard refresh (`Ctrl+Shift+R`) after deployments to bypass browser cache
