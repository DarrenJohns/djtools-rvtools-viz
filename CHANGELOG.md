# Changelog

All notable changes to RVTools Visualiser are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [Semantic Versioning](https://semver.org/).

## [Unreleased] — SKU Recommender beta

A new "what would this look like in Azure?" tier on top of the existing readiness work.

### Added

- **🎯 Azure SKU Recommender (beta).** Per-VM Azure SKU recommendations driven by live capability + retail-pricing data for AU East and NZ North.
  - **Sizing groups** with Balanced / Cost / Rightsized optimisation modes; pin groups to keep them top-of-rail; rail or 4-column board view (persisted in `localStorage`).
  - **Live SKU catalog** — 945+ B/D/E/F-family SKUs per region, refreshed monthly from Azure CLI + Retail Prices API. Restricted SKUs filtered, processor family inferred from name (Intel/AMD/ARM). Falls back to a 40-SKU seed catalog when offline / on `file://`.
  - **Per-VM recommendation** with primary SKU, two alternates, monthly cost, CPU/RAM headroom %, and confidence (High / Medium / Low).
  - **Plan controls** — region, currency, term (PAYG / 1-yr / 3-yr RI / Spot), OS pricing model, headroom targets — fan out to every group and VM live.
  - **Tag rules + auto-grouping** over annotations, folders, clusters; auto-cluster VMs by any tag value into sizing groups.
  - **Out-of-scope handling** — Decommission / Retain on-prem / Already migrated / Other (with note). Excluded from cost roll-ups; restorable in bulk.
  - **Bulk actions** — multi-select VMs and add to group, create new group, remove from all groups, or mark out-of-scope. Selection breakdown shows grouped / ungrouped / OOS counts; >5-VM OOS prompts confirmation.
  - **CSV export** — five scopes (Active / Pinned / All / OOS / Everything), 21-column schema with SKU + family + cost + headroom + confidence + alternates.
  - **Excel workbook export** — multi-sheet `.xlsx` with Summary (group totals, grand total, dup flag), All recommendations, per-group sheets (Excel-safe names), Out of scope when present, and Plan (settings + catalog source + timestamp). Three scopes: All / Pinned / Active.
- **Duplicate VM handling.** RVTools exports with duplicate vInfo rows (same UUID, or same name+cluster+DC) are now collapsed to first occurrence on import. Dropped count surfaced in the file-load banner and the Excel Summary sheet.
- **Azure data refresh pipeline.** New `refresh-azure-data.yml` GitHub Actions workflow (monthly cron + manual trigger) authenticates via OIDC and updates `data/<region>.json`, `<region>-pricing.json`, `<region>-disks.json`, plus shared `regions.json` / `metadata.json` / `retirements.json`. Scripts ported from the sister VM SKU locator app. Pipeline activation pending Azure secrets + federated credentials in this repo.

### Changed

- README now has an **Azure SKU Recommender** section between Migration Readiness and Explore/Export, plus an Excel-export row in Explore.
- Inventory bulk bar count shows breakdown — `5 selected (3 grouped · 1 ungrouped · 1 OOS)`.

## [1.0.0] — First public release

The first stable release. Drop in your RVTools `.xlsx` export and turn it into a live VMware estate dashboard — all in your browser, nothing uploaded.

### Highlights

- **Multi-tab parsing.** Reads vInfo, vDatastore, vSnapshot, vHost, vDisk, vNetwork, vHealth, vCluster, vCPU, and vMemory. Auto-detects column-name variations across RVTools versions.
- **Eight infrastructure dashboards.** Overview · Environment Topology · Host Capacity · Storage Dashboard · Disk Analysis · Network Analysis · Resource Allocation · Snapshot Health · Environment Health. Each unlocks progressively as more RVTools tabs are present. The Overview section combines six metric cards, exec-summary text, a scoped filter bar (Datacenter / OS family / Power / Readiness), and six analytics charts.
- **Migration Readiness Groups.** Technical-readiness scoring (Ready Now / Light Prep / Modernise / Remediate) derived from OS, hardware version, firmware, sizing, and snapshot signals. Risk Quadrant scatter highlights the high-effort/high-impact migration candidates.
- **Distribution histograms for high-cardinality data.** Datastore utilisation, over-provisioning, host CPU/memory, and vCPU:core ratio charts now show the *shape* of the estate (bucketed counts) rather than per-entity bars — meaningful at any scale, from 30 VMs to thousands.
- **Demo Mode.** First-load synthetic dataset + sample `.xlsx` you can download from the drop zone. Toggle between vInfo-only and full multi-tab to see what extra tabs unlock.
- **Save Locally.** Export a self-contained HTML snapshot with charts baked in as images — works offline, perfect for emailing or pasting into a Teams chat.
- **Dark mode.** Theme tokens cover all charts, cards, hero, and nav. Persisted via `localStorage`.
- **Privacy by design.** Single-file static HTML. Two CDN libraries (Chart.js, SheetJS) loaded with **Subresource Integrity** sha384 hashes so a CDN compromise cannot inject code. Strict referrer-policy. No analytics, no telemetry, no backend.
- **Accessibility.** Keyboard-operable collapsible sections, `:focus-visible` outlines, `aria-label`s on icon-only controls, `aria-live` file-info status, `role=img` + descriptive labels on every chart canvas.
- **Built-in helpful errors.** Friendly messages for non-Excel files, missing vInfo sheets, empty exports, and unparseable data — with steps to fix.

### Operations

- Hosted on Azure Static Web Apps via GitHub Actions deploy on every push to `main`.
- Custom domain: [rvtoolsviz.djtools.co.nz](https://rvtoolsviz.djtools.co.nz/).
- HTML validation workflow runs on every PR touching `*.html`.
- Issue + PR templates, SECURITY.md, MIT license.

### Acknowledgements

Built end-to-end with [GitHub Copilot CLI](https://github.com/features/copilot/cli/).
