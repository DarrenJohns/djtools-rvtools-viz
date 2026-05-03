# Changelog

All notable changes to RVTools Visualiser are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [Semantic Versioning](https://semver.org/).

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
