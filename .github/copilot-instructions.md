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
- Two CDN dependencies are permitted and required:
  - **Chart.js** (`cdn.jsdelivr.net/npm/chart.js`) — all chart visualisations
  - **SheetJS** (`cdn.sheetjs.com/xlsx`) — client-side Excel (.xlsx) parsing
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
