# 📋 RVTools Visualiser — Specification

> **Version:** v1.2.0-beta
> **Format:** Single HTML file with CDN dependencies (Chart.js + SheetJS + JSZip)
> **Audience:** VMware administrators, migration planners, infrastructure architects

---

## 1. Overview

RVTools Visualiser is a browser-based tool that parses RVTools VMware Excel exports and renders an interactive dashboard with executive summaries, infrastructure deep-dives, charts, migration-readiness analysis, and a per-VM Azure SKU recommender. Everything runs client-side — no data ever leaves the browser.

### Design Constraints

- **Single file** — all HTML, CSS, and JavaScript live in `index.html`
- **CDN dependencies only** — Chart.js (charts), SheetJS (`.xlsx` parsing), JSZip (`.rvz` scenario bundling) — all pinned with SRI
- **Privacy-first** — no server-side processing, no telemetry, no uploads
- **Offline capable** — exported HTML snapshots run without internet; scenario / workspace files round-trip locally
- **No build step** — file deploys as-is
- **Hosting** — Azure Static Web Apps (Free SKU)
- **CI/CD** — GitHub Actions on `ubuntu-latest` → SWA CLI deploy

---

## 2. Data Model

### 2.1 Tabs Parsed

The parser opens an RVTools workbook and locates each known tab by case-insensitive name match. Only `vInfo` is required; every other tab unlocks additional dashboards.

| Tab | Required? | Powers |
|-----|-----------|--------|
| `vInfo` | ✅ Required | Executive summary, OS / power / hardware charts, Risk Quadrant, Readiness Groups, Full Inventory |
| `vDatastore` | optional | 💾 Storage Dashboard |
| `vSnapshot` | optional | 📸 Snapshot Health |
| `vHost` | optional | 🏗️ Host Capacity |
| `vDisk` | optional | 💿 Disk Analysis |
| `vNetwork` | optional | 🌐 Network Analysis |
| `vHealth` | optional | 🏥 Environment Health |
| `vCluster` | optional | 🗺️ Environment Topology rollups |
| `vCPU` | optional | ⚡ Resource Allocation (CPU side) |
| `vMemory` | optional | ⚡ Resource Allocation (memory side) |

### 2.2 vInfo Column Mapping

The parser supports both legacy and modern RVTools column naming. Modern names are tried first, then legacy.

| App field | Modern column | Legacy column | Type |
|-----------|---------------|---------------|------|
| `name` | `VM` | `Name` | string |
| `powerState` | `Powerstate` | `Power state` | string |
| `cpus` | `CPUs` | `Num CPUs` | integer |
| `memoryMB` | `Memory` | `Memory MB` | integer |
| `provisionedMB` | `Provisioned MB` | `Provisioned MiB` | float |
| `os` | `OS according to the VMware Tools` | `OS according to the configuration file` | string |
| `datacenter` | `Datacenter` | `DC` | string |
| `cluster` | `Cluster` | `Cluster` | string |
| `host` | `Host` | `Host` | string |
| `hwVersion` | `HW version` | `VM hardware version` | integer |
| `firmware` | `Firmware` | — | string (BIOS/EFI) |

### 2.3 Computed Fields

| Field | Derivation |
|-------|-----------|
| `osFamily` | Categorised from OS string into Windows Server / Windows Desktop / Linux / Other |
| `wave` | 1–4, calculated by `getWave()` from OS age, power state, hardware/firmware modernity |
| `risk` | Four-tier readiness label mapped from wave |
| `complexity` | Score from vCPU count, memory, provisioned storage, OS, firmware, hardware version |
| `impact` | Score from disk, memory, CPU as a business-impact proxy |
| `notes` | Plain-English migration recommendation per VM |

---

## 3. Import

### Supported format

| Format | Extension | Detection |
|--------|-----------|-----------|
| RVTools Excel export | `.xlsx` (`.xls` accepted) | SheetJS parses the workbook, locates `vInfo`, then optionally each known tab |

### Import flow

