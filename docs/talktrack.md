# 🎯 RVTools Visualiser — End-to-End DevOps Talk Track

> **From idea to production in minutes — powered by GitHub & Copilot.**

---

## 🗺️ The Journey at a Glance

```
💡 Idea  →  🤖 Code with Copilot  →  🌿 Branch  →  📋 PR  →  🔍 Review  →  ✅ Merge  →  🚀 Deploy  →  🌐 Live
```

---

## Step 1 — 💡 Identify the Change

> *"It all starts with a need — a bug report, a feature request, or an improvement."*

- GitHub **Issue Templates** provide structured intake forms
- 🐛 **Bug reports** capture browser, steps to reproduce, and severity
- ✨ **Feature requests** capture the problem, proposed solution, and priority
- Issues are tracked, labelled, and linked to PRs for full traceability

**🎤 Demo point:** *"Go to Issues → New Issue — notice the structured templates, not a blank text box."*

---

## Step 2 — 🤖 Code with GitHub Copilot

> *"Instead of writing every line from scratch, I collaborate with an AI pair programmer."*

- **GitHub Copilot CLI** assists directly in the terminal — no IDE required
- Copilot understands the full codebase context and makes surgical changes
- It suggests code, explains logic, runs tests, and even drives the deploy
- Every commit includes a `Co-authored-by: Copilot` trailer for attribution

**🎤 Demo point:** *"Watch me describe the change in natural language and Copilot implements it — including edge cases I hadn't considered."*

### Recent features built with Copilot

- **Multi-tab RVTools parsing** — `vInfo` plus optional `vDatastore`, `vSnapshot`, `vHost`, `vDisk`, `vNetwork`, `vHealth`, `vCluster`, `vCPU`, `vMemory`. Each tab unlocks a deeper dashboard.
- **Eight infrastructure dashboards** — Environment Topology, Host Capacity, Storage, Disk, Network, Resource Allocation, Snapshot Health, and Environment Health, every one collapsible and self-hiding when its tab is missing.
- **Migration Readiness model** — renamed waves to **Ready Now / Light Prep / Modernise / Remediate** with a Risk Quadrant scatter plot and per-VM migration notes, plus an Azure Migrate signpost so users know where to go for proper assessment.
- **Indicative Azure VM Family Fit chart** — coarse first-look bucketing of VMs into D-/E-/F-/M-series-style families.
- **Demo mode UX** — the app boots in demo mode with a synthetic dataset, a vInfo Only / Full Export toggle, and a downloadable sample `.xlsx` for users testing the upload flow.
- **Privacy-first messaging** — a permanent "your data stays in your browser" badge on the upload area; nothing ever leaves the client.
- **Friendly file errors** — wrong extension, no `vInfo`, empty sheet, no VMs after parsing — every common failure has a helpful hint.
- **Pagination across all ten tables** — single shared helper, 25 rows per page, consistent look and feel.
- **Offline HTML snapshot ("Save Locally")** — self-contained report with charts converted to images and an amber OFFLINE SNAPSHOT banner.
- **Connected-dots background with parallax** — themed for both light and dark modes.
- **Azure SWA deployment pipeline** — GitHub Actions with SWA CLI and the staging-folder workaround.

---

## Step 3 — 🌿 Create a Feature Branch

> *"We never push directly to production. Every change starts on its own branch."*

```bash
git checkout -b feature/my-new-feature
```

- **GitHub Flow** branching — simple and effective
- `main` is always deployable
- Feature branches are short-lived and focused

**🎤 Demo point:** *"Show the branch naming convention — `feature/`, `fix/`, `docs/` prefixes."*

---

## Step 4 — 📋 Open a Pull Request

> *"A PR is a conversation about the change, not just a merge button."*

- **PR template** with a checklist: description, testing, screenshots
- Linked to the original issue for traceability
- **Automated HTML validation** runs on every PR via GitHub Actions

**🎤 Demo point:** *"Open a PR and show the template, the automated checks, and the diff view."*

---

## Step 5 — 🔍 Review & Validate

> *"Even with AI writing the code, review is essential."*

- The HTML validation workflow checks:
  - DOCTYPE presence and essential HTML tags
  - Tag balance (with a threshold for the JS template strings used by the HTML-export builder)
  - Common smells (`TODO`, `console.log`)
- Review the diff, test locally, then approve

**🎤 Demo point:** *"Show the Actions tab — green check means validation passed."*

---

## Step 6 — ✅ Merge to Main

> *"One click to merge, and the deployment pipeline kicks off automatically."*

- Squash merge keeps history clean
- Branch is auto-deleted after merge
- The deploy workflow triggers immediately

---

## Step 7 — 🚀 Deploy to Azure

> *"From merge to live in under a minute."*

```
Merge → GitHub Actions → SWA CLI deploy → rvtoolsviz.djtools.co.nz
```

