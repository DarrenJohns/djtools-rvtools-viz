# 📋 RVTools Visualiser — Specification

> **Version:** v1.0.0-beta
> **Format:** Single HTML file with CDN dependencies (Chart.js + SheetJS)
> **Audience:** VMware administrators, migration planners, infrastructure architects

---

## 1. Overview

RVTools Visualiser is a browser-based tool that parses RVTools VMware Excel exports and renders an interactive dashboard with executive summaries, infrastructure deep-dives, charts, and migration-readiness analysis. Everything runs client-side — no data ever leaves the browser.

### Design Constraints

- **Single file** — all HTML, CSS, and JavaScript live in `index.html`
- **CDN dependencies only** — Chart.js for charts, SheetJS for `.xlsx` parsing
- **Privacy-first** — no server-side processing, no telemetry, no uploads
- **Offline capable** — exported HTML snapshots run without internet
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

### 4.4 Bottom

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

### 8.2 Offline HTML snapshot ("Save Locally")

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