1. User drags an `.xlsx` onto the upload zone (or picks one via the hidden file input).
2. SheetJS reads the workbook into memory.
3. The parser locates `vInfo` (case-insensitive). If missing → friendly error pointing the user back to *File → Export all to Excel*.
4. `parseRVToolsData()` maps columns using modern names first, falling back to legacy.
5. Each known optional tab is detected and routed to its parser (`parseDatastoreTab`, `parseSnapshotTab`, etc.).
6. Filters are populated and every section renders. Sections backed by missing tabs hide themselves.

### Error handling

The app surfaces friendly messages instead of stack traces for the common cases:
- File extension isn't `.xlsx` / `.xls`
- File can't be parsed as Excel
- No `vInfo` sheet (lists the sheets that *were* found)
- vInfo sheet empty
- vInfo parses but no VMs survive (e.g. all rows filtered as templates)

### Sample data and demo mode

On first visit (or after clicking *Back to demo*), the app loads a synthetic dataset of ~30 VMs across multiple datacenters, with matching synthetic vDatastore / vSnapshot / vHost / vDisk / vNetwork / vHealth tabs.

The drop zone offers a download link to `test-samples/rvtools-sample.xlsx` — a realistic full-tab RVTools export for users who want to test the upload flow with real-looking data.

The demo bar exposes a **vInfo Only / Full Export** toggle so users can preview the difference between minimal and rich datasets.

---

## 4. Sections

The app is organised into three groups plus the inventory table.

### 4.1 Top — global controls

1. **Nav bar** — brand, theme toggle, *Save Locally* (HTML snapshot export)
2. **Hero** — title, description, file info pill once a file is loaded
3. **Privacy badge** — "🔒 Private — your data stays in your browser"
4. **Demo bar** *(only when in demo mode)* — vInfo Only / Full Export toggle
5. **Drop zone** — drag-and-drop with a sample-file download link
6. **Overview** — six metric cards, exec text, filter bar (DC / OS family / power / readiness), and six analytics charts. The filter bar is scoped to this section only; tables and infrastructure sections elsewhere always show the full estate.

### 4.2 Infrastructure Analysis (collapsible)

Each section is collapsed by default. A section auto-hides if the tab that powers it is absent.

| Section | Tab | Highlights |
|---------|-----|------------|
| 🗺️ **Environment Topology** | `vInfo` (+ `vCluster` rollups) | VMs per DC/cluster, **Indicative Azure VM Family Fit** chart, capacity rollups |
| 🏗️ **Host Capacity** | `vHost` | Per-host CPU & memory utilisation, vCPU-to-core ratio, ESXi version, hardware vendor |
| 💾 **Storage Dashboard** | `vDatastore` | Datastore utilisation, over-provisioning warnings, free-space alerts, prov ratios |
| 💿 **Disk Analysis** | `vDisk` | Thin vs thick provisioning split, top 15 VMs by disk, per-disk breakdown with search + DC/cluster filters and CSV export |
| 🌐 **Network Analysis** | `vNetwork` | VMs per VLAN/network, adapter type distribution, per-NIC connectivity, IP visibility |
| ⚡ **Resource Allocation** | `vCPU` + `vMemory` | Top 15 by vCPU and memory, CPU/memory reservations and limits |
| 📸 **Snapshot Health** | `vSnapshot` | Old / oversized / orphaned snapshots highlighted with age and size |
| 🏥 **Environment Health** | `vHealth` | Health messages with severity classification |

### 4.3 Migration Readiness (collapsible)

| Section | Description |
|---------|-------------|
| 🎯 **Risk Quadrant** | Scatter plot of every VM, X = Migration Complexity, Y = Business Impact, coloured by readiness group. Includes an Azure Migrate signpost. |
| 🌊 **Readiness Groups** | Searchable, sortable, paginated table of VMs grouped by readiness with per-VM notes |

### 4.4 Azure SKU Recommender (collapsible, beta)

A second-tier "what would this look like in Azure?" view, layered on top of the readiness analysis.