The deployment pipeline:
1. **Checkout** the repo on a GitHub-hosted `ubuntu-latest` runner
2. **Copy** `index.html` to a `deploy-staging/` folder
3. **Deploy** via `npx @azure/static-web-apps-cli deploy`
4. **Verify** with an HTTP request to the custom domain

**🎤 Demo point:** *"Go to Actions → show the deploy workflow running → refresh the live site to see the change."*

---

## What's New in v1.2.0-beta

The latest release lands a full **save / resume / share** layer on top of the existing dashboard, without giving up the privacy-first model. Talk-track demo flow:

1. **Drop in a real RVTools file** → web-worker parsing keeps the UI snappy on large estates; magic-byte detection catches mislabelled files politely.
2. **Build a workspace** — make a couple of sizing groups, mark some VMs out-of-scope, add a tag rule.
3. **💾 Save scenario (.rvz)** → a real ZIP containing the full RVTools workbook + your customisations. Shows a privacy modal because the file holds your inventory.
4. **Reload the page** → autosave silently restores the workspace (matched on the SHA-256 fingerprint of the source bytes).
5. **Drop the .rvz back in** → full data + workspace round-trip from a single file.
6. **📋 Save workspace (.json)** → two flavours:
   - **Full workspace** — re-applies on the same dataset.
   - **Rules template** — just rules + plan settings, safe to share with other customers (no inventory data).
7. **Apply a workspace JSON to a *different* RVTools file** → reconciliation modal: matched/unmatched/group/rule counts; unmatched IDs are *preserved* on the workspace for round-trip back.
8. **Open the app in two tabs** → the older tab shows a top-of-page amber banner: *"Autosave paused — another tab is editing this workspace."*

**🎤 Talk track quote:** *"This isn't an upload tool — it's a single HTML file that runs entirely in your browser. Your RVTools data never leaves your machine, but you still get save, resume, and share — backed by IndexedDB, localStorage, and BroadcastChannel. No server, no account, no SaaS subscription."*

---

---

## Step 8 — 🌐 Live!

> *"The change is live at [rvtoolsviz.djtools.co.nz](https://rvtoolsviz.djtools.co.nz/) — users see it immediately."*

- Azure Static Web Apps handles CDN, HTTPS, and the custom domain
- Free tier is sufficient for this use case
- No server to manage, no infrastructure to maintain

---

## 🎬 Demo Script — The App Itself

### 1. First impression (1 min)

1. Open the live app — demo mode is on by default, so the dashboard is already populated.
2. Point out the **🔒 Private — your data stays in your browser** badge above the drop zone.
3. Click **vInfo Only** then **Full Export** in the demo bar — the infrastructure dashboards unlock when you go to full.

### 2. Upload your own (1 min)

1. Click the *Download a sample RVTools file ↓* link, or drop your own `.xlsx`.
2. Watch the file-info pill in the hero appear, the demo bar disappear, and every dashboard repopulate with real data.
3. *(Optional)* break it on purpose: drop a non-Excel file — show the friendly error.

### 3. Explore (3 min)

1. Scroll through the **Overview** section — six metric cards, exec summary text, the four-dropdown filter bar, and six analytics charts. Demo a filter (e.g. Datacenter) so customers see Overview reshape live while the rest of the page stays put.
2. Open the **Infrastructure Analysis** sections — Topology, Host Capacity, Storage, Disk, Network, Resource Allocation, Snapshot Health, Environment Health.
3. Highlight the **Indicative Azure VM Family Fit** chart inside Environment Topology.

### 4. Migrate (2 min)

1. Open **Migration Readiness** → show the Risk Quadrant scatter.
2. Hover a few points — show the per-VM tooltip.
3. Mention the Azure Migrate signpost — this is an indicator, not a replacement.
4. Scroll into **Readiness Groups** and search/filter to find a specific VM.

### 5. Filter & paginate (1 min)

1. Pick a datacenter and a readiness group from the filters — every chart and every table updates.
2. Page through any of the tables (25 rows per page, consistent across all of them).

### 6. Export (1 min)

1. Download a CSV of readiness recommendations.
2. Click **Save Locally** to export the offline HTML snapshot.
3. Open the snapshot — show the amber OFFLINE banner, charts preserved as images, no internet required.

### 7. Theme (30 sec)

1. Toggle dark mode — show the connected-dots background change.
2. Note the parallax effect when scrolling.

---

## 💬 Wrap Up

> *"What started as a simple idea became a production-ready visualisation tool with multi-tab parsing, eight infrastructure dashboards, and a migration readiness model. Copilot CLI handled everything from writing the parsers to deploying to Azure. The takeaway: AI-assisted development isn't just about writing code faster — it's about shipping complete, polished solutions."*

### Links

- [GitHub Copilot CLI](https://github.com/features/copilot/cli/)
- [Azure Static Web Apps](https://azure.microsoft.com/products/app-service/static)
- [RVTools (Dell)](https://www.dell.com/support/kbdoc/en-nz/000325532/rvtools)
- [Azure Migrate](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)