| Section | Description |
|---------|-------------|
| **Plan settings bar** | Region, currency, term (PAYG / 1-yr / 3-yr RI / Spot), OS pricing model, headroom targets. Changes fan out to every group + VM via a `skurPlanChanged` event. |
| **Tag rules** | JSON-serialisable rules over annotations / folders / clusters. Auto-cluster VMs by any tag value into sizing groups. |
| **Sizing groups** | Each group has a name, optimisation mode (Balanced / Cost / Rightsized), members (VM keys), and an optional pin flag. Two view modes (rail+panel and 4-column board) persisted in `localStorage['skur.groupsView']`. |
| **Inventory grid + bulk bar** | Multi-select VMs to add to group, create new group, remove from all groups, or mark out-of-scope. Bulk bar shows breakdown (grouped / ungrouped / OOS). >5-VM OOS prompts confirmation. |
| **CSV / Excel exports** | CSV: 5 scopes (Active / Pinned / All / OOS / Everything), 21-column schema. Excel: multi-sheet workbook (Summary / All recommendations / per-group / OOS / Plan), 3 scopes (All / Pinned / Active), Excel-safe sheet-name sanitisation. |

**SKU catalog source.** Live JSON loader (`skurInitLiveData` / `_skurLoadRegionData`) consumes `data/<region>.json`, `<region>-pricing.json`, `<region>-disks.json`, plus shared `regions.json` + `metadata.json`. The normaliser scopes to families B/D/E/F/L/M (DC/EC confidential-compute collapse to D/E, FX collapses to F; GPU/HPC excluded) and stores both Linux and Windows hourly rates so the recommender can price per-VM by OS. Falls back to an inline seed catalog (Linux pricing only) when offline / on `file://`. Catalog refresh is automated via the `refresh-azure-data.yml` workflow (monthly cron) — see [`docs/data-pipeline.md`](data-pipeline.md).

**Stable VM identity.** Every parsed VM gets `vm.identity = {key, name, vcenter, datacenter, cluster, moRef, instanceUuid, biosUuid}`. The `key` is a normalized composite preferring strong IDs over name so manual tags / OOS / group membership survive VM rename: `iuid:<instanceUuid>` → `buid:<biosUuid>` → `mo:<vcenter>|<moRef>` → `nm:<name>|<cluster>|<dc>` (last resort). All in-app keying (`skurVmKey`, OOS map, group members, dedupe in `parseRVToolsData`) flows through this single identity.

**Recommendation algorithm (per VM).**
1. If the VM is out-of-scope → return `{state:'oos'}`.
2. If `cpus`/`ram` missing → return `{state:'no-input', mode:'balanced'}`.
3. Resolve eligibility — if VM belongs to exactly one group, use that group's mode + filtered SKU list; else balanced + full regional catalog.
4. Score every eligible SKU by mode (Balanced = distance from headroom target on both axes + cost tiebreaker; Cost = cheapest with min headroom; Rightsized = waste-normalised + cost tiebreaker).
5. Pick top score → recommended SKU; next two → alternates. Fit object carries CPU/RAM headroom + waste counts.
6. Confidence: **High** = full inputs + min headroom ≥ 20% + non-burstable. **Medium** = headroom 10–20% or burstable. **Low** = no inputs, no eligible, no match, or unhealthy state.

### 4.5 Bottom

| Section | Description |
|---------|-------------|
| 🖥️ **Full VM Inventory** | Searchable, sortable, paginated table of every VM with all parsed fields |
| Footer | Attribution and disclaimer |

---

## 5. Readiness Algorithm

The `getWave()` function assigns each VM to one of four readiness groups.

| Wave | Readiness label | Criteria | Risk |
|------|-----------------|----------|------|
| **1** | 🟢 **Ready Now** | Modern OS, powered on, modern hardware/firmware, standard resources | Low |
| **2** | 🟡 **Light Prep** | Older but supported OS, or slightly oversized, or hardware needs minor refresh | Medium |
| **3** | 🟠 **Modernise** | Legacy OS requiring upgrade, BIOS firmware, old hardware version, or powered off | High |
| **4** | 🔴 **Remediate** | End-of-life OS, or VMs needing significant rework before migrating | Critical |

### OS Classification helpers

- **Legacy** — Windows Server 2008/R2, 2003, 2000; Windows XP / Vista / 7; RHEL/CentOS 5–6
- **Older** — Windows Server 2012/R2; Ubuntu 14/16; RHEL/CentOS 7
- **Modern** — Windows Server 2016+; Ubuntu 18+; RHEL/CentOS 8+; Debian 10+

---

## 6. Charts

### 6.1 Base charts (§4.1)

| Chart | Type | Data |
|-------|------|------|
| OS Distribution | doughnut | VM count per OS family |
| Power State | pie | Powered on vs off |
| VMs per Datacenter | bar | VM count per datacenter |
| OS Versions | horizontal bar | Count of specific OS strings |
| Hardware Versions | doughnut | VMware virtual hardware version distribution |
| Storage by Datacenter | bar | Total provisioned storage (GB) per datacenter |

### 6.2 Dashboard charts (§4.2)

| Section | Charts |
|---------|--------|
| Environment Topology | VMs per Datacenter (rolled-up bar) · Indicative Azure Family Fit (doughnut) |
| Host Capacity | Host Utilisation Distribution (CPU & Memory % buckets) · vCPU:Core Overcommit Distribution |
| Storage Dashboard | Datastore Utilisation Distribution (% used buckets) · Over-provisioning Distribution (provisioned/capacity buckets) |
| Disk Analysis | Thin vs Thick Provisioning · Top 15 VMs by Disk Capacity |
| Network Analysis | VMs per Network/VLAN (top 15) · Adapter Type Distribution |
| Resource Allocation | Top 15 by CPU Allocation · Top 15 by Memory Allocation |

> **Why distributions for high-cardinality data?** Per-entity bar charts become unreadable past ~15 entities. The five distribution histograms (host util, vCPU:core, datastore util, over-prov, plus the rolled-up topology) summarise the *shape* of the estate — users drill into specific entities via the paginated tables underneath each dashboard.

### 6.3 Risk Quadrant

A `scatter` chart with one dataset per readiness group (colour-coded). Hover reveals VM name, OS, vCPU, RAM, and notes.

---

## 7. Save / Resume / Share *(v1.2.0-beta)*

### 7.1 Vocabulary

| Term | Meaning | File extension |
|------|---------|----------------|
| **RVTools file** | Raw multi-tab workbook exported from RVTools — one-way *in* | `.xlsx` |
| **Scenario** | Bundle of source data + workspace customisations — round-trips | `.rvz` |
| **Workspace** | Just the user customisations (groups, OOS, rules, plan settings) — round-trips | `.json` |
| **Report** | Output for sharing analysis — one-way *out* | `.csv` / `.xlsx` / `.html` |

### 7.2 Scenario file (`.rvz`)

A real ZIP container produced via JSZip. Layout:

```
manifest.json     {schema, appVersion, label, exportedAt, sourceFilename,
                   vmCount, byteSha256, workspaceSchema}
workspace.json    {schema, appVersion, exportedAt,
                   groups, outOfScope, tagRules, planSettings}
rvtools.xlsx      verbatim source bytes (NEVER reserialised)
```

- The xlsx bytes are stored **verbatim** so all original formatting, formulas, and tabs are preserved on reopen.
- `byteSha256` mismatch on reopen logs a warning but doesn't reject (the bytes are authoritative).
- `manifest.schema > RVZ_SCHEMA_VERSION` → rejected with a clear message ("file created by a newer app version").
- `workspace.schema` walks through `migrateWorkspace()` so older scenarios upgrade transparently.

### 7.3 Workspace JSON

Two flavours, both written via the same `_collectWorkspaceSnapshot()`:

| Flavour | Contents | Use case |
|---------|----------|----------|
| **Full workspace** | groups + outOfScope + tagRules + planSettings | Restore the same dataset; share with others who have the same RVTools file |
| **Rules template** | tagRules + planSettings only | Share standard-issue tagging conventions or plan defaults across customers — contains zero VM-derived data |

### 7.4 Reconciliation

Workspace JSON applied to a different dataset is reconciled non-destructively:

- VM IDs that match the current `allVMs` keys are restored.
- Unmatched VM IDs are preserved on `workspace.unresolvedVmRefs` (and per-group `_unresolved`) so a re-export round-trips back to the original.
- A confirm modal surfaces matched / unmatched / group / rule counts before applying.

### 7.5 Stable VM identity

Every VM gets `vm.identity = {key, name, vcenter, datacenter, cluster, moRef, instanceUuid, biosUuid}` with the key chosen by precedence:

1. `iuid:<instanceUuid>` — preferred (globally unique vCenter ID)
2. `buid:<biosUuid>` — fallback (unique within an org)
3. `mo:<vcenter>|<moRef>` — fallback (unique per vCenter)
4. `nm:<name>|<cluster>|<dc>` — last resort

This makes group memberships and OOS marks survive VM renames, cluster moves, and re-exports as long as one of the strong IDs is present.

### 7.6 Source-bytes persistence

After every successful parse, `_persistSourceBytes()`:

1. Computes SHA-256 of the raw bytes via SubtleCrypto → fingerprint.
2. Stores `{xlsxBuffer, fingerprint, sourceFilename, vmCount}` on `window.__rvtoolsCurrent`.
3. Writes the bytes to IndexedDB (`rvtools-viz` database, `sourceBytes` store, keyed by fingerprint) for cross-session resume.

This makes the Save scenario button work without re-uploading the original file.

### 7.7 Autosave

| Aspect | Behaviour |
|--------|-----------|
| Trigger | `setInterval` every 8s while data is loaded; flushes on `beforeunload` |
| Storage | `localStorage['rvtools.autosave.v1']` — `{savedAt, dataset:{fingerprint, sourceFilename, vmCount}, workspace}` |
| Resume | On `_persistSourceBytes` → if same `fingerprint` then silent restore; else reconciliation modal; if user cancels, autosave is discarded |
| Conflict | Refuses to overwrite an existing autosave with a `savedAt` newer than ours |

### 7.8 Cross-tab coordination

Two tabs open at once must not clobber each other:

| Channel | Works on | Mechanism |
|---------|----------|-----------|
| `BroadcastChannel('rvtools-viz')` | http(s) | Tabs `hello` on startup; on `autosave` event from a peer the receiving tab pauses |
| `storage` event | file:// + http(s) | Listens for `localStorage` writes from other tabs; pauses if peer's `savedAt > ours` |

When a tab pauses, a top-of-page amber banner (`role=alert`, `aria-live=assertive`) is shown with a Dismiss button.

### 7.9 File detection

The drop zone accepts `.xlsx`, `.xls`, `.rvz`, `.json`. Routing is **content-based**, not extension-based:

| Magic bytes | Routed to |
|-------------|-----------|
| `PK\x03\x04` (zip) | `detectZipKind()` peeks for `manifest.json`: yes → scenario flow; no → xlsx flow |
| `D0 CF 11 E0` (OLE compound) | xlsx (legacy `.xls`) |
| `{` or `[` after BOM/whitespace | workspace JSON flow |
| anything else | rejected with a clear message |

### 7.10 CSV / Excel export hardening

All exported cells are wrapped via `_safeCell()` which prefixes a single quote to any value starting with `=`, `+`, `-`, `@`, or tab. This neutralises Excel formula injection and DDE attacks if the export is opened in Excel by a downstream consumer.

---

## 7. Tables & Pagination

All ten data tables share a consistent look and a single pagination helper:

| Table | Section |
|-------|---------|
| Topology rollup | 🗺️ Environment Topology |
| Hosts | 🏗️ Host Capacity |
| Datastores | 💾 Storage Dashboard |
| Disks | 💿 Disk Analysis |
| Networks | 🌐 Network Analysis |
| Resource allocation | ⚡ Resource Allocation |
| Snapshots | 📸 Snapshot Health |
| Health messages | 🏥 Environment Health |
| Readiness Groups | 🚀 Migration Readiness |
| Full VM Inventory | 🖥️ Inventory |

All tables paginate at **25 rows per page** with prev/next controls and a row-range indicator.

---

## 8. Export

### 8.1 CSV

Two CSV exports are available:
- **Readiness Recommendations** — VM name, OS, datacenter, readiness, notes
- **Full Inventory** — every parsed field (vCPU, memory, storage, host, cluster, hardware, …)

Filename pattern: `rvtools_export_YYYYMMDD_HHMMSS.csv`

### 8.2 SKU Recommender CSV

Per-VM recommendation rows for one of five scopes — **Active group** / **Pinned** / **All groups** / **Out-of-scope** / **Everything**. Filename pattern: `rvtools_skur_<scope>_YYYY-MM-DD.csv`.

Columns (21): `Group, Mode, VM, OS, vCPU, RAM_GB, Cluster, Datacentre, Powered, OOS_Reason, Recommended_SKU, SKU_Family, SKU_vCPU, SKU_RAM_GB, Monthly_Cost, Currency, CPU_Headroom_Pct, RAM_Headroom_Pct, Confidence, State, Alt_SKUs`.

### 8.3 SKU Recommender Excel workbook

Multi-sheet `.xlsx` for one of three scopes (All / Pinned / Active). Filename pattern: `rvtools_skur_YYYY-MM-DD[_<scope>].xlsx`.

Sheets:
- **Summary** — group, mode, members, eligible SKUs, total monthly $/region currency, pinned flag, grand total + OOS count + duplicates-collapsed flag (when present).
- **All recommendations** — every grouped VM as a row, prefixed with Group + Mode columns.
- **One sheet per group** — Excel-safe sheet name (strip `: \ / ? * [ ]`, cap at 28 chars, dedupe with suffix).
- **Out of scope** — present only when OOS VMs exist; columns: VM / OS / vCPU / RAM_GB / Cluster / Datacentre / Reason / Note.
- **Plan** — every `skurPlan` key/value, export timestamp, catalog source (seed / live / live-pending / unavailable).

Numeric cells (vCPU, RAM, costs, headroom %) are written as numbers, not strings, so Excel can chart and aggregate them directly.

### 8.4 Offline HTML snapshot ("Save Locally")

A single self-contained `.html` file that contains:
- All charts as base64 PNGs (`canvas.toDataURL()`)
- Cloned summary cards and tables
- Inline CSS, no external dependencies
- An amber **OFFLINE SNAPSHOT** banner so it's never confused with the live app
- Export timestamp in the footer

Filename pattern: `rvtools_visualiser_YYYYMMDD_HHMMSS.html`

The snapshot is *not* paginated — every row is rendered for self-contained reading.

---

## 9. UI / Theme

- Light & dark mode with `prefers-color-scheme` detection and a manual toggle saved to `localStorage`
- Connected-dots SVG background with parallax effect, themed per mode
- All colours sourced from CSS custom properties so a single class flip on `<body>` re-themes the app
- Section groups (`Infrastructure Analysis`, `Migration Readiness`) act as visual headers above their collapsible sections
- All collapsible sections are closed by default to keep the initial view scannable

---

## 10. Deployment

| Aspect | Detail |
|--------|--------|
| Hosting | Azure Static Web Apps (Free SKU, East Asia) |
| CI/CD | GitHub Actions on push to `main` (paths: `index.html`, `deploy.yml`) |
| Runner | GitHub-hosted `ubuntu-latest` |
| Deploy method | `npx @azure/static-web-apps-cli deploy` against a `deploy-staging/` folder |
| Custom domain | `rvtoolsviz.djtools.co.nz` |
| Validation | Separate `validate.yml` workflow runs HTML-structure checks on PRs |
